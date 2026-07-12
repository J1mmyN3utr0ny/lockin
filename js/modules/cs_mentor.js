// cs_mentor.js — Socratic guide for the Local-CyberComm project. Guides, never solves.
// Hints are gated behind a ladder; the deepest is a pseudocode OUTLINE, never a full solution.
import * as S from "../state.js";
import { esc, barHTML, refresh, toast, confetti, buzz } from "../ui.js";
import { project, milestones, libs } from "../data/cs_milestones.js";
import { openTutor, PERSONA } from "../ai.js";

function tutorFor(m, mode) {
  const ctx = `The student is on this milestone of his Local-CyberComm CS project: "${m.name}".\n` +
    `Milestone goal: ${m.goal}\n` +
    `Design questions he should answer: ${m.designQuestions.join(" | ")}\n` +
    `Libraries in play: ${m.libs.join(", ")}`;
  if (mode === "review") {
    openTutor({
      title: "Review my code", context: ctx,
      intro: "Paste the code you wrote for this milestone. I'll review it against the goal — I won't rewrite it.",
      starters: ["Review the code I'm about to paste", "Is my message-framing correct?"]
    });
  } else {
    openTutor({
      title: "Hint — " + m.name, context: ctx,
      intro: "I'll give the smallest nudge that unblocks you — never the full solution. What's stuck?",
      starters: ["I'm stuck on where to start", "Give me the smallest next step", "What should this function's inputs/outputs be?"]
    });
  }
}

let sub = "milestones"; // milestones | libraries
let openMs = null;

function rec(id) {
  const st = S.getState();
  if (!st.cs.milestones[id]) st.cs.milestones[id] = { status: "todo", hintLevel: 0, reflection: "" };
  return st.cs.milestones[id];
}

const STATUS = { todo: ["To do", ""], doing: ["In progress", "warn"], done: ["Done ✓", "good"] };

