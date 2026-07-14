// projects.js — the Portfolio: a ladder of résumé-worthy projects built FROM SCRATCH, plus a
// Résumé view that assembles shipped projects into a copy-paste CV section.
//
// The whole point is effective learning + real experience: retrieval-first design questions, a
// hint ladder that never solves, a build-from-scratch mandate, an explain-back reflection, and a
// "prove you own it" rebuild. Shipping a project (Git + README + demo) turns study into an artifact.
import * as S from "../state.js";
import { esc, barHTML, refresh, toast, confetti, buzz, openModal } from "../ui.js";
import { whyProjects, principles, resumeTips, tiers, projects, projectById, projectsInTier } from "../data/resume_projects.js";
import { milestones as csMilestones } from "../data/cs_milestones.js";
import { trackById } from "../data/skill_tracks.js";
import { openTutor, PERSONA, BUILDER } from "../ai.js";

let sub = "portfolio"; // portfolio | resume
let openProj = null;
let openStage = null;   // `${projId}:${i}`

// ---- state records ---------------------------------------------------------
function rec(id) {
  const st = S.getState();
  if (!st.projects[id]) st.projects[id] = { stages: {}, ship: {}, bullets: "", reflection: "", rebuilt: false };
  const r = st.projects[id];
  if (!r.stages) r.stages = {};
  if (!r.ship) r.ship = {};
  return r;
}
function stageRec(id, i) {
  const r = rec(id);
  if (!r.stages[i]) r.stages[i] = { done: false, hintLevel: 0 };
  return r.stages[i];
}
function stagesDone(p, r) { return p.stages.filter((_, i) => (r.stages[i] || {}).done).length; }
function shipDone(p, r) { return p.ship.filter((_, i) => r.ship[i]).length; }
function isShipped(p, r) { return p.ship.length > 0 && shipDone(p, r) === p.ship.length; }
function statusOf(p, r) {
  if (isShipped(p, r)) return "shipped";
  if (stagesDone(p, r) > 0 || shipDone(p, r) > 0 || r.rebuilt) return "building";
  return "planned";
}
// A project's completion for the Portfolio meter: build stages + shipping, with a mastery nudge.
function projPct(p, r) {
  const stageFrac = p.stages.length ? stagesDone(p, r) / p.stages.length : 0;
  const shipFrac = p.ship.length ? shipDone(p, r) / p.ship.length : 0;
  return 100 * Math.min(1, 0.6 * stageFrac + 0.3 * shipFrac + (r.rebuilt ? 0.1 : 0));
}

const STATUS = { planned: ["Planned", ""], building: ["Building", "warn"], shipped: ["Shipped ✓", "good"] };

// ---- AI hooks --------------------------------------------------------------
function tutorForStage(p, i, mode) {
  const s = p.stages[i];
  const ctx = `The student is building a résumé project: "${p.name}" (${p.tagline}).\n` +
    `Current stage: "${s.name}" — goal: ${s.goal}\n` +
    `Design questions he should answer himself first: ${s.dq.join(" | ")}\n` +
    `Tech in play: ${p.stack.join(", ")}`;
  if (mode === "build") {
    // The Build Coach: by explicit user request this mode IS allowed to hand over
    // exact commands and code lines — it's for when he is actively building.
    openTutor({ title: "🏗 Build guide — " + s.name, system: BUILDER, context: ctx,
      intro: "Tell me where you are (or paste your current code) and I'll give you the exact next steps — real commands, real lines, with the why.",
      starters: ["I'm starting from zero — give me step 1 with the exact code",
                 "Here's my current code — what exactly do I write next?",
                 "Give me the exact setup commands for this stage"] });
  } else if (mode === "review") {
    openTutor({ title: "Review my code", context: ctx,
      intro: "Paste the code you wrote for this stage. I'll review it against the goal — I won't rewrite it.",
      starters: ["Review the code I'm about to paste", "Did I structure this the right way?"] });
  } else {
    openTutor({ title: "Hint — " + s.name, context: ctx,
      intro: "Smallest nudge that unblocks you — never the full solution. What's stuck?",
      starters: ["I don't know where to start", "Give me the smallest next step", "What should this function's inputs/outputs be?"] });
  }
}
function coachBullet(p, current) {
  const ctx = `The student shipped the project "${p.name}" (${p.tagline}). Tech: ${p.stack.join(", ")}. ` +
    `It demonstrates: ${p.why}\n` +
    `He is drafting a RÉSUMÉ bullet for it. His current draft: "${current || "(none yet)"}".`;
  openTutor({
    title: "Coach my résumé bullet",
    system: PERSONA + " In this mode you are a résumé coach. Do NOT write the bullet for him. Critique his draft: is there a strong action verb, the concrete thing built, the tech, and the hard part or result? Ask him for a metric if one is missing. Give targeted feedback, then have HIM rewrite it.",
    context: ctx,
    intro: "Paste (or type) your bullet draft. I'll push it from 'fine' to 'sharp' — but you write the final line.",
    starters: ["Critique my draft bullet", "Is this specific enough?", "Help me add a metric"]
  });
}

