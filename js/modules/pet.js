// pet.js — Psychometric prep: a readiness gauge (target 97%) fed by three practice tracks.
// Hebrew is the heaviest weight (weakest section); English is vocab-only; Math is the solution path.
import * as S from "../state.js";
import { esc, barHTML, refresh, toast, buzz, flashHTML } from "../ui.js";
import { hebrewVocab, englishVocab, mathDrills, hebrewSentences, hebrewTips } from "../data/pet_content.js";
import { pteVocab } from "../data/pte_vocab.js";
import { cardRec, grade, deckStats, dueQueue } from "../srs.js";

// Full English deck = curated (English-defined) + the PTE list (Hebrew-glossed).
const englishDeck = englishVocab.concat(pteVocab);
const hasHebrew = (s) => /[֐-׿]/.test(s);

let sub = "overview"; // overview | hebrew | english | math
let mathIdx = 0;
let hsIdx = 0;

const W = { hebrew: 0.45, math: 0.35, english: 0.20 };

export function petReadiness() {
  const s = S.getState();
  const heb = deckStats(hebrewVocab).mastery;
  const sent = hebrewSentences.length ? Object.keys(s.pet.sentencesDone).length / hebrewSentences.length : 0;
  const hebrew = 0.7 * heb + 0.3 * sent;
  const english = deckStats(englishDeck).mastery;
  const math = mathDrills.length ? Object.keys(s.pet.mathSolved).length / mathDrills.length : 0;
  const total = 100 * (W.hebrew * hebrew + W.english * english + W.math * math);
  return { total, hebrew: hebrew * 100, english: english * 100, math: math * 100 };
}

// ---------- Overview ----------
function renderOverview(view) {
  const r = petReadiness();
  const ready = r.total >= 97;
  view.innerHTML = `
    <div class="card center" style="border-color:${ready ? "rgba(52,211,153,.5)" : "var(--line)"}">
      <div class="section-title">PET readiness</div>
      <div class="ring" style="--sz:120px; --p:${Math.round(r.total)}; position:relative; margin:0 auto">
        <span style="font-size:22px">${Math.round(r.total)}%</span>
      </div>
      <p class="small muted" style="margin-top:10px">Target: <b style="color:${ready ? "var(--good)" : "var(--gold)"}">97%</b>${ready ? " — reached! 🎯" : ""}</p>
      <p class="small dim">Tracks your in-app practice. Your Sun/Wed course is the main engine — this keeps every section moving between lessons.</p>
    </div>

    <div class="card">
      <div class="section-title">By section</div>
      ${[["Hebrew", r.hebrew, "45%"], ["Math", r.math, "35%"], ["English", r.english, "20%"]].map(([n, v, w]) => `
        <div style="margin-bottom:10px">
          <div class="row between small"><span><b>${n}</b> <span class="dim">weight ${w}</span></span><span class="muted">${Math.round(v)}%</span></div>
          ${barHTML(v, n === "Hebrew" ? "" : n === "Math" ? "good" : "gold")}
        </div>`).join("")}
    </div>

    <div class="card tight">
      <div class="section-title">Course</div>
      <p class="small muted" style="margin:0">📅 Psychometric course — <b>Sundays & Wednesdays, 09:00–14:00</b> (from July 12). It's pinned into your Today schedule on those days.</p>
    </div>

    <div class="card tight">
      <div class="section-title">Hebrew tips</div>
      <ul class="list-plain small muted">${hebrewTips.map((t) => `<li>${esc(t)}</li>`).join("")}</ul>
    </div>`;
}

// ---------- Vocab decks (Hebrew / English) ----------
function renderVocab(view, cards, rtl, label) {
  const queue = dueQueue(cards);
  const stats = deckStats(cards);
  const card = queue[0];
  view.innerHTML = `
    <div class="card tight">
      <div class="row between"><b>${label} vocabulary</b>
        <span class="pill ${stats.due ? "accent" : "good"}">${stats.due ? stats.due + " due" : "caught up"}</span></div>
      <div class="row" style="gap:12px; margin-top:8px"><span class="small muted">Learned ${stats.learned}/${stats.total}</span>
        <div style="flex:1">${barHTML(stats.mastery * 100, "good")}</div></div>
    </div>
    <div id="v-rev"></div>`;
  const rev = view.querySelector("#v-rev");
  if (!card) { rev.innerHTML = `<div class="card center"><div style="font-size:36px">✅</div><b>All caught up.</b><p class="muted small">More words scheduled for later.</p></div>`; return; }
  const r = cardRec(card.id);
  const backRtl = hasHebrew(card.meaning);
  rev.innerHTML = `
    ${flashHTML({
      front: esc(card.word),
      back: backRtl ? `<span class="rtl" style="direction:rtl">${esc(card.meaning)}</span>` : esc(card.meaning),
      sub: card.ex ? `<span class="rtl" style="direction:rtl">${esc(card.ex)}</span>` : "",
      hint: "tap to reveal meaning", backHint: "Did you know it?", rtl
    })}
    <div class="row" id="grade" style="gap:10px; margin-top:12px; display:none">
      <button class="btn bad" id="g-miss" style="flex:1">Didn't know</button>
      <button class="btn good" id="g-got" style="flex:1">Knew it +2⚡</button>
    </div>
    <p class="small dim center" style="margin-top:8px">box ${r.box} · ${queue.length} due</p>`;
  const flash = rev.querySelector("#flash");
  flash.addEventListener("click", () => {
    flash.classList.add("flipped");
    rev.querySelector("#grade").style.display = "flex";
  });
  const doGrade = (ok) => {
    S.update(() => grade(card.id, ok));
    if (ok) { S.addXP(2); buzz(); }
    refresh();
  };
  rev.querySelector("#g-got").addEventListener("click", () => doGrade(true));
  rev.querySelector("#g-miss").addEventListener("click", () => doGrade(false));
}

