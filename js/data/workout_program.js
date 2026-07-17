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
  // Launches the installed Gymmy app from the PWA on Android via its gymmy:// deep link
  // (Gymmy 1.4+ declares a VIEW+BROWSABLE intent-filter for scheme "gymmy"). Browsers
  // refuse to dispatch intent:// links to activities without category BROWSABLE, so the
  // old MAIN/LAUNCHER-targeting URL could never work — the fix required a change in
  // Gymmy's manifest, not just here. Chrome intent syntax: scheme + package, host-less.
  intentUrl: "intent://open/#Intent;scheme=gymmy;package=com.yaniv.gymmy;end"
};

export const philosophy = {
  title: "How this program is built for you",
  points: [
    "EQUIPMENT RULE: machines with built-in weight stacks and cables first; dumbbells and short/EZ bars are fine. NO free-barbell squats, deadlifts, RDLs or lunges — nothing that means standing up and down under a bar.",
    "Fewer sets, more exercises: most slots are 2 hard sets. Variety covers the muscle from more angles without grinding volume on any one lift.",
    "CALVES are an emphasis now: trained on five days (seated raise, standing machine, leg-press calf press) — they grow on frequency.",
    "Legs are trained twice (Day B quads + Day D posterior chain), and adductors/abductors get machine work BOTH days — inner/outer thigh is real leg mass.",
    "Chest keeps a heavy day and a volume day (Day A + Day E). Abs 3×/week on machines and cables.",
    "Biceps are maintained, not chased; forearms grow via direct wrist work on cables, dumbbells and short bars (Day C + Day E).",
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
    "Use lifting straps on ALL back/pull work (pulldowns, rows). The lats should quit first — not your grip.",
    "Prefer machines & cables for chest (machine press, pec deck, cable fly). Less stabilizing grip = more chest.",
    "On curls, cue 'drive the elbow, relax the hand'. Think of your hand as a hook, not a gripper.",
    "Pre-exhaust the target: do the isolation (pec deck / fly) BEFORE the press so the chest is the limiter.",
    "Forearm GROWTH comes from the dedicated wrist-curl slots (Day C + Day E) — seated, supported, no heavy carrying."
  ]
};