// ---- Portfolio view --------------------------------------------------------
function whyCard() {
  return `
    <div class="card" style="border-color:rgba(52,211,153,.35); background:linear-gradient(135deg,#0f2418,#0e1a13)">
      <b class="emoji">💡 ${esc(whyProjects.title)}</b>
      <p class="small muted" style="margin:6px 0 10px">${esc(whyProjects.blurb)}</p>
      ${whyProjects.points.map((r) => `
        <div class="row" style="gap:10px; align-items:flex-start; margin-bottom:8px">
          <div style="font-size:18px; line-height:1.2">${r.icon}</div>
          <div><b class="small">${esc(r.name)}</b><div class="small muted">${esc(r.text)}</div></div>
        </div>`).join("")}
    </div>`;
}

function principlesCard() {
  return `
    <div class="card" style="border-color:rgba(167,139,250,.35); background:linear-gradient(135deg,#1a1730,#141126)">
      <b class="emoji">🧭 ${esc(principles.title)}</b>
      <p class="small muted" style="margin:6px 0 10px">${esc(principles.blurb)}</p>
      ${principles.rules.map((r) => `
        <div class="row" style="gap:10px; align-items:flex-start; margin-bottom:8px">
          <div style="font-size:18px; line-height:1.2">${r.icon}</div>
          <div><b class="small">${esc(r.name)}</b><div class="small muted">${esc(r.text)}</div></div>
        </div>`).join("")}
    </div>`;
}

function stageHTML(p, i) {
  const s = p.stages[i];
  const r = stageRec(p.id, i);
  const open = openStage === `${p.id}:${i}`;
  const labels = ["Nudge", "More specific", "Pseudocode outline"];
  return `
    <div class="card tight" style="background:var(--bg-2); margin-bottom:9px">
      <div class="row" style="gap:10px; align-items:flex-start">
        <div class="chk" style="width:24px;height:24px;flex:none" data-stage-done="${p.id}:${i}">${r.done ? "✓" : ""}</div>
        <div class="body" style="flex:1; min-width:0; cursor:pointer" data-stage="${p.id}:${i}">
          <div class="row between"><b class="small" style="${r.done ? "text-decoration:line-through;color:var(--dim)" : ""}">${esc(s.name)}</b><span class="chev" style="color:var(--dim)">${open ? "▾" : "▶"}</span></div>
          <div class="small muted">${esc(s.goal)}</div>
        </div>
      </div>
      ${open ? `
        <div class="section-title" style="margin-top:10px">Answer these first — from memory</div>
        <ul class="list-plain small">${s.dq.map((q) => `<li>${esc(q)}</li>`).join("")}</ul>
        <div class="section-title" style="margin-top:10px">Stuck? Reveal hints one at a time</div>
        <div>
          ${[0, 1, 2].map((h) => {
            const shown = r.hintLevel > h;
            return shown
              ? `<div class="card tight" style="background:var(--card)"><div class="small"><b>${labels[h]}:</b> ${esc(s.hints[h])}</div></div>`
              : (r.hintLevel === h ? `<button class="btn sm block" data-hint="${p.id}:${i}" style="margin-bottom:8px">Reveal ${labels[h].toLowerCase()} →</button>` : "");
          }).join("")}
          ${r.hintLevel >= 3 ? `<p class="small dim">That's the deepest hint — an outline, not code. You write it.</p>` : ""}
        </div>
        <div class="row" style="gap:8px; margin-top:10px">
          <button class="btn sm" data-tutor="${p.id}:${i}:hint" style="flex:1">💡 Ask tutor</button>
          <button class="btn sm" data-tutor="${p.id}:${i}:review" style="flex:1">✓ Review my code</button>
        </div>
        <button class="btn sm primary block" data-tutor="${p.id}:${i}:build" style="margin-top:8px">🏗 Build guide — exact steps while you build</button>
      ` : ""}
    </div>`;
}

