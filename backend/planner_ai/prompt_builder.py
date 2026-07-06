from typing import List, Dict


def build_study_plan_prompt(
    subjects: List[Dict],
    hours_per_day: float,
    num_days: int,
    exam_context: str = "",
) -> str:
    subject_lines = "\n".join(
        f"- {s['name']} (difficulty: {s['difficulty']}, priority: {s['priority']})"
        for s in subjects
    )

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
   concrete focus topic or activity (not just "study X" — say what to do).
5. Adds one short, encouraging tip for each day.

OUTPUT FORMAT — respond with ONLY valid JSON, no markdown fences, no
commentary before or after, matching this exact schema:

{{
  "plan": [
    {{
      "day_number": 1,
      "total_hours": {hours_per_day},
      "sessions": [
        {{"subject": "string", "duration_minutes": number, "focus": "string"}}
      ],
      "tip": "string"
    }}
  ]
}}

Return exactly {num_days} entries in the "plan" array, one per day.
"""
    return prompt.strip()