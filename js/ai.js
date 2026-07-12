// ai.js — the AI tutor. Talks to Google's Gemini 2.5 Flash (free tier) with a key the user
// pastes into Settings. Powers hands-on teaching: Socratic hints, work review, Q&A.
import * as S from "./state.js";
import { esc, openModal, closeModal, toast } from "./ui.js";

export const MODEL = "gemini-2.5-flash";
const ENDPOINT = (key) =>
  `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${encodeURIComponent(key)}`;

export function getKey() { return (S.getState().settings.geminiKey || "").trim(); }
export function hasKey() { return getKey().length > 20; }
export function setKey(k) { S.update((st) => { st.settings.geminiKey = (k || "").trim(); }); }

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

// Low-level call. Returns text or throws a friendly Error.
export async function gemini({ system, messages, temperature = 0.7 }) {
  const key = getKey();
  if (!key) throw new Error("NO_KEY");
  const body = {
    contents: messages.map((m) => ({ role: m.role === "assistant" ? "model" : "user", parts: [{ text: m.text }] })),
    // 2.5 Flash is a thinking model: disable thinking so tokens go to the answer, not silent reasoning,
    // and give the reply real room so structured reviews aren't truncated.
    generationConfig: { temperature, maxOutputTokens: 2048, thinkingConfig: { thinkingBudget: 0 } }
  };
  if (system) body.system_instruction = { parts: [{ text: system }] };

  let res;
  try {
    res = await fetch(ENDPOINT(key), {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
    });
  } catch (e) { throw new Error("Network error — are you online? (The tutor needs internet; the rest of the app doesn't.)"); }

  if (res.status === 400) throw new Error("Gemini rejected the request — your API key may be wrong. Re-check it in ⚙ Settings.");
  if (res.status === 403) throw new Error("Access denied (403) — the key isn't authorized for the Gemini API. Make a fresh free key at aistudio.google.com.");
  if (res.status === 429) throw new Error("Rate limit hit (free tier) — wait a minute and try again.");
  if (!res.ok) throw new Error(`Gemini error ${res.status}. Try again shortly.`);

  const data = await res.json();
  const cand = data.candidates && data.candidates[0];
  const text = cand && cand.content && cand.content.parts && cand.content.parts.map((p) => p.text).join("");
  if (!text) throw new Error("The tutor returned nothing — try rephrasing.");
  return text.trim();
}

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
