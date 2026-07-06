"""
database.py
-----------
SQLite schema and data access. Identical structure to the Streamlit
version — only the layer calling into it has changed (FastAPI routers
instead of Streamlit page code).
"""

import sqlite3
import os
import json
from contextlib import contextmanager
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "study_planner.db")


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                hours_per_day REAL NOT NULL,
                num_days INTEGER NOT NULL,
                plan_json TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS academic_profile (
                user_id INTEGER PRIMARY KEY,
                country TEXT,
                university TEXT,
                course TEXT,
                semester TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS syllabus_units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                unit_number INTEGER NOT NULL,
                unit_title TEXT NOT NULL,
                topics_json TEXT NOT NULL,
                estimated_hours REAL NOT NULL,
                weightage_percent REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                unit_number INTEGER NOT NULL,
                topic_name TEXT NOT NULL,
                estimated_hours REAL,
                completed INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)


# --- User queries -----------------------------------------------------

def create_user(name: str, email: str, password_hash: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, datetime.utcnow().isoformat()),
        )
        return cursor.lastrowid


def get_user_by_email(email: str):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_password(user_id: int, new_password_hash: str):
    with get_connection() as conn:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))


def update_profile(user_id: int, name: str):
    with get_connection() as conn:
        conn.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))


# --- Password reset queries --------------------------------------------

def create_password_reset(user_id: int, token: str, expires_at: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO password_resets (user_id, token, expires_at, used) VALUES (?, ?, ?, 0)",
            (user_id, token, expires_at),
        )


def get_password_reset(token: str):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM password_resets WHERE token = ?", (token,)).fetchone()
        return dict(row) if row else None


def mark_reset_used(token: str):
    with get_connection() as conn:
        conn.execute("UPDATE password_resets SET used = 1 WHERE token = ?", (token,))


# --- Study plan queries --------------------------------------------------

def save_study_plan(user_id: int, hours_per_day: float, num_days: int, plan_json: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO study_plans (user_id, created_at, hours_per_day, num_days, plan_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, datetime.utcnow().isoformat(), hours_per_day, num_days, plan_json),
        )
        return cursor.lastrowid


def get_user_plans(user_id: int):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM study_plans WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        return [dict(row) for row in rows]


# --- Academic profile queries --------------------------------------------

def save_academic_profile(user_id: int, country: str, university: str, course: str, semester: str):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO academic_profile (user_id, country, university, course, semester)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                country = excluded.country, university = excluded.university,
                course = excluded.course, semester = excluded.semester
        """, (user_id, country, university, course, semester))


def get_academic_profile(user_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM academic_profile WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


# --- Syllabus queries ------------------------------------------------------

def save_syllabus_units(user_id: int, subject: str, units: list):
    with get_connection() as conn:
        conn.execute("DELETE FROM syllabus_units WHERE user_id = ? AND subject = ?", (user_id, subject))
        conn.execute("DELETE FROM study_topics WHERE user_id = ? AND subject = ?", (user_id, subject))

        now = datetime.utcnow().isoformat()
        for unit in units:
            conn.execute("""
                INSERT INTO syllabus_units
                    (user_id, subject, unit_number, unit_title, topics_json,
                     estimated_hours, weightage_percent, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, subject, unit["unit_number"], unit["unit_title"],
                json.dumps(unit["topics"]), unit["estimated_hours"],
                unit["weightage_percent"], now,
            ))

            hours_per_topic = unit["estimated_hours"] / max(len(unit["topics"]), 1)
            for topic_name in unit["topics"]:
                conn.execute("""
                    INSERT INTO study_topics
                        (user_id, subject, unit_number, topic_name, estimated_hours, completed)
                    VALUES (?, ?, ?, ?, ?, 0)
                """, (user_id, subject, unit["unit_number"], topic_name, hours_per_topic))


def get_syllabus_subjects(user_id: int):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT subject FROM syllabus_units WHERE user_id = ? ORDER BY subject", (user_id,)
        ).fetchall()
        return [row["subject"] for row in rows]


def get_syllabus_units(user_id: int, subject: str):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM syllabus_units WHERE user_id = ? AND subject = ? ORDER BY unit_number",
            (user_id, subject),
        ).fetchall()
        results = []
        for row in rows:
            unit = dict(row)
            unit["topics"] = json.loads(unit["topics_json"])
            results.append(unit)
        return results


def get_study_topics(user_id: int, subject: str = None):
    with get_connection() as conn:
        if subject:
            rows = conn.execute(
                "SELECT * FROM study_topics WHERE user_id = ? AND subject = ? ORDER BY unit_number",
                (user_id, subject),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM study_topics WHERE user_id = ? ORDER BY subject, unit_number", (user_id,)
            ).fetchall()
        return [dict(row) for row in rows]


def set_topic_completed(topic_id: int, completed: bool):
    with get_connection() as conn:
        conn.execute("UPDATE study_topics SET completed = ? WHERE id = ?", (1 if completed else 0, topic_id))