"""
security/users.py
=================

Password hashing for **account** passwords only.

OTP hashing lives in ``security/otp.py``.  Keeping the two apart removes the
duplicate ``hash_otp`` / ``verify_otp`` definitions that used to shadow the
repository function inside ``service/users.py``.

The old module also ran a database query at import time::

    user_detail = get_user_by_email(UserLogin.email)   # FieldInfo, not a str

That crashed every import and is gone; hashing is now pure and dependency-free.
"""

from passlib.context import CryptContext  # Argon2 is the only scheme we issue.

pwd_context = CryptContext(  # Shared hashing configuration.
    schemes=["argon2"],  # Modern, memory-hard password hash.
    deprecated="auto",  # Transparently accept and upgrade other schemes.
)


def hash_password(password: str) -> str:  # Produce a digest suitable for storage.
    return pwd_context.hash(password)  # Argon2 embeds its own salt and parameters.


def verify_password(password: str, stored_hash: str) -> bool:  # Check a plaintext guess.
    try:  # ``passlib`` raises on a malformed or truncated digest.
        return pwd_context.verify(password, stored_hash)  # Constant-time comparison.
    except (ValueError, TypeError):  # Unreadable hash (legacy row, NULL, corrupted data).
        return False  # A bad hash must mean "wrong password", never a 500.
