// lesson_gen.js — generates NEW rich lessons on demand with the user's Gemini key,
// so the Learn hub grows without anyone hand-authoring content.
//
// Safety-first design (AI output is never trusted):
//  · The lesson is built across a COLLECTION of small prompts — outline → one prompt
//    per section → quiz → a final fact-check pass — never one giant generation.
//  · Every reply must be strict JSON; each step is schema-validated and gets exactly
//    one retry (with the validation error echoed back). Any hard failure aborts the
//    whole run and nothing is saved — no half-lessons, ever.
//  · Calls are spaced PAUSE_MS apart to stay far inside the Gemini free-tier rate
//    limits (429s also back off once).
//  · Generated text is stored as plain markdown-lite and ESCAPED at render time —
//    AI output is never injected as raw HTML (unlike the hand-authored lessons).
import * as S from "../state.js";
import { esc, openModal, closeModal, toast, confetti, buzz } from "../ui.js";
import { gemini, hasKey } from "../ai.js";
import { lessonTracks } from "../data/lessons_content.js";
import { topicSuggestions } from "../data/lesson_topics.js";

const PAUSE_MS = 6500;   // ≥6.5s between calls ≈ max ~9 req/min — inside the free tier's 10 RPM
const MAX_SECTIONS = 5;

const SYSTEM =
  "You are generating factual course content for LockIn, a study app for an 18-year-old Israeli student " +
  "preparing for the IDF's GAMA cyber program. Accuracy is critical: state only facts you are certain of; " +
  "prefer widely-agreed fundamentals over obscure trivia. Write clear, serious English at an " +
  "advanced-beginner level (he can read code). You MUST reply with ONLY valid JSON matching the requested " +
  "schema — no markdown fences, no commentary, no trailing commas, no extra keys.";

let running = false; // one generation at a time

// ---- strict parsing & validation ----------------------------------------------

function extractJSON(text) {
  let t = String(text).trim().replace(/^```(?:json)?/i, "").replace(/```$/, "").trim();
  const a = t.indexOf("{"), b = t.indexOf("[");
  const start = a === -1 ? b : (b === -1 ? a : Math.min(a, b));
  if (start === -1) throw new Error("no JSON found in the reply");
  const end = Math.max(t.lastIndexOf("}"), t.lastIndexOf("]"));
  if (end <= start) throw new Error("unterminated JSON in the reply");
  return JSON.parse(t.slice(start, end + 1));
}

const isStr = (v, min, max) => typeof v === "string" && v.trim().length >= min && v.length <= max;

function vOutline(o) {
  if (!o || typeof o !== "object") return "reply is not an object";
  if (!isStr(o.title, 4, 90)) return "title must be a 4-90 char string";
  if (!isStr(o.summary, 10, 220)) return "summary must be a 10-220 char string";
  if (!Number.isInteger(o.minutes) || o.minutes < 4 || o.minutes > 25) return "minutes must be an integer 4-25";
  if (!Array.isArray(o.sections) || o.sections.length < 3 || o.sections.length > MAX_SECTIONS)
    return `sections must be an array of 3-${MAX_SECTIONS}`;
  for (const s of o.sections) {
    if (!isStr(s.h, 3, 80)) return "every section needs h (3-80 chars)";
    if (!isStr(s.goal, 10, 400)) return "every section needs goal (10-400 chars)";
  }
  return null;
}

