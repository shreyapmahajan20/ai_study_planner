from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from deps import get_current_user
from database import update_profile, update_password
from security import verify_password, hash_password

router = APIRouter(prefix="/profile", tags=["profile"])


class UpdateProfileRequest(BaseModel):
    name: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.get("")
def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "created_at": current_user["created_at"],
    }


@router.put("")
def update_profile_route(payload: UpdateProfileRequest, current_user: dict = Depends(get_current_user)):
    update_profile(current_user["id"], payload.name.strip())
    return {"message": "Profile updated."}


@router.put("/password")
def change_password(payload: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    if not verify_password(payload.current_password, current_user["password_hash"]):
        raise HTTPException(400, "Current password is incorrect.")
    if len(payload.new_password) < 8:
        raise HTTPException(400, "New password must be at least 8 characters.")

    update_password(current_user["id"], hash_password(payload.new_password))
    return {"message": "Password updated."}