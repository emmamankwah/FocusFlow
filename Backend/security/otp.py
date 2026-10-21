from utilities.otp import generate_otp
    
from passlib.context import CryptContext

from Backend.utilities.otp import generate_otp




pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
    )

def hash_otp(otp: str) -> str:
    otp = generate_otp()
    otp = pwd_context.hash(otp)
    if otp is None:
        raise ValueError("OTP cannot be None")
    return otp