function projectCard(p) {
  const r = rec(p.id);
  const st = statusOf(p, r);
  const [lbl, cls] = STATUS[st];
  const open = openProj === p.id;
  const pct = projPct(p, r);
  const sd = stagesDone(p, r), shd = shipDone(p, r);
  return `
    <div class="card ${open ? "" : "tight"}">
      <div class="row between accordion-h" data-proj="${p.id}">
        <div style="min-width:0"><b>${p.icon} ${esc(p.name)}</b>
          <div class="small muted" style="white-space:normal">${esc(p.tagline)}</div>
        </div>
        <span class="pill ${cls}">${lbl}</span>
      </div>
      <div class="row wrap" style="gap:5px; margin-top:8px">${p.stack.map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div>
      <div style="margin-top:8px">${barHTML(pct, "violet")}</div>
      <div class="small dim" style="margin-top:5px">${sd}/${p.stages.length} build stages · ${shd}/${p.ship.length} ship steps${r.rebuilt ? " · 🏆 owned" : ""}</div>
      ${open ? `
        <div class="divide"></div>
        <p class="small" style="color:var(--gold)">🎖️ Why it's résumé-worthy: <span class="muted">${esc(p.why)}</span></p>
        ${p.realUse ? `<p class="small" style="color:var(--good)">🔧 Where this is actually used: <span class="muted">${esc(p.realUse)}</span></p>` : ""}
        <p class="small">Builds: ${p.skills.map((s) => `<span class="tag">${esc((trackById(s) || {}).name || s)}</span>`).join(" ")}</p>

        <div class="section-title" style="margin-top:12px">Build ladder (retrieval first, blank file, no AI)</div>
        <div>${p.stages.map((_, i) => stageHTML(p, i)).join("")}</div>

        <div class="section-title" style="margin-top:12px">🚀 Ship it — make it a portfolio artifact</div>
        <div>${p.ship.map((item, i) => `
          <div class="block tight ${r.ship[i] ? "done" : ""}" style="padding:9px">
            <div class="chk" style="width:22px;height:22px" data-ship="${p.id}:${i}">${r.ship[i] ? "✓" : ""}</div>
            <div class="body"><div class="s" style="color:var(--text)">${esc(item)}</div></div>
          </div>`).join("")}</div>
        ${p.stretch ? `<p class="small" style="color:var(--accent-2); margin-top:8px">✨ Stretch: ${esc(p.stretch)}</p>` : ""}

        <div class="section-title" style="margin-top:12px">🏆 Prove you own it</div>
        <p class="small muted" style="margin:0 0 8px">${esc(p.proveIt)}</p>
        <button class="btn sm ${r.rebuilt ? "good" : ""} block" data-rebuilt="${p.id}">${r.rebuilt ? "✓ Rebuilt from scratch — owned" : "I rebuilt it from a blank file · +30⚡"}</button>

        <div class="section-title" style="margin-top:12px">🗣️ Explain it back (your own words)</div>
        <textarea id="pref-${p.id}" rows="2" placeholder="In two sentences, how does the core actually work?">${esc(r.reflection)}</textarea>

        <div class="section-title" style="margin-top:12px">📄 Your résumé bullet</div>
        <p class="small dim" style="margin:0 0 6px">Starter to rewrite in your own words: “${esc(p.resumeBullet)}”</p>
        <textarea id="pbul-${p.id}" rows="3" placeholder="Write your version — action verb + what you built + the tech + the hard part.">${esc(r.bullets)}</textarea>
        <div class="row" style="gap:8px; margin-top:8px">
          <button class="btn sm" data-usebullet="${p.id}" style="flex:1">Use starter</button>
          <button class="btn sm" data-coach="${p.id}" style="flex:1">🤖 Coach my bullet</button>
        </div>
      ` : ""}
    </div>`;
}

