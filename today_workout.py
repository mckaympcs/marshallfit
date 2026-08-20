"""Display-only helpers for the MarshallFit Today's Workout TV page.

The Streamlit route in ``pages/today.py`` imports this module so the page can
reuse the existing generator and scheduler data without duplicating UI controls
from the main app.
"""

from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path
from typing import Any

import generator

BASE_DIR = Path(__file__).resolve().parent
SCHEDULE_PATH = BASE_DIR / "data" / "scheduled_workouts.json"
WORKOUT_TYPE_TO_TEMPLATE = {
    "Chest / Triceps": "chest_triceps",
    "Back / Biceps": "back_biceps",
    "Lower Body": "lower_body",
    "Upper Body": "upper_body",
}
WEEKDAY_WORKOUTS = {
    0: ("Chest / Triceps", "chest_triceps"),
    1: ("Back / Biceps", "back_biceps"),
    2: ("Legs", "lower_body"),
    3: ("Rest Day", None),
    4: ("Upper Body", "upper_body"),
    5: ("Lower Body", "lower_body"),
    6: ("Rest Day", None),
}


def load_schedule() -> dict[str, Any]:
    """Load saved scheduled workouts when the scheduler data file exists."""
    if not SCHEDULE_PATH.exists():
        return {}

    with SCHEDULE_PATH.open(encoding="utf-8") as schedule_file:
        return json.load(schedule_file)


def deterministic_workout_for_date(workout_date: date) -> dict[str, Any]:
    """Generate the weekday's weighted fallback, keeping it stable all day."""
    workout_type, template_id = WEEKDAY_WORKOUTS[workout_date.weekday()]
    if template_id is None:
        return {
            "date": workout_date.isoformat(),
            "workoutType": workout_type,
            "displayMode": "Rest Day",
            "source": "Weekly default schedule",
            "isRestDay": True,
            "weightedExercises": [],
            "exercises": [],
        }

    previous_random_state = random.getstate()
    try:
        # The interactive generator uses randomness. Isolate and seed it so a
        # generated daily plan stays unchanged across page refreshes.
        random.seed(f"marshallfit-today-{workout_date.isoformat()}-{template_id}-weighted")
        exercises = generator.generate_workout(template_id, "weighted")["exercises"]
    finally:
        random.setstate(previous_random_state)

    return {
        "date": workout_date.isoformat(),
        "workoutType": workout_type,
        "displayMode": "Weighted",
        "source": "Weekly default schedule",
        "isRestDay": False,
        "weightedExercises": exercises,
        "exercises": exercises,
    }


def todays_workout(workout_date: date | None = None) -> dict[str, Any]:
    """Return today's scheduled workout, or a deterministic fallback workout."""
    selected_date = workout_date or date.today()
    scheduled_workout = load_schedule().get(selected_date.isoformat())

    if scheduled_workout:
        weighted_exercises = scheduled_workout.get("weightedExercises", [])

        return {
            "date": selected_date.isoformat(),
            "workoutType": scheduled_workout.get("workoutType", "Scheduled Workout"),
            "displayMode": "Weighted",
            "source": "Saved scheduler workout",
            "isRestDay": False,
            "weightedExercises": weighted_exercises,
            "exercises": weighted_exercises,
        }

    return deterministic_workout_for_date(selected_date)
