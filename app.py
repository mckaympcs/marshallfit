"""Streamlit interface for the MarshallFit workout generator and scheduler.

Run this app locally with:
    streamlit run app.py
"""

from __future__ import annotations

import base64
import calendar
import importlib.util
import json
from datetime import date, datetime
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
GENERATOR_PATH = BASE_DIR / "generator.py"


def load_workout_engine() -> ModuleType:
    """Load the local generator module without relying on import-name resolution.

    Streamlit Cloud can have extra packages installed in the runtime. Loading by
    file path guarantees the app uses this repository's ``generator.py`` instead
    of any unrelated package named ``generator``.
    """
    spec = importlib.util.spec_from_file_location(
        "marshallfit_workout_generator", GENERATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load workout generator from {GENERATOR_PATH}")

    workout_engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workout_engine)
    return workout_engine


workout_engine = load_workout_engine()
generate_workout = workout_engine.generate_workout
load_templates = workout_engine.load_templates
regenerate_exercise = workout_engine.regenerate_exercise
resolve_diagram_path = workout_engine.resolve_diagram_path
EXERCISES_PATH = BASE_DIR / "data" / "exercises.json"
SCHEDULE_PATH = BASE_DIR / "data" / "scheduled_workouts.json"
ICON_LOGO_PATH = BASE_DIR / "public" / "logos" / "marshallfit-icon.svg"
HORIZONTAL_LOGO_PATH = BASE_DIR / "public" / "logos" / "marshallfit-logo-horizontal.svg"

WORKOUT_TYPE_TO_TEMPLATE = {
    "Chest / Triceps": "chest_triceps",
    "Back / Biceps": "back_biceps",
    "Lower Body": "lower_body",
    "Upper Body": "upper_body",
}
WORKOUT_TYPE_COLORS = {
    "Chest / Triceps": {"bg": "rgba(239, 68, 68, 0.14)", "border": "#ef4444", "text": "#fecaca"},
    "Back / Biceps": {"bg": "rgba(59, 130, 246, 0.14)", "border": "#3b82f6", "text": "#bfdbfe"},
    "Lower Body": {"bg": "rgba(34, 197, 94, 0.14)", "border": "#22c55e", "text": "#bbf7d0"},
    "Upper Body": {"bg": "rgba(234, 179, 8, 0.16)", "border": "#eab308", "text": "#fef08a"},
}
NAV_ITEMS = [
    ("Dashboard", "Dashboard", ":material/home:"),
    ("Workout Generator", "Workout Generator", ":material/bolt:"),
    ("Scheduler", "Scheduler", ":material/calendar_month:"),
    ("Saved Workouts", "Saved Workouts", ":material/bookmark:"),
]
UTILITY_NAV_ITEMS = [("Exercise Library", "Exercise Library", ":material/fitness_center:")]
LIST_FIELDS = [
    "movement_patterns",
    "muscle_focus",
    "equipment",
    "coaching_notes",
    "regressions",
    "progressions",
    "source_refs",
    "template_slots",
]
TABLE_COLUMNS = [
    "delete",
    "id",
    "name",
    "description",
    "setup",
    "coaching_notes",
    "movement_patterns",
    "exercise_role",
    "muscle_focus",
    "equipment",
    "load_type",
    "difficulty",
    "unilateral",
    "bodyweight",
    "regressions",
    "progressions",
    "template_slots",
    "source_refs",
]

st.set_page_config(page_title="MarshallFit", page_icon=ICON_LOGO_PATH, layout="wide")


