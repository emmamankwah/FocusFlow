from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.outbox import enqueue_verification_email
from app.core.security import generate_otp, hash_password, verify_password
from app.database.session import get_db
from app.models.pending_users import PendingUser
from app.models.users import User
from app.schemas.user import ResendOtpRequest, VerifyEmailRequest

router = APIRouter()
#Number of attempts
MAX_OTP_ATTEMPTS = 3
LOCK_OUT_MESSAGE = "Too many incorrect attempts, please re-enter email to get new OTP"

@router.post("/resend-otp")
def resend_otp(payload: ResendOtpRequest, db: Session = Depends(get_db)):
    pending_user = (
        db.query(PendingUser)
        .filter(PendingUser.email == payload.email)
        .with_for_update()
        .populate_existing()
        .first()
    )
    if not pending_user:
        raise HTTPException(status_code=404, detail="Pending registration not found")
    now = datetime.now(timezone.utc)
    otp_expires_at = pending_user.otp_expires_at
    if otp_expires_at is not None and otp_expires_at.tzinfo is None:
        otp_expires_at = otp_expires_at.replace(tzinfo=timezone.utc)

    if otp_expires_at is not None:
        sent_at = otp_expires_at - timedelta(minutes=3)
        if now < sent_at + timedelta(seconds=60):
            raise HTTPException(status_code=429, detail="Please wait a minute before requesting another code")

    if otp_expires_at is not None and otp_expires_at > now:
        raise HTTPException(status_code=400, detail="The current OTP has not expired yet")

    otp = generate_otp()
    pending_user.otp_code = hash_password(otp)
    pending_user.otp_expires_at = now + timedelta(minutes=3)
    pending_user.otp_attempts = 0
    try:
        enqueue_verification_email(db, pending_user.email, otp)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"message": "A new verification code has been queued for delivery"}


@router.post("/verify-email")
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    # Find the pending registration associated with the submitted email address.
    pending_user = (
        db.query(PendingUser)
        .filter(PendingUser.email == payload.email)
        .with_for_update()
        .first()
    )
    if not pending_user:
        existing_user = db.query(User).filter(User.email == payload.email).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Email is already verified")
        raise HTTPException(status_code=404, detail="Pending registration not found")
    
    if pending_user.otp_attempts >= MAX_OTP_ATTEMPTS:
        raise HTTPException(status_code=429, detail =LOCK_OUT_MESSAGE)

    # MySQL DATETIME values are returned without timezone info; treat stored values as UTC.
    otp_expires_at = pending_user.otp_expires_at
    if otp_expires_at is not None and otp_expires_at.tzinfo is None:
        otp_expires_at = otp_expires_at.replace(tzinfo=timezone.utc)

    # Require a stored OTP that has not passed its expiry time.
    if not pending_user.otp_code or not otp_expires_at or otp_expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired, request a new one")

    # Compare the submitted code against the stored password-style hash.
    if not verify_password(payload.otp, pending_user.otp_code):
        pending_user.otp_attempts += 1
        db.commit()
        if pending_user.otp_attempts >= MAX_OTP_ATTEMPTS:
            raise HTTPException(status_code=429, detail=LOCK_OUT_MESSAGE)
        remaining = MAX_OTP_ATTEMPTS - pending_user.otp_attempts
        raise HTTPException(status_code=400, detail=f"Invalid OTP, {remaining} attempts left")

    existing_user = db.query(User).filter(User.email == pending_user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email is already verified")

    # Promote the pending user to the verified account table.
    user = User(
        first_name=pending_user.first_name,
        last_name=pending_user.last_name,
        email=pending_user.email,
        hashed_password=pending_user.hashed_password,
        timezone=pending_user.timezone,
        is_verified=True,
    )
    db.add(user)
    db.delete(pending_user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        existing_user = db.query(User).filter(User.email == payload.email).first()
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Email is already verified",
            ) from exc
        raise
    return {"message": "Email verified successfully"}