# LockIn Lab 🧪 — the cyber Virtual Environment (desktop IDE)

The **desktop** half of LockIn. The phone app runs your day, training, math and PET; **this app
runs the hands-on cyber curriculum** in a real coding environment — because C, assembly, Linux,
networks and algorithms need a real terminal, a compiler, and room to write code.

It's a small **PyCharm-style IDE**: a project tree, a code editor with line numbers + syntax
highlighting, a **Run** button, and a **Run Tests** button that grades your LeetCode/DSA solutions
against real test cases. A **Gemini 2.5 Flash** tutor (free key) checks your code and helps only
when you ask. And it **syncs to your phone** so the phone's Focus Lock unlocks once you've done the
work here.

## Run it

1. Install **Python 3** from <https://www.python.org/downloads/> (tick *Add python.exe to PATH*).
2. Double-click **`Launch LockIn Lab.bat`** (or run `python lockin_lab.py`).
3. Click **⚙ Settings**, paste a free **Gemini API key** (<https://aistudio.google.com/apikey>),
   press **Test**. Optional but recommended.

No `pip install` — standard library only (tkinter + urllib). To run **C** exercises you also need
`gcc` on your PATH (or WSL); Python runs out of the box.

## What's inside

- **⭐ LeetCode — Daily**: a fresh problem each day (a **Hard** lands about weekly). Write your
  function, press **✓ Run Tests**, see each case pass/fail. Solving it records the win and syncs to
  your phone.
- **🧠 Data Structures & Algorithms**: a 12-lesson course (Big-O → arrays/hashing → sliding window →
  stacks/queues → linked lists → binary search → recursion/backtracking → trees/BFS/DFS →
  sorting/heaps → graphs → DP), each with an **auto-graded** coding exercise.
- **📚 Cyber courses**: Python, C#, C, x86 Assembly, Linux, Networks, Low-level, Windows CMD —
  **60 lessons total**, each with real teaching, a hands-on task, and (for coding tasks) the AI
  checker. Every track ends with a capstone project.
- **🧩 LeetCode — Browse**: the whole problem bank to practice any time.

## How to use it

- Pick something on the left. **Read** the lesson/problem in the right panel.
- Write code in the editor. Choose the language (Python / C) top-left.
- **▶ Run** executes your code and shows Output. **✓ Run Tests** grades an exercise/problem; **✓ AI
  Check** reviews a prose-task's code.
- Stuck? **💡 Hint** (instant built-in hint + an AI nudge), **❔ Ask**, **📖 Explain**.
- **▣ Lesson** hides the right panel for a full-width editor. **⟲ Reset** restores the starter code.

## Sync & phone-unlock

The Lab runs a tiny local server so the phone can read your progress over Wi-Fi:

1. In the Lab, **⚙ Settings** shows a **Phone sync URL** (e.g. `http://192.168.1.20:8765`).
2. On the phone: **⚙ Settings → LockIn Lab address** → paste it → **Sync now**. Your lesson count,
   solved problems and today's LeetCode now show on the phone's Cyber tab.
3. When the phone starts a **Lab-gated Focus Lock** for a cyber/LeetCode block, it watches the Lab
   and **unlocks itself automatically** the moment you finish a task here.

(Phone and PC must be on the same Wi-Fi. If they can't connect, everything still works locally.)

## How the tutor is told to behave

All behavior lives in editable prompts in **`prompts.py`** — a `PERSONA` (guide-don't-solve, help
only when necessary, be brief, make the student do the work, stay honest) plus strict modes:
**HINT** (a ladder, never the answer), **REVIEW** (verdict → what's right → the one fix, no
rewrite → nudge), **ASK**, **EXPLAIN**.

## Files

| File | What it is |
|------|------------|
| `lockin_lab.py` | The IDE app (tkinter). |
| `editor.py` | The code editor widget (gutter, highlighting, auto-indent). |
| `runner.py` | Runs code (Python; C via gcc) and the test harness. |
| `content.py` / `leet.py` / `courses.json` | The curriculum: courses, DSA, LeetCode bank. |
| `sync.py` | The local status server the phone reads. |
| `prompts.py` | The tutor's behavior rules. |
| `lab_state.json` | Auto-created: your key, progress, solved problems, code drafts, XP (local only). |
| `Launch LockIn Lab.bat` | Double-click launcher. |

Your key and code never leave this PC except when you press an AI button (sent to Gemini to answer)
or when your phone reads `/status` over your own Wi-Fi.
