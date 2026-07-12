// focus.js — Focus Lock. A web app can't disable the whole phone, so this does the strongest
// thing a PWA can: it takes over the screen fullscreen, keeps the display awake (Wake Lock),
// counts every time you leave, and won't let go of the app until you finish the event.
import { esc, confetti, buzz, confirmModal } from "./ui.js";
import { labConfigured, fetchStatus } from "./lab.js";

let active = null;

export function isFocusing() { return !!active; }

export function startFocus({ title, minutes = 45, onComplete, labGate = false, leetOnly = false }) {
  if (active) return;
  const gated = labGate && labConfigured();
  const total = Math.max(1, minutes) * 60;
  let remaining = total;
  let escapes = 0;
  let wakeLock = null;
  let tick = null;

  const el = document.createElement("div");
  el.className = "focus-lock";
  el.innerHTML = `
    <div class="fl-tag"><span class="pulse"></span>Focus Lock${gated ? " · Lab-gated 🧪" : ""}</div>
    <h2>${esc(title)}</h2>
    <div class="fl-sub">${gated
      ? "Locked until you finish your work in LockIn Lab on your PC. The phone unlocks itself the moment the Lab records a completed task."
      : "Stay here until it's done. The screen stays on and every time you leave the app is counted."}</div>
    <div class="fl-clock" id="fl-clock">--:--</div>
    <div class="bar" style="width:min(340px,80vw)"><i id="fl-bar" style="width:0%"></i></div>
    <div class="fl-escapes" id="fl-esc"></div>
    ${gated ? `<div class="fl-lab" id="fl-lab">🧪 Connecting to the Lab…</div>` : ""}
    <div class="fl-refs hidden" id="fl-refs">
      <button class="btn sm" id="fl-refull">Return to fullscreen</button>
    </div>
    <div class="fl-actions">
      <button class="btn ghost" id="fl-break">Break focus</button>
      ${gated ? `<button class="btn good hidden" id="fl-done">Unlock manually</button>`
              : `<button class="btn good" id="fl-done">✓ Completed</button>`}
    </div>
    <div class="fl-note">${gated
      ? "Do the work in the Lab — this releases automatically. Can't reach the Lab? A manual unlock appears after a few tries."
      : "A website can't lock the whole phone — but leaving here is deliberate and it's all counted. Own it."}</div>`;
  document.body.appendChild(el);

  const clock = el.querySelector("#fl-clock");
  const bar = el.querySelector("#fl-bar");
  const escEl = el.querySelector("#fl-esc");

  function fmt(s) {
    const m = Math.floor(Math.abs(s) / 60), ss = Math.abs(s) % 60;
    return `${s < 0 ? "+" : ""}${String(m).padStart(2, "0")}:${String(ss).padStart(2, "0")}`;
  }
  function render() {
    clock.textContent = fmt(remaining);
    bar.style.width = Math.min(100, ((total - Math.max(remaining, 0)) / total) * 100) + "%";
    if (remaining <= 0 && !el.classList.contains("over")) {
      el.classList.add("over");
      confetti(24); buzz(30);
      escEl.innerHTML = `<span style="color:var(--good)">Time's up — finish strong and tap Completed.</span>`;
    }
  }

  async function acquireWake() {
    try { if ("wakeLock" in navigator) wakeLock = await navigator.wakeLock.request("screen"); } catch (e) {}
  }
  async function goFullscreen() {
    try { if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen(); } catch (e) {}
  }

  function onVisible() {
    if (document.hidden) {
      escapes++;
    } else {
      acquireWake();
      if (escapes > 0) escEl.innerHTML = `You left focus <b>${escapes}</b> time${escapes > 1 ? "s" : ""} — get back in. 👊`;
    }
  }
  function onFsChange() {
    const out = !document.fullscreenElement;
    el.querySelector("#fl-refs").classList.toggle("hidden", !out);
  }

  function cleanup() {
    clearInterval(tick);
    clearInterval(poll);
    document.removeEventListener("visibilitychange", onVisible);
    document.removeEventListener("fullscreenchange", onFsChange);
    try { if (wakeLock) wakeLock.release(); } catch (e) {}
    if (document.fullscreenElement) { try { document.exitFullscreen(); } catch (e) {} }
    el.remove();
    active = null;
  }

  function finish() {
    const elapsed = Math.round((total - remaining) / 60);
    cleanup();
    buzz(20);
    onComplete && onComplete({ elapsedMin: Math.max(0, elapsed), escapes });
  }

  // ---- Lab-gated polling: unlock when the Lab records finished work ----
  let poll = null, baseline = null, fails = 0;
  const labEl = el.querySelector("#fl-lab");
  async function checkLab() {
    try {
      const s = await fetchStatus(4000);
      fails = 0;
      if (baseline === null) {
        baseline = leetOnly ? (s.leetToday && s.leetToday.solved ? 1 : 0) : (s.completedTodayCount || 0);
        // Already done the work before starting? Nothing to gate — release now.
        if (leetOnly && baseline === 1) {
          labEl.innerHTML = `<span style="color:var(--good)">✓ Today's LeetCode is already solved — unlocking!</span>`;
          confetti(30); buzz(30); setTimeout(finish, 700);
          return;
        }
        labEl.innerHTML = leetOnly
          ? "🧪 Solve today's LeetCode in the Lab to unlock."
          : `🧪 Finish a lesson or problem in the Lab to unlock.`;
        return;
      }
      const now = leetOnly ? (s.leetToday && s.leetToday.solved ? 1 : 0) : (s.completedTodayCount || 0);
      if (now > baseline) {
        labEl.innerHTML = `<span style="color:var(--good)">✓ Lab work detected — unlocking!</span>`;
        confetti(30); buzz(30);
        setTimeout(finish, 700);
      } else {
        labEl.innerHTML = leetOnly
          ? `🧪 Waiting… today's problem: <b>${esc((s.leetToday && s.leetToday.title) || "?")}</b> (${esc((s.leetToday && s.leetToday.difficulty) || "")})`
          : `🧪 Waiting for a completed task in the Lab…`;
      }
    } catch (e) {
      fails++;
      labEl.innerHTML = `<span style="color:var(--warn)">🧪 ${esc(e.message)}</span>`;
      if (fails >= 3) el.querySelector("#fl-done").classList.remove("hidden");
    }
  }

  el.querySelector("#fl-done").addEventListener("click", finish);
  el.querySelector("#fl-break").addEventListener("click", () => {
    confirmModal({
      title: "Break focus early?", danger: true, yes: "Break it", no: "Keep going",
      body: "The event isn't marked done and this counts as leaving the task. Sure?",
      onYes: () => cleanup()
    });
  });
  el.querySelector("#fl-refull").addEventListener("click", goFullscreen);

  active = { cleanup };
  document.addEventListener("visibilitychange", onVisible);
  document.addEventListener("fullscreenchange", onFsChange);
  acquireWake();
  goFullscreen();
  render();
  tick = setInterval(() => { remaining--; render(); }, 1000);
  if (gated) { checkLab(); poll = setInterval(checkLab, 5000); }
}
