// diet.js — eating as a checklist (not appetite). 3 meals + 2 snacks, protein-first,
// plus the bodyweight log that proves the bulk is working.
import * as S from "../state.js";
import { esc, barHTML, refresh, toast, buzz, sparkSVG } from "../ui.js";
import { mealSlots, targets, tips } from "../data/meals.js";
import { buildDay } from "../schedule.js";

// Each meal slot reads its time from TODAY's actual schedule (so a shifted or
// reordered day moves the meals with it); the static time is only a fallback.
const SLOT_BLOCKS = { m1: ["breakfast", "wake"], s1: [], m2: ["lunch"], s2: ["snack"], m3: ["dinner"] };
function slotTime(blocks, m) {
  for (const id of SLOT_BLOCKS[m.id] || []) {
    const b = blocks.find((x) => x.id === id);
    if (b && /^\d/.test(b.time)) return b.time;
  }
  return m.time.split(" ")[0];
}

function toggleMeal(key, id) {
  let nowOn = false;
  S.update((st) => {
    if (!st.meals[key]) st.meals[key] = {};
    nowOn = !st.meals[key][id];
    st.meals[key][id] = nowOn;
  });
  S.addXP(nowOn ? 5 : -5);
  if (nowOn) buzz();
  refresh();
}

export default {
  id: "diet", label: "Diet",
  render(view) {
    const key = S.todayKey();
    const s = S.getState();
    const ticks = s.meals[key] || {};
    const done = mealSlots.filter((m) => ticks[m.id]).length;
    const pct = (done / mealSlots.length) * 100;
    const tg = targets(s.profile.bodyweightKg);
    const dayBlocks = buildDay(key).blocks;
    // slot grams are shares of ONE daily number, so the five together = the target
    const proteinMid = Math.round((tg.proteinLow + tg.proteinHigh) / 2);
    const slotGrams = (m) => Math.round(proteinMid * m.frac);

    // bodyweight trend
    const entries = Object.entries(s.body.weights).sort((a, b) => a[0] < b[0] ? -1 : 1);
    const vals = entries.map(([, v]) => v);
    const first = vals[0], last = vals[vals.length - 1];
    const delta = vals.length >= 2 ? (last - first) : 0;
    const todayW = s.body.weights[key];

    view.innerHTML = `
      <div class="card">
        <div class="row between">
          <div><h2 style="margin:0">Fuel the build</h2><div class="small muted">Hit all 5 — hungry or not. +5⚡ each.</div></div>
          <div class="ring" style="--p:${Math.round(pct)}; position:relative"><span>${done}/5</span></div>
        </div>
        <div style="margin-top:10px">${barHTML(pct, "gold")}</div>
        <div class="grid2" style="margin-top:12px">
          <div class="stat"><div class="n" style="color:var(--good)">${tg.proteinLow}–${tg.proteinHigh}g</div><div class="l">Protein / day</div></div>
          <div class="stat"><div class="n" style="color:var(--warn)">~${tg.kcal}</div><div class="l">Calories (lean-bulk)</div></div>
        </div>
        <p class="small dim" style="margin:8px 0 0">Slot times follow <b>today's schedule</b> (they move when your day does), and the five amounts below add up to ~${mealSlots.reduce((n, m) => n + slotGrams(m), 0)}g — the middle of your target.</p>
      </div>

      <div id="meals"></div>

      <div class="card">
        <div class="section-title">Bodyweight — the scoreboard of the bulk</div>
        <div class="row" style="gap:8px">
          <input type="number" step="0.1" id="bw-in" placeholder="kg" value="${todayW ?? ""}">
          <button class="btn sm primary" id="bw-log">Log today</button>
          <span class="spacer"></span>
          ${vals.length >= 2 ? `<span class="pill ${delta >= 0 ? "good" : "warn"}">${delta >= 0 ? "+" : ""}${delta.toFixed(1)} kg since start</span>` : ""}
        </div>
        <div style="margin-top:10px">${sparkSVG(vals.slice(-21), { color: "var(--good)" })}</div>
        <p class="small dim" style="margin:6px 0 0">Weigh in 2–3×/week, same time of day. Aim for roughly +0.25–0.5 kg per week — slower is fine, backwards is a food problem.</p>
      </div>

      <div class="card tight">
        <div class="section-title">Make eating effortless</div>
        <ul class="list-plain small muted">${tips.map((t) => `<li>${esc(t)}</li>`).join("")}</ul>
      </div>`;

    const wrap = view.querySelector("#meals");
    wrap.innerHTML = mealSlots.map((m) => {
      const on = !!ticks[m.id];
      return `
        <div class="block ${on ? "done" : ""}" style="--cat:#f59e0b" data-meal="${m.id}">
          <div class="time" style="min-width:64px">${esc(slotTime(dayBlocks, m))}</div>
          <div class="body">
            <div class="t">${esc(m.label)} <span class="tag">~${slotGrams(m)}g protein</span></div>
            <div class="s">${esc(m.ideas.join(" · "))}</div>
          </div>
          <div class="chk" data-mealchk="${m.id}">${on ? "✓" : ""}</div>
        </div>`;
    }).join("");
    wrap.querySelectorAll("[data-mealchk]").forEach((el) =>
      el.addEventListener("click", () => toggleMeal(key, el.dataset.mealchk)));

    view.querySelector("#bw-log").addEventListener("click", () => {
      const v = Number(view.querySelector("#bw-in").value);
      if (!v || v < 30 || v > 200) { toast("Enter a weight in kg"); return; }
      const first = !s.body.weights[key];
      S.update((st) => { st.body.weights[key] = v; st.profile.bodyweightKg = v; });
      if (first) S.addXP(5);
      buzz();
      toast("Weight logged 📈");
      refresh();
    });
  }
};
