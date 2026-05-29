"""Full-screen Today's Workout display route for a portrait TV."""

from __future__ import annotations

import base64
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

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


def logo_markup() -> str:
    """Return an inline logo so the TV page has no external asset dependency."""
    if HORIZONTAL_LOGO_PATH.exists():
        encoded_logo = base64.b64encode(HORIZONTAL_LOGO_PATH.read_bytes()).decode("utf-8")
        return f'<img class="today-logo" src="data:image/svg+xml;base64,{encoded_logo}" alt="MarshallFit" />'
    return '<div class="today-wordmark">MARSHALL<span>FIT</span></div>'


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
    rest_markup = f'<span class="exercise-rest">Rest {html_escape(rest)}</span>' if rest else ""
    category = exercise.get("category") or exercise.get("slot_name") or "Training Slot"

    return f"""
        <article class="today-exercise-card">
            <div class="exercise-number">{number:02d}</div>
            <div class="exercise-main">
                <div class="exercise-name">{html_escape(exercise.get('name', 'Exercise'))}</div>
                <div class="exercise-meta-line">
                    <span>{html_escape(category)}</span>
                    {muscles_markup}
                </div>
            </div>
            <div class="exercise-prescription">
                <div class="sets-reps">{html_escape(exercise.get('sets', '3'))}<span>SETS</span></div>
                <div class="sets-reps">{html_escape(exercise.get('reps', '8-10'))}<span>REPS</span></div>
                {rest_markup}
            </div>
        </article>
    """