function vSection(o) {
  if (!o || typeof o !== "object") return "reply is not an object";
  if (!isStr(o.body, 250, 2600)) return "body must be a 250-2600 char string of teaching text";
  if ((o.body.match(/```/g) || []).length > 2) return "at most ONE fenced code block is allowed";
  if (/<\s*(script|img|iframe|a)\b/i.test(o.body)) return "no HTML allowed in body";
  return null;
}

function vQuiz(o) {
  const arr = o && o.quiz;
  if (!Array.isArray(arr) || arr.length !== 4) return "quiz must be an array of exactly 4 questions";
  const err = arr.map(vQuizItem).find(Boolean);
  if (err) return err;
  if (new Set(arr.map((q) => q.answer)).size === 1) return "answer indices must not all be identical";
  return null;
}

function vQuizItem(q) {
  if (!q || !isStr(q.q, 8, 260)) return "each question needs q (8-260 chars)";
  if (!Array.isArray(q.options) || q.options.length !== 4) return "each question needs exactly 4 options";
  if (q.options.some((op) => !isStr(op, 1, 160))) return "every option must be a 1-160 char string";
  if (new Set(q.options.map((op) => op.trim().toLowerCase())).size !== 4) return "options must be distinct";
  if (!Number.isInteger(q.answer) || q.answer < 0 || q.answer > 3) return "answer must be an integer 0-3";
  if (!isStr(q.why, 8, 400)) return "each question needs why (8-400 chars)";
  return null;
}

function vVerify(o, sectionCount) {
  if (!o || typeof o !== "object" || typeof o.ok !== "boolean") return "reply needs boolean ok";
  if (!Array.isArray(o.sectionFixes) || !Array.isArray(o.quizFixes)) return "sectionFixes and quizFixes must be arrays";
  for (const f of o.sectionFixes) {
    if (!Number.isInteger(f.index) || f.index < 0 || f.index >= sectionCount) return "sectionFix index out of range";
    const err = vSection(f); if (err) return `sectionFix: ${err}`;
  }
  for (const f of o.quizFixes) {
    if (!Number.isInteger(f.index) || f.index < 0 || f.index > 3) return "quizFix index out of range";
    const err = vQuizItem(f); if (err) return `quizFix: ${err}`;
  }
  return null;
}

// ---- the paced, validated pipeline ---------------------------------------------

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// One validated step: ask → parse → validate → (on failure: ONE retry that echoes
// the exact problem back) → throw if still bad. 429s get a single long back-off.
async function step(prompt, validate, ctl) {
  for (let attempt = 0; attempt < 2; attempt++) {
    if (ctl.cancelled) throw new Error("cancelled");
    let raw;
    try {
      raw = await gemini({ system: SYSTEM, messages: [{ role: "user", text: prompt }], temperature: 0.35 });
    } catch (e) {
      if (/rate limit/i.test(e.message) && attempt === 0) { ctl.note("rate-limited — backing off 30s…"); await sleep(30000); continue; }
      throw e;
    }
    let parsed, problem;
    try { parsed = extractJSON(raw); problem = validate(parsed); }
    catch (e) { problem = e.message; }
    if (!problem) return parsed;
    if (attempt === 0) {
      ctl.note("reply was invalid — retrying once…");
      await sleep(PAUSE_MS);
      prompt += `\n\nYour previous reply was rejected: ${problem}. Reply again with ONLY the corrected valid JSON.`;
    } else {
      throw new Error(`The AI couldn't produce valid content (${problem}). Nothing was saved — try again or pick another topic.`);
    }
  }
}

async function generateLesson(trackId, topic, ctl) {
  const track = lessonTracks.find((t) => t.id === trackId);

  // 1 · outline
  ctl.stage("outline");
  const outline = await step(
    `Create the outline for ONE self-contained lesson.\n` +
    `Track: ${track.name}\nTopic: "${topic}"\n` +
    `Reply with ONLY this JSON shape:\n` +
    `{"title": string (max 60 chars, plain), "summary": string (one sentence, max 140 chars), ` +
    `"minutes": integer 6-12 (realistic read time), ` +
    `"sections": [{"h": string (max 50 chars), "goal": string (one sentence: what the reader must understand after it)}]}\n` +
    `Rules: 3 to 5 sections; they must build logically from fundamentals to application; no fluffy ` +
    `"introduction" section — every section teaches something concrete about the topic.`,
    vOutline, ctl);

  if (ctl.setSections) ctl.setSections(outline.sections.length);

  // 2 · one prompt per section, paced
  const sections = [];
  for (let i = 0; i < outline.sections.length; i++) {
    ctl.stage(`sec${i}`);
    await sleep(PAUSE_MS);
    const prev = outline.sections.slice(0, i).map((s) => s.h).join(" · ") || "none (this is the first)";
    const sec = await step(
      `Write section ${i + 1} of ${outline.sections.length} for the lesson "${outline.title}" (track: ${track.name}).\n` +
      `Section heading: "${outline.sections[i].h}"\nSection goal: ${outline.sections[i].goal}\n` +
      `Sections already written before this one: ${prev}.\n` +
      `Reply with ONLY this JSON: {"body": string}\n` +
      `The body is 130-220 words of teaching text. Allowed formatting ONLY: blank line between paragraphs, ` +
      `"- " bullet lines, **bold** for key terms, \`inline code\`, and at most ONE short code/terminal example ` +
      `inside a \`\`\` fence. No headings, no links, no HTML, no tables. Be concrete — real commands, real ` +
      `field/register/function names, real numbers. Do not repeat earlier sections. End with one sentence ` +
      `that connects the idea to practice.`,
      vSection, ctl);
    sections.push({ type: "ai", h: outline.sections[i].h, body: sec.body.trim() });
  }

  const fullText = sections.map((s) => `## ${s.h}\n${s.body}`).join("\n\n");

  // 3 · quiz
  ctl.stage("quiz");
  await sleep(PAUSE_MS);
  const quizObj = await step(
    `Write the self-check quiz for the lesson below.\n` +
    `Reply with ONLY this JSON: {"quiz":[{"q": string, "options":[string,string,string,string], ` +
    `"answer": integer 0-3, "why": string (one sentence explaining why the correct option is right)}]}\n` +
    `Rules: exactly 4 questions; each must be answerable from the lesson text alone; exactly 4 plausible ` +
    `options each with only ONE correct; vary the correct index between questions; "why" must be specific.\n\n` +
    `LESSON TEXT:\n<<<\n${fullText}\n>>>`,
    vQuiz, ctl);
  let quiz = quizObj.quiz;

  // 4 · independent fact-check pass over everything
  ctl.stage("check");
  await sleep(PAUSE_MS);
  const review = await step(
    `You are fact-checking a generated lesson BEFORE it is shown to a student. Look only for real factual ` +
    `errors, misleading claims, or a quiz question whose marked answer is wrong or ambiguous. Ignore style.\n` +
    `Reply with ONLY this JSON:\n` +
    `{"ok": boolean, "sectionFixes":[{"index": integer (0-based section number), "body": string (full replacement ` +
    `body, same formatting rules: paragraphs, "- " bullets, **bold**, \`inline code\`, max one \`\`\` fence)}], ` +
    `"quizFixes":[{"index": integer 0-3, "q": string, "options":[4 strings], "answer": integer 0-3, "why": string}]}\n` +
    `If everything is accurate reply {"ok":true,"sectionFixes":[],"quizFixes":[]}. Include a fix ONLY when you ` +
    `are certain something is wrong.\n\n` +
    `LESSON:\n<<<\n${fullText}\n\nQUIZ:\n${JSON.stringify(quiz)}\n>>>`,
    (o) => vVerify(o, sections.length), ctl);
  for (const f of review.sectionFixes) sections[f.index] = { ...sections[f.index], body: f.body.trim() };
  for (const f of review.quizFixes) quiz[f.index] = { q: f.q, options: f.options, answer: f.answer, why: f.why };

  return {
    id: `ai-${Date.now().toString(36)}`,
    ai: true,
    track: trackId,
    created: S.todayKey(),
    title: outline.title.trim(),
    summary: outline.summary.trim(),
    minutes: Math.min(15, Math.max(5, outline.minutes)),
    sections,
    quiz
  };
}

// ---- UI -------------------------------------------------------------------------

export function deleteCustomLesson(id) {
  S.update((st) => { st.customLessons = (st.customLessons || []).filter((l) => l.id !== id); });
}

export function openGenerator(trackId, onDone) {
  if (running) { toast("A lesson is already being generated — give it a minute ⏳"); return; }
  if (!hasKey()) {
    openModal(`
      <h2>Connect Gemini first 🤖</h2>
      <p class="muted small">Lesson generation uses your free Gemini key (the same one as the AI tutor).
      Get one at <span class="kbd">aistudio.google.com/apikey</span> and paste it in <b>⚙ Settings → AI tutor</b>.</p>
      <button class="btn primary block" data-close style="margin-top:10px">Got it</button>`);
    return;
  }
  const track = lessonTracks.find((t) => t.id === trackId) || lessonTracks[0];
  const done = new Set((S.getState().customLessons || []).map((l) => l.title.toLowerCase()));
  const ideas = (topicSuggestions[track.id] || []).filter((t) => !done.has(t.toLowerCase())).slice(0, 5);

  const m = openModal(`
    <h2 style="margin:0">➕ New ${esc(track.name)} lesson</h2>
    <p class="small muted" style="margin:6px 0 10px">Built by AI in careful stages — outline, section-by-section
    writing, a quiz, then an independent fact-check — with rate-limit spacing between calls (~1-2 min total).
    If any stage fails validation, nothing is saved.</p>
    ${ideas.length ? `<div class="section-title">Pick a topic</div>
    <div class="row wrap" style="gap:6px; margin-bottom:10px">
      ${ideas.map((t, i) => `<button class="btn sm ghost" data-idea="${i}">${esc(t)}</button>`).join("")}
    </div>` : ""}
    <div class="section-title">…or your own</div>
    <div class="row" style="gap:8px">
      <input id="gen-topic" placeholder="e.g. ${esc(ideas[0] || "ARP spoofing basics")}" style="flex:1">
      <button class="btn primary" id="gen-go">Generate</button>
    </div>
    <div id="gen-run" style="display:none; margin-top:12px"></div>
    <button class="btn block ghost" data-close style="margin-top:12px">Close</button>`);

  const input = m.querySelector("#gen-topic");
  m.querySelectorAll("[data-idea]").forEach((b) =>
    b.addEventListener("click", () => { input.value = ideas[Number(b.dataset.idea)]; }));

  m.querySelector("#gen-go").addEventListener("click", async () => {
    const topic = input.value.trim();
    if (topic.length < 6) { toast("Give the topic a few words 🙂"); return; }
    if (running) return;
    running = true;

    let stages = [
      { id: "outline", label: "Outline — structure of the lesson" },
      { id: "quiz", label: "Quiz — 4 graded questions" },
      { id: "check", label: "Independent fact-check pass" }
    ];
    const runEl = m.querySelector("#gen-run");
    runEl.style.display = "block";
    m.querySelector("#gen-go").disabled = true;
    input.disabled = true;

    const ctl = {
      cancelled: false,
      current: null,
      stage(id) { this.current = id; paint(); },
      note(msg) { paintNote(msg); },
      setSections(n) {
        const secs = Array.from({ length: n }, (_, i) => ({ id: `sec${i}`, label: `Writing section ${i + 1} of ${n}` }));
        stages = [stages[0], ...secs, ...stages.slice(-2)];
        paint();
      }
    };
    function paint() {
      if (!runEl.isConnected) return;
      const order = stages.map((s) => s.id);
      const cur = order.indexOf(ctl.current);
      runEl.innerHTML = stages.map((st, i) => {
        const state = i < cur ? "✓" : (i === cur ? "⏳" : "·");
        return `<div class="small" style="padding:3px 0; ${state === "✓" ? "color:var(--good)" : state === "·" ? "opacity:.45" : ""}">${state} ${esc(st.label)}</div>`;
      }).join("") + `<div class="small dim" id="gen-note" style="margin-top:4px"></div>`;
    }
    function paintNote(msg) {
      const n = runEl.isConnected && runEl.querySelector("#gen-note");
      if (n) n.textContent = msg;
    }
    paint();

    try {
      const lesson = await generateLesson(track.id, topic, ctl);
      S.update((st) => {
        if (!Array.isArray(st.customLessons)) st.customLessons = [];
        st.customLessons.push(lesson);
      });
      running = false;
      confetti(24); buzz(20);
      toast(`📘 "${lesson.title}" is ready in ${track.name}`);
      if (m.isConnected) closeModal(); // still on the generator? jump straight into the lesson
      if (onDone) onDone(lesson);
    } catch (e) {
      running = false;
      const msg = e.message === "NO_KEY" ? "No API key set." : e.message;
      if (runEl.isConnected) {
        runEl.innerHTML += `<div class="small" style="color:var(--bad); margin-top:6px">✗ ${esc(msg)}</div>`;
        m.querySelector("#gen-go").disabled = false;
        input.disabled = false;
      } else if (e.message !== "cancelled") {
        toast(`Lesson generation failed: ${msg}`);
      }
    }
  });
}
