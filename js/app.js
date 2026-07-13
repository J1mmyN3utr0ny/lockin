// app.js — shell: tab router, top bar, onboarding, settings, mode switch, SW registration.
import * as S from "./state.js";
import { $, $$, esc, toast, openModal, closeModal, confirmModal, confetti, buzz } from "./ui.js";
import * as AI from "./ai.js";
import * as Lab from "./lab.js";

import today from "./modules/today.js";
import physique from "./modules/physique.js";
import diet from "./modules/diet.js";
import sleep from "./modules/sleep.js";
import cyber from "./modules/cyber.js";
import lessons from "./modules/lessons.js";
import csmentor from "./modules/cs_mentor.js";
import projects from "./modules/projects.js";
import mathmod from "./modules/math.js";
import pet from "./modules/pet.js";
import progress from "./modules/progress.js";
import testmode from "./modules/testmode.js";
import review from "./modules/review.js";

// Grouped screen with an internal segmented control.
function group(id, label, ico, subs) {
  return {
    id, label, ico,
    render(view, subId) {
      const active = subs.find((s) => s.id === subId) || subs[0];
      view.innerHTML = `
        <div class="seg scroll" style="width:100%; margin-bottom:14px">
          ${subs.map((s) => `<button data-sub="${s.id}" class="${s === active ? "on" : ""}">${esc(s.label)}</button>`).join("")}
        </div>
        <div id="sub-view"></div>`;
      view.querySelectorAll("[data-sub]").forEach((b) =>
        b.addEventListener("click", () => { location.hash = `#${id}/${b.dataset.sub}`; }));
      active.render($("#sub-view", view));
    }
  };
}

const bodyTab = group("body", "Body", "💪", [physique, diet, sleep]);
const learnTab = group("learn", "Learn", "🧠", [lessons, cyber, csmentor, projects, mathmod, pet]);
const TABS = [today, bodyTab, learnTab, progress];
const ALL = { today, body: bodyTab, learn: learnTab, progress, testmode, review, physique, diet, sleep, cyber, lessons, csmentor, projects, math: mathmod, pet };

function renderTabbar(activeId) {
  const nav = $("#tabbar");
  nav.innerHTML = TABS.map((t) => `
    <button class="tab ${t.id === activeId ? "active" : ""}" data-tab="${t.id}">
      <span class="ico">${t.ico}</span><span>${esc(t.label)}</span>
    </button>`).join("");
  nav.querySelectorAll("[data-tab]").forEach((b) =>
    b.addEventListener("click", () => { location.hash = `#${b.dataset.tab}`; }));
}

function renderTopbar() {
  const mode = S.appMode();
  const dLeft = S.daysToSummerEnd();
  const el = $("#topbar-right");
  const streak = S.computeStreak();
  const lp = S.levelProgress(S.getState().xp || 0);
  el.innerHTML = `
    <span class="pill xp" title="${lp.into}/${lp.need} XP to Lv ${lp.lvl + 1}">⚡ Lv ${lp.lvl}</span>
    ${streak > 0 ? `<span class="pill gold">🔥 ${streak}</span>` : ""}
    ${mode === "test"
      ? `<span class="pill accent">Proving Grounds</span>`
      : `<span class="pill">${dLeft >= 0 ? dLeft + "d to Sep 30" : "summer over"}</span>`}
    <button class="btn sm ghost" id="gear" aria-label="settings">⚙</button>`;
  $("#gear").addEventListener("click", openSettings);
}

function route(opts = {}) {
  const raw = (location.hash || "#today").slice(1);
  const [tabId, subId] = raw.split("/");
  let tab = ALL[tabId] && TABS.includes(ALL[tabId]) ? ALL[tabId] : (ALL[tabId] || today);
  // Route to testmode screen explicitly
  if (tabId === "testmode") tab = testmode;
  const activeTop = TABS.includes(tab) ? tab.id : "progress";

  renderTopbar();
  renderTabbar(activeTop);

  const y = opts.keepScroll ? window.scrollY : 0;
  const view = $("#view");
  view.classList.remove("enter");
  tab.render(view, subId);
  if (!opts.keepScroll) { void view.offsetWidth; view.classList.add("enter"); }
  document.body.dataset.mode = S.appMode();
  window.scrollTo(0, y);
}

