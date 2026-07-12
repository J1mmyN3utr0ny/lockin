// skill_tracks.js — the 9 learning goals as milestone ladders (current -> end-of-summer target).
// Levels use the shared scale: none, low, low-med, medium, med-high, high.

export const tracks = [
  {
    id: "python", name: "Python", icon: "🐍", from: "medium", to: "high",
    gama: "GAMA exam-day Python test; also the language of your CS project.",
    why: "You can read/analyze code well — this track pushes you into writing from scratch and owning the standard library.",
    milestones: [
      "Rebuild one old project from an empty file, no AI — just docs.",
      "OOP deep-dive: abstract base classes, @property, dunder methods, composition vs inheritance.",
      "Master iterators/generators + comprehensions; know when each saves memory.",
      "Decorators & context managers (`with`), and write your own of each.",
      "Concurrency: threading vs asyncio — build a tiny echo server both ways.",
      "sqlite3 + json + hashlib from memory (no snippet lookups).",
      "Package a script into a runnable module with argparse."
    ],
    resources: ["docs.python.org stdlib", "Your CS project is the perfect forcing function — see Learn → CS Project"]
  },
  {
    id: "csharp", name: "C#", icon: "🎯", from: "low-med", to: "high",
    gama: "GAMA RECOMMENDS C# for the OOP workshop (the CTF-style exercise). Highest-leverage language track.",
    why: "You know Java — most of OOP transfers. This track is mostly mapping Java habits onto C# idioms.",
    milestones: [
      "Java→C#: namespaces vs packages, properties (get/set) vs getters, `var`, string interpolation.",
      "Collections: List<T>, Dictionary<K,V>, and LINQ (Where/Select/OrderBy).",
      "Interfaces + abstract classes + a destructor/`IDisposable` (GAMA asks which languages have destructors!).",
      "Delegates, events, and lambda expressions.",
      "async/await and Tasks.",
      "Build the GAMA-style OOP exercise: a car-importer system (models, plates, HP, add-ons) that's easy to extend.",
      "Do a 3-stage 'add a feature each stage' drill without rewriting earlier code (open/closed)."
    ],
    resources: ["learn.microsoft.com/dotnet/csharp", "Practice extendable OOP — GAMA adds requirements stage by stage"]
  },
  {
    id: "c", name: "C", icon: "🔩", from: "none", to: "med-high",
    gama: "Foundation for low-level cyber, ASM, and the research (LOW LEVEL) workshop.",
    why: "C forces you to understand memory — the thing that makes low-level cyber click.",
    milestones: [
      "Compile & run with gcc; understand the compile→link→run pipeline.",
      "Types, `printf`/`scanf`, arrays and C-strings (null terminator).",
      "Pointers: address-of, dereference, pointer arithmetic.",
      "structs + typedef; arrays of structs.",
      "Dynamic memory: malloc/free, and what a memory leak / dangling pointer is.",
      "Bitwise ops (& | ^ ~ << >>) and building bit flags.",
      "Write a small program that parses a binary buffer by bytes."
    ],
    resources: ["'The C Programming Language' (K&R) ch.1-6", "godbolt.org to see C become ASM"]
  },
  {
    id: "asm", name: "Assembly (x86)", icon: "⚙️", from: "none", to: "medium",
    gama: "Exam-day ASM test + 'memory-32' / battle-calculator questions.",
    why: "You don't need to write huge programs — you need to READ it and know the terms cold.",
    milestones: [
      "Registers (eax/ebx/ecx/edx/esi/edi/esp/ebp) and what each is conventionally for.",
      "mov / add / sub / cmp / jmp / conditional jumps (JNE, JE...).",
      "The stack: push/pop, call/ret, and a stack frame (EBP/ESP).",
      "Flags: zero flag, carry flag — how cmp sets them.",
      "loop instruction and translating a for-loop to ASM.",
      "syscalls: int 0x80 (Linux) / int 0x21 (DOS).",
      "Read a short disassembly and explain what it does."
    ],
    resources: ["Deck: Learn → Cyber → Assembly", "godbolt.org — write C, read the ASM it emits"]
  },
  {
    id: "linux", name: "Linux", icon: "🐧", from: "low", to: "medium",
    gama: "Exam-day Linux test; the research workshop lives closer to Unix.",
    why: "Daily driver fluency: move around, manage files/permissions, chain commands.",
    milestones: [
      "Filesystem layout + navigation: pwd, ls, cd, absolute vs relative paths.",
      "Files: cat, less, cp, mv, rm, mkdir, touch, find.",
      "Permissions: rwx, chmod, chown, sudo.",
      "Pipes & redirection: |, >, >>, grep, wc.",
      "Processes: ps, top, kill, & and jobs.",
      "Package manager basics (apt) + editing a file in nano/vim.",
      "Write a 10-line bash script with a loop and an if."
    ],
    resources: ["Install WSL on Windows for a real Linux shell", "linuxjourney.com"]
  },
  {
    id: "cyber_high", name: "Cyber — high level", icon: "🌐", from: "low", to: "high",
    gama: "Exam-day Networks + the invented-protocol exercise; your GAMA course already covers this to med-high.",
    why: "Protocols and how data actually moves. Pairs directly with your CS networking project.",
    milestones: [
      "OSI / TCP-IP layers — place each protocol on a layer.",
      "TCP vs UDP: when and why each; the 3-way handshake.",
      "IP, ARP, DHCP, DNS — trace 'open a website' end to end.",
      "HTTP (GET/POST, status codes) + HTTPS/TLS at a high level.",
      "NAT, ports, sockets, and the client/server model.",
      "Capture real traffic in Wireshark and identify the handshake.",
      "Explain every card in the Networks deck out loud (mastery)."
    ],
    resources: ["Deck: Learn → Cyber → Networks", "Your GAMA course covers this — this track keeps it fresh"]
  },
  {
    id: "cyber_low", name: "Cyber — low level", icon: "🧬", from: "low", to: "med-high",
    gama: "The LOW-LEVEL research workshop + memory/bit questions on exam day.",
    why: "Bits, bytes, and memory — how the machine really represents everything.",
    milestones: [
      "Number bases: binary ↔ hex ↔ decimal by hand.",
      "Bit operations & masks; two's complement for negatives.",
      "Endianness (little vs big) and reading a hex dump.",
      "Memory layout of a process: stack, heap, data (.data/.bss), code (.text).",
      "malloc/free and what a buffer overflow conceptually is.",
      "Executable formats: PE (MZ header) vs ELF, sections & RVAs.",
      "Explain every card in the Assembly deck (mastery)."
    ],
    resources: ["Deck: Learn → Cyber → Assembly", "CyberChef for base/bit conversions"]
  },
  {
    id: "cmd", name: "Windows CMD", icon: "🖥️", from: "low", to: "high",
    gama: "Exam-day Windows test; your GAMA course takes CMD to 'high'.",
    why: "Fast, native network + system recon from the terminal.",
    milestones: [
      "Navigation & files: cd, dir, type, copy, move, del, mkdir.",
      "Networking: ipconfig (/all /release /renew /flushdns), ping, tracert.",
      "nslookup — you already built a DNS tool in Python; map it to the CLI.",
      "netstat -ano, tasklist, taskkill — see connections & processes.",
      "arp -a, route print, getmac.",
      "Pipes/redirection: |, >, findstr; chaining with && and ||.",
      "Write a small .bat script."
    ],
    resources: ["Your nslookup project mirrors the CLI tool", "ss64.com/nt CMD reference"]
  },
  {
    id: "git", name: "Git", icon: "🌿", from: "none", to: "medium",
    gama: "Professional baseline; you'll use it for every future project.",
    why: "Taught properly in Git School (Learn → Cyber → Git School): 6 lessons with commands, practice and quizzes. Publishing the app itself is scripted (publish.bat) and needs none of this.",
    milestones: [
      "Git School Lesson 1 — what Git is (snapshots, the three zones).",
      "Git School Lesson 2 — first commits (add, commit, log, .gitignore).",
      "Git School Lesson 3 — reading history & undoing (diff, restore, revert).",
      "Git School Lesson 4 — branches & merges (switch -c, merge, conflicts).",
      "Git School Lesson 5 — remotes & GitHub (clone, push, pull).",
      "Git School Lesson 6 — the professional loop (pull→branch→commit→push).",
      "Put your CS project under Git: one commit per milestone from now on."
    ],
    resources: ["Git School: Learn → Cyber → Git School", "learngitbranching.js.org (visual practice)"]
  },
  {
    id: "dsa", name: "Data Structures & Algorithms", icon: "🧠", from: "low", to: "high",
    gama: "The core skill behind coding interviews, the battle-calculator, and every real project.",
    why: "Taught hands-on in LockIn Lab (desktop): 12 lessons + auto-graded exercises, then a daily LeetCode problem the Lab tests for you. This card just tracks your levels.",
    milestones: [
      "Big-O: judge speed before coding.",
      "Arrays & two pointers; hash maps/sets (the #1 tool).",
      "Sliding window; stacks & queues.",
      "Linked lists; binary search.",
      "Recursion & backtracking; trees + BFS/DFS.",
      "Sorting & heaps; graphs & connectivity.",
      "Dynamic programming — recognize and set up the recurrence.",
      "Capstone: a 7-day LeetCode streak incl. one Hard."
    ],
    resources: ["LockIn Lab → Data Structures track + LeetCode Daily", "neetcode.io roadmap (reference)"]
  }
];

export function trackById(id) { return tracks.find((t) => t.id === id); }