function renderPortfolio(view) {
  const st = S.getState();
  const shipped = projects.filter((p) => statusOf(p, rec(p.id)) === "shipped").length;
  const building = projects.filter((p) => statusOf(p, rec(p.id)) === "building").length;

  view.innerHTML = `
    <div class="card hero">
      <div class="row between"><b class="emoji">🎯 Project Portfolio</b><span class="pill accent">${shipped}/${projects.length} shipped</span></div>
      <p class="small muted" style="margin:6px 0 0">Résumé-worthy builds, ordered easy → hard. Each one is built from a blank file so the experience is real — then shipped so it's an artifact you can show. ${building} in progress.</p>
    </div>
    ${whyCard()}
    ${principlesCard()}
    <div id="tiers"></div>`;

  const wrap = view.querySelector("#tiers");
  wrap.innerHTML = tiers.map((tier) => {
    const ps = projectsInTier(tier.id);
    return `
      <div class="section-title" style="margin-top:14px">${esc(tier.name)} — <span style="text-transform:none;letter-spacing:0;font-weight:600">${esc(tier.sub)}</span></div>
      ${ps.map((p) => projectCard(p)).join("")}`;
  }).join("");

  wireEvents(view);
}

// ---- Résumé view -----------------------------------------------------------
// A shipped project's bullet, falling back to its starter until the student writes their own.
function bulletFor(p, r) { return (r.bullets && r.bullets.trim()) || p.resumeBullet; }

// The flagship CS assignment is surfaced as a résumé entry once its milestones are done.
function flagshipEntry() {
  const st = S.getState();
  const done = csMilestones.filter((m) => (st.cs.milestones[m.id] || {}).status === "done").length;
  if (done < csMilestones.length) return null;
  const saved = (st.projects.flagship || {});
  return {
    id: "flagship", name: "Local-CyberComm", flagship: true,
    tagline: "LAN comms platform: multithreaded server, SQLite auth, custom protocol, GUI, WebRTC calls.",
    stack: ["Python", "sockets", "threading", "SQLite", "WebRTC", "GUI"],
    bullet: (saved.bullets && saved.bullets.trim()) ||
      "Engineered Local-CyberComm, a LAN chat/calls platform in Python: a multithreaded socket server with SQLite-backed auth (salted hashing), a custom length-framed JSON protocol, file transfer, and WebRTC audio/video with the server as signaling.",
    starter: true
  };
}

function resumeEntries() {
  const st = S.getState();
  const out = [];
  const fs = flagshipEntry();
  if (fs) out.push(fs);
  for (const p of projects) {
    const r = rec(p.id);
    if (statusOf(p, r) === "shipped") {
      out.push({ id: p.id, name: p.name, tagline: p.tagline, stack: p.stack, bullet: bulletFor(p, r), custom: !!(r.bullets && r.bullets.trim()) });
    }
  }
  return out;
}

function resumeText(entries) {
  let t = "PROJECTS\n";
  for (const e of entries) {
    t += `\n${e.name} — ${e.tagline}\n`;
    t += `Stack: ${e.stack.join(", ")}\n`;
    t += `• ${e.bullet}\n`;
  }
  return t.trimEnd() + "\n";
}

