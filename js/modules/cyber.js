// cyber.js — the learning hub: 9 skill tracks, four SR flashcard decks, Git School, GAMA roadmap.
import * as S from "../state.js";
import { esc, barHTML, refresh, toast, confetti, buzz, flashHTML, LEVELS } from "../ui.js";
import { tracks, trackById } from "../data/skill_tracks.js";
import { decks, deckList } from "../data/cyber_decks.js";
import { stages, yourEdge } from "../data/gama_notes.js";
import { gitIntro, lessons } from "../data/git_lessons.js";
import { reading, READ_ICON } from "../data/reading.js";
import { cardRec, grade, deckStats, dueQueue } from "../srs.js";
import * as Lab from "../lab.js";

let sub = "tracks"; // tracks | git | <deckId> | gama
let openTrack = null;
let openLesson = null;
const quizPicks = {}; // `${lessonId}:${qIdx}` -> chosen option index (session-only)

function ensureSkill(t) {
  const st = S.getState();
  if (!st.skills[t.id]) st.skills[t.id] = { level: t.from, milestones: {} };
  return st.skills[t.id];
}

// ---------- Tracks ----------
function labCard() {
  const st = Lab.lastStatus();
  const when = Lab.lastSyncedAt();
  if (st) {
    const leet = st.leetToday || {};
    return `
    <div class="card" style="border-color:rgba(34,211,238,.4); background:linear-gradient(135deg,#0f2233,#101a2e)">
      <div class="row between">
        <span class="row" style="gap:8px"><b class="emoji">🧪 Synced from LockIn Lab</b>${st.streak ? `<span class="pill gold">🔥 ${st.streak}d</span>` : ""}</span>
        <button class="btn sm" id="lab-sync">↻ Sync</button></div>
      <div class="grid3" style="margin-top:10px">
        <div class="stat"><div class="n" style="color:var(--acc2)">${st.lessonsDone}/${st.lessonsTotal}</div><div class="l">Lessons</div></div>
        <div class="stat"><div class="n" style="color:var(--good)">${st.solvedCount}</div><div class="l">Problems</div></div>
        <div class="stat"><div class="n" style="color:var(--violet)">${st.xp}</div><div class="l">Lab XP</div></div>
      </div>
      <div class="card tight" style="margin-top:10px; background:var(--bg-2)">
        <div class="row between"><span class="small"><b>🧩 Today's LeetCode</b><br><span class="muted">${esc(leet.title || "—")}</span></span>
          <span class="pill ${leet.solved ? "good" : "warn"}">${leet.difficulty || ""}${leet.solved ? " ✓" : ""}</span></div>
      </div>
      <p class="small dim" style="margin:8px 0 0">Last synced ${when ? esc(new Date(when).toLocaleString()) : "—"}. Hands-on lessons run in the Lab on your PC.</p>
    </div>`;
  }
  return `
    <div class="card" style="border-color:rgba(34,211,238,.4); background:linear-gradient(135deg,#0f2233,#101a2e)">
      <b class="emoji">🧪 Hands-on cyber lives in LockIn Lab (desktop)</b>
      <p class="small muted" style="margin:6px 0 8px">The coding lessons, the <b>Data Structures</b> course and <b>daily LeetCode</b> run in the <b>LockIn Lab</b> app on your PC — with a real code editor, a run button, and AI code-checking. Open the <span class="kbd">Lab</span> folder → <span class="kbd">Launch&nbsp;LockIn&nbsp;Lab.bat</span>.</p>
      <p class="small dim" style="margin:0 0 8px">Connect it in <b>⚙ Settings → Lab</b> to sync progress here and let the Lab unlock your phone.</p>
      <button class="btn sm primary" id="lab-sync">Sync with the Lab</button>
    </div>`;
}

