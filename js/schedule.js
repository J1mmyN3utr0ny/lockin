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
function travelBlock(id, time, mins, title, mode = "drive", group) {
  const sub = mode === "walk"
    ? `A ${mins}-minute walk — head straight over.`
    : `About ${mins} min door-to-door — leave on time so nothing runs late.`;
  return { id, time, cat: "travel", title, sub, group };
}

function gymBlock(time, dow) {
  const id = weekPlan[dow];
  if (!id) return { id: "gym", time, cat: "gym", title: "Rest / mobility", sub: "No lift scheduled — walk, stretch, recover.", link: L.gym, group: "gym" };
  const d = dayById(id);
  const optional = dow === 5 ? " · optional — skip guilt-free if the week was heavy" : "";
  return { id: "gym", time, cat: "gym", title: `Gym · ${d.name}`, sub: `${d.focus} — same workout as in Gymmy${optional}`, link: L.gym, group: "gym" };
}

// PET work only exists while the exam is still ahead (the course itself stops at EXAM_DATE).
// Afterwards every one of those minutes rolls into the capstone / portfolio build.
function petLive(dateKey) { return S.daysBetween(dateKey, S.EXAM_DATE) >= 0; }

const PORTFOLIO_SUB = "One stage of your résumé ladder (Learn → Portfolio). Use the 🏗 Build guide when you're actively writing.";

// The 14:30–17:15 stretch of a deep-work day: PET homework + course-site drilling while the
// exam is live, otherwise one long build session. Free time starts at 17:15 either way.
// Which weekdays the course meets on around `dateKey` — it moved from Sun & Wed to
// Mon & Thu after Jul 15, and past days must keep rendering as they actually happened.
function courseDaysLabel(dateKey) {
  return S.daysBetween(dateKey, S.COURSE_MOVE) >= 0 ? "Sunday/Wednesday" : "Monday/Thursday";
}

function petAfternoon(dateKey) {
  if (petLive(dateKey)) {
    return [
      { id: "pethw", time: "14:30", cat: "pet", title: "PET course homework", sub: `A full hour on whatever's still open from ${courseDaysLabel(dateKey)}'s class. Understand each step — it's direct exam practice.` },
      { id: "petsite", time: "15:30", cat: "pet", title: "PET practice — course website", sub: "Timed drill sets on the course's site (Hebrew first). Their material mirrors the real exam." },
      { id: "portfolio", time: "16:30", cat: "cs", title: "Portfolio project — build & ship", sub: PORTFOLIO_SUB, link: "#learn/projects" }
    ];
  }
  return [
    S.daysBetween(S.PROJECT_START, dateKey) >= 0
      ? { id: "capstone", time: "14:30", cat: "cs", title: "🚀 Capstone project — the big build", sub: "Post-exam finale: your capstone in Learn → Portfolio. PET's done — pour the freed time into shipping this.", link: "#learn/projects" }
      : { id: "portfolio", time: "14:30", cat: "cs", title: "Portfolio project — build & ship", sub: `Exam's behind you — a long session on the ladder. ${PORTFOLIO_SUB}`, link: "#learn/projects" }
  ];
}

function studyMathBlock(time) {
  if (mathDone())
    return { id: "math", time, cat: "math", title: "Math keep-sharp (10 min) + CS project", sub: "Assignment done ✓ — quick PET math, then straight into building.", link: L.cs };
  return { id: "math", time, cat: "math", title: "Math assignment — DO FIRST", sub: "Clear it before anything else. Two focused sessions and it's gone.", link: L.math };
}