function openSettings() {
  const s = S.getState();
  const m = openModal(`
    <h2>Settings</h2>
    <label class="field">Your name</label>
    <input id="set-name" value="${esc(s.profile.name)}" placeholder="Name" />
    <label class="field" style="margin-top:10px">Bodyweight (kg) — used for protein & load targets</label>
    <input id="set-bw" type="number" value="${esc(s.profile.bodyweightKg)}" style="width:100%" />

    <hr class="hr" />
    <label class="field">App mode</label>
    <div class="seg" style="display:flex; width:100%">
      ${["auto", "summer", "test"].map((v) => `<button data-mode="${v}" class="${s.settings.mode === v ? "on" : ""}" style="flex:1">${v}</button>`).join("")}
    </div>
    <p class="small dim" style="margin-top:6px">Auto flips to <b>Proving Grounds</b> on Sep 30, 2026.</p>

    <hr class="hr" />
    <label class="field">🤖 AI tutor — Gemini 2.5 Flash key (free)</label>
    <input id="set-ai" type="password" placeholder="paste API key" value="${esc(s.settings.geminiKey || "")}" />
    <div class="row" style="gap:8px; margin-top:8px">
      <button class="btn sm" id="set-ai-save" style="flex:1">Save key</button>
      <button class="btn sm primary" id="set-ai-test" style="flex:1">Test</button>
    </div>
    <p class="small dim" style="margin-top:6px">Get a free key at <span class="kbd">aistudio.google.com/apikey</span>. Powers the hands-on tutor, work reviews and hints. Stored only on this device.</p>
    <div id="set-ai-status" class="small" style="margin-top:4px"></div>

    <hr class="hr" />
    <label class="field">🧪 LockIn Lab address (desktop) — for sync & Lab-gated Focus</label>
    <input id="set-lab" placeholder="e.g. http://192.168.1.20:8765" value="${esc(s.settings.labUrl || "")}" />
    <div class="row" style="gap:8px; margin-top:8px">
      <button class="btn sm" id="set-lab-save" style="flex:1">Save</button>
      <button class="btn sm primary" id="set-lab-sync" style="flex:1">Sync now</button>
    </div>
    <p class="small dim" style="margin-top:6px">Open the Lab on your PC → ⚙ Settings → copy the "Phone sync URL" here. Same Wi-Fi.</p>
    <div id="set-lab-status" class="small" style="margin-top:4px"></div>

    <hr class="hr" />
    <label class="field">Simulate date (testing) — YYYY-MM-DD</label>
    <div class="row">
      <input id="set-date" placeholder="e.g. 2026-09-07" value="${esc(s.settings.debugDate || "")}" style="flex:1" />
      <button class="btn sm" id="set-date-clear">Clear</button>
    </div>

    <hr class="hr" />
    <div class="row" style="gap:10px">
      <button class="btn" id="set-install" style="flex:1">Install help</button>
      <button class="btn bad" id="set-reset" style="flex:1">Reset all data</button>
    </div>
    <div class="row" style="margin-top:14px">
      <button class="btn primary block" data-close style="flex:1">Done</button>
    </div>`);

  const commit = () => S.update((st) => {
    st.profile.name = $("#set-name").value.trim();
    st.profile.bodyweightKg = Number($("#set-bw").value) || st.profile.bodyweightKg;
  });
  m.querySelector("#set-name").addEventListener("change", commit);
  m.querySelector("#set-bw").addEventListener("change", commit);
  m.querySelectorAll("[data-mode]").forEach((b) => b.addEventListener("click", () => {
    S.update((st) => { st.settings.mode = b.dataset.mode; });
    closeModal(); route();
  }));
  m.querySelector("#set-date").addEventListener("change", (e) => {
    S.update((st) => { st.settings.debugDate = e.target.value.trim() || null; });
    closeModal(); route();
  });
  m.querySelector("#set-date-clear").addEventListener("click", () => {
    S.update((st) => { st.settings.debugDate = null; }); closeModal(); route();
  });
  m.querySelector("#set-ai-save").addEventListener("click", () => {
    AI.setKey($("#set-ai").value);
    toast(AI.hasKey() ? "AI key saved" : "Key cleared");
  });
  m.querySelector("#set-ai-test").addEventListener("click", async () => {
    AI.setKey($("#set-ai").value);
    const status = $("#set-ai-status");
    if (!AI.hasKey()) { status.innerHTML = `<span style="color:var(--warn)">Paste a key first.</span>`; return; }
    status.innerHTML = `<span class="dim">Testing…</span>`;
    try {
      await AI.gemini({ messages: [{ role: "user", text: "Reply with exactly: OK" }], temperature: 0 });
      status.innerHTML = `<span style="color:var(--good)">✓ Connected — the tutor is live.</span>`;
    } catch (e) {
      status.innerHTML = `<span style="color:var(--bad)">${esc(e.message === "NO_KEY" ? "No key set." : e.message)}</span>`;
    }
  });
  m.querySelector("#set-lab-save").addEventListener("click", () => {
    S.update((st) => { st.settings.labUrl = $("#set-lab").value.trim(); });
    toast("Lab address saved");
  });
  m.querySelector("#set-lab-sync").addEventListener("click", async () => {
    S.update((st) => { st.settings.labUrl = $("#set-lab").value.trim(); });
    const status = $("#set-lab-status");
    if (!Lab.labConfigured()) { status.innerHTML = `<span style="color:var(--warn)">Enter the Lab address first.</span>`; return; }
    status.innerHTML = `<span class="dim">Syncing…</span>`;
    try {
      const st = await Lab.syncNow();
      status.innerHTML = `<span style="color:var(--good)">✓ Synced — ${st.lessonsDone}/${st.lessonsTotal} lessons, ${st.solvedCount} solved, today's LeetCode: ${esc(st.leetToday.title)}${st.leetToday.solved ? " ✓" : ""}.</span>`;
    } catch (e) {
      status.innerHTML = `<span style="color:var(--bad)">${esc(e.message)}</span>`;
    }
  });
  m.querySelector("#set-install").addEventListener("click", installHelp);
  m.querySelector("#set-reset").addEventListener("click", () => {
    confirmModal({
      title: "Reset everything?", danger: true, yes: "Erase all data",
      body: "This wipes all your progress, logs and streaks. Cannot be undone.",
      onYes: () => { S.resetAll(); location.hash = "#today"; toast("All data reset"); route(); }
    });
  });
}

