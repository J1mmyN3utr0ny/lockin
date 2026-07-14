// schedule.js — the daily routine engine. Builds a timeblocked day from the weekday,
// the sleep-taper phase, the active goals and the fixed PET course. Free time is always a
// protected block near the end of the day.
import * as S from "./state.js";
import { weekPlan, dayById } from "./data/workout_program.js";
import { tracks } from "./data/skill_tracks.js";
import { sections as mathSections } from "./data/math_checklist.js";

// ---- sleep target ----------------------------------------------------------
// Instant fix: hold the 07:30 wake / 23:30 sleep anchor from day one — no gradual walk-back.
const TARGET_WAKE = 7 * 60 + 30; // 07:30

function toHHMM(mins) {
  mins = ((mins % 1440) + 1440) % 1440;
  return `${String(Math.floor(mins / 60)).padStart(2, "0")}:${String(mins % 60).padStart(2, "0")}`;
}

// Days since the program start. Everything is anchored here, not the first-run day.
function programDay(dateKey) {
  return Math.max(0, S.daysBetween(S.PROGRAM_START, dateKey));
}

export function taperTargets(dateKey) {
  // No taper — the target is a 07:30 wake and 23:30 sleep every day, starting immediately.
  return { wake: toHHMM(TARGET_WAKE), sleep: "23:30", inReset: false, dayIndex: programDay(dateKey) };
}

// ---- rotations -------------------------------------------------------------
// The rotation index counts PRODUCTIVE days only: an off-day doesn't burn a lesson, it pauses the
// rotation so the topic you'd have done simply rolls to your next working day — recycled, never
// skipped. (Off-days strictly before this date shift everything after them back by one.)
function rotationIndex(dateKey) {
  const cal = programDay(dateKey);
  const offBefore = S.getState().offDays.spent.filter(
    (k) => S.daysBetween(S.PROGRAM_START, k) >= 0 && S.daysBetween(k, dateKey) > 0
  ).length;
  return Math.max(0, cal - offBefore);
}

export function cyberTrackFor(dateKey) {
  return tracks[rotationIndex(dateKey) % tracks.length];
}

// Hebrew is the priority; weight the PET rotation toward it.
const PET_ROTA = ["Hebrew vocab", "Hebrew sentences", "English vocab", "Hebrew vocab", "Math drills", "Hebrew vocab"];
export function petFocusFor(dateKey) {
  return PET_ROTA[rotationIndex(dateKey) % PET_ROTA.length];
}

function mathDone() {
  const c = S.getState().math.checklist;
  return mathSections.every((s) => c[s.id]);
}

// ---- block builders --------------------------------------------------------
const L = { food: "#body/diet", gym: "#body/physique", cyber: "#learn/cyber",
  pet: "#learn/pet", cs: "#learn/csmentor", math: "#learn/math", sleep: "#body/sleep" };

// Explicit travel time so the day doesn't silently run late. One-way minutes (tweak here if they
// change): home↔gym and home↔course are drives; the gym is a short walk from the PET course.
const TRAVEL = { gym: 20, course: 30, courseToGym: 10 };
function travelBlock(id, time, mins, title, mode = "drive") {
  const sub = mode === "walk"
    ? `A ${mins}-minute walk — head straight over.`
    : `About ${mins} min door-to-door — leave on time so nothing runs late.`;
  return { id, time, cat: "travel", title, sub };
}

function gymBlock(time, dow) {
  const id = weekPlan[dow];
  if (!id) return { id: "gym", time, cat: "gym", title: "Rest / mobility", sub: "No lift scheduled — walk, stretch, recover.", link: L.gym };
  const d = dayById(id);
  const optional = dow === 5 ? " · optional — skip guilt-free if the week was heavy" : "";
  return { id: "gym", time, cat: "gym", title: `Gym · ${d.name}`, sub: `${d.focus} — same workout as in Gymmy${optional}`, link: L.gym };
}

function studyMathBlock(time) {
  if (mathDone())
    return { id: "math", time, cat: "math", title: "Math keep-sharp (10 min) + CS project", sub: "Assignment done ✓ — quick PET math, then straight into building.", link: L.cs };
  return { id: "math", time, cat: "math", title: "Math assignment — DO FIRST", sub: "Clear it before anything else. Two focused sessions and it's gone.", link: L.math };
}

