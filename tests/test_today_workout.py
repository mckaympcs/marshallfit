"""Tests for the automatic Today's Workout weekly schedule."""

from datetime import date
from unittest.mock import patch

import today_workout


def test_weekday_fallback_schedule_uses_expected_weighted_templates() -> None:
    week = {
        date(2026, 8, 17): ("Chest / Triceps", "chest_triceps"),
        date(2026, 8, 18): ("Back / Biceps", "back_biceps"),
        date(2026, 8, 19): ("Legs", "lower_body"),
        date(2026, 8, 21): ("Upper Body", "upper_body"),
        date(2026, 8, 22): ("Lower Body", "lower_body"),
    }

    with patch.object(today_workout.generator, "generate_workout") as generate:
        generate.return_value = {"exercises": [{"name": "Generated"}]}

        for workout_date, (label, template) in week.items():
            workout = today_workout.deterministic_workout_for_date(workout_date)
            assert workout["workoutType"] == label
            assert workout["displayMode"] == "Weighted"
            assert workout["isRestDay"] is False
            assert "bodyweightExercises" not in workout
            generate.assert_called_with(template, "weighted")


def test_thursday_and_sunday_are_rest_days() -> None:
    with patch.object(today_workout.generator, "generate_workout") as generate:
        for workout_date in (date(2026, 8, 20), date(2026, 8, 23)):
            workout = today_workout.deterministic_workout_for_date(workout_date)
            assert workout["workoutType"] == "Rest Day"
            assert workout["isRestDay"] is True
            assert workout["exercises"] == []

        generate.assert_not_called()


def test_saved_workout_only_exposes_weighted_exercises() -> None:
    scheduled = {
        "workoutType": "Upper Body",
        "weightedExercises": [{"name": "Bench Press"}],
        "nonWeightedExercises": [{"name": "Push Up"}],
    }
    with patch.object(today_workout, "load_schedule", return_value={"2026-08-21": scheduled}):
        workout = today_workout.todays_workout(date(2026, 8, 21))

    assert workout["exercises"] == [{"name": "Bench Press"}]
    assert "bodyweightExercises" not in workout

