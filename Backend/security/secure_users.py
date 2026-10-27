"""Hashing helpers for passwords and one-time codes."""

from passlib.context import CryptContext

from utilities.authentication_user.otp import generate_otp

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

MAX_PASSWORD_LENGTH = 60
MAX_OTP_LENGTH = 6


def hash_password(password: str) -> str:
    if not password or len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be between 1 and {MAX_PASSWORD_LENGTH} characters."
        )
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    if (
        not plain_password
        or len(plain_password) > MAX_PASSWORD_LENGTH
        or not hashed_password
    ):
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        return False


def create_secure_otp() -> tuple[str, str]:
    """Return ``(plain_otp, otp_hash)``; the plain value is only ever emailed."""
    plain_otp = generate_otp()
    return plain_otp, secure_hash_otp(plain_otp)


def secure_hash_otp(otp: str) -> str:
    if not otp or len(otp) > MAX_OTP_LENGTH:
        raise ValueError(
            f"OTP must be between 1 and {MAX_OTP_LENGTH} characters."
        )
    return pwd_context.hash(otp)


def secure_verify_otp(plain_otp: str, hashed_otp: str | None) -> bool:
    if (
        not plain_otp
        or len(plain_otp) > MAX_OTP_LENGTH
        or not hashed_otp
    ):
        return False
    try:
        return pwd_context.verify(plain_otp, hashed_otp)
    except (ValueError, TypeError):
        return False
