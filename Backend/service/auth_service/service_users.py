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

from model.user import UserLogin, UserRegister
from repository.authentication.user_repo import (
    clear_otp,
    delete_pending_user,
    get_user_by_email,
    get_user_by_username,
    get_user_otp,
    increment_attempts,
    move_pending_user_to_users,
    save_otp,
    save_pending_user,
    update_user_password,
)
from security.otp import verify_otp as verify_otp_hash
from security.secure_users import hash_password, verify_password
from utilities.authentication_user.mail import send_verification_email

logger = logging.getLogger(__name__)


def _issue_otp(email: str) -> None:
    """Generate a code, email it, and store its hash with its expiry."""
    otp = send_verification_email(email)
    save_otp(email, otp["hashed_otp"], otp["created_at"], otp["expired_at"])


def _check_otp(email: str, otp: str) -> str | None:
    """Return an error message if the code is unusable or wrong, else None."""
    otp_row = get_user_otp(email)

    if not otp_row or not otp_row["hash_otp"]:
        return "No active verification code. Request a new one."

    expired_at = otp_row["expired_at"]
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

    if otp_row["attempts"] >= otp_row["total_attempts"]:
        return "Too many attempts. Request a new code."

    if not verify_otp_hash(otp.strip(), otp_row["hash_otp"]):
        increment_attempts(email)
        remaining = otp_row["total_attempts"] - otp_row["attempts"] - 1
        if remaining <= 0:
            return "Too many attempts. Request a new code."
        return f"Invalid code. {remaining} attempt(s) left."

    return None


def register_user(user_data: UserRegister) -> Dict[str, str]:
    email = user_data.email.strip().lower()
    username = user_data.username.strip()

    if get_user_by_email(email):
        return {"error": "Email already registered."}

    if get_user_by_username(username):
        return {"error": "Username already taken."}

    save_pending_user(
        user_data.firstName,
        user_data.lastName,
        email,
        username,
        hash_password(user_data.password),
    )

    try:
        _issue_otp(email)
    except Exception:
        logger.exception("Could not send verification email to %s", email)
        delete_pending_user(email)
        return {"error": "Could not send the verification email. Please try again."}

    return {"message": "Verification code sent. Check your email."}


def login_user(user: UserLogin) -> Dict[str, str]:
    existing_user = get_user_by_email(user.email.strip().lower())

    if not existing_user:
        return {"error": "Invalid email or password."}

    if not verify_password(user.password, existing_user["password"]):
        return {"error": "Invalid email or password."}

    return {"message": "Login successful."}


def request_otp(email: str) -> Dict[str, str]:
    """Re-issue a code for an email that already started registering."""
    return resend_otp(email)


def resend_otp(email: str) -> Dict[str, str]:
    email = email.strip().lower()

    # The OTP row survives verification (clear_otp nulls the hash), so its
    # presence is what proves this email belongs to a real account.
    if get_user_otp(email) is None:
        return {"error": "No registration found for this email."}

    try:
        _issue_otp(email)
    except Exception:
        logger.exception("Could not resend verification email to %s", email)
        return {"error": "Could not send the verification email. Please try again."}

    return {"message": "Verification code sent."}


def verify_otp(email: str, otp: str) -> Dict[str, str]:
    email = email.strip().lower()

    error = _check_otp(email, otp)
    if error:
        return {"error": error}

    # Promote first, clear second: if the promotion fails the code is still
    # valid and the user can retry instead of having to register again.
    try:
        move_pending_user_to_users(email)
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

    error = _check_otp(email, otp)
    if error:
        return {"error": error}

    update_user_password(email, hash_password(new_password))
    clear_otp(email)

    return {"message": "Password reset successfully."}
