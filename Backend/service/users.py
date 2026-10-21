

from psycopg2 import errors
from security.users import Register_password, login_password
from model.user import UserLogin, UserRegister
from backend.repository.user import get_user_by_email, get_user_by_username, create_user



def register_user(user: UserRegister):
    if user.password != user.confirm_password:
        return {"error": "Passwords do not match."}

    email = user.email

    try:
        result_by_email = get_user_by_email(email)
        result_by_username = get_user_by_username(user.username)
        if result_by_email and result_by_username:
            return {"error": "Account already exists."}
        
        hash_password = Register_password(user)
            
        return create_user(user.first_name, user.last_name, email, user.username, hash_password)
       
    
    except errors.UniqueViolation:
        return {"error": "Email or username already exists."}
    
    except Exception:
        return ("register_user failed")

   


def login_user(user: UserLogin):
    try:
        result_by_email = get_user_by_email(user.email)
        existing_user = get_user_by_email(user.email) and get_user_by_username(user.username)  

        if not existing_user:
            return {"error": "User not found."}

        hash_password = Register_password(user)
        strored_password = result_by_email["password"]

        if hash_password != strored_password:
            return {"error": "Incorrect password."}
        
    except Exception:
        return {"error": "Something went wrong. Please try again."}

   

        