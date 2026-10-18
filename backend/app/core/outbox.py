import base64
import hashlib
from datetime import datetime, timezone

from cryptography.fernet import Fernet

from app.core.config import settings
from app.models.email_outbox import EmailOutbox


def _cipher() -> Fernet:
    if settings.OTP_OUTBOX_ENCRYPTION_KEY:
        key = settings.OTP_OUTBOX_ENCRYPTION_KEY.encode("ascii")
    else:
        key = base64.urlsafe_b64encode(
            hashlib.sha256(
                f"focusflow-otp-outbox:{settings.SECRET_KEY}".encode("utf-8")
            ).digest()
        )
    return Fernet(key)


def enqueue_verification_email(db, email: str, otp: str) -> None:
    encrypted_otp = _cipher().encrypt(otp.encode("ascii")).decode("ascii")
    db.add(
        EmailOutbox(
            recipient=email,
            encrypted_otp=encrypted_otp,
            next_attempt_at=datetime.now(timezone.utc),
        )
    )


def decrypt_verification_otp(encrypted_otp: str) -> str:
    return _cipher().decrypt(encrypted_otp.encode("ascii")).decode("ascii")