function installHelp() {
  openModal(`
    <h2>Install LockIn on your phone</h2>
    <p class="muted small">It runs offline once installed — no app store needed.</p>
    <ol class="list-plain small" style="padding-left:18px">
      <li>Publish once with the ready-made scripts — <b>no Git knowledge needed</b>: run <span class="kbd">setup-github.bat</span> the first time, then <span class="kbd">publish.bat</span> for updates (full walkthrough in <b>PUBLISH.md</b>).</li>
      <li>Or test on Wi-Fi: <span class="kbd">py -m http.server 8080</span> on the PC, open <span class="kbd">http://&lt;PC-IP&gt;:8080</span> on the phone.</li>
      <li>Open the URL in <b>Chrome</b> on the Redmi Note 13 Pro+.</li>
      <li>Tap the <b>⋮</b> menu → <b>Add to Home screen</b> / <b>Install app</b>.</li>
    </ol>
    <p class="small dim">Want to actually understand Git? That's a proper course now: <b>Learn → Cyber → Git School</b>.</p>
    <button class="btn primary block" data-close style="margin-top:12px">Got it</button>`);
}

function onboard() {
  const s = S.getState();
  if (s.settings.onboarded) return;
  const m = openModal(`
    <h2>Welcome — let's Lock In 🔒</h2>
    <p class="muted small">One system for the whole summer: train, study, and learn — all the way to <b>Sep 30</b>.
    Answer two quick things and you're set.</p>
    <label class="field" style="margin-top:8px">What should I call you?</label>
    <input id="ob-name" placeholder="Your name" />
    <label class="field" style="margin-top:10px">Bodyweight (kg)</label>
    <input id="ob-bw" type="number" value="62" style="width:100%" />
    <label class="field" style="margin-top:10px">🤖 AI tutor key (optional, recommended) — Gemini free key from aistudio.google.com/apikey</label>
    <input id="ob-ai" type="password" placeholder="paste Gemini key (or add later in Settings)" />
    <button class="btn primary block" id="ob-go" style="margin-top:16px">Start</button>`);
  m.querySelector("#ob-go").addEventListener("click", () => {
    S.update((st) => {
      st.profile.name = $("#ob-name").value.trim();
      st.profile.bodyweightKg = Number($("#ob-bw").value) || 62;
      st.settings.geminiKey = $("#ob-ai").value.trim();
      st.settings.onboarded = true;
    });
    closeModal(); route();
  });
}

function boot() {
  S.load();
  S.subscribe(() => { renderTopbar(); }); // keep streak/countdown fresh on any change
  window.addEventListener("hashchange", () => route());
  window.addEventListener("lockin:refresh", () => route({ keepScroll: true }));
  window.addEventListener("lockin:levelup", (e) => {
    confetti(40);
    buzz(40);
    toast(`⚡ LEVEL UP — you're now Lv ${e.detail.level}!`, 3200);
  });
  if (!location.hash) location.hash = "#today";

  // Desktop: the app is running on the PC next to the Lab. Point it at the local Lab by default so it
  // auto-connects when the Lab is running. (Set labUrl WITHOUT bumping updatedAt — it's device config,
  // not data — so a fresh PC install pulls the phone's data instead of pushing its empty state up.)
  const isDesktop = window.matchMedia("(min-width: 900px) and (pointer: fine)").matches;
  if (isDesktop) {
    document.documentElement.classList.add("is-desktop");
    if (!S.getState().settings.labUrl) { S.getState().settings.labUrl = "http://localhost:8765"; S.save(); }
  }

  route();
  onboard();
  Lab.startAppSync(); // keep phone and PC in step through the Lab hub

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("./service-worker.js").catch(() => {});
    });
  }
}

boot();
