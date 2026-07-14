// lessons.js — the rich Learning reader (the theory half of the split). Renders long, illustrated
// lessons (SVG diagrams, CSS animations, video links) and interactive graded quizzes. Reading &
// understanding lives here; building & running code lives in the Lab. Besides the hand-authored
// lessons, every track can grow on demand with AI-generated lessons (see lesson_gen.js).
import * as S from "../state.js";
import { esc, refresh, toast, confetti, buzz } from "../ui.js";
import { mdLite } from "../ai.js";
import { lessonTracks, lessons } from "../data/lessons_content.js";
import { openGenerator, deleteCustomLesson } from "./lesson_gen.js";

let openId = null;                 // currently open lesson
const picks = {};                  // `${lessonId}:${qi}` -> chosen option index (session only)

function rec(id) { return S.getState().lessons[id] || {}; }
function isDone(id) { return !!rec(id).done; }

// Hand-authored + AI-generated lessons, as one list.
function allLessons() { return lessons.concat(S.getState().customLessons || []); }
function byId(id) { return allLessons().find((l) => l.id === id); }
function inTrack(trackId) { return allLessons().filter((l) => l.track === trackId); }

// ---- section rendering -------------------------------------------------------------------------
// Hand-authored sections are author-trusted HTML. AI sections ("ai") are NEVER trusted:
// their body is plain markdown-lite text that gets escaped by mdLite before display.
function sectionHTML(sec) {
  switch (sec.type) {
    case "text":
      return `<section class="lsec">${sec.h ? `<h3>${esc(sec.h)}</h3>` : ""}<div class="lprose">${sec.body}</div></section>`;
    case "ai":
      return `<section class="lsec">${sec.h ? `<h3>${esc(sec.h)}</h3>` : ""}<div class="lprose">${mdLite(sec.body)}</div></section>`;
    case "svg":
      return `<figure class="lfig">${sec.svg}${sec.caption ? `<figcaption>${esc(sec.caption)}</figcaption>` : ""}</figure>`;
    case "anim":
      return `<figure class="lfig lfig-anim">${sec.html}${sec.caption ? `<figcaption>${esc(sec.caption)}</figcaption>` : ""}</figure>`;
    case "callout":
      return `<aside class="lcallout"><div class="lcallout-h">${sec.icon || "💡"} <b>${esc(sec.title || "")}</b></div><div class="lprose">${sec.body}</div></aside>`;
    case "video":
      return `<a class="lvideo" href="${esc(sec.url)}" target="_blank" rel="noopener">
                <span class="lvideo-play">▶</span>
                <span class="lvideo-txt"><b>${esc(sec.title)}</b>
                  <span class="muted small">${esc(sec.by || "Watch")}${sec.note ? " · " + esc(sec.note) : ""} ↗</span></span>
              </a>`;
    default: return "";
  }
}

function quizHTML(l) {
  return `
    <section class="lquiz">
      <div class="section-title">✅ Check yourself — ${l.quiz.length} questions</div>
      ${l.quiz.map((q, qi) => {
        const picked = picks[`${l.id}:${qi}`];
        const answered = picked !== undefined;
        return `
        <div class="lq" data-qi="${qi}">
          <div class="lq-q">${qi + 1}. ${esc(q.q)}</div>
          <div class="lq-opts">
            ${q.options.map((opt, oi) => {
              let cls = "lq-opt";
              if (answered) {
                if (oi === q.answer) cls += " correct";
                else if (oi === picked) cls += " wrong";
                else cls += " dim";
              }
              return `<button class="${cls}" data-pick="${qi}:${oi}" ${answered ? "disabled" : ""}>${esc(opt)}</button>`;
            }).join("")}
          </div>
          ${answered ? `<div class="lq-why ${picked === q.answer ? "good" : "bad"}">${picked === q.answer ? "✓ " : "✗ "}${esc(q.why)}</div>` : ""}
        </div>`;
      }).join("")}
    </section>`;
}

function lessonCard(l) {
  const done = isDone(l.id);
  return `
    <button class="lcard ${done ? "done" : ""}" data-open="${l.id}">
      <div class="lcard-top">
        <b>${l.ai ? "🤖 " : ""}${esc(l.title)}</b>
        <span class="pill ${done ? "good" : ""}">${done ? "✓ done" : `⏱ ${l.minutes}m`}</span>
      </div>
      <div class="small muted">${esc(l.summary)}</div>
    </button>`;
}

