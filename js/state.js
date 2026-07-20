// state.js — single source of truth, persisted to localStorage, with date helpers.

export const KEY = "lockin.state.v1";
export const PROGRAM_START = "2026-07-14"; // the whole program is anchored here (a Tuesday)
export const SUMMER_END = "2026-09-30"; // extended: build through the capstone, then -> Test Mode
export const COUNTDOWN_TARGET = "2026-09-01"; // the date the top-bar countdown pill counts down to
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
    settings: { debugDate: null, mode: "auto", onboarded: false, geminiKey: "", geminiKey2: "", labUrl: "", sixthDay: "F" },
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
    tickAt: {}, // tickAt[key][blockId] = ms the tick was last toggled — lets sync merge ticks
                // per-checkbox instead of letting one device's whole-state push erase the other's.
                // The pseudo-id "__off" stamps off-day toggles so those merge the same way.
    _syncSeed: 0, // one-time cross-device reconcile marker (see SYNC_SEED / seedOnce in lab.js)
    dayOrders: {}, // dayOrders[key] = [movable unit ids in the user's chosen day order]
    dayTweaks: {}, // dayTweaks[key] = { shift: mins, skip: [unit ids] } — AI/day adjustments
    customLessons: [], // AI-generated Learn-hub lessons (see modules/lesson_gen.js)
    events: [], // capped log of notable app events — the AI manager's raw material
    notifications: [], // manager notes for the 🔔 panel: {id, t, icon, text, read}
    autogen: { lastRun: 0 }, // throttle for the background lesson auto-builder
    workoutLogs: {}, // [key] = { dayId, ex:{ exId:[{w,r}] } }
    workoutTweaks: {}, // [key] = { dayId, note, exercises:[{id,sets,reps}] } — AI-adjusted session
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

// ---- sync clock hygiene ------------------------------------------------------
// updatedAt drives last-write-wins. A value from the FUTURE is therefore poison: it wins
// forever, every device adopts the stale blob carrying it, and — because a real edit then
// sets updatedAt to a SMALLER number (Date.now()) — the push guard in lab.js decides there's
// nothing new and the edit never leaves the device. That is exactly how a hand-injected
// 9999999999999 in the hub's app_state.json silently froze phone->desktop sync: ticks were
// made, stored locally, and never sent. Never trust a clock we didn't just read ourselves.
// An impossible clock is demoted to 0 rather than clamped to now: we have no idea when that blob
// was really written, and clamping to now would promote a stale snapshot to "newest in the system"
// — turning a stuck sync into active data loss. 0 makes it lose every comparison instead, which is
// safe now that day ticks merge independently of the clock.
const CLOCK_SKEW_MS = 5 * 60 * 1000; // tolerate a little honest clock drift between devices
export function sanitizeClock(ts) {
  const n = Number(ts);
  if (!isFinite(n) || n <= 0) return 0;
  return n > Date.now() + CLOCK_SKEW_MS ? 0 : n;
}

