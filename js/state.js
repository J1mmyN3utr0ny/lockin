// state.js — single source of truth, persisted to localStorage, with date helpers.

export const KEY = "lockin.state.v1";
export const PROGRAM_START = "2026-07-14"; // the whole program is anchored here (a Tuesday)
export const SUMMER_END = "2026-09-30"; // extended: build through the capstone, then -> Test Mode
export const COURSE_START = "2026-07-14"; // PET course runs Sun & Wed 09:00-14:00 (first one Wed Jul 15)
export const EXAM_DATE = "2026-09-03"; // PET exam (Sep 2-3; anchored to the later day). Course ends here.
export const PROJECT_START = "2026-09-05"; // the capstone kicks off 2 days after the exam
export const WAKE_TARGET = "07:30";
export const OFFDAY_TOKENS = 10; // more free days across the longer summer — room for a social life

function todayISO() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

// Week number of the program (week 1 = Jul 12–18), and its date range.
// Before the program starts we still call it week 1 (the upcoming week).
export function weekOf(dateKey) {
  const diff = daysBetween(PROGRAM_START, dateKey);
  if (diff < 0) return 1;
  return Math.floor(diff / 7) + 1;
}
export function weekRange(week) {
  const start = addDays(PROGRAM_START, (week - 1) * 7);
  return { start, end: addDays(start, 6) };
}

function defaults() {
  return {
    version: 1,
    createdAt: new Date().toISOString(),
    updatedAt: 0, // ms of the last edit — drives last-write-wins sync between phone and PC
    startKey: PROGRAM_START, // program anchored to Jul 12, not first-run day
    settings: { debugDate: null, mode: "auto", onboarded: false, geminiKey: "", labUrl: "" },
    lab: { status: null, syncedAt: null }, // last synced snapshot from the desktop Lab
    profile: {
      name: "",
      bodyweightKg: 62,
      // Tzav-Rishon + Hundred-Day context (for the "you're already competitive" panel)
      stats: {
        dapar: "90/90", keshev: "4/5", profile: "72/98", hebrewCls: "8/8",
        hundred: { "Instructional": 4, "Human Care": 3, "Technical-Op": 5, "Admin/Org": 4,
          "Info Processing": 5, "Command": 3, "Teamwork": 3, "Persistence": 4,
          "Framework": 5, "Maturity": 4, "Spatial": 5 }
      }
    },
    sleep: { logs: {} }, // logs[key] = { sleep:"03:30", wake:"14:00" }
    meals: {}, // meals[key] = { slotId:true }
    days: {}, // days[key] = { blocks:{id:true}, offDay:false, note:"" }
    workoutLogs: {}, // [key] = { dayId, ex:{ exId:[{w,r}] } }
    cs: { milestones: {} }, // id -> { status, hintLevel, reflection }
    projects: {}, // resume-project id -> { stages:{i:{done,hintLevel}}, ship:{i:true}, bullets, reflection, rebuilt }
    math: { checklist: {} }, // id -> true
    pet: { mathSolved: {}, sentencesDone: {} }, // id->true
    skills: {}, // trackId -> { level, milestones:{id:true} }
    decks: {}, // cardId -> { box, due }
    git: { lessons: {} }, // lessonId -> { done: true }
    lessons: {}, // rich Learn-hub lesson id -> { done, date }
    reviews: {}, // weekNumber -> { score, total, date }
    body: { weights: {} }, // dateKey -> kg (bodyweight log)
    xp: 0,
    offDays: { spent: [] }, // [dateKey,...]
    reflections: []
  };
}

function deepMerge(base, saved) {
  if (Array.isArray(base)) return Array.isArray(saved) ? saved : base;
  if (base && typeof base === "object") {
    const out = { ...base };
    if (saved && typeof saved === "object") {
      for (const k of Object.keys(saved)) {
        out[k] = k in base ? deepMerge(base[k], saved[k]) : saved[k];
      }
    }
    return out;
  }
  return saved === undefined ? base : saved;
}

let state = defaults();
const listeners = new Set();

// One-time clean start: the program now begins PROGRAM_START (Jul 14). Wipe every day-keyed record
// and all accumulated progress from before then — those days are gone, as if they never happened.
// Device settings and profile are kept so you don't have to re-onboard or re-enter the Lab URL.
const ANCHOR_RESET = "2026-07-14";
function migrateToAnchor(st) {
  if (st._anchorReset === ANCHOR_RESET) return;
  st.days = {}; st.meals = {}; st.workoutLogs = {}; st.reviews = {}; st.reflections = [];
  st.sleep = { logs: {} }; st.body = { weights: {} };
  st.offDays = { spent: [] };
  st.skills = {}; st.projects = {}; st.lessons = {}; st.decks = {};
  st.cs = { milestones: {} }; st.math = { checklist: {} };
  st.pet = { mathSolved: {}, sentencesDone: {} }; st.git = { lessons: {} };
  st.xp = 0;
  st._anchorReset = ANCHOR_RESET;
  st.updatedAt = Date.now(); // treat the reset as the newest state so it propagates to the other device
}

