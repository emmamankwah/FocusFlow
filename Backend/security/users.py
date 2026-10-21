from passlib.context import CryptContext
from model.user import UserLogin, UserRegister
from repository.user import get_user_by_email, get_user_by_username, create_user
from utilities.otp import generate_otp


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
    )



user_detail = get_user_by_email(UserLogin.email)
stored_hash = user_detail["password"] 

def hash_password(password: str) -> str:    
    return pwd_context.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    return pwd_context.verify(password, stored_hash)

def hash_otp(otp: str) -> str:
    otp = generate_otp()
    return pwd_context.hash(otp)

def verify_otp(otp: str, stored_hash: str) -> bool:
    return pwd_context.verify(otp, stored_hash)

