
import logging
from psycopg2 import errors
from security.users import hash_password, verify_password
from model.user import UserLogin, UserRegister
from repository.user import (get_user_by_email, get_user_by_username, create_user)
from security.users import hash_otp, verify_otp
from utilities.mail import send_verification_email

logger = logging.getLogger(__name__)

def register_user(user: UserRegister):
    if user.password != user.confirm_password:
        logger.error("Passwords do not match.")
        return {"error": "Passwords do not match."}

    email = user.email.strip()
    username = user.username.strip()

    try:
        result_by_email = get_user_by_email(email)
        if result_by_email :
            return {"error": "Account already exists."}
        
       
            
        create_user(
                user.first_name, 
                user.last_name, 
                email,
                username, 
                hash_password(user.password)
        )
        logger.info("User created successfully.")
        return {"message": "User registered successfully."}
        
    
    except errors.UniqueViolation:
        logger.error("Email or username already exists.")
        return {"error": "Email or username already exists."}
    
    except Exception:
        logger.exception("register_user failed")
        return {"error":"Registration failed. Please try again."}

   


def login_user(user: UserLogin):
    try:
       
        existing_user = get_user_by_email(user.email) 

        if not existing_user:
            logger.info("Invalid Credentials.")
            return {"error": "Invalid Credentials ."}

        if existing_user is None:
            logger.info("User not found.")
            return {"error": "Account not found."}

        if not verify_password(user.password, existing_user["password"]):
            logger.info("Invalid Credentials.")
            return {"error": "Invalid Credentials."}  
        
        logger.info("Login successful.")
        return {"message": "Login successful."}
    
    except Exception:
        logger.info("login_user failed")
        return {"error": "Something went wrong. Please try again."}

   

def Request_otp(email: str):
    email = email.strip()
    try:
        existing_user = get_user_by_email(email)
        if not existing_user:
            logger.info("User not found.")
            return {"error": "User not found."}
        
        # Generate and send OTP logic here
        
       
        hashed_otp = send_verification_email(email)
        logger.info("OTP sent successfully.")
        return {"message": "OTP sent successfully."}
    
    except Exception:
        logger.info("Request_otp failed")
        return {"error": "Something went wrong. Please try again."}