export function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      state = deepMerge(defaults(), JSON.parse(raw));
      migrateToAnchor(state);
      // Heal a device that already swallowed a poisoned clock (it can't sync until we do).
      const fixed = sanitizeClock(state.updatedAt);
      if (fixed !== (state.updatedAt || 0)) state.updatedAt = fixed;
      save();
    }
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
// Like update(), but for DEVICE-ONLY fields (labUrl, geminiKey/geminiKey2): saves and
// re-renders WITHOUT bumping updatedAt, so per-device config never makes this device
// "newest" in last-write-wins sync and pushes its state over the other device's data.
export function updateLocal(mutator) {
  mutator(state);
  save();
  emit();
}
// Adopt a state blob pulled from the Lab sync hub. Keeps THIS device's labUrl (the desktop says
// "localhost", the phone says the PC's LAN IP — they can never be the same value) and Lab snapshot,
// and does not bump updatedAt — we take the remote's. The Gemini keys DO sync (single user, one
// pair of keys everywhere) — but an empty remote key never wipes a locally-set one.
// Day records are ALWAYS merged (see mergeDays) — that part is order-independent, so a device
// that was offline can never lose its ticks just because the other one pushed more recently.
// Everything else still follows last-write-wins, and is only taken when the remote really is
// newer. XP takes the max: it's a monotonic counter, and watching it drop reads as data loss.
// Returns true if anything actually changed (so callers only repaint when there's news).
export function applyRemote(remote) {
  if (!remote || typeof remote !== "object" || !remote.settings || remote.version === undefined) return false;
  const remoteTs = sanitizeClock(remote.updatedAt);
  const newer = remoteTs > (state.updatedAt || 0);
  const merged = mergeDays(state, remote);
  if (!newer && !merged.changed) return false;

  const keepLabUrl = state.settings.labUrl;
  const keepKey = state.settings.geminiKey;
  const keepKey2 = state.settings.geminiKey2;
  const keepLab = state.lab;
  const keepXp = state.xp || 0;
  const keepSeed = state._syncSeed || 0; // the one-time reconcile marker is per-device, never adopted
  const keepProfile = state.profile;
  const keepWeights = (state.body && state.body.weights) || {};
  if (newer) {
    state = deepMerge(defaults(), remote);
    state.settings.labUrl = keepLabUrl;
    state.lab = keepLab;
  }
  // Keys, name, and the weight log sync BOTH ways (single user, one set of data everywhere), not
  // only on the newer path: adopt any non-empty remote value we're missing so a key pasted or a
  // weight logged on one device reaches the other even when neither state is strictly newer.
  const rs = remote.settings || {}, rp = remote.profile || {};
  state.settings.geminiKey = (newer ? state.settings.geminiKey : keepKey) || rs.geminiKey || keepKey || "";
  state.settings.geminiKey2 = (newer ? state.settings.geminiKey2 : keepKey2) || rs.geminiKey2 || keepKey2 || "";
  if (!newer) {
    state.profile = keepProfile;
    if (!state.profile.name && rp.name) state.profile.name = rp.name;
    if (rp.bodyweightKg && (!state.profile.bodyweightKg || remoteTs >= (state.updatedAt || 0)))
      state.profile.bodyweightKg = rp.bodyweightKg;
  }
  state.body = state.body || { weights: {} };
  state.body.weights = { ...((remote.body && remote.body.weights) || {}), ...keepWeights }; // local wins ties
  state.days = merged.days;
  state.tickAt = merged.tickAt;
  // off-days follow the merged day flags on BOTH devices, so a token spent anywhere shows everywhere.
  state.offDays = state.offDays || { spent: [] };
  state.offDays.spent = Object.keys(merged.days).filter((k) => merged.days[k].offDay).sort();
  state.xp = Math.max(keepXp, Number(remote.xp) || 0);
  state._syncSeed = keepSeed;
  // If we folded in ticks the hub hasn't seen, we are now the newest copy and must push the union
  // back. The stamp has to BEAT the blob we just merged, not merely be "now": if the other device's
  // clock runs even slightly ahead of ours, a plain Date.now() lands behind it and lab.js's push
  // guard silently swallows the union — the merge would be correct locally and never leave the
  // device. max(now, remote+1) keeps it honest and guarantees it propagates.
  state.updatedAt = merged.changed ? Math.max(Date.now(), remoteTs + 1) : (remoteTs || Date.now());
  save();
  emit();
  return true;
}
export function subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); }
export function emit() { listeners.forEach((fn) => fn(state)); }

// ---- one-time cross-device reconcile --------------------------------------------------------
// The phone and desktop drifted apart before per-field sync existed. To let the desktop CATCH UP,
// the richer device (the phone, which holds the real progress) wins one reconcile: it stamps its
// state fresh and pushes authoritatively; the other device adopts it. After that, ongoing sync is
// fully bidirectional. Bump SYNC_SEED to trigger another reconcile in the future.
export const SYNC_SEED = 1;
export function seedDone() { return (state._syncSeed || 0) >= SYNC_SEED; }
// How much real progress a state holds — the tiebreak for who wins the one-time reconcile.
export function richness(s = state) {
  if (!s || typeof s !== "object") return -1;
  const onboarded = s.settings && s.settings.onboarded ? 5 : 0;
  const xp = Number(s.xp) > 0 ? 3 : 0;
  const days = Object.keys(s.days || {}).length;
  const off = ((s.offDays && s.offDays.spent) || []).length;
  const name = s.profile && s.profile.name ? 1 : 0;
  return onboarded + xp + days + off + name;
}
// This device is authoritative: keep our data, stamp it fresh so our push is newest, mark seeded.
export function seedAsAuthority() {
  state._syncSeed = SYNC_SEED;
  state.updatedAt = Date.now();
  save();
  emit();
}
// This device just records that the reconcile happened (no push) — used by the device that will
// instead ADOPT the authoritative copy through the normal pull/stream.
export function markSeeded() {
  state._syncSeed = SYNC_SEED;
  save();
}

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
// The PET course MOVED: it ran Sun & Wed through Jul 15, and runs Mon & Thu from Jul 17
// on (Thu Jul 16 is explicitly excluded — the course skips it during the switch). The
// old rule stays in place for past dates so history renders as it actually happened.
export const COURSE_MOVE = "2026-07-15"; // last day of the Sun/Wed era
const COURSE_SKIP = "2026-07-16"; // the one Thursday the new era does NOT include

export function dayType(dateKey) {
  const d = dow(dateKey);
  if (d === 6) return "shabbat";
  if (d === 5) return "friday";
  const courseLive = daysBetween(COURSE_START, dateKey) >= 0 && daysBetween(dateKey, EXAM_DATE) >= 0;
  if (courseLive && dateKey !== COURSE_SKIP) {
    const oldEra = daysBetween(dateKey, COURSE_MOVE) >= 0; // dateKey <= Jul 15
    if (oldEra ? (d === 0 || d === 3) : (d === 1 || d === 4)) return "course";
  }
  return "deepwork";
}