def inject_today_styles() -> None:
    """Add CSS scoped to the TV workout display page."""
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
                    radial-gradient(circle at 22% 0%, rgba(239, 68, 68, 0.27), transparent 28rem),
                    radial-gradient(circle at 100% 18%, rgba(245, 158, 11, 0.16), transparent 24rem),
                    linear-gradient(180deg, #030407 0%, #070a10 44%, #0f172a 100%);
                color: var(--today-text);
            }

            [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="collapsedControl"],
            [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu,
            footer:not(.today-footer), header { display: none !important; }

            .block-container {
                width: 100vw;
                max-width: none;
                min-height: 100vh;
                padding: clamp(1.6rem, 4vh, 3.8rem) clamp(1.25rem, 4vw, 4.5rem) clamp(1.2rem, 3vh, 3rem);
            }

            .today-tv-shell {
                width: 100%;
                min-height: calc(100vh - clamp(2.8rem, 7vh, 6.8rem));
                display: flex;
                flex-direction: column;
                gap: clamp(1rem, 2vh, 2rem);
            }

            .today-hero {
                border: 1px solid rgba(239, 68, 68, 0.32);
                border-radius: clamp(1.4rem, 3vw, 2.8rem);
                padding: clamp(1.25rem, 3vh, 2.4rem);
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(3, 4, 7, 0.74));
                box-shadow: 0 2rem 5rem rgba(0, 0, 0, 0.38);
            }

            .today-logo {
                width: min(48vw, 440px);
                max-height: 96px;
                object-fit: contain;
                object-position: left center;
                filter: drop-shadow(0 1rem 2.2rem rgba(239, 68, 68, 0.22));
            }

            .today-wordmark {
                color: #ffffff;
                font-size: clamp(1.1rem, 3vw, 2.1rem);
                font-weight: 950;
                letter-spacing: 0.18em;
            }

            .today-wordmark span { color: var(--today-red); }

            .today-kicker {
                margin-top: clamp(1.1rem, 2vh, 1.8rem);
                color: var(--today-gold);
                font-size: clamp(0.88rem, 1.55vw, 1.35rem);
                font-weight: 900;
                letter-spacing: 0.24em;
                text-transform: uppercase;
            }

            .today-title {
                margin: 0.2rem 0 0;
                color: #ffffff;
                font-size: clamp(3.6rem, 9vw, 7.8rem);
                font-weight: 1000;
                letter-spacing: -0.07em;
                line-height: 0.86;
                text-transform: uppercase;
            }

            .today-summary {
                display: grid;
                grid-template-columns: 1.2fr 0.8fr;
                gap: clamp(0.8rem, 2vw, 1.4rem);
                margin-top: clamp(1rem, 2vh, 1.8rem);
            }

            .summary-card {
                border: 1px solid var(--today-border);
                border-radius: 1.35rem;
                padding: clamp(0.95rem, 1.9vh, 1.45rem);
                background: rgba(248, 250, 252, 0.055);
            }

            .summary-label {
                color: var(--today-muted);
                font-size: clamp(0.78rem, 1.25vw, 1rem);
                font-weight: 850;
                letter-spacing: 0.18em;
                text-transform: uppercase;
            }

            .summary-value {
                margin-top: 0.35rem;
                color: #ffffff;
                font-size: clamp(1.35rem, 3vw, 2.5rem);
                font-weight: 950;
                line-height: 1;
            }

            .exercise-list {
                display: flex;
                flex-direction: column;
                gap: clamp(0.68rem, 1.28vh, 1.1rem);
                flex: 1 1 auto;
            }

            .today-exercise-card {
                display: grid;
                grid-template-columns: minmax(4.1rem, 8vw) 1fr auto;
                align-items: center;
                gap: clamp(0.85rem, 2vw, 1.55rem);
                border: 1px solid var(--today-border);
                border-left: 0.38rem solid rgba(239, 68, 68, 0.86);
                border-radius: clamp(1rem, 2.1vw, 1.65rem);
                padding: clamp(0.85rem, 1.7vh, 1.4rem) clamp(0.95rem, 2.4vw, 1.7rem);
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.78), rgba(3, 4, 7, 0.62));
                box-shadow: 0 1rem 2.4rem rgba(0, 0, 0, 0.22);
            }

            .exercise-number {
                color: rgba(248, 250, 252, 0.38);
                font-size: clamp(1.6rem, 4vw, 3.35rem);
                font-weight: 1000;
                line-height: 1;
                letter-spacing: -0.08em;
            }

            .exercise-name {
                color: #ffffff;
                font-size: clamp(1.55rem, 3.85vw, 3.35rem);
                font-weight: 950;
                line-height: 0.98;
                letter-spacing: -0.045em;
            }

            .exercise-meta-line {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                margin-top: 0.35rem;
                color: var(--today-muted);
                font-size: clamp(0.78rem, 1.4vw, 1.08rem);
                font-weight: 800;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }

            .exercise-muscles::before { content: "• "; color: var(--today-red); }

            .exercise-prescription {
                display: flex;
                align-items: center;
                justify-content: flex-end;
                gap: clamp(0.55rem, 1.2vw, 0.9rem);
            }

            .sets-reps {
                min-width: clamp(4.4rem, 8vw, 6.3rem);
                border-radius: 1rem;
                padding: 0.62rem 0.72rem;
                text-align: center;
                color: #ffffff;
                background: rgba(239, 68, 68, 0.18);
                border: 1px solid rgba(239, 68, 68, 0.36);
                font-size: clamp(1.35rem, 3.2vw, 2.55rem);
                font-weight: 1000;
                line-height: 0.92;
            }

            .sets-reps span {
                display: block;
                margin-top: 0.3rem;
                color: #fecaca;
                font-size: clamp(0.52rem, 0.9vw, 0.72rem);
                letter-spacing: 0.18em;
            }

            .exercise-rest {
                color: var(--today-muted);
                font-weight: 900;
                text-transform: uppercase;
            }

            .today-footer {
                display: flex;
                justify-content: space-between;
                gap: 1rem;
                color: rgba(148, 163, 184, 0.86);
                font-size: clamp(0.78rem, 1.2vw, 1rem);
                font-weight: 750;
                letter-spacing: 0.08em;
                text-transform: uppercase;
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

            @media (max-width: 760px), (max-aspect-ratio: 3/5) {
                .today-summary { grid-template-columns: 1fr; }
                .today-exercise-card { grid-template-columns: 3.8rem 1fr; }
                .exercise-prescription {
                    grid-column: 2;
                    justify-content: flex-start;
                }
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
    exercises = workout.get("exercises", [])
    exercise_markup = "".join(exercise_card(exercise, index) for index, exercise in enumerate(exercises, start=1))

    inject_today_styles()
    render_fullscreen_helper()
    st.markdown(
        f"""
        <main class="today-tv-shell">
            <section class="today-hero">
                {logo_markup()}
                <div class="today-kicker">{html_escape(friendly_date(workout['date']))}</div>
                <h1 class="today-title">TODAY’S<br>WORKOUT</h1>
                <div class="today-summary">
                    <div class="summary-card">
                        <div class="summary-label">Workout Type</div>
                        <div class="summary-value">{html_escape(workout['workoutType'])}</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-label">Display Plan</div>
                        <div class="summary-value">{html_escape(workout['displayMode'])}</div>
                    </div>
                </div>
            </section>
            <section class="exercise-list" aria-label="Today’s exercise list">
                {exercise_markup}
            </section>
            <footer class="today-footer">
                <span>{html_escape(workout['source'])}</span>
                <span>{len(exercises)} exercises · MarshallFit</span>
            </footer>
        </main>
        """,
        unsafe_allow_html=True,
    )


render_today_page()
