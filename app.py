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


# Streamlit reruns this script from top to bottom whenever the user changes a
# widget. Keeping the page setup near the top makes the app easy to scan.
st.set_page_config(page_title="Marshall Fit Workout Generator", page_icon="💪")
st.title("Marshall Fit Workout Generator")


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

    # Display each generated exercise with beginner-friendly labels so the user
    # can understand why it was selected and what set/rep target to use.
    for number, exercise in enumerate(workout["exercises"], start=1):
        st.markdown(f"### {number}. {exercise['name']}")
        st.write(f"**Template slot:** {exercise['slot_name']}")
        st.write(f"**Movement pattern:** {exercise['movement_pattern']}")
        st.write(
            "**Primary muscles:** "
            + (", ".join(exercise["primary_muscles"]) or "Not listed")
        )
        st.write(
            "**Secondary muscles:** "
            + (", ".join(exercise["secondary_muscles"]) or "Not listed")
        )
        st.write(f"**Sets/Reps:** {exercise['sets']} sets of {exercise['reps']} reps")

        diagram_path = exercise["diagram_path"]
        diagram_file = BASE_DIR / diagram_path

        # If the diagram file has already been added locally, show the image.
        # Otherwise, show the intended path as placeholder text for now.
        if diagram_file.exists():
            st.image(str(diagram_file), caption=diagram_path)
        else:
            st.info(f"Diagram placeholder: {diagram_path}")
