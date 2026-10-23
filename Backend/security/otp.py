"""
security/otp.py
===============

Generation and constant-time verification of one-time passcodes.

The old file imported ``generate_otp`` twice, once from ``utilities.otp`` and
once from ``Backend.utilities.otp``.  The second import raised
``ModuleNotFoundError: No module named 'Backend'`` and made this module
unimportable.  There is now exactly one import.
"""

from passlib.context import CryptContext  # Argon2 for the short-lived code digest.

from utilities.otp import generate_otp  # Cryptographically secure digit generator.

pwd_context = CryptContext(  # Shared hashing configuration.
    schemes=["argon2"],  # Slow hashing makes offline brute-force of the six digits expensive.
    deprecated="auto",  # Transparently accept older schemes if the config changes.
)


def create_secure_otp() -> tuple[str, str]:  # Produce a code and its digest together.
    """Return ``(plain_otp, otp_hash)``; the plain value is only ever emailed."""
    plain_otp = generate_otp()  # Six digits from ``secrets``, not ``random``.
    return plain_otp, pwd_context.hash(plain_otp)  # Hash before anything else can see it.


def hash_existing_otp(plain_otp: str) -> str:  # Re-hash a code, e.g. when re-issuing.
    if not plain_otp:  # An empty code is never valid.
        raise ValueError("OTP cannot be empty")  # Fail loudly instead of storing a usable empty hash.
    return pwd_context.hash(plain_otp)  # Argon2 embeds the salt.


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:  # Compare a submitted code with its digest.
    if not plain_otp or not hashed_otp:  # Guard against empty or NULL values.
        return False  # An absent code never matches.
    try:  # ``passlib`` raises on a malformed digest.
        return pwd_context.verify(plain_otp, hashed_otp)  # Constant-time comparison.
    except (ValueError, TypeError):  # Corrupted or legacy hash.
        return False  # Treat it as a mismatch, never a 500.
