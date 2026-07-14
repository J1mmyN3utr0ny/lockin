// manager.js — the AI manager of the app. It watches what actually happened (the
// event log + today's numbers), and leaves short, concrete inform-notes in the 🔔
// panel. Small task → FAST model tier. It runs at most once per cooldown window,
// never blocks the UI, and fails silently — a manager that nags about itself is
// worse than no manager.
import * as S from "../state.js";
import { esc, openModal, refresh, toast } from "../ui.js";
import { gemini, hasKey, extractJSON } from "../ai.js";
import { buildDay, taskBlockIds, hasCustomOrder } from "../schedule.js";

const COOLDOWN_MS = 4 * 3600 * 1000; // at most one AI check every 4 hours

function ago(t) {
  const m = Math.max(1, Math.round((Date.now() - t) / 60000));
  if (m < 60) return `${m}m ago`;
  const h = Math.round(m / 60);
  return h < 24 ? `${h}h ago` : `${Math.round(h / 24)}d ago`;
}

function buildContext() {
  const st = S.getState();
  const key = S.todayKey();
  const day = buildDay(key);
  const rec = S.dayRec(key);
  const ids = taskBlockIds(key);
  const done = ids.filter((id) => rec.blocks[id]).length;
  const workout = st.workoutLogs[key];
  const sets = workout ? Object.values(workout.ex || {}).reduce((n, arr) => n + arr.length, 0) : 0;
  const events = (st.events || []).slice(-14).map((e) => `- ${ago(e.t)}: [${e.type}] ${e.text}`).join("\n") || "- none";
  const prior = (st.notifications || []).slice(0, 8).map((n) => `- ${n.text}`).join("\n") || "- none";
  return (
    `Date: ${S.prettyDate(key)} (${day.label}). PET exam in ${S.daysBetween(key, S.EXAM_DATE)} days; summer ends in ${S.daysToSummerEnd()} days.\n` +
    `Today: ${done}/${ids.length} blocks done. Day order ${hasCustomOrder(key) ? "was customized by the user" : "is the default"}.\n` +
    `Workout today: ${sets ? `${sets} sets logged` : "nothing logged yet"}. Streak: ${S.computeStreak()} days. Level: ${S.levelProgress(st.xp || 0).lvl}.\n` +
    `Off-days left: ${S.offDaysLeft()}. AI lessons created so far: ${(st.customLessons || []).length}.\n` +
    `Recent events:\n${events}\n` +
    `Notes you already sent (do NOT repeat these):\n${prior}`
  );
}

function validNotes(o) {
  const arr = o && o.notes;
  if (!Array.isArray(arr) || arr.length > 3) return null;
  const out = [];
  for (const n of arr) {
    if (!n || typeof n.text !== "string") return null;
    const text = n.text.trim();
    if (text.length < 8 || text.length > 200) return null;
    out.push({ text, icon: typeof n.icon === "string" && n.icon.trim() ? n.icon.trim().slice(0, 4) : "🤖" });
  }
  return out;
}

// One throttled manager pass. Returns how many new notes landed (0 on skip/failure).
export async function managerTick(force = false) {
  if (!hasKey() || !navigator.onLine) return 0;
  const st = S.getState();
  if (!force && Date.now() - ((st.manager || {}).lastRun || 0) < COOLDOWN_MS) return 0;
  S.update((s) => { s.manager = { lastRun: Date.now() }; }); // claim the slot before the call
  try {
    const raw = await gemini({
      tier: "fast",
      system:
        "You are the manager of 'LockIn', a summer study/training app for an 18-year-old aiming at the IDF GAMA " +
        "cyber program. From the status report, produce 0-3 SHORT inform-notifications the user should see now. " +
        "Rules: only observations grounded in the data (progress, patterns, risks, next-best-action); concrete and " +
        "specific, never generic motivation; no emoji inside the text; don't repeat notes already sent; if nothing " +
        "is worth saying reply with an empty list. Reply with ONLY this JSON: " +
        `{"notes":[{"icon":"one emoji","text":"under 140 chars"}]}`,
      messages: [{ role: "user", text: buildContext() }],
      temperature: 0.4
    });
    const notes = validNotes(extractJSON(raw));
    if (!notes || !notes.length) return 0;
    let added = 0;
    S.update((s) => {
      if (!Array.isArray(s.notifications)) s.notifications = [];
      const seen = new Set(s.notifications.map((n) => n.text));
      for (const n of notes) {
        if (seen.has(n.text)) continue;
        s.notifications.unshift({ id: `n${Date.now().toString(36)}${Math.floor(Math.random() * 1e4)}`, t: Date.now(), icon: n.icon, text: n.text, read: false });
        added++;
      }
      s.notifications = s.notifications.slice(0, 30);
    });
    return added;
  } catch (e) {
    return 0; // silent by design
  }
}

export function unreadCount() {
  return (S.getState().notifications || []).filter((n) => !n.read).length;
}

export function openNotifications() {
  const st = S.getState();
  const list = st.notifications || [];
  const m = openModal(`
    <div class="row between"><h2 style="margin:0">🔔 Manager notes</h2><button class="btn sm ghost" data-close>✕</button></div>
    <p class="small dim" style="margin:4px 0 10px">The AI manager watches your progress and leaves short notes here.</p>
    <div style="max-height:52vh; overflow:auto">
      ${list.length ? list.map((n) => `
        <div class="card tight" style="margin-bottom:8px; ${n.read ? "" : "border-color:rgba(79,140,255,.45)"}">
          <div class="row" style="gap:10px; align-items:flex-start">
            <div style="font-size:18px; line-height:1.3">${esc(n.icon || "🤖")}</div>
            <div style="flex:1; min-width:0">
              <div class="small">${esc(n.text)}</div>
              <div class="small dim" style="margin-top:2px">${ago(n.t)}</div>
            </div>
          </div>
        </div>`).join("")
      : `<p class="small muted center" style="padding:14px 0">Nothing yet — notes appear as the manager sees your day unfold.</p>`}
    </div>
    <div class="row" style="gap:8px; margin-top:12px">
      <button class="btn sm ghost" id="ntf-clear" style="flex:1" ${list.length ? "" : "disabled"}>Clear all</button>
      <button class="btn sm" id="ntf-now" style="flex:1">🤖 Check now</button>
      <button class="btn sm primary" data-close style="flex:1">Done</button>
    </div>`);
  // opening the panel marks everything read
  if (list.some((n) => !n.read)) S.update((s) => { (s.notifications || []).forEach((n) => { n.read = true; }); });
  m.querySelector("#ntf-clear").addEventListener("click", () => {
    S.update((s) => { s.notifications = []; });
    refresh(); openNotifications();
  });
  m.querySelector("#ntf-now").addEventListener("click", async () => {
    const btn = m.querySelector("#ntf-now");
    btn.disabled = true; btn.textContent = "checking…";
    const n = await managerTick(true);
    toast(n ? `🤖 ${n} new note${n > 1 ? "s" : ""}` : "Nothing new to report.");
    refresh(); openNotifications();
  });
}
