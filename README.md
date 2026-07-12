# LockIn 🔒

A personal system that turns the whole summer into one plan — **train, study, and learn** — all the way to **September 6, 2026**, then flips into a testing mode to prove the skills stuck.

It comes in **two parts**:

1. **The mobile app** (this folder) — an offline-first PWA for the **Redmi Note 13 Pro Plus**: your daily routine, gym, diet, sleep, math, PET prep, the CS-project mentor, progress and Proving Grounds. Installs to the home screen, runs with no internet.
2. **[LockIn Lab](Lab/LAB_README.md)** (the `Lab/` folder) — a **desktop coding IDE** (Python) that hosts the **hands-on cyber curriculum**: a code editor with **Run** + **Run Tests**, **60 lessons** across 8 cyber tracks, a **Data Structures & Algorithms** course, and a **daily LeetCode** problem graded against real test cases. A Gemini tutor checks your code and helps only when asked. It **syncs to the phone** and can **unlock the phone's Focus Lock** once you finish your work. Double-click `Lab/Launch LockIn Lab.bat`.

Why split? C, assembly, Linux, networks and algorithms need a real keyboard, terminal and compiler — a phone can't do them justice. The phone runs your life; the Lab runs the deep cyber work, and the two stay in sync.

## The mobile app

## What it does

| Tab | What's inside |
|-----|----------------|
| **Today** | Your daily routine as check-off timeblocks, anchored to a fixed program start of **July 12, 2026** (Sun–Thu study, **Friday = Weekly Review**, Shabbat rest). Free time is protected at the end of every day. A finite pool of **6 off-days** you must deliberately spend. A sleep-reset banner walks your wake-time back to **07:30**. |
| **Weekly Review** | Every **Friday** the schedule runs a **cumulative recall test** — this week *and every week before it* — drawn from all your decks (Networks, Assembly, Linux, CMD, Hebrew + English vocab). It scores you, tracks improvement week over week, and grades each card into spaced repetition. |
| **Body** | **Workout** — a 5-day full-gym split (legs 2×, chest, abs, obliques) with the forearm-takeover fix baked in, plus a set logger that drives progressive overload. **Diet** — eating as a checklist (3 meals + 2 snacks), protein/calorie targets, tuna-friendly meals. **Sleep** — sleep/wake log + the taper. |
| **Learn** | **Cyber** — 10 skill tracks (incl. **Data Structures**), synced Lab progress + today's LeetCode, **four** spaced-repetition flashcard decks, **Git School** (6 lessons), and the GAMA roadmap. Hands-on lessons live in the **Lab**. **CS Project** — a Socratic mentor for Local-CyberComm (guides, never solves) with AI hint/review. **Math** — do-first checklist + keep-sharp rotation. **PET** — 156 Hebrew + 249 English words, 20 math path-drills and 10 sentence completions feeding a **97% readiness gauge**. |
| **Progress** | The five headline goals as rings, streak, off-days left, days to Sep 6, and your Tzav/Hundred-Day stats. |
| **Proving Grounds** | Unlocks on **Sep 6**: a skill report card, a GAMA-style rapid exam, and from-scratch coding challenges. |

All data lives on the device (localStorage) — no account, no server, nothing leaves the phone.

## Run it locally (for testing on the PC)

From this folder:

```bash
python -m http.server 8080
```

Then open <http://localhost:8080> in a browser. (A PWA must be served over http/https — opening `index.html` as a file won't load the modules.)

To open it **on the phone over Wi-Fi**: find the PC's IP (`ipconfig` → IPv4), then on the Redmi browse to `http://<PC-IP>:8080`.

## Install on the Redmi Note 13 Pro Plus

1. Serve it over **HTTPS** (GitHub Pages, below) or the local Wi-Fi URL above.
2. Open the URL in **Chrome** on the phone.
3. Tap **⋮ → Add to Home screen / Install app**.
4. Launch from the home screen — it opens full-screen and works offline.

## Deploy via GitHub Pages — no Git knowledge required

Publishing is fully scripted so it never blocks you:

- **First time:** double-click **`setup-github.bat`** and follow **[PUBLISH.md](PUBLISH.md)** (create the GitHub repo, paste its URL, flip on Pages).
- **Every update after:** double-click **`publish.bat`** — it stages, commits and pushes in one go.

Your app goes live at `https://<you>.github.io/lockin/` — open that on the phone and install it.

Learning Git *properly* is a separate, deliberate thing: **Learn → Cyber → Git School** in the app
is a 6-lesson course (concepts → commands → real-terminal practice → quiz) that takes the Git track
from none to medium.

## Editing the program

All curriculum content is data — tweak it without touching UI code:

- `js/data/workout_program.js` — the split, exercises, cues, forearm fix.
- `js/data/meals.js` — meals and protein/calorie targets.
- `js/data/skill_tracks.js` — the 9 tracks and their milestone ladders.
- `js/data/cyber_decks.js` — the Networks/Assembly flashcards.
- `js/data/cs_milestones.js` — the CS project milestones, hint ladders, library cards.
- `js/data/math_checklist.js` — map the section labels to your actual math packet.
- `js/data/pet_content.js` — Hebrew (156 words) + curated English vocab, math drills, sentence completions.
- `PTE/vocab.txt` → `js/data/pte_vocab.js` — 199 English words auto-parsed from your file (re-run the parser after editing the txt).
- `js/data/git_lessons.js` — the Git School lessons and quizzes.
- `js/data/gama_notes.js` — the GAMA selection roadmap.
- `Lab/` — the desktop IDE: `courses.json` + `content.py` (60 lessons + DSA), `leet.py` (LeetCode bank), `runner.py` (code/test execution), `sync.py` (phone sync), `prompts.py` (tutor rules). See `Lab/LAB_README.md`.
- `js/lab.js` — the phone's sync client to the Lab; Lab-gated unlock lives in `js/focus.js`.

## Tech notes

- Vanilla ES modules + CSS + a service worker (`service-worker.js` precaches the shell for offline).
- `js/state.js` is the single source of truth, autosaved to `localStorage`.
- `js/schedule.js` is the routine engine; `js/srs.js` is the Leitner spaced-repetition scheduler.
- Simulate any date (e.g. to preview Proving Grounds) via **⚙ Settings → Simulate date**.