function deepWorkDay(dateKey, dow) {
  const t = cyberTrackFor(dateKey);
  return [
    { id: "wake", time: "07:30", cat: "sleep", title: "Wake · water · 10 min daylight", sub: "Sunlight + light mobility anchors your body clock.", link: L.sleep, fixed: true },
    { id: "breakfast", time: "08:00", cat: "food", title: "Breakfast — ~35g protein", sub: "Eat even if not hungry. It's a checklist, not a craving.", link: L.food },
    studyMathBlock("08:30"),
    { id: "csdeep", time: "10:15", cat: "cs", title: "CS project — deep work", sub: "The 'start from an empty file' muscle. One milestone at a time.", link: L.cs },
    { id: "lunch", time: "12:00", cat: "food", title: "Lunch — ~40g protein", sub: "Tuna pasta / chicken + rice.", link: L.food },
    { id: "cyber", time: "13:00", cat: "cyber", title: `Cyber — ${t.icon} ${t.name}`, sub: "In LockIn Lab (desktop): read the lesson, build it, get your code checked. 🔒 Focus is Lab-gated.", link: L.cyber },
    { id: "leet", time: "13:45", cat: "leet", title: "LeetCode — daily", sub: "Solve today's problem in the Lab (a Hard lands ~weekly). Finishing it unlocks your phone.", link: L.cyber },
    ...petAfternoon(dateKey),
    { id: "free", time: "17:15", cat: "free", free: true, title: "FREE TIME — protected", sub: "Friends, games, whatever. You earned it — nothing schedules over this." },
    { id: "snack", time: "19:00", cat: "food", title: "Snack — pre-gym fuel", sub: "~25g protein about an hour before you lift.", link: L.food },
    travelBlock("togym", "19:40", TRAVEL.gym, "Head to the gym", "drive", "gym"),
    gymBlock("20:00", dow),
    travelBlock("homegym", "21:15", TRAVEL.gym, "Head home", "drive", "gym"),
    { id: "dinner", time: "21:40", cat: "food", title: "Dinner — biggest meal, ~45g protein", sub: "Post-workout — the meal that builds the physique.", link: L.food },
    { id: "wind", time: "22:45", cat: "wind", title: "Wind-down — screens dim, prep tomorrow", sub: "Lay out gym clothes, set breakfast.", link: L.sleep, fixed: true },
    { id: "sleep", time: "23:30", cat: "sleep", title: "Sleep", sub: "Protecting this is the whole reset.", link: L.sleep, fixed: true }
  ];
}

function courseDay(dateKey, dow) {
  const t = cyberTrackFor(dateKey);
  return [
    { id: "wake", time: "07:00", cat: "sleep", title: "Wake · water · quick breakfast", sub: "Course day — up a little earlier to make the 9:00 start.", link: L.sleep, fixed: true },
    { id: "commute", time: "08:15", cat: "travel", title: "Head to PET course", sub: `About ${TRAVEL.course} min — bring water + a snack.`, fixed: true, hard: true, group: "course" },
    { id: "course", time: "09:00", cat: "pet", title: "PET course (09:00–14:00)", sub: `${S.daysBetween(dateKey, S.COURSE_MOVE) >= 0 ? "Sundays & Wednesdays" : "Mondays & Thursdays"}. This is your main PET engine.`, link: L.pet, fixed: true, hard: true, group: "course" },
    { id: "lunch", time: "14:00", cat: "food", title: "Lunch + decompress", sub: "Refuel right after class.", link: L.food, fixed: true, hard: true, group: "course" },
    { ...travelBlock("homecourse", "14:40", TRAVEL.course, "Head home", "drive", "course"), hard: true },
    { id: "leet", time: "15:30", cat: "leet", title: "LeetCode — daily (quick)", sub: "One problem in LockIn Lab. Unlocks your phone when solved.", link: L.cyber },
    { id: "light", time: "16:15", cat: "cyber", title: `Light block — ${t.icon} ${t.name} or CS`, sub: "Lower intensity after the course. A lesson in the Lab or one CS step.", link: L.cyber },
    { id: "homework", time: "17:00", cat: "pet", title: "PET homework — from today's class", sub: "The big one: 75 minutes while it's still fresh. Understand each step — it's direct exam practice, not busywork.", link: L.pet },
    { id: "petsite", time: "18:15", cat: "pet", title: "PET practice — course website", sub: "Lock in today's class with a drill set on the course's site." },
    { id: "dinner", time: "18:55", cat: "food", title: "Dinner — ~45g protein", sub: "Fuel for tonight's session — eat well before you lift.", link: L.food },
    travelBlock("togym", "19:40", TRAVEL.gym, "Head to the gym", "drive", "gym"),
    gymBlock("20:00", dow),
    travelBlock("homegym", "21:15", TRAVEL.gym, "Head home", "drive", "gym"),
    { id: "free", time: "21:40", cat: "free", free: true, title: "FREE TIME — protected", sub: "Post-gym shake, then recover. Big day done." },
    { id: "wind", time: "22:45", cat: "wind", title: "Wind-down", sub: "Prep for tomorrow.", link: L.sleep, fixed: true },
    { id: "sleep", time: "23:30", cat: "sleep", title: "Sleep", sub: "", link: L.sleep, fixed: true }
  ];
}