function renderTracks(view) {
  view.innerHTML = `
    ${labCard()}
    <div class="card tight">
      <b>🎯 10 tracks · current → end-of-summer</b>
      <p class="small muted" style="margin:6px 0 0">Tap a track for what to learn + its milestone ladder. Ticking a milestone = +8 XP. Full lessons are in the Lab.</p>
    </div>
    <div id="tk"></div>`;
  const syncBtn = view.querySelector("#lab-sync");
  if (syncBtn) syncBtn.addEventListener("click", async () => {
    if (!Lab.labConfigured()) { toast("Add the Lab address in ⚙ Settings first"); return; }
    syncBtn.textContent = "Syncing…"; syncBtn.disabled = true;
    try { await Lab.syncNow(); toast("Synced from Lab ✓"); refresh(); }
    catch (e) { toast(e.message); syncBtn.textContent = "↻ Sync"; syncBtn.disabled = false; }
  });
  const wrap = view.querySelector("#tk");
  wrap.innerHTML = tracks.map((t) => {
    const sk = S.getState().skills[t.id] || { level: t.from, milestones: {} };
    const total = t.milestones.length;
    const done = t.milestones.filter((_, i) => sk.milestones[i]).length;
    const isOpen = openTrack === t.id;
    return `
      <div class="card ${isOpen ? "" : "tight"}">
        <div class="row between accordion-h" data-tk="${t.id}">
          <div><b>${t.icon} ${esc(t.name)}</b>
            <div class="small muted">${esc(sk.level)} → <b style="color:var(--accent)">${esc(t.to)}</b> · ${done}/${total} milestones</div>
          </div>
          <span class="chev">▶</span>
        </div>
        <div style="margin-top:8px">${barHTML((done / total) * 100, "good")}</div>
        ${isOpen ? `
          <div class="divide"></div>
          <p class="small" style="color:var(--gold)">🎖️ GAMA: ${esc(t.gama)}</p>
          <p class="small muted">${esc(t.why)}</p>
          <label class="field" style="margin-top:8px">Your current level</label>
          <div class="seg scroll">
            ${LEVELS.map((lv) => `<button data-lvl="${t.id}:${lv}" class="${sk.level === lv ? "on" : ""}">${lv}</button>`).join("")}
          </div>
          <div class="section-title" style="margin-top:12px">Milestone ladder</div>
          <div>${t.milestones.map((m, i) => {
            const on = !!sk.milestones[i];
            return `<div class="block tight ${on ? "done" : ""}" style="padding:9px">
              <div class="chk" style="width:22px;height:22px" data-ms="${t.id}:${i}">${on ? "✓" : ""}</div>
              <div class="body"><div class="s" style="color:var(--text)">${esc(m)}</div></div>
            </div>`;
          }).join("")}</div>
          <div class="section-title" style="margin-top:10px">Resources</div>
          <ul class="list-plain small muted">${t.resources.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
          ${(reading[t.id] || []).length ? `
            <div class="section-title" style="margin-top:10px">📚 Further reading</div>
            <ul class="list-plain small muted">${reading[t.id].map((r) => `<li>${READ_ICON[r.type] || "📄"} ${r.url
              ? `<a href="${esc(r.url)}" target="_blank" rel="noopener" style="color:var(--accent)">${esc(r.title)}</a>`
              : `<b>${esc(r.title)}</b>`}${r.note ? ` — ${esc(r.note)}` : ""}</li>`).join("")}</ul>
          ` : ""}
        ` : ""}
      </div>`;
  }).join("");

  wrap.querySelectorAll("[data-tk]").forEach((el) => el.addEventListener("click", () => {
    openTrack = openTrack === el.dataset.tk ? null : el.dataset.tk; refresh();
  }));
  wrap.querySelectorAll("[data-lvl]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const [id, lv] = el.dataset.lvl.split(":");
    S.update((st) => { ensureSkill(trackById(id)); st.skills[id].level = lv; });
    refresh();
  }));
  wrap.querySelectorAll(".chk[data-ms]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const [id, i] = el.dataset.ms.split(":");
    let nowOn = false;
    S.update((st) => {
      ensureSkill(trackById(id));
      nowOn = !st.skills[id].milestones[i];
      st.skills[id].milestones[i] = nowOn;
    });
    S.addXP(nowOn ? 8 : -8);
    if (nowOn) buzz();
    refresh();
  }));
}

