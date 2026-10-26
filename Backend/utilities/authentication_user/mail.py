from datetime import datetime, timedelta, timezone

from settings.mail import configure_email
from security.secure_users import create_secure_otp


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
