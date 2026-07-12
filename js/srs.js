// srs.js — a small Leitner spaced-repetition scheduler used by every flashcard deck.
import { getState, todayKey, addDays } from "./state.js";

// Box -> days until next review. Box 0 = brand new / just failed (due today).
const INTERVALS = [0, 1, 3, 7, 16, 35];
export const MAX_BOX = INTERVALS.length - 1;

// Returns the persisted SR record for a card id (created lazily, not saved here).
export function cardRec(id) {
  const s = getState();
  if (!s.decks[id]) s.decks[id] = { box: 0, due: todayKey(), seen: 0 };
  return s.decks[id];
}

export function isDue(id) {
  const r = cardRec(id);
  return r.due <= todayKey();
}

// grade(id, true) promotes a box; grade(id, false) resets toward box 0.
export function grade(id, correct) {
  const r = cardRec(id);
  r.seen = (r.seen || 0) + 1;
  if (correct) r.box = Math.min(MAX_BOX, r.box + 1);
  else r.box = Math.max(0, r.box - 2);
  r.due = addDays(todayKey(), INTERVALS[r.box] || 0);
  return r;
}

// Deck stats over an array of card objects that each have an `id`.
export function deckStats(cards) {
  let due = 0, learned = 0, seen = 0;
  for (const c of cards) {
    const r = cardRec(c.id);
    if (r.due <= todayKey()) due++;
    if (r.box >= 3) learned++;
    if (r.seen > 0) seen++;
  }
  return { total: cards.length, due, learned, seen, mastery: cards.length ? learned / cards.length : 0 };
}

// Ordered queue of due cards (most overdue first, then unseen).
export function dueQueue(cards) {
  return cards
    .filter((c) => isDue(c.id))
    .sort((a, b) => {
      const ra = cardRec(a.id), rb = cardRec(b.id);
      if (ra.due !== rb.due) return ra.due < rb.due ? -1 : 1;
      return (ra.seen || 0) - (rb.seen || 0);
    });
}
