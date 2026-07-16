// today.js — the day's routine as checkable timeblocks. Free time is protected.
// A block opens its tab with a full-card tap; the ⣿ holding bar on the left of each
// movable block DRAGS it to a new slot (chained blocks like the gym trip drag as one,
// and nothing can cross a fixed anchor — times re-flow automatically). The 🤖 button
// expands a block into a concrete mini-plan, and "Plan my day" lets the AI reorder
// the whole day around your constraints.
import * as S from "../state.js";
import { esc, barHTML, refresh, toast, confetti, buzz, openModal, closeModal } from "../ui.js";
import { buildDay, taskBlockIds, unitize, placeUnit, applyAiPlan, resetDayOrder, hasCustomOrder, debtSummary } from "../schedule.js";
import { gemini, hasKey, mdLite, extractJSON } from "../ai.js";
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

// Tick/untick one block of `dateKey`. Works for any day that has happened, so a
// forgotten tick can be fixed later and still count. `celebrate` is off when the day
// isn't today — back-filling Tuesday shouldn't throw confetti at you on Thursday.
let lastTick = null; // { id, t } — so ONLY the newest checkmark plays the pop animation

function justTicked(id) { return !!(lastTick && lastTick.id === id && Date.now() - lastTick.t < 800); }

function toggle(dateKey, id, taskIds, celebrate = true) {
  let nowOn = false;
  S.update(() => {
    const rec = S.dayRec(dateKey);
    nowOn = !rec.blocks[id];
    rec.blocks[id] = nowOn;
  });
  S.addXP(nowOn ? 10 : -10);
  lastTick = nowOn ? { id, t: Date.now() } : null;
  if (nowOn) {
    buzz();
    const rec = S.dayRec(dateKey);
    if (taskIds.every((tid) => rec.blocks[tid])) {
      if (celebrate) {
        confetti(36); buzz(30);
        toast("🔥 Full day cleared. That's how the summer gets won.");
        S.logEvent("fullclear", "cleared every block of the day");
      } else {
        toast(`✓ ${S.prettyDate(dateKey)} logged as fully cleared.`);
      }
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

const sundayOf = (k) => S.addDays(k, -S.dow(k));

// The week strip now scrolls through EVERY remaining week of the summer. Days beyond
// the current week are visible but their day-plan details stay blank until their week
// arrives (see previewDay).
function weekStrip(todayKey) {
  const start = sundayOf(todayKey);
  const total = Math.max(7, S.daysBetween(start, S.SUMMER_END) + 1);
  let html = `<div class="week scrollx">`;
  let lastMonth = null;
  for (let i = 0; i < total; i++) {
    const k = S.addDays(start, i);
    const month = k.slice(0, 7);
    if (lastMonth !== null && month !== lastMonth) {
      html += `<div class="wmon">${new Date(k + "T12:00:00").toLocaleDateString("en-GB", { month: "short" })}</div>`;
    }
    lastMonth = month;
    const isToday = k === todayKey;
    const isFuture = S.daysBetween(todayKey, k) > 0;
    const farWeek = S.daysBetween(start, k) >= 7;
    const st = dayStatus(k);
    html += `<div class="wd ${isToday ? "today" : ""} ${isFuture ? "future" : ""} ${farWeek ? "far" : ""} ${st}" data-day="${k}" title="tap for this day's plan" style="cursor:pointer">
      <div class="d">${S.DAY_NAMES[S.dow(k)].slice(0, 3)}</div>
      <div class="n">${Number(k.slice(8))}</div>
      <div class="dot"></div>
    </div>`;
  }
  return html + `</div>`;
}

// Open any day's plan in a modal, paging the whole summer. Days that have already
// happened (and today) are EDITABLE — tick blocks you forgot to mark at the time, and
// the day's record, XP and streak update exactly as if you'd ticked them live. A day
// that hasn't happened yet stays read-only; ticking the future isn't progress. Days
// beyond the current week show only times + titles until their week arrives.
const _retroLogged = new Set(); // one manager event per back-filled day, not per tap

function previewDay(dateKey) {
  const d = buildDay(dateKey);
  const todayKey = S.todayKey();
  const revealed = S.daysBetween(sundayOf(todayKey), sundayOf(dateKey)) <= 0;
  const started = S.daysBetween(S.PROGRAM_START, dateKey) >= 0;
  const happened = S.daysBetween(dateKey, todayKey) >= 0;
  const isToday = dateKey === todayKey;
  const off = S.getState().offDays.spent.includes(dateKey);
  const editable = started && happened && !off;
  const canPrev = S.daysBetween(S.PROGRAM_START, dateKey) > 0;
  const canNext = S.daysBetween(dateKey, S.SUMMER_END) > 0;
  const taskIds = taskBlockIds(dateKey);

  function rowsHTML() {
    const rec = S.getState().days[dateKey] || { blocks: {} };
    return d.blocks.map((b) => {
      const c = CAT[b.cat] || CAT.free;
      const done = !!(rec.blocks || {})[b.id];
      return `
        <div class="pvrow ${done ? "done" : ""}">
          <div class="pvbar" style="background:${c.color}"></div>
          <div class="pvtime">${esc(b.time)}</div>
          <div class="pvbody">
            <div class="pvt">${esc(b.title)} ${b.fixed ? `<span class="dim" style="font-weight:400">🔒</span>` : ""}</div>
            ${revealed && b.sub ? `<div class="small muted">${esc(b.sub)}</div>` : ""}
          </div>
          ${b.free
            ? `<span class="emoji" style="flex:none">${c.emoji}</span>`
            : editable
              ? `<div class="chk ${justTicked(b.id) ? "pop" : ""}" data-pvchk="${b.id}" title="mark done">${done ? "✓" : ""}</div>`
              : `<span class="pvghost">${done ? "✓" : ""}</span>`}
        </div>`;
    }).join("");
  }
  function headHTML() {
    const rec = S.getState().days[dateKey] || { blocks: {} };
    const n = taskIds.filter((id) => (rec.blocks || {})[id]).length;
    return `${n}/${taskIds.length}`;
  }

  const m = openModal(`
    <div class="row between" style="margin-bottom:8px">
      <button class="btn sm ghost" id="pv-prev" ${canPrev ? "" : "disabled"}>‹</button>
      <div class="center"><b>${esc(S.prettyDate(dateKey))}</b>
        <div style="margin-top:2px"><span class="tag">${esc(d.label)}</span>
          ${taskIds.length ? `<span class="tag" id="pv-count">${headHTML()}</span>` : ""}</div></div>
      <button class="btn sm ghost" id="pv-next" ${canNext ? "" : "disabled"}>›</button>
    </div>
    ${off ? `<p class="small dim" style="margin:0 0 6px">🌙 You spent an off-day here — nothing to tick.</p>`
      : editable ? `<p class="small dim" style="margin:0 0 6px">${isToday ? "✅ Tick anything you've done today." : "✅ Forgot to tick something? Fix it here — XP and your streak update too."}</p>`
      : !started ? `<p class="small dim" style="margin:0 0 6px">Before the program started.</p>`
      : `<p class="small dim" style="margin:0 0 6px">🔭 Hasn't happened yet${revealed ? "" : " — the details fill in when its week arrives"}.</p>`}
    <div style="max-height:58vh; overflow:auto" id="pv-rows">${rowsHTML()}</div>
    <button class="btn block" data-close style="margin-top:12px">Close</button>`);

  function paint() {
    m.querySelector("#pv-rows").innerHTML = rowsHTML();
    const cnt = m.querySelector("#pv-count");
    if (cnt) cnt.textContent = headHTML();
    bind();
  }
  function bind() {
    m.querySelectorAll("[data-pvchk]").forEach((el) => el.addEventListener("click", () => {
      toggle(dateKey, el.dataset.pvchk, taskIds, isToday);
      if (!isToday && !_retroLogged.has(dateKey)) {
        _retroLogged.add(dateKey);
        S.logEvent("retro", `back-filled blocks for ${S.prettyDate(dateKey)}`);
      }
      paint();
    }));
  }
  bind();
  if (canPrev) m.querySelector("#pv-prev").addEventListener("click", () => previewDay(S.addDays(dateKey, -1)));
  if (canNext) m.querySelector("#pv-next").addEventListener("click", () => previewDay(S.addDays(dateKey, 1)));
}

// ---- AI: expand a block into a concrete mini-plan ------------------------------

const expandCache = {}; // `${dateKey}:${blockId}` -> reply text (session only)

function keyGate() {
  openModal(`
    <h2>Connect Gemini first 🤖</h2>
    <p class="muted small">This uses your free Gemini key — paste it once in <b>⚙ Settings → AI</b> (aistudio.google.com/apikey).</p>
    <button class="btn primary block" data-close style="margin-top:10px">Got it</button>`);
}

async function expandBlock(day, b, i, dateKey) {
  if (!hasKey()) { keyGate(); return; }
  const cacheKey = `${dateKey}:${b.id}`;
  const m = openModal(`
    <div class="row between"><h2 style="margin:0">🤖 ${esc(b.title)}</h2><button class="btn sm ghost" data-close>✕</button></div>
    <p class="small dim" style="margin:4px 0 8px">${esc(b.time)} · ~${blockMinutes(day.blocks, i)} min</p>
    <div id="xp-body" class="small"><span class="dim">building your game plan…</span></div>
    <div class="row" style="gap:8px; margin-top:12px">
      <button class="btn sm ghost" id="xp-redo" style="flex:1" disabled>↻ Regenerate</button>
      <button class="btn sm primary" data-close style="flex:1">Done</button>
    </div>`);
  const body = m.querySelector("#xp-body");
  const redo = m.querySelector("#xp-redo");
  async function run(force) {
    if (!force && expandCache[cacheKey]) { body.innerHTML = mdLite(expandCache[cacheKey]); redo.disabled = false; return; }
    body.innerHTML = `<span class="dim">building your game plan…</span>`;
    redo.disabled = true;
    try {
      const daysToExam = S.daysBetween(S.todayKey(), S.EXAM_DATE);
      const reply = await gemini({
        tier: "fast",
        system: "You are the planning assistant inside LockIn, a summer study/training app for an 18-year-old " +
          "preparing for the IDF GAMA cyber program and the PET exam. Expand ONE schedule block into a concrete, " +
          "numbered mini-plan (3-6 steps) for this exact session. Be specific — real actions, real commands or " +
          "exercise names where relevant, minutes per step. No fluff, no motivation talk. Under 160 words.",
        messages: [{ role: "user", text:
          `Block: "${b.title}" at ${b.time} (~${blockMinutes(day.blocks, i)} min). Details: ${b.sub || "none"}. ` +
          `Day type: ${day.label}. PET exam in ${daysToExam} days. Give the mini-plan.` }],
        temperature: 0.5
      });
      expandCache[cacheKey] = reply;
      if (body.isConnected) body.innerHTML = mdLite(reply);
    } catch (e) {
      if (body.isConnected) body.innerHTML = `<span style="color:var(--bad)">${esc(e.message === "NO_KEY" ? "No API key set." : e.message)}</span>`;
    } finally { if (redo.isConnected) redo.disabled = false; }
  }
  redo.addEventListener("click", () => run(true));
  run(false);
}

// ---- AI: plan my day (reorder movable units from free-text constraints) --------

function dayPromptLines(dateKey) {
  const units = unitize(buildDay(dateKey).blocks);
  const lines = units.map((u) => {
    const first = u.blocks[0], last = u.blocks[u.blocks.length - 1];
    const label = u.blocks.map((b) => b.title).join(" + ");
    if (u.hard) return `HARD ANCHOR (never moves) at ${first.time}: ${label}`;
    if (u.fixed) return `anchor (moves only with "shift") at ${first.time}: ${label}`;
    return `id="${u.id}" (${first.time}–${last.time}): ${label}`;
  }).join("\n");
  const movable = units.filter((u) => !u.fixed).map((u) => u.id);
  return { lines, movable };
}

function aiPlanDay(dateKey) {
  if (!hasKey()) { keyGate(); return; }
  const m = openModal(`
    <h2 style="margin:0">🤖 Plan my days</h2>
    <p class="small muted" style="margin:6px 0 10px">Tell it what's going on in plain words. It can reorder blocks, <b>skip</b> ones
    that don't fit, <b>shift a whole day</b> (late hangout tonight → tomorrow starts later), and adjust tomorrow along with today.
    The PET course and family dinner never move.</p>
    <textarea id="plan-in" rows="3" placeholder="e.g. hanging out till late tonight — push tomorrow an hour; skip the snack; heavy thinking before noon" style="width:100%"></textarea>
    <div id="plan-status" class="small" style="margin-top:6px"></div>
    <div class="row" style="gap:8px; margin-top:10px">
      <button class="btn ghost" data-close style="flex:1">Cancel</button>
      <button class="btn primary" id="plan-go" style="flex:1">Re-plan</button>
    </div>`);
  const status = m.querySelector("#plan-status");
  m.querySelector("#plan-go").addEventListener("click", async () => {
    const constraints = m.querySelector("#plan-in").value.trim();
    if (constraints.length < 4) { toast("Describe your constraints first 🙂"); return; }
    const go = m.querySelector("#plan-go");
    go.disabled = true;
    status.innerHTML = `<span class="dim">thinking…</span>`;
    const tomorrow = S.addDays(dateKey, 1);
    const dToday = dayPromptLines(dateKey);
    const dTmrw = dayPromptLines(tomorrow);
    const debts = debtSummary();
    let prompt =
      `TODAY ${dateKey}:\n${dToday.lines}\n(movable ids: ${dToday.movable.join(", ")})\n\n` +
      `TOMORROW ${tomorrow}:\n${dTmrw.lines}\n(movable ids: ${dTmrw.movable.join(", ")})\n\n` +
      (debts.length ? `CATCH-UP DEBT (study blocks missed in the last 7 days): ${debts.join(", ")}. ` +
        `When re-planning, protect these categories and skip them only as a last resort — cyber debt first.\n\n` : "") +
      `The user says: "${constraints}"\n\n` +
      `Per day you may: reorder movable units between their anchors; "skip" movable units that shouldn't happen; ` +
      `"shift" the WHOLE day by minutes (-120..180) — wake, wind-down and sleep move with it, HARD anchors don't ` +
      `(late night → positive shift the NEXT day so he still gets ~8h sleep).\n` +
      `Reply with ONLY this JSON, including ONLY the days you change:\n` +
      `{"days":[{"date":"YYYY-MM-DD","shift":0,"skip":[],"order":[every remaining movable id exactly once, in day order]}]}`;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const raw = await gemini({
          tier: "fast",
          system: "You manage an 18-year-old student's daily schedule inside LockIn. Protect sleep (~8h) and the " +
            "protected free time; the gym is best ~20:00. PET context: the course runs Monday & Thursday 09:00-14:00 " +
            "(a hard anchor), the exam is Sep 2-3, and practice volume should GROW as it approaches — cut PET blocks last. " +
            "Reply with ONLY valid JSON matching the requested schema.",
          messages: [{ role: "user", text: prompt }], temperature: 0.2
        });
        const parsed = extractJSON(raw);
        if (applyAiPlan(parsed && parsed.days)) {
          S.logEvent("adjust", "AI re-planned the day(s) around user constraints");
          closeModal(); toast("Re-planned 🤖 — check today and tomorrow."); refresh();
          return;
        }
        if (attempt === 0) { prompt += `\n\nYour previous plan was rejected (dates must be today/tomorrow; "order" must contain every remaining movable id exactly once; shift -120..180). Reply again with ONLY the corrected JSON.`; continue; }
        status.innerHTML = `<span style="color:var(--bad)">The AI couldn't produce a valid plan — nothing was changed.</span>`;
      } catch (e) {
        status.innerHTML = `<span style="color:var(--bad)">${esc(e.message === "NO_KEY" ? "No API key set." : e.message)}</span>`;
        break;
      }
    }
    go.disabled = false;
  });
}

