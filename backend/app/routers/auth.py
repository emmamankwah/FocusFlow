from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from datetime import datetime,timedelta,timezone
from app.core.security import authenticate_user, create_access_token, get_current_user, hash_password,generate_otp
from app.core.outbox import enqueue_verification_email
from app.database.session import get_db
from app.models.users import User
from app.models.pending_users import PendingUser
from app.schemas.user import Token, UserCreate, UserLogin, UserOut

# Router for authentication and account-related endpoints.
router = APIRouter()


# Register a new user account.
# This route validates that the email is not already in use, hashes the password,
# and saves a pending registration before sending the verification code.
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Prevent duplicate accounts across both active and pending registrations.
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    existing_pending = db.query(PendingUser).filter(PendingUser.email == user_in.email).first()
    if existing_user or existing_pending:
        raise HTTPException(status_code=400, detail="Email already registered")

    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=3)

    pending = db.query(PendingUser).filter(PendingUser.email == user_in.email).first()
    if pending:
        pending.hashed_password = hash_password(user_in.password)
        pending.first_name = user_in.first_name
        pending.last_name = user_in.last_name
        pending.timezone = user_in.timezone
        pending.otp_code = hash_password(otp)
        pending.otp_expires_at = expires_at
    else:
        pending = PendingUser(
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            timezone=user_in.timezone,
            otp_code=hash_password(otp),
            otp_expires_at=expires_at,
        )

        db.add(pending)

    try:
        enqueue_verification_email(db, user_in.email, otp)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"message": "Verification code queued for email delivery"}


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a signed JWT access token."""
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile from the token."""
    return current_user