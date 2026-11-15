"""Read the signed-in user from the Bearer token."""

import psycopg2
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.authentication.repository.authentication.user_repo import get_token_version
from app.authentication.security.token import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    claims = decode_access_token(credentials.credentials)
    if claims is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    try:
        user_id = int(claims["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token subject.")

    raw_version = claims.get("ver", 0)
    try:
        token_version = int(raw_version)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token version.")
    if token_version < 0:
        raise HTTPException(status_code=401, detail="Invalid token version.")

    try:
        current_version = get_token_version(user_id)
    except (ConnectionError, psycopg2.Error):
        raise HTTPException(status_code=503, detail="Authentication unavailable.")

    if current_version is None:
        raise HTTPException(status_code=401, detail="User no longer exists.")
    if current_version != token_version:
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated. Please log in again.",
        )

    return user_id