// ---------- Math drills + Hebrew sentences ----------
function renderMath(view) {
  const s = S.getState();
  const solved = s.pet.mathSolved;
  const d = mathDrills[mathIdx % mathDrills.length];
  const done = Object.keys(solved).length;
  view.innerHTML = `
    <div class="card tight"><div class="row between"><b>Math — the PATH, not just the answer</b>
      <span class="pill">${done}/${mathDrills.length} solved</span></div></div>
    <div class="card">
      <div class="small dim">Problem ${(mathIdx % mathDrills.length) + 1} of ${mathDrills.length}${solved[d.id] ? " · ✓ solved" : ""}</div>
      <p style="font-weight:600; margin:8px 0">${esc(d.q)}</p>
      <div id="m-reveal" class="hidden">
        <div class="divide"></div>
        <p class="small"><b style="color:var(--accent-2)">Path:</b> ${esc(d.path)}</p>
        <p class="small"><b style="color:var(--good)">Answer:</b> ${esc(d.answer)}</p>
      </div>
      <div class="row" style="gap:10px; margin-top:10px">
        <button class="btn" id="m-show" style="flex:1">Show path</button>
        <button class="btn good" id="m-got" style="flex:1">Understood ✓</button>
      </div>
      <div class="row between" style="margin-top:12px">
        <button class="btn sm ghost" id="m-prev">← prev</button>
        <button class="btn sm ghost" id="m-next">next →</button>
      </div>
    </div>

    <div class="section-title">Hebrew sentence-completion</div>
    <div id="hs"></div>`;

  view.querySelector("#m-show").addEventListener("click", () => view.querySelector("#m-reveal").classList.toggle("hidden"));
  view.querySelector("#m-got").addEventListener("click", () => {
    const first = !solved[d.id];
    S.update((st) => { st.pet.mathSolved[d.id] = true; });
    if (first) { S.addXP(5); buzz(); }
    toast("Nice — logged"); mathIdx++; refresh();
  });
  view.querySelector("#m-prev").addEventListener("click", () => { mathIdx = (mathIdx - 1 + mathDrills.length) % mathDrills.length; refresh(); });
  view.querySelector("#m-next").addEventListener("click", () => { mathIdx = (mathIdx + 1) % mathDrills.length; refresh(); });

  // sentence completion
  const hs = hebrewSentences[hsIdx % hebrewSentences.length];
  const hsEl = view.querySelector("#hs");
  hsEl.innerHTML = `
    <div class="card">
      <p class="rtl" style="direction:rtl; font-weight:600">${esc(hs.text)}</p>
      <div class="row wrap" style="gap:8px; margin-top:8px; direction:rtl">
        ${hs.options.map((o) => `<button class="btn sm hs-opt" data-opt="${esc(o)}">${esc(o)}</button>`).join("")}
      </div>
      <div id="hs-fb" class="small" style="margin-top:10px"></div>
      <div class="row between" style="margin-top:8px">
        <button class="btn sm ghost" id="hs-next">another →</button>
      </div>
    </div>`;
  hsEl.querySelectorAll(".hs-opt").forEach((b) => b.addEventListener("click", () => {
    const ok = b.dataset.opt === hs.answer;
    const fb = hsEl.querySelector("#hs-fb");
    fb.innerHTML = ok
      ? `<span style="color:var(--good)">✓ Correct — ${esc(hs.answer)}.</span> <span class="muted rtl" style="direction:rtl">${esc(hs.why)}</span>`
      : `<span style="color:var(--bad)">✗ Not quite.</span> <span class="muted">Answer: <b>${esc(hs.answer)}</b> — <span class="rtl" style="direction:rtl">${esc(hs.why)}</span></span>`;
    if (ok) {
      const first = !S.getState().pet.sentencesDone[hs.id];
      S.update((st) => { st.pet.sentencesDone[hs.id] = true; });
      if (first) { S.addXP(5); buzz(); }
    }
  }));
  hsEl.querySelector("#hs-next").addEventListener("click", () => { hsIdx++; refresh(); });
}

export default {
  id: "pet", label: "PET",
  render(view) {
    const tabs = [["overview", "Overview"], ["hebrew", "Hebrew"], ["english", "English"], ["math", "Math"]];
    view.innerHTML = `
      <div class="seg" style="display:flex; width:100%; margin-bottom:12px">
        ${tabs.map(([id, l]) => `<button data-sub="${id}" class="${sub === id ? "on" : ""}" style="flex:1">${l}</button>`).join("")}
      </div>
      <div id="pet-body"></div>`;
    view.querySelectorAll("[data-sub]").forEach((b) =>
      b.addEventListener("click", () => { sub = b.dataset.sub; refresh(); }));
    const body = view.querySelector("#pet-body");
    if (sub === "hebrew") renderVocab(body, hebrewVocab, true, "Hebrew");
    else if (sub === "english") renderVocab(body, englishDeck, false, "English");
    else if (sub === "math") renderMath(body);
    else renderOverview(body);
  }
};
