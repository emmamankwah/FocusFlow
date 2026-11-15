from datetime import datetime, timedelta, timezone

from app.authentication.settings.mail import configure_email
from app.authentication.security.secure_users import create_secure_otp


def create_verification_otp(expires_minutes: int) -> dict:
    """Return a fresh code plus the hash and expiry to persist for it."""
    plain_otp, hashed_otp = create_secure_otp()
    created_at = datetime.now(timezone.utc)
    return {
        "plain_otp": plain_otp,
        "hashed_otp": hashed_otp,
        "created_at": created_at,
        "expired_at": created_at + timedelta(minutes=expires_minutes),
    }


def send_verification_email(
    user_email: str, plain_otp: str, expires_minutes: int
) -> None:
    """Email a verification code that has already been issued and stored."""
    subject = "Your Verification Code"
    body = (
        f"Your verification code is: {plain_otp}.\n"
        f"It expires in {expires_minutes} minutes.\n"
        "If you did not request this, you can ignore this email."
    )

    if not configure_email(user_email, subject, body):
        raise RuntimeError("Failed to send verification email")


def send_email_change_verification(
    new_email: str, plain_otp: str, expires_minutes: int
) -> None:
    """Email the code that must be confirmed before the email is changed."""
    subject = "Confirm Your New Email Address"
    body = (
        f"Your email change verification code is: {plain_otp}.\n"
        f"It expires in {expires_minutes} minutes.\n"
        "If you did not request this change, you can ignore this email."
    )

    if not configure_email(new_email, subject, body):
        raise RuntimeError("Failed to send email change verification")


def send_email_change_notice(old_email: str, new_email: str) -> None:
    """Tell the previous address that the account email was changed."""
    subject = "Your Email Address Was Changed"
    body = (
        f"The email address for your account was changed to {new_email}.\n"
        "If you did not make this change, reset your password immediately."
    )

    if not configure_email(old_email, subject, body):
        raise RuntimeError("Failed to send email change notice")
