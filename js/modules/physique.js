// physique.js — the Workout tab. GYMMY-FIRST by design: Gymmy is where sets get
// logged; this tab is the program's home base — what to do today, the overload
// targets to beat (computed from Gymmy-synced logs), the optional 6th-day chooser,
// and the AI session adjuster. No manual set entry here — finish in Gymmy and the
// session syncs over by itself.
import * as S from "../state.js";
import { esc, refresh, toast, openModal, closeModal } from "../ui.js";
import { gemini, hasKey, extractJSON } from "../ai.js";
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

// Most recent Gymmy-synced session (workoutLogs are written by the hub sync).
function lastGymmySession() {
  const logs = S.getState().workoutLogs;
  const keys = Object.keys(logs).sort().reverse();
  for (const k of keys) {
    const l = logs[k];
    if (l && l.ex && Object.keys(l.ex).length) {
      const sets = Object.values(l.ex).reduce((n, arr) => n + arr.length, 0);
      return { key: k, dayId: l.dayId, exercises: Object.keys(l.ex).length, sets, fromGymmy: !!l.gymmy };
    }
  }
  return null;
}

// ---- 🤖 adjust TODAY's session to the user's predicament ---------------------
// The program itself never changes — the AI may only bend today's session: drop
// exercises, trim sets/reps, reorder. Output is validated against the day's own
// exercise list; anything outside it is rejected wholesale.
function vTweak(o, day) {
  if (!o || typeof o !== "object") return "reply is not an object";
  if (typeof o.note !== "string" || o.note.trim().length < 3 || o.note.length > 140) return "note must be a 3-140 char string";
  const ids = new Set(day.exercises.map((e) => e.id));
  const list = o.exercises;
  if (!Array.isArray(list) || !list.length || list.length > day.exercises.length) return "exercises must be a non-empty array";
  const seen = new Set();
  for (const t of list) {
    if (!t || !ids.has(t.id)) return "every exercise id must come from today's workout";
    if (seen.has(t.id)) return "no duplicate exercises";
    seen.add(t.id);
    if (!Number.isInteger(t.sets) || t.sets < 1 || t.sets > 5) return "sets must be an integer 1-5";
    if (t.reps !== null && (!Number.isInteger(t.reps) || t.reps < 5 || t.reps > 25)) return "reps must be null or an integer 5-25";
  }
  return null;
}

function adjustWorkout(day, key) {
  if (!hasKey()) {
    openModal(`<h2>Connect Gemini first 🤖</h2>
      <p class="muted small">Paste your free key in <b>⚙ Settings → AI</b> (aistudio.google.com/apikey).</p>
      <button class="btn primary block" data-close style="margin-top:10px">Got it</button>`);
    return;
  }
  const m = openModal(`
    <h2 style="margin:0">🤖 Adjust today's workout</h2>
    <p class="small muted" style="margin:6px 0 10px">Tell it your predicament — it bends <b>${esc(day.name)}</b> for today only
    (drop/lighten/reorder exercises). The program itself stays untouched.</p>
    <textarea id="wt-in" rows="3" placeholder="e.g. slept 4 hours, low energy — make it lighter but keep the forearm work" style="width:100%"></textarea>
    <div id="wt-status" class="small" style="margin-top:6px"></div>
    <div class="row" style="gap:8px; margin-top:10px">
      <button class="btn ghost" data-close style="flex:1">Cancel</button>
      <button class="btn primary" id="wt-go" style="flex:1">Adjust</button>
    </div>`);
  const status = m.querySelector("#wt-status");
  m.querySelector("#wt-go").addEventListener("click", async () => {
    const text = m.querySelector("#wt-in").value.trim();
    if (text.length < 4) { toast("Describe how you're doing first 🙂"); return; }
    const go = m.querySelector("#wt-go");
    go.disabled = true;
    status.innerHTML = `<span class="dim">thinking…</span>`;
    const table = day.exercises.map((e) =>
      `id="${e.id}" · ${e.name} · ${e.sets}×${e.reps || "timed"} · ${e.target}`).join("\n");
    let prompt =
      `Today's planned workout (${day.name} — ${day.focus}):\n${table}\n\n` +
      `The user says: "${text}"\n\n` +
      `Adjust TODAY's session to fit. Reply with ONLY this JSON:\n` +
      `{"note": string (short summary of what you changed and why), "exercises":[{"id": one of the ids above, "sets": 1-5, "reps": 5-25 or null for timed holds}]}\n` +
      `Rules: only ids from the list, each at most once, in the order he should do them; lighter day = fewer sets/reps or ` +
      `fewer exercises (keep at least the first compound unless he's clearly wrecked); never add new exercises.`;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const raw = await gemini({
          tier: "smart",
          system: "You are the training assistant inside LockIn. The user follows a fixed 5+1-day program mirrored in his " +
            "Gymmy app; you may bend ONE day's session to his current state (sleep, soreness, time) without changing the " +
            "program. His standing rules: machines with built-in weight stacks and cables first, dumbbells and short/EZ " +
            "bars fine, NEVER free-barbell squats/deadlifts/lunges; CALVES are a growth emphasis (cut them last), " +
            "forearms are a growth focus, most slots run 2 hard sets. Preserve the session's main purpose when possible. " +
            "Reply with ONLY valid JSON matching the requested schema.",
          messages: [{ role: "user", text: prompt }], temperature: 0.3
        });
        const parsed = extractJSON(raw);
        const problem = vTweak(parsed, day);
        if (!problem) {
          S.update((st) => {
            if (!st.workoutTweaks) st.workoutTweaks = {};
            st.workoutTweaks[key] = { dayId: day.id, note: parsed.note.trim(), exercises: parsed.exercises };
            for (const k of Object.keys(st.workoutTweaks)) {
              if (S.daysBetween(k, key) > 3) delete st.workoutTweaks[k]; // stale tweaks die fast
            }
          });
          closeModal(); toast("Workout adjusted for today 🤖"); refresh();
          return;
        }
        if (attempt === 0) { prompt += `\n\nYour previous reply was rejected: ${problem}. Reply again with ONLY the corrected JSON.`; continue; }
        status.innerHTML = `<span style="color:var(--bad)">The AI couldn't produce a valid adjustment — nothing changed.</span>`;
      } catch (e) {
        status.innerHTML = `<span style="color:var(--bad)">${esc(e.message === "NO_KEY" ? "No API key set." : e.message)}</span>`;
        break;
      }
    }
    go.disabled = false;
  });
}