// ---- rendering ------------------------------------------------------------------

function blocksHTML(day, rec, nowI, unitByBlock) {
  const focusable = new Set(["math", "cs", "cyber", "pet", "gym", "leet"]);
  const expandable = new Set(["math", "cs", "cyber", "pet", "gym", "leet", "review"]);
  return day.blocks.map((b, i) => {
    const done = !!rec.blocks[b.id];
    const c = CAT[b.cat] || CAT.free;
    const u = unitByBlock[i]; // { id, fixed, first, last }
    const canFocus = !b.free && !done && focusable.has(b.cat);
    const canExpand = !b.free && expandable.has(b.cat);
    const tap = !!b.link && !b.free;
    return `
      <div class="block ${done ? "done" : ""} ${b.free ? "free" : ""} ${i === nowI ? "now" : ""} ${tap ? "tap" : ""} ${u.fixed ? "" : "movable"} ${u.chained ? "chained" : ""} ${u.first ? "u-first" : ""} ${u.last ? "u-last" : ""}"
           style="--cat:${c.color}" data-id="${b.id}" data-unit="${u.id}" ${tap ? `data-go="${b.link}" role="button" tabindex="0"` : ""}>
        ${u.fixed
          ? `<div class="grip locked" title="anchored — can't move">🔒</div>`
          : `<div class="grip" data-grip="${u.id}" title="hold to drag"><span></span><span></span><span></span></div>`}
        <div class="time">${esc(b.time)}</div>
        <div class="body">
          <div class="t">${esc(b.title)}</div>
          ${b.sub ? `<div class="s">${esc(b.sub)}</div>` : ""}
          ${(canFocus || canExpand) ? `<div class="row" style="gap:6px; margin-top:7px">
            ${canFocus ? `<button class="btn sm" data-focus="${b.id}|${i}">🔒 Focus</button>` : ""}
            ${canExpand ? `<button class="btn sm ghost" data-expand="${b.id}|${i}">🤖 Expand</button>` : ""}
          </div>` : ""}
        </div>
        ${tap ? `<span class="go">›</span>` : ""}
        ${b.free ? `<span class="cat emoji">${c.emoji}</span>`
          : `<div class="chk ${justTicked(b.id) ? "pop" : ""}" data-chk="${b.id}" title="mark done">${done ? "✓" : ""}</div>`}
      </div>`;
  }).join("");
}

