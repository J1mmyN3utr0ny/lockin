// review.js — the end-of-week (Friday) Weekly Review. A cumulative test of everything learned so
// far (this week + every week before it), pulled from all the knowledge decks. It also grades the
// cards through the spaced-repetition system, so reviewing reinforces memory.
import * as S from "../state.js";
import { esc, barHTML, flashHTML, confetti, buzz, refresh, toast } from "../ui.js";
import { allCards as cyberCards } from "../data/cyber_decks.js";
import { hebrewVocab, englishVocab } from "../data/pet_content.js";
import { pteVocab } from "../data/pte_vocab.js";
import { cardRec, grade } from "../srs.js";

const TARGET = 15; // items per review
const hasHebrew = (s) => /[֐-׿]/.test(s);

let queue = null, idx = 0, score = 0, flipped = false, reviewWeek = 0;

// Normalize every knowledge source into {id, front, back, rtl}.
function pool() {
  const cyber = cyberCards().map((c) => ({ id: c.id, front: c.term, back: c.explain, rtl: false }));
  const heb = hebrewVocab.map((c) => ({ id: c.id, front: c.word, back: c.meaning + (c.ex ? " · " + c.ex : ""), rtl: true }));
  const eng = englishVocab.concat(pteVocab).map((c) => ({ id: c.id, front: c.word, back: c.meaning, rtl: hasHebrew(c.meaning) }));
  return cyber.concat(heb, eng);
}

function buildQueue() {
  const all = pool();
  const seen = all.filter((c) => (cardRec(c.id).seen || 0) > 0);
  let picked = shuffle(seen).slice(0, TARGET);
  if (picked.length < TARGET) { // not much studied yet — top up with new material
    const rest = shuffle(all.filter((c) => !picked.includes(c)));
    picked = picked.concat(rest.slice(0, TARGET - picked.length));
  }
  return shuffle(picked);
}
function shuffle(a) { return a.map((x) => [Math.random(), x]).sort((p, q) => p[0] - q[0]).map((p) => p[1]); }

function start() {
  reviewWeek = S.weekOf(S.todayKey());
  queue = buildQueue();
  idx = 0; score = 0; flipped = false;
  refresh();
}

function finish() {
  const s = S.getState();
  const wk = reviewWeek || S.weekOf(S.todayKey());
  const prev = s.reviews[wk];
  const rec = { score, total: queue.length, date: S.todayKey() };
  const improved = !prev || score >= prev.score;
  S.update((st) => { if (!prev || score >= prev.score) st.reviews[wk] = rec; });
  S.addXP(20 + score * 3);
  if (score / queue.length >= 0.8) confetti(36);
  buzz(25);
  return { rec, improved, prev };
}

export default {
  id: "review", label: "Review",
  render(view) {
    const s = S.getState();
    const wk = S.weekOf(S.todayKey());
    const range = S.weekRange(wk || 1);

    // ---- active quiz ----
    if (queue && idx < queue.length) {
      const c = queue[idx];
      view.innerHTML = `
        <div class="row between">
          <div><h1 style="margin:0">Weekly Review</h1><p class="muted" style="margin:0">Week ${reviewWeek} · card ${idx + 1}/${queue.length}</p></div>
          <span class="pill good">${score} correct</span>
        </div>
        <div style="margin:10px 0">${barHTML((idx / queue.length) * 100)}</div>
        ${flashHTML({ front: esc(c.front), back: c.rtl ? `<span class="rtl" style="direction:rtl">${esc(c.back)}</span>` : esc(c.back), hint: "recall it, then tap", backHint: "Did you get it?", rtl: c.rtl })}
        <div class="row" id="grade" style="gap:10px; margin-top:12px; display:none">
          <button class="btn bad" id="g-miss" style="flex:1">Missed</button>
          <button class="btn good" id="g-got" style="flex:1">Got it</button>
        </div>`;
      const flash = view.querySelector("#flash");
      flash.addEventListener("click", () => { flash.classList.add("flipped"); view.querySelector("#grade").style.display = "flex"; });
      const next = (ok) => {
        S.update(() => grade(c.id, ok)); // reinforce SRS
        if (ok) score++;
        idx++; flipped = false; refresh();
      };
      view.querySelector("#g-got").addEventListener("click", () => next(true));
      view.querySelector("#g-miss").addEventListener("click", () => next(false));
      return;
    }

    // ---- results (just finished) ----
    if (queue && idx >= queue.length) {
      const { rec, improved, prev } = finish();
      const pct = Math.round((rec.score / rec.total) * 100);
      queue = null;
      view.innerHTML = `
        <div class="card center" style="border-color:${pct >= 80 ? "rgba(52,211,153,.5)" : "var(--line)"}">
          <div style="font-size:42px">${pct >= 80 ? "🏆" : "📋"}</div>
          <h1 style="margin:0">${rec.score}/${rec.total} · ${pct}%</h1>
          <p class="muted">Week ${reviewWeek} review complete · +${20 + rec.score * 3} XP</p>
          ${prev ? `<div class="pill ${improved ? "good" : "warn"}">${improved ? "≥ last week ✓" : "last week: " + prev.score + "/" + prev.total}</div>` : ""}
          <p class="small dim" style="margin-top:10px">This tested everything through week ${reviewWeek}. Every Friday it grows to cover one more week. See you next Friday.</p>
          <button class="btn primary block" id="again" style="margin-top:12px">Review again</button>
        </div>
        <a class="btn ghost block" href="#today" style="margin-top:8px">Back to Today</a>`;
      view.querySelector("#again").addEventListener("click", start);
      return;
    }

    // ---- intro ----
    const weeks = Object.keys(s.reviews).map(Number).sort((a, b) => a - b);
    view.innerHTML = `
      <h1>📋 Weekly Review</h1>
      <p class="muted">Week ${wk} · ${esc(S.prettyDate(range.start))} → ${esc(S.prettyDate(range.end))}</p>
      <div class="card">
        <b>Test everything through week ${wk}</b>
        <p class="small muted" style="margin:6px 0 0">A mixed, cumulative recall test drawn from all your decks — Networks, Assembly, Linux, CMD, and Hebrew + English vocab. It covers <b>this week and every week before it</b>, and grades each card into your spaced-repetition memory. Do it every Friday.</p>
        <button class="btn primary block" id="start" style="margin-top:12px">Start Week ${wk} review (${TARGET} items)</button>
      </div>
      ${weeks.length ? `<div class="card tight"><div class="section-title">Your reviews</div>
        ${weeks.map((w) => { const r = s.reviews[w]; const p = Math.round((r.score / r.total) * 100); return `<div class="row between" style="padding:6px 0; border-bottom:1px solid var(--line)"><span class="small">Week ${w}</span><span class="pill ${p >= 80 ? "good" : ""}">${r.score}/${r.total} · ${p}%</span></div>`; }).join("")}
      </div>` : ""}
      <a class="btn ghost block" href="#today" style="margin-top:8px">Back to Today</a>`;
    view.querySelector("#start").addEventListener("click", start);
  }
};
