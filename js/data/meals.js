// meals.js — fixes UNDER-eating by making food a checklist, not an appetite decision.
// Built around foods the user already eats (tuna!) and zero-cooking, high-protein options.

// Daily structure: 3 meals + 2 snacks. Ticking all 5 is the win condition, regardless of hunger.
// `frac` is each slot's share of the DAILY protein target (fractions sum to 1.0), so the
// five slot amounts always add up to the headline number instead of overshooting it.
// `time` is only the fallback — the Diet tab reads the real times from today's schedule.
export const mealSlots = [
  { id: "m1", label: "Breakfast", time: "08:00", frac: 0.22, ideas: [
    "3-4 eggs (scrambled/omelette) + 2 toast", "Greek yogurt (500g) + honey + oats",
    "Cottage cheese (250g) + bread + tomato", "Protein shake + banana + peanut butter"
  ] },
  { id: "s1", label: "Snack", time: "11:00", frac: 0.10, ideas: [
    "1 tuna can + crackers", "Handful of nuts + a glass of milk", "Chocolate milk (500ml)", "Protein bar"
  ] },
  { id: "m2", label: "Lunch", time: "13:00", frac: 0.25, ideas: [
    "Tuna pasta (2 cans + pasta + olive oil)", "Chicken breast + rice + veg",
    "Tuna sandwich x2 (whole meal) + egg", "Rice bowl + 2 eggs + tuna"
  ] },
  { id: "s2", label: "Snack (pre-gym)", time: "19:00", frac: 0.13, ideas: [
    "Protein shake + oats", "2 tuna cans on bread", "Greek yogurt + fruit", "Cottage cheese + granola"
  ] },
  { id: "m3", label: "Dinner (post-gym)", time: "21:40", frac: 0.30, ideas: [
    "Chicken/beef + rice/potato + salad", "Big tuna+egg rice bowl", "Family dinner — eat well and go back for seconds",
    "Pasta + tuna + cheese + side of yogurt"
  ] }
];

// Protein target scales with bodyweight; calories are a modest lean-bulk surplus.
export function targets(bwKg) {
  const proteinLow = Math.round(bwKg * 1.6);
  const proteinHigh = Math.round(bwKg * 2.2);
  // rough maintenance for a lean, active 18yo ~ bw*33; +300-400 surplus to grow
  const kcal = Math.round(bwKg * 33 + 400);
  return { proteinLow, proteinHigh, kcal };
}

export const tips = [
  "You don't need appetite — you need a checklist. Hit the 5 ticks even when you're not hungry.",
  "Liquid calories are your cheat code: milk, chocolate milk, and shakes add protein + calories without feeling full.",
  "Keep 6+ tuna cans, eggs, and yogurt stocked so a meal is always 60 seconds away.",
  "Friday dinner and going out are your best-eating days — lean into them, don't skip the leftovers.",
  "A missed meal is a missed set. Under-eating is the #1 thing capping your physique right now."
];