function fridayDay(dateKey, dow) {
  const wk = S.weekOf(dateKey);
  return [
    { id: "wake", time: "08:30", cat: "sleep", title: "Relaxed wake + breakfast", sub: "End-of-week day — but keep the wake time honest.", link: L.sleep, fixed: true },
    ...(petLive(dateKey) ? [
      { id: "pethw", time: "09:30", cat: "pet", title: "PET catch-up — homework + weak spots", sub: "Close out anything left from the week's two classes, then drill the section that hurt most. Hebrew wins the exam." }
    ] : []),
    { id: "review", time: "10:30", cat: "review", title: `📋 Weekly Review — Week ${wk}`, sub: `Cumulative test: everything you've learned through week ${wk}. Beat last week's score.`, link: "#review" },
    { id: "labreview", time: "11:30", cat: "leet", title: "Lab: re-solve a past problem", sub: "Pick an earlier LeetCode/DSA exercise and redo it from scratch — proof it stuck.", link: L.cyber },
    travelBlock("togym", "12:15", TRAVEL.gym, "Head to the gym", "drive", "gym"),
    gymBlock("12:40", dow),
    travelBlock("homegym", "13:50", TRAVEL.gym, "Head home", "drive", "gym"),
    { id: "free1", time: "14:15", cat: "free", free: true, title: "FREE — friends / rest", sub: "You reviewed the week. Enjoy it." },
    { id: "dinner", time: "19:00", cat: "food", title: "Family dinner — EAT BIG", sub: "Your best-eating day. Seconds encouraged — this fuels growth.", link: L.food, fixed: true, hard: true },
    { id: "free2", time: "20:30", cat: "free", free: true, title: "FREE evening", sub: "" },
    { id: "sleep", time: "00:00", cat: "sleep", title: "Sleep (a bit later is OK)", sub: "Don't drift too far — Monday's course comes fast.", link: L.sleep, fixed: true }
  ];
}

function shabbatDay(dateKey) {
  const mondayCourse = S.dayType(S.addDays(dateKey, 2)) === "course";
  return [
    { id: "rest", time: "—", cat: "free", free: true, title: "REST DAY — Shabbat", sub: "The built-in light day. No goals required. This does NOT cost an off-day token.", fixed: true },
    { id: "flash", time: "11:00", cat: "cyber", title: "Optional: 10-min flashcards", sub: "Only if you feel like it.", link: L.cyber, fixed: true },
    { id: "dinner", time: "19:00", cat: "food", title: "Dinner — hit your protein", sub: "Recovery still needs food.", link: L.food, fixed: true },
    { id: "sleep", time: "23:30", cat: "sleep", title: mondayCourse ? "Protect sleep — Monday is a course day" : "Protect sleep",
      sub: mondayCourse ? "Back on the 07:30 wake tomorrow; 07:00 on Monday." : "Back on the 07:30 wake tomorrow.", link: L.sleep, fixed: true }
  ];
}

function canonicalBlocks(dateKey) {
  const type = S.dayType(dateKey);
  const dow = S.dow(dateKey);
  if (type === "course") return { type, label: "Course day", blocks: courseDay(dateKey, dow) };
  if (type === "friday") return { type, label: "Friday — Weekly Review", blocks: fridayDay(dateKey, dow) };
  if (type === "shabbat") return { type, label: "Shabbat — rest", blocks: shabbatDay(dateKey) };
  return { type, label: "Deep-work day", blocks: deepWorkDay(dateKey, dow) };
}

