// today.js — the day's routine as checkable timeblocks. Free time is protected.
import * as S from "../state.js";
import { esc, barHTML, refresh, toast, confetti, buzz } from "../ui.js";
import { buildDay, taskBlockIds } from "../schedule.js";
import { openOffDayFlow, isOffDay } from "./offday.js";
import { startFocus } from "../focus.js";

const CAT = {
  sleep: { emoji: "🌙", color: "#8b5cf6" }, food: { emoji: "🍽️", color: "#f59e0b" },
  math: { emoji: "📐", color: "#22d3ee" }, cs: { emoji: "💻", color: "#4f8cff" },
  cyber: { emoji: "🛡️", color: "#34d399" }, pet: { emoji: "📝", color: "#f472b6" },
  gym: { emoji: "🏋️", color: "#fb7185" }, free: { emoji: "✨", color: "#f5c451" },
  wind: { emoji: "🌆", color: "#94a3b8" }, leet: { emoji: "🧩", color: "#a78bfa" },
  review: { emoji: "📋", color: "#22d3ee" }
};

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
    html += `<div class="wd ${isToday ? "today" : ""} ${isFuture ? "future" : ""} ${st}">
      <div class="d">${S.DAY_NAMES[i].slice(0, 3)}</div>
      <div class="n">${Number(k.slice(8))}</div>
      <div class="dot"></div>
    </div>`;
  }
  return html + `</div>`;
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

    view.innerHTML = `
      <div class="row between">
        <div>
          <h1>Today${hi}</h1>
          <p class="muted" style="margin:0">${esc(S.prettyDate(key))} · <span class="tag">${esc(day.label)}</span></p>
        </div>
        <div class="ring" style="--p:${Math.round(pct)}; position:relative"><span>${doneCount}/${taskIds.length}</span></div>
      </div>
      ${weekStrip(key)}
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

    const nowI = nowIndex(day.blocks);
    const focusable = new Set(["math", "cs", "cyber", "pet", "gym", "leet"]);
    const wrap = view.querySelector("#blocks");
    wrap.innerHTML = day.blocks.map((b, i) => {
      const done = !!rec.blocks[b.id];
      const c = CAT[b.cat] || CAT.free;
      const canFocus = !b.free && !done && focusable.has(b.cat);
      return `
        <div class="block ${done ? "done" : ""} ${b.free ? "free" : ""} ${i === nowI ? "now" : ""}" style="--cat:${c.color}" data-id="${b.id}">
          <div class="time">${esc(b.time)}</div>
          <div class="body">
            <div class="t">${esc(b.title)}</div>
            ${b.sub ? `<div class="s">${esc(b.sub)}</div>` : ""}
            <div class="row" style="gap:12px; margin-top:2px">
              ${b.link && !b.free ? `<a class="small" style="color:var(--accent)" href="${b.link}">Open →</a>` : ""}
              ${canFocus ? `<button class="btn sm" data-focus="${b.id}|${i}" style="padding:3px 9px">🔒 Focus</button>` : ""}
            </div>
          </div>
          ${b.free ? `<span class="cat emoji">${c.emoji}</span>`
            : `<div class="chk" data-chk="${b.id}" title="mark done">${done ? "✓" : ""}</div>`}
        </div>`;
    }).join("");

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
    view.querySelector("#take-off").addEventListener("click", () => openOffDayFlow(key));
  }
};
