def build_syllabus_extraction_prompt(subject_name: str, raw_text: str) -> str:
    trimmed_text = raw_text[:15000]

    prompt = f"""
You are analyzing a university course syllabus document for the subject
"{subject_name}". Below is the raw extracted text from the syllabus file.
It may contain formatting artifacts, page numbers, or unrelated header/footer
text — ignore anything that isn't actual syllabus content.

RAW SYLLABUS TEXT:
---
{trimmed_text}
---

YOUR TASK:
Identify each unit/module/chapter in this syllabus and break it down into
its individual topics. For each unit, also estimate:
- A reasonable number of study hours needed to cover it
- An approximate exam weightage percentage (distribute evenly if the
  syllabus doesn't specify marks distribution)

OUTPUT FORMAT — respond with ONLY valid JSON, no markdown fences, no
commentary, matching this exact schema:

{{
  "units": [
    {{
      "unit_number": 1,
      "unit_title": "string",
      "topics": ["string", "string"],
      "estimated_hours": number,
      "weightage_percent": number
    }}
  ]
}}

Rules:
- Extract EVERY unit you can find. Do not skip any.
- Each topic should be a short, specific phrase.
- If the document doesn't look like a syllabus at all, return {{"units": []}}.
"""
    return prompt.strip()