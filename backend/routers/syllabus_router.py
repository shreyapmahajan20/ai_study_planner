from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from deps import get_current_user
from database import save_syllabus_units, get_syllabus_subjects, get_syllabus_units, get_study_topics
from syllabus_ai.extractor import extract_text
from syllabus_ai.prompt_builder import build_syllabus_extraction_prompt
from syllabus_ai.validator import parse_and_validate_syllabus
from planner_ai.gemini_client import generate_response

router = APIRouter(prefix="/syllabus", tags=["syllabus"])


@router.post("/upload")
async def upload_syllabus(
    subject: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    file_bytes = await file.read()

    try:
        raw_text = extract_text(file.filename, file_bytes)
    except ValueError as e:
        raise HTTPException(400, str(e))

    if not raw_text.strip():
        raise HTTPException(400, "Couldn't extract any text from this file. Try a different document.")

    prompt = build_syllabus_extraction_prompt(subject, raw_text)
    raw_response = generate_response(prompt, expect_json=True)
    data, error = parse_and_validate_syllabus(raw_response)

    if error:
        raw_response = generate_response(prompt, expect_json=True)
        data, error = parse_and_validate_syllabus(raw_response)

    if error:
        raise HTTPException(502, f"Couldn't extract syllabus: {error}")

    save_syllabus_units(current_user["id"], subject, data["units"])
    return data


@router.get("/subjects")
def list_subjects(current_user: dict = Depends(get_current_user)):
    return get_syllabus_subjects(current_user["id"])


@router.get("/{subject}")
def get_subject_units(subject: str, current_user: dict = Depends(get_current_user)):
    units = get_syllabus_units(current_user["id"], subject)
    topics = get_study_topics(current_user["id"], subject)
    return {"units": units, "topics": topics}