function renderResume(view) {
  const entries = resumeEntries();
  const shippedCount = entries.length;
  const building = projects.filter((p) => statusOf(p, rec(p.id)) === "building").length;

  view.innerHTML = `
    <div class="grid3" style="margin-bottom:6px">
      <div class="card tight stat"><div class="n" style="color:var(--good)">${shippedCount}</div><div class="l">On your CV</div></div>
      <div class="card tight stat"><div class="n" style="color:var(--warn)">${building}</div><div class="l">In progress</div></div>
      <div class="card tight stat"><div class="n" style="color:var(--violet)">${projects.length}</div><div class="l">In the ladder</div></div>
    </div>

    <div class="card" style="border-color:rgba(34,211,238,.3)">
      <b class="emoji">🧾 ${esc(resumeTips.title)}</b>
      <p class="small" style="color:var(--accent);margin:6px 0 8px">${esc(resumeTips.formula)}</p>
      ${resumeTips.examples.map((ex) => `
        <div class="card tight" style="background:var(--bg-2)">
          <p class="small" style="color:var(--bad);margin:0 0 4px">✗ ${esc(ex.bad)}</p>
          <p class="small" style="color:var(--good);margin:0">✓ ${esc(ex.good)}</p>
        </div>`).join("")}
      <div class="row wrap" style="gap:5px;margin-top:8px">${resumeTips.verbs.map((v) => `<span class="tag">${esc(v)}</span>`).join("")}</div>
      <p class="small dim" style="margin:8px 0 0">${esc(resumeTips.note)}</p>
    </div>

    <div class="section-title">Your Projects section${shippedCount ? "" : " — empty for now"}</div>
    <div id="entries"></div>`;

  const box = view.querySelector("#entries");
  if (!shippedCount) {
    box.innerHTML = `
      <div class="card center">
        <div style="font-size:34px">📭</div>
        <b>Nothing shipped yet.</b>
        <p class="small muted">Finish a project's build ladder AND its ship checklist in the Portfolio tab, and it lands here as a copy-paste CV entry. Aim for one shipped project a week.</p>
      </div>`;
    return;
  }

  box.innerHTML = `
    ${entries.map((e) => `
      <div class="card tight">
        <div class="row between"><b>${esc(e.name)}${e.flagship ? ` <span class="pill gold">flagship</span>` : ""}</b>
          ${e.custom || e.flagship ? "" : `<span class="pill">starter</span>`}</div>
        <p class="small muted" style="margin:4px 0 6px">${esc(e.tagline)}</p>
        <div class="row wrap" style="gap:5px;margin-bottom:6px">${e.stack.map((s) => `<span class="tag">${esc(s)}</span>`).join("")}</div>
        <p class="small" style="margin:0">• ${esc(e.bullet)}</p>
      </div>`).join("")}
    <div class="row" style="gap:8px;margin-top:4px">
      <button class="btn primary" id="copy-resume" style="flex:1">📋 Copy Projects section</button>
    </div>
    <p class="small dim center" style="margin-top:8px">Paste straight into your CV or LinkedIn. Rewrite each bullet in the Portfolio tab so it's yours.</p>`;

  const copyBtn = box.querySelector("#copy-resume");
  if (copyBtn) copyBtn.addEventListener("click", async () => {
    const text = resumeText(entries);
    let ok = false;
    try { if (navigator.clipboard && navigator.clipboard.writeText) { await navigator.clipboard.writeText(text); ok = true; } } catch (e) { ok = false; }
    if (!ok) {
      const ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.focus(); ta.select();
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      ta.remove();
    }
    if (ok) { toast("Projects section copied ✓"); buzz(); return; }
    // Fallback (e.g. clipboard blocked): show the text pre-selected so it can be copied by hand.
    const m = openModal(`
      <h2>Copy your Projects section</h2>
      <p class="small muted">Your device blocked the auto-copy. Tap inside, Select All, then copy.</p>
      <textarea id="resume-out" rows="12" readonly style="width:100%; font-family:ui-monospace,Consolas,monospace; font-size:12px">${esc(text)}</textarea>
      <button class="btn primary block" data-close style="margin-top:12px">Done</button>`);
    const out = m.querySelector("#resume-out");
    out.focus(); out.select();
  });
}