function deepWorkDay(dateKey, dow) {
  const t = cyberTrackFor(dateKey);
  return [
    { id: "wake", time: "07:30", cat: "sleep", title: "Wake · water · 10 min daylight", sub: "Sunlight + light mobility anchors your body clock.", link: L.sleep },
    { id: "breakfast", time: "08:00", cat: "food", title: "Breakfast — ~35g protein", sub: "Eat even if not hungry. It's a checklist, not a craving.", link: L.food },
    studyMathBlock("08:30"),
    { id: "csdeep", time: "10:15", cat: "cs", title: "CS project — deep work", sub: "The 'start from an empty file' muscle. One milestone at a time.", link: L.cs },
    { id: "lunch", time: "12:00", cat: "food", title: "Lunch — ~40g protein", sub: "Tuna pasta / chicken + rice.", link: L.food },
    { id: "cyber", time: "13:00", cat: "cyber", title: `Cyber — ${t.icon} ${t.name}`, sub: "In LockIn Lab (desktop): read the lesson, build it, get your code checked. 🔒 Focus is Lab-gated.", link: L.cyber },
    { id: "leet", time: "13:45", cat: "leet", title: "LeetCode — daily", sub: "Solve today's problem in the Lab (a Hard lands ~weekly). Finishing it unlocks your phone.", link: L.cyber },
    { id: "vocab", time: "14:30", cat: "pet", title: "Hebrew + English vocab", sub: "15+ new words. Recognition compounds fast.", link: L.pet },
    S.daysBetween(S.PROJECT_START, dateKey) >= 0
      ? { id: "capstone", time: "15:15", cat: "cs", title: "🚀 Capstone project — the big build", sub: "Post-exam finale: your capstone in Learn → Portfolio. PET's done — pour the freed time into shipping this.", link: "#learn/projects" }
      : { id: "petpractice", time: "15:15", cat: "pet", title: `PET practice — ${petFocusFor(dateKey)}`, sub: "One focused set. Understand the path, not just the answer.", link: L.pet },
    { id: "free", time: "16:15", cat: "free", free: true, title: "FREE TIME — protected", sub: "Friends, games, whatever. You earned it — nothing schedules over this." },
    { id: "snack", time: "19:00", cat: "food", title: "Snack — pre-gym fuel", sub: "~25g protein about an hour before you lift.", link: L.food },
    travelBlock("togym", "19:40", TRAVEL.gym, "Head to the gym"),
    gymBlock("20:00", dow),
    travelBlock("homegym", "21:15", TRAVEL.gym, "Head home"),
    { id: "dinner", time: "21:40", cat: "food", title: "Dinner — biggest meal, ~45g protein", sub: "Post-workout — the meal that builds the physique.", link: L.food },
    { id: "wind", time: "22:45", cat: "wind", title: "Wind-down — screens dim, prep tomorrow", sub: "Lay out gym clothes, set breakfast.", link: L.sleep },
    { id: "sleep", time: "23:30", cat: "sleep", title: "Sleep", sub: "Protecting this is the whole reset.", link: L.sleep }
  ];
}