export function buildDay(dateKey) {
  const c = canonicalBlocks(dateKey);
  let blocks = applyDayOrder(dateKey, c.blocks);
  // Catch-up only decorates today and future days; the debt itself is computed from
  // PAST days built without decoration — so this can never recurse.
  if (S.daysBetween(S.todayKey(), dateKey) >= 0) blocks = applyCatchUp(blocks);
  return { type: c.type, label: c.label, taper: taperTargets(dateKey), blocks };
}

// ---- catch-up: unfinished blocks become the next days' focus -------------------
// Debt = study blocks missed over the last 7 days. Off-days, Shabbat and days before
// the program don't count, and a user-skipped unit (dayTweaks) isn't a miss. Cyber is
// the priority track (GAMA prep), so it's always boosted and listed first.
export const DEBT_CATS = ["cyber", "leet", "pet", "cs", "math"];
let _debtCache = { key: "", debt: null };

export function catchUpDebt() {
  const st = S.getState();
  const today = S.todayKey();
  const key = today + ":" + (st.updatedAt || 0);
  if (_debtCache.key === key) return _debtCache.debt;
  const debt = { cyber: 0, leet: 0, pet: 0, cs: 0, math: 0 };
  for (let i = 1; i <= 7; i++) {
    const k = S.addDays(today, -i);
    if (S.daysBetween(S.PROGRAM_START, k) < 0) break;
    if (st.offDays.spent.includes(k) || S.dayType(k) === "shabbat") continue;
    const rec = st.days[k];
    const ticked = (rec && rec.blocks) || {};
    // past days: canonical + the user's saved order/skips, WITHOUT catch-up decoration
    for (const b of applyDayOrder(k, canonicalBlocks(k).blocks)) {
      if (!b.free && DEBT_CATS.includes(b.cat) && !ticked[b.id]) {
        debt[b.cat] = Math.min(4, debt[b.cat] + 1); // cap so one bad week can't demand the impossible
      }
    }
  }
  _debtCache = { key, debt };
  return debt;
}

export function debtSummary() {
  const debt = catchUpDebt();
  return DEBT_CATS.filter((c) => debt[c] > 0).map((c) => `${c} ×${debt[c]}`);
}

const CATCHUP_NOTE = {
  cyber: (n) => `⚡ CATCH-UP: ${n} missed cyber session${n > 1 ? "s" : ""} this week — add ${n > 1 ? "an extra Lab lesson AND its explain-back" : "one extra Lab lesson"} today. Cyber debt clears first.`,
  leet: (n) => `⚡ CATCH-UP: ${n} missed problem${n > 1 ? "s" : ""} this week — solve one extra (or redo an old one from scratch).`,
  pet: (n) => `⚡ CATCH-UP: ${n} missed PET block${n > 1 ? "s" : ""} this week — add one extra drill set. The exam doesn't move.`,
  cs: (n) => `⚡ CATCH-UP: the project lost ${n} session${n > 1 ? "s" : ""} this week — push one milestone step further today.`,
  math: (n) => `⚡ CATCH-UP: ${n} missed math block${n > 1 ? "s" : ""} — clear assignment work before it stacks up.`
};

function applyCatchUp(blocks) {
  const debt = catchUpDebt();
  if (!DEBT_CATS.some((c) => debt[c] > 0)) return blocks;
  const boosted = new Set(); // decorate only the FIRST block of each indebted category
  return blocks.map((b) => {
    if (b.free || !debt[b.cat] || boosted.has(b.cat)) return b;
    boosted.add(b.cat);
    return { ...b, catchUp: true, sub: `${CATCHUP_NOTE[b.cat](debt[b.cat])} ${b.sub || ""}`.trim() };
  });
}

// ---- movable units & per-day reordering -------------------------------------
// A "unit" is the smallest thing the user can move: one block, or an inseparable
// group that travels together (drive→gym→drive; the PET-course cluster). Units
// flagged `fixed` (wake, wind-down, sleep, the course, family dinner) anchor the
// day. Movable units may be reordered BETWEEN two anchors; times are then
// recomputed from block durations, so everything still meets each anchor exactly.

