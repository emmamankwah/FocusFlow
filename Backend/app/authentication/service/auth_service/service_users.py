"""Service layer for the authentication flow.

Registration happens in two steps:

1. ``register_user`` stores the details in ``pending_users`` and emails an OTP.
2. ``verify_otp`` checks the OTP, then moves the pending row into ``users``.

Only verified users ever reach ``users``, so a row in ``users`` implies a
verified account.
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

from app.authentication.model.user import (
    UserLogin,
    UserProfileUpdate,
    UserPublic,
    UserRegister,
)
from app.authentication.repository.authentication.user_repo import (
    clear_otp,
    delete_pending_email_change,
    delete_pending_user,
    email_in_use_exact,
    get_pending_email_change,
    get_pending_user,
    get_user_by_email,
    get_user_by_id,
    get_user_otp,
    increment_attempts,
    increment_email_change_attempts,
    move_pending_user_to_users,
    save_otp,
    save_pending_email_change,
    save_pending_user,
    update_user_email_and_bump_version,
    update_user_password,
    update_user_password_by_id,
    update_user_profile,
    username_in_use,
)
from app.authentication.security.rate_limit import RedisSlidingWindowLimiter
from app.authentication.security.secure_users import (
    hash_password,
    verify_password,
    secure_verify_otp,
)
from app.authentication.security.token import create_access_token
from app.authentication.utilities.authentication_user.mail import (
    create_verification_otp,
    send_email_change_notice,
    send_email_change_verification,
    send_verification_email,
)

load_dotenv(Path(__file__).resolve().parents[4] / ".env")

OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "3"))
OTP_SEND_COOLDOWN_SECONDS = int(os.getenv("OTP_SEND_COOLDOWN_SECONDS", "45"))

# One code per email every OTP_SEND_COOLDOWN_SECONDS, at most five per 15
# minutes.
OTP_SEND_LIMIT = 5
OTP_SEND_WINDOW_SECONDS = 15 * 60

# Wrong guesses are counted per email across codes, so requesting a fresh code
# does not reset the brute-force budget.
OTP_FAILED_LIMIT = 10
OTP_FAILED_WINDOW_SECONDS = 15 * 60

otp_send_limiter = RedisSlidingWindowLimiter(
    "otp-send",
    ((1, OTP_SEND_COOLDOWN_SECONDS), (OTP_SEND_LIMIT, OTP_SEND_WINDOW_SECONDS)),
)
otp_verify_limiter = RedisSlidingWindowLimiter(
    "otp-verify",
    ((OTP_FAILED_LIMIT, OTP_FAILED_WINDOW_SECONDS),),
)
email_change_send_limiter = RedisSlidingWindowLimiter(
    "email-change-send",
    ((1, OTP_SEND_COOLDOWN_SECONDS), (OTP_SEND_LIMIT, OTP_SEND_WINDOW_SECONDS)),
)
email_change_verify_limiter = RedisSlidingWindowLimiter(
    "email-change-verify",
    ((OTP_FAILED_LIMIT, OTP_FAILED_WINDOW_SECONDS),),
)

logger = logging.getLogger(__name__)


class OtpRateLimited(Exception):
    """Raised when an email has requested codes too often."""

    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after
        super().__init__(f"OTP requested too often; retry in {retry_after:.0f}s.")


def _rate_limit_key(email: str) -> str:
    return email.strip()


def _email_change_key(user_id: int, email: str) -> str:
    return f"{user_id}:{email}"


def _wait_text(seconds: float) -> str:
    whole = max(1, int(seconds + 0.999))
    if whole < 60:
        return f"{whole} second{'s' if whole != 1 else ''}"
    minutes = (whole + 59) // 60
    return f"{minutes} minute{'s' if minutes != 1 else ''}"



def send_verification_mail(user_email: str) -> None:
    # Applies to registration, resend and password reset: an unauthenticated
    # caller cannot use this endpoint to flood an inbox or to buy extra guesses.
    wait = otp_send_limiter.hit(_rate_limit_key(user_email))
    if wait:
        raise OtpRateLimited(wait)

    expires_minutes = OTP_EXPIRE_MINUTES

    # Generate ONE OTP
    otp_data = create_verification_otp(expires_minutes)

    # Email the matching plain OTP
    send_verification_email(
        user_email=user_email,
        plain_otp=otp_data["plain_otp"],
        expires_minutes=expires_minutes,
    )

    # Save its hash and timestamps to the database
    save_otp(
        email=user_email,
        hash_otp=otp_data["hashed_otp"],
        created_at=otp_data["created_at"],
        expired_at=otp_data["expired_at"],
        total_attempts=OTP_MAX_ATTEMPTS,
    )


def check_otp(email: str, otp: str) -> str | None:
    """Return an error message if the code is unusable or wrong, else None."""
    email = email.strip()

    # Counted per email, not per code: resending a code resets the row in
    # ``otp_table`` but must not hand out a fresh brute-force budget.
    wait = otp_verify_limiter.retry_after(_rate_limit_key(email))
    if wait:
        return f"Too many failed attempts. Try again in {_wait_text(wait)}."

    otp_data = get_user_otp(email)

    if not otp_data or not otp_data["hash_otp"]:
        return "No active verification code. Request a new one."

    expired_at = otp_data["expired_at"]
    if expired_at is None:
        return "Verification code expired. Request a new one."

    # The column may be TIMESTAMP (naive) or TIMESTAMPTZ (aware). Build the
    # current time in the same form so the comparison never raises.
    now = (
        datetime.now(expired_at.tzinfo)
        if expired_at.tzinfo is not None
        else datetime.now(timezone.utc).replace(tzinfo=None)
    )
    if expired_at < now:
        return "Verification code expired. Request a new one."

    if otp_data["attempts"] >= otp_data["total_attempts"]:
        return "Too many attempts. Request a new code."

    if not secure_verify_otp(otp.strip(), otp_data["hash_otp"]):
        otp_verify_limiter.hit(_rate_limit_key(email))
        row = increment_attempts(email) or {}
        attempts = row.get("attempts", otp_data["attempts"] + 1)
        total = row.get("total_attempts", otp_data["total_attempts"])
        remaining = total - attempts
        if remaining <= 0:
            return "Too many attempts. Request a new code."
        return f"Invalid code. {remaining} attempt(s) left."

    return None



def register_user(user_data: UserRegister) -> Dict[str, str]:
    email = user_data.email.strip()
    username = user_data.username.strip()

    if not username:
        return {"error": "Username cannot be empty."}
    if any(character.isspace() for character in username):
        return {"error": "Username cannot contain spaces."}

    if get_user_by_email(email):
        return {"error": "Email already registered."}

    if username_in_use(username):
        return {"error": "Username already taken."}

    if get_pending_user(email):
        # A registration is already in flight for this email; never overwrite
        # the staged row, or an arriving OTP could promote attacker-chosen data.
        return {
            "message": "A verification is already in progress for this email. "
                       "Wait for it to expire or use the resend flow.",
        }

    if email_in_use_exact(email):
        return {"error": "Email already in use."}

    try:
        save_pending_user(
            user_data.firstName,
            user_data.lastName,
            email,
            username,
            hash_password(user_data.password),
        )
    except ValueError as exc:
        return {"error": str(exc)}

    try:
        send_verification_mail(email)
    except OtpRateLimited as exc:
        # Keep the pending row: the user can continue once the wait is over.
        return {
            "error": "Too many verification emails requested. "
            f"Try again in {_wait_text(exc.retry_after)}."
        }
    except Exception:
        logger.exception("Could not send verification email to %s", email)
        delete_pending_user(email)
        return {"error": "Could not send the verification email. Please try again."}

    return {"message": "Verification code sent. Check your email."}


def login_user(user: UserLogin) -> Dict[str, str]:
    existing_user = get_user_by_email(user.email.strip())

    if not existing_user:
        return {"error": "Invalid email or password."}

    if not verify_password(user.password, existing_user["password"]):
        return {"error": "Invalid email or password."}

    token = create_access_token(
        str(existing_user["id"]),
        int(existing_user.get("token_version") or 0),
    )
    return {
        "message": "Login successful.",
        "access_token": token,
        "token_type": "bearer",
    }


def get_profile(user_id: int) -> Dict[str, object]:
    user = get_user_by_id(user_id)

    if not user:
        return {"error": "User not found."}

    profile = UserPublic(
        id=user["id"],
        firstName=user["first_name"],
        lastName=user["last_name"],
        username=user["username"],
        email=user["email"],
    )
    return profile.model_dump()


def update_profile(
    user_id: int,
    user_data: UserProfileUpdate,
) -> Dict[str, object]:
    user = get_user_by_id(user_id)

    if not user:
        return {"error": "User not found."}

    username = user_data.username.strip()

    if not username:
        return {"error": "Username cannot be empty."}

    # Verified users keep their own name; pending registrations also reserve
    # theirs so a promotion can never collide later.
    if username_in_use(username, exclude_user_id=user_id):
        return {"error": "Username already taken."}

    update_user_profile(
        user_id,
        user_data.firstName,
        user_data.lastName,
        username,
    )
    return get_profile(user_id)


def change_password(
    user_id: int,
    old_password: str,
    new_password: str,
) -> Dict[str, str]:
    user = get_user_by_id(user_id)

    if not user:
        return {"error": "User not found."}

    if not verify_password(old_password, user["password"]):
        return {"error": "Current password is incorrect."}

    token_version = update_user_password_by_id(
        user_id,
        hash_password(new_password),
    )
    if token_version is None:
        return {"error": "User not found."}

    token = create_access_token(str(user_id), token_version)
    return {
        "message": "Password changed successfully.",
        "access_token": token,
        "token_type": "bearer",
    }


def request_email_change(
    user_id: int,
    new_email: str,
    current_password: str,
) -> Dict[str, str]:
    user = get_user_by_id(user_id)

    if not user:
        return {"error": "User not found."}

    if not verify_password(current_password, user["password"]):
        return {"error": "Current password is incorrect."}

    if new_email == user["email"]:
        return {"error": "New email must be different from the current email."}

    if email_in_use_exact(new_email, exclude_user_id=user_id):
        return {"error": "Email already in use."}

    wait = email_change_send_limiter.hit(_email_change_key(user_id, new_email))
    if wait:
        return {
            "error": "Too many verification emails requested. "
            f"Try again in {_wait_text(wait)}."
        }

    expires_minutes = OTP_EXPIRE_MINUTES
    otp_data = create_verification_otp(expires_minutes)

    try:
        save_pending_email_change(
            user_id,
            new_email,
            otp_data["hashed_otp"],
            otp_data["expired_at"],
            OTP_MAX_ATTEMPTS,
        )
    except ValueError as exc:
        return {"error": str(exc)}
    except Exception:
        logger.exception("Could not save pending email change for user %s", user_id)
        return {"error": "Could not start the email change. Please try again."}

    try:
        send_email_change_verification(
            new_email,
            otp_data["plain_otp"],
            expires_minutes,
        )
    except Exception:
        logger.exception("Could not send email change verification to %s", new_email)
        try:
            delete_pending_email_change(user_id)
        except Exception:
            logger.exception(
                "Could not delete pending email change for user %s",
                user_id,
            )
        return {"error": "Could not send the verification email. Please try again."}

    return {"message": "Verification code sent to the new email."}


def verify_email_change(user_id: int, otp: str) -> Dict[str, object]:
    pending = get_pending_email_change(user_id)

    if not pending:
        return {"error": "No active email change. Request a new one."}

    new_email = pending["new_email"]
    key = _email_change_key(user_id, new_email)

    wait = email_change_verify_limiter.retry_after(key)
    if wait:
        return {
            "error": f"Too many failed attempts. Try again in {_wait_text(wait)}."
        }

    expires_at = pending["expires_at"]
    if expires_at is None:
        delete_pending_email_change(user_id)
        return {"error": "Verification code expired. Request a new one."}

    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        delete_pending_email_change(user_id)
        return {"error": "Verification code expired. Request a new one."}

    if pending["attempts"] >= pending["total_attempts"]:
        return {"error": "Too many attempts. Request a new code."}

    if not secure_verify_otp(otp.strip(), pending["otp_hash"]):
        email_change_verify_limiter.hit(key)
        row = increment_email_change_attempts(user_id) or {}
        attempts = row.get("attempts", pending["attempts"] + 1)
        total = row.get("total_attempts", pending["total_attempts"])
        remaining = total - attempts
        if remaining <= 0:
            return {"error": "Too many attempts. Request a new code."}
        return {"error": f"Invalid code. {remaining} attempt(s) left."}

    user = get_user_by_id(user_id)
    if not user:
        delete_pending_email_change(user_id)
        return {"error": "User not found."}

    old_email = user["email"]

    try:
        token_version = update_user_email_and_bump_version(user_id, new_email)
    except ValueError as exc:
        delete_pending_email_change(user_id)
        return {"error": str(exc)}
    except Exception:
        logger.exception("Could not complete email change for user %s", user_id)
        return {"error": "Could not complete the email change. Please try again."}

    try:
        send_email_change_notice(old_email, new_email)
    except Exception:
        logger.exception("Could not notify old email %s", old_email)

    profile = get_profile(user_id)
    if "error" in profile:
        return profile

    token = create_access_token(str(user_id), token_version)
    return {
        **profile,
        "message": "Email changed successfully.",
        "access_token": token,
        "token_type": "bearer",
    }


def cancel_email_change(user_id: int) -> Dict[str, str]:
    delete_pending_email_change(user_id)
    return {"message": "Email change cancelled."}


def request_otp(email: str) -> Dict[str, str]:
    """Send a reset code only when the account exists."""
    email = email.strip()

    if not get_user_by_email(email):
        return {
            "message": "If that email is registered, a verification code has been sent."
        }

    try:
        send_verification_mail(email)
    except OtpRateLimited as exc:
        return {
            "error": "Too many verification emails requested. "
            f"Try again in {_wait_text(exc.retry_after)}."
        }
    except Exception:
        logger.exception("Could not send verification email to %s", email)
        return {"error": "Could not send the verification email. Please try again."}

    return {
        "message": "If that email is registered, a verification code has been sent."
    }


def verify_reset_otp(email: str, otp: str) -> Dict[str, str]:
    email = email.strip()

    if not get_user_by_email(email):
        return {"error": "No active verification code. Request a new one."}

    error_check = check_otp(email, otp)
    if error_check:
        return {"error": error_check}

    return {"message": "Verification code accepted."}


def resend_otp(email: str) -> Dict[str, str]:
    email = email.strip()

    if get_user_otp(email) is None:
        return {"error": "No registration found for this email."}

    if not get_pending_user(email) and not get_user_by_email(email):
        clear_otp(email)
        return {"error": "No registration found for this email."}

    try:
        send_verification_mail(email)
    except OtpRateLimited as exc:
        return {
            "error": "Too many verification emails requested. "
            f"Try again in {_wait_text(exc.retry_after)}."
        }
    except Exception:
        logger.exception("Could not resend verification email to %s", email)
        return {"error": "Could not send the verification email. Please try again."}

    return {"message": "Verification code sent."}


def verify_otp(email: str, otp: str) -> Dict[str, str]:
    email = email.strip()

    if not get_pending_user(email):
        return {"error": "No registration found for this email."}

    error_check = check_otp(email, otp)
    if error_check:
        return {"error": error_check}

    # Promote first, clear second: if the promotion fails the code is still
    # valid and the user can retry instead of having to register again.
    try:
        move_pending_user_to_users(email)
    except ValueError as exc:
        if "Username already in use" in str(exc):
            # The staged row can never be promoted; free the email so the
            # user can register again with a different username.
            delete_pending_user(email)
            clear_otp(email)
            return {"error": str(exc)}
        return {"error": "No registration found for this email."}
    except Exception:
        logger.exception("Could not promote pending user %s", email)
        return {"error": "Could not complete verification. Please try again."}

    clear_otp(email)

    return {"message": "Email verified. You can now log in."}


def reset_password(email: str, otp: str, new_password: str) -> Dict[str, str]:
    email = email.strip()

    if not get_user_by_email(email):
        return {"error": "Invalid email."}

    error_check = check_otp(email, otp)
    if error_check:
        return {"error": error_check}

    token_version = update_user_password(email, hash_password(new_password))
    if token_version is None:
        return {"error": "Invalid email."}

    clear_otp(email)

    return {"message": "Password reset successfully."}
