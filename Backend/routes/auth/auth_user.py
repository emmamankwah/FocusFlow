"""Authentication routes.

The service layer reports failures as ``{"error": "..."}`` with HTTP 200, so
these handlers simply pass the model straight through.
"""

from fastapi import APIRouter

from model.user import (
    OtpRequest,
    OtpResend,
    OtpVerification,
    ResetPassword,
    UserLogin,
    UserRegister,
)
from service.auth_service.service_users import (
    login_user,
    register_user,
    request_otp,
    resend_otp,
    reset_password,
    verify_otp,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user_data: UserRegister):
    return register_user(user_data)


@router.post("/login")
def login(user: UserLogin):
    return login_user(user)


@router.post("/verify-otp")
def verify(payload: OtpVerification):
    return verify_otp(payload.email, payload.otp)


@router.post("/resend-otp")
def resend(payload: OtpResend):
    return resend_otp(payload.email)


@router.post("/forgot-password")
def forgot_password(payload: OtpRequest):
    return request_otp(payload.email)


@router.post("/reset-password")
def reset(payload: ResetPassword):
    return reset_password(payload.email, payload.otp, payload.newPassword)
