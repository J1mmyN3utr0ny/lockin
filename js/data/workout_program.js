// workout_program.js — LockIn is connected to Gymmy (the user's own Android gym app).
// The six workouts below are recreated 1:1 from Gymmy's built-in workouts
// (WorkoutTemplates.kt + assets/exercises.json in the gymmy repo): same names,
// same exercises, same order, proper exercise names from Gymmy's library.
// Gymmy is the source of truth — if a workout changes there, mirror it here.

export const gymmyApp = {
  name: "Gymmy",
  package: "com.yaniv.gymmy",
  // Launches the installed Gymmy app from the PWA on Android.
  intentUrl: "intent:#Intent;action=android.intent.action.MAIN;category=android.intent.category.LAUNCHER;package=com.yaniv.gymmy;end"
};

export const philosophy = {
  title: "Connected to Gymmy",
  points: [
    "These are your Gymmy workouts, recreated exactly — same six names, same exercises, same order.",
    "Gymmy stays the source of truth: build, edit and browse exercises there; LockIn only schedules and tracks the habit.",
    "Sets/reps are yours to set (like in Gymmy): ~3-4 sets on big barbell lifts, 2-3 on isolations.",
    "Progressive overload is still the whole game: beat last session by a rep or a small load, every time.",
    "Evening sessions (~20:00) — fuel with the 19:00 snack, then dinner is your post-workout meal."
  ]
};

// The core fix for "I only feel my forearms." (Coaching overlay — doesn't change the workouts.)
export const forearmFix = {
  title: "Stop the forearm takeover",
  why: "Your forearms fail/pump first because they carry the grip on every pull and curl, so the target muscle never gets fully loaded.",
  rules: [
    "Use lifting straps on ALL back/pull work (pullups, rows, pulldowns, RDLs, deadlifts). The lats/hamstrings should quit first — not your grip.",
    "On curls, cue 'drive the elbow, relax the hand'. Think of your hand as a hook, not a gripper.",
    "On presses, grip only as hard as needed to control the bar — drive with the chest/shoulders.",
    "Cut direct forearm/grip work to near zero this block — they're already ahead."
  ]
};