// Pointer-based drag & drop on the holding bars. Chained blocks (one unit) move as a
// whole; the drop is clamped so it can never cross a fixed anchor (engine re-clamps too).
function attachDrag(wrap, key) {
  let drag = null;

  function unitMeta(excludeId) {
    // group block elements by unit, in day order, with document-space geometry
    const els = [...wrap.querySelectorAll(".block")];
    const metas = [];
    for (const el of els) {
      const uid = el.dataset.unit;
      const last = metas[metas.length - 1];
      if (last && last.id === uid) { last.els.push(el); continue; }
      metas.push({ id: uid, fixed: !el.querySelector("[data-grip]"), els: [el] });
    }
    const sy = window.scrollY;
    for (const mt of metas) {
      mt.top = mt.els[0].getBoundingClientRect().top + sy;
      mt.bottom = mt.els[mt.els.length - 1].getBoundingClientRect().bottom + sy;
      mt.mid = (mt.top + mt.bottom) / 2;
    }
    return { metas, candidates: metas.filter((mt) => mt.id !== excludeId) };
  }

  wrap.querySelectorAll("[data-grip]").forEach((grip) => {
    grip.addEventListener("click", (e) => e.stopPropagation());
    grip.addEventListener("pointerdown", (e) => {
      e.preventDefault(); e.stopPropagation();
      const unitId = grip.dataset.grip;
      const { metas, candidates } = unitMeta(unitId);
      const i = metas.findIndex((mt) => mt.id === unitId);
      let lo = i; while (lo > 0 && !metas[lo - 1].fixed) lo--;
      let hi = i; while (hi < metas.length - 1 && !metas[hi + 1].fixed) hi++;
      drag = { unitId, startY: e.pageY, lastY: e.pageY, metas, candidates, unit: metas[i], lo, hi,
               dragH: metas[i].bottom - metas[i].top + 9, slot: null, moved: false };
      try { grip.setPointerCapture(e.pointerId); } catch (err) { /* capture is best-effort */ }
    });
    grip.addEventListener("pointermove", (e) => {
      if (!drag) return;
      const dy = e.pageY - drag.startY;
      if (!drag.moved && Math.abs(dy) < 6) return;
      if (!drag.moved) { drag.moved = true; wrap.classList.add("drag-live"); }
      // the held unit "flops": it tilts with the direction of motion and floats above
      const tilt = Math.max(-3.5, Math.min(3.5, (e.pageY - drag.lastY) * 0.55));
      drag.lastY = e.pageY;
      drag.unit.els.forEach((el) => {
        el.classList.add("dragging");
        el.style.transform = `translateY(${dy}px) rotate(${tilt.toFixed(2)}deg) scale(1.02)`;
      });
      // auto-scroll near the viewport edges so long days are draggable end-to-end
      if (e.clientY < 90) window.scrollBy(0, -12);
      else if (e.clientY > innerHeight - 90) window.scrollBy(0, 12);
      // insertion slot = how many candidates sit above the pointer, clamped to the segment
      let slot = drag.candidates.filter((mt) => mt.mid < e.pageY).length;
      slot = Math.max(drag.lo, Math.min(drag.hi, slot));
      drag.slot = slot;
      // everyone else slides out of the way, clearing a gap exactly the unit's size
      drag.candidates.forEach((cand, ci) => {
        const below = cand.top > drag.unit.top;
        const t = (below ? -drag.dragH : 0) + (ci >= slot ? drag.dragH : 0);
        const want = t ? `translateY(${t}px)` : "";
        if (cand._t !== want) {
          cand._t = want;
          cand.els.forEach((el) => { el.style.transform = want; });
        }
      });
    });
    const finish = (commit) => () => {
      if (!drag) return;
      const { unitId, unit, metas, slot, moved } = drag;
      wrap.classList.remove("drag-live");
      unit.els.forEach((el) => { el.classList.remove("dragging"); el.style.transform = ""; });
      metas.forEach((mt) => { mt._t = ""; mt.els.forEach((el) => { el.style.transform = ""; }); });
      drag = null;
      if (commit && moved && slot !== null) {
        if (placeUnit(key, unitId, slot)) { buzz(); refresh(); }
      }
    };
    grip.addEventListener("pointerup", finish(true));
    grip.addEventListener("pointercancel", finish(false));
  });
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

    // Catch-up: missed study blocks from the last 7 days turn into today's focus.
    const debts = debtSummary();
    const catchUpBanner = debts.length ? `
      <div class="card tight" style="border-color:rgba(52,211,153,.45); background:linear-gradient(180deg,rgba(52,211,153,.10),var(--card))">
        <b>⚡ Catch-up mode</b>
        <div class="small muted" style="margin-top:2px">Missed this week: <b>${esc(debts.join(" · "))}</b>.
        The matching blocks below are boosted — clear the ${debts[0].startsWith("cyber") ? "cyber" : esc(debts[0].split(" ")[0])} debt first. Ticking forgotten past days (📅 preview) clears debt too.</div>
      </div>` : "";

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

    // block index -> unit info (for grips + chained styling)
    const units = unitize(day.blocks);
    const unitByBlock = [];
    units.forEach((u) => u.blocks.forEach((b, bi) => unitByBlock.push({
      id: u.id, fixed: u.fixed, chained: u.blocks.length > 1, first: bi === 0, last: bi === u.blocks.length - 1
    })));
    const anyMovable = units.some((u) => !u.fixed);

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
        ${anyMovable ? `<button class="btn sm ghost" id="ai-plan" style="flex:1">🤖 Plan my day</button>` : ""}
        <button class="btn sm ghost" id="preview-day" style="flex:1">📅 Preview any day</button>
      </div>
      ${resetBanner}
      ${catchUpBanner}
      ${anyMovable && hasCustomOrder(key) ? `
        <div class="row between" style="margin:0 2px 8px">
          <span class="small dim">✋ custom order — drag the ⣿ bars to keep adjusting</span>
          <button class="btn sm ghost" id="order-reset">↺ Reset</button>
        </div>` : anyMovable ? `
        <div class="small dim" style="margin:0 2px 8px">✋ hold a block's left bar to drag it — chained blocks move together</div>` : ""}
      <div style="margin:6px 2px 12px">${barHTML(pct)}</div>
      <div id="blocks" style="position:relative"></div>
      <div class="card tight" style="margin-top:6px">
        <div class="row between">
          <div><b>Need a real break?</b><div class="small muted">${S.offDaysLeft()} off-days left all summer</div></div>
          <button class="btn sm" id="take-off">Take an off-day</button>
        </div>
      </div>
      ${pct >= 100 ? `<div class="card center" style="border-color:rgba(52,211,153,.4)"><b class="emoji">🔥</b> Full day cleared. That's how the summer gets won.</div>` : ""}`;

    const nowI = nowIndex(day.blocks);
    const wrap = view.querySelector("#blocks");
    wrap.innerHTML = blocksHTML(day, rec, nowI, unitByBlock);

    attachDrag(wrap, key);
    wrap.querySelectorAll("[data-go]").forEach((el) => {
      el.addEventListener("click", () => { location.hash = el.dataset.go; });
      el.addEventListener("keydown", (e) => { if (e.key === "Enter") location.hash = el.dataset.go; });
    });
    wrap.querySelectorAll("[data-chk]").forEach((el) =>
      el.addEventListener("click", (e) => { e.stopPropagation(); toggle(key, el.dataset.chk, taskIds); }));
    wrap.querySelectorAll("[data-expand]").forEach((el) =>
      el.addEventListener("click", (e) => {
        e.stopPropagation();
        const [, iStr] = el.dataset.expand.split("|");
        const i = Number(iStr);
        expandBlock(day, day.blocks[i], i, key);
      }));
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

    const planBtn = view.querySelector("#ai-plan");
    if (planBtn) planBtn.addEventListener("click", () => aiPlanDay(key));
    const orderReset = view.querySelector("#order-reset");
    if (orderReset) orderReset.addEventListener("click", () => { resetDayOrder(key); toast("Back to the default plan."); refresh(); });
    view.querySelector("#take-off").addEventListener("click", () => openOffDayFlow(key));
    view.querySelectorAll("[data-day]").forEach((el) =>
      el.addEventListener("click", () => previewDay(el.dataset.day)));
    view.querySelector("#preview-day").addEventListener("click", () => previewDay(key));
  }
};
