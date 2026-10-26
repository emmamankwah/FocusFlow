"""Service layer for the authentication flow.

Registration happens in two steps:

1. ``register_user`` stores the details in ``pending_users`` and emails an OTP.
2. ``verify_otp`` checks the OTP, then moves the pending row into ``users``.

Only verified users ever reach ``users``, so a row in ``users`` implies a
verified account.
"""

import logging
from datetime import datetime, timezone
from typing import Dict
import os 
import dotenv
from dotenv import load_dotenv


from model.user import UserLogin, UserRegister
from repository.authentication.user_repo import (
    clear_otp,
    create_user,
    delete_pending_user,
    get_pending_user,
    get_user_by_email,
    get_user_by_username,
    get_user_otp,
    increment_attempts,
    save_otp,
    save_pending_user,
    update_user_password,
)
from security.rate_limit import SlidingWindowLimiter
from security.secure_users import (
    hash_password, 
    verify_password,
    secure_verify_otp,
    secure_hash_otp
)

from utilities.authentication_user.mail import (
    create_verification_otp,
    send_verification_email,
)

load_dotenv()

OTP_EXPIRE_MINUTES = os.getenv("OTP_EXPIRE_MINUTES")
OTP_MAX_ATTEMPTS = os.getenv("OTP_MAX_ATTEMPTS", 3)

# One code per email every 45 seconds, at most five per 15 minutes.
OTP_SEND_COOLDOWN_SECONDS = os.getenv("OTP_SEND_COOLDOWN_SECONDS", 45)
OTP_SEND_LIMIT = 5
OTP_SEND_WINDOW_SECONDS = 15 * 60

# Wrong guesses are counted per email across codes, so requesting a fresh code
# does not reset the brute-force budget.
OTP_FAILED_LIMIT = 10
OTP_FAILED_WINDOW_SECONDS = 15 * 60

otp_send_limiter = SlidingWindowLimiter(
    "otp-send",
    ((1, OTP_SEND_COOLDOWN_SECONDS), (OTP_SEND_LIMIT, OTP_SEND_WINDOW_SECONDS)),
)
otp_verify_limiter = SlidingWindowLimiter(
    "otp-verify",
    ((OTP_FAILED_LIMIT, OTP_FAILED_WINDOW_SECONDS),),
)

logger = logging.getLogger(__name__)


class OtpRateLimited(Exception):
    """Raised when an email has requested codes too often."""

    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after
        super().__init__(f"OTP requested too often; retry in {retry_after:.0f}s.")


def _rate_limit_key(email: str) -> str:
    # Case-fold the key so "User@x.com" cannot get a second budget.
    return email.strip().lower()


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

    if get_user_by_email(email):
        return {"error": "Email already registered."}

    if get_user_by_username(username):
        return {"error": "Username already taken."}

    if get_pending_user(email):
        delete_pending_user(email)
        
    save_pending_user(
        user_data.firstName,
        user_data.lastName,
        email,
        username,
        hash_password(user_data.password),
    )

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

    return {"message": "Login successful."}


def request_otp(email: str) -> Dict[str, str]:
    """Send a verification/reset code, throttled per email."""
    email = email.strip()

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

    return {"message": "Verification code sent. Check your email."}


def resend_otp(email: str) -> Dict[str, str]:
    email = email.strip()

   
    if get_user_otp(email) is None:
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
    error_check = check_otp(email, otp)
    if error_check:
        return {"error": error_check}

    # Promote first, clear second: if the promotion fails the code is still
    # valid and the user can retry instead of having to register again.
    try:
        create_user(email)
    except ValueError:
        return {"error": "No registration found for this email."}
    except Exception:
        logger.exception("Could not promote pending user %s", email)
        return {"error": "Could not complete verification. Please try again."}

    clear_otp(email)

    return {"message": "Email verified. You can now log in."}


def reset_password(email: str, otp: str, new_password: str) -> Dict[str, str]:
    email = email.strip().lower()

    if not get_user_by_email(email):
        return {"error": "Invalid email."}

    error_check = check_otp(email, otp)
    if error_check:
        return {"error": error_check}

    update_user_password(email, hash_password(new_password))
    clear_otp(email)

    return {"message": "Password reset successfully."}