// ---------- Flashcard deck ----------
function renderDeck(view, deckId) {
  const deck = decks[deckId];
  const stats = deckStats(deck.cards);
  const queue = dueQueue(deck.cards);
  const card = queue[0];

  view.innerHTML = `
    <div class="card tight">
      <div class="row between">
        <b>${esc(deck.title)}</b>
        <span class="pill ${stats.due ? "accent" : "good"}">${stats.due ? stats.due + " due" : "all caught up"}</span>
      </div>
      <p class="small" style="color:var(--gold); margin:6px 0 0">🎖️ ${esc(deck.gama)}</p>
      <div class="row" style="gap:14px; margin-top:8px">
        <span class="small muted">Mastered ${stats.learned}/${stats.total}</span>
        <div style="flex:1">${barHTML(stats.mastery * 100, "good")}</div>
      </div>
    </div>
    <div id="review"></div>
    <div class="accordion" id="browse-acc">
      <div class="accordion-h card tight" id="browse-h"><b>Browse all ${stats.total} cards</b><span class="chev">▶</span></div>
      <div id="browse" class="hidden"></div>
    </div>`;

  const rev = view.querySelector("#review");
  if (!card) {
    rev.innerHTML = `<div class="card center"><div style="font-size:38px">✅</div><b>Nothing due right now.</b>
      <p class="muted small">Spaced repetition scheduled the rest for later. Come back tomorrow, or browse below.</p></div>`;
  } else {
    const r = cardRec(card.id);
    rev.innerHTML = `
      ${flashHTML({ front: esc(card.term), back: esc(card.explain), hint: `"${deck.prompt}" · tap to flip` })}
      <div class="row" id="grade" style="gap:10px; margin-top:12px; display:none">
        <button class="btn bad" id="g-miss" style="flex:1">Missed</button>
        <button class="btn good" id="g-got" style="flex:1">Got it +2⚡</button>
      </div>
      <p class="small dim center" style="margin-top:8px">box ${r.box} · ${queue.length} due in this deck</p>`;
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

  const browse = view.querySelector("#browse");
  browse.innerHTML = deck.cards.map((c) => {
    const rc = cardRec(c.id);
    const badge = rc.seen ? (rc.box >= 3 ? "good" : "") : "";
    return `<div class="card tight"><div class="row between"><b>${esc(c.term)}</b>
      <span class="pill ${badge}">${rc.seen ? "box " + rc.box : "new"}</span></div>
      <p class="small muted" style="margin:6px 0 0">${esc(c.explain)}</p></div>`;
  }).join("");
  view.querySelector("#browse-h").addEventListener("click", () => {
    browse.classList.toggle("hidden");
    view.querySelector("#browse-acc").classList.toggle("open");
  });
}

// ---------- Git School ----------
function renderGit(view) {
  const st = S.getState();
  const doneCount = lessons.filter((l) => (st.git.lessons[l.id] || {}).done).length;

  view.innerHTML = `
    <div class="card" style="border-color:rgba(52,211,153,.35)">
      <b>${esc(gitIntro.title)}</b>
      <p class="small muted" style="margin:6px 0 8px">${esc(gitIntro.blurb)}</p>
      <div style="margin:8px 0">${barHTML((doneCount / lessons.length) * 100, "good")}</div>
      <div class="small dim center">${doneCount}/${lessons.length} lessons complete · +30 XP each</div>
      <div class="divide"></div>
      <p class="small" style="color:var(--gold); margin:0">💡 ${esc(gitIntro.note)}</p>
    </div>
    <div id="gl"></div>`;

  const wrap = view.querySelector("#gl");
  wrap.innerHTML = lessons.map((l, li) => {
    const rec = st.git.lessons[l.id] || {};
    const isOpen = openLesson === l.id;
    const locked = li > 0 && !(st.git.lessons[lessons[li - 1].id] || {}).done;
    return `
      <div class="card ${isOpen ? "" : "tight"}" ${locked ? 'style="opacity:.55"' : ""}>
        <div class="row between accordion-h" data-lesson="${l.id}">
          <div><b>${locked ? "🔒 " : rec.done ? "✅ " : ""}${esc(l.title)}</b>
            <div class="small dim">${esc(l.time)}</div></div>
          <span class="chev">▶</span>
        </div>
        ${isOpen && !locked ? `
          <div class="divide"></div>
          <div class="section-title">The idea</div>
          ${l.concepts.map((c) => `<p class="small muted">${esc(c)}</p>`).join("")}
          <div class="section-title" style="margin-top:10px">Commands</div>
          <div>${l.commands.map((c) => `<div class="cmdrow"><span class="kbd">${esc(c.cmd)}</span><span class="what">${esc(c.what)}</span></div>`).join("")}</div>
          <div class="card tight" style="margin-top:12px; background:var(--bg-2)">
            <b class="small">🛠️ Practice (do it for real)</b>
            <p class="small muted" style="margin:5px 0 0">${esc(l.practice)}</p>
          </div>
          <div class="section-title" style="margin-top:12px">Quiz — get all ${l.quiz.length} right to finish</div>
          <div id="quiz-${l.id}">${l.quiz.map((q, qi) => quizQ(l.id, q, qi)).join("")}</div>
          ${quizAllCorrect(l)
            ? (rec.done
              ? `<p class="small center" style="color:var(--good); margin-top:10px">Lesson complete ✓</p>`
              : `<button class="btn primary block" data-finish="${l.id}" style="margin-top:10px">Finish lesson · +30 XP ⚡</button>`)
            : `<p class="small dim center" style="margin-top:10px">Answer all questions correctly to unlock “finish”.</p>`}
        ` : ""}
      </div>`;
  }).join("");

  wrap.querySelectorAll("[data-lesson]").forEach((el) => el.addEventListener("click", () => {
    openLesson = openLesson === el.dataset.lesson ? null : el.dataset.lesson; refresh();
  }));
  wrap.querySelectorAll("[data-q]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const [lid, qi, oi] = el.dataset.q.split("|");
    quizPicks[`${lid}:${qi}`] = Number(oi);
    refresh();
  }));
  wrap.querySelectorAll("[data-finish]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const id = el.dataset.finish;
    S.update((s2) => { s2.git.lessons[id] = { done: true }; });
    S.addXP(30);
    confetti(24); buzz(25);
    toast("Lesson complete — Git level rising 🌿");
    refresh();
  }));
}