// ---- shared event wiring (Portfolio) --------------------------------------
function wireEvents(view) {
  view.querySelectorAll("[data-proj]").forEach((el) => el.addEventListener("click", () => {
    openProj = openProj === el.dataset.proj ? null : el.dataset.proj;
    openStage = null;
    refresh();
  }));
  view.querySelectorAll("[data-stage]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    openStage = openStage === el.dataset.stage ? null : el.dataset.stage;
    refresh();
  }));
  view.querySelectorAll("[data-stage-done]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const [id, i] = el.dataset.stageDone.split(":");
    let nowOn = false;
    S.update(() => { const r = stageRec(id, i); r.done = !r.done; nowOn = r.done; });
    S.addXP(nowOn ? 15 : -15);
    if (nowOn) buzz();
    refresh();
  }));
  view.querySelectorAll("[data-hint]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const [id, i] = el.dataset.hint.split(":");
    S.update(() => { stageRec(id, i).hintLevel++; });
    refresh();
  }));
  view.querySelectorAll("[data-tutor]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const [id, i, mode] = el.dataset.tutor.split(":");
    tutorForStage(projectById(id), Number(i), mode);
  }));
  view.querySelectorAll("[data-ship]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const [id, i] = el.dataset.ship.split(":");
    const p = projectById(id);
    let wasShipped, nowShipped, nowOn;
    S.update(() => {
      const r = rec(id);
      wasShipped = isShipped(p, r);
      nowOn = !r.ship[i];
      if (nowOn) r.ship[i] = true; else delete r.ship[i];
      nowShipped = isShipped(p, r);
    });
    S.addXP(nowOn ? 10 : -10);
    if (nowShipped && !wasShipped) {
      S.addXP(25); confetti(30); buzz(30);
      toast("🚀 Shipped! It's on your résumé now — write your bullet.");
    } else if (nowOn) buzz();
    refresh();
  }));
  view.querySelectorAll("[data-rebuilt]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const id = el.dataset.rebuilt;
    let nowOn = false;
    S.update(() => { const r = rec(id); r.rebuilt = !r.rebuilt; nowOn = r.rebuilt; });
    S.addXP(nowOn ? 30 : -30);
    if (nowOn) { confetti(24); buzz(25); toast("🏆 You own it — that's the rep that lasts."); }
    refresh();
  }));
  view.querySelectorAll("[data-usebullet]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const id = el.dataset.usebullet;
    S.update(() => { rec(id).bullets = projectById(id).resumeBullet; });
    toast("Starter loaded — now make it yours");
    refresh();
  }));
  view.querySelectorAll("[data-coach]").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const id = el.dataset.coach;
    coachBullet(projectById(id), rec(id).bullets);
  }));
  view.querySelectorAll("textarea[id^='pref-']").forEach((el) => el.addEventListener("change", () => {
    const id = el.id.slice(5);
    S.update(() => { rec(id).reflection = el.value; });
  }));
  view.querySelectorAll("textarea[id^='pbul-']").forEach((el) => el.addEventListener("change", () => {
    const id = el.id.slice(5);
    S.update(() => { rec(id).bullets = el.value; });
  }));
}

export default {
  id: "projects", label: "Portfolio",
  render(view) {
    const tabs = [["portfolio", "Portfolio"], ["resume", "Résumé"]];
    view.innerHTML = `
      <div class="seg" style="display:flex; width:100%; margin-bottom:12px">
        ${tabs.map(([id, l]) => `<button data-sub="${id}" class="${sub === id ? "on" : ""}" style="flex:1">${esc(l)}</button>`).join("")}
      </div>
      <div id="proj-body"></div>`;
    view.querySelectorAll("[data-sub]").forEach((b) =>
      b.addEventListener("click", () => { sub = b.dataset.sub; refresh(); }));
    const body = view.querySelector("#proj-body");
    if (sub === "resume") renderResume(body); else renderPortfolio(body);
  }
};
