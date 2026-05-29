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
