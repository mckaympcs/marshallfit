# Marshall Fit — Design System

## 1. Visual Direction

The app should feel clean, instructional, and sports-science oriented. The visual language should match a professional fitness certification manual or anatomical exercise poster.

Primary style description:

> Professional anatomical fitness infographic, white background, clean vector illustration, highly detailed grayscale human anatomy, target muscles highlighted in red/orange, instructional callouts with blue leader lines, exercise shown in START and BOTTOM or START and FINISH position panels, educational gym poster style, sports science textbook quality, crisp black outlines, realistic proportions, labeled movement arrows, modern physical therapy and strength training manual aesthetic, minimal distractions, high resolution.

## 2. Diagram Style

### Core Diagram Attributes

- White background.
- Clean anatomical line-art.
- Grayscale human figure.
- Primary muscles highlighted in red/orange.
- Optional secondary muscles highlighted in lighter orange/yellow.
- Blue arrows for movement direction or bar path.
- Blue leader lines for form callouts.
- Bold panel labels such as `START`, `BOTTOM`, `FINISH`, or `LOCKOUT`.
- Minimal clutter.
- Realistic gym equipment proportions.
- Consistent camera angle per exercise type.

## 3. Reusable Diagram Prompt Template

Use this as the master image prompt for future exercise diagrams:

```text
Professional anatomical fitness infographic, white background, clean vector illustration, highly detailed grayscale human anatomy, target muscles highlighted in red/orange, instructional callouts with blue leader lines, exercise shown in START and FINISH position panels, educational gym poster style, sports science textbook quality, crisp black outlines, realistic proportions, labeled movement arrows, modern physical therapy and strength training manual aesthetic, minimal distractions, high resolution.

Exercise: [EXERCISE NAME]
View angle: [SIDE VIEW / FRONT VIEW / 3/4 VIEW]
Equipment: [EQUIPMENT]
Show: [START POSITION] and [END/BOTTOM/FINISH POSITION]
Highlight primary muscles: [PRIMARY MUSCLES]
Include arrows showing: [BAR PATH / LIMB PATH / BODY PATH]
```

## 4. Example Diagram Prompts

### Flat Barbell Bench Press

```text
Professional anatomical fitness infographic, white background, clean vector illustration, highly detailed grayscale human anatomy, chest highlighted in red/orange, blue instructional callouts and bar path arrow, side view of a person doing a flat barbell bench press, two panels labeled START and BOTTOM, educational gym poster style, sports science textbook quality, realistic proportions, modern strength training manual aesthetic.
```

### Back Squat

```text
Professional anatomical fitness infographic, white background, clean vector illustration, highly detailed grayscale human anatomy, quadriceps and glutes highlighted in red/orange, blue instructional callouts and vertical bar path arrow, side view of a person doing a barbell back squat, two panels labeled START and BOTTOM, educational gym poster style, sports science textbook quality, realistic proportions, modern strength training manual aesthetic.
```

### Lat Pulldown

```text
Professional anatomical fitness infographic, white background, clean vector illustration, highly detailed grayscale human anatomy, lats highlighted in red/orange, blue instructional callouts and downward cable path arrow, front or slight 3/4 view of a person doing a lat pulldown, two panels labeled START and BOTTOM, educational gym poster style, sports science textbook quality, realistic proportions, modern strength training manual aesthetic.
```

## 5. App UI Style

### Overall Feel

- Clean.
- Minimal.
- Fitness-focused.
- Premium home-gym aesthetic.
- Easy to read quickly before or during a workout.

### Suggested Color Palette

```text
Background: White / off-white
Primary text: Charcoal / near black
Secondary text: Medium gray
Accent blue: Used for buttons, callouts, arrows
Muscle highlight red/orange: Used only in diagrams or muscle tags
Success/active: Green, used sparingly
Warning: Amber, used sparingly
```

### Typography Direction

Use bold, simple sans-serif headings and highly readable body text. Avoid decorative fonts. Exercise names should be large and scannable.

### Layout Direction

Workout screen should prioritize:

1. Day type and mode.
2. Exercise order.
3. Sets/reps.
4. Diagram.
5. Simple instructions.
6. Regenerate/swap actions.

## 6. Exercise Detail Screen Concept

Each exercise detail page should include:

- Exercise name.
- Primary muscle tags.
- Secondary muscle tags.
- Equipment required.
- Instructional diagram.
- Setup instructions.
- Execution instructions.
- Common mistakes.
- Youth-safe indicator if applicable.

## 7. Diagram File Naming

Use stable, lowercase, snake_case file names that match exercise IDs:

```text
diagrams/flat_barbell_bench_press.png
diagrams/incline_db_press.png
diagrams/lat_pulldown.png
diagrams/bodyweight_split_squat.png
```

## 8. Consistency Rules

- Use the same visual style for every diagram.
- Use one diagram per exercise and reuse it.
- Do not regenerate diagrams every time a workout is generated.
- Do not mix cartoon, photorealistic, comic, or painterly styles.
- Keep labels consistent: `START`, `BOTTOM`, `FINISH`, `LOCKOUT`.
- Keep arrow color and callout style consistent.
