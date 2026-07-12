// reading.js — curated "further reading" per learning track: articles, blogs and books that go
// deeper than the milestones. Free/online where possible; books noted for the library or a PDF.
// type is one of: book, blog, article, docs, interactive, video.

export const reading = {
  python: [
    { type: "book", title: "Fluent Python (Luciano Ramalho)", note: "The idiomatic-Python bible — the data model, generators, dunder methods." },
    { type: "blog", title: "Real Python", url: "https://realpython.com", note: "Clear, well-edited tutorials on every stdlib topic you'll hit." },
    { type: "docs", title: "Python docs — Functional HOWTO", url: "https://docs.python.org/3/howto/functional.html", note: "Iterators, generators and comprehensions, straight from the source." },
  ],
  csharp: [
    { type: "book", title: "C# in Depth (Jon Skeet)", note: "Why C# works the way it does — LINQ, generics, async." },
    { type: "docs", title: "Microsoft — C# guide", url: "https://learn.microsoft.com/dotnet/csharp/", note: "The official tour: properties, delegates, async/await, LINQ." },
    { type: "article", title: "101 LINQ Samples", url: "https://learn.microsoft.com/samples/dotnet/try-samples/101-linq-samples/", note: "Where/Select/OrderBy by example — skim, then rebuild from memory." },
  ],
  c: [
    { type: "book", title: "The C Programming Language (K&R)", note: "Short, dense, timeless. Chapters 1–6 cover most of what you need." },
    { type: "book", title: "Beej's Guide to C Programming", url: "https://beej.us/guide/bgc/", note: "Free, friendly, modern — great on pointers and memory." },
    { type: "interactive", title: "Compiler Explorer (godbolt.org)", url: "https://godbolt.org", note: "Write C, watch it become assembly — the fastest way to 'get' both." },
  ],
  asm: [
    { type: "book", title: "Programming from the Ground Up (Bartlett)", note: "Free PDF — builds x86 assembly up from nothing." },
    { type: "docs", title: "x86 Assembly (WikiBooks)", url: "https://en.wikibooks.org/wiki/X86_Assembly", note: "A reference for instructions, registers and calling conventions." },
    { type: "video", title: "LiveOverflow — Assembly / binary basics", url: "https://www.youtube.com/c/LiveOverflow", note: "Reading disassembly as a skill, exactly what the exam tests." },
  ],
  linux: [
    { type: "book", title: "The Linux Command Line (William Shotts)", url: "https://linuxcommand.org/tlcl.php", note: "Free PDF — the shell from navigation to scripting." },
    { type: "article", title: "MIT — The Missing Semester", url: "https://missing.csail.mit.edu/", note: "The command-line/tooling skills school never teaches." },
    { type: "interactive", title: "explainshell.com", url: "https://explainshell.com", note: "Paste any command and it explains every flag." },
  ],
  cyber_high: [
    { type: "article", title: "Cloudflare Learning Center", url: "https://www.cloudflare.com/learning/", note: "Short, clear explainers: TCP, DNS, TLS, HTTP — the whole stack." },
    { type: "book", title: "High Performance Browser Networking (Grigorik)", url: "https://hpbn.co/", note: "Free online — what really happens when you load a page." },
    { type: "book", title: "Computer Networking: A Top-Down Approach (Kurose & Ross)", note: "The standard networking textbook if you want the deep version." },
  ],
  cyber_low: [
    { type: "book", title: "Hacking: The Art of Exploitation (Jon Erickson)", note: "The classic that connects C, memory and exploitation." },
    { type: "video", title: "LiveOverflow — Binary Exploitation", url: "https://www.youtube.com/c/LiveOverflow", note: "Stacks, overflows and memory layout, shown live (defender's mindset)." },
    { type: "interactive", title: "pwn.college", url: "https://pwn.college/", note: "Structured, hands-on low-level security from the basics up." },
  ],
  cmd: [
    { type: "docs", title: "Microsoft — Windows Commands reference", url: "https://learn.microsoft.com/windows-server/administration/windows-commands/windows-commands", note: "Every built-in command with its switches." },
    { type: "docs", title: "SS64 — Windows CMD & PowerShell", url: "https://ss64.com/nt/", note: "The reference admins actually keep open." },
    { type: "book", title: "Learn PowerShell in a Month of Lunches", note: "The friendliest on-ramp once you outgrow cmd." },
  ],
  git: [
    { type: "book", title: "Pro Git (Chacon & Straub)", url: "https://git-scm.com/book", note: "Free, official, complete — the only Git book you need." },
    { type: "interactive", title: "Learn Git Branching", url: "https://learngitbranching.js.org/", note: "Visual, hands-on branching/merging drills in the browser." },
    { type: "article", title: "Oh Sh*t, Git!?!", url: "https://ohshitgit.com/", note: "How to undo the common mistakes — bookmark it." },
  ],
  dsa: [
    { type: "interactive", title: "NeetCode", url: "https://neetcode.io/", note: "The pattern-based roadmap for LeetCode, with clear video solutions." },
    { type: "book", title: "Grokking Algorithms (Aditya Bhargava)", note: "Illustrated, beginner-friendly — the ideas behind the patterns." },
    { type: "article", title: "Tech Interview Handbook", url: "https://www.techinterviewhandbook.org/", note: "Free: which topics matter and how to practice efficiently." },
  ],
};

export const READ_ICON = {
  book: "📕", blog: "✍️", article: "📄", docs: "📘", interactive: "🕹️", video: "▶️",
};
