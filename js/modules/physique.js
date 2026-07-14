// physique.js — the Workout tab. Mirrors the user's Gymmy app 1:1 (same six
// workouts, proper exercise names) and adds a set logger for progressive overload.
import * as S from "../state.js";
import { esc, refresh, toast, buzz } from "../ui.js";
import { days, dayById, weekPlan, philosophy, forearmFix, gymmyApp } from "../data/workout_program.js";

// pick which workout the user is viewing (persisted lightly in the hash-less UI via a module var)
let viewDayId = null;

// Most recent prior log of an exercise (before today, else today's).
function lastLog(exId) {
  const logs = S.getState().workoutLogs;
  const keys = Object.keys(logs).sort().reverse();
  for (const k of keys) {
    const ex = logs[k].ex && logs[k].ex[exId];
    if (ex && ex.length) return { key: k, sets: ex };
  }
  return null;
}

function overloadHint(ex) {
  const last = lastLog(ex.id);
  if (!last) return { text: "First time — find a weight where the last set is tough but clean.", cls: "" };
  const summary = last.sets.map((s) => `${s.w}×${s.r}`).join(", ");
  const allHitTarget = ex.reps && last.sets.length >= ex.sets && last.sets.every((s) => Number(s.r) >= ex.reps);
  if (allHitTarget) return { text: `Last: ${summary}. You hit the target everywhere → add a little load today. 📈`, cls: "good" };
  return { text: `Last: ${summary}. Beat it by a rep or a small load.`, cls: "" };
}

function addSet(dayId, exId, w, r) {
  if (!w && !r) return;
  const key = S.todayKey();
  if (!S.getState().workoutLogs[key]) S.logEvent("workout", `started logging the ${dayId} workout`);
  S.update((st) => {
    if (!st.workoutLogs[key]) st.workoutLogs[key] = { dayId, ex: {} };
    st.workoutLogs[key].dayId = dayId;
    if (!st.workoutLogs[key].ex[exId]) st.workoutLogs[key].ex[exId] = [];
    st.workoutLogs[key].ex[exId].push({ w: Number(w) || 0, r: Number(r) || 0 });
  });
  S.addXP(3);
  buzz();
  refresh();
}
function clearSets(exId) {
  const key = S.todayKey();
  S.update((st) => { if (st.workoutLogs[key] && st.workoutLogs[key].ex) delete st.workoutLogs[key].ex[exId]; });
  refresh();
}

export default {
  id: "physique", label: "Workout",
  render(view) {
    const key = S.todayKey();
    const suggestedId = weekPlan[S.dow(key)];
    const activeId = viewDayId || suggestedId || "A";
    const day = dayById(activeId);
    const todayLog = S.getState().workoutLogs[key] || { ex: {} };
    const suggested = suggestedId ? dayById(suggestedId) : null;
    const onAndroid = /android/i.test(navigator.userAgent);

    view.innerHTML = `
      <div class="card tight" style="border-color:rgba(52,211,153,.35)">
        <div class="row between">
          <b>🔗 Connected to Gymmy</b>
          ${onAndroid ? `<a class="btn sm" href="${gymmyApp.intentUrl}">Open Gymmy ↗</a>` : ""}
        </div>
        <p class="small muted" style="margin:6px 0 0">This program lives inside Gymmy too — the built-in <b>Day A–E</b> templates (Plans tab) are these exact workouts, targets included. Tap one there to create it as a plan. Log sets in either app.</p>
      </div>

      <div class="card tight" style="border-color:rgba(251,113,133,.35)">
        <b>🏋️ Forearm fix — ${esc(forearmFix.title)}</b>
        <p class="small muted" style="margin:6px 0 8px">${esc(forearmFix.why)}</p>
        <ul class="list-plain small">${forearmFix.rules.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
      </div>

      <div class="section-title">Choose workout ${suggested ? `· today = ${esc(suggested.name)}` : "· today = rest"}</div>
      <div class="row wrap" style="gap:8px; margin-bottom:12px">
        ${days.map((d) => `<button class="btn sm ${d.id === activeId ? "primary" : ""}" data-day="${d.id}">${esc(d.name)}</button>`).join("")}
      </div>

      <div class="card">
        <div class="row between">
          <h2 style="margin:0">${esc(day.name)}</h2>
          <span class="pill accent">${esc(day.focus)}</span>
        </div>
        <p class="small muted" style="margin-top:6px">Warm-up: ${esc(day.warmup)}</p>
      </div>

      <div id="ex-list"></div>

      <div class="card tight">
        <div class="section-title">${esc(philosophy.title)}</div>
        <ul class="list-plain small muted">${philosophy.points.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>
      </div>`;

    view.querySelectorAll("[data-day]").forEach((b) =>
      b.addEventListener("click", () => { viewDayId = b.dataset.day; refresh(); }));

    const list = view.querySelector("#ex-list");
    list.innerHTML = day.exercises.map((ex) => {
      const hint = overloadHint(ex);
      const sets = (todayLog.ex && todayLog.ex[ex.id]) || [];
      return `
        <div class="card tight">
          <div class="row between">
            <div><b>${esc(ex.name)}</b> <span class="tag">${esc(ex.target)}</span></div>
            <span class="pill">${ex.reps ? `${ex.sets}×${ex.reps}` : `${ex.sets} sets`}</span>
          </div>
          ${ex.straps ? `<span class="pill warn" style="margin-top:6px">🎗️ straps on</span>` : ""}
          <p class="small muted" style="margin:8px 0 6px">💡 ${esc(ex.cue)}</p>
          <p class="small ${hint.cls === "good" ? "" : "dim"}" style="margin:0 0 6px; color:${hint.cls === "good" ? "var(--good)" : ""}">${esc(hint.text)}</p>
          <div class="row wrap" style="gap:6px; margin:8px 0">
            ${sets.map((s) => `<span class="pill accent">${s.w}kg × ${s.r}</span>`).join("") || `<span class="small dim">no sets logged yet</span>`}
          </div>
          <div class="row" style="gap:6px">
            <input type="number" placeholder="kg" id="w-${ex.id}">
            <input type="number" placeholder="reps" id="r-${ex.id}">
            <button class="btn sm primary" data-add="${ex.id}">＋ set</button>
            ${sets.length ? `<button class="btn sm ghost" data-clear="${ex.id}">clear</button>` : ""}
          </div>
        </div>`;
    }).join("");

    list.querySelectorAll("[data-add]").forEach((b) => b.addEventListener("click", () => {
      const id = b.dataset.add;
      addSet(activeId, id, view.querySelector(`#w-${id}`).value, view.querySelector(`#r-${id}`).value);
    }));
    list.querySelectorAll("[data-clear]").forEach((b) =>
      b.addEventListener("click", () => clearSets(b.dataset.clear)));
  }
};
