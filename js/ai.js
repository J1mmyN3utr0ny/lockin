// ai.js — the AI core. Talks to Google's Gemini free tier with a key the user pastes into
// Settings. Powers the Socratic tutor, the Build Coach, lesson generation and the app manager.
import * as S from "./state.js";
import { esc, openModal, closeModal, toast } from "./ui.js";

// Model tiers — the right brain for each job: SMART for lessons, build guides and
// tutoring; FAST for small tasks like manager notes and quick plans. Line-up verified
// against ai.google.dev/gemini-api/docs/models (July 2026): gemini-3.5-flash is the
// current stable Flash and gemini-3.1-flash-lite the current stable Lite. Each tier is
// a fallback chain: models the key/region doesn't serve (404) or that reject the
// request shape (400) are skipped, and the working pick is remembered for the session.
export const MODEL_TIERS = {
  smart: ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-3-flash-preview"],
  fast: ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash"]
};
export const MODEL = MODEL_TIERS.smart[0];
const picked = {}; // tier -> model confirmed working for this key (session only)

const ENDPOINT = (key, model) =>
  `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(key)}`;

export function getKey() { return (S.getState().settings.geminiKey || "").trim(); }
export function hasKey() { return getKey().length > 20; }
export function setKey(k) { S.update((st) => { st.settings.geminiKey = (k || "").trim(); }); }

// Backup key: a second free-tier key that takes over the moment the primary gets
// rate-limited (429), doubling the effective quota. Session remembers which key works.
function allKeys() {
  const s = S.getState().settings;
  return [(s.geminiKey || "").trim(), (s.geminiKey2 || "").trim()].filter((k) => k.length > 20);
}
let keyIx = 0; // rotates on 429 so later calls start from the key that still has quota

// The tutor's fixed persona — enforces "guide, don't solve" and the user's real goals.
export const PERSONA =
  "You are the built-in tutor inside 'LockIn', a study app for an 18-year-old Israeli software-engineering " +
  "student aiming for the IDF's elite GAMA Cyber program and a future in high-tech. He is strong at reading " +
  "code and at math, but he is training to BUILD from scratch and to truly understand low-level and cyber topics. " +
  "Teaching rules you must follow: (1) Be Socratic and hands-on — prefer questions, hints and small next steps " +
  "over finished answers. (2) NEVER hand over a full solution to an exercise or project; give the smallest hint " +
  "that unblocks, and only escalate if he's still stuck after trying. (3) When he shares work, review it: name what's " +
  "right, then the single most important thing to fix, then a nudge — not a rewrite. (4) Be concrete and brief; use " +
  "short code snippets only to illustrate a concept, never to complete his task. (5) Encourage him to run things " +
  "himself in a real terminal/editor. Keep answers focused and under ~200 words unless he asks to go deep.";

