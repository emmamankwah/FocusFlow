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
    verify_user_otp,
    clear_otp,
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

        user_otp = get_user_otp(email)

        if not user_otp.email:
            return {"error": "OTP request failed."}


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

        clear_otp(email)

        return {"message": "OTP verified successfully."}

    except Exception:
        return {"error": "Something went wrong. Please try again."}


def resend_otp(email: str) -> Dict:
    try:
        otp_resend = OtpResend(email=email)
        existing_user = get_user_by_email(email)

        if not existing_user:
            return {"error": "Invalid email."}

        get_otp = get_user_otp(otp_resend.email)

        if get_otp is not None:
            clear_otp(email)

        send_verification_email(otp_resend.email)

        return {"message": "OTP resent successfully."}

    except Exception:
        return {"error": "Something went wrong. Please try again."}





def reset_password(email: str, otp: str, new_password: str) -> Dict:
    try:
        reset_password = ResetPassword(email=email, otp=otp, new_password=new_password)
        existing_user = get_user_by_email(reset_password.email)

        if not existing_user:
            return {"error": "Invalid email."}

        hashed_otp = existing_user.hashed_otp
        plain_otp = reset_password.otp

        if not secure_verify_otp(plain_otp, hashed_otp):
            return {"error": "Invalid OTP."}

        hashed_new_password = hash_password(reset_password.new_password)

        # Update the user's password in the database
        # Assuming you have a function to update the password
        update_user_password(email, hashed_new_password)

        return {"message": "Password reset successfully."}

    except Exception:
        return {"error": "Something went wrong. Please try again."}