def inject_design_system() -> None:
    """Apply the global dark gym dashboard design system.

    The base look comes from the real Streamlit dark theme in
    ``.streamlit/config.toml``; this CSS only styles the custom components
    (nav, masthead, cards, calendar) instead of repainting every widget.
    """
    st.markdown(
        """
        <style>
            :root {
                --mf-panel: #10151f;
                --mf-card: #151c2b;
                --mf-border: rgba(148, 163, 184, 0.14);
                --mf-text: #f1f5f9;
                --mf-muted: #8f9bb0;
                --mf-accent: #ef4444;
                --mf-accent-soft: rgba(239, 68, 68, 0.14);
                --mf-radius: 14px;
                --mf-day-h: 124px;
            }

            .stApp {
                background:
                    radial-gradient(circle at 15% 0%, rgba(239, 68, 68, 0.07), transparent 28rem),
                    #0b0f17;
            }

            header[data-testid="stHeader"] {
                background: transparent;
            }

            .stAppDeployButton {
                display: none;
            }

            .block-container {
                max-width: 1280px;
                padding: 1.25rem 2rem 3.5rem;
            }

            /* ---------- Sidebar navigation ---------- */

            [data-testid="stSidebar"] {
                background: var(--mf-panel);
                border-right: 1px solid var(--mf-border);
            }

            [data-testid="stSidebar"] .stButton > button,
            [data-testid="stSidebar"] [data-testid="stPageLink"] a {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 10px;
                color: #c7d0de;
                font-weight: 600;
                justify-content: flex-start;
                min-height: 2.6rem;
                padding: 0.45rem 0.8rem;
                text-align: left;
                transition: background 140ms ease, color 140ms ease;
                width: 100%;
            }

            [data-testid="stSidebar"] .stButton > button > div,
            [data-testid="stSidebar"] [data-testid="stPageLink"] a > span {
                justify-content: flex-start;
            }

            [data-testid="stSidebar"] .stButton > button:hover,
            [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
                background: rgba(248, 250, 252, 0.06);
                border-color: transparent;
                color: #ffffff;
            }

            [data-testid="stSidebar"] .stButton > button[kind="primary"] {
                background: var(--mf-accent-soft);
                border-left: 3px solid var(--mf-accent);
                border-radius: 4px 10px 10px 4px;
                color: #ffffff;
                padding-left: calc(0.8rem - 2px);
            }

            [data-testid="stSidebar"] .stButton > button:focus:not(:focus-visible) {
                box-shadow: none;
            }

            [data-testid="stSidebar"] hr {
                background: var(--mf-border);
                margin: 0.9rem 0;
            }

            .sidebar-caption {
                color: var(--mf-muted);
                font-size: 0.7rem;
                font-weight: 700;
                letter-spacing: 0.14em;
                margin: 0.4rem 0 0.9rem;
                text-transform: uppercase;
            }

            /* ---------- Typography ---------- */

            h1 {
                font-size: clamp(1.8rem, 3vw, 2.5rem);
                font-weight: 800;
                letter-spacing: -0.03em;
                margin-bottom: 0.2rem;
            }

            h2, h3 {
                font-weight: 750;
                letter-spacing: -0.015em;
            }

            /* ---------- Masthead and page header ---------- */

            .mf-masthead {
                align-items: center;
                background: var(--mf-panel);
                border: 1px solid var(--mf-border);
                border-radius: var(--mf-radius);
                display: flex;
                justify-content: center;
                margin-bottom: 1.4rem;
                padding: 1.1rem 1.4rem;
                position: relative;
            }

            .mf-masthead::after {
                background: linear-gradient(90deg, transparent, rgba(239, 68, 68, 0.55), transparent);
                bottom: -1px;
                content: "";
                height: 1px;
                left: 10%;
                position: absolute;
                width: 80%;
            }

            .mf-masthead img {
                display: block;
                height: auto;
                max-height: 58px;
                max-width: min(560px, 78vw);
                object-fit: contain;
                width: 100%;
            }

            .mf-page-header {
                margin: 0 0 1.25rem;
            }

            .mf-page-kicker {
                color: #f87171;
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.16em;
                margin-bottom: 0.2rem;
                text-transform: uppercase;
            }

            .mf-page-description {
                color: var(--mf-muted);
                font-size: 1rem;
                margin-top: 0.15rem;
                max-width: 760px;
            }

            /* ---------- Panels, cards, buttons ---------- */

            div[data-testid="stVerticalBlockBorderWrapper"],
            div[data-testid="stExpander"] details {
                background: var(--mf-card);
                border-color: var(--mf-border) !important;
                border-radius: var(--mf-radius) !important;
            }

            .stButton > button,
            .stDownloadButton > button {
                border-radius: 10px;
                font-weight: 600;
                transition: border-color 140ms ease, box-shadow 140ms ease;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover {
                border-color: rgba(239, 68, 68, 0.6);
            }

            .diagram-placeholder {
                align-items: center;
                aspect-ratio: 1 / 1;
                background: var(--mf-accent-soft);
                border: 1px dashed rgba(239, 68, 68, 0.4);
                border-radius: 12px;
                color: #cbd5e1;
                display: flex;
                flex-direction: column;
                font-size: 0.72rem;
                font-weight: 700;
                gap: 0.25rem;
                justify-content: center;
                min-height: 96px;
                padding: 0.75rem;
                text-align: center;
                text-transform: uppercase;
            }

            .diagram-placeholder span {
                color: #fca5a5;
                display: block;
                font-size: 1.45rem;
                line-height: 1;
            }

            .exercise-title {
                color: var(--mf-text);
                font-size: 1.05rem;
                font-weight: 700;
                line-height: 1.2;
                margin: 0 0 0.25rem;
            }

            .exercise-category {
                color: var(--mf-muted);
                font-size: 0.74rem;
                font-weight: 600;
                letter-spacing: 0.06em;
                margin-bottom: 0.7rem;
                text-transform: uppercase;
            }

            .sets-reps-pill,
            .workout-badge {
                border-radius: 999px;
                display: inline-flex;
                font-size: 0.8rem;
                font-weight: 700;
                line-height: 1.1;
                padding: 0.4rem 0.7rem;
            }

            .sets-reps-pill {
                background: var(--mf-accent-soft);
                border: 1px solid rgba(239, 68, 68, 0.36);
                color: #fecaca;
            }

            .metric-card, .calendar-card, .saved-card {
                background: var(--mf-card);
                border: 1px solid var(--mf-border);
                border-radius: var(--mf-radius);
                padding: 1rem;
            }

            .metric-value {
                color: #ffffff;
                font-size: 2.1rem;
                font-weight: 800;
                letter-spacing: -0.03em;
            }

            .metric-label, .calendar-empty-label {
                color: var(--mf-muted);
                font-size: 0.74rem;
                font-weight: 600;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }

            /* ---------- Scheduler calendar ---------- */

            .calendar-month-title {
                color: #ffffff;
                font-size: clamp(1.35rem, 2.5vw, 1.8rem);
                font-weight: 800;
                letter-spacing: -0.02em;
                margin: 0;
                text-align: center;
            }

            .weekday-label {
                color: var(--mf-muted);
                font-size: 0.74rem;
                font-weight: 700;
                letter-spacing: 0.1em;
                padding: 0.6rem 0 0.35rem;
                text-align: center;
                text-transform: uppercase;
            }

            .calendar-card {
                height: var(--mf-day-h);
                overflow: hidden;
                padding: 0.75rem;
                transition: border-color 140ms ease;
            }

            .calendar-card.today {
                border-color: rgba(239, 68, 68, 0.65);
                box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.3);
            }

            .calendar-card .workout-badge {
                font-size: 0.7rem;
                padding: 0.3rem 0.55rem;
            }

            .calendar-day-number {
                color: var(--mf-text);
                font-size: 1rem;
                font-weight: 700;
            }

            .calendar-muted {
                background: transparent;
                border-style: dashed;
                opacity: 0.35;
            }

            /* Each day button (key schedule_day_*) is pulled up over its card
               so the whole cell is clickable; hover shows a red outline. */
            div[class*="st-key-schedule_day_"] {
                margin-top: calc(-1 * var(--mf-day-h));
            }

            div[class*="st-key-schedule_day_"] button {
                background: transparent;
                border: 1px solid transparent;
                border-radius: var(--mf-radius);
                color: transparent;
                height: var(--mf-day-h);
                min-height: var(--mf-day-h);
                width: 100%;
            }

            div[class*="st-key-schedule_day_"] button:hover,
            div[class*="st-key-schedule_day_"] button:focus-visible {
                background: rgba(239, 68, 68, 0.06);
                border-color: rgba(239, 68, 68, 0.6);
            }

            div[class*="st-key-schedule_day_"] button * {
                color: transparent !important;
            }

            @media (max-width: 780px) {
                :root { --mf-day-h: 92px; }
                .block-container { padding: 1rem 0.85rem 2.5rem; }
                .mf-masthead { padding: 0.75rem; }
                .calendar-card { padding: 0.6rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_app_shell() -> str:
    """Render reusable sidebar and masthead, returning the selected page."""
    all_nav_items = [*NAV_ITEMS, *UTILITY_NAV_ITEMS]
    selected_index = min(st.session_state.get("nav_index", 0), len(all_nav_items) - 1)

    with st.sidebar:
        if ICON_LOGO_PATH.exists():
            st.image(str(ICON_LOGO_PATH), width=72)
        st.markdown("<div class='sidebar-caption'>MarshallFit Command Center</div>", unsafe_allow_html=True)
        for index, (label, _, icon) in enumerate(all_nav_items):
            is_active = index == selected_index
            if st.button(
                label,
                icon=icon,
                key=f"nav_{index}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ) and not is_active:
                st.session_state.nav_index = index
                st.rerun()
        st.divider()
        st.page_link("pages/today.py", label="Today's Workout (TV)", icon=":material/tv:")

    if HORIZONTAL_LOGO_PATH.exists():
        encoded_logo = base64.b64encode(HORIZONTAL_LOGO_PATH.read_bytes()).decode("utf-8")
        masthead_logo = (
            f'<img src="data:image/svg+xml;base64,{encoded_logo}" '
            'alt="MarshallFit" loading="eager" />'
        )
    else:
        masthead_logo = "<h1>MarshallFit</h1>"
    st.markdown(
        f"<div class='mf-masthead'>{masthead_logo}</div>",
        unsafe_allow_html=True,
    )

    return all_nav_items[selected_index][1]


def page_header(title: str, description: str, kicker: str = "Training Dashboard") -> None:
    """Render the branded page title treatment below the masthead."""
    st.markdown(
        f"""
        <section class="mf-page-header">
            <div class="mf-page-kicker">{kicker}</div>
            <h1>{title}</h1>
            <p class="mf-page-description">{description}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def load_exercise_library() -> dict[str, Any]:
    """Load the complete exercise JSON document so metadata is preserved."""
    with EXERCISES_PATH.open(encoding="utf-8") as exercise_file:
        return json.load(exercise_file)


def save_exercise_library(exercise_library: dict[str, Any]) -> None:
    """Persist edited exercise data back to ``data/exercises.json``."""
    with EXERCISES_PATH.open("w", encoding="utf-8") as exercise_file:
        json.dump(exercise_library, exercise_file, indent=2)
        exercise_file.write("\n")


def load_schedule() -> dict[str, Any]:
    """Load scheduled workouts from the local app data file."""
    if not SCHEDULE_PATH.exists():
        return {}
    with SCHEDULE_PATH.open(encoding="utf-8") as schedule_file:
        return json.load(schedule_file)


def save_schedule(schedule: dict[str, Any]) -> None:
    """Persist scheduled workouts to the local app data file."""
    SCHEDULE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SCHEDULE_PATH.open("w", encoding="utf-8") as schedule_file:
        json.dump(schedule, schedule_file, indent=2)
        schedule_file.write("\n")


def friendly_label(value: str) -> str:
    """Turn data keys such as ``horizontal_push`` into readable labels."""
    return value.replace("_", " ").replace("-", " ").title()


def list_to_cell(value: Any) -> str:
    """Display list data in a compact, editable table cell."""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return "" if value is None else str(value)


def cell_to_list(value: Any) -> list[str]:
    """Convert a comma-separated editable table cell back into JSON list data."""
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None:
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def render_diagram(exercise: dict[str, Any]) -> None:
    """Render the id-matched exercise diagram or a compact fallback placeholder."""
    exercise_id = exercise.get("exercise_id") or exercise.get("id")
    diagram_path = exercise.get("diagram_path")
    if exercise_id:
        diagram_path = resolve_diagram_path(str(exercise_id), diagram_path)

    diagram_file = BASE_DIR / str(diagram_path or "")
    if diagram_file.exists():
        st.image(str(diagram_file), use_container_width=True)
    else:
        st.markdown(
            """
            <div class="diagram-placeholder">
                <span>↔</span>
                Diagram<br>Placeholder
            </div>
            """,
            unsafe_allow_html=True,
        )


def generate_workout_columns(template_id: str) -> dict[str, list[dict[str, Any]]]:
    """Generate the weighted and non-weighted workout columns for a template."""
    return {
        "weighted": generate_workout(template_id, "weighted")["exercises"],
        "bodyweight": generate_workout(template_id, "bodyweight")["exercises"],
    }


def replace_exercise_slot(
    exercises: list[dict[str, Any]], template_id: str, mode: str, slot_id: str
) -> list[dict[str, Any]]:
    """Return exercises with only the requested slot regenerated."""
    replacement = regenerate_exercise(template_id, mode, slot_id, exercises)
    return [replacement if exercise.get("slot_id") == slot_id else exercise for exercise in exercises]


def render_exercise_card(
    exercise: dict[str, Any],
    number: int,
    key_prefix: str,
    on_regenerate: Callable[[str], None] | None = None,
) -> None:
    """Render a generated exercise card with an optional per-slot regenerate button."""
    with st.container(border=True):
        diagram_column, details_column = st.columns([1, 2.35], gap="medium", vertical_alignment="center")
        with diagram_column:
            render_diagram(exercise)
        with details_column:
            st.markdown(f'<div class="exercise-title">{number}. {exercise["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="exercise-category">{exercise["category"]}</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="sets-reps-pill">'
                f'{exercise["sets"]} sets × {exercise["reps"]} reps'
                "</div>",
                unsafe_allow_html=True,
            )
            st.caption(f"Slot: {exercise['slot_name']}")
            if on_regenerate is not None:
                if st.button("Regenerate", key=f"{key_prefix}_{exercise['slot_id']}"):
                    on_regenerate(exercise["slot_id"])
                    st.rerun()


def render_exercise_column(
    title: str,
    exercises: list[dict[str, Any]],
    key_prefix: str,
    on_regenerate: Callable[[str], None] | None = None,
) -> None:
    """Render one complete exercise column."""
    st.subheader(title)
    for number, exercise in enumerate(exercises, start=1):
        render_exercise_card(exercise, number, key_prefix, on_regenerate)


def render_dual_workout_columns(
    weighted_exercises: list[dict[str, Any]],
    bodyweight_exercises: list[dict[str, Any]],
    key_prefix: str,
    on_regenerate_weighted: Callable[[str], None] | None = None,
    on_regenerate_bodyweight: Callable[[str], None] | None = None,
) -> None:
    """Render weighted and non-weighted generated workouts side by side."""
    weighted_column, bodyweight_column = st.columns(2, gap="large")
    with weighted_column:
        render_exercise_column("Weighted", weighted_exercises, f"{key_prefix}_weighted", on_regenerate_weighted)
    with bodyweight_column:
        render_exercise_column("Non-Weighted", bodyweight_exercises, f"{key_prefix}_bodyweight", on_regenerate_bodyweight)


def workout_type_selector(label: str, key: str, initial: str | None = None) -> str:
    """Render a workout type selector using the supported template names."""
    workout_types = list(WORKOUT_TYPE_TO_TEMPLATE)
    index = workout_types.index(initial) if initial in workout_types else 0
    return st.selectbox(label, workout_types, index=index, key=key)


def render_workout_generator_page() -> None:
    """Render the random workout generator page with full and slot regeneration."""
    page_header(
        "Workout Generator",
        "Build weighted and non-weighted workouts by muscle group, then regenerate the full plan or any individual slot.",
    )
    selected_type = workout_type_selector("Workout type", "generator_workout_type")
    template_id = WORKOUT_TYPE_TO_TEMPLATE[selected_type]
    generator_state = st.session_state.setdefault("generator_workout", {})
    template_changed = generator_state.get("template_id") != template_id

    controls = st.columns([1, 1.2, 2.4])
    if controls[0].button("Generate Workout", type="primary") or controls[1].button("Regenerate Full Workout") or template_changed:
        columns = generate_workout_columns(template_id)
        st.session_state.generator_workout = {
            "template_id": template_id,
            "workoutType": selected_type,
            "weighted": columns["weighted"],
            "bodyweight": columns["bodyweight"],
        }
        generator_state = st.session_state.generator_workout

    selected_template = next(template for template in load_templates() if template["id"] == template_id)
    if selected_template.get("description"):
        st.info(selected_template["description"])

    def regenerate_weighted(slot_id: str) -> None:
        st.session_state.generator_workout["weighted"] = replace_exercise_slot(
            st.session_state.generator_workout["weighted"], template_id, "weighted", slot_id
        )

    def regenerate_bodyweight(slot_id: str) -> None:
        st.session_state.generator_workout["bodyweight"] = replace_exercise_slot(
            st.session_state.generator_workout["bodyweight"], template_id, "bodyweight", slot_id
        )

    render_dual_workout_columns(
        generator_state["weighted"],
        generator_state["bodyweight"],
        "generator",
        regenerate_weighted,
        regenerate_bodyweight,
    )


def format_display_date(iso_date: str, include_weekday: bool = False) -> str:
    """Format an ISO date for display without ``%-d`` (unsupported on Windows)."""
    parsed = datetime.fromisoformat(iso_date)
    weekday = f"{parsed.strftime('%A')}, " if include_weekday else ""
    return f"{weekday}{parsed.strftime('%B')} {parsed.day}, {parsed.year}"


def date_key(year: int, month: int, day: int) -> str:
    """Format a calendar date key as YYYY-MM-DD."""
    return date(year, month, day).isoformat()


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    """Return the year and month after moving delta months."""
    zero_based = (year * 12 + month - 1) + delta
    return zero_based // 12, zero_based % 12 + 1


def ensure_calendar_state() -> tuple[int, int]:
    """Initialize and return the visible scheduler month."""
    today = date.today()
    st.session_state.setdefault("scheduler_year", today.year)
    st.session_state.setdefault("scheduler_month", today.month)
    return int(st.session_state.scheduler_year), int(st.session_state.scheduler_month)


def render_workout_badge(workout_type: str) -> str:
    """Return HTML for a color-coded scheduled-workout badge."""
    colors = WORKOUT_TYPE_COLORS[workout_type]
    return (
        "<div class='workout-badge' "
        f"style='background:{colors['bg']}; border:1px solid {colors['border']}; color:{colors['text']};'>"
        f"{workout_type}</div>"
    )


def render_calendar_cell(day: int, year: int, month: int, schedule: dict[str, Any]) -> None:
    """Render one day in the monthly Scheduler calendar."""
    if day == 0:
        st.markdown("<div class='calendar-card calendar-muted'></div>", unsafe_allow_html=True)
        return

    key = date_key(year, month, day)
    scheduled_workout = schedule.get(key)
    today_class = " today" if key == date.today().isoformat() else ""
    badge_html = render_workout_badge(scheduled_workout["workoutType"]) if scheduled_workout else "<div class='calendar-empty-label'>Open slot</div>"

    st.markdown(
        f"""
        <div class="calendar-card{today_class}">
            <div class="calendar-day-number">{day}</div>
            <div style="height:.7rem"></div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
    button_label = f"Edit {day}" if scheduled_workout else f"Schedule {day}"
    if st.button(button_label, key=f"schedule_day_{key}", use_container_width=True):
        st.session_state.scheduler_selected_date = key
        st.session_state.scheduler_view = "day"
        st.rerun()


def render_scheduler_calendar() -> None:
    """Render the main monthly Scheduler calendar view."""
    page_header("Scheduler", "Plan and organize your workouts by day with a premium monthly training calendar.")
    year, month = ensure_calendar_state()
    schedule = load_schedule()

    previous_col, title_col, next_col, today_col = st.columns([1, 4, 1, 1.2], vertical_alignment="center")
    if previous_col.button("← Previous", use_container_width=True):
        st.session_state.scheduler_year, st.session_state.scheduler_month = shift_month(year, month, -1)
        st.rerun()
    title_col.markdown(f'<div class="calendar-month-title">{calendar.month_name[month]} {year}</div>', unsafe_allow_html=True)
    if next_col.button("Next →", use_container_width=True):
        st.session_state.scheduler_year, st.session_state.scheduler_month = shift_month(year, month, 1)
        st.rerun()
    if today_col.button("Today", use_container_width=True):
        today = date.today()
        st.session_state.scheduler_year = today.year
        st.session_state.scheduler_month = today.month
        st.rerun()

    for weekday, column in zip(calendar.day_abbr, st.columns(7)):
        column.markdown(f"<div class='weekday-label'>{weekday}</div>", unsafe_allow_html=True)

    for week in calendar.monthcalendar(year, month):
        columns = st.columns(7, gap="small")
        for day, column in zip(week, columns):
            with column:
                render_calendar_cell(day, year, month, schedule)


def render_scheduler_day_view() -> None:
    """Render workout selection and generation for one scheduled date."""
    selected_date = st.session_state.get("scheduler_selected_date")
    if not selected_date:
        st.session_state.scheduler_view = "calendar"
        st.rerun()

    schedule = load_schedule()
    existing_workout = schedule.get(selected_date, {})
    readable_date = format_display_date(selected_date, include_weekday=True)

    if st.button("← Back to calendar"):
        st.session_state.scheduler_view = "calendar"
        st.rerun()

    page_header("Schedule Workout", f"Selected date: {readable_date}. Choose a type, generate options, and save the plan to this day.")
    selected_type = workout_type_selector(
        "Workout type",
        f"scheduler_type_{selected_date}",
        existing_workout.get("workoutType"),
    )
    template_id = WORKOUT_TYPE_TO_TEMPLATE[selected_type]
    day_state_key = f"scheduler_draft_{selected_date}"
    draft = st.session_state.get(day_state_key)
    needs_new_draft = draft is None or draft.get("workoutType") != selected_type

    if needs_new_draft:
        if existing_workout.get("workoutType") == selected_type:
            st.session_state[day_state_key] = {
                "workoutType": selected_type,
                "weightedExercises": existing_workout.get("weightedExercises", []),
                "nonWeightedExercises": existing_workout.get("nonWeightedExercises", []),
            }
        else:
            columns = generate_workout_columns(template_id)
            st.session_state[day_state_key] = {
                "workoutType": selected_type,
                "weightedExercises": columns["weighted"],
                "nonWeightedExercises": columns["bodyweight"],
            }
        draft = st.session_state[day_state_key]

    action_columns = st.columns([1.2, 1, 3])
    if action_columns[0].button("Regenerate Full Workout"):
        columns = generate_workout_columns(template_id)
        st.session_state[day_state_key] = {
            "workoutType": selected_type,
            "weightedExercises": columns["weighted"],
            "nonWeightedExercises": columns["bodyweight"],
        }
        st.rerun()

    if action_columns[1].button("Save to This Day", type="primary"):
        schedule[selected_date] = {
            "date": selected_date,
            "workoutType": selected_type,
            "weightedExercises": draft["weightedExercises"],
            "nonWeightedExercises": draft["nonWeightedExercises"],
        }
        save_schedule(schedule)
        st.session_state.scheduler_view = "calendar"
        st.success(f"Saved {selected_type} to {selected_date}.")
        st.rerun()

    def regenerate_weighted(slot_id: str) -> None:
        st.session_state[day_state_key]["weightedExercises"] = replace_exercise_slot(
            st.session_state[day_state_key]["weightedExercises"], template_id, "weighted", slot_id
        )

    def regenerate_bodyweight(slot_id: str) -> None:
        st.session_state[day_state_key]["nonWeightedExercises"] = replace_exercise_slot(
            st.session_state[day_state_key]["nonWeightedExercises"], template_id, "bodyweight", slot_id
        )

    render_dual_workout_columns(
        draft["weightedExercises"],
        draft["nonWeightedExercises"],
        f"scheduler_{selected_date}",
        regenerate_weighted,
        regenerate_bodyweight,
    )


def render_scheduler_page() -> None:
    """Render either the Scheduler calendar or selected-day flow."""
    if st.session_state.get("scheduler_view", "calendar") == "day":
        render_scheduler_day_view()
    else:
        render_scheduler_calendar()


def render_dashboard_page() -> None:
    """Render a summary dashboard for generated and saved training plans."""
    schedule = load_schedule()
    today_key = date.today().isoformat()
    upcoming = sorted(key for key in schedule if key >= today_key)
    workout_counts = {workout_type: 0 for workout_type in WORKOUT_TYPE_TO_TEMPLATE}
    for workout in schedule.values():
        workout_counts[workout.get("workoutType", "")] = workout_counts.get(workout.get("workoutType", ""), 0) + 1

    page_header("Dashboard", "Your dark gym-style command center for training plans, scheduled workouts, and quick navigation.")
    metric_columns = st.columns(4, gap="large")
    metrics = [
        (len(schedule), "Scheduled days"),
        (len(upcoming), "Upcoming sessions"),
        (sum(len(item.get("weightedExercises", [])) for item in schedule.values()), "Weighted slots"),
        (sum(len(item.get("nonWeightedExercises", [])) for item in schedule.values()), "Non-weighted slots"),
    ]
    for column, (value, label) in zip(metric_columns, metrics):
        column.markdown(f"<div class='metric-card'><div class='metric-value'>{value}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

    st.subheader("Training split mix")
    split_columns = st.columns(4, gap="small")
    for column, workout_type in zip(split_columns, WORKOUT_TYPE_TO_TEMPLATE):
        column.markdown(
            f"<div class='metric-card'>{render_workout_badge(workout_type)}<div class='metric-value'>{workout_counts.get(workout_type, 0)}</div><div class='metric-label'>Saved sessions</div></div>",
            unsafe_allow_html=True,
        )

    st.subheader("Next on the calendar")
    if not upcoming:
        st.info("No upcoming workouts yet. Open Scheduler to assign your next training day.")
    else:
        for key in upcoming[:5]:
            workout = schedule[key]
            st.markdown(
                f"<div class='saved-card'><strong>{format_display_date(key)}</strong><br>{render_workout_badge(workout['workoutType'])}</div>",
                unsafe_allow_html=True,
            )


def render_saved_workouts_page() -> None:
    """Render saved scheduled workouts in a dashboard card layout."""
    page_header("Saved Workouts", "Review every workout saved from the Scheduler, including weighted and non-weighted exercise options.")
    schedule = load_schedule()
    if not schedule:
        st.info("No saved workouts yet. Schedule a workout day to build this library.")
        return

    for key in sorted(schedule):
        workout = schedule[key]
        with st.expander(f"{format_display_date(key)} · {workout['workoutType']}", expanded=False):
            st.markdown(render_workout_badge(workout["workoutType"]), unsafe_allow_html=True)
            render_dual_workout_columns(
                workout.get("weightedExercises", []),
                workout.get("nonWeightedExercises", []),
                f"saved_{key}",
            )


def edited_table_to_rows(edited_table: Any) -> list[dict[str, Any]]:
    """Normalize Streamlit data editor output into row dictionaries."""
    if hasattr(edited_table, "to_dict"):
        return edited_table.to_dict(orient="records")
    return list(edited_table)


def exercise_to_table_row(exercise: dict[str, Any]) -> dict[str, Any]:
    """Flatten one exercise into values Streamlit can edit in a table."""
    row = {column: exercise.get(column, "") for column in TABLE_COLUMNS}
    row["delete"] = False
    for field in LIST_FIELDS:
        row[field] = list_to_cell(exercise.get(field, []))
    row["description"] = exercise.get("description", exercise.get("setup", ""))
    row["unilateral"] = bool(exercise.get("unilateral", False))
    row["bodyweight"] = bool(exercise.get("bodyweight", False))
    return row


def table_row_to_exercise(row: dict[str, Any], original: dict[str, Any] | None = None) -> dict[str, Any]:
    """Convert an edited table row into the exercise JSON schema."""
    exercise = dict(original or {})
    for column in TABLE_COLUMNS:
        if column == "delete":
            continue
        if column in LIST_FIELDS:
            exercise[column] = cell_to_list(row.get(column, ""))
        elif column in {"unilateral", "bodyweight"}:
            exercise[column] = bool(row.get(column, False))
        else:
            exercise[column] = str(row.get(column, "")).strip()
    return exercise


def unique_values(exercises: list[dict[str, Any]], field: str) -> list[str]:
    """Return sorted unique values for a field that may contain strings or lists."""
    values: set[str] = set()
    for exercise in exercises:
        raw_value = exercise.get(field)
        if isinstance(raw_value, list):
            values.update(str(item) for item in raw_value if item)
        elif raw_value not in {None, ""}:
            values.add(str(raw_value))
    return sorted(values)


def exercise_matches_filters(
    exercise: dict[str, Any],
    search_text: str,
    selected_load_types: list[str],
    selected_difficulties: list[str],
    selected_movements: list[str],
    selected_roles: list[str],
    selected_muscles: list[str],
    selected_equipment: list[str],
    selected_template_slots: list[str],
    bodyweight_filter: str,
    unilateral_filter: str,
) -> bool:
    """Return True when an exercise should appear in the review table."""
    searchable_text = " ".join(
        [
            str(exercise.get("id", "")),
            str(exercise.get("name", "")),
            str(exercise.get("description", "")),
            str(exercise.get("setup", "")),
            list_to_cell(exercise.get("coaching_notes", [])),
        ]
    ).lower()
    if search_text and search_text.lower() not in searchable_text:
        return False

    filters = [
        (selected_load_types, [exercise.get("load_type", "")]),
        (selected_difficulties, [exercise.get("difficulty", "")]),
        (selected_movements, exercise.get("movement_patterns", [])),
        (selected_roles, [exercise.get("exercise_role", "")]),
        (selected_muscles, exercise.get("muscle_focus", [])),
        (selected_equipment, exercise.get("equipment", [])),
        (selected_template_slots, exercise.get("template_slots", [])),
    ]
    for selected_values, exercise_values in filters:
        if selected_values and not set(selected_values).intersection(exercise_values):
            return False
    if bodyweight_filter != "Any" and bool(exercise.get("bodyweight", False)) != (bodyweight_filter == "Yes"):
        return False
    if unilateral_filter != "Any" and bool(exercise.get("unilateral", False)) != (unilateral_filter == "Yes"):
        return False
    return True


def render_exercise_library_page() -> None:
    """Render a filterable, editable table for the exercise JSON library."""
    page_header("Exercise Library", "Review, filter, edit, and expand the exercise data powering MarshallFit.", "Admin Utility")
    exercise_library = load_exercise_library()
    exercises = exercise_library["exercises"]

    st.subheader("Filters")
    filter_columns = st.columns(3)
    search_text = filter_columns[0].text_input("Search")
    selected_load_types = filter_columns[1].multiselect("Load type", unique_values(exercises, "load_type"))
    selected_difficulties = filter_columns[2].multiselect("Difficulty", unique_values(exercises, "difficulty"))

    filter_columns = st.columns(3)
    selected_movements = filter_columns[0].multiselect("Movement type", unique_values(exercises, "movement_patterns"))
    selected_roles = filter_columns[1].multiselect("Exercise role", unique_values(exercises, "exercise_role"))
    selected_muscles = filter_columns[2].multiselect("Muscle focus", unique_values(exercises, "muscle_focus"))

    filter_columns = st.columns(3)
    selected_equipment = filter_columns[0].multiselect("Equipment", unique_values(exercises, "equipment"))
    selected_template_slots = filter_columns[1].multiselect("Template slots", unique_values(exercises, "template_slots"))
    bodyweight_filter = filter_columns[2].radio("Bodyweight", ["Any", "Yes", "No"], horizontal=True)
    unilateral_filter = st.radio("Unilateral", ["Any", "Yes", "No"], horizontal=True)

    filtered_exercises = [
        exercise
        for exercise in exercises
        if exercise_matches_filters(
            exercise,
            search_text,
            selected_load_types,
            selected_difficulties,
            selected_movements,
            selected_roles,
            selected_muscles,
            selected_equipment,
            selected_template_slots,
            bodyweight_filter,
            unilateral_filter,
        )
    ]

    st.caption(f"Showing {len(filtered_exercises)} of {len(exercises)} exercises.")
    st.write("Comma-separated fields become JSON lists when saved. Check the delete box beside any exercise you want removed, then click Save table changes.")

    edited_rows = st.data_editor(
        [exercise_to_table_row(exercise) for exercise in filtered_exercises],
        key="exercise_editor",
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "delete": st.column_config.CheckboxColumn("Delete?"),
            "description": st.column_config.TextColumn("Description", width="large"),
            "setup": st.column_config.TextColumn("Setup", width="large"),
            "coaching_notes": st.column_config.TextColumn("Coaching notes", width="large"),
            "movement_patterns": st.column_config.TextColumn("Movement type"),
            "load_type": st.column_config.SelectboxColumn("Load type", options=unique_values(exercises, "load_type")),
            "difficulty": st.column_config.SelectboxColumn("Difficulty", options=unique_values(exercises, "difficulty")),
            "exercise_role": st.column_config.SelectboxColumn("Exercise role", options=unique_values(exercises, "exercise_role")),
        },
    )

    if st.button("Save table changes", type="primary"):
        edited_table_rows = edited_table_to_rows(edited_rows)
        edited_by_original_id = {original["id"]: row for original, row in zip(filtered_exercises, edited_table_rows)}
        existing_ids_outside_filter = {exercise["id"] for exercise in exercises if exercise["id"] not in edited_by_original_id}
        saved_exercises = []
        deleted_count = 0
        for exercise in exercises:
            edited_row = edited_by_original_id.get(exercise["id"])
            if edited_row is None:
                saved_exercises.append(exercise)
                continue
            if edited_row.get("delete"):
                deleted_count += 1
                continue
            saved_exercise = table_row_to_exercise(edited_row, exercise)
            if not saved_exercise["id"] or not saved_exercise["name"]:
                st.error("Every saved exercise needs an ID and a name.")
                st.stop()
            if saved_exercise["id"] in existing_ids_outside_filter:
                st.error(f"Duplicate exercise ID: {saved_exercise['id']}")
                st.stop()
            existing_ids_outside_filter.add(saved_exercise["id"])
            saved_exercises.append(saved_exercise)
        exercise_library["exercises"] = saved_exercises
        save_exercise_library(exercise_library)
        st.success(f"Saved changes. Deleted {deleted_count} exercise(s).")
        st.rerun()

    with st.expander("Add an exercise"):
        with st.form("add_exercise_form", clear_on_submit=True):
            add_columns = st.columns(2)
            new_id = add_columns[0].text_input("Exercise ID", placeholder="kettlebell_goblet_squat")
            new_name = add_columns[1].text_input("Exercise name", placeholder="Kettlebell Goblet Squat")
            new_description = st.text_area("Description")
            new_setup = st.text_area("Setup")
            new_coaching_notes = st.text_area("Coaching notes (comma-separated)")

            add_columns = st.columns(3)
            new_movements = add_columns[0].text_input("Movement types (comma-separated)", placeholder="squat")
            new_role = add_columns[1].selectbox("Exercise role", ["", *unique_values(exercises, "exercise_role")])
            new_muscles = add_columns[2].text_input("Muscle focus (comma-separated)", placeholder="quads, glutes")

            add_columns = st.columns(3)
            new_equipment = add_columns[0].text_input("Equipment (comma-separated)", placeholder="kettlebells")
            new_load_type = add_columns[1].selectbox("Load type", ["", *unique_values(exercises, "load_type")])
            new_difficulty = add_columns[2].selectbox("Difficulty", ["", *unique_values(exercises, "difficulty")])

            add_columns = st.columns(3)
            new_template_slots = add_columns[0].text_input("Template slots (comma-separated)", placeholder="squat_primary")
            new_bodyweight = add_columns[1].checkbox("Bodyweight")
            new_unilateral = add_columns[2].checkbox("Unilateral")

            submitted = st.form_submit_button("Add exercise", type="primary")
            if submitted:
                existing_ids = {exercise["id"] for exercise in exercises}
                cleaned_id = new_id.strip()
                if not cleaned_id or not new_name.strip():
                    st.error("Add an exercise ID and name before saving.")
                    st.stop()
                if cleaned_id in existing_ids:
                    st.error(f"Exercise ID already exists: {cleaned_id}")
                    st.stop()
                exercises.append(
                    {
                        "id": cleaned_id,
                        "name": new_name.strip(),
                        "description": new_description.strip(),
                        "movement_patterns": cell_to_list(new_movements),
                        "exercise_role": new_role,
                        "muscle_focus": cell_to_list(new_muscles),
                        "equipment": cell_to_list(new_equipment),
                        "load_type": new_load_type,
                        "difficulty": new_difficulty,
                        "unilateral": new_unilateral,
                        "bodyweight": new_bodyweight,
                        "setup": new_setup.strip(),
                        "coaching_notes": cell_to_list(new_coaching_notes),
                        "regressions": [],
                        "progressions": [],
                        "source_refs": ["marshallfit_exercise_library_editor"],
                        "template_slots": cell_to_list(new_template_slots),
                    }
                )
                exercise_library["exercises"] = exercises
                save_exercise_library(exercise_library)
                st.success(f"Added {new_name.strip()}.")
                st.rerun()


def main() -> None:
    """Run the MarshallFit Streamlit app."""
    inject_design_system()
    page = render_app_shell()
    if page == "Dashboard":
        render_dashboard_page()
    elif page == "Workout Generator":
        render_workout_generator_page()
    elif page == "Scheduler":
        render_scheduler_page()
    elif page == "Saved Workouts":
        render_saved_workouts_page()
    else:
        render_exercise_library_page()


main()
