"""Full-screen Today's Workout display route for a portrait TV."""

from __future__ import annotations

import base64
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from generator import resolve_diagram_path
from today_workout import todays_workout

BASE_DIR = Path(__file__).resolve().parents[1]
ICON_LOGO_PATH = BASE_DIR / "public" / "logos" / "marshallfit-icon.svg"
HORIZONTAL_LOGO_PATH = BASE_DIR / "public" / "logos" / "marshallfit-logo-horizontal.svg"

st.set_page_config(
    page_title="Today’s Workout · MarshallFit",
    page_icon=ICON_LOGO_PATH,
    layout="wide",
    initial_sidebar_state="collapsed",
)


def html_escape(value: Any) -> str:
    """Escape dynamic text before it is inserted into custom HTML."""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def friendly_date(value: str) -> str:
    """Format an ISO date as a TV-friendly day label."""
    workout_date = datetime.fromisoformat(value).date()
    return f"{workout_date.strftime('%A').upper()} · {workout_date.strftime('%B')} {workout_date.day}, {workout_date.year}"


def image_data_uri(path: Path) -> str | None:
    """Return a base64 data URI for a local image file, or None when missing."""
    if not path.exists() or not path.is_file():
        return None

    mime_types = {
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    mime_type = mime_types.get(path.suffix.lower(), "application/octet-stream")
    encoded_image = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_image}"


def logo_markup() -> str:
    """Return an inline logo so the TV page has no external asset dependency."""
    logo_uri = image_data_uri(HORIZONTAL_LOGO_PATH)
    if logo_uri:
        return f'<img class="today-logo" src="{logo_uri}" alt="MarshallFit" />'
    return '<div class="today-wordmark">MARSHALL<span>FIT</span></div>'


def diagram_markup(exercise: dict[str, Any]) -> str:
    """Return the local exercise diagram image or a subtle no-diagram placeholder."""
    exercise_id = exercise.get("exercise_id") or exercise.get("id")
    diagram_path = exercise.get("diagram_path")
    if exercise_id:
        diagram_path = resolve_diagram_path(str(exercise_id), diagram_path)

    diagram_file = BASE_DIR / str(diagram_path or "")
    diagram_uri = image_data_uri(diagram_file)
    if not diagram_uri:
        return '<div class="exercise-diagram-placeholder">Diagram<br>coming soon</div>'

    exercise_name = html_escape(exercise.get("name", "Exercise diagram"))
    return f'<img class="exercise-diagram" src="{diagram_uri}" alt="{exercise_name} diagram" />'


def muscle_label(exercise: dict[str, Any]) -> str:
    """Return the compact primary-muscle label for an exercise row."""
    muscles = exercise.get("primary_muscles") or []
    if not muscles:
        return ""
    return ", ".join(html_escape(muscle) for muscle in muscles)


def exercise_card(exercise: dict[str, Any], number: int) -> str:
    """Build one display-only exercise row with no edit/generate controls."""
    muscles = muscle_label(exercise)
    muscles_markup = f'<span class="exercise-muscles">{muscles}</span>' if muscles else ""
    rest = exercise.get("rest") or exercise.get("rest_time") or exercise.get("rest_seconds")
    rest_markup = (
        f'<div class="sets-reps rest-pill">{html_escape(rest)}<span>REST</span></div>'
        if rest
        else ""
    )
    category = exercise.get("category") or exercise.get("slot_name") or "Training Slot"

    return f"""
        <article class="today-exercise-card">
            <div class="exercise-number">{number:02d}</div>
            <div class="exercise-art">{diagram_markup(exercise)}</div>
            <div class="exercise-main">
                <div class="exercise-name">{html_escape(exercise.get('name', 'Exercise'))}</div>
                <div class="exercise-meta-line">
                    <span>{html_escape(category)}</span>
                    {muscles_markup}
                </div>
                <div class="exercise-prescription">
                    <div class="sets-reps">{html_escape(exercise.get('sets', '3'))}<span>SETS</span></div>
                    <div class="sets-reps reps-pill">{html_escape(exercise.get('reps', '8-10'))}<span>REPS</span></div>
                    {rest_markup}
                </div>
            </div>
        </article>
    """


