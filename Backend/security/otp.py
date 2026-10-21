from utilities.otp import generate_otp
    
from passlib.context import CryptContext

from Backend.utilities.otp import generate_otp




pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
    )

def create_secure_otp() -> tuple[str, str]:
    plain_otp = generate_otp()
    hash_otp = pwd_context.hash(plain_otp)
    if plain_otp is None:
        raise ValueError("OTP cannot be None")
    return plain_otp,hash_otp


def hash_existing_otp(plain_otp: str) -> str:  
    
    if plain_otp is None:
        raise ValueError("OTP cannot be None")
    return pwd_context.hash(plain_otp)


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    return pwd_context.verify(plain_otp, hashed_otp)

