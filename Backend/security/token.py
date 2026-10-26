"""Signing and reading login tokens."""
import os 
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
load_dotenv()

JWT_ALGORITHM = "HS256"

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES"))


def create_access_token(subject: str) -> str:
    """Return a signed token whose ``sub`` is the user's email."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Return the claims, or ``None`` if the token is invalid or expired."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
