// today.js — the day's routine as checkable timeblocks. Free time is protected.
// A block opens its tab with a full-card tap (no tiny links); ✏️ Adjust-day mode
// reorders the movable parts of the day — grouped blocks (travel→gym→travel) move
// as one, anchored blocks (wake, course, wind-down, sleep) stay put.
import * as S from "../state.js";
import { esc, barHTML, refresh, toast, confetti, buzz, openModal } from "../ui.js";
import { buildDay, taskBlockIds, unitize, moveUnit, resetDayOrder, hasCustomOrder } from "../schedule.js";
import { openOffDayFlow, isOffDay } from "./offday.js";
import { startFocus } from "../focus.js";

const CAT = {
  sleep: { emoji: "🌙", color: "#8b5cf6" }, food: { emoji: "🍽️", color: "#f59e0b" },
  math: { emoji: "📐", color: "#22d3ee" }, cs: { emoji: "💻", color: "#4f8cff" },
  cyber: { emoji: "🛡️", color: "#34d399" }, pet: { emoji: "📝", color: "#f472b6" },
  gym: { emoji: "🏋️", color: "#fb7185" }, free: { emoji: "✨", color: "#f5c451" },
  wind: { emoji: "🌆", color: "#94a3b8" }, leet: { emoji: "🧩", color: "#a78bfa" },
  review: { emoji: "📋", color: "#22d3ee" }, travel: { emoji: "🚗", color: "#94a3b8" }
};

let editMode = false; // ✏️ Adjust-day mode (session-only)

function toggle(dateKey, id, taskIds) {
  let nowOn = false;
  S.update((st) => {
    const rec = S.dayRec(dateKey);
    nowOn = !rec.blocks[id];
    rec.blocks[id] = nowOn;
  });
  S.addXP(nowOn ? 10 : -10);
  if (nowOn) {
    buzz();
    const rec = S.dayRec(dateKey);
    if (taskIds.every((tid) => rec.blocks[tid])) {
      confetti(36); buzz(30);
      toast("🔥 Full day cleared. That's how the summer gets won.");
    }
  }
  refresh();
}

// Minutes since midnight for "HH:MM"; null for non-times like "—".
function toMin(t) {
  const m = /^(\d{1,2}):(\d{2})$/.exec(t || "");
  return m ? Number(m[1]) * 60 + Number(m[2]) : null;
}

// Scheduled minutes of a block = gap to the next timed block (capped, sensible default).
function blockMinutes(blocks, i) {
  const start = toMin(blocks[i].time);
  if (start === null) return 30;
  for (let j = i + 1; j < blocks.length; j++) {
    const nxt = toMin(blocks[j].time);
    if (nxt !== null) return Math.max(10, Math.min(120, nxt - start));
  }
  return 45;
}

// Index of the block happening right now (last started, not done yet by time).
function nowIndex(blocks) {
  const n = S.now();
  const cur = n.getHours() * 60 + n.getMinutes();
  let idx = -1;
  blocks.forEach((b, i) => {
    const t = toMin(b.time);
    if (t !== null && t <= cur) idx = i;
  });
  return idx;
}

function dayStatus(k) {
  const s = S.getState();
  if (s.offDays.spent.includes(k)) return "off";
  const rec = s.days[k];
  const productive = rec && Object.values(rec.blocks || {}).filter(Boolean).length >= 3;
  return productive ? "done" : "none";
}

function weekStrip(todayKey) {
  const start = S.addDays(todayKey, -S.dow(todayKey)); // Sunday of this week
  let html = `<div class="week">`;
  for (let i = 0; i < 7; i++) {
    const k = S.addDays(start, i);
    const isToday = k === todayKey;
    const isFuture = S.daysBetween(todayKey, k) > 0;
    const st = dayStatus(k);
    html += `<div class="wd ${isToday ? "today" : ""} ${isFuture ? "future" : ""} ${st}" data-day="${k}" title="tap for this day's plan" style="cursor:pointer">
      <div class="d">${S.DAY_NAMES[i].slice(0, 3)}</div>
      <div class="n">${Number(k.slice(8))}</div>
      <div class="dot"></div>
    </div>`;
  }
  return html + `</div>`;
}

