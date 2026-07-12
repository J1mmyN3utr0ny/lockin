// ui.js — tiny DOM/render helpers shared by all modules.

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

// Ask the shell to re-render the current screen (scroll position preserved).
export function refresh() { window.dispatchEvent(new CustomEvent("lockin:refresh")); }

export function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

let toastTimer = null;
export function toast(msg, ms = 2200) {
  let t = $("#toast");
  if (!t) { t = document.createElement("div"); t.id = "toast"; t.className = "toast"; document.body.appendChild(t); }
  t.textContent = msg;
  requestAnimationFrame(() => t.classList.add("show"));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), ms);
}

// Tiny haptic tick on satisfying actions (supported on Android Chrome).
export function buzz(ms = 12) {
  try { if (navigator.vibrate) navigator.vibrate(ms); } catch (e) {}
}

// Celebration confetti — pure DOM, self-cleaning.
export function confetti(n = 30) {
  const colors = ["#4f8cff", "#22d3ee", "#34d399", "#f5c451", "#f472b6", "#fb7185", "#a78bfa"];
  const c = document.createElement("div");
  c.className = "confetti";
  for (let i = 0; i < n; i++) {
    const p = document.createElement("i");
    const s = 6 + Math.random() * 7;
    p.style.left = Math.random() * 100 + "vw";
    p.style.width = s + "px";
    p.style.height = s * 0.45 + "px";
    p.style.background = colors[i % colors.length];
    p.style.animationDelay = (Math.random() * 0.35) + "s";
    p.style.animationDuration = (1.5 + Math.random() * 1.3) + "s";
    c.appendChild(p);
  }
  document.body.appendChild(c);
  setTimeout(() => c.remove(), 3400);
}

// Bottom-sheet modal. Returns the modal element; closes on backdrop tap or [data-close].
export function openModal(innerHTML) {
  closeModal();
  const back = document.createElement("div");
  back.className = "modal-back";
  back.id = "modal-back";
  back.innerHTML = `<div class="modal">${innerHTML}</div>`;
  back.addEventListener("click", (e) => { if (e.target === back) closeModal(); });
  document.body.appendChild(back);
  back.querySelectorAll("[data-close]").forEach((b) => b.addEventListener("click", closeModal));
  return back.querySelector(".modal");
}
export function closeModal() {
  const b = $("#modal-back");
  if (b) b.remove();
}

// A styled confirm dialog. onYes runs when confirmed.
export function confirmModal({ title, body, yes = "Confirm", no = "Cancel", danger = false, onYes }) {
  const m = openModal(`
    <h2>${esc(title)}</h2>
    <p class="muted">${body}</p>
    <div class="row" style="margin-top:16px; gap:10px;">
      <button class="btn ghost" data-close style="flex:1">${esc(no)}</button>
      <button class="btn ${danger ? "bad" : "primary"}" id="cf-yes" style="flex:1">${esc(yes)}</button>
    </div>`);
  m.querySelector("#cf-yes").addEventListener("click", () => { closeModal(); onYes && onYes(); });
}

export function barHTML(pct, cls = "") {
  const p = Math.max(0, Math.min(100, Math.round(pct)));
  return `<div class="bar ${cls}"><i style="width:${p}%"></i></div>`;
}

export function ringHTML(pct, inner) {
  const p = Math.max(0, Math.min(100, Math.round(pct)));
  return `<div class="ring" style="--p:${p}; position:relative"><span>${inner ?? p + "%"}</span></div>`;
}

// 3D-flip flashcard. Caller attaches a click on #flash to toggle .flipped and reveal grading.
export function flashHTML({ front, back, sub = "", hint = "tap to reveal", backHint = "Did you get it?", rtl = false }) {
  return `
    <div class="flash3d" id="flash">
      <div class="flash-inner">
        <div class="face front">
          <div class="term ${rtl ? "rtl" : ""}" ${rtl ? 'style="direction:rtl"' : ""}>${front}</div>
          <div class="hint">${esc(hint)}</div>
        </div>
        <div class="face back">
          <div class="ans">${back}</div>
          ${sub ? `<div class="sub">${sub}</div>` : ""}
          <div class="hint">${esc(backHint)}</div>
        </div>
      </div>
    </div>`;
}

// Minimal SVG sparkline for trend data (e.g. bodyweight).
export function sparkSVG(vals, { w = 300, h = 64, color = "var(--accent-2)" } = {}) {
  if (!vals || vals.length < 2) return `<p class="small dim" style="margin:6px 0 0">Log at least two entries to see the trend.</p>`;
  const min = Math.min(...vals), max = Math.max(...vals), span = (max - min) || 1;
  const X = (i) => (i / (vals.length - 1)) * (w - 8) + 4;
  const Y = (v) => h - 8 - ((v - min) / span) * (h - 20);
  const pts = vals.map((v, i) => `${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(" ");
  const lastX = X(vals.length - 1), lastY = Y(vals[vals.length - 1]);
  return `
    <svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-hidden="true">
      <polyline class="area" points="4,${h - 4} ${pts} ${lastX.toFixed(1)},${h - 4}" fill="${color}" stroke="none"/>
      <polyline points="${pts}" stroke="${color}"/>
      <circle cx="${lastX.toFixed(1)}" cy="${lastY.toFixed(1)}" r="3.5" fill="${color}"/>
    </svg>`;
}

// Level chip helper for skill tracks (none..high scale).
export const LEVELS = ["none", "low", "low-med", "medium", "med-high", "high"];
export function levelPct(level) {
  const i = LEVELS.indexOf(level);
  return i < 0 ? 0 : Math.round((i / (LEVELS.length - 1)) * 100);
}
