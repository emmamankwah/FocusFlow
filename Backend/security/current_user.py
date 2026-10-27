"""Read the signed-in user from the Bearer token."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from security.token import decode_access_token

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
        return int(claims["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token subject.")