// Preview any day's plan in a modal, paging the whole summer (program start → Sep-6 deadline).
function previewDay(dateKey) {
  const d = buildDay(dateKey);
  const canPrev = S.daysBetween(S.PROGRAM_START, dateKey) > 0;
  const canNext = S.daysBetween(dateKey, S.SUMMER_END) > 0;
  const rows = d.blocks.map((b) => {
    const c = CAT[b.cat] || CAT.free;
    return `
      <div class="row" style="gap:10px; align-items:flex-start; padding:7px 0; border-bottom:1px solid var(--line)">
        <div style="width:4px; align-self:stretch; border-radius:3px; background:${c.color}; flex:none"></div>
        <div class="time" style="min-width:46px; color:var(--accent-2); font-weight:800; font-size:13px">${esc(b.time)}</div>
        <div style="flex:1; min-width:0">
          <div style="font-weight:700; font-size:13.5px">${esc(b.title)} ${b.fixed ? `<span class="dim" style="font-weight:400">🔒</span>` : ""}</div>
          ${b.sub ? `<div class="small muted">${esc(b.sub)}</div>` : ""}
        </div>
      </div>`;
  }).join("");
  const m = openModal(`
    <div class="row between" style="margin-bottom:8px">
      <button class="btn sm ghost" id="pv-prev" ${canPrev ? "" : "disabled"}>‹</button>
      <div class="center"><b>${esc(S.prettyDate(dateKey))}</b>
        <div style="margin-top:2px"><span class="tag">${esc(d.label)}</span></div></div>
      <button class="btn sm ghost" id="pv-next" ${canNext ? "" : "disabled"}>›</button>
    </div>
    <div style="max-height:58vh; overflow:auto">${rows}</div>
    <button class="btn block" data-close style="margin-top:12px">Close</button>`);
  if (canPrev) m.querySelector("#pv-prev").addEventListener("click", () => previewDay(S.addDays(dateKey, -1)));
  if (canNext) m.querySelector("#pv-next").addEventListener("click", () => previewDay(S.addDays(dateKey, 1)));
}

// ---- the two block renderings ------------------------------------------------

function blocksHTML(day, rec, nowI) {
  const focusable = new Set(["math", "cs", "cyber", "pet", "gym", "leet"]);
  return day.blocks.map((b, i) => {
    const done = !!rec.blocks[b.id];
    const c = CAT[b.cat] || CAT.free;
    const canFocus = !b.free && !done && focusable.has(b.cat);
    const tap = !!b.link && !b.free;
    return `
      <div class="block ${done ? "done" : ""} ${b.free ? "free" : ""} ${i === nowI ? "now" : ""} ${tap ? "tap" : ""}"
           style="--cat:${c.color}" data-id="${b.id}" ${tap ? `data-go="${b.link}" role="button" tabindex="0"` : ""}>
        <div class="time">${esc(b.time)}</div>
        <div class="body">
          <div class="t">${esc(b.title)}</div>
          ${b.sub ? `<div class="s">${esc(b.sub)}</div>` : ""}
          ${canFocus ? `<div class="row" style="margin-top:7px"><button class="btn sm" data-focus="${b.id}|${i}">🔒 Focus</button></div>` : ""}
        </div>
        ${tap ? `<span class="go">›</span>` : ""}
        ${b.free ? `<span class="cat emoji">${c.emoji}</span>`
          : `<div class="chk" data-chk="${b.id}" title="mark done">${done ? "✓" : ""}</div>`}
      </div>`;
  }).join("");
}