// Low-level call. Picks the model from `tier` (or an explicit `model`), walking the
// tier's fallback chain when a model isn't served — and rotating to the BACKUP key when
// the active one is rate-limited. Returns text or throws a friendly Error.
export async function gemini({ system, messages, temperature = 0.7, tier = "smart", model }) {
  const keys = allKeys();
  if (!keys.length) throw new Error("NO_KEY");
  const chain = model ? [model] : (MODEL_TIERS[tier] || MODEL_TIERS.smart);
  const start = Math.max(0, picked[tier] ? chain.indexOf(picked[tier]) : 0);
  let lastErr = null;

  for (let ci = start; ci < chain.length; ci++) {
    const mdl = chain[ci];
    const body = {
      contents: messages.map((m) => ({ role: m.role === "assistant" ? "model" : "user", parts: [{ text: m.text }] })),
      // 2.5 models think by default: disable it so tokens go to the answer, not silent
      // reasoning. (other generations reject thinkingConfig, so only send it where supported.)
      generationConfig: {
        temperature, maxOutputTokens: 2048,
        ...(mdl.startsWith("gemini-2.5") ? { thinkingConfig: { thinkingBudget: 0 } } : {})
      }
    };
    if (system) body.system_instruction = { parts: [{ text: system }] };

    for (let kt = 0; kt < keys.length; kt++) {
      const key = keys[(keyIx + kt) % keys.length];
      let res;
      try {
        res = await fetch(ENDPOINT(key, mdl), {
          method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
        });
      } catch (e) { throw new Error("Network error — are you online? (The AI needs internet; the rest of the app doesn't.)"); }

      // 429 → the active key is out of quota: rotate to the backup and retry in place.
      if (res.status === 429) {
        lastErr = new Error(keys.length > 1
          ? "Both Gemini keys are rate-limited — wait a minute and try again."
          : "Rate limit hit (free tier) — wait a minute, or add a backup key in ⚙ Settings.");
        continue;
      }
      // 404 = model not served for this key; 400 can be a model-specific request-shape
      // rejection (e.g. thinking params) — both walk the model chain instead of failing hard.
      if (res.status === 404) { lastErr = new Error(`Model ${mdl} isn't available for this key.`); break; }
      if (res.status === 400) { lastErr = new Error("Gemini rejected the request — your API key may be wrong. Re-check it in ⚙ Settings."); break; }
      if (res.status === 403) throw new Error("Access denied (403) — the key isn't authorized for the Gemini API. Make a fresh free key at aistudio.google.com.");
      if (!res.ok) throw new Error(`Gemini error ${res.status}. Try again shortly.`);

      const data = await res.json();
      const cand = data.candidates && data.candidates[0];
      const text = cand && cand.content && cand.content.parts && cand.content.parts.map((p) => p.text).join("");
      if (!text) throw new Error("The AI returned nothing — try rephrasing.");
      picked[tier] = mdl;
      keyIx = (keyIx + kt) % keys.length; // remember which key still has quota
      return text.trim();
    }
    // all keys 429'd on this model — free-tier quotas are per-model, so the next
    // model in the chain may still have room; keep walking.
  }
  throw lastErr || new Error("No Gemini model available for this key.");
}

// Strict JSON extraction from a model reply (strips fences, trims chatter). Shared by
// every feature that demands machine-readable output. Throws on anything non-JSON.
export function extractJSON(text) {
  let t = String(text).trim().replace(/^```(?:json)?/i, "").replace(/```$/, "").trim();
  const a = t.indexOf("{"), b = t.indexOf("[");
  const start = a === -1 ? b : (b === -1 ? a : Math.min(a, b));
  if (start === -1) throw new Error("no JSON found in the reply");
  const end = Math.max(t.lastIndexOf("}"), t.lastIndexOf("]"));
  if (end <= start) throw new Error("unterminated JSON in the reply");
  return JSON.parse(t.slice(start, end + 1));
}

// The Build Coach persona — the deliberate opposite of the Socratic tutor, by the user's
// explicit request: when he is actively BUILDING, give detailed concrete instructions —
// exact commands, exact code lines, file names — each with a one-line why, so the build
// moves and the learning sticks.
export const BUILDER =
  "You are the BUILD COACH inside 'LockIn', guiding an 18-year-old software-engineering student " +
  "(strong Python reader, aiming for the IDF's GAMA cyber program) while he is ACTIVELY building. " +
  "Unlike the app's Socratic tutor, in this mode you are hands-on and concrete: give the exact next " +
  "steps with real terminal commands, real code lines/snippets and file names — never vague advice. " +
  "Structure every answer as: (1) where he is right now, (2) the next concrete step with the exact " +
  "code/commands to write, (3) one short WHY per step so he learns while building, (4) how to verify " +
  "it works before moving on. Keep it under ~350 words and specific to the state he shows you.";

