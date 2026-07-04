"""
gemini_client.py
-----------------
Thin wrapper around the Gemini API. This is the ONLY file that talks
directly to Google's SDK. Everything else in the app calls into this
module rather than importing google.genai itself — that way, if we
ever swap providers, this is the only file we touch.
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()  # reads variables from your local .env file

# Read the API key once, when this module is first imported.
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Make sure you have a .env file "
        "with GEMINI_API_KEY=your_key_here in the project root."
    )

# One client instance, reused for every call (this is the recommended
# pattern — don't recreate the client on every request).
client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"  # fast + free-tier friendly, plenty for this task


def generate_response(prompt: str, expect_json: bool = False) -> str:
    """
    Sends a prompt to Gemini and returns the raw text response.

    Args:
        prompt: The full prompt string to send.
        expect_json: If True, tells Gemini to return valid JSON only
                     (no markdown fences, no commentary). We'll use
                     this for the study plan itself.

    Returns:
        The model's response as a plain string.
    """
    config = None
    if expect_json:
        config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )

    return response.text


if __name__ == "__main__":
    # Quick manual test: run `python planner/gemini_client.py` from the
    # project root to confirm your API key + connection actually work.
    test_reply = generate_response("Say hello in one short sentence.")
    print("Gemini says:", test_reply)