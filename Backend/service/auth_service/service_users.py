from pyexpat import errors

from model.user import (UserRegister,UserLogin,
                        ResetPassword,ChangePassword,
                        OtpRequest,OtpVerification,
                        OtpResend,UserProfileUpdate
                    )
from security.secure_users import (hash_password, verify_password,
                                   hash_otp,secure_verify_otp
                                )
from repository.authentication.user_repo import (
    get_user_by_email,
    get_user_by_username,
    create_user,
    get_user_otp,
    verify_user_otp
)
from utilities.mail import send_verification_email
from typing import Dict


def register_user(user_data: UserRegister) -> Dict:
    try:
        email = user_data['email']

        if get_user_by_email(email):
            return {"error": "Email already exists."}
        
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



def login_user(user: UserLogin) -> Dict:
    try:
        existing_user = get_user_by_email(user.email.strip())

        if not existing_user :
            return {"error": "Invalid credentials."}

        user_password = user.password
        server_password = existing_user['confirm_password']

        if not verify_password(user_password, server_password):
            return {"error": "Invalid credentials."}
        
        return {"message": "Login successful."}

    except Exception:
        return {"error": "Something went wrong. Please try again."}



def request_otp(email: str) -> Dict:
    try:
        otp_request = OtpRequest(email=email)
        existing_user = get_user_by_email(email)

        if not existing_user:
            return {"error": "Invalid email."}

        send_verification_email(otp_request.email)

        return {"message": "OTP sent successfully."}

    except Exception:
        return {"error": "Something went wrong. Please try again."}




def verify_otp(email: str, otp: str) -> Dict:
    try:
        otp_user = OtpVerification(email=email, otp=otp)
        existing_user = verify_user_otp(email)

        if not existing_user:
            return {"error": "Invalid email."}

        hashed_otp = existing_user.hashed_otp
        plain_otp = otp_user.otp

        if not secure_verify_otp(plain_otp, hashed_otp):
            return {"error": "Invalid OTP."}

        return {"message": "OTP verified successfully."}

    except Exception:
        return {"error": "Something went wrong. Please try again."}