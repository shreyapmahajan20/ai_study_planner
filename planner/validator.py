"""
validator.py
------------
Parses and validates the JSON that Gemini returns. LLMs are usually
reliable but not perfect — they can occasionally wrap JSON in markdown
fences despite instructions, skip a field, or return a slightly wrong
shape. This module is our safety net so the UI never crashes on a
malformed response.
"""

import json
from typing import Tuple, Optional, Dict


def clean_json_text(raw_text: str) -> str:
    """
    Strips common wrappers models sometimes add even when told not to,
    like ```json ... ``` fences.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        # Remove the first line (```json or ```) and the last ``` line
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def parse_and_validate(raw_text: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Attempts to parse Gemini's response and validate its structure.

    Returns:
        (parsed_data, error_message)
        - On success: (dict, None)
        - On failure: (None, "description of what went wrong")
    """
    cleaned = clean_json_text(raw_text)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return None, f"Response wasn't valid JSON: {e}"

    # Validate the top-level shape
    if "plan" not in data:
        return None, "Response is missing the 'plan' key."

    if not isinstance(data["plan"], list) or len(data["plan"]) == 0:
        return None, "'plan' is empty or not a list."

    # Validate each day's structure so the UI can safely assume these
    # fields exist when rendering.
    for i, day in enumerate(data["plan"]):
        required_keys = {"day_number", "sessions", "tip"}
        missing = required_keys - day.keys()
        if missing:
            return None, f"Day {i + 1} is missing fields: {missing}"

        if not isinstance(day["sessions"], list) or len(day["sessions"]) == 0:
            return None, f"Day {i + 1} has no study sessions."

        for session in day["sessions"]:
            if not {"subject", "duration_minutes", "focus"} <= session.keys():
                return None, f"Day {i + 1} has a malformed session entry."

    return data, None