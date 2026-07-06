import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from deps import get_current_user
from database import save_study_plan, get_user_plans
from planner_ai.prompt_builder import build_study_plan_prompt
from planner_ai.gemini_client import generate_response
from planner_ai.validator import parse_and_validate

router = APIRouter(prefix="/planner", tags=["planner"])


class Subject(BaseModel):
    name: str
    difficulty: str
    priority: str


class GeneratePlanRequest(BaseModel):
    subjects: List[Subject]
    hours_per_day: float
    num_days: int
    exam_context: str = ""


@router.post("/generate")
def generate_plan(payload: GeneratePlanRequest, current_user: dict = Depends(get_current_user)):
    if not payload.subjects:
        raise HTTPException(400, "Add at least one subject.")

    subjects_dicts = [s.model_dump() for s in payload.subjects]
    prompt = build_study_plan_prompt(
        subjects_dicts, payload.hours_per_day, payload.num_days, payload.exam_context
    )

    raw_response = generate_response(prompt, expect_json=True)
    data, error = parse_and_validate(raw_response)

    if error:
        # One retry — LLMs occasionally slip on strict JSON formatting.
        raw_response = generate_response(prompt, expect_json=True)
        data, error = parse_and_validate(raw_response)

    if error:
        raise HTTPException(502, f"Couldn't generate a valid plan: {error}")

    save_study_plan(current_user["id"], payload.hours_per_day, payload.num_days, json.dumps(data))
    return data


@router.get("/history")
def get_history(current_user: dict = Depends(get_current_user)):
    plans = get_user_plans(current_user["id"])
    for p in plans:
        p["plan_json"] = json.loads(p["plan_json"])
    return plans