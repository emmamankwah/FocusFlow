"""Signing and reading login tokens."""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from jose import JWTError, jwt

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

JWT_ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

TOKEN_TYPE = "access"


def create_access_token(subject: str) -> str:
    """Return a signed, short-lived access token for ``subject``."""
    if not subject:
        raise ValueError("Token subject cannot be empty.")

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "token_type": TOKEN_TYPE,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Return the claims, or ``None`` if the token is invalid or expired."""
    if not isinstance(token, str) or not token:
        return None

    try:
        claims = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={
                "require_exp": True,
                "require_iat": True,
                "require_sub": True,
            },
        )
    except JWTError:
        return None

    if claims.get("token_type") != TOKEN_TYPE:
        return None
    if not isinstance(claims.get("sub"), str) or not claims["sub"]:
        return None
    return claims