function editHTML(day, key) {
  const units = unitize(day.blocks);
  return `
    <div class="card tight" style="border-color:rgba(79,140,255,.4); background:linear-gradient(180deg,rgba(79,140,255,.08),var(--card))">
      <b>✏️ Adjust your day</b>
      <p class="small muted" style="margin:4px 0 0">Move blocks with the arrows — times re-flow on their own. 🔒 blocks are anchored and can't move; chained blocks (like the gym trip) move together.</p>
    </div>
    ${units.map((u, i) => {
      const canUp = !u.fixed && i > 0 && !units[i - 1].fixed;
      const canDn = !u.fixed && i < units.length - 1 && !units[i + 1].fixed;
      const c = CAT[u.blocks[0].cat] || CAT.free;
      return `
      <div class="unit ${u.fixed ? "fixed" : ""}" style="--cat:${c.color}">
        <div class="unit-rows">
          ${u.blocks.map((b) => `
            <div class="unit-row">
              <span class="time">${esc(b.time)}</span>
              <span class="ut">${esc(b.title)}</span>
            </div>`).join("")}
          ${u.blocks.length > 1 ? `<div class="small dim" style="margin-top:3px">⛓️ these move together</div>` : ""}
        </div>
        ${u.fixed
          ? `<div class="unit-lock" title="anchored — can't move">🔒</div>`
          : `<div class="unit-btns">
               <button class="ubtn" data-mv="${u.id}|-1" ${canUp ? "" : "disabled"} aria-label="move earlier">▲</button>
               <button class="ubtn" data-mv="${u.id}|1" ${canDn ? "" : "disabled"} aria-label="move later">▼</button>
             </div>`}
      </div>`;
    }).join("")}
    <div class="row" style="gap:8px; margin-top:12px">
      <button class="btn primary" id="edit-done" style="flex:1">✓ Done adjusting</button>
      ${hasCustomOrder(key) ? `<button class="btn ghost" id="edit-reset">Reset order</button>` : ""}
    </div>`;
}

