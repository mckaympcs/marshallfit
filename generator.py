"""Workout generation helpers for Marshall Fit.

Beginner note:
    The Streamlit app and any future CLI can import this module instead of
    duplicating workout-selection rules. Keeping the generation logic here makes
    it easier to change the app design later without rewriting the engine.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

# These paths are relative to this file, so the generator works even if the
# command is started from a different folder.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_PATH = DATA_DIR / "templates.json"
EXERCISES_PATH = DATA_DIR / "exercises.json"
DIAGRAMS_DIR = BASE_DIR / "diagrams"

# Exercise load types that are reasonable to offer when the user asks for a
# bodyweight-focused workout. Some use a light tool or assistance but are still
# not heavy barbell/dumbbell work.
BODYWEIGHT_LOAD_TYPES = {
    "bodyweight",
    "bodyweight_assisted",
    "bodyweight_or_assisted",
    "bodyweight_or_weighted",
    "bodyweight_with_tool",
}

# Exercise load types that are reasonable to offer for a weighted workout.
WEIGHTED_LOAD_TYPES = {
    "weighted",
    "power",
    "bodyweight_or_weighted",
}


def load_templates() -> list[dict[str, Any]]:
    """Load workout templates from ``data/templates.json``."""
    with TEMPLATES_PATH.open(encoding="utf-8") as template_file:
        template_data = json.load(template_file)

    return template_data["templates"]


def load_exercises() -> list[dict[str, Any]]:
    """Load the exercise library from ``data/exercises.json``."""
    with EXERCISES_PATH.open(encoding="utf-8") as exercise_file:
        exercise_data = json.load(exercise_file)

    return exercise_data["exercises"]


def get_template_by_id(template_id: str) -> dict[str, Any]:
    """Find one template by its id, raising a clear error if it is missing."""
    for template in load_templates():
        if template["id"] == template_id:
            return template

    raise ValueError(f"Unknown workout template id: {template_id}")


def generate_workout(template_id: str, mode: str = "weighted") -> dict[str, Any]:
    """Generate a workout for a template and mode.

    Args:
        template_id: The id from ``data/templates.json``.
        mode: Either ``"weighted"`` or ``"bodyweight"``.

    Returns:
        A dictionary with the selected template and an ordered list of exercises.
    """
    if mode not in {"weighted", "bodyweight"}:
        raise ValueError('mode must be either "weighted" or "bodyweight"')

    template = get_template_by_id(template_id)
    exercises = load_exercises()
    used_exercise_ids: set[str] = set()
    generated_exercises = []

    for slot in template["slots"]:
        exercise = _choose_exercise_for_slot(slot, exercises, mode, used_exercise_ids)
        used_exercise_ids.add(exercise["id"])
        generated_exercises.append(_format_generated_exercise(slot, exercise))

    return {
        "template_id": template["id"],
        "template_name": template["name"],
        "template_description": template.get("description", ""),
        "mode": mode,
        "exercises": generated_exercises,
    }


def regenerate_exercise(
    template_id: str,
    mode: str,
    slot_id: str,
    current_exercises: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Regenerate a single exercise for one template slot.

    The caller passes the currently displayed exercises so the replacement can
    avoid duplicating exercises already present in the workout whenever the
    exercise library has enough alternatives.
    """
    if mode not in {"weighted", "bodyweight"}:
        raise ValueError('mode must be either "weighted" or "bodyweight"')

    template = get_template_by_id(template_id)
    slot = next((item for item in template["slots"] if item["id"] == slot_id), None)
    if slot is None:
        raise ValueError(f"Unknown template slot id: {slot_id}")

    used_exercise_ids = {
        exercise.get("exercise_id")
        for exercise in current_exercises or []
        if exercise.get("slot_id") != slot_id and exercise.get("exercise_id")
    }
    exercises = load_exercises()
    replacement = _choose_exercise_for_slot(slot, exercises, mode, used_exercise_ids)
    return _format_generated_exercise(slot, replacement)


def _choose_exercise_for_slot(
    slot: dict[str, Any],
    exercises: list[dict[str, Any]],
    mode: str,
    used_exercise_ids: set[str],
) -> dict[str, Any]:
    """Pick one exercise that fits a template slot.

    The main path respects the selected workout mode. If a slot does not have a
    perfect mode match yet, the fallback still fills the workout using any
    movement-pattern match from the current data instead of failing in the UI.
    """
    matching_exercises = [
        exercise
        for exercise in exercises
        if _exercise_matches_slot(exercise, slot)
        and _exercise_matches_mode(exercise, mode)
        and exercise["id"] not in used_exercise_ids
    ]

    if not matching_exercises:
        matching_exercises = [
            exercise
            for exercise in exercises
            if _exercise_matches_slot(exercise, slot)
            and exercise["id"] not in used_exercise_ids
        ]

    if not matching_exercises:
        raise ValueError(f"No exercise found for template slot: {slot['id']}")

    return random.choice(matching_exercises)