// Each exercise mirrors a Gymmy library entry: id + name are Gymmy's own
// (assets/exercises.json), target = its primary muscle, equip = its equipment.
// `straps` is LockIn's forearm-fix overlay, not Gymmy data.
export const days = [
  {
    id: "push", name: "Push", focus: "Chest · shoulders · triceps",
    exercises: [
      { id: "Barbell_Bench_Press_-_Medium_Grip", name: "Barbell Bench Press - Medium Grip", target: "Chest", equip: "barbell" },
      { id: "Barbell_Incline_Bench_Press_-_Medium_Grip", name: "Barbell Incline Bench Press - Medium Grip", target: "Chest", equip: "barbell" },
      { id: "Barbell_Shoulder_Press", name: "Barbell Shoulder Press", target: "Shoulders", equip: "barbell" },
      { id: "Side_Lateral_Raise", name: "Side Lateral Raise", target: "Shoulders", equip: "dumbbell" },
      { id: "Triceps_Pushdown", name: "Triceps Pushdown", target: "Triceps", equip: "cable" },
      { id: "Dips_-_Triceps_Version", name: "Dips - Triceps Version", target: "Triceps", equip: "bodyweight" }
    ]
  },
  {
    id: "pull", name: "Pull", focus: "Back · biceps",
    exercises: [
      { id: "Pullups", name: "Pullups", target: "Lats", equip: "bodyweight", straps: true },
      { id: "Bent_Over_Barbell_Row", name: "Bent Over Barbell Row", target: "Mid-back", equip: "barbell", straps: true },
      { id: "Wide-Grip_Lat_Pulldown", name: "Wide-Grip Lat Pulldown", target: "Lats", equip: "cable", straps: true },
      { id: "Face_Pull", name: "Face Pull", target: "Rear delts", equip: "cable" },
      { id: "Barbell_Curl", name: "Barbell Curl", target: "Biceps", equip: "barbell" },
      { id: "Hammer_Curls", name: "Hammer Curls", target: "Biceps", equip: "dumbbell" }
    ]
  },
  {
    id: "lower", name: "Lower", focus: "Quads · hamstrings · calves",
    exercises: [
      { id: "Barbell_Squat", name: "Barbell Squat", target: "Quads", equip: "barbell" },
      { id: "Romanian_Deadlift", name: "Romanian Deadlift", target: "Hamstrings", equip: "barbell", straps: true },
      { id: "Leg_Press", name: "Leg Press", target: "Quads", equip: "machine" },
      { id: "Lying_Leg_Curls", name: "Lying Leg Curls", target: "Hamstrings", equip: "machine" },
      { id: "Leg_Extensions", name: "Leg Extensions", target: "Quads", equip: "machine" },
      { id: "Standing_Calf_Raises", name: "Standing Calf Raises", target: "Calves", equip: "machine" }
    ]
  },
  {
    id: "upper", name: "Upper", focus: "Chest · back · shoulders · arms",
    exercises: [
      { id: "Barbell_Bench_Press_-_Medium_Grip", name: "Barbell Bench Press - Medium Grip", target: "Chest", equip: "barbell" },
      { id: "Bent_Over_Barbell_Row", name: "Bent Over Barbell Row", target: "Mid-back", equip: "barbell", straps: true },
      { id: "Barbell_Shoulder_Press", name: "Barbell Shoulder Press", target: "Shoulders", equip: "barbell" },
      { id: "Wide-Grip_Lat_Pulldown", name: "Wide-Grip Lat Pulldown", target: "Lats", equip: "cable", straps: true },
      { id: "Barbell_Curl", name: "Barbell Curl", target: "Biceps", equip: "barbell" },
      { id: "Triceps_Pushdown", name: "Triceps Pushdown", target: "Triceps", equip: "cable" }
    ]
  },
  {
    id: "abs", name: "Abs", focus: "Core",
    exercises: [
      { id: "Hanging_Leg_Raise", name: "Hanging Leg Raise", target: "Abs", equip: "bodyweight" },
      { id: "Crunches", name: "Crunches", target: "Abs", equip: "bodyweight" },
      { id: "Cable_Crunch", name: "Cable Crunch", target: "Abs", equip: "cable" },
      { id: "Plank", name: "Plank", target: "Abs", equip: "bodyweight" },
      { id: "Russian_Twist", name: "Russian Twist", target: "Abs", equip: "bodyweight" }
    ]
  },
  {
    id: "full", name: "Full body", focus: "Whole-body compound session",
    exercises: [
      { id: "Barbell_Squat", name: "Barbell Squat", target: "Quads", equip: "barbell" },
      { id: "Barbell_Bench_Press_-_Medium_Grip", name: "Barbell Bench Press - Medium Grip", target: "Chest", equip: "barbell" },
      { id: "Barbell_Deadlift", name: "Barbell Deadlift", target: "Lower back", equip: "barbell", straps: true },
      { id: "Wide-Grip_Lat_Pulldown", name: "Wide-Grip Lat Pulldown", target: "Lats", equip: "cable", straps: true },
      { id: "Barbell_Shoulder_Press", name: "Barbell Shoulder Press", target: "Shoulders", equip: "barbell" }
    ]
  }
];

export function dayById(id) { return days.find((d) => d.id === id); }

// Which workout on which weekday (0=Sun..6=Sat). Gym is the ~20:00 evening slot.
// Sun Push, Mon Pull, Tue Lower, Wed Upper, Thu Abs (light), Fri Full body
// (optional, midday — gyms close early before Shabbat), Sat rest.
export const weekPlan = { 0: "push", 1: "pull", 2: "lower", 3: "upper", 4: "abs", 5: "full", 6: null };