export default {
  id: "today", label: "Today", ico: "📅",
  render(view) {
    const key = S.todayKey();
    const day = buildDay(key);
    const rec = S.dayRec(key);
    const off = isOffDay(key);
    const taskIds = taskBlockIds(key);
    const doneCount = taskIds.filter((id) => rec.blocks[id]).length;
    const pct = taskIds.length ? (doneCount / taskIds.length) * 100 : 0;
    const s = S.getState();
    const hi = s.profile.name ? `, ${esc(s.profile.name)}` : "";

    const resetBanner = day.taper.inReset ? `
      <div class="card tight" style="border-color:rgba(139,92,246,.4); background:linear-gradient(180deg,rgba(139,92,246,.12),var(--card))">
        <div class="row between">
          <div><b>🌙 Sleep reset — day ${day.taper.dayIndex + 1}</b>
            <div class="small muted">Aim to wake by <b>${day.taper.wake}</b> and be asleep by <b>${day.taper.sleep}</b> tonight. You're walking it back to 07:30.</div>
          </div>
        </div>
      </div>` : "";

    if (off) {
      view.innerHTML = `
        <h1>Off-day 🌙</h1>
        <p class="muted">${esc(S.prettyDate(key))}</p>
        <div class="card center" style="margin-top:12px">
          <div style="font-size:44px">😌</div>
          <h2>You chose to rest today.</h2>
          <p class="muted">No goals, no guilt. Your streak is protected. Come back tomorrow ready to Lock In.</p>
          <div class="pill gold" style="margin-top:6px">${S.offDaysLeft()} off-days left this summer</div>
          <div style="margin-top:14px"><button class="btn ghost" id="undo-off">Actually, cancel the off-day</button></div>
        </div>`;
      view.querySelector("#undo-off").addEventListener("click", () => openOffDayFlow(key));
      return;
    }

    const adjustable = unitize(day.blocks).some((u) => !u.fixed);
    view.innerHTML = `
      <div class="row between">
        <div>
          <h1>Today${hi}</h1>
          <p class="muted" style="margin:0">${esc(S.prettyDate(key))} · <span class="tag">${esc(day.label)}</span></p>
        </div>
        <div class="ring" style="--p:${Math.round(pct)}; position:relative"><span>${doneCount}/${taskIds.length}</span></div>
      </div>
      ${weekStrip(key)}
      <div class="row" style="gap:8px; margin:-2px 2px 12px">
        ${adjustable ? `<button class="btn sm ${editMode ? "primary" : "ghost"}" id="edit-day" style="flex:1">${editMode ? "✓ Done" : "✏️ Adjust day"}</button>` : ""}
        <button class="btn sm ghost" id="preview-day" style="flex:1">📅 Preview any day</button>
      </div>
      ${resetBanner}
      <div style="margin:6px 2px 12px">${barHTML(pct)}</div>
      <div id="blocks"></div>
      <div class="card tight" style="margin-top:6px">
        <div class="row between">
          <div><b>Need a real break?</b><div class="small muted">${S.offDaysLeft()} off-days left all summer</div></div>
          <button class="btn sm" id="take-off">Take an off-day</button>
        </div>
      </div>
      ${pct >= 100 ? `<div class="card center" style="border-color:rgba(52,211,153,.4)"><b class="emoji">🔥</b> Full day cleared. That's how the summer gets won.</div>` : ""}`;

    const wrap = view.querySelector("#blocks");

    if (editMode) {
      wrap.innerHTML = editHTML(day, key);
      wrap.querySelectorAll("[data-mv]").forEach((b) => b.addEventListener("click", () => {
        const [id, d] = b.dataset.mv.split("|");
        if (moveUnit(key, id, Number(d))) { buzz(); refresh(); }
      }));
      wrap.querySelector("#edit-done").addEventListener("click", () => { editMode = false; refresh(); });
      const rst = wrap.querySelector("#edit-reset");
      if (rst) rst.addEventListener("click", () => { resetDayOrder(key); toast("Back to the default plan."); refresh(); });
    } else {
      const nowI = nowIndex(day.blocks);
      wrap.innerHTML = blocksHTML(day, rec, nowI);

      wrap.querySelectorAll("[data-go]").forEach((el) => {
        el.addEventListener("click", () => { location.hash = el.dataset.go; });
        el.addEventListener("keydown", (e) => { if (e.key === "Enter") location.hash = el.dataset.go; });
      });
      wrap.querySelectorAll("[data-chk]").forEach((el) =>
        el.addEventListener("click", (e) => { e.stopPropagation(); toggle(key, el.dataset.chk, taskIds); }));
      wrap.querySelectorAll("[data-focus]").forEach((el) =>
        el.addEventListener("click", (e) => {
          e.stopPropagation();
          const [id, iStr] = el.dataset.focus.split("|");
          const i = Number(iStr);
          const b = day.blocks[i];
          startFocus({
            title: b.title,
            minutes: blockMinutes(day.blocks, i),
            labGate: b.cat === "cyber" || b.cat === "leet",
            leetOnly: b.cat === "leet",
            onComplete: ({ escapes }) => {
              if (!S.dayRec(key).blocks[id]) toggle(key, id, taskIds);
              toast(escapes === 0 ? "Locked in the whole time. 🔒 That's the standard." : "Event done — fewer escapes next time.");
            }
          });
        }));
    }

    const editBtn = view.querySelector("#edit-day");
    if (editBtn) editBtn.addEventListener("click", () => { editMode = !editMode; refresh(); });
    view.querySelector("#take-off").addEventListener("click", () => openOffDayFlow(key));
    view.querySelectorAll("[data-day]").forEach((el) =>
      el.addEventListener("click", () => previewDay(el.dataset.day)));
    view.querySelector("#preview-day").addEventListener("click", () => previewDay(key));
  }
};
