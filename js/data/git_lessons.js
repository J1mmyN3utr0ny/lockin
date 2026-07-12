// git_lessons.js — Git School: a proper 6-lesson course (concepts → commands → practice → quiz).
// Publishing this app does NOT require these lessons — publish.bat handles that. These make Git
// a skill you actually own (target level: medium).

export const gitIntro = {
  title: "Git School 🌿",
  blurb: "Six short lessons, ~10 minutes each. Read the idea, study the commands, do the practice in a real terminal, then pass the quiz. Complete them in order — each builds on the last.",
  note: "Publishing LockIn needs zero Git knowledge (that's scripted in publish.bat). This course is so that, by September, Git is simply a tool you know."
};

export const lessons = [
  {
    id: "gl1", title: "Lesson 1 · What Git actually is", time: "~8 min",
    concepts: [
      "Git is a time machine for a folder. Every 'commit' is a snapshot of ALL your files at one moment, with a message describing what changed. You can always go back to any snapshot.",
      "A 'repository' (repo) is just a normal folder where Git keeps that snapshot history — hidden inside a .git subfolder. Delete .git and it's a normal folder again.",
      "Git has three zones: the WORKING DIRECTORY (your actual files), the STAGING AREA (the changes you've marked 'include this in the next snapshot'), and the HISTORY (committed snapshots). Almost every Git command moves changes between these three.",
      "Why it matters for you: every serious codebase — including everything you'll touch in GAMA and high-tech — lives in Git."
    ],
    commands: [
      { cmd: "git init", what: "Turn the current folder into a repo (creates .git). Done once per project." },
      { cmd: "git status", what: "The command you'll run most: shows what changed and which zone each change is in." },
      { cmd: "git --version", what: "Check Git is installed at all." }
    ],
    practice: "Make a new folder anywhere, open a terminal in it, run git init, then git status. Read every word of the output — Git literally tells you what to do next.",
    quiz: [
      { q: "A commit is best described as…", options: ["A backup of one file", "A snapshot of the whole project at a moment in time", "A sync with GitHub", "A zip archive"], answer: 1, why: "A commit records the state of ALL tracked files, plus a message — a point you can return to." },
      { q: "The staging area is…", options: ["Where deleted files go", "The GitHub server", "The set of changes marked for the NEXT commit", "A backup folder"], answer: 2, why: "You stage (git add) exactly what the next snapshot should include — nothing more." },
      { q: "What makes a folder a Git repo?", options: ["A GitHub account", "The hidden .git folder created by git init", "A README file", "An internet connection"], answer: 1, why: "All history lives in .git. No server or internet is involved at all." }
    ]
  },
  {
    id: "gl2", title: "Lesson 2 · Your first commits", time: "~10 min",
    concepts: [
      "The core loop of all Git work is: edit files → git add (stage) → git commit (snapshot). You'll do this thousands of times in your career.",
      "git add chooses WHAT goes into the snapshot. 'git add .' stages everything; 'git add file.py' stages one file. This is why you can make a focused commit even after editing ten files.",
      "A commit message answers 'what does this change do?' in one line. 'Fix login crash when username is empty' — good. 'stuff' — useless six months later.",
      "A .gitignore file lists things Git should never track: __pycache__/, .env with passwords, huge binaries. It keeps the history clean."
    ],
    commands: [
      { cmd: "git add <file>  /  git add .", what: "Stage one file / everything changed." },
      { cmd: "git commit -m \"message\"", what: "Snapshot everything staged, with a message." },
      { cmd: "git log --oneline", what: "The history: one line per commit, newest first." },
      { cmd: "git diff", what: "Exactly what changed and is NOT yet staged." },
      { cmd: ".gitignore", what: "A text file of patterns Git must ignore (one per line)." }
    ],
    practice: "In your practice repo: create hello.py, add + commit it ('Add hello script'). Edit it, run git diff to see the change, then add + commit again. Run git log --oneline — you now have history.",
    quiz: [
      { q: "You edited 5 files but want to commit only one. What do you run before git commit?", options: ["git commit -all", "git add <that file>", "git push", "git init"], answer: 1, why: "Staging is the filter: add only what belongs in this snapshot." },
      { q: "Which is the best commit message?", options: ["update", "changes", "Add length-prefix framing to protocol", "final version 2 REAL"], answer: 2, why: "It says exactly what the snapshot does — readable in history forever." },
      { q: "__pycache__/ keeps appearing in git status. The right fix is…", options: ["Delete Python", "Commit it once so Git stops asking", "Add __pycache__/ to .gitignore", "Rename the folder"], answer: 2, why: "Generated files never belong in history — ignore them." }
    ]
  },
  {
    id: "gl3", title: "Lesson 3 · Reading history & undoing", time: "~10 min",
    concepts: [
      "History is only useful if you can read it: git log shows commits, git show <id> shows what one commit changed, git diff compares states.",
      "Undo has levels. Unstaged mess in a file? git restore <file> throws it away. Staged by mistake? git restore --staged <file> unstages. Bad commit already made? git revert <id> creates a NEW commit that cancels it.",
      "git reset --hard moves you back to a commit and DESTROYS everything after it. Powerful, occasionally right, dangerous — know it exists, reach for revert first.",
      "HEAD is just 'where you are now' — the commit your working directory is based on."
    ],
    commands: [
      { cmd: "git log --oneline --graph", what: "Compact history with branch structure drawn." },
      { cmd: "git show <commit>", what: "Everything that one commit changed." },
      { cmd: "git restore <file>", what: "Discard uncommitted changes to a file (careful — gone is gone)." },
      { cmd: "git restore --staged <file>", what: "Un-stage without losing the edit." },
      { cmd: "git revert <commit>", what: "Safely undo a commit by adding its opposite." }
    ],
    practice: "In the practice repo: break hello.py on purpose, then git restore it. Then make a bad commit and git revert it. Check git log — the revert is itself a commit.",
    quiz: [
      { q: "You ruined a file but haven't committed. Fastest fix?", options: ["git revert", "git restore <file>", "git reset --hard on the whole repo", "Delete the repo"], answer: 1, why: "restore throws away uncommitted changes to that one file." },
      { q: "A bad commit is already in history (and shared). The SAFE undo is…", options: ["git revert <commit>", "git reset --hard", "Edit .git by hand", "git rm"], answer: 0, why: "revert adds a canceling commit — history stays intact for everyone." },
      { q: "HEAD is…", options: ["The first commit ever", "The GitHub homepage", "The commit your working directory currently sits on", "The largest file"], answer: 2, why: "HEAD = 'you are here' in the history graph." }
    ]
  },
  {
    id: "gl4", title: "Lesson 4 · Branches", time: "~12 min",
    concepts: [
      "A branch is a movable label on a chain of commits — a parallel line of work. 'main' is just the default label, nothing magic.",
      "The workflow: branch off main → commit your experiment there → if it works, merge it back; if not, delete the branch. main never saw your mess.",
      "Merging usually 'just works'. A CONFLICT happens only when two branches changed the SAME lines — Git marks the spot with <<<<<<< / ======= / >>>>>>> and you pick what stays, then commit.",
      "This is how teams of hundreds work on one codebase at once — and why interviewers care that you get it."
    ],
    commands: [
      { cmd: "git branch", what: "List branches (* marks where you are)." },
      { cmd: "git switch -c feature-x", what: "Create AND move to a new branch." },
      { cmd: "git switch main", what: "Jump back to main." },
      { cmd: "git merge feature-x", what: "From main: bring feature-x's commits in." },
      { cmd: "git branch -d feature-x", what: "Delete a branch you're done with." }
    ],
    practice: "Practice repo: git switch -c experiment, change hello.py, commit. Switch to main — the file reverts before your eyes. Merge experiment back, then delete the branch. Bonus: engineer a conflict (change the same line on both branches) and resolve it.",
    quiz: [
      { q: "A branch is really…", options: ["A copy of the whole folder", "A movable pointer to a line of commits", "A different repo", "A GitHub feature"], answer: 1, why: "Branches are just labels on the commit graph — that's why they're instant and free." },
      { q: "Merge conflicts happen when…", options: ["Two branches exist", "The internet drops", "Two branches edited the same lines", "You forget to push"], answer: 2, why: "If changes don't overlap, Git merges silently; overlapping lines need a human." },
      { q: "The main reason to branch for an experiment is…", options: ["It runs faster", "main stays clean if the experiment fails", "GitHub requires it", "It compresses files"], answer: 1, why: "Fail safely: delete the branch and main never knew." }
    ]
  },
  {
    id: "gl5", title: "Lesson 5 · Remotes & GitHub", time: "~12 min",
    concepts: [
      "Everything so far was local. A REMOTE is a copy of the repo on a server — GitHub is the most common host. The remote is conventionally named 'origin'.",
      "git push uploads your new commits to the remote; git pull downloads commits others (or you, from another machine) pushed. git clone copies an entire existing repo to a new machine.",
      "Nothing syncs automatically. Git only moves history when you explicitly push or pull — you're always in control.",
      "GitHub adds the social layer: sharing, issues, pull requests, and free static hosting (Pages) — which is exactly how LockIn gets onto your phone."
    ],
    commands: [
      { cmd: "git clone <url>", what: "Copy a whole remote repo (history included) to this machine." },
      { cmd: "git remote add origin <url>", what: "Connect a local repo to a server copy, once." },
      { cmd: "git push -u origin main", what: "First upload (—u remembers the pairing; later just git push)." },
      { cmd: "git push / git pull", what: "Send my new commits / fetch + merge theirs." }
    ],
    practice: "Create a free GitHub account if you don't have one. Make an empty repo named lockin, then connect and push this very folder — or just run setup-github.bat, then READ what it did line by line. That script is this lesson.",
    quiz: [
      { q: "'origin' is…", options: ["The first commit", "The conventional name for your main remote", "A branch", "The .git folder"], answer: 1, why: "It's just the default nickname for the server copy's URL." },
      { q: "You committed locally. GitHub doesn't show it. Why?", options: ["The commit failed", "You haven't pushed", "GitHub is down", "You need a new branch"], answer: 1, why: "Commits are local until you push — Git never syncs on its own." },
      { q: "git clone vs git pull:", options: ["Identical", "clone copies a whole repo fresh; pull updates one you already have", "pull is for branches only", "clone is GitHub-only"], answer: 1, why: "Clone once to get it; pull thereafter to stay current." }
    ]
  },
  {
    id: "gl6", title: "Lesson 6 · The professional loop", time: "~10 min",
    concepts: [
      "The daily rhythm you'll use on every project from now on: pull → branch → edit → add → commit → push → merge. Run it until it's muscle memory.",
      "Commit small and often. Ten tiny commits ('Add DB schema', 'Hash passwords', 'Fix empty-username crash') beat one giant 'did stuff' — you can read, revert, and reason about them.",
      "Use your CS project as the training ground: from today, every Local-CyberComm milestone ends with a commit. By September your project history IS your proof of work.",
      "In interviews, 'do you know Git?' really asks: do you understand snapshots, branching, and pushing to a shared repo. After these six lessons — you do."
    ],
    commands: [
      { cmd: "git pull", what: "Start of session: sync down first." },
      { cmd: "git switch -c <task>", what: "One branch per task keeps work isolated." },
      { cmd: "git add -p", what: "Pro move: stage change-by-change, reviewing each hunk." },
      { cmd: "git stash / git stash pop", what: "Shelve half-done work, come back to it later." },
      { cmd: "publish.bat", what: "Your one-tap deploy for LockIn: add + commit + push, scripted." }
    ],
    practice: "Make your CS project a repo today: git init, write a .gitignore (start with __pycache__/), first commit 'Project start'. From now on, one commit per milestone — future-you will thank you in the GAMA interview.",
    quiz: [
      { q: "The healthiest commit habit is…", options: ["One huge commit per week", "Small, frequent commits with clear messages", "Only committing when everything is perfect", "Committing without messages to save time"], answer: 1, why: "Small commits are readable, revertible, and tell the story of the work." },
      { q: "First command when you sit down to work on a shared repo?", options: ["git push", "git pull", "git init", "git merge"], answer: 1, why: "Sync down before building on stale code." },
      { q: "git stash is for…", options: ["Deleting branches", "Shelving unfinished changes temporarily", "Compressing history", "Renaming files"], answer: 1, why: "It parks your working-directory changes so you can switch context cleanly." }
    ]
  }
];
