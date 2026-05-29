# Marshall Fit — Beginner-Friendly Build Plan

This plan turns the existing product notes into a small, safe first build. The goal is to get a local Python command-line app working before building a web or mobile interface.

## What we are building first

Marshall Fit should start as a data-driven workout generator. That means most workout rules live in JSON files, while Python code loads those files, filters exercises, randomly chooses a workout, and writes a readable Markdown file.

The first local version should be able to:

1. Read the available gym equipment from `data/equipment.json`.
2. Read approved exercises from `data/exercises.json`.
3. Read workout-day templates from `data/templates.json`.
4. Generate a workout for a selected day and mode.
5. Save the result as a Markdown file in `output/`.

## 1. Recommended folder/file structure

Use this structure for Phase 1:

```text
marshallfit/
  README.md
  app-vision.md
  features.md
  design-system.md
  equipment-catalog.md

  docs/
    build-plan.md

  data/
    equipment.json
    exercises.json
    templates.json

  diagrams/
    .gitkeep

  output/
    .gitkeep

  marshallfit/
    __init__.py
    generator.py
    loaders.py
    validators.py
    renderer.py

  tests/
    test_generator.py
    test_validators.py

  cli.py
```

### What each file/folder does

| Path | Purpose |
|---|---|
| `data/equipment.json` | The source of truth for what equipment exists in the gym. |
| `data/exercises.json` | The exercise library. Each exercise lists muscles, equipment, mode, safety flags, and diagram path. |
| `data/templates.json` | Workout structures such as chest/triceps, back/biceps, and legs. |
| `diagrams/` | Reusable exercise diagram images. Phase 1 can use placeholder paths only. |
| `output/` | Generated workout files. These should usually not be hand-edited. |
| `marshallfit/generator.py` | The main workout-selection logic. |
| `marshallfit/loaders.py` | Helper functions that load JSON files. |
| `marshallfit/validators.py` | Checks that exercises only use available equipment and match the expected schema. |
| `marshallfit/renderer.py` | Turns a generated workout object into Markdown. |
| `cli.py` | The beginner-friendly command you run from the terminal. |
| `tests/` | Small automated checks to make sure the app keeps working as it grows. |

This is a little more organized than putting everything in `generator.py`. It will be easier for Codex to work on one small piece at a time.

## 2. First 10 small tasks to ask Codex to complete

Ask Codex for these in order. Each task is intentionally small so you can review the app as it grows.

### Task 1 — Create the project skeleton

Ask Codex to create the folders and empty starter files:

- `data/`
- `diagrams/`
- `output/`
- `marshallfit/`
- `tests/`
- `cli.py`

Also ask for `.gitkeep` files in `diagrams/` and `output/` so the empty folders stay in Git.

### Task 2 — Create `data/equipment.json`

Ask Codex to convert `equipment-catalog.md` into structured JSON using only the equipment IDs listed in `features.md`.

Important review checkpoint: confirm that the equipment list does **not** include jammer arms.

### Task 3 — Add JSON loading helpers

Ask Codex to implement `marshallfit/loaders.py` with simple functions like:

- `load_equipment()`
- `load_exercises()`
- `load_templates()`

These should read JSON files and return Python dictionaries/lists.

### Task 4 — Draft a small starter exercise library

Ask Codex to create the first version of `data/exercises.json` with about 20–30 exercises, not the full final library.

The starter library should include enough exercises for:

- Chest/triceps weighted workouts.
- Back/biceps weighted workouts.
- Legs weighted workouts.
- At least a few bodyweight/youth-safe options.

Pause after this task and review the exercise list carefully.

### Task 5 — Add validation checks

Ask Codex to implement `marshallfit/validators.py` and tests that confirm:

- Every exercise only uses equipment from `equipment.json`.
- Every exercise has a diagram path.
- Every exercise uses an allowed `movement_pattern`.
- Every exercise uses an allowed `loadable` value.
- Bodyweight/youth-safe rules are not accidentally violated.

This protects the app from silently generating impossible workouts.

### Task 6 — Create `data/templates.json`

Ask Codex to create templates for:

- `chest_triceps`
- `back_biceps`
- `legs`

Each template should be an ordered list of slots, with sets/reps stored in the JSON instead of hard-coded in Python.

### Task 7 — Build the first generator engine

Ask Codex to implement `marshallfit/generator.py` so it can:

1. Pick a template.
2. Filter exercises by movement pattern.
3. Filter by workout mode.
4. Filter by compound/finisher/category rules.
5. Exclude unavailable equipment.
6. Avoid duplicate exercises in the same workout.
7. Randomly choose one valid exercise per slot.
8. Return a helpful error if no exercise matches.

Keep the output as a Python object first. Do not worry about pretty formatting yet.

### Task 8 — Add Markdown rendering

Ask Codex to implement `marshallfit/renderer.py` so a generated workout becomes Markdown with:

- Workout day.
- Mode.
- Date/time generated.
- Exercise order.
- Sets/reps.
- Diagram path.
- Notes, if available.