def _exercise_matches_slot(exercise: dict[str, Any], slot: dict[str, Any]) -> bool:
    """Return True when an exercise fits a template slot."""
    slot_patterns = {
        slot["movement_pattern"],
        *slot.get("alternate_movement_patterns", []),
    }
    exercise_patterns = set(exercise.get("movement_patterns", []))
    exercise_template_slots = set(exercise.get("template_slots", []))

    return bool(
        slot["id"] in exercise_template_slots
        or slot_patterns.intersection(exercise_patterns)
    )


def _exercise_matches_mode(exercise: dict[str, Any], mode: str) -> bool:
    """Return True when an exercise belongs in the selected workout mode."""
    load_type = exercise.get("load_type")

    if mode == "bodyweight":
        return bool(exercise.get("bodyweight")) or load_type in BODYWEIGHT_LOAD_TYPES

    return load_type in WEIGHTED_LOAD_TYPES


def _format_generated_exercise(
    slot: dict[str, Any], exercise: dict[str, Any]
) -> dict[str, Any]:
    """Combine slot prescription details with exercise-library details."""
    muscle_focus = exercise.get("muscle_focus", [])
    sets, reps = _prescribe_sets_and_reps(slot, exercise)

    return {
        "slot_id": slot["id"],
        "slot_name": slot["name"],
        "exercise_id": exercise["id"],
        "name": exercise["name"],
        "category": _exercise_category(slot, exercise),
        "movement_pattern": _friendly_list(exercise.get("movement_patterns", [])),
        "primary_muscles": muscle_focus[:1],
        "secondary_muscles": muscle_focus[1:],
        "sets": sets,
        "reps": reps,
        "diagram_path": _find_diagram_path(exercise),
    }


def _prescribe_sets_and_reps(
    slot: dict[str, Any], exercise: dict[str, Any]
) -> tuple[int, str]:
    """Return a simple set/rep target based on the exercise type.

    The app keeps working sets consistent at three per exercise, then adjusts
    the rep range by role: heavy compound lifts stay lower, accessories sit in
    the moderate hypertrophy range, and isolations/bodyweight moves can go a
    little higher.
    """
    role = exercise.get("exercise_role") or slot.get("exercise_role", "")
    movement_patterns = set(exercise.get("movement_patterns", []))
    unilateral_suffix = " each side" if exercise.get("unilateral") else ""

    if role == "compound_primary":
        return 3, f"6-8{unilateral_suffix}"

    if role in {"compound_accessory", "power", "accessory"}:
        return 3, f"8-10{unilateral_suffix}"

    if role in {"isolation", "accessory_mobility"}:
        return 3, f"10-12{unilateral_suffix}"

    if exercise.get("bodyweight"):
        return 3, f"8-12{unilateral_suffix}"

    if movement_patterns.intersection(
        {
            "horizontal_push",
            "incline_push",
            "vertical_push",
            "horizontal_pull",
            "vertical_pull",
            "quad_compound",
            "hip_hinge",
        }
    ):
        return 3, f"6-8{unilateral_suffix}"

    return int(slot.get("sets", 3)), str(slot.get("reps", f"8-10{unilateral_suffix}"))


def _exercise_category(slot: dict[str, Any], exercise: dict[str, Any]) -> str:
    """Return the short subtitle shown below each exercise name."""
    role = exercise.get("exercise_role") or slot.get("exercise_role", "")
    movement_patterns = exercise.get("movement_patterns", [])

    role_label = role.replace("_", " ").title()
    pattern_label = _friendly_list(movement_patterns[:1])

    if role_label and pattern_label:
        return f"{role_label} · {pattern_label}"

    return role_label or slot["name"]


def resolve_diagram_path(exercise_id: str, configured_path: str | None = None) -> str:
    """Return the local diagram path for an exercise id.

    Exercise diagrams are stored in ``diagrams/`` and named after the stable
    exercise id from ``data/exercises.json``. A configured path is still
    honored when it points at an existing file so older data can keep working,
    but generated workout cards default to the id-matched PNG files.
    """
    if configured_path:
        configured_file = BASE_DIR / configured_path
        if configured_file.exists():
            return str(configured_file.relative_to(BASE_DIR))

    for extension in (".png", ".jpg", ".jpeg", ".svg", ".webp"):
        diagram_path = DIAGRAMS_DIR / f"{exercise_id}{extension}"
        if diagram_path.exists():
            return str(diagram_path.relative_to(BASE_DIR))

    return f"diagrams/{exercise_id}.png"


def _find_diagram_path(exercise: dict[str, Any]) -> str:
    """Return the exercise diagram path used by generated workout cards."""
    return resolve_diagram_path(exercise["id"], exercise.get("diagram_path"))


def _friendly_list(values: list[str]) -> str:
    """Turn data values such as ``horizontal_push`` into readable text."""
    return ", ".join(value.replace("_", " ").title() for value in values)