function minOf(t) { const m = /^(\d{1,2}):(\d{2})$/.exec(t || ""); return m ? Number(m[1]) * 60 + Number(m[2]) : null; }

// Group consecutive blocks that share a `group` tag into single units. `fixed` units
// anchor the reorder; `hard` units (the PET course, family dinner) additionally refuse
// whole-day shifts — the world outside the app doesn't move because you slept in.
export function unitize(blocks) {
  const units = [];
  for (const b of blocks) {
    const last = units[units.length - 1];
    if (b.group && last && last.group === b.group) {
      last.blocks.push(b);
      last.fixed = last.fixed || !!b.fixed;
      last.hard = last.hard || !!b.hard;
    } else units.push({ id: b.id, group: b.group || null, fixed: !!b.fixed, hard: !!b.hard, blocks: [b] });
  }
  return units;
}

// Duration of every block = gap to the next timed block (day order). The value is
// derived from the canonical times, so segment totals always equal the anchor gap.
function blockDurations(blocks) {
  const durs = new Map();
  for (let i = 0; i < blocks.length; i++) {
    const t = minOf(blocks[i].time);
    let d = 45;
    if (t !== null) {
      for (let j = i + 1; j < blocks.length; j++) {
        const n = minOf(blocks[j].time);
        if (n !== null) { d = n - t; if (d <= 0) d += 1440; break; }
      }
    }
    durs.set(blocks[i], d);
  }
  return durs;
}

// Apply the user's (or the AI's) saved plan for this date: drop skipped units,
// reorder movable units within their segment, shift the day's own anchors (wake,
// wind-down, sleep — never `hard` ones), then re-time everything off the durations.
function applyDayOrder(dateKey, blocks) {
  const st = S.getState();
  const saved = (st.dayOrders || {})[dateKey] || [];
  const tweaks = (st.dayTweaks || {})[dateKey] || {};
  const shift = Math.round(Number(tweaks.shift) || 0);
  const skip = new Set(Array.isArray(tweaks.skip) ? tweaks.skip : []);
  if (!saved.length && !shift && !skip.size) return blocks;
  if (blocks.some((b) => minOf(b.time) === null)) return blocks; // untimed day (Shabbat) — nothing to move

  const durs = blockDurations(blocks); // durations from CANONICAL times, before any drop
  let units = unitize(blocks);
  if (skip.size) units = units.filter((u) => u.fixed || !skip.has(u.id));

  // Reorder each run of movable units (a "segment") by the saved id order;
  // ids the save doesn't know keep their canonical order (stable sort).
  const ordered = [];
  let seg = [];
  const flush = () => {
    seg.sort((a, b) => {
      const ia = saved.indexOf(a.id), ib = saved.indexOf(b.id);
      return (ia === -1 ? 1e9 : ia) - (ib === -1 ? 1e9 : ib);
    });
    ordered.push(...seg);
    seg = [];
  };
  for (const u of units) {
    if (u.fixed) { flush(); ordered.push(u); }
    else seg.push(u);
  }
  flush();

  // Re-time: fixed anchors keep their canonical time (+shift unless hard); movable
  // blocks stack from the cursor between them.
  let cursor = minOf(units[0].blocks[0].time) + (units[0].hard ? 0 : shift);
  const out = [];
  for (const u of ordered) {
    if (u.fixed) {
      const uShift = u.hard ? 0 : shift;
      for (const b of u.blocks) out.push(uShift ? { ...b, time: toHHMM(minOf(b.time) + uShift) } : b);
      const lastB = u.blocks[u.blocks.length - 1];
      cursor = minOf(lastB.time) + uShift + durs.get(lastB);
    } else {
      for (const b of u.blocks) {
        out.push({ ...b, time: toHHMM(cursor) });
        cursor += durs.get(b);
      }
    }
  }
  return out;
}

