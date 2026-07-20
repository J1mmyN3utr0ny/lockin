// offday.js — finite off-day tokens. Spending one is a deliberate, confirmed choice:
// a guilt-free full break that preserves your streak, but the pool is small and never refills.
import * as S from "../state.js";
import { openModal, closeModal, confirmModal, toast, refresh } from "../ui.js";

export function isOffDay(key = S.todayKey()) {
  return S.getState().offDays.spent.includes(key);
}

export function openOffDayFlow(dateKey = S.todayKey()) {
  const left = S.offDaysLeft();
  if (isOffDay(dateKey)) {
    confirmModal({
      title: "Cancel this off-day?",
      body: "Give the token back and return to your normal routine for today.",
      yes: "Give token back", no: "Keep resting",
      onYes: () => {
        S.setOffDay(dateKey, false); // stamped so the cancel syncs to the other device
        toast("Off-day cancelled — token returned"); refresh();
      }
    });
    return;
  }
  if (left <= 0) {
    openModal(`
      <h2>No off-days left 🚫</h2>
      <p class="muted">You've spent all ${S.OFFDAY_TOKENS} off-days for the summer. That was the deal —
      they're finite on purpose. Shabbat is still a built-in light day and costs nothing.</p>
      <button class="btn primary block" data-close style="margin-top:12px">Back to it</button>`);
    return;
  }
  confirmModal({
    title: "Spend an off-day?",
    danger: true,
    yes: `Yes — spend 1 of ${left}`,
    no: "Not today",
    body: `This uses <b>1 of your ${left} remaining</b> off-days for the <b>whole summer</b>. A real, guilt-free break — your streak is safe. But once it's gone, it's gone. Waste it only if you truly need it.`,
    onYes: () => {
      S.setOffDay(dateKey, true); // stamped so taking an off-day on the phone shows on the desktop
      closeModal();
      toast("Off-day taken. Rest well. 🌙");
      refresh();
    }
  });
}