function quizQ(lid, q, qi) {
  const pick = quizPicks[`${lid}:${qi}`];
  return `
    <div class="card tight" style="background:var(--bg-2)">
      <p class="small" style="font-weight:700; margin:0 0 8px">${qi + 1}. ${esc(q.q)}</p>
      ${q.options.map((o, oi) => {
        let cls = "";
        if (pick !== undefined) {
          if (oi === q.answer && pick === oi) cls = "correct";
          else if (pick === oi) cls = "wrong";
        }
        return `<button class="btn sm qopt ${cls}" data-q="${lid}|${qi}|${oi}">${esc(o)}</button>`;
      }).join("")}
      ${pick !== undefined
        ? (pick === q.answer
          ? `<p class="small" style="color:var(--good); margin:4px 0 0">✓ ${esc(q.why)}</p>`
          : `<p class="small" style="color:var(--bad); margin:4px 0 0">✗ Not quite — try again. </p>`)
        : ""}
    </div>`;
}
function quizAllCorrect(l) {
  return l.quiz.every((q, qi) => quizPicks[`${l.id}:${qi}`] === q.answer);
}

// ---------- GAMA ----------
function renderGama(view) {
  view.innerHTML = `
    <div class="card" style="border-color:rgba(245,196,81,.4)">
      <b class="emoji">🎖️ ${esc(yourEdge.title)}</b>
      <ul class="list-plain small muted" style="margin-top:8px">${yourEdge.bullets.map((b) => `<li>${esc(b)}</li>`).join("")}</ul>
    </div>
    ${stages.map((st) => `
      <div class="card tight">
        <b>${esc(st.name)}</b>
        <p class="small dim" style="margin:4px 0">📍 ${esc(st.where)}</p>
        <p class="small muted" style="margin:0 0 6px">${esc(st.tests)}</p>
        ${st.menu ? `<div class="row wrap" style="gap:6px; margin:6px 0">${st.menu.map((m) => `<span class="tag">${esc(m)}</span>`).join("")}</div>` : ""}
        <div class="section-title" style="margin-top:6px">How to prep</div>
        <ul class="list-plain small">${st.prep.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>
      </div>`).join("")}`;
}

export default {
  id: "cyber", label: "Cyber",
  render(view) {
    const tabs = [
      ["tracks", "Tracks"],
      ["git", "Git School"],
      ...deckList.map((d) => [d.id, d.title]),
      ["gama", "GAMA"]
    ];
    view.innerHTML = `
      <div class="seg scroll" style="width:100%; margin-bottom:12px">
        ${tabs.map(([id, l]) => `<button data-sub="${id}" class="${sub === id ? "on" : ""}">${esc(l)}</button>`).join("")}
      </div>
      <div id="cyber-body"></div>`;
    view.querySelectorAll("[data-sub]").forEach((b) =>
      b.addEventListener("click", () => { sub = b.dataset.sub; refresh(); }));
    const body = view.querySelector("#cyber-body");
    if (sub === "git") renderGit(body);
    else if (decks[sub]) renderDeck(body, sub);
    else if (sub === "gama") renderGama(body);
    else renderTracks(body);
  }
};
