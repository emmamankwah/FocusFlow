"""Authentication routes and HTTP status mapping for service results."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.authentication.model.user import (
    ChangePassword,
    EmailChangeRequest,
    EmailChangeVerification,
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
    cancel_email_change as cancel_email_change_user,
    change_password as change_password_user,
    get_profile as get_profile_user,
    login_user,
    register_user,
    request_email_change as request_email_change_user,
    request_otp,
    resend_otp,
    reset_password,
    update_profile as update_profile_user,
    verify_email_change as verify_email_change_user,
    verify_otp,
    verify_reset_otp as verify_reset_otp_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(result: dict):
    """Keep service error bodies stable while returning an appropriate status."""
    error = result.get("error")
    if not error:
        return result

    message = error.lower()
    if "too many" in message:
        status_code = 429
    elif "could not" in message or "unavailable" in message:
        status_code = 503
    elif any(
        term in message
        for term in ("already registered", "already taken", "already in use")
    ):
        status_code = 409
    elif "not found" in message or "no registration" in message:
        status_code = 404
    elif "current password is incorrect" in message:
        # The Bearer token is still valid, so this is authorization, not
        # authentication. A 401 here would make clients discard the session.
        status_code = 403
    elif "invalid email or password" in message:
        status_code = 401
    else:
        status_code = 400

    return JSONResponse(status_code=status_code, content=result)


@router.post("/register")
def register(user_data: UserRegister):
    return _auth_response(register_user(user_data))


@router.post("/login")
def login(user: UserLogin):
    return _auth_response(login_user(user))


@router.post("/verify-otp")
def verify(payload: OtpVerification):
    return _auth_response(verify_otp(payload.email, payload.otp))


@router.post("/verify-reset-otp")
def verify_reset(payload: OtpVerification):
    return _auth_response(verify_reset_otp_user(payload.email, payload.otp))


@router.post("/resend-otp")
def resend(payload: OtpResend):
    return _auth_response(resend_otp(payload.email))


@router.post("/forgot-password")
def forgot_password(payload: OtpRequest):
    return _auth_response(request_otp(payload.email))


@router.post("/reset-password")
def reset(payload: ResetPassword):
    return _auth_response(
        reset_password(payload.email, payload.otp, payload.newPassword)
    )


@router.get("/profile")
def profile(user_id: int = Depends(get_current_user_id)):
    return _auth_response(get_profile_user(user_id))


@router.put("/profile")
def update_profile(
    payload: UserProfileUpdate,
    user_id: int = Depends(get_current_user_id),
):
    return _auth_response(update_profile_user(user_id, payload))


@router.post("/profile/email")
def request_email_change(
    payload: EmailChangeRequest,
    user_id: int = Depends(get_current_user_id),
):
    return _auth_response(
        request_email_change_user(
            user_id,
            payload.newEmail,
            payload.currentPassword,
        )
    )


@router.post("/profile/email/verify")
def verify_email_change(
    payload: EmailChangeVerification,
    user_id: int = Depends(get_current_user_id),
):
    return _auth_response(verify_email_change_user(user_id, payload.otp))


@router.delete("/profile/email")
def cancel_email_change(
    user_id: int = Depends(get_current_user_id),
):
    return _auth_response(cancel_email_change_user(user_id))


@router.post("/change-password")
def change_password(
    payload: ChangePassword,
    user_id: int = Depends(get_current_user_id),
):
    return _auth_response(
        change_password_user(
            user_id,
            payload.oldPassword,
            payload.newPassword,
        )
    )