function renderMilestones(view) {
  const st = S.getState();
  const total = milestones.length;
  const done = milestones.filter((m) => (st.cs.milestones[m.id] || {}).status === "done").length;

  view.innerHTML = `
    <div class="card">
      <b>💻 ${esc(project.name)}</b>
      <p class="small muted" style="margin:6px 0">${esc(project.summary)}</p>
      <div class="divide"></div>
      <p class="small" style="color:var(--accent)">${esc(project.learnGoal)}</p>
      <p class="small" style="color:var(--gold)">🧭 ${esc(project.gutCheck)}</p>
      <div style="margin-top:10px">${barHTML((done / total) * 100)}</div>
      <div class="small dim center" style="margin-top:6px">${done}/${total} milestones done</div>
    </div>
    <div id="ms"></div>`;

  const wrap = view.querySelector("#ms");
  wrap.innerHTML = milestones.map((m) => {
    const r = st.cs.milestones[m.id] || { status: "todo", hintLevel: 0, reflection: "" };
    const isOpen = openMs === m.id;
    const [lbl, cls] = STATUS[r.status];
    return `
      <div class="card ${isOpen ? "" : "tight"}">
        <div class="row between accordion-h" data-ms="${m.id}">
          <b>${esc(m.name)}</b>
          <span class="pill ${cls}">${lbl}</span>
        </div>
        ${isOpen ? `
          <p class="small muted" style="margin-top:8px"><b>Goal:</b> ${esc(m.goal)}</p>
          <div class="section-title" style="margin-top:8px">Answer these first (yourself)</div>
          <ul class="list-plain small">${m.designQuestions.map((q) => `<li>${esc(q)}</li>`).join("")}</ul>

          <div class="section-title" style="margin-top:10px">Libraries in play</div>
          <div class="row wrap" style="gap:6px">${m.libs.map((l) => `<span class="tag">${esc(libs[l] ? libs[l].name : l)}</span>`).join("")}</div>

          <div class="section-title" style="margin-top:12px">Stuck? Reveal hints one at a time</div>
          <div id="hints-${m.id}">
            ${[0, 1, 2].map((i) => {
              const shown = r.hintLevel > i;
              const labels = ["Nudge", "More specific", "Pseudocode outline"];
              return shown
                ? `<div class="card tight" style="background:var(--bg-2)"><div class="small"><b>${labels[i]}:</b> ${esc(m.hints[i])}</div></div>`
                : (r.hintLevel === i ? `<button class="btn sm block" data-hint="${m.id}" style="margin-bottom:8px">Reveal ${labels[i].toLowerCase()} →</button>` : "");
            }).join("")}
            ${r.hintLevel >= 3 ? `<p class="small dim">That's the deepest hint — an outline, not a solution. The code is yours to write.</p>` : ""}
          </div>

          <div class="section-title" style="margin-top:12px">AI tutor (Socratic — never solves)</div>
          <div class="row" style="gap:8px">
            <button class="btn sm" data-tutor="${m.id}:hint" style="flex:1">💡 Hint from tutor</button>
            <button class="btn sm" data-tutor="${m.id}:review" style="flex:1">✓ Review my code</button>
          </div>

          <div class="section-title" style="margin-top:12px">Reflection (capture the experience)</div>
          <p class="small muted" style="margin:0 0 6px">${esc(m.reflection)}</p>
          <textarea id="ref-${m.id}" rows="2" placeholder="Your answer in your own words...">${esc(r.reflection)}</textarea>

          <div class="section-title" style="margin-top:12px">Status</div>
          <div class="seg" style="display:flex; width:100%">
            ${Object.keys(STATUS).map((sKey) => `<button data-status="${m.id}:${sKey}" class="${r.status === sKey ? "on" : ""}" style="flex:1">${STATUS[sKey][0]}</button>`).join("")}
          </div>
        ` : `<p class="small muted" style="margin:6px 0 0">${esc(m.goal)}</p>`}
      </div>`;
  }).join("");

  wrap.querySelectorAll("[data-ms]").forEach((el) => el.addEventListener("click", () => {
    openMs = openMs === el.dataset.ms ? null : el.dataset.ms; refresh();
  }));
  wrap.querySelectorAll("[data-hint]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    S.update((s2) => { rec(el.dataset.hint); s2.cs.milestones[el.dataset.hint].hintLevel++; });
    refresh();
  }));
  wrap.querySelectorAll("[data-tutor]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const [id, mode] = el.dataset.tutor.split(":");
    tutorFor(milestones.find((x) => x.id === id), mode);
  }));
  wrap.querySelectorAll("[data-status]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const [id, val] = el.dataset.status.split(":");
    const was = (S.getState().cs.milestones[id] || {}).status;
    S.update((s2) => { rec(id); s2.cs.milestones[id].status = val; });
    if (val === "done" && was !== "done") {
      S.addXP(25); confetti(24); buzz(25);
      toast("Milestone done +25⚡ — could you re-explain it to your teacher?");
    } else if (was === "done" && val !== "done") {
      S.addXP(-25);
    }
    refresh();
  }));
  wrap.querySelectorAll("textarea[id^='ref-']").forEach((el) => el.addEventListener("change", () => {
    const id = el.id.slice(4);
    S.update((s2) => { rec(id); s2.cs.milestones[id].reflection = el.value; });
  }));
}

function renderLibraries(view) {
  view.innerHTML = `
    <div class="card tight"><b>📚 Library memory-jog</b>
      <p class="small muted" style="margin:6px 0 0">Your stated weakness is remembering libraries. These are the API surface + the gotcha — no code, so you still write it. Quiz yourself on each.</p></div>
    ${Object.values(libs).map((l) => `
      <div class="card tight">
        <div class="row between"><b>${esc(l.name)}</b><span class="tag">${esc(l.whatFor)}</span></div>
        <div class="section-title" style="margin-top:8px">Key API</div>
        <div class="row wrap" style="gap:6px">${l.keyAPI.map((a) => `<span class="kbd">${esc(a)}</span>`).join("")}</div>
        <p class="small" style="margin-top:8px; color:var(--warn)">⚠️ ${esc(l.gotcha)}</p>
        <p class="small" style="color:var(--accent-2)">❓ ${esc(l.quiz)}</p>
      </div>`).join("")}`;
}

export default {
  id: "csmentor", label: "CS Project",
  render(view) {
    const tabs = [["milestones", "Milestones"], ["libraries", "Libraries"]];
    view.innerHTML = `
      <div class="seg" style="display:flex; width:100%; margin-bottom:12px">
        ${tabs.map(([id, l]) => `<button data-sub="${id}" class="${sub === id ? "on" : ""}" style="flex:1">${l}</button>`).join("")}
      </div>
      <div id="cs-body"></div>`;
    view.querySelectorAll("[data-sub]").forEach((b) =>
      b.addEventListener("click", () => { sub = b.dataset.sub; refresh(); }));
    const body = view.querySelector("#cs-body");
    if (sub === "libraries") renderLibraries(body); else renderMilestones(body);
  }
};
