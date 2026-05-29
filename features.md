# Marshall Fit — Features & Functional Requirements

## 1. Project Structure

Recommended starter structure:

```text
/data
  exercises.json
  equipment.json
  templates.json
/diagrams
/output
generator.py
cli.py
```

## 2. Data Files

### 2.1 `equipment.json`

Purpose: structured version of the Marshall Fit equipment catalog.

The catalog should include only actual equipment available in the gym. The app should use this file as the constraint layer for validating exercises.

Recommended equipment IDs:

```text
power_rack
integrated_dual_cable_system
multi_grip_pull_up_bar
rack_mounted_dip_station
bts_smith_attachment
landmine_attachment
pritchett_pad
rogue_leg_roller
spotter_arms_j_cups
bulletproof_isolator
dumbbells
barbells
ez_curl_bar
bumper_plates
iron_plates
kettlebells
med_slam_ball
adjustable_fid_bench
atg_platform
resistance_bands
ab_roller
suspension_straps
mag_grip_handles
tricep_rope
v_bar
cable_attachments
```

Important catalog rules:

- Integrated cable system supports 150 lb per side or up to 300 lb when linked.
- No jammer arms are available.
- Bulletproof Isolator includes the leg developer roller pad.
- Exercise library must not include exercises requiring equipment outside the catalog.

### 2.2 `exercises.json`

Purpose: complete exercise library used by the generator.

Each exercise object should follow this schema:

```json
{
  "id": "incline_db_press",
  "name": "Incline Dumbbell Press",
  "movement_pattern": "vertical_push",
  "primary_muscles": ["chest_upper", "shoulders"],
  "secondary_muscles": ["triceps"],
  "equipment_required": ["dumbbells", "adjustable_fid_bench"],
  "category": "push",
  "is_compound": true,
  "is_finisher": false,
  "loadable": "weighted",
  "youth_safe": true,
  "diagram": "diagrams/incline_db_press.png"
}
```

Allowed `movement_pattern` values:

```text
horizontal_push
vertical_push
horizontal_pull
vertical_pull
compound_leg_push
compound_hamstring
accessory_quad
isolated_hamstring
iso_finisher
```

Allowed `loadable` values:

```text
weighted
bodyweight
both
```

Recommended approach for `both` movements:

Use separate entries when the weighted and bodyweight versions differ materially. For example:

```text
bulgarian_split_squat_db
bulgarian_split_squat_bodyweight
```

This keeps youth/bodyweight filtering simple and avoids ambiguity.

### 2.3 `templates.json`

Purpose: define workout day structures as ordered slots.

Templates should be editable without changing Python code.

Each slot should include:

- Slot name.
- Movement pattern.
- Whether compound is required.
- Whether finisher is required.
- Optional muscle/category constraints.
- Sets and reps prescription.
- Duplicate prevention rule.

Default prescription:

```text
3 sets of 6–10 reps
```

Make this configurable globally and overrideable per slot.

## 3. Workout Templates

### 3.1 `chest_triceps`

1. Horizontal push compound.
2. Horizontal push compound, different exercise.
3. Vertical/incline push.
4. Vertical/incline push, different exercise.
5. Tricep isolation.
6. Tricep isolation, different exercise.
7. Chest isolation finisher.

### 3.2 `back_biceps`

1. Horizontal pull.
2. Horizontal pull, different exercise.
3. Vertical pull.
4. Lat-focused exercise.
5. Bicep isolation.
6. Bicep isolation, different exercise.

### 3.3 `legs`

1. Compound push leg.
2. Compound hamstring.
3. Accessory quad.
4. Isolated hamstring.

## 4. Generator Engine

### 4.1 Inputs

The generator should accept:

```text
template_name
mode
random_seed optional
```

Allowed modes:

```text
weighted
bodyweight
```

Example CLI command:

```bash
python cli.py --day chest_triceps --mode weighted
```

### 4.2 Selection Rules

For each template slot, the generator should:

1. Load the template.
2. Filter exercises by movement pattern.
3. Filter by mode.
4. Filter by compound/finisher/category requirements.
5. Filter by equipment availability.
6. Exclude exercises already selected in the session.
7. Randomly select one remaining exercise.
8. Return a clear error if no exercise satisfies the slot.

### 4.3 Weighted Mode

Weighted mode may include weighted, bodyweight, or both movements if they fit the template. It should still respect available equipment.

### 4.4 Bodyweight / Youth Mode

Bodyweight mode must be conservative.

Rules:

- Only include exercises where `youth_safe` is `true`.
- Only include exercises where `loadable` is `bodyweight` or `both`.
- Exclude barbell back squats, deadlifts, and heavy pressing.
- Favor push-ups, pull-ups, chin-ups, dips, bodyweight lunges, bodyweight split squats, suspension rows, light cable work, and core movements.

## 5. Output

Generated workout output should include:

- Workout day type.
- Mode.
- Date/time generated.
- Exercise list.
- Sets/reps.
- Diagram path.
- Optional instructions or notes.

Recommended first output format: Markdown.

Example output section:

```markdown
## Chest + Triceps — Weighted

1. Flat Dumbbell Press — 3 × 6–10  
   Diagram: diagrams/flat_db_press.png

2. Smith Bench Press — 3 × 6–10  
   Diagram: diagrams/smith_bench_press.png
```

## 6. Exercise Diagrams

Each exercise should have one reusable diagram stored in `/diagrams` and referenced by the exercise object.

Diagram rules:

- Generate once.
- Reuse across workouts.
- Show start and end/bottom positions when helpful.
- Highlight primary muscle.
- Include movement arrows.
- Keep visual style consistent across exercises.

Do not mass-generate all diagrams until the exercise library is reviewed and approved.

## 7. Build Order for Codex

### Step 1 — Create project skeleton

Create folders and placeholder files.

### Step 2 — Parse equipment catalog

Create `equipment.json` manually or with a parser.

### Step 3 — Draft exercise library

Build `exercises.json` using only catalog-supported exercises.

Pause for user review before continuing.

### Step 4 — Create workout templates

Build `templates.json` for chest/triceps, back/biceps, and legs.

### Step 5 — Build generator engine

Implement filtering, randomization, duplicate prevention, and output object.

### Step 6 — Build CLI

Allow commands like:

```bash
python cli.py --day chest_triceps --mode weighted
python cli.py --day legs --mode bodyweight
```

### Step 7 — Generate output files

Write Markdown or HTML workouts to `/output`.

### Step 8 — Add diagrams

Confirm generation method, generate diagrams, then wire them into output.

## 8. Open Decisions

- Confirm default rep scheme: currently assumed 3×6–10.
- Confirm whether bodyweight mode is strictly youth-safe or simply no-barbell.
- Confirm whether diagrams should be generated by AI image generation or created as static SVG/vector art.
- Confirm additional day types beyond chest/triceps, back/biceps, and legs.
