// testmode.js — "Proving Grounds". After Sep 30 the app stops teaching and starts TESTING:
// a skill report card, a GAMA-style rapid mixed exam, and from-scratch coding challenges.
import * as S from "../state.js";
import { esc, barHTML, refresh, toast, confetti, flashHTML, LEVELS, levelPct } from "../ui.js";
import { tracks } from "../data/skill_tracks.js";
import { allCards } from "../data/cyber_decks.js";
import { deckStats, cardRec } from "../srs.js";
import { milestones as csMs } from "../data/cs_milestones.js";
import { sections as mathSecs } from "../data/math_checklist.js";
import { petReadiness } from "./pet.js";

let sub = "report"; // report | exam
let examCards = null, examIdx = 0, examScore = 0;

const CHALLENGES = [
  { id: "ch1", text: "From an empty file: a length-prefixed message framing (send + recv_all) — no notes." },
  { id: "ch2", text: "In C: read a buffer and count the set bits in each byte using bitwise ops." },
  { id: "ch3", text: "In C#: a small OOP class hierarchy with an interface + one overridden method, built to extend." },
  { id: "ch4", text: "Explain, out loud and unaided, the full path of opening a website (DNS→ARP→TCP→HTTP)." },
  { id: "ch5", text: "Read a short x86 disassembly and describe what it does." },
  { id: "ch6", text: "In Linux: a 10-line bash script with a loop + condition that processes files." },
  { id: "ch7", text: "In CMD: chase a suspicious connection with netstat/tasklist and identify the process." },
  { id: "ch8", text: "Deploy this app to GitHub Pages via git (init→commit→push→Pages) unaided." }
];

function reached(t) {
  const lvl = (S.getState().skills[t.id] || {}).level || t.from;
  return LEVELS.indexOf(lvl) >= LEVELS.indexOf(t.to);
}

function renderReport(view) {
  const s = S.getState();
  const csDone = csMs.filter((m) => (s.cs.milestones[m.id] || {}).status === "done").length === csMs.length;
  const mathDone = mathSecs.every((x) => s.math.checklist[x.id]);
  const pet = petReadiness().total;
  const deckM = deckStats(allCards()).mastery * 100;
  const passedTracks = tracks.filter(reached).length;

  const targets = [
    ["CS assignment complete", csDone, csDone ? "done" : "unfinished"],
    ["Math assignment complete", mathDone, mathDone ? "done" : "unfinished"],
    ["PET ≥ 97%", pet >= 97, Math.round(pet) + "%"],
    ["Cyber decks mastered ≥ 80%", deckM >= 80, Math.round(deckM) + "%"],
    ["Skill targets reached", passedTracks >= 8, passedTracks + "/9"]
  ];
  const passedAll = targets.every((t) => t[1]);

  view.innerHTML = `
    <div class="card center" style="border-color:${passedAll ? "rgba(52,211,153,.5)" : "var(--line)"}">
      <div style="font-size:40px">${passedAll ? "🏆" : "🧪"}</div>
      <h2 style="margin:0">${passedAll ? "Summer targets: cleared." : "Prove what stuck."}</h2>
      <p class="small muted">The app flipped to testing on Sep 30. No more teaching — just verification.</p>
    </div>

    <div class="section-title">Target report card</div>
    <div class="card">
      ${targets.map(([n, ok, val]) => `
        <div class="row between" style="padding:8px 0; border-bottom:1px solid var(--line)">
          <span>${ok ? "✅" : "⬜"} ${esc(n)}</span><span class="pill ${ok ? "good" : "warn"}">${esc(String(val))}</span>
        </div>`).join("")}
    </div>

    <div class="section-title">Skill levels — target vs. now</div>
    <div id="tk"></div>`;

  view.querySelector("#tk").innerHTML = tracks.map((t) => {
    const lvl = (s.skills[t.id] || {}).level || t.from;
    const ok = reached(t);
    return `<div class="card tight">
      <div class="row between"><b>${t.icon} ${esc(t.name)}</b><span class="pill ${ok ? "good" : "warn"}">${esc(lvl)} / ${esc(t.to)}</span></div>
      <div style="margin-top:6px">${barHTML(levelPct(lvl), ok ? "good" : "")}</div>
    </div>`;
  }).join("");
}

function newExam() {
  examCards = [...allCards()].sort(() => Math.random() - 0.5).slice(0, 10);
  examIdx = 0; examScore = 0;
}

