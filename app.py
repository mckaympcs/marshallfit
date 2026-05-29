"""Simple Streamlit interface for the Marshall Fit workout generator.

Run this app locally with:
    streamlit run app.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from generator import generate_workout, load_templates

# The app file lives in the project root, so this path lets us check whether a
# diagram image exists before asking Streamlit to display it.
BASE_DIR = Path(__file__).resolve().parent
EXERCISES_PATH = BASE_DIR / "data" / "exercises.json"
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


# Streamlit reruns this script from top to bottom whenever the user changes a
# widget. Keeping the page setup near the top makes the app easy to scan.
st.set_page_config(
    page_title="Marshall Fit Workout Generator",
    page_icon="💪",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: rgba(255, 76, 90, 0.18);
            box-shadow: 0 10px 28px rgba(17, 24, 39, 0.06);
        }

        .diagram-placeholder {
            align-items: center;
            aspect-ratio: 1 / 1;
            background:
                linear-gradient(135deg, rgba(255, 76, 90, 0.12), rgba(255, 185, 68, 0.16)),
                #f8fafc;
            border: 1px dashed rgba(255, 76, 90, 0.45);
            border-radius: 14px;
            color: #475569;
            display: flex;
            flex-direction: column;
            font-size: 0.72rem;
            font-weight: 700;
            gap: 0.2rem;
            justify-content: center;
            min-height: 86px;
            padding: 0.65rem;
            text-align: center;
            text-transform: uppercase;
        }

        .diagram-placeholder span {
            display: block;
            font-size: 1.35rem;
            line-height: 1;
        }

        .workout-column-title {
            color: #111827;
            font-size: 1.08rem;
            font-weight: 900;
            letter-spacing: 0.06em;
            margin: 0 0 0.55rem;
            text-transform: uppercase;
        }

        .exercise-title {
            font-size: 1.08rem;
            font-weight: 900;
            line-height: 1.15;
            margin: 0 0 0.18rem;
        }

        .exercise-category {
            color: #64748b;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            margin: 0;
            text-transform: uppercase;
        }

        .sets-reps-pill {
            background: #111827;
            border-radius: 999px;
            color: #ffffff;
            display: inline-block;
            font-size: 0.86rem;
            font-weight: 900;
            line-height: 1.1;
            padding: 0.45rem 0.72rem;
            text-align: center;
            white-space: nowrap;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Marshall Fit Workout Generator")
st.write(
    "Generate paired six-exercise weighted and bodyweight workouts with compact "
    "diagram, movement type, and set/rep rows."
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


def friendly_label(value: str) -> str:
    """Turn data keys such as ``horizontal_push`` into readable labels."""
    return value.replace("_", " ").replace("-", " ").title()


def list_to_cell(value: Any) -> str:
    """Display list data in a compact, editable table cell."""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)

    return "" if value is None else str(value)


def render_diagram(exercise: dict[str, Any]) -> None:
    """Render an exercise diagram or a compact placeholder in its position."""
    diagram_path = exercise["diagram_path"]
    diagram_file = BASE_DIR / diagram_path

    if diagram_file.exists():
        st.image(str(diagram_file), use_container_width=True)
    else:
        st.markdown(
            """
            <div class="diagram-placeholder">
                <span>↔</span>
                Diagram
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_exercise_row(exercise: dict[str, Any]) -> None:
    """Render one compact generated-workout row."""
    with st.container(border=True):
        diagram_column, details_column, prescription_column = st.columns(
            [0.95, 1.75, 0.95], gap="small", vertical_alignment="center"
        )

        with diagram_column:
            render_diagram(exercise)

        with details_column:
            st.markdown(
                f'<div class="exercise-title">{exercise["name"]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="exercise-category">{exercise["category"]}</div>',
                unsafe_allow_html=True,
            )

        with prescription_column:
            st.markdown(
                '<div class="sets-reps-pill">'
                f"{exercise['sets']} sets × {exercise['reps']} reps"
                "</div>",
                unsafe_allow_html=True,
            )


def render_workout_column(title: str, workout: dict[str, Any]) -> None:
    """Render six generated exercises for one workout mode."""
    st.markdown(
        f'<div class="workout-column-title">{title}</div>',
        unsafe_allow_html=True,
    )

    for exercise in workout["exercises"][:6]:
        render_exercise_row(exercise)


def cell_to_list(value: Any) -> list[str]:
    """Convert a comma-separated editable table cell back into JSON list data."""
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if value is None:
        return []

    return [item.strip() for item in str(value).split(",") if item.strip()]


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


def table_row_to_exercise(
    row: dict[str, Any], original: dict[str, Any] | None = None
) -> dict[str, Any]:
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

    # Keep older exercise records compatible even if they predate an explicit
    # description field. The table exposes description separately from setup for
    # review, while the generator can continue to rely on the original fields.
    exercise["description"] = str(row.get("description", "")).strip()
    return exercise


def unique_values(exercises: list[dict[str, Any]], field: str) -> list[str]:
    """Collect sorted unique values for a scalar or list exercise field."""
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

    if bodyweight_filter != "Any" and bool(exercise.get("bodyweight", False)) != (
        bodyweight_filter == "Yes"
    ):
        return False

    if unilateral_filter != "Any" and bool(exercise.get("unilateral", False)) != (
        unilateral_filter == "Yes"
    ):
        return False

    return True


