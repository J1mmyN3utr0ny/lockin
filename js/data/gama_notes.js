// gama_notes.js — the GAMA Cyber selection roadmap, distilled from the Gama.docx the user attached,
// so the app trains exactly the subjects each stage tests.

export const stages = [
  {
    id: "s1", name: "Stage 1 — GAMA Questionnaire (שאלון גאמ\"א)",
    where: "Online, untimed, from the מתגייסים site.",
    tests: "Knowledge across computers, math and science. Many fail not from lack of knowledge but from not knowing HOW to fill it.",
    prep: ["Answer deliberately, not fast.", "Lean on your math/science strength.", "Know your terms both by USE and by DEFINITION."]
  },
  {
    id: "s2", name: "Stage 2 — Exam Day (יום מבחנים)",
    where: "At an Intelligence-corps facility. 12 exams, ~20 questions each, 3¼ hours total.",
    tests: "You pick which exams to take. Peek at the first 4 questions before committing — then you can't back out.",
    menu: ["Battle-calculator (invented language + 'memory-32' array logic)",
      "Invented network protocol (TCP/UDP/DHCP/ARP/IP concepts)",
      "Knowledge tests you choose: C#, JAVA, PYTHON, SECURITY, WEB, NETWORKS, WINDOWS, LINUX, C++, OOP, ASM"],
    prep: ["Go DEEP on 2-3 chosen topics rather than shallow on all.", "Your strongest picks: Python, Networks, ASM, OOP.",
      "Master the invented-language reading — it's your battle-calculator points.", "Personality inventory: 227 true/false items — answer honestly and consistently."]
  },
  {
    id: "s3", name: "Stage 3 — Development & Research Workshop (סדנה)",
    where: "In person, mentors present — asking for help does NOT lower your score.",
    tests: "Two parts: DEVELOPMENT (OOP exercise, CTF-flavored — C# recommended) and RESEARCH / BLACK-BOX (LOW LEVEL).",
    prep: ["Write OPEN, FLEXIBLE code — later stages add requirements without warning.",
      "Be ready to define: OOP principles, abstract class vs interface, which languages have a destructor.",
      "Show effort, curiosity, and willingness to learn — that's graded too."]
  },
  {
    id: "s4", name: "Stage 4 — Interviews (ראיונות)",
    where: "In person, per track.",
    tests: "Personal questions (school, family, strengths, hobbies) + professional questions on terms and code.",
    prep: ["Know your Stage-2 successes cold — they interview around what you did well.", "Terms by definition AND usage.", "Show maturity, seriousness, and passion for computers."]
  },
  {
    id: "s5", name: "Stage 5 — Personality inventory + Psychologist",
    where: "Online from home (a ~6-hour inventory), then a psychologist meeting.",
    tests: "Analyze images, complete sentences, deep personal questions probing weak points.",
    prep: ["Calm, steady, honest, accountable.", "Consistency between what you write and what you say."]
  }
];

// Where the user already stands — motivation, not noise.
export const yourEdge = {
  title: "You're already competitive",
  bullets: [
    "Dapar 90/90 and top cognitive scores put you in the range GAMA recruits from.",
    "Software-engineering track = you should get the Stage-1 questionnaire automatically.",
    "Strong math/science is exactly what Stage 1 and the battle-calculator reward.",
    "The gap to close is breadth (C, ASM, Linux, low-level) and turning 'can read code' into 'can build from scratch'."
  ]
};

export const subjectToTrack = {
  PYTHON: "python", "C#": "csharp", JAVA: "csharp", "C++": "c", C: "c",
  ASM: "asm", NETWORKS: "cyber_high", SECURITY: "cyber_high", WEB: "cyber_high",
  WINDOWS: "cmd", LINUX: "linux", OOP: "csharp"
};