export default {
  id: "physique", label: "Workout",
  render(view) {
    const key = S.todayKey();
    const st = S.getState();
    const sixth = st.settings.sixthDay || "F";
    // Friday's suggestion honors the 6th-day choice (Day F light, or the chosen redo).
    const suggestedId = S.dow(key) === 5 ? sixth : weekPlan[S.dow(key)];
    const activeId = viewDayId || suggestedId || "A";
    const day = dayById(activeId);
    const todayLog = st.workoutLogs[key] || { ex: {} };
    const suggested = suggestedId ? dayById(suggestedId) : null;
    const onAndroid = /android/i.test(navigator.userAgent);
    const last = lastGymmySession();
    const gymTicked = !!(st.days[key] && st.days[key].blocks && st.days[key].blocks.gym);

    // Today's AI adjustment (if any) bends the session without touching the program.
    const tweak = (S.getState().workoutTweaks || {})[key];
    const tweakActive = !!(tweak && tweak.dayId === activeId);
    const exList = tweakActive
      ? tweak.exercises.map((t) => {
          const base = day.exercises.find((e) => e.id === t.id) || { id: t.id, name: t.id, target: "" };
          return { ...base, sets: t.sets, reps: t.reps };
        })
      : day.exercises;

    view.innerHTML = `
      <div class="card" style="border-color:rgba(52,211,153,.45); background:linear-gradient(180deg,rgba(52,211,153,.08),var(--card))">
        <div class="row between">
          <b>🏋️ Gymmy runs the gym</b>
          ${onAndroid ? `<button class="btn sm primary" id="open-gymmy">Open Gymmy ↗</button>` : `<span class="tag">on your phone</span>`}
        </div>
        <p class="small muted" style="margin:6px 0 8px">Sets are logged <b>in Gymmy</b> — start today's plan there (the Day A–F templates ARE this program). Finishing a session syncs it here and ticks today's gym block by itself. This tab is home base: what to do, and what to beat.</p>
        <div class="row wrap" style="gap:6px">
          ${gymTicked
            ? `<span class="pill good">✓ today's session synced from Gymmy</span>`
            : `<span class="pill">⏳ waiting for today's Gymmy session</span>`}
          ${last
            ? `<span class="pill accent">last: ${last.dayId ? "Day " + esc(last.dayId) : "workout"} · ${esc(S.prettyDate(last.key))} · ${last.sets} sets</span>`
            : `<span class="pill warn">no synced sessions yet — finish one in Gymmy</span>`}
        </div>
      </div>

      <div class="card tight" style="border-color:rgba(245,196,81,.4)">
        <b>➕ Optional 6th session — Friday midday</b>
        <p class="small muted" style="margin:6px 0 8px">For weeks that felt too light. Default is <b>Day F</b> — a light full-body pump — or pick a day to <b>redo</b> (whichever the week shortchanged). Entirely guilt-free to skip.</p>
        <div class="row wrap" style="gap:6px">
          ${["F", "A", "B", "C", "D", "E"].map((id) => `
            <button class="btn sm ${sixth === id ? "primary" : "ghost"}" data-sixth="${id}">${id === "F" ? "Day F · light (default)" : "Redo " + esc(dayById(id).name)}</button>`).join("")}
        </div>
      </div>

      <div class="card tight" style="border-color:rgba(251,113,133,.35)">
        <b>🏋️ Forearm fix — ${esc(forearmFix.title)}</b>
        <p class="small muted" style="margin:6px 0 8px">${esc(forearmFix.why)}</p>
        <ul class="list-plain small">${forearmFix.rules.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
      </div>

      <div class="section-title">Choose workout ${suggested ? `· today = ${esc(suggested.name)}${S.dow(key) === 5 ? " (optional)" : ""}` : "· today = rest"}</div>
      <div class="row wrap" style="gap:8px; margin-bottom:12px">
        ${days.map((d) => `<button class="btn sm ${d.id === activeId ? "primary" : ""}" data-day="${d.id}">${esc(d.name)}</button>`).join("")}
      </div>

      <div class="card">
        <div class="row between">
          <h2 style="margin:0">${esc(day.name)}</h2>
          <span class="pill accent">${esc(day.focus)}</span>
        </div>
        <p class="small muted" style="margin-top:6px">Warm-up: ${esc(day.warmup)}</p>
        ${activeId === suggestedId ? `<button class="btn sm ghost block" id="wt-adjust" style="margin-top:8px">🤖 Adjust today's workout (sleep, soreness, time…)</button>` : ""}
      </div>

      ${tweakActive ? `
      <div class="card tight" style="border-color:rgba(167,139,250,.45); background:linear-gradient(180deg,rgba(167,139,250,.1),var(--card))">
        <div class="row between" style="gap:10px">
          <div class="small"><b>🤖 Adjusted for today:</b> ${esc(tweak.note)}</div>
          <button class="btn sm ghost" id="wt-reset">↺ Full plan</button>
        </div>
      </div>` : ""}

      <div id="ex-list"></div>

      <div class="card tight">
        <div class="section-title">${esc(philosophy.title)}</div>
        <ul class="list-plain small muted">${philosophy.points.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>
      </div>`;

    view.querySelectorAll("[data-day]").forEach((b) =>
      b.addEventListener("click", () => { viewDayId = b.dataset.day; refresh(); }));

    const openGymmy = view.querySelector("#open-gymmy");
    if (openGymmy) openGymmy.addEventListener("click", () => {
      // A static <a href="intent://…"> is the textbook approach, but some Android
      // WebView/PWA shells resolve intent-scheme navigation more reliably when it's
      // triggered as an explicit location assignment INSIDE the click's user gesture,
      // rather than via the anchor's default-action navigation. Try that first.
      window.location.href = gymmyApp.intentUrl;
      // Diagnostic: if the OS actually launched Gymmy, this tab backgrounds (or the
      // page starts unloading) almost immediately. If we're still here and visible
      // after a beat, the intent was NOT picked up — tell the user plainly instead
      // of leaving a silent dead click.
      const t0 = Date.now();
      setTimeout(() => {
        if (document.visibilityState === "visible" && Date.now() - t0 < 3000) {
          toast("Gymmy didn't open — make sure it's installed on this device.");
        }
      }, 1200);
    });

    const adj = view.querySelector("#wt-adjust");
    if (adj) adj.addEventListener("click", () => adjustWorkout(day, key));
    const wtReset = view.querySelector("#wt-reset");
    if (wtReset) wtReset.addEventListener("click", () => {
      S.update((st) => { if (st.workoutTweaks) delete st.workoutTweaks[key]; });
      toast("Back to the full session."); refresh();
    });

    view.querySelectorAll("[data-sixth]").forEach((b) => b.addEventListener("click", () => {
      const id = b.dataset.sixth;
      S.update((s2) => { s2.settings.sixthDay = id; });
      S.logEvent("adjust", id === "F" ? "6th day set to the light Day F" : `6th day set to redo Day ${id}`);
      toast(id === "F" ? "Friday's optional session: Day F (light) ✓" : `Friday's optional session: redo Day ${id} ✓`);
      refresh();
    }));

    const list = view.querySelector("#ex-list");
    list.innerHTML = exList.map((ex) => {
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
            ${sets.map((s) => `<span class="pill accent">${s.w}kg × ${s.r}</span>`).join("") ||
              `<span class="small dim">no sets synced today — log them in Gymmy</span>`}
          </div>
        </div>`;
    }).join("");
  }
};