def render_workout_generator_page() -> None:
    """Render paired weighted and bodyweight workouts for the selected day."""
    st.header("Generate Workout")

    templates = load_templates()
    template_names = [template["name"] for template in templates]
    selected_template_name = st.selectbox("Workout day / template", template_names)
    selected_template = next(
        template for template in templates if template["name"] == selected_template_name
    )

    # The button prevents a new random workout from appearing on every widget change.
    # A paired view is created only when the user explicitly asks for one.
    if st.button("Generate Workout"):
        weighted_workout = generate_workout(selected_template["id"], "weighted")
        bodyweight_workout = generate_workout(selected_template["id"], "bodyweight")

        st.subheader(weighted_workout["template_name"])
        st.caption("Weighted on the left · Bodyweight on the right")
        st.markdown("---")

        weighted_column, bodyweight_column = st.columns(2, gap="large")

        with weighted_column:
            render_workout_column("Weighted", weighted_workout)

        with bodyweight_column:
            render_workout_column("Bodyweight", bodyweight_workout)


def render_exercise_library_page() -> None:
    """Render a filterable, editable table for the exercise JSON library."""
    st.header("Exercise Library")
    st.write(
        "Review every generated exercise, filter by the main programming fields, "
        "edit table values, add new exercises, or mark rows for deletion."
    )

    exercise_library = load_exercise_library()
    exercises = exercise_library["exercises"]

    st.subheader("Filters")
    filter_columns = st.columns(3)
    search_text = filter_columns[0].text_input(
        "Search name, ID, description, setup, or notes"
    )
    selected_load_types = filter_columns[1].multiselect(
        "Load type", unique_values(exercises, "load_type"), format_func=friendly_label
    )
    selected_difficulties = filter_columns[2].multiselect(
        "Difficulty", unique_values(exercises, "difficulty"), format_func=friendly_label
    )

    filter_columns = st.columns(3)
    selected_movements = filter_columns[0].multiselect(
        "Movement type",
        unique_values(exercises, "movement_patterns"),
        format_func=friendly_label,
    )
    selected_roles = filter_columns[1].multiselect(
        "Exercise role",
        unique_values(exercises, "exercise_role"),
        format_func=friendly_label,
    )
    selected_muscles = filter_columns[2].multiselect(
        "Muscle focus",
        unique_values(exercises, "muscle_focus"),
        format_func=friendly_label,
    )

    filter_columns = st.columns(3)
    selected_equipment = filter_columns[0].multiselect(
        "Equipment", unique_values(exercises, "equipment"), format_func=friendly_label
    )
    selected_template_slots = filter_columns[1].multiselect(
        "Template slots",
        unique_values(exercises, "template_slots"),
        format_func=friendly_label,
    )
    bodyweight_filter = filter_columns[2].selectbox("Bodyweight", ["Any", "Yes", "No"])
    unilateral_filter = filter_columns[2].selectbox("Unilateral", ["Any", "Yes", "No"])

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
    st.info(
        "Comma-separated fields become JSON lists when saved. Check the delete "
        "box beside any exercise you want removed, then click Save table changes."
    )

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
            "coaching_notes": st.column_config.TextColumn(
                "Coaching notes", width="large"
            ),
            "movement_patterns": st.column_config.TextColumn("Movement type"),
            "load_type": st.column_config.SelectboxColumn(
                "Load type", options=unique_values(exercises, "load_type")
            ),
            "difficulty": st.column_config.SelectboxColumn(
                "Difficulty", options=unique_values(exercises, "difficulty")
            ),
            "exercise_role": st.column_config.SelectboxColumn(
                "Exercise role", options=unique_values(exercises, "exercise_role")
            ),
        },
    )

    if st.button("Save table changes", type="primary"):
        edited_table_rows = edited_table_to_rows(edited_rows)
        edited_by_original_id = {
            original["id"]: row
            for original, row in zip(filtered_exercises, edited_table_rows)
        }
        existing_ids_outside_filter = {
            exercise["id"]
            for exercise in exercises
            if exercise["id"] not in edited_by_original_id
        }
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
            new_id = add_columns[0].text_input(
                "Exercise ID", placeholder="kettlebell_goblet_squat"
            )
            new_name = add_columns[1].text_input(
                "Exercise name", placeholder="Kettlebell Goblet Squat"
            )
            new_description = st.text_area("Description")
            new_setup = st.text_area("Setup")
            new_coaching_notes = st.text_area("Coaching notes (comma-separated)")

            add_columns = st.columns(3)
            new_movements = add_columns[0].text_input(
                "Movement types (comma-separated)", placeholder="squat"
            )
            new_role = add_columns[1].selectbox(
                "Exercise role", ["", *unique_values(exercises, "exercise_role")]
            )
            new_muscles = add_columns[2].text_input(
                "Muscle focus (comma-separated)", placeholder="quads, glutes"
            )

            add_columns = st.columns(3)
            new_equipment = add_columns[0].text_input(
                "Equipment (comma-separated)", placeholder="kettlebells"
            )
            new_load_type = add_columns[1].selectbox(
                "Load type", ["", *unique_values(exercises, "load_type")]
            )
            new_difficulty = add_columns[2].selectbox(
                "Difficulty", ["", *unique_values(exercises, "difficulty")]
            )

            add_columns = st.columns(3)
            new_template_slots = add_columns[0].text_input(
                "Template slots (comma-separated)", placeholder="squat_primary"
            )
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


page = st.sidebar.radio("Page", ["Generate Workout", "Exercise Library"])

if page == "Generate Workout":
    render_workout_generator_page()
else:
    render_exercise_library_page()