def workout_column(title: str, exercises: list[dict[str, Any]]) -> str:
    """Build one display-only workout column for the TV grid."""
    if not exercises:
        cards_markup = '<div class="empty-column">No exercises scheduled for this column.</div>'
    else:
        cards_markup = "".join(
            exercise_card(exercise, index)
            for index, exercise in enumerate(exercises, start=1)
        )

    return f"""
        <section class="workout-column" aria-label="{html_escape(title)} workout">
            <div class="column-heading">{html_escape(title)}</div>
            <div class="exercise-list">{cards_markup}</div>
        </section>
    """


def inject_today_styles() -> None:
    """Add TV-route CSS for the compact header, two-column layout, and hidden Streamlit chrome."""
    st.markdown(
        """
        <style>
            :root {
                --today-bg: #030407;
                --today-panel: rgba(15, 23, 42, 0.78);
                --today-border: rgba(248, 250, 252, 0.14);
                --today-muted: #94a3b8;
                --today-text: #f8fafc;
                --today-red: #ef4444;
                --today-gold: #f59e0b;
            }

            html, body, [data-testid="stAppViewContainer"], .stApp {
                width: 100vw;
                min-height: 100vh;
                overflow-x: hidden;
                background: #030407;
            }

            .stApp {
                background:
                    radial-gradient(circle at 22% 0%, rgba(239, 68, 68, 0.22), transparent 25rem),
                    radial-gradient(circle at 100% 18%, rgba(245, 158, 11, 0.13), transparent 22rem),
                    linear-gradient(180deg, #030407 0%, #070a10 44%, #0f172a 100%);
                color: var(--today-text);
            }

            /* TV-only route: hide Streamlit navigation, headers, toolbar, and default footer chrome. */
            [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="collapsedControl"],
            [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"],
            [data-testid="manage-app-button"], #MainMenu, footer, header { display: none !important; }

            .block-container {
                width: 100vw;
                max-width: none;
                min-height: 100vh;
                padding: clamp(0.7rem, 1.6vh, 1.35rem) clamp(0.75rem, 2.4vw, 2.3rem) clamp(0.75rem, 1.8vh, 1.5rem);
            }

            /* TV-specific layout: compact centered brand/date header above two fixed workout columns. */
            .today-tv-shell {
                width: 100%;
                min-height: calc(100vh - 2rem);
                display: flex;
                flex-direction: column;
                gap: clamp(0.65rem, 1.25vh, 1.15rem);
            }

            .today-header {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: clamp(0.25rem, 0.55vh, 0.45rem);
                padding: clamp(0.45rem, 1vh, 0.9rem) 1rem clamp(0.35rem, 0.8vh, 0.65rem);
                text-align: center;
            }

            .today-logo {
                display: block;
                width: min(34vw, 360px);
                max-height: clamp(38px, 5.5vh, 74px);
                object-fit: contain;
                object-position: center;
                filter: drop-shadow(0 0.8rem 1.9rem rgba(239, 68, 68, 0.22));
            }

            .today-wordmark {
                color: #ffffff;
                font-size: clamp(1.25rem, 2.8vw, 2.4rem);
                font-weight: 950;
                letter-spacing: 0.18em;
            }

            .today-wordmark span { color: var(--today-red); }

            .today-date {
                color: var(--today-gold);
                font-size: clamp(0.78rem, 1.35vw, 1.2rem);
                font-weight: 950;
                letter-spacing: 0.22em;
                text-transform: uppercase;
            }

            .workout-grid {
                display: grid;
                grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
                gap: clamp(0.75rem, 1.8vw, 1.6rem);
                align-items: start;
                flex: 1 1 auto;
            }

            .workout-column {
                min-width: 0;
                display: flex;
                flex-direction: column;
                gap: clamp(0.55rem, 0.95vh, 0.85rem);
            }

            .column-heading {
                align-self: flex-start;
                border: 1px solid rgba(239, 68, 68, 0.34);
                border-radius: 999px;
                padding: clamp(0.34rem, 0.7vh, 0.55rem) clamp(0.8rem, 1.6vw, 1.2rem);
                color: #ffffff;
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.28), rgba(245, 158, 11, 0.08));
                box-shadow: 0 0.9rem 1.8rem rgba(0, 0, 0, 0.18);
                font-size: clamp(1rem, 2vw, 1.65rem);
                font-weight: 1000;
                letter-spacing: -0.02em;
                line-height: 1;
            }

            .exercise-list {
                display: flex;
                flex-direction: column;
                gap: clamp(0.5rem, 0.95vh, 0.78rem);
            }

            .today-exercise-card {
                display: grid;
                grid-template-columns: clamp(2.1rem, 3.6vw, 3.3rem) clamp(5.6rem, 11vw, 8.4rem) minmax(0, 1fr);
                align-items: center;
                gap: clamp(0.55rem, 1.1vw, 0.95rem);
                border: 1px solid var(--today-border);
                border-left: 0.26rem solid rgba(239, 68, 68, 0.86);
                border-radius: clamp(0.85rem, 1.5vw, 1.25rem);
                padding: clamp(0.45rem, 0.95vh, 0.75rem) clamp(0.55rem, 1.3vw, 0.95rem);
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.78), rgba(3, 4, 7, 0.62));
                box-shadow: 0 0.9rem 2rem rgba(0, 0, 0, 0.22);
            }

            .exercise-number {
                color: rgba(248, 250, 252, 0.4);
                font-size: clamp(1.25rem, 2.55vw, 2.25rem);
                font-weight: 1000;
                line-height: 1;
                letter-spacing: -0.08em;
            }

            .exercise-art {
                width: 100%;
                aspect-ratio: 1 / 1;
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: clamp(0.75rem, 1.2vw, 1rem);
                display: grid;
                place-items: center;
                overflow: hidden;
                background: radial-gradient(circle at 50% 42%, rgba(248, 250, 252, 0.11), rgba(15, 23, 42, 0.42));
            }

            .exercise-diagram {
                width: 100%;
                height: 100%;
                object-fit: contain;
                padding: 0.18rem;
                mix-blend-mode: screen;
            }

            .exercise-diagram-placeholder {
                padding: 0.35rem;
                color: rgba(148, 163, 184, 0.74);
                font-size: clamp(0.55rem, 0.85vw, 0.72rem);
                font-weight: 900;
                letter-spacing: 0.08em;
                line-height: 1.15;
                text-align: center;
                text-transform: uppercase;
            }

            .exercise-main { min-width: 0; }

            .exercise-name {
                color: #ffffff;
                font-size: clamp(1.05rem, 2.15vw, 1.95rem);
                font-weight: 950;
                line-height: 0.98;
                letter-spacing: -0.045em;
            }

            .exercise-meta-line {
                display: flex;
                flex-wrap: wrap;
                gap: 0.3rem;
                margin-top: 0.22rem;
                color: var(--today-muted);
                font-size: clamp(0.52rem, 0.86vw, 0.72rem);
                font-weight: 850;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }

            .exercise-muscles::before { content: "• "; color: var(--today-red); }

            .exercise-prescription {
                display: flex;
                align-items: stretch;
                flex-wrap: wrap;
                gap: clamp(0.3rem, 0.65vw, 0.5rem);
                margin-top: clamp(0.38rem, 0.75vh, 0.58rem);
            }

            .sets-reps {
                min-width: clamp(3.15rem, 5vw, 4.6rem);
                border-radius: 0.7rem;
                padding: 0.38rem 0.48rem 0.32rem;
                text-align: center;
                color: #ffffff;
                background: rgba(239, 68, 68, 0.18);
                border: 1px solid rgba(239, 68, 68, 0.36);
                font-size: clamp(0.9rem, 1.75vw, 1.5rem);
                font-weight: 1000;
                line-height: 0.95;
            }

            .sets-reps span {
                display: block;
                margin-top: 0.2rem;
                color: #fecaca;
                font-size: clamp(0.42rem, 0.62vw, 0.54rem);
                letter-spacing: 0.16em;
            }

            .reps-pill { min-width: clamp(4.5rem, 7.4vw, 6.9rem); }
            .rest-pill { color: var(--today-muted); }

            .empty-column {
                border: 1px dashed rgba(148, 163, 184, 0.28);
                border-radius: 1rem;
                padding: 1rem;
                color: var(--today-muted);
                font-weight: 800;
                text-align: center;
            }

            .today-footer-bar {
                height: clamp(0.35rem, 0.65vh, 0.6rem);
                border-radius: 999px;
                background: linear-gradient(90deg, rgba(239, 68, 68, 0), rgba(239, 68, 68, 0.76), rgba(245, 158, 11, 0.72), rgba(239, 68, 68, 0));
                opacity: 0.78;
            }

            @media (orientation: landscape) {
                .today-tv-shell::before {
                    content: "Portrait TV display: rotate this screen to 9:16 for the intended layout.";
                    border: 1px solid rgba(245, 158, 11, 0.32);
                    border-radius: 1rem;
                    padding: 0.75rem 1rem;
                    color: #fde68a;
                    background: rgba(245, 158, 11, 0.09);
                    font-weight: 850;
                    text-align: center;
                }
            }

            @media (max-width: 760px) {
                .workout-grid { grid-template-columns: 1fr; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_fullscreen_helper() -> None:
    """Render an optional full-screen button and F-key shortcut."""
    components.html(
        """
        <button id="mf-fullscreen-button" type="button" aria-label="Enter full screen">Enter Full Screen · F</button>
        <style>
            #mf-fullscreen-button {
                position: fixed;
                top: 18px;
                right: 18px;
                z-index: 2147483647;
                border: 1px solid rgba(248, 250, 252, 0.2);
                border-radius: 999px;
                padding: 0.58rem 0.88rem;
                color: #f8fafc;
                background: rgba(3, 4, 7, 0.76);
                font: 800 12px/1.1 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                cursor: pointer;
                backdrop-filter: blur(12px);
            }
        </style>
        <script>
            const button = document.getElementById("mf-fullscreen-button");
            const targetDocument = window.parent && window.parent.document ? window.parent.document : document;
            const targetElement = targetDocument.documentElement;

            function fullscreenElement() {
                return targetDocument.fullscreenElement || targetDocument.webkitFullscreenElement || null;
            }

            function updateButton() {
                button.style.display = fullscreenElement() ? "none" : "inline-flex";
            }

            async function enterFullscreen() {
                if (fullscreenElement()) return;
                if (targetElement.requestFullscreen) {
                    await targetElement.requestFullscreen();
                } else if (targetElement.webkitRequestFullscreen) {
                    targetElement.webkitRequestFullscreen();
                }
                updateButton();
            }

            button.addEventListener("click", enterFullscreen);
            targetDocument.addEventListener("fullscreenchange", updateButton);
            targetDocument.addEventListener("webkitfullscreenchange", updateButton);
            targetDocument.addEventListener("keydown", (event) => {
                if (event.key && event.key.toLowerCase() === "f" && !event.metaKey && !event.ctrlKey && !event.altKey) {
                    enterFullscreen();
                }
            });
            updateButton();
        </script>
        """,
        height=1,
        scrolling=False,
    )


def render_today_page() -> None:
    """Render the complete display-only TV page."""
    workout = todays_workout(date.today())
    weighted_exercises = workout.get("weightedExercises") or workout.get("exercises", [])
    bodyweight_exercises = workout.get("bodyweightExercises") or workout.get("nonWeightedExercises", [])

    inject_today_styles()
    render_fullscreen_helper()
    st.markdown(
        f"""
        <main class="today-tv-shell">
            <section class="today-header" aria-label="MarshallFit daily workout date">
                {logo_markup()}
                <div class="today-date">{html_escape(friendly_date(workout['date']))}</div>
            </section>
            <div class="workout-grid">
                {workout_column('Weighted', weighted_exercises)}
                {workout_column('Bodyweight', bodyweight_exercises)}
            </div>
            <div class="today-footer-bar" aria-hidden="true"></div>
        </main>
        """,
        unsafe_allow_html=True,
    )


render_today_page()
