// workout_program.js — the 5-day split, mirrored 1:1 from the Gymmy app
// (the user's own Android gym app). The SAME workouts live in Gymmy as built-in
// templates named "Day A".."Day E" (WorkoutTemplates.kt); exercise ids + names +
// set/rep targets here match Gymmy's bundled library (assets/exercises.json)
// exactly. If the program changes, change BOTH places.
// Program goals: GROW chest, legs (weakest) and abs; START loaded oblique work;
// MAINTAIN biceps; keep grip demand low so forearms stop stealing every lift.

export const gymmyApp = {
  name: "Gymmy",
  package: "com.yaniv.gymmy",
  // Launches the installed Gymmy app from the PWA on Android.
  intentUrl: "intent:#Intent;action=android.intent.action.MAIN;category=android.intent.category.LAUNCHER;package=com.yaniv.gymmy;end"
};

export const philosophy = {
  title: "How this program is built for you",
  points: [
    "Legs are trained twice a week (Day B + Day D) because they're the biggest gap.",
    "Chest gets a heavy day and a second volume day (Day A + Day E).",
    "Abs are hit 3×/week; obliques get dedicated loaded work (new for you) on Day D.",
    "Biceps are maintained, not chased — one focused slot on Day C with a grip that spares forearms.",
    "Forearms are a growth FOCUS: direct work ends Day C + Day E, and a hand gripper covers the other days.",
    "Progressive overload is the whole game: beat last week's log by a rep or a small load, every session.",
    "Day F is an OPTIONAL Friday 6th: a light full-body pump for weeks that felt too easy — or swap it for a redo of any day you missed.",
    "The exact same workouts live in your Gymmy app as the Day A–F templates — Gymmy is where you log; LockIn watches and ticks the schedule."
  ]
};

// The core fix for "I only feel my forearms."
export const forearmFix = {
  title: "Stop the forearm takeover",
  why: "Your forearms fail/pump first because they carry the grip on every pull and curl, so the target muscle never gets fully loaded.",
  rules: [
    "Use lifting straps on ALL back/pull work (pulldowns, rows, RDLs). The lats/hamstrings should quit first — not your grip.",
    "Prefer machines & cables for chest (machine press, pec deck, cable fly). Less stabilizing grip = more chest.",
    "On curls, cue 'drive the elbow, relax the hand'. Think of your hand as a hook, not a gripper.",
    "Pre-exhaust the target: do the isolation (pec deck / fly) BEFORE the press so the chest is the limiter.",
    "Cut direct forearm/grip work to near zero this block — they're already ahead."
  ]
};