function renderReader(view, l) {
  const done = isDone(l.id);
  const track = lessonTracks.find((t) => t.id === l.track);
  const allAnswered = l.quiz.every((_, qi) => picks[`${l.id}:${qi}`] !== undefined);
  view.innerHTML = `
    <button class="btn ghost sm" id="l-back">← All lessons</button>
    <h1 style="margin-top:10px">${esc(l.title)}</h1>
    <p class="muted small" style="margin:2px 0 14px">⏱ ${l.minutes} min read · ${esc(track ? track.name : "Lesson")}${l.ai ? " · 🤖 AI-generated — fact-checked in a second pass, but keep a critical eye" : ""}</p>
    <div class="lreader">
      ${l.sections.map(sectionHTML).join("")}
      ${quizHTML(l)}
    </div>
    <button class="btn ${done ? "good" : "primary"} block" id="l-done" style="margin-top:16px">
      ${done ? "✓ Completed — read again anytime" : "Mark lesson complete"}
    </button>
    ${l.ai ? `<button class="btn ghost block sm" id="l-del" style="margin-top:8px">🗑 Delete this AI lesson</button>` : ""}`;

  view.querySelector("#l-back").addEventListener("click", () => { openId = null; refresh(); });
  view.querySelectorAll("[data-pick]").forEach((b) => b.addEventListener("click", () => {
    const [qi, oi] = b.dataset.pick.split(":").map(Number);
    if (picks[`${l.id}:${qi}`] !== undefined) return;
    picks[`${l.id}:${qi}`] = oi;
    const correct = oi === l.quiz[qi].answer;
    if (correct) { S.addXP(3); buzz(); }
    refresh();
  }));
  view.querySelector("#l-done").addEventListener("click", () => {
    if (isDone(l.id)) return;
    if (!allAnswered) { toast("Answer the check questions first 💪"); return; }
    S.update((st) => { st.lessons[l.id] = { done: true, date: S.todayKey() }; });
    S.addXP(20); confetti(30); buzz(30); toast("📘 Lesson complete · +20 XP");
    refresh();
  });
  const del = view.querySelector("#l-del");
  if (del) del.addEventListener("click", () => {
    deleteCustomLesson(l.id);
    openId = null;
    toast("Lesson deleted.");
    refresh();
  });
}

export default {
  id: "lessons", label: "📖 Lessons",
  render(view) {
    if (openId && byId(openId)) { renderReader(view, byId(openId)); return; }
    const all = allLessons();
    const total = all.length;
    const done = all.filter((l) => isDone(l.id)).length;
    view.innerHTML = `
      <div class="card" style="border-color:rgba(34,211,238,.35)">
        <b class="emoji">📖 Lessons — read & understand</b>
        <p class="small muted" style="margin:6px 0 0">The theory half: illustrated, in-depth lessons with diagrams, animations and videos. Hands-on coding lives in the <b>Lab</b>. ${done}/${total} done.</p>
      </div>
      ${lessonTracks.map((t) => {
        const ls = inTrack(t.id);
        return `
        <div class="section-title" style="margin-top:14px">${t.icon} ${esc(t.name)} — <span style="text-transform:none;letter-spacing:0;font-weight:600">${esc(t.blurb)}</span></div>
        <div class="lcards">
          ${ls.map(lessonCard).join("")}
          <button class="lcard lcard-new" data-gen="${t.id}">
            <div class="lcard-top"><b>➕ New AI lesson</b><span class="pill">🤖</span></div>
            <div class="small muted">${ls.length ? "Grow this track" : "This track is empty — generate its first lesson"} with your Gemini key.</div>
          </button>
        </div>`;
      }).join("")}
      <p class="small dim center" style="margin-top:16px">AI lessons are built in stages (outline → sections → quiz → fact-check) and validated at every step.</p>`;
    view.querySelectorAll("[data-open]").forEach((b) => b.addEventListener("click", () => { openId = b.dataset.open; window.scrollTo(0, 0); refresh(); }));
    view.querySelectorAll("[data-gen]").forEach((b) => b.addEventListener("click", () =>
      openGenerator(b.dataset.gen, (lesson) => { openId = lesson.id; window.scrollTo(0, 0); refresh(); })));
  },
};