function courseDay(dateKey, dow) {
  const t = cyberTrackFor(dateKey);
  return [
    { id: "wake", time: "07:00", cat: "sleep", title: "Wake · water · quick breakfast", sub: "Course day — up a little earlier to make the 9:00 start.", link: L.sleep },
    { id: "commute", time: "08:15", cat: "travel", title: "Head to PET course", sub: `About ${TRAVEL.course} min — bring water + a snack.` },
    { id: "course", time: "09:00", cat: "pet", title: "PET course (09:00–14:00)", sub: "Sundays & Wednesdays. This is your main PET engine.", link: L.pet },
    { id: "lunch", time: "14:00", cat: "food", title: "Lunch + decompress", sub: "Refuel right after class.", link: L.food },
    travelBlock("homecourse", "14:40", TRAVEL.course, "Head home"),
    { id: "leet", time: "15:30", cat: "leet", title: "LeetCode — daily (quick)", sub: "One problem in LockIn Lab. Unlocks your phone when solved.", link: L.cyber },
    { id: "light", time: "16:15", cat: "cyber", title: `Light block — ${t.icon} ${t.name} or CS`, sub: "Lower intensity after the course. A lesson in the Lab or one CS step.", link: L.cyber },
    { id: "homework", time: "17:15", cat: "pet", title: "PET homework — from today's class", sub: "Do it while it's fresh. Understand each step — it's direct exam practice, not busywork.", link: L.pet },
    { id: "review", time: "18:00", cat: "pet", title: "Review notes + vocab", sub: "Lock in today's course material.", link: L.pet },
    { id: "dinner", time: "18:40", cat: "food", title: "Dinner — ~45g protein", sub: "Fuel for tonight's session — eat well, you lift at 20:00.", link: L.food },
    travelBlock("togym", "19:40", TRAVEL.gym, "Head to the gym"),
    gymBlock("20:00", dow),
    travelBlock("homegym", "21:15", TRAVEL.gym, "Head home"),
    { id: "free", time: "21:40", cat: "free", free: true, title: "FREE TIME — protected", sub: "Post-gym shake, then recover. Big day done." },
    { id: "wind", time: "22:45", cat: "wind", title: "Wind-down", sub: "Prep for tomorrow.", link: L.sleep },
    { id: "sleep", time: "23:30", cat: "sleep", title: "Sleep", sub: "", link: L.sleep }
  ];
}

function fridayDay(dateKey, dow) {
  const wk = S.weekOf(dateKey);
  return [
    { id: "wake", time: "08:30", cat: "sleep", title: "Relaxed wake + breakfast", sub: "End-of-week day — but keep the wake time honest.", link: L.sleep },
    { id: "review", time: "10:30", cat: "review", title: `📋 Weekly Review — Week ${wk}`, sub: `Cumulative test: everything you've learned through week ${wk}. Beat last week's score.`, link: "#review" },
    { id: "labreview", time: "11:30", cat: "leet", title: "Lab: re-solve a past problem", sub: "Pick an earlier LeetCode/DSA exercise and redo it from scratch — proof it stuck.", link: L.cyber },
    travelBlock("togym", "12:15", TRAVEL.gym, "Head to the gym"),
    gymBlock("12:40", dow),
    travelBlock("homegym", "13:50", TRAVEL.gym, "Head home"),
    { id: "free1", time: "14:15", cat: "free", free: true, title: "FREE — friends / rest", sub: "You reviewed the week. Enjoy it." },
    { id: "dinner", time: "19:00", cat: "food", title: "Family dinner — EAT BIG", sub: "Your best-eating day. Seconds encouraged — this fuels growth.", link: L.food },
    { id: "free2", time: "20:30", cat: "free", free: true, title: "FREE evening", sub: "" },
    { id: "sleep", time: "00:00", cat: "sleep", title: "Sleep (a bit later is OK)", sub: "Don't drift too far — Sunday is a course day.", link: L.sleep }
  ];
}

function shabbatDay(dateKey) {
  return [
    { id: "rest", time: "—", cat: "free", free: true, title: "REST DAY — Shabbat", sub: "The built-in light day. No goals required. This does NOT cost an off-day token." },
    { id: "flash", time: "11:00", cat: "cyber", title: "Optional: 10-min flashcards", sub: "Only if you feel like it.", link: L.cyber },
    { id: "dinner", time: "19:00", cat: "food", title: "Dinner — hit your protein", sub: "Recovery still needs food.", link: L.food },
    { id: "sleep", time: "23:30", cat: "sleep", title: "Protect sleep — Sunday is a course day", sub: "Back on the 07:00 wake tomorrow.", link: L.sleep }
  ];
}

export function buildDay(dateKey) {
  const type = S.dayType(dateKey);
  const dow = S.dow(dateKey);
  const taper = taperTargets(dateKey);
  let blocks, label;
  if (type === "course") { blocks = courseDay(dateKey, dow); label = "Course day"; }
  else if (type === "friday") { blocks = fridayDay(dateKey, dow); label = "Friday — Weekly Review"; }
  else if (type === "shabbat") { blocks = shabbatDay(dateKey); label = "Shabbat — rest"; }
  else { blocks = deepWorkDay(dateKey, dow); label = "Deep-work day"; }
  return { type, label, taper, blocks };
}

// How many non-free blocks a day has, for progress math.
export function taskBlockIds(dateKey) {
  return buildDay(dateKey).blocks.filter((b) => !b.free).map((b) => b.id);
}
