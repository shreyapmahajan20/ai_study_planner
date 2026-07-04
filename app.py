"""
app.py
------
The Streamlit UI entrypoint. This file is intentionally "dumb" about
AI logic — it collects input, calls into planner.gemini_client via
planner.prompt_builder, validates with planner.validator, and renders
the result. All the actual intelligence lives in the planner/ package.
"""

import streamlit as st
from planner.prompt_builder import build_study_plan_prompt
from planner.gemini_client import generate_response
from planner.validator import parse_and_validate

st.set_page_config(
    page_title="Study Plan — Illuminated",
    page_icon="💡",
    layout="wide",
)

# ---------------------------------------------------------------------------
# THEME: "a desk lamp at night" — deep indigo background, warm amber glow
# for primary actions, soft mint for progress. Custom design tokens below,
# not default Streamlit styling.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

    :root {
        --bg: #14162B;
        --surface: #1F2340;
        --surface-raised: #262B4D;
        --accent-amber: #F2A65A;
        --accent-mint: #6FCF97;
        --text-primary: #F5F3EE;
        --text-muted: #A9ACC4;
        --hard-tag: #E8735C;
        --medium-tag: #F2C14E;
        --easy-tag: #6FCF97;
    }

    .stApp {
        background: linear-gradient(180deg, #14162B 0%, #191C36 100%);
        color: var(--text-primary);
    }

    h1, h2, h3 { font-family: 'Fraunces', serif !important; font-weight: 600 !important; }
    p, div, span, label { font-family: 'Inter', sans-serif; }

    .hero-title {
        font-family: 'Fraunces', serif;
        font-size: 2.6rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0;
    }
    .hero-sub {
        color: var(--text-muted);
        font-size: 1.05rem;
        margin-top: 4px;
    }

    /* Day card — the core visual unit of the plan */
    .day-card {
        background: var(--surface);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        border: 1px solid rgba(242, 166, 90, 0.15);
        position: relative;
    }
    .day-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: radial-gradient(circle, var(--accent-amber) 0%, #C97A3A 100%);
        color: #14162B;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.95rem;
        box-shadow: 0 0 18px rgba(242, 166, 90, 0.45);
        margin-right: 12px;
    }
    .day-header-row {
        display: flex;
        align-items: center;
        margin-bottom: 14px;
    }
    .day-title {
        font-family: 'Fraunces', serif;
        font-size: 1.3rem;
        font-weight: 600;
    }

    .session-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .session-row:last-of-type { border-bottom: none; }
    .session-subject { font-weight: 600; color: var(--text-primary); }
    .session-focus { color: var(--text-muted); font-size: 0.9rem; }
    .session-duration {
        font-family: 'JetBrains Mono', monospace;
        color: var(--accent-mint);
        font-size: 0.85rem;
        white-space: nowrap;
        margin-left: 16px;
    }

    .tip-box {
        margin-top: 16px;
        padding: 12px 16px;
        background: rgba(111, 207, 151, 0.08);
        border-left: 3px solid var(--accent-mint);
        border-radius: 6px;
        color: var(--text-muted);
        font-size: 0.9rem;
        font-style: italic;
    }

    .tag-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 8px;
    }

    div[data-testid="stForm"] {
        background: var(--surface);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.06);
    }

    .stButton button, .stFormSubmitButton button {
        background: linear-gradient(135deg, var(--accent-amber), #C97A3A);
        color: #14162B;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        box-shadow: 0 0 16px rgba(242, 166, 90, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-title">💡 Your Study Plan, Illuminated</div>
    <div class="hero-sub">Tell it what you're studying and how much time you have — Gemini builds the schedule.</div>
    <br>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# SESSION STATE: holds the dynamic list of subjects across reruns
# ---------------------------------------------------------------------------
if "subjects" not in st.session_state:
    st.session_state.subjects = [{"name": "", "difficulty": "Medium", "priority": "Medium"}]

col_form, col_results = st.columns([1, 1.6], gap="large")

with col_form:
    st.subheader("Your subjects")

    for i, subject in enumerate(st.session_state.subjects):
        c1, c2, c3, c4 = st.columns([2.2, 1, 1, 0.4])
        subject["name"] = c1.text_input(
            "Subject", value=subject["name"], key=f"name_{i}", label_visibility="collapsed",
            placeholder="e.g. Data Structures"
        )
        subject["difficulty"] = c2.selectbox(
            "Difficulty", ["Easy", "Medium", "Hard"],
            index=["Easy", "Medium", "Hard"].index(subject["difficulty"]),
            key=f"diff_{i}", label_visibility="collapsed"
        )
        subject["priority"] = c3.selectbox(
            "Priority", ["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(subject["priority"]),
            key=f"prio_{i}", label_visibility="collapsed"
        )
        if c4.button("✕", key=f"remove_{i}") and len(st.session_state.subjects) > 1:
            st.session_state.subjects.pop(i)
            st.rerun()

    if st.button("+ Add another subject"):
        st.session_state.subjects.append({"name": "", "difficulty": "Medium", "priority": "Medium"})
        st.rerun()

    st.write("")

    with st.form("plan_form"):
        hours_per_day = st.slider("Hours available per day", 1.0, 12.0, 4.0, 0.5)
        num_days = st.slider("Number of days to plan", 1, 14, 5)
        exam_context = st.text_area(
            "Anything else Gemini should know? (optional)",
            placeholder="e.g. Exam in 10 days, I'm weakest at dynamic programming, prefer mornings for hard topics",
            height=80,
        )
        submitted = st.form_submit_button("Generate my study plan →")

with col_results:
    if submitted:
        valid_subjects = [s for s in st.session_state.subjects if s["name"].strip()]

        if not valid_subjects:
            st.warning("Add at least one subject before generating a plan.")
        else:
            with st.spinner("Gemini is building your plan..."):
                prompt = build_study_plan_prompt(
                    subjects=valid_subjects,
                    hours_per_day=hours_per_day,
                    num_days=num_days,
                    exam_context=exam_context,
                )
                raw_response = generate_response(prompt, expect_json=True)
                data, error = parse_and_validate(raw_response)

                # One retry if the model's output was malformed — LLMs
                # occasionally slip on strict formatting, and a single
                # retry resolves the vast majority of cases.
                if error:
                    raw_response = generate_response(prompt, expect_json=True)
                    data, error = parse_and_validate(raw_response)

            if error:
                st.error(f"Couldn't generate a valid plan: {error}")
                with st.expander("Raw response (for debugging)"):
                    st.code(raw_response)
            else:
                st.session_state.last_plan = data

    if "last_plan" in st.session_state:
        difficulty_colors = {
            "Hard": "background:#E8735C33;color:#E8735C;",
            "Medium": "background:#F2C14E33;color:#F2C14E;",
            "Easy": "background:#6FCF9733;color:#6FCF97;",
        }

        for day in st.session_state.last_plan["plan"]:
            sessions_html = ""
            for s in day["sessions"]:
                sessions_html += f"""
                <div class="session-row">
                    <div>
                        <div class="session-subject">{s['subject']}</div>
                        <div class="session-focus">{s['focus']}</div>
                    </div>
                    <div class="session-duration">{s['duration_minutes']} min</div>
                </div>
                """

            st.markdown(
                f"""
                <div class="day-card">
                    <div class="day-header-row">
                        <div class="day-badge">{day['day_number']}</div>
                        <div class="day-title">Day {day['day_number']}</div>
                    </div>
                    {sessions_html}
                    <div class="tip-box">💡 {day['tip']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("Fill in your subjects and hit **Generate** — your plan will appear here.")