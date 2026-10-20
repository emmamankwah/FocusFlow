# from utilities.otp import generate_otp

from passlib.context import CryptContext

# from Backend.utilities import otp

generate_otp = 'hellowoelrd'
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
    )

def hash_otp(otp: str) -> str:
    otp = generate_otp
    otp = pwd_context.hash(otp)
    if otp is None:
        raise ValueError("OTP cannot be None")
    return otp

if __name__ == "__main__":
    # otp = generate_otp()
    hashed_otp = hash_otp(generate_otp)
    print(f"Generated OTP: {generate_otp}")
    print(f"Hashed OTP: {hashed_otp}")
