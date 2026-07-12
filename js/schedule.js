// schedule.js — the daily routine engine. Builds a timeblocked day from the weekday,
// the sleep-taper phase, the active goals and the fixed PET course. Free time is always a
// protected block near the end of the day.
import * as S from "./state.js";
import { weekPlan, dayById } from "./data/workout_program.js";
import { tracks } from "./data/skill_tracks.js";
import { sections as mathSections } from "./data/math_checklist.js";

// ---- sleep taper -----------------------------------------------------------
// He currently wakes ~17:00. We walk wake-time earlier ~75 min/day to a 07:30 anchor.
const START_WAKE = 17 * 60;      // 17:00 in minutes
const TARGET_WAKE = 7 * 60 + 30; // 07:30
const SHIFT = 75;                // minutes earlier per day

function toHHMM(mins) {
  mins = ((mins % 1440) + 1440) % 1440;
  return `${String(Math.floor(mins / 60)).padStart(2, "0")}:${String(mins % 60).padStart(2, "0")}`;
}

// Days since the program start (Jul 12). Everything is anchored here, not the first-run day.
function programDay(dateKey) {
  return Math.max(0, S.daysBetween(S.PROGRAM_START, dateKey));
}

export function taperTargets(dateKey) {
  const i = programDay(dateKey);
  const wake = Math.max(TARGET_WAKE, START_WAKE - i * SHIFT);
  const inReset = wake > TARGET_WAKE;
  const bed = wake + (23 * 60 + 30) - TARGET_WAKE; // keep ~8h; bed walks earlier with wake
  return { wake: toHHMM(wake), sleep: toHHMM(Math.min(bed, 24 * 60 + 30)), inReset, dayIndex: i };
}

// ---- rotations (anchored to Jul 12) ----------------------------------------
export function cyberTrackFor(dateKey) {
  return tracks[programDay(dateKey) % tracks.length];
}

// Hebrew is the priority; weight the PET rotation toward it.
const PET_ROTA = ["Hebrew vocab", "Hebrew sentences", "English vocab", "Hebrew vocab", "Math drills", "Hebrew vocab"];
export function petFocusFor(dateKey) {
  return PET_ROTA[programDay(dateKey) % PET_ROTA.length];
}

function mathDone() {
  const c = S.getState().math.checklist;
  return mathSections.every((s) => c[s.id]);
}

// ---- block builders --------------------------------------------------------
const L = { food: "#body/diet", gym: "#body/physique", cyber: "#learn/cyber",
  pet: "#learn/pet", cs: "#learn/csmentor", math: "#learn/math", sleep: "#body/sleep" };

function gymBlock(time, dow) {
  const id = weekPlan[dow];
  if (!id) return { id: "gym", time, cat: "gym", title: "Rest / mobility", sub: "No lift scheduled — walk, stretch, recover.", link: L.gym };
  const d = dayById(id);
  return { id: "gym", time, cat: "gym", title: `Gym · Day ${id} — ${d.name}`, sub: d.focus, link: L.gym };
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
    { id: "snack", time: "15:15", cat: "food", title: "Snack + short rest", sub: "Pre-gym fuel.", link: L.food },
    gymBlock("16:00", dow),
    { id: "dinner", time: "17:45", cat: "food", title: "Dinner — biggest meal, ~45g protein", sub: "The meal that builds the physique.", link: L.food },
    { id: "petpractice", time: "18:45", cat: "pet", title: `PET practice — ${petFocusFor(dateKey)}`, sub: "One focused set. Understand the path, not just the answer.", link: L.pet },
    { id: "free", time: "19:45", cat: "free", free: true, title: "FREE TIME — protected", sub: "Friends, games, whatever. You earned it — nothing schedules over this." },
    { id: "wind", time: "22:45", cat: "wind", title: "Wind-down — screens dim, prep tomorrow", sub: "Lay out gym clothes, set breakfast.", link: L.sleep },
    { id: "sleep", time: "23:30", cat: "sleep", title: "Sleep", sub: "Protecting this is the whole reset.", link: L.sleep }
  ];
}

function courseDay(dateKey, dow) {
  const t = cyberTrackFor(dateKey);
  return [
    { id: "wake", time: "07:00", cat: "sleep", title: "Wake · water · quick breakfast", sub: "Course day — up a little earlier to make the 9:00 start.", link: L.sleep },
    { id: "commute", time: "08:15", cat: "pet", title: "Head to PET course", sub: "Bring water + a snack." },
    { id: "course", time: "09:00", cat: "pet", title: "PET course (09:00–14:00)", sub: "Sundays & Wednesdays. This is your main PET engine.", link: L.pet },
    { id: "lunch", time: "14:00", cat: "food", title: "Lunch + decompress", sub: "Refuel properly after 5 hours of focus.", link: L.food },
    gymBlock("15:15", dow),
    { id: "leet", time: "16:30", cat: "leet", title: "LeetCode — daily (quick)", sub: "One problem in LockIn Lab. Unlocks your phone when solved.", link: L.cyber },
    { id: "light", time: "17:00", cat: "cyber", title: `Light block — ${t.icon} ${t.name} or CS`, sub: "Lower intensity after the course. A lesson in the Lab or one CS step.", link: L.cyber },
    { id: "dinner", time: "18:15", cat: "food", title: "Dinner — ~45g protein", sub: "", link: L.food },
    { id: "review", time: "19:00", cat: "pet", title: "Review course notes + vocab", sub: "Lock in today's course material while it's fresh.", link: L.pet },
    { id: "free", time: "19:45", cat: "free", free: true, title: "FREE TIME — protected", sub: "Recover. Big day done." },
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
    gymBlock("12:15", dow),
    { id: "free1", time: "14:00", cat: "free", free: true, title: "FREE — friends / rest", sub: "You reviewed the week. Enjoy it." },
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
