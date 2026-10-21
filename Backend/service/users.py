
import logging
from psycopg2 import errors
from Backend.security import otp
from security.users import hash_password, verify_password
from model.user import UserLogin, UserRegister
from repository.user import (get_user_by_email, get_user_by_username, create_user,otp_request, verify_otp,get_user_otp, verify_user_otp,clear_otp_record, increment_attempts,increment_attempts)
from security.users import hash_otp, verify_otp
from utilities.mail import send_verification_email

logging = logging.getLogger(__name__)


def register_user(user: UserRegister):
    if user.password != user.confirm_password:
        logging.error("Passwords do not match.")
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
        logging.info("User created successfully.")
        return {"message": "User registered successfully."}
        
    
    except errors.UniqueViolation:
        logging.error("Email or username already exists.")
        return {"error": "Email or username already exists."}
    
    except Exception:
        logging.exception("register_user failed")
        return {"error":"Registration failed. Please try again."}

   


def login_user(user: UserLogin):
    try:
       
        existing_user = get_user_by_email(user.email) 

        if not existing_user:
            logging.info("Invalid Credentials.")
            return {"error": "Invalid Credentials ."}

        if existing_user is None:
            logging.info("User not found.")
            return {"error": "Account not found."}

        if not verify_password(user.password, existing_user["password"]):
            logging.info("Invalid Credentials.")
            return {"error": "Invalid Credentials."}  
        
        logging.info("Login successful.")
        return {"message": "Login successful."}
    
    except Exception:
        logging.info("login_user failed")
        return {"error": "Something went wrong. Please try again."}

   

def Request_otp(email: str):
    email = email.strip()
    try:
        existing_user = get_user_by_email(email)
        otp_user = otp_request(email)
        if not existing_user:
            logging.info("User not found.")
            return {"error": "User not found."}
        
       
       
        hashed_otp = send_verification_email(email)
        logging.info("OTP sent successfully.")
        return {"message": "OTP sent successfully."}
    
    except Exception:
        logging.info("Request_otp failed")
        return {"error": "Something went wrong. Please try again."}




def verify_otp(email: str, user_otp: str):
    email = email.strip()
    user_otp = user_otp.strip()
    try:
        otp_record = get_user_otp(email)
        if not otp_record:
            logging.info("OTP record not found.")
            return {"error": "OTP record not found."}

        if otp_record["attempts"] >= otp_record["total_attempts"]:
            logging.info(" OTP limits exceeded.")
            return {"error": " OTP limits exceeded."}

        if otp_record['expired_at'] > otp_record['created_at']:
            logging.info("OTP has expired.")
            return {"error": "OTP has expired."}

        verification_result = verify_otp(email, user_otp)
        if not verification_result:
            increment_attempts(email)
            logging.info("Invalid OTP.")
            return {"error": "Invalid OTP."}

        clear_otp_record(email)
        logging.info("OTP verified successfully.")
        return {"message": "OTP verified successfully."}
    except Exception:
        logging.info("verify_otp failed")
        return {"error": "Something went wrong. Please try again."}
