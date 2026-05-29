# Marshall Fit Build Plan

Beginner note: this file captures the high-level build order for the project. It keeps the first step focused on scaffolding instead of building the full app too early.

## Step 1 — Initial Scaffold

- Create the main project folders: `data/`, `output/`, `diagrams/`, `tests/`, and `docs/`.
- Add starter JSON files for equipment, exercises, and templates.
- Add `generator.py` as the future home of workout-generation logic.
- Add `cli.py` as the command-line entry point.
- Keep the CLI simple for now: running `python cli.py` should print the project name.

## Later Steps

Do not implement these yet during the scaffold step:

1. Fill in the equipment catalog.
2. Draft the exercise library.
3. Create workout templates.
4. Implement filtering and random workout selection.
5. Export generated workouts to the `output/` folder.
6. Add reusable diagrams after the exercise library is reviewed.
