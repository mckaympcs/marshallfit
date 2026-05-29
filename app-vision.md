# Marshall Fit — App Vision

## Product Summary

Marshall Fit is a private home-gym workout generator. The app lets a user request a workout type, such as “give me a chest day,” and returns a complete workout assembled from a structured exercise library that only uses equipment available in the Marshall Fit gym.

The core experience is simple:

1. User selects a workout day type.
2. User selects workout mode: weighted or bodyweight/youth-safe.
3. App generates a randomized workout using fixed structural templates.
4. Each exercise includes prescribed sets/reps and a reusable instructional diagram.
5. User can regenerate the workout or save/export it.

## Primary Goal

Build a reliable workout-generation engine first, then add a UI later. The engine should be importable and data-driven so the app can grow from a command-line Python tool into a mobile or web app without rewriting the workout logic.

## Target Users

### Primary User

An adult user training in the Marshall Fit home gym who wants fast, varied workouts using the available equipment.

### Secondary User

Youth athletes around ages 12–13 who need bodyweight or youth-safe workouts that avoid barbell compounds and heavy pressing.

## Core Product Promise

Marshall Fit creates workouts that are:

- Randomized enough to feel fresh.
- Structured enough to follow sound training logic.
- Constrained to the actual equipment in the gym.
- Safe enough to support a separate bodyweight/youth mode.
- Visual enough that every exercise has a reusable instructional diagram.

## MVP Scope

The first version should be a Python CLI application, not a full mobile app. The CLI should generate workouts from JSON data files and output a readable Markdown or HTML workout file.

The MVP should include:

- Equipment catalog converted to `equipment.json`.
- Exercise library in `exercises.json`.
- Workout templates in `templates.json`.
- Workout generator engine in `generator.py`.
- CLI entry point in `cli.py`.
- Output folder for generated workouts.
- Diagram references for each exercise, even if diagrams are added later.

## Future App Direction

After the Python generator is working, the project can evolve into an app with:

- Exercise library browsing.
- Workout generation UI.
- Saved workout history.
- Regenerate/swap exercise actions.
- Diagram gallery.
- Progress tracking.
- User profiles for adult/youth modes.
- Admin editing interface for exercises and templates.

## Recommended Technology Path

### Phase 1 — Local Engine

- Python
- JSON storage
- CLI workflow
- Markdown or HTML output

### Phase 2 — App Interface

Potential options:

- React Native / Expo for mobile.
- Next.js for web.
- Supabase or SQLite/Postgres for persistence.
- Static image storage for diagrams.

## Guiding Principles

1. Do not invent unavailable equipment.
2. Keep templates data-driven.
3. Keep exercise selection randomized but constrained.
4. Keep youth/bodyweight mode conservative.
5. Generate diagrams once and reuse them.
6. Build in review checkpoints, especially before finalizing the exercise library.
