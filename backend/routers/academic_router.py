from fastapi import APIRouter, Depends
from pydantic import BaseModel

from deps import get_current_user
from database import save_academic_profile, get_academic_profile

router = APIRouter(prefix="/academic-profile", tags=["academic"])


class AcademicProfileRequest(BaseModel):
    country: str
    university: str
    course: str
    semester: str


@router.get("")
def get_profile(current_user: dict = Depends(get_current_user)):
    profile = get_academic_profile(current_user["id"])
    return profile or {"country": "", "university": "", "course": "", "semester": ""}


@router.put("")
def update_profile(payload: AcademicProfileRequest, current_user: dict = Depends(get_current_user)):
    save_academic_profile(
        current_user["id"], payload.country, payload.university, payload.course, payload.semester
    )
    return {"message": "Academic profile saved."}