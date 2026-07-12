// math.js — the summer math assignment as a DO-FIRST checklist, then a keep-sharp rotation.
import * as S from "../state.js";
import { esc, barHTML, refresh, toast, confetti, buzz } from "../ui.js";
import { assignment, sections, keepSharp } from "../data/math_checklist.js";

function toggle(id) {
  let nowOn = false;
  S.update((st) => {
    nowOn = !st.math.checklist[id];
    st.math.checklist[id] = nowOn;
  });
  S.addXP(nowOn ? 15 : -15);
  if (nowOn) buzz();
  refresh();
}

export default {
  id: "math", label: "Math",
  render(view) {
    const c = S.getState().math.checklist;
    const done = sections.filter((s) => c[s.id]).length;
    const pct = (done / sections.length) * 100;
    const allDone = done === sections.length;

    view.innerHTML = `
      <div class="card" style="border-color:${allDone ? "rgba(52,211,153,.5)" : "var(--line)"}">
        <div class="row between">
          <div><h2 style="margin:0">${esc(assignment.title)}</h2><div class="small dim">${esc(assignment.source)}</div></div>
          <div class="ring" style="--p:${Math.round(pct)}; position:relative"><span>${done}/${sections.length}</span></div>
        </div>
        <div style="margin-top:10px">${barHTML(pct, "good")}</div>
        <p class="small" style="color:var(--gold); margin-top:10px">🥇 ${esc(assignment.why)}</p>
        <p class="small muted">${esc(assignment.strategy)}</p>
      </div>

      <div class="section-title">Checklist</div>
      <div id="ck"></div>

      <div class="card ${allDone ? "" : "tight"}" style="${allDone ? "border-color:rgba(52,211,153,.4)" : ""}">
        <div class="section-title">Keep-sharp for the PET ${allDone ? "" : "· unlocks when the assignment is done"}</div>
        ${allDone
          ? `<p class="small good" style="color:var(--good)">Assignment cleared 🎉 Now a light rotation to keep quant fresh:</p>
             <ul class="list-plain small">${keepSharp.map((k) => `<li>${esc(k)}</li>`).join("")}</ul>`
          : `<p class="small dim">Finish the checklist to unlock the keep-sharp rotation. One thing at a time — momentum first.</p>`}
      </div>`;

    const ck = view.querySelector("#ck");
    ck.innerHTML = sections.map((s) => {
      const on = !!c[s.id];
      return `<div class="block ${on ? "done" : ""}" data-sec="${s.id}">
        <div class="chk" data-sec="${s.id}">${on ? "✓" : ""}</div>
        <div class="body"><div class="t">${esc(s.label)}</div><div class="s">${esc(s.note)}</div></div>
      </div>`;
    }).join("");
    ck.querySelectorAll(".chk[data-sec]").forEach((el) =>
      el.addEventListener("click", () => {
        toggle(el.dataset.sec);
        if (sections.every((s) => S.getState().math.checklist[s.id])) {
          confetti(44);
          toast("Math assignment DONE. Off your plate. 🎉", 3200);
        }
      }));
  }
};