// Very light markdown → HTML (bold, inline code, fenced code, line breaks).
export function mdLite(t) {
  let s = esc(t);
  s = s.replace(/```([\s\S]*?)```/g, (_, c) => `<pre>${c.replace(/^\n/, "")}</pre>`);
  s = s.replace(/`([^`]+)`/g, '<span class="kbd">$1</span>');
  s = s.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
  s = s.replace(/^\s*[-*]\s+(.*)$/gm, "• $1");
  s = s.replace(/\n/g, "<br>");
  return s;
}

function keyGateHTML() {
  return `
    <h2>Connect the AI tutor 🤖</h2>
    <p class="muted small">The hands-on tutor uses <b>Gemini 2.5 Flash</b> — Google's free tier. Add a key once:</p>
    <ol class="list-plain small" style="padding-left:18px">
      <li>Go to <span class="kbd">aistudio.google.com/apikey</span> (sign in with any Google account).</li>
      <li>Click <b>Create API key</b> → copy it.</li>
      <li>Paste it in <b>⚙ Settings → AI tutor</b>.</li>
    </ol>
    <p class="small dim">It's free, stored only on this device, and never sent anywhere except Google when you ask a question.</p>
    <button class="btn primary block" data-close style="margin-top:10px">Got it</button>`;
}

// Interactive tutor chat. opts: { title, system, intro, starters:[...], context }
export function openTutor({ title = "AI Tutor", system = PERSONA, intro = "", starters = [], context = "" } = {}) {
  if (!hasKey()) { openModal(keyGateHTML()); return; }
  const sys = context ? `${system}\n\nCurrent context the student is working on:\n${context}` : system;
  const history = []; // {role, text}

  const m = openModal(`
    <div class="row between"><h2 style="margin:0">${esc(title)}</h2><button class="btn sm ghost" data-close>✕</button></div>
    ${intro ? `<p class="small muted">${esc(intro)}</p>` : ""}
    <div id="ai-thread" style="max-height:46vh; overflow-y:auto; margin:6px 0"></div>
    ${starters.length ? `<div class="row wrap" id="ai-starters" style="gap:6px; margin-bottom:8px">
      ${starters.map((s, i) => `<button class="btn sm ghost" data-starter="${i}">${esc(s)}</button>`).join("")}</div>` : ""}
    <div class="row" style="gap:8px; align-items:flex-end">
      <textarea id="ai-in" rows="2" placeholder="Ask, or paste your code/answer for review…" style="flex:1"></textarea>
      <button class="btn primary" id="ai-send">Send</button>
    </div>`);

  const thread = m.querySelector("#ai-thread");
  const input = m.querySelector("#ai-in");

  function bubble(role, html) {
    const el = document.createElement("div");
    el.className = "card tight";
    el.style.cssText = `margin:6px 0; ${role === "user" ? "background:var(--card-2); border-color:rgba(79,140,255,.3)" : "background:var(--bg-2)"}`;
    el.innerHTML = `<div class="small" style="color:${role === "user" ? "var(--accent)" : "var(--good)"}; font-weight:700; margin-bottom:4px">${role === "user" ? "You" : "Tutor"}</div><div class="small">${html}</div>`;
    thread.appendChild(el);
    thread.scrollTop = thread.scrollHeight;
    return el;
  }

  async function send(text) {
    text = (text || input.value).trim();
    if (!text) return;
    input.value = "";
    const st = m.querySelector("#ai-starters"); if (st) st.remove();
    bubble("user", esc(text));
    history.push({ role: "user", text });
    const pending = bubble("assistant", `<span class="dim">thinking…</span>`);
    m.querySelector("#ai-send").disabled = true;
    try {
      const reply = await gemini({ system: sys, messages: history });
      history.push({ role: "assistant", text: reply });
      pending.querySelector(".small:last-child").innerHTML = mdLite(reply);
    } catch (e) {
      pending.querySelector(".small:last-child").innerHTML = `<span style="color:var(--bad)">${esc(e.message === "NO_KEY" ? "No API key set." : e.message)}</span>`;
    } finally {
      m.querySelector("#ai-send").disabled = false;
      thread.scrollTop = thread.scrollHeight;
    }
  }

  m.querySelector("#ai-send").addEventListener("click", () => send());
  input.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) send(); });
  m.querySelectorAll("[data-starter]").forEach((b) =>
    b.addEventListener("click", () => send(starters[Number(b.dataset.starter)])));
}

// A prompt builder for reviewing a hands-on submission against a rubric.
export function reviewPrompt(taskTitle, rubric, submission) {
  return `I'm working on this hands-on task: "${taskTitle}".\n` +
    `What I should demonstrate: ${rubric}\n\n` +
    `Here is my work:\n\n${submission}\n\n` +
    `Please review it against the task. Tell me what's correct, the single most important thing to improve, and one nudge to try next. Do NOT rewrite it for me.`;
}