// Current app mode: summer vs post-summer test mode.
export function appMode() {
  if (state.settings.mode !== "auto") return state.settings.mode;
  return daysBetween(SUMMER_END, todayKey()) >= 0 ? "test" : "summer";
}
export function daysToSummerEnd() { return daysBetween(todayKey(), SUMMER_END); }
export function daysToCountdown() { return daysBetween(todayKey(), COUNTDOWN_TARGET); }

// Off-day tokens
export function offDaysLeft() { return OFFDAY_TOKENS - state.offDays.spent.length; }

// Log a notable app event for the AI manager to reason over (capped, oldest dropped).
export function logEvent(type, text) {
  update((st) => {
    if (!Array.isArray(st.events)) st.events = [];
    st.events.push({ t: Date.now(), type, text });
    if (st.events.length > 40) st.events = st.events.slice(-40);
  });
}

// Ensure a day record exists (does not persist by itself).
export function dayRec(key) {
  if (!state.days[key]) state.days[key] = { blocks: {}, offDay: false, note: "" };
  return state.days[key];
}

// Tick a block on/off AND stamp when it happened. The stamp is what lets two devices merge
// their checkboxes (see mergeDays) instead of the newer whole-state blob silently winning.
const TICK_KEEP_DAYS = 400; // keep stamps long enough that off-days months back still sync
function _stamp(st, dateKey, id) {
  if (!st.tickAt) st.tickAt = {};
  (st.tickAt[dateKey] = st.tickAt[dateKey] || {})[id] = Date.now();
  const cutoff = addDays(todayKey(), -TICK_KEEP_DAYS);
  for (const k of Object.keys(st.tickAt)) {
    if (k < cutoff) delete st.tickAt[k]; // ISO keys sort lexicographically = chronologically
  }
}
export function setBlock(dateKey, id, on) {
  update((st) => {
    dayRec(dateKey).blocks[id] = on;
    _stamp(st, dateKey, id);
  });
}

// Take/cancel an off-day WITH a timestamp, so it merges across devices exactly like a tick.
// offDays.spent is kept as the fast lookup, but the merge is driven by days[key].offDay + the
// "__off" stamp so taking an off-day on the phone reliably shows up on the desktop (and vice versa).
export function setOffDay(dateKey, on) {
  update((st) => {
    dayRec(dateKey).offDay = !!on;
    if (!st.offDays) st.offDays = { spent: [] };
    const set = new Set(st.offDays.spent);
    if (on) set.add(dateKey); else set.delete(dateKey);
    st.offDays.spent = [...set].sort();
    _stamp(st, dateKey, "__off");
  });
}

// Merge two devices' day records checkbox by checkbox.
// Rule per (date, blockId): whichever side stamped it more recently wins. With no stamp on
// either side (data written before tickAt existed, or by an older build) a tick WINS over an
// absence — a checkmark is positive evidence that work happened, while its absence may just
// mean the other device never heard about it.
function mergeDays(local, remote) {
  const lT = local.tickAt || {}, rT = (remote && remote.tickAt) || {};
  const lD = local.days || {}, rD = (remote && remote.days) || {};
  const days = {}, tickAt = {};
  let changed = false; // did WE contribute anything the remote didn't have?
  for (const d of new Set([...Object.keys(lD), ...Object.keys(rD)])) {
    const lRec = lD[d], rRec = rD[d];
    const lB = (lRec && lRec.blocks) || {}, rB = (rRec && rRec.blocks) || {};
    const blocks = {}, ticks = {};
    for (const id of new Set([...Object.keys(lB), ...Object.keys(rB)])) {
      const lTs = (lT[d] || {})[id] || 0, rTs = (rT[d] || {})[id] || 0;
      const on = (lTs || rTs) ? (lTs >= rTs ? !!lB[id] : !!rB[id]) : (!!lB[id] || !!rB[id]);
      if (on) blocks[id] = true;
      if (on !== !!rB[id]) changed = true;
      const ts = Math.max(lTs, rTs);
      if (ts) ticks[id] = ts;
    }
    // off-day resolves by its "__off" stamp like a tick; with no stamp, a spent token wins (a fact).
    const lOff = !!(lRec && lRec.offDay), rOff = !!(rRec && rRec.offDay);
    const lOffTs = (lT[d] || {})["__off"] || 0, rOffTs = (rT[d] || {})["__off"] || 0;
    const offDay = (lOffTs || rOffTs) ? (lOffTs >= rOffTs ? lOff : rOff) : (lOff || rOff);
    if (lOffTs || rOffTs) ticks["__off"] = Math.max(lOffTs, rOffTs);
    days[d] = { blocks, offDay, note: (rRec && rRec.note) || (lRec && lRec.note) || "" };
    if (!rRec || offDay !== rOff) changed = true;
    if (Object.keys(ticks).length) tickAt[d] = ticks;
  }
  return { days, tickAt, changed };
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
