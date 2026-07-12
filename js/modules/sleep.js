// sleep.js — sleep/wake logger + the taper toward a 07:30 wake.
import * as S from "../state.js";
import { esc, refresh, toast } from "../ui.js";
import { taperTargets } from "../schedule.js";

function last7Keys() {
  const out = [];
  let k = S.todayKey();
  for (let i = 0; i < 7; i++) { out.push(k); k = S.addDays(k, -1); }
  return out;
}

export default {
  id: "sleep", label: "Sleep",
  render(view) {
    const key = S.todayKey();
    const t = taperTargets(key);
    const s = S.getState();
    const log = s.sleep.logs[key] || { sleep: "", wake: "" };

    view.innerHTML = `
      <div class="card" style="border-color:rgba(139,92,246,.35)">
        <div class="section-title">Tonight's target</div>
        <div class="grid2">
          <div class="stat"><div class="n" style="color:#a78bfa">${t.sleep}</div><div class="l">Asleep by</div></div>
          <div class="stat"><div class="n" style="color:#22d3ee">${t.wake}</div><div class="l">Wake by</div></div>
        </div>
        <p class="small muted" style="margin-top:10px">
          The target is <b>07:30 wake</b> / <b>23:30 sleep</b> from day one — no easing in. Set the alarm across the room, get daylight within 10 minutes, and hold it. Consistency is what makes it stick.
        </p>
      </div>

      <div class="card">
        <div class="section-title">Log last night</div>
        <div class="row" style="gap:12px">
          <div style="flex:1"><label class="field">Fell asleep</label><input type="time" id="sl-sleep" value="${esc(log.sleep)}" style="width:100%"></div>
          <div style="flex:1"><label class="field">Woke up</label><input type="time" id="sl-wake" value="${esc(log.wake)}" style="width:100%"></div>
        </div>
        <button class="btn primary block" id="sl-save" style="margin-top:12px">Save</button>
      </div>

      <div class="card">
        <div class="section-title">Last 7 days</div>
        <div id="sl-hist"></div>
      </div>

      <div class="card">
        <div class="section-title">Why this matters</div>
        <ul class="list-plain small muted">
          <li>A late, drifting sleep cycle is the single biggest drag on training, appetite and focus — so this snaps to 07:30 now, not gradually.</li>
          <li>Fixing wake-time (not bedtime) is the lever — get morning light within 10 min of waking, even on a rough night.</li>
          <li>The first few days are the hardest; push through and it locks in. No screens in the wind-down block — it's already in your Today schedule.</li>
        </ul>
      </div>`;

    const hist = view.querySelector("#sl-hist");
    hist.innerHTML = last7Keys().map((k) => {
      const l = s.sleep.logs[k];
      const tt = taperTargets(k);
      const hit = l && l.wake && l.wake <= tt.wake;
      return `<div class="row between" style="padding:6px 0; border-bottom:1px solid var(--line)">
        <span class="small">${esc(S.DAY_NAMES[S.dow(k)].slice(0,3))} ${esc(k.slice(5))}</span>
        <span class="small muted">${l && l.sleep ? esc(l.sleep) : "—"} → ${l && l.wake ? esc(l.wake) : "—"}</span>
        <span class="pill ${hit ? "good" : ""}">${l && l.wake ? (hit ? "on target" : "target " + tt.wake) : "no log"}</span>
      </div>`;
    }).join("");

    view.querySelector("#sl-save").addEventListener("click", () => {
      const sleepV = view.querySelector("#sl-sleep").value;
      const wakeV = view.querySelector("#sl-wake").value;
      S.update((st) => { st.sleep.logs[key] = { sleep: sleepV, wake: wakeV }; });
      toast("Sleep logged"); refresh();
    });
  }
};
