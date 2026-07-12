# LockIn — Project Summary (handoff)

Single-file context for resuming work. LockIn is a personal system for one user, **Itamar** (18,
Israeli software-engineering student aiming for the IDF **GAMA Cyber** program), to hit five summer
goals by **September 6, 2026**. The program is anchored to a fixed start of **July 12, 2026** (Sunday).

It's **two apps** in this folder:
1. **Mobile PWA** (repo root) — routine, gym, diet, sleep, math, PET, CS-project mentor, cyber
   trackers/drills, progress, weekly review, test mode. Offline-first, for a Redmi Note 13 Pro+.
2. **LockIn Lab** (`Lab/`) — a desktop Python IDE hosting the hands-on cyber curriculum (lessons,
   Data Structures, daily LeetCode) with code execution and a Gemini tutor. Syncs to the phone.

---

## The five goals
1. **CS assignment** — finish `Local-CyberComm` (multithreaded server, SQLite auth, custom JSON
   protocol, GUI, WebRTC calls, file transfer) *while actually learning* (Socratic mentor, never solves).
2. **Physique** — grow chest, legs (weakest), abs, start obliques; fix forearms hijacking lifts; fix
   an under-eating diet and a wrecked sleep schedule (was asleep 4–7am → taper to 07:30).
3. **Cyber learning** — 10 tracks: Python, C#, C, ASM, Linux, high/low-level cyber, Windows CMD, Git,
   **Data Structures & Algorithms**. Build a daily study habit.
4. **PET ≥ 97%** — strong math/English, weak **Hebrew** (the priority). Course Sun & Wed 09:00–14:00.
5. **Math assignment** — do it FIRST (motivation/time problem), then keep-sharp for PET.

User stats (context/motivation): Dapar 90/90, Profile 72, top Tzav-Rishon cognitive scores.

---

## Mobile PWA — structure
Vanilla **ES modules + CSS + service worker** (cache `lockin-v9`), no build step. Single state
object in `localStorage` (`lockin.state.v1`). Serve with `python -m http.server 8080` (or the
`.claude/launch.json` server named **lockin**).

**Tabs:** Today · Body (Workout/Diet/Sleep) · Learn (Cyber/CS Project/**Portfolio**/Math/PET) ·
Progress.
**Extra routes:** `#review` (Weekly Review, Fridays), `#testmode` (Proving Grounds, ≥ Sep 6).

**Files**
- `index.html`, `manifest.webmanifest`, `service-worker.js`, `css/styles.css`
- `js/`: `app.js` (router/shell/settings), `state.js` (store, dates, XP, `PROGRAM_START`,
  `weekOf`/`weekRange`), `ui.js` (helpers: toast/modal/confetti/flashHTML/sparkSVG), `srs.js`
  (Leitner SR), `schedule.js` (routine engine, taper, rotations, day templates), `ai.js` (Gemini
  client), `focus.js` (Focus Lock), `lab.js` (Lab sync client).
- `js/modules/`: `today, progress, physique, diet, sleep, cyber, cs_mentor, projects, math, pet,
  offday, testmode, review`.
- `js/data/`: `workout_program, meals, cs_milestones, resume_projects, math_checklist, pet_content,
  pte_vocab (auto-gen from PTE/vocab.txt), cyber_decks, skill_tracks, gama_notes, git_lessons`.

**Key features**
- **Today**: timeblock routine anchored to Jul 12 (Sun–Thu study, Fri = Weekly Review, Sat rest);
  week strip; "NOW" highlight; protected end-of-day free time; **6 finite off-day tokens**; sleep
  taper banner to 07:30; a daily **LeetCode** block.
- **Focus Lock** (`focus.js`): fullscreen + Wake Lock + counts every time you leave; for cyber/leet
  blocks it's **Lab-gated** — polls the Lab and auto-unlocks when Lab work is done.
- **XP/levels** with confetti + haptics; day streak.
- **Body**: 5-day gym split (legs 2×, chest, abs, obliques) with an explicit **forearm-takeover
  fix**; progressive-overload set logger; diet as a 5-item checklist + protein/kcal targets +
  bodyweight sparkline; sleep taper log.
