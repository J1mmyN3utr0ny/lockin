// workout_program.js — 5-day full-gym split tuned to the user's goals:
// GROW: chest, legs (weakest), abs, and START obliques. MAINTAIN: biceps (already strong).
// FIX: forearms hijacking every lift. See `forearmFix` for the mechanism used throughout.

export const philosophy = {
  title: "How this program is built for you",
  points: [
    "Legs are trained twice a week (Day B + Day D) because they're the biggest gap.",
    "Chest gets a heavy day and a second volume day (Day A + Day E).",
    "Abs are hit 3×/week; obliques get dedicated loaded work (new for you) on Day D + Day E.",
    "Biceps are maintained, not chased — one focused slot on Day C, done with a grip that spares forearms.",
    "Progressive overload is the whole game: beat last week's log by a rep or a small load, every session."
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
    "Pre-exhaust the target: do the isolation (fly / pec deck) BEFORE the press so the chest is the limiter.",
    "Cut direct forearm/grip work to near zero this block — they're already ahead."
  ]
};

// Each exercise: id, name, target, sets, reps (rep range), straps, cue.
export const days = [
  {
    id: "A", name: "Chest + Abs", focus: "Chest (heavy) · Abs",
    warmup: "5 min bike + arm circles, then 2 light warmup sets on the first press.",
    exercises: [
      { id: "A1", name: "Pec deck (pre-exhaust)", target: "Chest", sets: 3, reps: "12-15", cue: "Squeeze hands together with your chest, not your arms. This tires the chest first." },
      { id: "A2", name: "Incline machine / Smith press", target: "Upper chest", sets: 4, reps: "8-12", cue: "Elbows ~45°. Drive with the chest; hands are just hooks on the bar." },
      { id: "A3", name: "Flat machine chest press", target: "Chest", sets: 3, reps: "10-12", cue: "Machine = no grip fatigue. Full stretch at the bottom." },
      { id: "A4", name: "Cable fly (high-to-low)", target: "Lower chest", sets: 3, reps: "12-15", cue: "Long arc, meet at the belt line, 1s squeeze." },
      { id: "A5", name: "Cable crunch", target: "Abs", sets: 3, reps: "12-15", cue: "Round the spine down toward the pelvis — crunch, don't hip-hinge." },
      { id: "A6", name: "Hanging / captain's-chair leg raise", target: "Lower abs", sets: 3, reps: "10-15", cue: "Curl the pelvis up. Straps optional so grip isn't the limiter." }
    ]
  },
  {
    id: "B", name: "Legs (Quad focus)", focus: "Quads · Glutes · Calves",
    warmup: "5 min bike, bodyweight squats, leg-extension warmup set.",
    exercises: [
      { id: "B1", name: "Hack squat or Barbell squat", target: "Quads", sets: 4, reps: "8-12", cue: "Full depth, control the descent 2-3s. This is your #1 leg builder." },
      { id: "B2", name: "Leg press", target: "Quads/Glutes", sets: 3, reps: "10-15", cue: "Feet mid-platform. Don't lock out hard; keep tension." },
      { id: "B3", name: "Romanian deadlift", target: "Hamstrings", sets: 3, reps: "8-12", straps: true, cue: "STRAPS ON. Hinge, soft knees, feel the hamstring stretch. Grip must not be the limiter." },
      { id: "B4", name: "Leg extension", target: "Quads", sets: 3, reps: "12-15", cue: "1s squeeze at the top. Great finisher for the teardrop." },
      { id: "B5", name: "Seated leg curl", target: "Hamstrings", sets: 3, reps: "12-15", cue: "Control the negative." },
      { id: "B6", name: "Standing calf raise", target: "Calves", sets: 4, reps: "12-20", cue: "Full stretch at the bottom, pause at the top." }
    ]
  },
  {
    id: "C", name: "Back + Biceps", focus: "Back (straps) · Biceps (maintain)",
    warmup: "Band pull-aparts, light lat-pulldown set.",
    exercises: [
      { id: "C1", name: "Lat pulldown", target: "Lats", sets: 4, reps: "8-12", straps: true, cue: "STRAPS. Pull with the elbows to the hips; imagine your hands are just hooks." },
      { id: "C2", name: "Chest-supported row", target: "Mid-back", sets: 3, reps: "10-12", straps: true, cue: "STRAPS. Squeeze shoulder blades; don't yank with the arms." },
      { id: "C3", name: "Seated cable row (neutral)", target: "Back", sets: 3, reps: "10-12", straps: true, cue: "STRAPS. Chest up, drive elbows back." },
      { id: "C4", name: "Face pull", target: "Rear delts", sets: 3, reps: "15-20", cue: "Rope to forehead, external rotation. Posture insurance." },
      { id: "C5", name: "Incline DB curl", target: "Biceps", sets: 3, reps: "10-12", cue: "Elbow drives the rep; keep wrist neutral and grip loose to keep forearms out of it." },
      { id: "C6", name: "Cable curl (bar)", target: "Biceps", sets: 2, reps: "12-15", cue: "Constant tension. Maintenance only — don't turn this into a forearm day." }
    ]
  },
  {
    id: "D", name: "Legs #2 + Obliques", focus: "Posterior chain · Obliques (new)",
    warmup: "5 min incline walk, hip openers.",
    exercises: [
      { id: "D1", name: "Bulgarian split squat", target: "Quads/Glutes", sets: 3, reps: "8-12 /leg", cue: "Front-foot pressure, tall torso. Balance + growth for lagging legs." },
      { id: "D2", name: "Hip thrust", target: "Glutes", sets: 3, reps: "10-12", cue: "Full lockout, 1s squeeze. Builds the shape the legs are missing." },
      { id: "D3", name: "Lying leg curl", target: "Hamstrings", sets: 3, reps: "10-12", cue: "No hip movement; hamstrings only." },
      { id: "D4", name: "Walking lunge", target: "Legs", sets: 3, reps: "10-12 /leg", straps: true, cue: "STRAPS if using DBs, so grip doesn't cap the set." },
      { id: "D5", name: "Cable woodchopper", target: "Obliques", sets: 3, reps: "12-15 /side", cue: "Rotate from the torso, not the arms. This is your new oblique work." },
      { id: "D6", name: "Suitcase carry / side plank", target: "Obliques/Core", sets: 3, reps: "30-40s", cue: "Stay square; resist the lean. Anti-rotation builds the sides." }
    ]
  },
  {
    id: "E", name: "Shoulders + Chest #2 + Abs", focus: "Delts · Chest volume · Abs",
    warmup: "Band dislocates, light lateral raises.",
    exercises: [
      { id: "E1", name: "Machine / DB shoulder press", target: "Front/Side delts", sets: 4, reps: "8-12", cue: "Press slightly forward of the ears; controlled." },
      { id: "E2", name: "Lateral raise", target: "Side delts", sets: 4, reps: "12-20", cue: "Lead with the elbow; light and strict for width." },
      { id: "E3", name: "Incline cable/machine press", target: "Upper chest", sets: 3, reps: "10-12", cue: "Second chest hit of the week — grip-light selection." },
      { id: "E4", name: "Pec deck", target: "Chest", sets: 3, reps: "12-15", cue: "Pure chest squeeze, no grip demand." },
      { id: "E5", name: "Rear-delt fly", target: "Rear delts", sets: 3, reps: "15-20", cue: "Balances all the pressing." },
      { id: "E6", name: "Ab wheel / weighted decline crunch", target: "Abs", sets: 3, reps: "8-15", cue: "Slow eccentric; brace hard." }
    ]
  }
];

export function dayById(id) { return days.find((d) => d.id === id); }

// Which workout to suggest for a given weekday (0=Sun..6=Sat).
// 5 lifting days: Sun A, Mon B, Tue C, Wed D (lighter after course), Thu E, Fri light/optional, Sat rest.
export const weekPlan = { 0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: null, 6: null };
