import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"


def generate_response(prompt: str, expect_json: bool = False) -> str:
    config = None
    if expect_json:
        config = types.GenerateContentConfig(response_mime_type="application/json")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )
    return response.text