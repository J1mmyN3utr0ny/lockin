// progress.js — the dashboard: five headline goals, the 97% PET gauge, streak, off-days,
// countdown, and the "you're already competitive" stats panel.
import * as S from "../state.js";
import { esc, barHTML, ringHTML } from "../ui.js";
import { tracks } from "../data/skill_tracks.js";
import { milestones as csMs } from "../data/cs_milestones.js";
import { projects as resumeProjects } from "../data/resume_projects.js";
import { sections as mathSecs } from "../data/math_checklist.js";
import { allCards } from "../data/cyber_decks.js";
import { deckStats } from "../srs.js";
import { petReadiness } from "./pet.js";
import { taperTargets } from "../schedule.js";

function csPct() {
  const m = S.getState().cs.milestones;
  const done = csMs.filter((x) => (m[x.id] || {}).status === "done").length;
  return (done / csMs.length) * 100;
}
function mathPct() {
  const c = S.getState().math.checklist;
  return (mathSecs.filter((s) => c[s.id]).length / mathSecs.length) * 100;
}
// Portfolio: average project completion (build stages weighted with shipping) across the ladder.
function portfolioFrac() {
  const pj = S.getState().projects || {};
  let sum = 0;
  for (const p of resumeProjects) {
    const r = pj[p.id] || { stages: {}, ship: {} };
    const stages = r.stages || {}, ship = r.ship || {};
    const stageFrac = p.stages.length ? p.stages.filter((_, i) => (stages[i] || {}).done).length / p.stages.length : 0;
    const shipFrac = p.ship.length ? p.ship.filter((_, i) => ship[i]).length / p.ship.length : 0;
    sum += Math.min(1, 0.7 * stageFrac + 0.3 * shipFrac);
  }
  return resumeProjects.length ? sum / resumeProjects.length : 0;
}
function learningPct() {
  const sk = S.getState().skills;
  let sum = 0;
  for (const t of tracks) {
    const ms = (sk[t.id] || { milestones: {} }).milestones;
    const done = t.milestones.filter((_, i) => ms[i]).length;
    sum += done / t.milestones.length;
  }
  const ladder = sum / tracks.length;
  const decks = deckStats(allCards()).mastery;
  const portfolio = portfolioFrac();
  return 100 * (0.5 * ladder + 0.2 * decks + 0.3 * portfolio);
}
function physiquePct() {
  const s = S.getState();
  let k = S.todayKey(), workoutDays = 0, mealSum = 0, sleepHit = 0, sleepLogged = 0;
  for (let i = 0; i < 14; i++) {
    const wl = s.workoutLogs[k];
    if (wl && wl.ex && Object.values(wl.ex).some((a) => a.length)) workoutDays++;
    const meals = s.meals[k]; if (meals) mealSum += Object.values(meals).filter(Boolean).length / 5;
    const sl = s.sleep.logs[k];
    if (sl && sl.wake) { sleepLogged++; if (sl.wake <= taperTargets(k).wake) sleepHit++; }
    k = S.addDays(k, -1);
  }
  const consistency = Math.min(1, workoutDays / 10); // ~5/week
  const meal = mealSum / 14;
  const sleep = sleepLogged ? sleepHit / sleepLogged : 0;
  return 100 * (0.5 * consistency + 0.25 * meal + 0.25 * sleep);
}

const GOALS = [
  { id: "cs", name: "CS assignment", icon: "💻", link: "#learn/csmentor", pct: csPct, color: "#4f8cff" },
  { id: "phys", name: "Physique", icon: "💪", link: "#body/physique", pct: physiquePct, color: "#fb7185" },
  { id: "learn", name: "Learning", icon: "🧠", link: "#learn/cyber", pct: learningPct, color: "#34d399" },
  { id: "pet", name: "PET (→97%)", icon: "📝", link: "#learn/pet", pct: () => petReadiness().total, color: "#f472b6" },
  { id: "math", name: "Math assignment", icon: "📐", link: "#learn/math", pct: mathPct, color: "#22d3ee" }
];

