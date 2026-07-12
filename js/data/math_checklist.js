// math_checklist.js — the summer math assignment as a DO-FIRST checklist, plus a keep-sharp
// rotation for after it's done. Section labels map to the user's packet (ספר 572 / עבודת קיץ יא–יב);
// edit the labels if your PDF splits differently — the point is momentum, not perfect naming.

export const assignment = {
  title: "Math summer assignment",
  source: "עבודת קיץ יא–יב · ספר 572",
  why: "For you this is a MOTIVATION + TIME problem, not a difficulty one. You wanted it done before everything else — so it's front-loaded and chunked small. Clear it, then keep math warm for the PET.",
  strategy: "Two focused sessions and it's gone. Don't aim for elegant — aim for DONE and correct."
};

// Break it into small, tickable chunks so starting is easy.
export const sections = [
  { id: "m0", label: "Read the cover page + submission rules", note: "Know the deadline and format before you write anything." },
  { id: "m1", label: "ספר 572 · §3.8 — solve the problem set", note: "First block. Just start — you know this material." },
  { id: "m2", label: "ספר 572 · §4.8 — solve the problem set", note: "Second block." },
  { id: "m3", label: "Extra problems 1–7", note: "Grind through; check answers as you go." },
  { id: "m4", label: "Extra problems 8–14", note: "Second half of the problem sheet." },
  { id: "m5", label: "Graphs / function analysis questions", note: "The parts that need a sketch." },
  { id: "m6", label: "Review every answer once", note: "Catch silly mistakes — you lose 100s to these, not to hard math." },
  { id: "m7", label: "Write up cleanly + submit", note: "Done. Free your head for the PET and CS project." }
];

// After the assignment: light rotation to stay sharp for the Psychometric quantitative section.
export const keepSharp = [
  "Word problems: rate/work/mixture — translate to equations fast.",
  "Percentages & ratios under time pressure.",
  "Geometry: areas, similar triangles, circle facts.",
  "Algebra: quadratics, inequalities, systems.",
  "Sequences & averages tricks.",
  "Graph/function reading (fastest-path, not full solving).",
  "Powers, roots and exponent rules.",
  "Probability & counting basics."
];
