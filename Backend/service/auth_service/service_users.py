from pyexpat import errors

from model.user import (UserRegister,UserLogin,
                        ResetPassword,ChangePassword,
                        OtpRequest,OtpVerification,
                        OtpResend,UserProfileUpdate
                    )
from security.secure_users import hash_password, verify_password
from repository.authentication.user_repo import (
    get_user_by_email,
    get_user_by_username,
    create_user,
    get_user_otp,
    verify_user_otp
)
from utilities.mail import send_verification_email



def register_user(user_data: dict):
    try:
       
        password = user_data['password']
        confirm_password = user_data['confirm_password']

        if password != confirm_password:
            raise ValueError("Passwords do not match.")

        hashed_password = hash_password(password)

        create_user(
            user_data['first_name'],
            user_data['last_name'],
            user_data['email'],
            user_data['username'],
            hashed_password
        )

        return {"message": "User registered successfully"}
    except errors.UniqueViolation:
        return {"error": "Email or username already exists."}
    except ValueError as e:
        return {"error": str(e)}