# Marshall Fit Workout Generator

Marshall Fit is a private home-gym workout generator. The first version is a simple Python project that creates workouts from JSON data files and now includes a local Streamlit web interface.

## Current Status

This repository contains the starter workout generator, completed JSON data files, and a first simple Streamlit user interface.

## Project Folders

- `data/` — JSON files for equipment, exercises, and workout templates.
- `diagrams/` — future home for reusable exercise diagram images.
- `docs/` — planning and project documentation.
- `output/` — future generated workout files, such as Markdown or HTML exports.
- `tests/` — future automated tests for the generator and CLI.

## Starter Files

- `app.py` — local Streamlit web interface for generating workouts.
- `cli.py` — beginner-friendly command-line entry point. Run it with `python cli.py`.
- `generator.py` — importable workout-generation engine used by the interface.
- `data/equipment.json` — equipment catalog data.
- `data/exercises.json` — exercise library data.
- `data/templates.json` — workout template data.

## Run the Streamlit Interface

Install Streamlit:

```bash
pip install streamlit
```

Start the local web app:

```bash
streamlit run app.py
```

Then use the page to choose a workout template, select weighted or bodyweight mode, and click **Generate Workout**.

## Try the Starter CLI

```bash
python cli.py
```

Expected output:

```text
Marshall Fit Workout Generator
```

## Today's Workout TV Display

Marshall Fit includes a display-only **Today's Workout** page for a 32-inch TV in portrait orientation. It is intended for showing the workout of the day only, so it does not include workout generation, editing, sharing, star, toolbar, or utility controls.

Open it locally after starting Streamlit:

```bash
streamlit run app.py
```

Then browse directly to:

```text
http://localhost:8501/today
```

For the best TV setup:

- Rotate the TV or display to portrait mode, ideally around a 9:16 aspect ratio.
- Open the `/today` page URL directly.
- Use browser full-screen mode, usually **F11**.
- Optionally use the page's **Enter Full Screen** button or press **F** if the browser allows page-triggered full-screen.
- If a workout is saved in the Scheduler for today's date, the TV page shows that workout. If not, it creates a deterministic date-based workout so the same workout appears for the same day.
