"""Authentication routes.

The service layer reports failures as ``{"error": "..."}`` with HTTP 200, so
these handlers simply pass the model straight through. Profile and password
routes also require a Bearer token and return 401 when it is missing or invalid.
"""

from fastapi import APIRouter, Depends

from app.authentication.model.user import (
    ChangePassword,
    OtpRequest,
    OtpResend,
    OtpVerification,
    ResetPassword,
    UserLogin,
    UserProfileUpdate,
    UserRegister,
)
from app.authentication.security.current_user import get_current_user_id
from app.authentication.service.auth_service.service_users import (
    change_password as change_password_user,
    get_profile as get_profile_user,
    login_user,
    register_user,
    request_otp,
    resend_otp,
    reset_password,
    update_profile as update_profile_user,
    verify_otp,
    verify_reset_otp as verify_reset_otp_user,
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


@router.post("/verify-reset-otp")
def verify_reset(payload: OtpVerification):
    return verify_reset_otp_user(payload.email, payload.otp)


@router.post("/resend-otp")
def resend(payload: OtpResend):
    return resend_otp(payload.email)


@router.post("/forgot-password")
def forgot_password(payload: OtpRequest):
    return request_otp(payload.email)


@router.post("/reset-password")
def reset(payload: ResetPassword):
    return reset_password(payload.email, payload.otp, payload.newPassword)


@router.get("/profile")
def profile(user_id: int = Depends(get_current_user_id)):
    return get_profile_user(user_id)


@router.put("/profile")
def update_profile(
    payload: UserProfileUpdate,
    user_id: int = Depends(get_current_user_id),
):
    return update_profile_user(user_id, payload)


@router.post("/change-password")
def change_password(
    payload: ChangePassword,
    user_id: int = Depends(get_current_user_id),
):
    return change_password_user(
        user_id,
        payload.email,
        payload.oldPassword,
        payload.newPassword,
    )
