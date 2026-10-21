
import logger
from psycopg2 import errors
from backend.security.users import hash_password, verify_password
from model.user import UserLogin, UserRegister
from backend.repository.user import get_user_by_email, get_user_by_username, create_user

logger = logger.get_logger(__name__)

def register_user(user: UserRegister):
    if user.password != user.confirm_password:
        logger.error("Passwords do not match.")
        return {"error": "Passwords do not match."}

    email = user.email.srtip()
    username = user.username.strip()

    try:
        result_by_email = get_user_by_email(email)
        result_by_username = get_user_by_username(username)
        if result_by_email and result_by_username:
            return {"error": "Account already exists."}
        
       
            
        return create_user(
                user.first_name, 
                user.last_name, 
                email,
                username, 
                hash_password(user.password)
        )
        
    
    except errors.UniqueViolation:
        logger.error("Email or username already exists.")
        return {"error": "Email or username already exists."}
    
    except Exception:
        logger.info("register_user failed")
        return {"error":"Registration failed. Please try again."}

   


def login_user(user: UserLogin):
    try:
       
        existing_user = get_user_by_email(user.email) and get_user_by_username(user.username)  
        logger.info("User not found.")

        if not existing_user:
            return {"error": "User not found."}

        if not verify_password(user.password, existing_user["password"]):
            logger.info("Invalid password.")
            return {"error": "Invalid password."}  
        
        logger.info("Login successful.")
        return {"message": "Login successful."}
    
    except Exception:
        logger.info("login_user failed")
        return {"error": "Something went wrong. Please try again."}

   

        