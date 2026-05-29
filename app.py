"""Simple Streamlit interface for the Marshall Fit workout generator.

Run this app locally with:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from generator import generate_workout, load_templates


# The app file lives in the project root, so this path lets us check whether a
# diagram image exists before asking Streamlit to display it.
BASE_DIR = Path(__file__).resolve().parent
EXERCISES_PER_COLUMN = 3


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
            border-radius: 18px;
            color: #475569;
            display: flex;
            flex-direction: column;
            font-size: 0.82rem;
            font-weight: 700;
            gap: 0.35rem;
            justify-content: center;
            min-height: 132px;
            padding: 1rem;
            text-align: center;
            text-transform: uppercase;
        }

        .diagram-placeholder span {
            display: block;
            font-size: 1.75rem;
            line-height: 1;
        }

        .exercise-title {
            font-size: 1.18rem;
            font-weight: 800;
            line-height: 1.18;
            margin: 0 0 0.1rem;
        }

        .exercise-category {
            color: #64748b;
            font-size: 0.86rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
        }

        .sets-reps-pill {
            background: #111827;
            border-radius: 999px;
            color: #ffffff;
            display: inline-block;
            font-size: 0.94rem;
            font-weight: 800;
            padding: 0.48rem 0.85rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Marshall Fit Workout Generator")
st.write(
    "Generate a six-exercise workout with diagram-first cards, quick movement "
    "categories, and set/rep targets matched to the exercise type."
)


# Load the workout day templates from the finished JSON data file. The dropdown
# shows friendly names while the app keeps the matching template id behind the
# scenes for the generator.
templates = load_templates()
template_names = [template["name"] for template in templates]
selected_template_name = st.selectbox("Workout day / template", template_names)
selected_template = next(
    template for template in templates if template["name"] == selected_template_name
)


# Let the user choose whether they want a weighted workout or a bodyweight-first
# workout. The lowercase value is passed directly into generator.py.
mode = st.radio("Mode", ["weighted", "bodyweight"], horizontal=True)


# The button prevents a new random workout from appearing on every widget change.
# A workout is only created when the user explicitly asks for one.
if st.button("Generate Workout"):
    workout = generate_workout(selected_template["id"], mode)

    st.subheader(workout["template_name"])
    st.caption(f"Mode: {workout['mode'].title()}")

    if workout.get("template_description"):
        st.write(workout["template_description"])

    st.markdown("---")

    # Landscape browsers get two columns of three exercises. Streamlit stacks
    # columns on narrow screens, so the same structure remains mobile-friendly.
    exercise_columns = st.columns(2, gap="large")
    column_groups = [
        workout["exercises"][:EXERCISES_PER_COLUMN],
        workout["exercises"][EXERCISES_PER_COLUMN:],
    ]

    for column_index, column_exercises in enumerate(column_groups):
        with exercise_columns[column_index]:
            for offset, exercise in enumerate(column_exercises, start=1):
                number = column_index * EXERCISES_PER_COLUMN + offset

                with st.container(border=True):
                    diagram_column, details_column = st.columns(
                        [1, 2.25], gap="medium", vertical_alignment="center"
                    )

                    with diagram_column:
                        diagram_path = exercise["diagram_path"]
                        diagram_file = BASE_DIR / diagram_path

                        # If the diagram file has already been added locally,
                        # show it. Otherwise, render a visual placeholder in the
                        # same spot so the card layout is ready for diagrams.
                        if diagram_file.exists():
                            st.image(str(diagram_file), caption="Exercise diagram")
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

                    with details_column:
                        st.markdown(
                            (
                                '<div class="exercise-title">'
                                f'{number}. {exercise["name"]}'
                                '</div>'
                            ),
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            (
                                '<div class="exercise-category">'
                                f'{exercise["category"]}'
                                '</div>'
                            ),
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            "<div class=\"sets-reps-pill\">"
                            f"{exercise['sets']} sets × {exercise['reps']} reps"
                            "</div>",
                            unsafe_allow_html=True,
                        )