### Task 9 — Build the CLI command

Ask Codex to implement `cli.py` so you can run commands like:

```bash
python cli.py --day chest_triceps --mode weighted
python cli.py --day legs --mode bodyweight
python cli.py --day back_biceps --mode weighted --seed 123
```

The CLI should save a Markdown file into `output/` and print the saved file path.

### Task 10 — Add basic tests and sample runs

Ask Codex to add tests for the generator and validators, then run sample commands for each starting template.

Minimum checks:

```bash
python -m pytest
python cli.py --day chest_triceps --mode weighted --seed 1
python cli.py --day back_biceps --mode weighted --seed 1
python cli.py --day legs --mode bodyweight --seed 1
```

## 3. Missing decisions and questions before coding

Answering these before implementation will reduce rework.

### Workout rules

1. Should the default prescription stay `3 sets of 6–10 reps` for every slot unless a template overrides it?
2. Should warmups be included in Phase 1, or should Phase 1 only generate working sets?
3. Should rest periods be included now, or added later?
4. Should the first version include only the three documented day types: chest/triceps, back/biceps, and legs?
5. Should a generated workout ever repeat a movement pattern if the template asks for it, as long as it does not repeat the exact exercise?

### Youth/bodyweight mode

1. Is bodyweight mode always the same thing as youth-safe mode?
2. Are light cable exercises allowed for youth mode, or should youth mode be strictly bodyweight only?
3. Are dips and pull-ups allowed for youth mode if marked `youth_safe`, or should assisted versions be preferred?
4. Should youth mode avoid all loaded spinal compression, including goblet squats and loaded carries?

### Exercise library

1. How large should the reviewed Phase 1 exercise library be: about 25 exercises, about 50 exercises, or larger?
2. Do you want setup, execution, and common-mistake instructions in Phase 1, or only names, equipment, muscles, and diagram paths?
3. Should each exercise have a stable difficulty level such as beginner, intermediate, or advanced?
4. Should each exercise include substitutions in the data, or should substitutions come later?

### Output format

1. Is Markdown enough for Phase 1, or do you also want HTML output immediately?
2. Should generated files include the random seed so the same workout can be reproduced?
3. Should generated output files be kept in Git, or should `output/` be ignored once the app exists?

### Diagrams and design

1. Should diagrams be AI-generated PNG images, hand-made SVG/vector files, or placeholders at first?
2. Should Phase 1 block on real diagrams, or is it acceptable to store diagram paths before images exist?
3. Should diagram labels use only `START`, `BOTTOM`, `FINISH`, and `LOCKOUT` as the design system suggests?

### Technical setup

1. Which Python version should the project target?
2. Should the project use only the Python standard library at first, or is it okay to add packages like `pytest` and `jsonschema`?
3. Should Codex create a `requirements.txt` or a modern `pyproject.toml`?

## 4. Suggested Phase 1 MVP that can run locally

Phase 1 should be intentionally simple. A successful MVP is a terminal command that creates useful workout files from reviewed data.

### Phase 1 MVP scope

Build a Python CLI app with:

- `data/equipment.json` based on the home gym catalog.
- `data/exercises.json` with a reviewed starter exercise library.
- `data/templates.json` with chest/triceps, back/biceps, and legs templates.
- A generator that supports `weighted` and `bodyweight` modes.
- Duplicate exercise prevention within a workout.
- Equipment validation so unsupported exercises cannot slip in.
- Markdown output saved to `output/`.
- Diagram paths included in output, even if diagram image files are placeholders.
- Basic tests for data validation and workout generation.

### Example local workflow

From the project root, the user should be able to run:

```bash
python cli.py --day chest_triceps --mode weighted
```

And receive a generated file such as:

```text
output/chest_triceps_weighted_2026-05-29_1530.md
```

The file should look roughly like:

```markdown
# Chest + Triceps — Weighted

Generated: 2026-05-29 15:30

1. Flat Dumbbell Press — 3 × 6–10
   Diagram: diagrams/flat_db_press.png

2. Incline Smith Press — 3 × 6–10
   Diagram: diagrams/incline_smith_press.png
```

### What Phase 1 should not include yet

To keep the first version beginner-friendly, do not include these yet:

- Mobile app UI.
- Web app UI.
- User accounts.
- Saved workout history database.
- Progress tracking.
- Admin editing screens.
- Mass diagram generation.
- Complex periodization or multi-week plans.

### Phase 1 definition of done

Phase 1 is done when:

1. All JSON data files load without errors.
2. Tests confirm exercises only use available gym equipment.
3. Each documented day type can generate a weighted workout.
4. Bodyweight mode can generate at least one safe workout, or fails with a clear message explaining what data is missing.
5. The CLI writes a Markdown file to `output/`.
6. A beginner can run the app locally with one documented command.

## Recommended next step

Start with Task 1 only. After the skeleton exists, move to Task 2 and review `equipment.json` before adding exercises. The most important early habit is to review the data before building more code on top of it.