// Exercise ids + names + sets/reps mirror the Gymmy templates exactly.
// `cue` and `straps` are LockIn's coaching overlay on top.
export const days = [
  {
    id: "A", name: "Day A", focus: "Chest (heavy) · abs",
    warmup: "5 min bike + arm circles, then 1-2 light ramp-up sets on the first press.",
    exercises: [
      { id: "Butterfly", name: "Butterfly (pec deck)", target: "Chest", sets: 3, reps: 12, cue: "Pre-exhaust: squeeze hands together with your chest, not your arms. This tires the chest first." },
      { id: "Leverage_Incline_Chest_Press", name: "Leverage Incline Chest Press", target: "Upper chest", sets: 4, reps: 10, cue: "Elbows ~45°. Drive with the chest; hands are just hooks on the handles." },
      { id: "Machine_Bench_Press", name: "Machine Bench Press", target: "Chest", sets: 3, reps: 10, cue: "Machine = no grip fatigue. Full stretch at the bottom, controlled." },
      { id: "Cable_Crossover", name: "Cable Crossover", target: "Lower chest", sets: 3, reps: 12, cue: "High-to-low arc, meet at the belt line, 1s squeeze." },
      { id: "Cable_Crunch", name: "Cable Crunch", target: "Abs", sets: 3, reps: 12, cue: "Round the spine down toward the pelvis — crunch, don't hip-hinge." },
      { id: "Hanging_Leg_Raise", name: "Hanging Leg Raise", target: "Lower abs", sets: 3, reps: 12, cue: "Curl the pelvis up. Straps optional so grip isn't the limiter." }
    ]
  },
  {
    id: "B", name: "Day B", focus: "Legs — quad focus · calves",
    warmup: "5 min bike, bodyweight squats, one light leg-extension set.",
    exercises: [
      { id: "Hack_Squat", name: "Hack Squat", target: "Quads", sets: 4, reps: 10, cue: "Full depth, control the descent 2-3s. This is your #1 leg builder." },
      { id: "Leg_Press", name: "Leg Press", target: "Quads/Glutes", sets: 3, reps: 12, cue: "Feet mid-platform. Don't lock out hard; keep tension." },
      { id: "Romanian_Deadlift", name: "Romanian Deadlift", target: "Hamstrings", sets: 3, reps: 10, straps: true, cue: "STRAPS ON. Hinge, soft knees, feel the hamstring stretch. Grip must not be the limiter." },
      { id: "Leg_Extensions", name: "Leg Extensions", target: "Quads", sets: 3, reps: 12, cue: "1s squeeze at the top. Great finisher for the teardrop." },
      { id: "Seated_Leg_Curl", name: "Seated Leg Curl", target: "Hamstrings", sets: 3, reps: 12, cue: "Control the negative." },
      { id: "Standing_Calf_Raises", name: "Standing Calf Raises", target: "Calves", sets: 4, reps: 15, cue: "Full stretch at the bottom, pause at the top." }
    ]
  },
  {
    id: "C", name: "Day C", focus: "Back (straps) · biceps · forearms",
    warmup: "Band pull-aparts, one light lat-pulldown set.",
    exercises: [
      { id: "Wide-Grip_Lat_Pulldown", name: "Wide-Grip Lat Pulldown", target: "Lats", sets: 4, reps: 10, straps: true, cue: "STRAPS. Pull with the elbows to the hips; imagine your hands are just hooks." },
      { id: "Dumbbell_Incline_Row", name: "Dumbbell Incline Row", target: "Mid-back", sets: 3, reps: 10, straps: true, cue: "STRAPS. Chest on the bench, squeeze shoulder blades; don't yank with the arms." },
      { id: "Seated_Cable_Rows", name: "Seated Cable Rows", target: "Back", sets: 3, reps: 10, straps: true, cue: "STRAPS. Chest up, drive elbows back." },
      { id: "Face_Pull", name: "Face Pull", target: "Rear delts", sets: 3, reps: 15, cue: "Rope to forehead, external rotation. Posture insurance." },
      { id: "Incline_Dumbbell_Curl", name: "Incline Dumbbell Curl", target: "Biceps", sets: 3, reps: 10, cue: "Elbow drives the rep; keep the wrist neutral so the biceps do the work." },
      { id: "Standing_Biceps_Cable_Curl", name: "Standing Biceps Cable Curl", target: "Biceps", sets: 2, reps: 12, cue: "Constant tension, strict form." },
      { id: "Palms-Up_Barbell_Wrist_Curl_Over_A_Bench", name: "Palms-Up Barbell Wrist Curl Over A Bench", target: "Forearms", sets: 3, reps: 15, cue: "GROWTH FOCUS. Light bar, full stretch at the bottom, slow squeeze up — last thing of the day so grip fatigue costs nothing." },
      { id: "Reverse_Barbell_Curl", name: "Reverse Barbell Curl", target: "Forearms", sets: 3, reps: 12, cue: "Light weight, palms down — hits the top of the forearm that actually shows." }
    ]
  },
  {
    id: "D", name: "Day D", focus: "Legs #2 — posterior chain · obliques",
    warmup: "5 min incline walk, hip openers.",
    exercises: [
      { id: "Split_Squat_with_Dumbbells", name: "Split Squat with Dumbbells", target: "Quads/Glutes", sets: 3, reps: 10, cue: "Per leg. Front-foot pressure, tall torso. Balance + growth for lagging legs." },
      { id: "Barbell_Hip_Thrust", name: "Barbell Hip Thrust", target: "Glutes", sets: 3, reps: 10, cue: "Full lockout, 1s squeeze. Builds the shape the legs are missing." },
      { id: "Lying_Leg_Curls", name: "Lying Leg Curls", target: "Hamstrings", sets: 3, reps: 10, cue: "No hip movement; hamstrings only." },
      { id: "Dumbbell_Lunges", name: "Dumbbell Lunges", target: "Legs", sets: 3, reps: 10, straps: true, cue: "Per leg, walking-style. STRAPS so grip doesn't cap the set." },
      { id: "Standing_Cable_Wood_Chop", name: "Standing Cable Wood Chop", target: "Obliques", sets: 3, reps: 12, cue: "Per side. Rotate from the torso, not the arms. This is your new oblique work." },
      { id: "Side_Bridge", name: "Side Bridge (side plank)", target: "Obliques/Core", sets: 3, reps: null, cue: "30-40s per side. Stay square; resist the lean — anti-rotation builds the sides." }
    ]
  },
  {
    id: "E", name: "Day E", focus: "Shoulders · chest #2 · abs · forearms",
    warmup: "Band dislocates, one light lateral-raise set.",
    exercises: [
      { id: "Machine_Shoulder_Military_Press", name: "Machine Shoulder (Military) Press", target: "Front/Side delts", sets: 4, reps: 10, cue: "Press slightly forward of the ears; controlled. Machine = no grip demand." },
      { id: "Side_Lateral_Raise", name: "Side Lateral Raise", target: "Side delts", sets: 4, reps: 15, cue: "Lead with the elbow; light and strict for width." },
      { id: "Incline_Cable_Chest_Press", name: "Incline Cable Chest Press", target: "Upper chest", sets: 3, reps: 10, cue: "Second chest hit of the week — grip-light selection." },
      { id: "Butterfly", name: "Butterfly (pec deck)", target: "Chest", sets: 3, reps: 12, cue: "Pure chest squeeze, no grip demand." },
      { id: "Reverse_Machine_Flyes", name: "Reverse Machine Flyes", target: "Rear delts", sets: 3, reps: 15, cue: "Balances all the pressing." },
      { id: "Decline_Crunch", name: "Decline Crunch", target: "Abs", sets: 3, reps: 12, cue: "Hold a plate on your chest once 12 is easy. Slow eccentric; brace hard." },
      { id: "Farmers_Walk", name: "Farmers Walk", target: "Forearms/Grip", sets: 3, reps: null, cue: "GROWTH FOCUS. Heavy dumbbells, 30–40 m per carry, stand tall. The last thing you do — grip failure here is the goal." },
      { id: "Plate_Pinch", name: "Plate Pinch", target: "Forearms/Grip", sets: 3, reps: null, cue: "Two plates smooth-side out, pinch 30s per hand. Builds the thumb side wrist curls miss." }
    ]
  },
  {
    id: "F", name: "Day F", focus: "Optional 6th — light full-body pump", optional: true,
    warmup: "5 min easy bike + arm circles. This one is a BONUS for weeks that felt too light — keep every set 2-3 reps shy of failure.",
    exercises: [
      { id: "Leg_Press", name: "Leg Press", target: "Quads/Glutes", sets: 2, reps: 15, cue: "Light and smooth — pump blood through the legs, don't chase numbers." },
      { id: "Butterfly", name: "Butterfly (pec deck)", target: "Chest", sets: 2, reps: 15, cue: "Squeeze and stretch. No grinding reps on a bonus day." },
      { id: "Seated_Cable_Rows", name: "Seated Cable Rows", target: "Back", sets: 2, reps: 15, straps: true, cue: "STRAPS. Easy weight, perfect posture, full squeeze." },
      { id: "Side_Lateral_Raise", name: "Side Lateral Raise", target: "Side delts", sets: 2, reps: 15, cue: "Light and strict — lead with the elbows." },
      { id: "Cable_Crunch", name: "Cable Crunch", target: "Abs", sets: 2, reps: 15, cue: "Slow and controlled; round the spine." },
      { id: "Standing_Calf_Raises", name: "Standing Calf Raises", target: "Calves", sets: 2, reps: 15, cue: "Full stretch at the bottom, pause at the top." }
    ]
  }
];

export function dayById(id) { return days.find((d) => d.id === id); }

// Which workout to suggest for a given weekday (0=Sun..6=Sat). Gym = the 20:00
// evening slot. 5 lifting days Sun A..Thu E, plus Friday's OPTIONAL midday 6th:
// Day F (light pump) by default, or a redo of any A–E day the user picks in the
// Workout tab (state.settings.sixthDay) — for weeks that felt too light. Sat rest.
export const weekPlan = { 0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: null };