// Exercise ids + names + sets/reps mirror the Gymmy templates exactly.
// `cue` and `straps` are LockIn's coaching overlay on top.
export const days = [
  {
    id: "A", name: "Day A", focus: "Chest (heavy) · abs · calves",
    warmup: "5 min bike + arm circles, then 1-2 light ramp-up sets on the first press.",
    exercises: [
      { id: "Butterfly", name: "Butterfly (pec deck)", target: "Chest", sets: 2, reps: 12, cue: "Pre-exhaust: squeeze hands together with your chest, not your arms. This tires the chest first." },
      { id: "Leverage_Incline_Chest_Press", name: "Leverage Incline Chest Press", target: "Upper chest", sets: 3, reps: 10, cue: "The day's main lift. Elbows ~45°; drive with the chest — hands are just hooks." },
      { id: "Machine_Bench_Press", name: "Machine Bench Press", target: "Chest", sets: 2, reps: 10, cue: "Machine = no grip fatigue. Full stretch at the bottom, controlled." },
      { id: "Cable_Crossover", name: "Cable Crossover", target: "Lower chest", sets: 2, reps: 12, cue: "High-to-low arc, meet at the belt line, 1s squeeze." },
      { id: "Ab_Crunch_Machine", name: "Ab Crunch Machine", target: "Abs", sets: 2, reps: 15, cue: "Pin-loaded and strict — exhale hard and curl the ribs to the hips." },
      { id: "Cable_Crunch", name: "Cable Crunch", target: "Abs", sets: 2, reps: 12, cue: "Round the spine down toward the pelvis — crunch, don't hip-hinge." },
      { id: "Seated_Calf_Raise", name: "Seated Calf Raise", target: "Calves", sets: 3, reps: 15, cue: "CALF EMPHASIS. Full stretch at the bottom, 1s pause at the top — the pause is the growth." }
    ]
  },
  {
    id: "B", name: "Day B", focus: "Legs — quads · adductors/abductors · calves",
    warmup: "5 min bike, one light leg-extension set, one light leg-press set.",
    exercises: [
      { id: "Leg_Press", name: "Leg Press", target: "Quads/Glutes", sets: 3, reps: 12, cue: "Your #1 leg builder now — seated, supported, heavy. Feet mid-platform; don't lock out hard." },
      { id: "Leg_Extensions", name: "Leg Extensions", target: "Quads", sets: 3, reps: 12, cue: "1s squeeze at the top. Builds the teardrop without any standing." },
      { id: "Seated_Leg_Curl", name: "Seated Leg Curl", target: "Hamstrings", sets: 2, reps: 12, cue: "Control the negative — hamstrings grow on the way back." },
      { id: "Thigh_Adductor", name: "Thigh Adductor (machine)", target: "Inner thigh", sets: 2, reps: 15, cue: "NEW. Squeeze in smoothly, no slamming — inner thigh is real leg size." },
      { id: "Thigh_Abductor", name: "Thigh Abductor (machine)", target: "Outer thigh/Glutes", sets: 2, reps: 15, cue: "NEW. Push out against the pads; keeps the hips strong and balanced." },
      { id: "Standing_Calf_Raises", name: "Standing Calf Raises (machine)", target: "Calves", sets: 3, reps: 15, cue: "CALF EMPHASIS. Full stretch, pause at the top, no bouncing." },
      { id: "Calf_Press_On_The_Leg_Press_Machine", name: "Calf Press (leg press)", target: "Calves", sets: 2, reps: 15, cue: "Straight into it after the standing raises — a different angle on the same growth." }
    ]
  },
  {
    id: "C", name: "Day C", focus: "Back (straps) · biceps · forearms",
    warmup: "Band pull-aparts, one light lat-pulldown set.",
    exercises: [
      { id: "Wide-Grip_Lat_Pulldown", name: "Wide-Grip Lat Pulldown", target: "Lats", sets: 3, reps: 10, straps: true, cue: "STRAPS. Pull with the elbows to the hips; imagine your hands are just hooks." },
      { id: "Seated_Cable_Rows", name: "Seated Cable Rows", target: "Back", sets: 2, reps: 10, straps: true, cue: "STRAPS. Chest up, drive elbows back." },
      { id: "Dumbbell_Incline_Row", name: "Dumbbell Incline Row", target: "Mid-back", sets: 2, reps: 10, straps: true, cue: "STRAPS. Chest on the bench so the lower back rests; squeeze the shoulder blades." },
      { id: "Face_Pull", name: "Face Pull", target: "Rear delts", sets: 2, reps: 15, cue: "Rope to forehead, external rotation. Posture insurance." },
      { id: "Incline_Dumbbell_Curl", name: "Incline Dumbbell Curl", target: "Biceps", sets: 2, reps: 10, cue: "Elbow drives the rep; keep the wrist neutral so the biceps do the work." },
      { id: "Cable_Hammer_Curls_-_Rope_Attachment", name: "Cable Hammer Curls (rope)", target: "Biceps/Forearms", sets: 2, reps: 12, cue: "Neutral grip on the rope — hits the arm-thickness muscles and the top of the forearm together." },
      { id: "Palms-Up_Barbell_Wrist_Curl_Over_A_Bench", name: "Palms-Up Wrist Curl (short bar)", target: "Forearms", sets: 2, reps: 15, cue: "GROWTH FOCUS. Light short bar, full stretch at the bottom, slow squeeze up." },
      { id: "Reverse_Barbell_Curl", name: "Reverse Curl (EZ bar)", target: "Forearms", sets: 2, reps: 12, cue: "Light EZ bar, palms down — the top of the forearm that actually shows." }
    ]
  },
  {
    id: "D", name: "Day D", focus: "Legs #2 — hamstrings/glutes · obliques · calves",
    warmup: "5 min incline walk, hip openers, one light lying-curl set.",
    exercises: [
      { id: "Lying_Leg_Curls", name: "Lying Leg Curls", target: "Hamstrings", sets: 3, reps: 10, cue: "The day's main lift. No hip movement; hamstrings only." },
      { id: "Leg_Press", name: "Leg Press (feet high)", target: "Glutes/Hamstrings", sets: 2, reps: 12, cue: "Feet HIGH and wide on the platform — same machine, posterior-chain bias. No barbell needed." },
      { id: "One-Legged_Cable_Kickback", name: "One-Legged Cable Kickback", target: "Glutes", sets: 2, reps: 12, cue: "Per leg. Ankle cuff on the low pulley; drive the heel back and squeeze — glute work without a bar." },
      { id: "Thigh_Adductor", name: "Thigh Adductor (machine)", target: "Inner thigh", sets: 2, reps: 15, cue: "Second weekly hit — inner thigh responds fast to frequency." },
      { id: "Thigh_Abductor", name: "Thigh Abductor (machine)", target: "Outer thigh/Glutes", sets: 2, reps: 15, cue: "Second weekly hit. Push out, pause, control back in." },
      { id: "Standing_Cable_Wood_Chop", name: "Standing Cable Wood Chop", target: "Obliques", sets: 2, reps: 12, cue: "Per side. Rotate from the torso, not the arms — your loaded oblique work." },
      { id: "Seated_Calf_Raise", name: "Seated Calf Raise", target: "Calves", sets: 3, reps: 15, cue: "CALF EMPHASIS — second seated session of the week. Pause every rep at the top." }
    ]
  },
  {
    id: "E", name: "Day E", focus: "Shoulders · chest #2 · abs · forearms · calves",
    warmup: "Band dislocates, one light lateral-raise set.",
    exercises: [
      { id: "Machine_Shoulder_Military_Press", name: "Machine Shoulder (Military) Press", target: "Front/Side delts", sets: 3, reps: 10, cue: "Press slightly forward of the ears; controlled. Machine = no grip demand." },
      { id: "Side_Lateral_Raise", name: "Side Lateral Raise", target: "Side delts", sets: 2, reps: 12, cue: "Dumbbells, light and strict — lead with the elbows for width." },
      { id: "Incline_Cable_Chest_Press", name: "Incline Cable Chest Press", target: "Upper chest", sets: 2, reps: 10, cue: "Second chest hit of the week — grip-light cable pressing." },
      { id: "Reverse_Machine_Flyes", name: "Reverse Machine Flyes", target: "Rear delts", sets: 2, reps: 15, cue: "Balances all the pressing." },
      { id: "Cable_Crunch", name: "Cable Crunch", target: "Abs", sets: 2, reps: 15, cue: "Third ab session of the week — slow, exhale hard at the bottom." },
      { id: "Seated_Two-Arm_Palms-Up_Low-Pulley_Wrist_Curl", name: "Cable Wrist Curl (low pulley)", target: "Forearms", sets: 2, reps: 15, cue: "GROWTH FOCUS. Constant cable tension the whole rep — better than any carry, no walking required." },
      { id: "Seated_Dumbbell_Palms-Down_Wrist_Curl", name: "Palms-Down DB Wrist Curl", target: "Forearms", sets: 2, reps: 12, cue: "Light dumbbells, palms down — the extensors that make the forearm look wide." },
      { id: "Calf_Press_On_The_Leg_Press_Machine", name: "Calf Press (leg press)", target: "Calves", sets: 3, reps: 15, cue: "CALF EMPHASIS — heavy day. Full stretch at the bottom; make the top brutal." }
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
      { id: "Seated_Calf_Raise", name: "Seated Calf Raise", target: "Calves", sets: 2, reps: 20, cue: "High-rep calf pump to close the week — pause at the top, always." }
    ]
  }
];

export function dayById(id) { return days.find((d) => d.id === id); }

// Which workout to suggest for a given weekday (0=Sun..6=Sat). Gym = the 20:00
// evening slot. 5 lifting days Sun A..Thu E, plus Friday's OPTIONAL midday 6th:
// Day F (light pump) by default, or a redo of any A–E day the user picks in the
// Workout tab (state.settings.sixthDay) — for weeks that felt too light. Sat rest.
export const weekPlan = { 0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: null };