export function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) { state = deepMerge(defaults(), JSON.parse(raw)); migrateToAnchor(state); save(); }
  } catch (e) { /* corrupt storage -> fresh defaults */ }
  return state;
}
export function save() {
  try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
}
export function getState() { return state; }
export function update(mutator) {
  mutator(state);
  state.updatedAt = Date.now();
  save();
  emit();
}
// Adopt a state blob pulled from the Lab sync hub. Keeps THIS device's connection settings and Lab
// snapshot (labUrl / geminiKey are per-device), and does not bump updatedAt — we take the remote's.
export function applyRemote(remote) {
  if (!remote || typeof remote !== "object" || !remote.settings || remote.version === undefined) return false;
  // Connection config is per-device; everything else (progress, xp, onboarded, …) syncs.
  const keepLabUrl = state.settings.labUrl;
  const keepKey = state.settings.geminiKey;
  const keepLab = state.lab;
  state = deepMerge(defaults(), remote);
  state.settings.labUrl = keepLabUrl;
  state.settings.geminiKey = keepKey;
  state.lab = keepLab;
  state.updatedAt = remote.updatedAt || Date.now();
  save();
  emit();
  return true;
}
export function subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); }
export function emit() { listeners.forEach((fn) => fn(state)); }

export function resetAll() {
  state = defaults();
  save();
  emit();
}

// ---- Date helpers -----------------------------------------------------------
export function now() {
  const dbg = state.settings.debugDate;
  if (dbg) { const d = new Date(dbg + "T12:00:00"); if (!isNaN(d)) return d; }
  return new Date();
}
export function keyOf(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
export function todayKey() { return keyOf(now()); }
export function addDays(dateKey, n) {
  const d = new Date(dateKey + "T12:00:00");
  d.setDate(d.getDate() + n);
  return keyOf(d);
}
export function daysBetween(aKey, bKey) {
  const a = new Date(aKey + "T12:00:00"), b = new Date(bKey + "T12:00:00");
  return Math.round((b - a) / 86400000);
}
export function dow(dateKey) { return new Date(dateKey + "T12:00:00").getDay(); } // 0=Sun..6=Sat
export function prettyDate(dateKey) {
  return new Date(dateKey + "T12:00:00").toLocaleDateString("en-GB", {
    weekday: "long", day: "numeric", month: "long"
  });
}
export const DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

// Day template type for a given date.
export function dayType(dateKey) {
  const d = dow(dateKey);
  // The PET course runs Sun & Wed from COURSE_START until the exam; after that those days free up.
  const courseLive = daysBetween(COURSE_START, dateKey) >= 0 && daysBetween(dateKey, EXAM_DATE) >= 0;
  if (d === 6) return "shabbat";
  if (d === 5) return "friday";
  if ((d === 0 || d === 3) && courseLive) return "course";
  return "deepwork";
}

// Current app mode: summer vs post-summer test mode.
export function appMode() {
  if (state.settings.mode !== "auto") return state.settings.mode;
  return daysBetween(SUMMER_END, todayKey()) >= 0 ? "test" : "summer";
}
export function daysToSummerEnd() { return daysBetween(todayKey(), SUMMER_END); }

// Off-day tokens
export function offDaysLeft() { return OFFDAY_TOKENS - state.offDays.spent.length; }

// Ensure a day record exists (does not persist by itself).
export function dayRec(key) {
  if (!state.days[key]) state.days[key] = { blocks: {}, offDay: false, note: "" };
  return state.days[key];
}

// ---- XP & levels ------------------------------------------------------------
// Level curve: level N needs 50·N² XP total (0→Lv1 at 50, Lv2 at 200, Lv3 at 450...).
export function levelOf(xp) { return Math.floor(Math.sqrt(Math.max(0, xp) / 50)); }
export function levelProgress(xp) {
  const lvl = levelOf(xp);
  const cur = 50 * lvl * lvl, next = 50 * (lvl + 1) * (lvl + 1);
  return { lvl, into: xp - cur, need: next - cur, pct: ((xp - cur) / (next - cur)) * 100 };
}
export function addXP(n) {
  const before = levelOf(state.xp || 0);
  state.xp = Math.max(0, (state.xp || 0) + n);
  const after = levelOf(state.xp);
  save();
  emit();
  if (after > before) {
    window.dispatchEvent(new CustomEvent("lockin:levelup", { detail: { level: after } }));
  }
}

// Consecutive-day streak: a day counts if it was productive (≥3 blocks), a spent off-day,
// or a logged Shabbat rest. Today-in-progress doesn't break the streak.
export function computeStreak() {
  let k = todayKey(), streak = 0;
  for (let i = 0; i < 200; i++) {
    const rec = state.days[k];
    const off = state.offDays.spent.includes(k);
    const productive = rec && Object.values(rec.blocks || {}).filter(Boolean).length >= 3;
    const shabbat = dayType(k) === "shabbat";
    if (off || productive || (shabbat && rec)) streak++;
    else if (i === 0) { /* today may still be in progress */ }
    else break;
    k = addDays(k, -1);
  }
  return streak;
}
