"""
deps.py
-------
Shared FastAPI dependencies. get_current_user is the key one — any
route that includes it as a parameter automatically requires a valid
JWT in the Authorization header, and gets the real user record handed
to it. This is the FastAPI equivalent of the Streamlit get_current_user()
function, but wired into the request/response cycle properly instead
of reading from session state.
"""

from fastapi import Header, HTTPException, status
from security import decode_jwt
from database import get_user_by_id


def get_current_user(authorization: str = Header(None)):
    """
    Expects a header like: Authorization: Bearer <jwt_token>
    Raises 401 if missing, malformed, expired, or invalid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
        )

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_jwt(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
        )

    return user