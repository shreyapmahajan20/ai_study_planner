"""
auth_router.py
--------------
All authentication endpoints. Each one returns plain JSON — no HTML,
no templating — because the frontend (dashboard.html/login.html) is
now a completely separate piece that calls these via fetch().
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone

from database import (
    create_user, get_user_by_email, update_password,
    create_password_reset, get_password_reset, mark_reset_used,
)
from security import hash_password, verify_password, create_jwt, generate_reset_token
from email_utils import send_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/signup")
def signup(payload: SignupRequest):
    email_clean = payload.email.lower()

    if len(payload.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters.")
    if get_user_by_email(email_clean):
        raise HTTPException(400, "An account with this email already exists.")

    user_id = create_user(payload.name.strip(), email_clean, hash_password(payload.password))
    token = create_jwt(user_id, email_clean)
    return {"token": token, "user": {"id": user_id, "name": payload.name, "email": email_clean}}


@router.post("/login")
def login(payload: LoginRequest):
    user = get_user_by_email(payload.email.lower())
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(401, "Incorrect email or password.")

    token = create_jwt(user["id"], user["email"])
    return {"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):
    user = get_user_by_email(payload.email.lower())

    # Always return the same response whether or not the email exists —
    # this prevents attackers from using this endpoint to discover which
    # emails are registered.
    if user:
        token = generate_reset_token()
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        create_password_reset(user["id"], token, expires_at)
        try:
            send_reset_email(user["email"], token)
        except Exception as e:
            raise HTTPException(500, f"Couldn't send email: {e}")

    return {"message": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):
    reset_record = get_password_reset(payload.token)
    now = datetime.now(timezone.utc)

    valid = (
        reset_record
        and not reset_record["used"]
        and datetime.fromisoformat(reset_record["expires_at"]) > now
    )
    if not valid:
        raise HTTPException(400, "This reset link is invalid or has expired.")

    if len(payload.new_password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters.")

    update_password(reset_record["user_id"], hash_password(payload.new_password))
    mark_reset_used(payload.token)
    return {"message": "Password reset successfully."}