- **Learn/Cyber**: 10 skill tracks (self-assess + milestones), **4 SR flashcard decks**
  (Networks/ASM/Linux/CMD, 80 cards), **Git School** (6 gated lessons + quizzes), GAMA roadmap, and
  a **Lab sync card**. Hands-on lessons live in the Lab.
- **CS Project mentor**: `Local-CyberComm` milestones with a hint ladder (never full solutions),
  library memory-jog cards, and AI hint/review.
- **Portfolio** (`projects.js` + `resume_projects.js`): a ladder of **6 résumé-worthy projects**
  (port scanner, packet sniffer, encrypted vault, file-integrity monitor, HTTP server from scratch,
  C/ASM reverse-engineering write-up) across 3 tiers, built FROM SCRATCH to fix his AI-reliance
  weakness. Each project = retrieval-first design questions → nudge/specific/**outline** hint ladder
  (never solves) → **build-from-scratch mandate** → explain-back reflection → a "prove you own it"
  rebuild → a **Ship-it checklist** (Git repo + README + demo). Every project also carries a
  **`realUse`** line (what real tool this mirrors — nmap, Wireshark, 1Password, Tripwire, etc. — and
  how to actually use the finished build) plus a top-of-page **"Why these, and not just more
  exercises"** card, so the value is explicit, not implied. A **Résumé** sub-tab assembles shipped
  projects (+ the `Local-CyberComm` flagship when its milestones are all done) into a copy-paste CV
  "Projects" section, with a bullet-writing rubric and an AI bullet coach that critiques but never
  writes. XP: +15/stage, +10/ship-step, +25 ship bonus, +30 prove-it. Folds into the Progress
  **Learning** ring (learning = 0.5·track-ladder + 0.2·decks + 0.3·portfolio).
- **Math**: do-first checklist + keep-sharp rotation. **PET**: Hebrew 156 + English 249 vocab,
  20 math path-drills, 10 sentence completions, weighted **97% readiness gauge** (Hebrew weighted).
- **Weekly Review** (`review.js`, Fridays): cumulative recall test across ALL decks (this week +
  every prior week), scores, tracks improvement, grades cards into SR. Records in `state.reviews`.
- **Progress**: 5 goal rings + PET gauge + streak + off-days + XP + Tzav/Hundred-Day panel.
- **Test Mode** (≥ Sep 6): skill report card, GAMA-style rapid exam, from-scratch coding challenges.
- **AI tutor**: Gemini 2.5 Flash key in ⚙ Settings (also onboarding). Requests set
  `thinkingConfig.thinkingBudget: 0`, `maxOutputTokens: 2048`.

**Deploy**: static → GitHub Pages. Zero-Git-knowledge scripts: `setup-github.bat`, `publish.bat`,
`PUBLISH.md`. Install on phone = open the Pages URL in Chrome → Add to Home screen.

---

## LockIn Lab — structure (`Lab/`)
Pure Python **standard library** (tkinter + urllib), **PyCharm-style IDE**. Run:
`python Lab/lockin_lab.py` or double-click `Lab/Launch LockIn Lab.bat`.

**Files**: `lockin_lab.py` (app/IDE), `editor.py` (editor: gutter, syntax highlight, auto-indent),
`runner.py` (subprocess Python run; C via gcc; test harness), `content.py` + `leet.py` +
`courses.json` (curriculum), `sync.py` (local status server), `prompts.py` (tutor behavior),
`lab_state.json` (runtime: key, progress, solved, code drafts, xp, history), `LAB_README.md`.

**Content**: **60 lessons across 8 cyber tracks** + a **Data Structures & Algorithms** course
(12 lessons, auto-graded exercises) + **24 LeetCode problems** with a deterministic **daily** picker
(a Hard ~weekly). All test cases validated against reference solutions.

**Lesson effectiveness (built for retention + engagement, not passive reading)**: every cyber lesson
opens with a concise, factual **"Why it matters"** relevance line (`HOOKS` dict — plain statements of
the point/use, no jokes or hype; an earlier jokey version was cut for being cringe/misleading), then
the read sections, then a universal **teach-back / free-recall** prompt, then **interactive graded
CHECKS**. **DSA lessons stay lean** (leaner intro +
a `TELLS` dict giving each a "🎯 THE LEETCODE TELL" — how to recognise the pattern — so they teach
just what's needed to solve LeetCode, no theory rabbit-holes).

**Interactive graded checks (verify the user actually learns)**: the old click-to-reveal quiz is now
a real **graded check** — click an option, correct = green + **+3 XP** (live), wrong = red strike,
try again; passing all of a lesson's 4 checks reveals a celebration + **+10 bonus XP**, and **"Mark
done" is gated** behind passing every check (`_answer_check` / `_update_check_status` / gated
`act_done` in `lockin_lab.py`; per-lesson state in `state["checks"]`). **Addictive loop**: instant
feedback + rising XP counter + a **daily 🔥 streak** (`state["activeDays"]`, `_streak()`, shown in
the status bar AND synced to the phone via `snapshot()["streak"]` → rendered as a gold pill in the
phone's Lab card). Quiz coverage remains **60/60 lessons, 240 questions — 4 per lesson** (2 concept
+ code-reading + predict/spot-the-bug), authored in `QUIZZES` / `CODE_QUIZZES` / `PRACTICE_QUIZZES`
and attached in `build_courses()`. Verified: 110 exercise test cases still pass, all 240 quizzes
structurally valid (0 malformed), and headless renders of the real Lab confirm the hook, the tell,
graded-check flow (wrong→no XP, all-correct→+22 XP & celebration), done-gating, and the streak.

**Features**: left project tree (LeetCode Daily / Data Structures / Cyber courses / LeetCode Browse);
big editor; **▶ Run** (Python always, C if gcc); **✓ Run Tests** (auto-grade against cases) / **✓ AI
Check** (prose tasks); **💡 Hint / ❔ Ask / 📖 Explain**; per-track **capstones**. Tutor = Gemini 2.5
Flash (guide-only; rules in `prompts.py`: PERSONA + HINT/REVIEW/ASK/EXPLAIN). Same thinkingBudget:0.

---

## How the two connect
- Lab runs a local **status server** (`sync.py`, `GET /status`, open CORS, port 8765). ⚙ Settings in
  the Lab shows a **Phone sync URL** (LAN IP).
- Phone: ⚙ Settings → **LockIn Lab address** → paste URL → **Sync now**. The Cyber tab then shows
  synced lessons/solved/XP + today's LeetCode.
- **Phone unlock**: a Lab-gated Focus Lock polls `/status` and releases the phone when the Lab
  records finished work today. Same Wi-Fi required; graceful manual fallback if unreachable.

---

## Status: everything built & verified
All done and preview-verified: 11 mobile routes render error-free; July-12 anchoring correct (week
numbers, taper day 1 = 17:00, reset by ~Jul 25); Weekly Review scores/records/grades-into-SR;
Lab-gated auto-unlock works over real cross-origin fetch; SW v8 caches 38 same-origin assets; Lab
modules compile; runner handles correct/wrong/missing-fn/timeout; all 24 LeetCode + 34 DSA tests pass.

### Gotchas for a new session
- **SW rule**: the fetch handler MUST skip cross-origin (`url.origin !== self.location.origin`) or it
  caches Lab `/status` + Gemini (bug fixed in v5/v6). Bump `VERSION` when changing precache.
- **Gemini**: 2.5 Flash is a thinking model — always set `thinkingConfig.thinkingBudget: 0` or it can
  return empty text.
- **Verifying in preview**: MCP `preview_click` doesn't dispatch to handlers — drive with native
  `.click()` via `javascript_tool`/`preview_eval`. Keep long waits in Bash `sleep` between short evals
  (long-await evals hit the ~30s tool timeout). Live Gemini needs the user's own key.
- **Lab**: GUI can't run headless here — use `python -m py_compile` + logic tests. Test sync by
  running a `sync.py` server whose `completedTodayCount` increments per request and fetching it
  cross-origin from the preview.
- Dates: today ≈ 2026-07-11; program `PROGRAM_START = 2026-07-12`; `SUMMER_END = 2026-09-06`.
