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


def load_schedule() -> dict[str, Any]:
    """Load saved scheduled workouts when the scheduler data file exists."""
    if not SCHEDULE_PATH.exists():
        return {}

    with SCHEDULE_PATH.open(encoding="utf-8") as schedule_file:
        return json.load(schedule_file)


def deterministic_workout_for_date(workout_date: date) -> dict[str, Any]:
    """Generate the fallback workout that should be stable for one calendar day."""
    workout_types = list(WORKOUT_TYPE_TO_TEMPLATE)
    workout_type = workout_types[workout_date.toordinal() % len(workout_types)]
    template_id = WORKOUT_TYPE_TO_TEMPLATE[workout_type]

    # The generator intentionally uses randomness for the interactive app. For
    # the TV display fallback, seed that same engine only during this call so the
    # same date produces the same exercise list without changing the generator.
    previous_random_state = random.getstate()
    random.seed(f"marshallfit-today-{workout_date.isoformat()}-{template_id}")
    try:
        generated_workout = generator.generate_workout(template_id, "weighted")
    finally:
        random.setstate(previous_random_state)

    return {
        "date": workout_date.isoformat(),
        "workoutType": workout_type,
        "displayMode": "Weighted",
        "source": "Date-based daily rotation",
        "exercises": generated_workout["exercises"],
    }


def todays_workout(workout_date: date | None = None) -> dict[str, Any]:
    """Return today's scheduled workout, or a deterministic fallback workout."""
    selected_date = workout_date or date.today()
    scheduled_workout = load_schedule().get(selected_date.isoformat())

    if scheduled_workout:
        weighted_exercises = scheduled_workout.get("weightedExercises", [])
        bodyweight_exercises = scheduled_workout.get("nonWeightedExercises", [])
        if weighted_exercises:
            display_mode = "Weighted"
            exercises = weighted_exercises
        else:
            display_mode = "Non-Weighted"
            exercises = bodyweight_exercises

        return {
            "date": selected_date.isoformat(),
            "workoutType": scheduled_workout.get("workoutType", "Scheduled Workout"),
            "displayMode": display_mode,
            "source": "Saved scheduler workout",
            "exercises": exercises,
        }

    return deterministic_workout_for_date(selected_date)
