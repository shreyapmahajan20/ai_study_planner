"""
prompt_builder.py
------------------
Turns raw user input (subjects, hours, days) into a carefully engineered
prompt string for Gemini. This is where "prompt engineering" actually
lives in this project — keeping it separate from the API call itself
and the UI means we can iterate on prompt wording without touching
anything else.
"""

from typing import List, Dict


def build_study_plan_prompt(
    subjects: List[Dict],
    hours_per_day: float,
    num_days: int,
    exam_context: str = "",
) -> str:
    """
    Builds the prompt we send to Gemini to generate a study plan.

    Args:
        subjects: list of dicts like
            {"name": "Data Structures", "difficulty": "Hard", "priority": "High"}
        hours_per_day: how many hours the student can study per day
        num_days: how many days the plan should cover
        exam_context: optional free-text like "exam in 10 days, weak in DP"

    Returns:
        A single prompt string ready to send to Gemini.
    """

    # Format the subject list into a clean, readable block for the model.
    subject_lines = "\n".join(
        f"- {s['name']} (difficulty: {s['difficulty']}, priority: {s['priority']})"
        for s in subjects
    )

    # This is the core of the "prompt engineering" lesson:
    # 1. Give the model a clear role.
    # 2. Give it the exact data it needs.
    # 3. Tell it EXACTLY what shape the output must be (schema),
    #    so we can reliably parse it afterwards.
    # 4. Give explicit rules to prevent common failure modes
    #    (e.g. ignoring a subject, uneven allocation, vague sessions).
    prompt = f"""
You are an expert academic study planner who creates realistic, well-balanced
study schedules for students.

STUDENT'S SITUATION:
- Available study time per day: {hours_per_day} hours
- Number of days to plan for: {num_days}
- Subjects to cover:
{subject_lines}
- Additional context from student: {exam_context or "None provided"}

YOUR TASK:
Create a day-by-day study plan that:
1. Allocates MORE time to subjects marked "Hard" difficulty or "High" priority.
2. Never exceeds the {hours_per_day} hour daily limit.
3. Includes every single subject listed at least twice across the full plan.
4. Breaks each day into specific sessions with a subject, duration, and a
   concrete focus topic or activity (not just "study X" — say what to do,
   e.g. "Practice recursion problems" not "study DSA").
5. Adds one short, encouraging tip for each day (e.g. a break reminder,
   a revision technique, or motivation).

OUTPUT FORMAT — respond with ONLY valid JSON, no markdown fences, no
commentary before or after, matching this exact schema:

{{
  "plan": [
    {{
      "day_number": 1,
      "total_hours": {hours_per_day},
      "sessions": [
        {{
          "subject": "string",
          "duration_minutes": number,
          "focus": "string - specific topic or task"
        }}
      ],
      "tip": "string - one short encouraging tip for this day"
    }}
  ]
}}

Return exactly {num_days} entries in the "plan" array, one per day.
"""
    return prompt.strip()