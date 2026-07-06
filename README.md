# 💡 AI Study Planner

A FastAPI + React app that generates a personalized, day-by-day study schedule using Google's Gemini API — built to be genuinely usable, not just a demo.

## Features
- Add multiple subjects with difficulty and priority levels
- Set available daily study hours and number of days to plan
- Gemini generates a structured, realistic schedule with focused sessions and daily tips
- Clean, custom-designed UI (not default Streamlit styling)

## Project Structure
```
ai-study-planner/
├── app.py                 # Streamlit UI entrypoint
├── planner/
│   ├── prompt_builder.py  # Builds the Gemini prompt
│   ├── gemini_client.py   # Handles API calls
│   └── validator.py       # Parses & validates the response
├── .env                    # Your API key (never committed)
├── .env.example
├── requirements.txt
└── README.md
```

## Local Setup

1. Clone the repo and create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

4. Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_key_here
```

5. Run the app:
```bash
streamlit run app.py
```

## Deploying to Streamlit Community Cloud

1. Push this project to a public (or private) GitHub repo — **make sure `.env` is in `.gitignore` and never committed**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub account.
3. Select the repo and set `app.py` as the entrypoint.
4. Under **Settings → Secrets**, add:
```
GEMINI_API_KEY = "your_key_here"
```
5. Deploy. Your app gets a public `.streamlit.app` URL.

## Tech Stack
- Python
- Streamlit
- Google Gemini API (`google-genai` SDK)

## Learning Notes
This project was built to practice: calling an LLM API, structured prompt engineering (requesting JSON output with an explicit schema), response validation with retry logic, and custom UI styling in Streamlit.
