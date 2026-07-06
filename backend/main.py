"""
main.py
-------
FastAPI application entrypoint. This is the equivalent of app.py in the
Streamlit version, except now it ONLY serves JSON data — no HTML
rendering happens here at all. The frontend (a separate set of static
HTML/JS files) is responsible for everything visual.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import auth_router, profile_router, planner_router, syllabus_router, academic_router

app = FastAPI(title="AI Study Planner API")

# CORS: allows the frontend (served from a different origin/port, e.g.
# http://localhost:5500 via Live Server) to actually call this API.
# Without this, the browser blocks the requests silently as a security
# measure (the "Same-Origin Policy").
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local dev only — tighten this before any real deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"status": "AI Study Planner API is running"}


app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(planner_router.router)
app.include_router(syllabus_router.router)
app.include_router(academic_router.router)