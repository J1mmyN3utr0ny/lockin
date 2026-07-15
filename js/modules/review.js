// review.js — the end-of-week (Friday) Weekly Review. A cumulative test of everything learned so
// far: flashcards from all the knowledge decks PLUS real quiz questions from the lessons finished
// this week — and a resurfaced sample of questions from PAST weeks' tests, so old material keeps
// getting recalled long after its week (that's what moves it into long-term memory).
import * as S from "../state.js";
import { esc, barHTML, flashHTML, confetti, buzz, refresh, toast } from "../ui.js";
import { allCards as cyberCards } from "../data/cyber_decks.js";
import { lessons as richLessons } from "../data/lessons_content.js";
import { hebrewVocab, englishVocab } from "../data/pet_content.js";
import { pteVocab } from "../data/pte_vocab.js";
import { cardRec, grade } from "../srs.js";

const TARGET = 15;      // items per review
const MC_FRESH = 5;     // lesson questions from THIS week's completed lessons
const MC_RESURFACED = 3; // questions pulled back from previous weeks' tests
const hasHebrew = (s) => /[֐-׿]/.test(s);

let queue = null, idx = 0, score = 0, flipped = false, reviewWeek = 0;

// Normalize every knowledge source into {id, front, back, rtl}.
function pool() {
  const cyber = cyberCards().map((c) => ({ id: c.id, front: c.term, back: c.explain, rtl: false }));
  const heb = hebrewVocab.map((c) => ({ id: c.id, front: c.word, back: c.meaning + (c.ex ? " · " + c.ex : ""), rtl: true }));
  const eng = englishVocab.concat(pteVocab).map((c) => ({ id: c.id, front: c.word, back: c.meaning, rtl: hasHebrew(c.meaning) }));
  return cyber.concat(heb, eng);
}

// Every quiz question of every COMPLETED rich lesson (hand-authored + AI-generated),
// as a multiple-choice review item tagged with when the lesson was finished.
function mcPool(s) {
  const out = [];
  for (const l of richLessons.concat(s.customLessons || [])) {
    const rec = s.lessons[l.id];
    if (!rec || !rec.done) continue;
    (l.quiz || []).forEach((q, i) => out.push({
      type: "mc", id: `${l.id}::q${i}`, lesson: l.title, doneDate: rec.date || "",
      q: q.q, options: q.options, answer: q.answer, why: q.why
    }));
  }
  return out;
}

function buildQueue() {
  const s = S.getState();
  const wk = S.weekOf(S.todayKey());
  const range = S.weekRange(wk);
  const mcs = mcPool(s);

  // fresh: questions from lessons completed this week
  const fresh = mcs.filter((m) => m.doneDate >= range.start && m.doneDate <= range.end);
  // resurfaced: questions that APPEARED in a previous week's test — variety + long-term recall
  const pastIds = new Set();
  for (const [w, r] of Object.entries(s.reviews)) {
    if (Number(w) < wk) (r.qids || []).forEach((id) => pastIds.add(id));
  }
  const freshPick = shuffle(fresh).slice(0, MC_FRESH);
  const resurfaced = shuffle(mcs.filter((m) => pastIds.has(m.id) && !freshPick.includes(m))).slice(0, MC_RESURFACED);
  const mcPick = freshPick.concat(resurfaced);

  // flashcards fill the remaining slots (studied cards first, then new material)
  const all = pool();
  const room = Math.max(0, TARGET - mcPick.length);
  const seen = all.filter((c) => (cardRec(c.id).seen || 0) > 0);
  let cards = shuffle(seen).slice(0, room);
  if (cards.length < room) {
    const rest = shuffle(all.filter((c) => !cards.includes(c)));
    cards = cards.concat(rest.slice(0, room - cards.length));
  }
  return shuffle(mcPick.concat(cards));
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
  // remember which lesson questions appeared — future weeks resurface a sample of them
  const qids = Array.from(new Set((queue.filter((i) => i.type === "mc").map((i) => i.id)).concat((prev && prev.qids) || [])));
  const rec = { score, total: queue.length, date: S.todayKey(), qids };
  const improved = !prev || score >= prev.score;
  S.update((st) => {
    if (!prev || score >= prev.score) st.reviews[wk] = rec;
    else st.reviews[wk] = { ...prev, qids }; // keep the better score, still record the questions
  });
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
      const head = `
        <div class="row between">
          <div><h1 style="margin:0">Weekly Review</h1><p class="muted" style="margin:0">Week ${reviewWeek} · item ${idx + 1}/${queue.length}</p></div>
          <span class="pill good">${score} correct</span>
        </div>
        <div style="margin:10px 0">${barHTML((idx / queue.length) * 100)}</div>`;

      // Multiple-choice lesson question — objective, auto-scored.
      if (c.type === "mc") {
        view.innerHTML = `${head}
          <div class="card">
            <div class="small dim" style="margin-bottom:6px">📘 from "${esc(c.lesson)}"</div>
            <div class="lq-q" style="font-weight:700">${esc(c.q)}</div>
            <div class="lq-opts" style="margin-top:10px">
              ${c.options.map((opt, oi) => `<button class="lq-opt" data-mc="${oi}">${esc(opt)}</button>`).join("")}
            </div>
            <div id="mc-why" class="small" style="margin-top:8px; display:none"></div>
            <button class="btn primary block" id="mc-next" style="margin-top:10px; display:none">Next →</button>
          </div>`;
        let answered = false;
        view.querySelectorAll("[data-mc]").forEach((b) => b.addEventListener("click", () => {
          if (answered) return;
          answered = true;
          const oi = Number(b.dataset.mc);
          const ok = oi === c.answer;
          if (ok) { score++; buzz(); }
          view.querySelectorAll("[data-mc]").forEach((x, xi) => {
            x.disabled = true;
            if (xi === c.answer) x.classList.add("correct");
            else if (xi === oi) x.classList.add("wrong");
            else x.classList.add("dim");
          });
          const why = view.querySelector("#mc-why");
          why.style.display = "block";
          why.innerHTML = `<span style="color:${ok ? "var(--good)" : "var(--bad)"}">${ok ? "✓" : "✗"} ${esc(c.why)}</span>`;
          view.querySelector("#mc-next").style.display = "block";
        }));
        view.querySelector("#mc-next").addEventListener("click", () => { idx++; refresh(); });
        return;
      }

      view.innerHTML = `${head}
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
        <p class="small muted" style="margin:6px 0 0">A mixed, cumulative test: real quiz questions from <b>the lessons you finished this week</b>, a resurfaced sample from <b>past weeks' tests</b> (so old material never fades), and recall flashcards from all your decks — graded into your spaced-repetition memory. Do it every Friday.</p>
        <button class="btn primary block" id="start" style="margin-top:12px">Start Week ${wk} review (${TARGET} items)</button>
      </div>
      ${weeks.length ? `<div class="card tight"><div class="section-title">Your reviews</div>
        ${weeks.map((w) => { const r = s.reviews[w]; const p = Math.round((r.score / r.total) * 100); return `<div class="row between" style="padding:6px 0; border-bottom:1px solid var(--line)"><span class="small">Week ${w}</span><span class="pill ${p >= 80 ? "good" : ""}">${r.score}/${r.total} · ${p}%</span></div>`; }).join("")}
      </div>` : ""}
      <a class="btn ghost block" href="#today" style="margin-top:8px">Back to Today</a>`;
    view.querySelector("#start").addEventListener("click", start);
  }
};