export default {
  id: "progress", label: "Progress", ico: "📊",
  render(view) {
    const s = S.getState();
    const streak = S.computeStreak();
    const dLeft = S.daysToSummerEnd();
    const mode = S.appMode();
    const lp = S.levelProgress(s.xp || 0);

    const testBanner = mode === "test" ? `
      <div class="card" style="border-color:rgba(79,140,255,.5); background:linear-gradient(135deg,#12233f,#101a2e)">
        <b class="emoji">🎓 The summer is over — time to prove it.</b>
        <p class="small muted" style="margin:6px 0 10px">Proving Grounds is unlocked. Test whether the skills actually stuck.</p>
        <a class="btn primary block" href="#testmode">Enter Proving Grounds →</a>
      </div>` : "";

    view.innerHTML = `
      ${testBanner}
      <div class="grid3" style="margin-bottom:6px">
        <div class="card tight stat"><div class="n" style="color:var(--gold)">${streak}🔥</div><div class="l">Day streak</div></div>
        <div class="card tight stat"><div class="n" style="color:var(--good)">${S.offDaysLeft()}</div><div class="l">Off-days left</div></div>
        <div class="card tight stat"><div class="n">${dLeft >= 0 ? dLeft : 0}</div><div class="l">Days to Sep 30</div></div>
      </div>

      <div class="card tight">
        <div class="row between">
          <b>⚡ Level ${lp.lvl}</b>
          <span class="small muted">${lp.into} / ${lp.need} XP to Lv ${lp.lvl + 1}</span>
        </div>
        <div style="margin-top:8px">${barHTML(lp.pct, "violet")}</div>
        <p class="small dim" style="margin:6px 0 0">XP comes from doing: blocks +10 · meals +5 · sets +3 · cards +2 · milestones +8–25 · Git lessons +30 · project stages +15 · shipping a project +75.</p>
      </div>

      <div class="section-title">The five goals</div>
      <div id="goals"></div>

      <div class="card" style="border-color:rgba(245,196,81,.35)">
        <b class="emoji">🎖️ You're already competitive</b>
        <div class="grid2" style="margin-top:10px">
          <div class="stat"><div class="n" style="color:var(--good)">${esc(s.profile.stats.dapar)}</div><div class="l">Dapar</div></div>
          <div class="stat"><div class="n" style="color:var(--good)">${esc(s.profile.stats.profile)}</div><div class="l">Profile</div></div>
          <div class="stat"><div class="n">${esc(s.profile.stats.keshev)}</div><div class="l">Keshev</div></div>
          <div class="stat"><div class="n">${esc(s.profile.stats.hebrewCls)}</div><div class="l">Hebrew</div></div>
        </div>
        <p class="small muted" style="margin-top:10px">The gap to GAMA isn't raw ability — it's breadth (C, ASM, Linux, low-level) and turning "can read code" into "can build from scratch." That's exactly what this summer closes.</p>
        <div class="accordion" id="hd-acc">
          <div class="accordion-h" id="hd-h"><span class="small"><b>Hundred-Day breakdown</b></span><span class="chev">▶</span></div>
          <div id="hd" class="hidden" style="margin-top:8px"></div>
        </div>
      </div>`;

    const goals = view.querySelector("#goals");
    goals.innerHTML = GOALS.map((g) => {
      const p = Math.round(g.pct());
      return `<a class="card tight row between" style="text-decoration:none; color:inherit" href="${g.link}">
        <div class="row" style="gap:12px">
          <div class="ring" style="--sz:52px; --p:${p}; position:relative"><span style="font-size:12px">${p}%</span></div>
          <div><b>${g.icon} ${esc(g.name)}</b><div class="small dim">tap to open →</div></div>
        </div>
      </a>`;
    }).join("");

    const hd = view.querySelector("#hd");
    hd.innerHTML = Object.entries(s.profile.stats.hundred).map(([k, v]) => `
      <div style="margin-bottom:7px">
        <div class="row between small"><span>${esc(k)}</span><span class="muted">${v}/5</span></div>
        ${barHTML((v / 5) * 100, v >= 4 ? "good" : "")}
      </div>`).join("");
    view.querySelector("#hd-h").addEventListener("click", () => {
      hd.classList.toggle("hidden"); view.querySelector("#hd-acc").classList.toggle("open");
    });
  }
};