export function hasCustomOrder(dateKey) {
  const st = S.getState();
  return !!(((st.dayOrders || {})[dateKey] || []).length || (st.dayTweaks || {})[dateKey]);
}
export function resetDayOrder(dateKey) {
  S.update((st) => {
    if (st.dayOrders) delete st.dayOrders[dateKey];
    if (st.dayTweaks) delete st.dayTweaks[dateKey];
  });
}

function saveOrder(dateKey, ids) {
  S.update((st) => {
    if (!st.dayOrders) st.dayOrders = {};
    st.dayOrders[dateKey] = ids;
    for (const k of Object.keys(st.dayOrders)) {
      if (S.daysBetween(k, dateKey) > 7) delete st.dayOrders[k]; // prune stale days
    }
  });
}

// Drag & drop: re-insert the movable unit `unitId` at `insertAt` — an index into the
// unit list WITHOUT the dragged unit. Clamped to the unit's own segment so a drop
// can never cross a fixed anchor. Returns true when an order was saved.
export function placeUnit(dateKey, unitId, insertAt) {
  const units = unitize(buildDay(dateKey).blocks);
  const i = units.findIndex((u) => u.id === unitId);
  if (i < 0 || units[i].fixed) return false;
  let lo = i; while (lo > 0 && !units[lo - 1].fixed) lo--;
  let hi = i; while (hi < units.length - 1 && !units[hi + 1].fixed) hi++;
  // After removing the unit, its segment occupies [lo, hi-1]; valid insert points are lo..hi.
  const t = Math.max(lo, Math.min(hi, insertAt));
  const arr = units.slice();
  const [u] = arr.splice(i, 1);
  arr.splice(t, 0, u);
  saveOrder(dateKey, arr.filter((x) => !x.fixed).map((x) => x.id));
  S.logEvent("adjust", `reordered the day plan (${S.prettyDate(dateKey)})`);
  return true;
}

// The AI day-planner writes whole plans at once — for today AND following days (a late
// hangout tonight can push tomorrow's start). Each day may reorder, SKIP movable units,
// and SHIFT the day's own anchors (wake/wind-down/sleep; `hard` anchors never move).
// Everything is validated against the canonical day — any deviation rejects the whole
// plan and nothing changes.
export function applyAiPlan(days) {
  if (!Array.isArray(days) || !days.length || days.length > 4) return false;
  const today = S.todayKey();
  const writes = [];
  for (const d of days) {
    if (!d || typeof d.date !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(d.date)) return false;
    const ahead = S.daysBetween(today, d.date);
    if (ahead < 0 || ahead > 7) return false;
    const shift = Math.round(Number(d.shift) || 0);
    if (shift < -120 || shift > 180) return false;
    const movable = unitize(canonicalBlocks(d.date).blocks).filter((u) => !u.fixed).map((u) => u.id);
    const skip = Array.isArray(d.skip) ? d.skip : [];
    if (new Set(skip).size !== skip.length || !skip.every((id) => movable.includes(id))) return false;
    const remaining = movable.filter((id) => !skip.includes(id));
    const order = Array.isArray(d.order) && d.order.length ? d.order : remaining;
    if (order.length !== remaining.length || new Set(order).size !== order.length ||
        !order.every((id) => remaining.includes(id))) return false;
    writes.push({ date: d.date, order, shift, skip });
  }
  S.update((st) => {
    if (!st.dayOrders) st.dayOrders = {};
    if (!st.dayTweaks) st.dayTweaks = {};
    for (const w of writes) {
      st.dayOrders[w.date] = w.order;
      if (w.shift || w.skip.length) st.dayTweaks[w.date] = { shift: w.shift, skip: w.skip };
      else delete st.dayTweaks[w.date];
    }
    for (const k of Object.keys(st.dayTweaks)) {
      if (S.daysBetween(k, today) > 7) delete st.dayTweaks[k];
    }
  });
  return true;
}

// How many non-free blocks a day has, for progress math.
export function taskBlockIds(dateKey) {
  return buildDay(dateKey).blocks.filter((b) => !b.free).map((b) => b.id);
}
