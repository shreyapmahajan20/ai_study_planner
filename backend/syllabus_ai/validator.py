import json
from typing import Tuple, Optional, Dict


def clean_json_text(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def parse_and_validate_syllabus(raw_text: str) -> Tuple[Optional[Dict], Optional[str]]:
    cleaned = clean_json_text(raw_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return None, f"Response wasn't valid JSON: {e}"

    if "units" not in data:
        return None, "Response is missing the 'units' key."
    if not isinstance(data["units"], list):
        return None, "'units' is not a list."
    if len(data["units"]) == 0:
        return None, "No units could be extracted. Try a clearer syllabus document."

    for i, unit in enumerate(data["units"]):
        required_keys = {"unit_number", "unit_title", "topics", "estimated_hours", "weightage_percent"}
        missing = required_keys - unit.keys()
        if missing:
            return None, f"Unit {i + 1} is missing fields: {missing}"
        if not isinstance(unit["topics"], list) or len(unit["topics"]) == 0:
            return None, f"Unit {i + 1} has no topics."

    return data, None