function renderExam(view) {
  const s = S.getState();
  if (!examCards) {
    view.innerHTML = `
      <div class="card">
        <b>🎯 GAMA-style rapid exam</b>
        <p class="small muted" style="margin:6px 0">10 mixed cards from Networks + Assembly, no spaced-repetition help. Flip, self-grade honestly, get a score. This mimics the exam-day knowledge tests.</p>
        <button class="btn primary block" id="start">Start 10-card exam</button>
      </div>
      <div class="section-title">From-scratch coding challenges</div>
      <div id="ch"></div>`;
    view.querySelector("#start").addEventListener("click", () => { newExam(); refresh(); });
    renderChallenges(view.querySelector("#ch"));
    return;
  }

  if (examIdx >= examCards.length) {
    const pct = Math.round((examScore / examCards.length) * 100);
    if (pct >= 80) confetti(30);
    view.innerHTML = `
      <div class="card center" style="border-color:${pct >= 80 ? "rgba(52,211,153,.5)" : "var(--line)"}">
        <div style="font-size:40px">${pct >= 80 ? "🎉" : "📚"}</div>
        <h2 style="margin:0">${examScore}/${examCards.length} · ${pct}%</h2>
        <p class="small muted">${pct >= 80 ? "Exam-day ready on knowledge recall." : "Solid, but drill the misses before the real thing."}</p>
        <button class="btn primary block" id="again" style="margin-top:10px">New exam</button>
      </div>
      <div class="section-title">From-scratch coding challenges</div>
      <div id="ch"></div>`;
    view.querySelector("#again").addEventListener("click", () => { newExam(); refresh(); });
    renderChallenges(view.querySelector("#ch"));
    return;
  }

  const c = examCards[examIdx];
  view.innerHTML = `
    <div class="row between"><span class="small muted">Card ${examIdx + 1}/${examCards.length}</span><span class="pill">${examScore} correct</span></div>
    <div style="margin-top:8px">
      ${flashHTML({ front: esc(c.term), back: esc(c.explain), hint: "explain it out loud, then tap", backHint: "Did you nail it?" })}
    </div>
    <div class="row" id="grade" style="gap:10px; margin-top:12px; display:none">
      <button class="btn bad" id="miss" style="flex:1">Missed</button>
      <button class="btn good" id="got" style="flex:1">Got it</button>
    </div>`;
  const flash = view.querySelector("#flash");
  flash.addEventListener("click", () => {
    flash.classList.add("flipped");
    view.querySelector("#grade").style.display = "flex";
  });
  const next = (ok) => { if (ok) examScore++; examIdx++; refresh(); };
  view.querySelector("#got").addEventListener("click", () => next(true));
  view.querySelector("#miss").addEventListener("click", () => next(false));
}

function renderChallenges(host) {
  const s = S.getState();
  host.innerHTML = CHALLENGES.map((c) => {
    const on = !!(s.days["_challenges"] && s.days["_challenges"].blocks[c.id]);
    return `<div class="block tight ${on ? "done" : ""}" style="padding:10px">
      <div class="chk" data-ch="${c.id}" style="width:22px;height:22px">${on ? "✓" : ""}</div>
      <div class="body"><div class="s" style="color:var(--text)">${esc(c.text)}</div></div>
    </div>`;
  }).join("");
  host.querySelectorAll("[data-ch]").forEach((el) => el.addEventListener("click", () => {
    S.update((st) => {
      if (!st.days["_challenges"]) st.days["_challenges"] = { blocks: {} };
      const b = st.days["_challenges"].blocks;
      b[el.dataset.ch] = !b[el.dataset.ch];
    });
    refresh();
  }));
}

export default {
  id: "testmode", label: "Test", ico: "🎓",
  render(view) {
    const tabs = [["report", "Report card"], ["exam", "Exam + challenges"]];
    view.innerHTML = `
      <h1>Proving Grounds 🎓</h1>
      <p class="muted small">Post-summer mode — test that the skills stuck.</p>
      <div class="seg" style="display:flex; width:100%; margin:12px 0">
        ${tabs.map(([id, l]) => `<button data-sub="${id}" class="${sub === id ? "on" : ""}" style="flex:1">${l}</button>`).join("")}
      </div>
      <div id="tm-body"></div>`;
    view.querySelectorAll("[data-sub]").forEach((b) =>
      b.addEventListener("click", () => { sub = b.dataset.sub; refresh(); }));
    const body = view.querySelector("#tm-body");
    if (sub === "exam") renderExam(body); else renderReport(body);
  }
};
