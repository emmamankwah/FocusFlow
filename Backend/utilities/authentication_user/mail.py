import os
from datetime import datetime, timedelta, timezone

from settings.mail import send_email
from security.otp import create_secure_otp


def send_verification_email(user_email: str):
    plain_otp, hashed_otp = create_secure_otp()

    otp_expire_minutes = int(os.getenv("OTP_EXPIRE_MINUTES"))
    now = datetime.now(timezone.utc)
    created_at = now
    expired_at = now + timedelta(minutes=otp_expire_minutes)

    subject = "Your Verification Code"
    body = (
        f"Your verification code is: {plain_otp}.\n"
        f"It expires in {otp_expire_minutes} minutes.\n"
        "If you did not request this, you can ignore this email."
    )

    send_email(user_email, subject, body)

    return {
        "plain_otp": plain_otp,
        "hashed_otp": hashed_otp,
        "created_at": created_at,
        "expired_at": expired_at,
    }

