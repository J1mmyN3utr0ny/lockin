#!/usr/bin/env python3
"""
LockIn Lab — the desktop cyber Virtual Environment (PyCharm-style).

A real coding environment for the whole cyber curriculum: read a lesson, write code in the editor,
RUN it (Python always; C if gcc is installed), and for LeetCode/DSA press RUN TESTS to grade it
against real test cases. A Gemini 2.5 Flash tutor (free key in Settings) helps only when you ask and
never hands over solutions. It keeps records and serves them to the phone app over Wi-Fi so the
phone's Focus Lock unlocks once you've done your Lab work.

Pure Python standard library (tkinter + urllib). Run: python lockin_lab.py
"""
import datetime
import json
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, messagebox

import prompts
import content
import runner
from editor import CodeEditor
from sync import SyncServer
from leet import daily_problem
import expansions
import depth
try:
    from explain_questions import EXPLAIN_QUESTIONS
except Exception:
    EXPLAIN_QUESTIONS = {}

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(HERE, "lab_state.json")
# Current stable Flash line-up (verified against ai.google.dev, July 2026). The call
# walks the chain when a model isn't served for the key and remembers what worked.
MODELS = ["gemini-3.5-flash", "gemini-2.5-flash"]
_model_ix = [0]
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent?key=%s"

C = {
    "bg": "#0d1117", "panel": "#0f1522", "editor": "#0a1120", "card": "#151d2b", "card2": "#1b2536",
    "line": "#26324a", "fg": "#e8edf6", "mut": "#90a0bb", "dim": "#64748b", "acc": "#4f8cff",
    "acc2": "#22d3ee", "good": "#34d399", "warn": "#fbbf24", "bad": "#f87171", "gold": "#f5c451",
    "violet": "#a78bfa", "gutterbg": "#0a1120", "gutterfg": "#3b4a63", "caret": "#22d3ee", "sel": "#24406b",
    "kw": "#c792ea", "bi": "#82aaff", "str": "#c3e88d", "com": "#546e7a", "num": "#f78c6c", "fn": "#ffcb6b",
}
MONO = ("Cascadia Mono", 12) if os.name == "nt" else ("DejaVu Sans Mono", 12)
MONOS = ("Cascadia Mono", 10) if os.name == "nt" else ("DejaVu Sans Mono", 10)
UI = ("Segoe UI", 10) if os.name == "nt" else ("DejaVu Sans", 10)
UIB = ("Segoe UI", 10, "bold") if os.name == "nt" else ("DejaVu Sans", 10, "bold")
H1 = ("Segoe UI", 15, "bold") if os.name == "nt" else ("DejaVu Sans", 15, "bold")
DIFF_COL = {"Easy": C["good"], "Medium": C["warn"], "Hard": C["bad"]}


_key_ix = [0]  # rotates on 429 so later calls start from the key that still has quota


def gemini(api_key, system, user, temperature=0.6):
    """Call Gemini. `api_key` may be one key or a list — extra keys are BACKUPS that take
    over the moment the active one is rate-limited (429), same as the phone app's ai.js."""
    keys = [api_key] if isinstance(api_key, str) else list(api_key or [])
    keys = [k for k in keys if k and len(k.strip()) >= 20]
    if not keys:
        raise RuntimeError("No API key set — paste a free Gemini key in ⚙ Settings "
                           "(or in the phone app; it syncs over through the hub).")
    last_err = None
    for mi in range(_model_ix[0], len(MODELS)):
        model = MODELS[mi]
        gen = {"temperature": temperature, "maxOutputTokens": 4096}
        # Thinking control differs per generation: 2.5 takes thinkingBudget (0 = off);
        # 3.x takes thinkingLevel ("minimal" = lightest). Unmanaged, a 3.x model can
        # think its whole token budget away and return an EMPTY reply.
        if model.startswith("gemini-2.5"):
            gen["thinkingConfig"] = {"thinkingBudget": 0}
        elif model.startswith("gemini-3"):
            gen["thinkingConfig"] = {"thinkingLevel": "minimal"}
        body = {"system_instruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": gen}
        payload = json.dumps(body).encode("utf-8")
        next_model = False
        for ki in range(len(keys)):
            key = keys[(_key_ix[0] + ki) % len(keys)]
            req = urllib.request.Request(ENDPOINT % (model, urllib.parse.quote(key)),
                                        data=payload,
                                        headers={"Content-Type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    data = json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    # this key is out of quota — rotate to the backup and retry in place
                    last_err = ("All Gemini keys are rate-limited — wait a minute." if len(keys) > 1
                                else "Rate limit hit (free tier) — wait a minute, or add a backup key "
                                     "in the phone app's ⚙ Settings (it syncs over).")
                    continue
                if e.code in (400, 404):
                    # model-specific (not served / request shape) — walk the model chain
                    last_err = "Model %s unavailable (%s)." % (model, e.code)
                    next_model = True
                    break
                m = {403: "Access denied (403) — make a fresh free key at aistudio.google.com/apikey."
                     }.get(e.code, "Gemini error %s." % e.code)
                raise RuntimeError(m)
            except urllib.error.URLError:
                raise RuntimeError("Network error — are you online?")
            cands = data.get("candidates") or []
            text = "".join(p.get("text", "") for p in cands[0].get("content", {}).get("parts", [])).strip() if cands else ""
            if not text:
                # empty reply (thinking ate the budget, or a bare candidate) — walk the chain
                last_err = "%s returned an empty reply — trying the next model." % model
                next_model = True
                break
            _model_ix[0] = mi
            _key_ix[0] = (_key_ix[0] + ki) % len(keys)  # remember which key still has quota
            return text
        # all keys 429'd on this model (quotas are per-model — the next may have room),
        # or the model itself failed (next_model) — either way keep walking the chain.
    raise RuntimeError(last_err or "No Gemini model available for this key.")


def extract_json(text):
    """Strict-ish JSON from a model reply: strip fences/chatter, parse or raise."""
    t = str(text).strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[-1]
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    a, b = t.find("{"), t.find("[")
    start = min(x for x in (a, b) if x != -1) if (a != -1 or b != -1) else -1
    if start == -1:
        raise ValueError("no JSON in the reply")
    end = max(t.rfind("}"), t.rfind("]"))
    if end <= start:
        raise ValueError("unterminated JSON in the reply")
    return json.loads(t[start:end + 1])


# The Lab is now two apps sharing one engine, chosen by mode:
#   "code"   → LockIn Lab: tracks you WRITE + RUN code for, with the editor + runner.
#   "theory" → LockIn Study: the concept tracks (no code to run) with a Workbench —
#              an AI-graded answer console where you explain what you learned and get
#              scored feedback + XP. That graded loop is the theory app's "terminal".
CODE_TRACKS = ["python", "csharp", "c", "asm", "dsa"]
THEORY_TRACKS = ["cyber_high", "cyber_low", "linux", "cmd"]

# Background lesson builder: every hour the Lab quietly grows whichever track has the fewest
# lessons, so the thin corners of the curriculum fill themselves in while you work.
AUTOGEN_PERIOD_S = 3600          # one new lesson per hour, at most
AUTOGEN_FIRST_MS = 120 * 1000    # let the app settle before the first attempt
AUTOGEN_CHECK_MS = 10 * 60 * 1000  # re-check this often (survives the app being closed for a while)
APP_TITLE = {"code": "LockIn Lab", "theory": "LockIn Study"}


class Lab(tk.Tk):
    def __init__(self, mode="code"):
        super().__init__()
        self.mode = mode if mode in ("code", "theory") else "code"
        self.title(APP_TITLE[self.mode])
        self.configure(bg=C["bg"])
        self.geometry("1280x820")
        self.minsize(1040, 640)

        self.courses = content.build_courses()
        self.state = self._load_state()
        self._merge_generated()  # AI-built lessons become ordinary lessons of their track
        self.current = None
        self.language = "python"
        self._busy = False
        self._autogen_busy = False
        self._save_job = None

        self._style()
        self._build()
        self._populate_tree()

        # sync server for the phone
        self.sync = SyncServer(self.snapshot, port=self.state.get("syncPort", 8765))
        self.sync_url = self.sync.start() or "(sync off)"
        self._set_status()
        self._select_default()
        self.after(AUTOGEN_FIRST_MS, self._autogen_tick)  # start the hourly lesson builder

    # -------- state --------
    def _load_state(self):
        base = {"apiKey": "", "apiKey2": "", "syncPort": 8765, "progress": {}, "solved": {},
                "code": {}, "capstone": {}, "xp": 0, "history": [], "checks": {}, "activeDays": [],
                "genLessons": {},                        # trackId -> [AI-built lessons]
                "autoGen": {"last": 0, "byTrack": {}}}   # hourly builder bookkeeping
        if os.path.exists(STATE_PATH):
            try:
                base.update(json.load(open(STATE_PATH, encoding="utf-8")))
            except Exception:
                pass
        # one-time clean start (Jul 14): wipe pre-start Lab progress; keep the API key + code drafts.
        if base.get("_anchorReset") != "2026-07-14":
            base.update({"progress": {}, "solved": {}, "capstone": {}, "xp": 0,
                         "history": [], "checks": {}, "activeDays": [], "_anchorReset": "2026-07-14"})
        return base

    def _save_state(self):
        json.dump(self.state, open(STATE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        sync = getattr(self, "sync", None)
        if sync:
            sync.broadcast_status()  # push progress to connected phone/PC in real time

    def _today(self):
        return datetime.date.today().isoformat()

    def add_xp(self, n):
        self.state["xp"] = max(0, self.state.get("xp", 0) + n)

    def log_history(self, kind, cid, title):
        today = self._today()
        if not any(h["id"] == cid and h["date"] == today for h in self.state["history"]):
            self.state["history"].append({"date": today, "type": kind, "id": cid, "title": title})

    def _lesson_done(self, lid):
        return bool(self.state["progress"].get(lid))

    def _solved(self, sid):
        return sid in self.state["solved"]

    # -------- styling --------
    def _style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except Exception:
            pass
        s.configure("Treeview", background=C["panel"], fieldbackground=C["panel"], foreground=C["fg"],
                    rowheight=25, borderwidth=0, font=UI)
        s.map("Treeview", background=[("selected", C["acc"])], foreground=[("selected", "#fff")])
        s.configure("TNotebook", background=C["bg"], borderwidth=0)
        s.configure("TNotebook.Tab", background=C["card2"], foreground=C["mut"], padding=(14, 6), font=UIB)
        s.map("TNotebook.Tab", background=[("selected", C["editor"])], foreground=[("selected", C["acc2"])])
        s.configure("TPanedwindow", background=C["bg"])
        s.configure("Vertical.TScrollbar", background=C["card2"], troughcolor=C["bg"], borderwidth=0, arrowcolor=C["mut"])
        # readable dark combobox (clam defaults to a light field)
        s.configure("TCombobox", fieldbackground=C["card2"], background=C["card2"], foreground=C["fg"],
                    arrowcolor=C["mut"], bordercolor=C["line"], selectbackground=C["card2"], selectforeground=C["fg"])
        s.map("TCombobox", fieldbackground=[("readonly", C["card2"])], foreground=[("readonly", C["fg"])])
        self.option_add("*TCombobox*Listbox.background", C["card"])
        self.option_add("*TCombobox*Listbox.foreground", C["fg"])
        self.option_add("*TCombobox*Listbox.selectBackground", C["acc"])

    def _btn(self, parent, text, cmd, kind="normal"):
        col = {"normal": (C["card2"], C["fg"]), "primary": (C["acc"], "#fff"),
               "run": ("#1b4332", C["good"]), "test": (C["acc"], "#fff"), "warn": ("#3a2f10", C["warn"])}
        bg, fg = col.get(kind, (C["card2"], C["fg"]))
        b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, activebackground=C["line"],
                      activeforeground=C["fg"], font=UIB, relief="flat", bd=0, padx=12, pady=6, cursor="hand2")
        return b

    # -------- layout --------
    def _build(self):
        # toolbar
        tb = tk.Frame(self, bg=C["panel"], height=46)
        tb.pack(fill="x", side="top")
        title = "◆ LockIn Lab" if self.mode == "code" else "◆ LockIn Study"
        tk.Label(tb, text=title, bg=C["panel"], fg=C["acc"], font=H1).pack(side="left", padx=(14, 8))
        self.lang_var = tk.StringVar(value="python")
        if self.mode == "code":
            self.run_btn = self._btn(tb, "▶ Run", self.act_run, "run"); self.run_btn.pack(side="left", padx=4, pady=6)
            self.test_btn = self._btn(tb, "✓ Run Tests", self.act_test, "test"); self.test_btn.pack(side="left", padx=4)
            self.reset_btn = self._btn(tb, "⟲ Reset", self.act_reset); self.reset_btn.pack(side="left", padx=4)
            tk.Label(tb, text="lang", bg=C["panel"], fg=C["dim"], font=UI).pack(side="left", padx=(12, 4))
            self.lang_menu = ttk.Combobox(tb, textvariable=self.lang_var, values=["python", "c", "csharp", "asm"], width=9, state="readonly")
            self.lang_menu.pack(side="left")
            self.lang_menu.bind("<<ComboboxSelected>>", self._lang_changed)
        else:
            # theory app: the Workbench is graded by AI, not run — so no Run/Tests/lang.
            self.grade_btn = self._btn(tb, "📝 Grade my answer", self.act_grade, "test"); self.grade_btn.pack(side="left", padx=4, pady=6)
            self.reset_btn = self._btn(tb, "⟲ Clear", self.act_reset); self.reset_btn.pack(side="left", padx=4)
            self.run_btn = None; self.test_btn = None

        self._btn(tb, "⚙", self.open_settings).pack(side="right", padx=(4, 12), pady=6)
        self.ai_dot = tk.Label(tb, text="", bg=C["panel"], font=UI); self.ai_dot.pack(side="right", padx=6)
        self.panel_btn = self._btn(tb, "▣ Lesson", self.toggle_panel); self.panel_btn.pack(side="right", padx=4)

        # main paned: sidebar | center | right
        self.pw = ttk.Panedwindow(self, orient="horizontal")
        self.pw.pack(fill="both", expand=True)

        side = tk.Frame(self.pw, bg=C["panel"])
        self.tree = ttk.Treeview(side, show="tree", selectmode="browse")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.pw.add(side, weight=0)

        center = tk.Frame(self.pw, bg=C["bg"])
        self.pw.add(center, weight=4)
        cpw = ttk.Panedwindow(center, orient="vertical")
        cpw.pack(fill="both", expand=True)
        edwrap = tk.Frame(cpw, bg=C["editor"])
        if self.mode == "theory":
            # the Workbench: where he writes his explanations/answers for AI grading.
            tk.Label(edwrap, text="  📝 Workbench — write your answer here, then “Grade my answer”",
                     bg=C["editor"], fg=C["dim"], font=UI, anchor="w").pack(fill="x", pady=(4, 0))
        self.editor = CodeEditor(edwrap, C, MONO, on_cursor=self._cursor)
        self.editor.pack(fill="both", expand=True)
        cpw.add(edwrap, weight=4)

        console = tk.Frame(cpw, bg=C["bg"])
        self.console = ttk.Notebook(console)
        self.console.pack(fill="both", expand=True)
        self.out_txt = self._console_text()
        self.test_txt = self._console_text()
        if self.mode == "code":
            self.console.add(self.out_txt.master, text="  Output  ")
            self.console.add(self.test_txt.master, text="  Tests  ")
        else:
            self.console.add(self.out_txt.master, text="  Feedback  ")
        cpw.add(console, weight=2)

        # right: lesson + tutor
        self.right = tk.Frame(self.pw, bg=C["bg"])
        self.pw.add(self.right, weight=2)
        self.lesson_txt = tk.Text(self.right, bg=C["card"], fg=C["fg"], relief="flat", font=UI, wrap="word",
                                 padx=14, pady=12, borderwidth=0, height=20)
        self.lesson_txt.pack(fill="both", expand=True)
        self._tags(self.lesson_txt)
        self.lesson_txt.configure(state="disabled")

        aibar = tk.Frame(self.right, bg=C["bg"])
        aibar.pack(fill="x")
        self._btn(aibar, "💡 Hint", self.act_hint).pack(side="left", padx=4, pady=6)
        self._btn(aibar, "❔ Ask", self.act_ask).pack(side="left", padx=4)
        self._btn(aibar, "📖 Explain", self.act_explain).pack(side="left", padx=4)
        if self.mode == "code":
            self._btn(aibar, "🏗 Guide me", self.act_guide).pack(side="left", padx=4)
        self._btn(aibar, "➕ AI practice", self.act_practice).pack(side="left", padx=4)
        self.done_btn = self._btn(aibar, "Mark done", self.act_done, "primary"); self.done_btn.pack(side="right", padx=8)

        self.tutor_txt = tk.Text(self.right, bg=C["panel"], fg=C["fg"], relief="flat", font=UI, wrap="word",
                                padx=12, pady=10, borderwidth=0, height=9)
        self.tutor_txt.pack(fill="x")
        self._tags(self.tutor_txt)
        self.tutor_txt.configure(state="disabled")

        # status bar
        self.status = tk.Label(self, text="", bg=C["panel"], fg=C["mut"], font=MONOS, anchor="w", padx=12)
        self.status.pack(fill="x", side="bottom")

    def _console_text(self):
        f = tk.Frame(self.console, bg=C["editor"])
        t = tk.Text(f, bg=C["editor"], fg=C["fg"], relief="flat", font=MONOS, wrap="word",
                    padx=12, pady=10, borderwidth=0)
        t.pack(fill="both", expand=True)
        t.tag_configure("ok", foreground=C["good"]); t.tag_configure("err", foreground=C["bad"])
        t.tag_configure("dim", foreground=C["dim"]); t.tag_configure("acc", foreground=C["acc2"])
        t.tag_configure("warn", foreground=C["warn"])
        t.configure(state="disabled")
        return t

    def _tags(self, w):
        w.tag_configure("h", foreground=C["acc2"], font=UIB, spacing1=10, spacing3=4)
        w.tag_configure("b", foreground=C["fg"], spacing3=5)
        w.tag_configure("task", foreground=C["gold"], spacing1=6, spacing3=6, lmargin1=6, lmargin2=6)
        w.tag_configure("code", foreground="#a7f3d0", font=MONOS, background=C["editor"], lmargin1=12, lmargin2=12, spacing1=3, spacing3=5)
        w.tag_configure("dim", foreground=C["dim"])
        w.tag_configure("good", foreground=C["good"])
        w.tag_configure("user", foreground=C["acc"], font=UIB)
        w.tag_configure("recall", foreground=C["violet"], font=UIB, spacing1=6, spacing3=6, lmargin1=6, lmargin2=6)
        w.tag_configure("reveal", foreground=C["acc"], underline=True)
        w.tag_configure("hooklbl", foreground=C["dim"], font=UIB, spacing1=6)
        w.tag_configure("hook", foreground=C["mut"], spacing1=6, spacing3=8, lmargin2=6)
        w.tag_configure("tell", foreground=C["acc2"], font=UIB, spacing1=4, spacing3=6, lmargin1=6, lmargin2=6)
        w.tag_configure("opt", foreground=C["fg"], lmargin1=6, lmargin2=18)
        w.tag_configure("optgood", foreground=C["good"], font=UIB, lmargin1=6, lmargin2=18)
        for d, col in DIFF_COL.items():
            w.tag_configure("diff_" + d, foreground=col, font=UIB)

    # -------- tree --------
    def _populate_tree(self):
        self.tree.insert("", "end", iid="dailyai", text="  ✨  Today's AI lesson — %s" % self._todays_track()[1])

        if self.mode == "code":
            # DSA gets its own top-level group; then the compiled-language tracks.
            dnode = self.tree.insert("", "end", iid="track:dsa", text="  🧠  Data Structures & Algorithms", open=True)
            self._track_children(dnode, "dsa", self.courses["dsa"])
            cnode = self.tree.insert("", "end", iid="courses", text="  💻  Code tracks", open=True)
            for tid in ["python", "csharp", "c", "asm"]:
                c = self.courses[tid]
                tnode = self.tree.insert(cnode, "end", iid="track:" + tid, text="   " + c["title"].split("—")[0].strip())
                self._track_children(tnode, tid, c)
            bnode = self.tree.insert("", "end", iid="leetbrowse", text="  🧩  LeetCode — Browse")
            self.tree.insert("", "end", iid="daily", text="  ⭐  LeetCode — Daily")
            self.tree.move("daily", "", 1)  # keep Daily near the top
            for p in content.PROBLEMS:
                mark = "✓ " if self._solved(p["id"]) else "•  "
                self.tree.insert(bnode, "end", iid="leet:" + p["id"], text="   %s%s" % (mark, p["title"]))
        else:
            cnode = self.tree.insert("", "end", iid="courses", text="  🧠  Theory tracks", open=True)
            for tid in THEORY_TRACKS:
                c = self.courses[tid]
                tnode = self.tree.insert(cnode, "end", iid="track:" + tid, text="   " + c["title"].split("—")[0].strip())
                self._track_children(tnode, tid, c)

    def _lesson_label(self, L):
        """Tree label: ✓ when finished, ✨ for an AI-built lesson, • otherwise."""
        if self._lesson_done(L["id"]) or self._solved(L["id"]):
            return "    ✓ %s" % L["title"]
        return "    %s%s" % ("✨ " if L.get("generated") else "•  ", L["title"])

    def _track_children(self, node, tid, course):
        for i, L in enumerate(course["lessons"]):
            self.tree.insert(node, "end", iid="lesson:%s#%d" % (tid, i), text=self._lesson_label(L))
        self.tree.insert(node, "end", iid="cap:" + tid, text="    🏁 " + course["capstone"]["name"])

    def _refresh_marks(self):
        for iid in (self.tree.get_children("leetbrowse") if self.tree.exists("leetbrowse") else ()):
            pid = iid.split(":", 1)[1]
            p = content.BY_ID[pid]
            self.tree.item(iid, text="   %s%s" % ("✓ " if self._solved(pid) else "•  ", p["title"]))
        for tid, course in self.courses.items():
            for i, L in enumerate(course["lessons"]):
                iid = "lesson:%s#%d" % (tid, i)
                if self.tree.exists(iid):
                    self.tree.item(iid, text=self._lesson_label(L))

    def _select_default(self):
        first = "daily" if self.tree.exists("daily") else "dailyai"
        self.tree.selection_set(first)
        self.tree.focus(first)
        self.on_select()

    # -------- selection & rendering --------
    def on_select(self, _e=None):
        sel = self.tree.focus()
        if sel == "daily":
            p = daily_problem(datetime.date.today().toordinal())
            self.current = {"kind": "leet", "problem": p, "daily": True}
            self._render_leet(p, daily=True)
        elif sel == "dailyai":
            self.current = {"kind": "dailyai"}
            self._render_dailyai()
        elif sel.startswith("leet:"):
            p = content.BY_ID[sel.split(":", 1)[1]]
            self.current = {"kind": "leet", "problem": p}
            self._render_leet(p)
        elif sel.startswith("lesson:"):
            tid, idx = sel.split(":", 1)[1].split("#")
            self.current = {"kind": "lesson", "tid": tid, "idx": int(idx)}
            self._render_lesson(tid, int(idx))
        elif sel.startswith("cap:"):
            tid = sel.split(":", 1)[1]
            self.current = {"kind": "cap", "tid": tid}
            self._render_capstone(tid)

    def _editor_id(self):
        c = self.current
        if c["kind"] == "leet":
            return "leet:" + c["problem"]["id"]
        if c["kind"] == "lesson":
            return self.courses[c["tid"]]["lessons"][c["idx"]]["id"]
        return None

    def _load_editor(self, starter, lang):
        eid = self._editor_id()
        saved = self.state["code"].get(eid) if eid else None
        self.language = lang
        self.lang_var.set(lang)
        self.editor.set_code(saved if saved is not None else starter, lang)

    def _set_lesson(self, render):
        self.lesson_txt.configure(state="normal")
        self.lesson_txt.delete("1.0", "end")
        render(self.lesson_txt)
        self.lesson_txt.configure(state="disabled")

    def _set_test_btn(self, **kw):
        # theory app has no Run Tests button — quietly ignore the code-mode calls.
        if self.test_btn is not None:
            self.test_btn.configure(**kw)

    def _render_leet(self, p, daily=False):
        self.test_btn.configure(text="✓ Run Tests", state="normal")
        self.done_btn.configure(text="✓ Solved" if self._solved(p["id"]) else "Solved?", state="disabled")

        def draw(w):
            if daily:
                w.insert("end", "⭐ TODAY'S DAILY\n", "user")
            w.insert("end", p["title"] + "  ", "h")
            w.insert("end", "[%s]\n\n" % p["difficulty"], "diff_" + p["difficulty"])
            w.insert("end", p["statement"] + "\n\n", "b")
            w.insert("end", "Examples\n", "h")
            for ex in p["examples"]:
                w.insert("end", "  " + ex + "\n", "code")
            # Terse statement? One click gets a full clarification — never a solving hint.
            w.insert("end", "\n🤖 Explain this problem fully (what's asked — never how to solve it) →\n", ("opt", "explainprob"))
            w.tag_bind("explainprob", "<Button-1>", lambda _e: self.act_explain_problem())
            w.tag_bind("explainprob", "<Enter>", lambda _e: w.configure(cursor="hand2"))
            w.tag_bind("explainprob", "<Leave>", lambda _e: w.configure(cursor=""))
            w.insert("end", "\nWrite %s(...) in the editor, then press ✓ Run Tests.\n" % p["func"], "dim")
        self._set_lesson(draw)
        self._load_editor(p["starter"], "python")
        self._to_tab(1)

    def _render_lesson(self, tid, idx):
        course = self.courses[tid]
        L = course["lessons"][idx]
        ex = L.get("exercise")
        self._set_test_btn(text="✓ Run Tests" if ex else "✓ AI Check", state="normal")
        self.done_btn.configure(text="✓ Done" if self._lesson_done(L["id"]) else "Mark done", state="normal")

        def draw(w):
            w.insert("end", L["title"] + "\n", "h")
            w.insert("end", "⏱ %s min · %s\n" % (L.get("minutes", "—"), course["title"].split("—")[0].strip()), "dim")
            if L.get("hook"):
                w.insert("end", "Why it matters  ", "hooklbl")
                w.insert("end", L["hook"] + "\n", "hook")
            w.insert("end", "\n", "dim")
            for sec in L.get("read", []):
                w.insert("end", sec.get("h", "") + "\n", "h")
                if sec.get("p"):
                    w.insert("end", sec["p"] + "\n", "b")
                if sec.get("code"):
                    w.insert("end", sec["code"] + "\n", "code")
            # The real lesson: several thousand words per topic (depth_<track>.py). The original
            # `read` sections above are the summary; this is the part you actually study from.
            dp = depth.for_lesson(L["id"], L["title"])
            if dp:
                w.insert("end", "\n📖  THE FULL LESSON\n", "h")
                for sec in dp.get("sections", []):
                    if sec.get("h"):
                        w.insert("end", "\n" + sec["h"] + "\n", "hooklbl")
                    if sec.get("body"):
                        w.insert("end", sec["body"] + "\n", "b")
            exp = expansions.for_lesson(tid, idx, L["title"])
            if exp:
                w.insert("end", "\n🔎  DEEP DIVE — beyond the lesson\n", "h")
                for sec in exp.get("sections", []):
                    if sec.get("h"):
                        w.insert("end", sec["h"] + "\n", "hooklbl")
                    if sec.get("body"):
                        w.insert("end", sec["body"] + "\n", "b")
                links = exp.get("links") or []
                if links:
                    w.insert("end", "Further reading: ", "dim")
                    w.insert("end", " · ".join("%s (%s)" % (l.get("label", "link"), l.get("url", "")) for l in links) + "\n", "dim")
            if L.get("tell"):
                w.insert("end", "\n🎯  THE LEETCODE TELL — how to spot it\n", "h")
                w.insert("end", L["tell"] + "\n", "tell")
            # Retrieval practice: force a free-recall / teach-back BEFORE the exercise. Struggling
            # to recall is what builds durable memory — far more than re-reading ever does.
            recall = L.get("recall")
            w.insert("end", "\n✍  RECALL FIRST — look away from the screen\n", "h")
            if recall:
                w.insert("end", recall + "\n", "recall")
            else:
                w.insert("end", "From memory, explain “%s” in a sentence or two as if teaching a friend, "
                                "and write the single most important line of code/command from it. "
                                "Do this before the exercise — the effort of retrieving is the learning.\n"
                         % L["title"], "recall")
            if ex:
                w.insert("end", "\n🛠  EXERCISE (auto-graded)\n", "h")
                w.insert("end", ex["prompt"] + "\n", "task")
                w.insert("end", "Define %s(...) then press ✓ Run Tests.\n" % ex["func"], "dim")
            else:
                do = L.get("doThis") or {}
                if do.get("task"):
                    w.insert("end", "\n🛠  DO THIS (hands-on)\n", "h")
                    w.insert("end", do["task"] + "\n", "task")
                    if self.mode == "code":
                        w.insert("end", "Do it in your terminal; use the editor to experiment (▶ Run), then ✓ AI Check.\n", "dim")
                    else:
                        w.insert("end", "Do it for real, then write what you did / what you found in the Workbench and press ✓ AI Check.\n", "dim")
            if L.get("quiz"):
                lid = L["id"]
                base = lid.replace("-", "_")
                checks = self.state.setdefault("checks", {}).setdefault(lid, {})
                n = len(L["quiz"])
                w.insert("end", "\n✅  CHECKS — pass all %d to prove you learned it\n" % n, "h")
                w.insert("end", "Pick the answer. Right = green + XP; wrong just turns red — try again.\n", "dim")
                for qi, q in enumerate(L["quiz"]):
                    solved_q = bool(checks.get(str(qi)))
                    w.insert("end", "\n%d. %s\n" % (qi + 1, q["q"]), "b")
                    if q.get("code"):  # a "what does this do?" snippet to read before choosing
                        w.insert("end", q["code"] + "\n", "code")
                    for oi, opt in enumerate(q["options"]):
                        correct = (oi == q["answer"])
                        if solved_q and correct:
                            w.insert("end", "   ✓ %s) %s\n" % ("abcd"[oi], opt), "optgood")
                        elif solved_q:
                            w.insert("end", "   %s) %s\n" % ("abcd"[oi], opt), "opt")
                        else:
                            otag = "opt_%s_%d_%d" % (base, qi, oi)
                            w.insert("end", "   %s) %s\n" % ("abcd"[oi], opt), ("opt", otag))
                            w.tag_bind(otag, "<Button-1>",
                                       lambda _e, a=qi, cor=correct, t=otag: self._answer_check(lid, a, cor, t))
                            w.tag_bind(otag, "<Enter>", lambda _e: w.configure(cursor="hand2"))
                            w.tag_bind(otag, "<Leave>", lambda _e: w.configure(cursor=""))
                    extag = "exp_%s_%d" % (base, qi)
                    w.insert("end", "     → %s\n" % q["why"], (extag,))
                    if q.get("detail"):  # the deep bank explains WHY the tempting wrong picks fail
                        w.insert("end", "       %s\n" % q["detail"], (extag,))
                    w.tag_configure(extag, foreground=C["good"], elide=not solved_q)
                allpassed = all(checks.get(str(i)) for i in range(n))
                celtag = "cel_%s" % base
                w.insert("end", "\n🎉  All checks passed — you've PROVEN this one. Hit “Finish lesson”. \n", (celtag,))
                w.tag_configure(celtag, foreground=C["gold"], font=UIB, elide=not allpassed)
            # Explain-back: an open question the AI grades. Deeper than a multiple choice —
            # you must produce the reasoning, not recognize it. Answer in the Workbench/editor.
            eq = EXPLAIN_QUESTIONS.get("%s:%d" % (tid, idx))
            if eq and (not eq.get("title_check") or eq["title_check"] == L["title"]):
                self._explain_q = eq  # act_grade reads this
                prevg = (self.state.get("explainScores") or {}).get(L["id"])
                w.insert("end", "\n🧠  EXPLAIN IT — graded by AI\n", "h")
                w.insert("end", eq["q"] + "\n", "task")
                where = "the editor" if self.mode == "code" else "the Workbench (left)"
                w.insert("end", "Write your answer in %s, then press %s.%s\n" % (
                    where,
                    "“📝 Grade my answer”" if self.mode == "theory" else "the ✓ AI Check button",
                    (" Best so far: %d/100." % prevg["score"]) if prevg else ""), "dim")
            else:
                self._explain_q = None
        self._set_lesson(draw)
        if L.get("quiz"):
            self._update_check_status()
        starters = {
            "c": ("c", "#include <stdio.h>\n\nint main(void) {\n    // Experiment here — press ▶ Run.\n    return 0;\n}\n"),
            "csharp": ("csharp", "using System;\n\nclass Program {\n    static void Main() {\n        // Experiment here — press ▶ Run.\n    }\n}\n"),
            "asm": ("asm", "; Intel syntax (nasm), assembled -f win64 and linked with gcc — printf works.\n"
                           "; win64 rules this starter already follows: `default rel` for data addressing,\n"
                           "; 1st arg in rcx, and 32 bytes of shadow space (+8 to align) before any call.\n"
                           "default rel\nglobal main\nextern printf\n\nsection .data\n"
                           "    msg db \"hello from asm!\", 10, 0\n\nsection .text\nmain:\n"
                           "    sub rsp, 40          ; shadow space + stack alignment\n"
                           "    lea rcx, [msg]       ; 1st argument (win64: rcx, rdx, r8, r9)\n"
                           "    call printf\n"
                           "    xor eax, eax         ; return 0\n"
                           "    add rsp, 40\n    ret\n"),
        }
        if self.mode == "theory":
            # the Workbench is a plain writing pad — seed it with the answer scaffold.
            self._load_editor("# Write your answer / notes here, then Grade my answer.\n\n", "text")
        elif ex:
            self._load_editor(ex["starter"], "python")
        elif tid in starters:
            lang, starter = starters[tid]
            self._load_editor(starter, lang)
        else:
            self._load_editor("# Experiment here — press ▶ Run.\n", "python")

    # -------- interactive graded checks (learning verification) --------
    def _answer_check(self, lid, qi, correct, otag):
        """Handle a click on a check option: grade it, give instant feedback and XP."""
        checks = self.state.setdefault("checks", {}).setdefault(lid, {})
        if checks.get(str(qi)):
            return  # this question is already passed — ignore further clicks
        w = self.lesson_txt
        w.configure(state="normal")
        if correct:
            checks[str(qi)] = True
            base = lid.replace("-", "_")
            w.tag_configure(otag, foreground=C["good"], font=UIB)     # the chosen option turns green
            w.tag_configure("exp_%s_%d" % (base, qi), elide=False)     # reveal the explanation
            self.add_xp(3)          # small, satisfying reward per correct check
            self._mark_active()
            self._save_state()
        else:
            w.tag_configure(otag, foreground=C["bad"], overstrike=True)  # wrong → red strike, try again
        w.configure(state="disabled")
        self._update_check_status()

    def _update_check_status(self):
        """Reflect check progress on the Finish button + status bar; celebrate a full pass once."""
        c = self.current
        if not c or c.get("kind") != "lesson":
            return
        L = self.courses[c["tid"]]["lessons"][c["idx"]]
        lid = L["id"]
        quiz = L.get("quiz") or []
        total = len(quiz)
        checks = self.state.get("checks", {}).get(lid, {})
        passed = sum(1 for i in range(total) if checks.get(str(i)))
        if self._lesson_done(lid):
            self.done_btn.configure(text="✓ Done", bg=C["acc"], fg="#fff")
        elif total and passed == total:
            self.done_btn.configure(text="✓ Finish lesson (+15)", bg=C["acc"], fg="#fff")
            base = lid.replace("-", "_")
            self.lesson_txt.configure(state="normal")
            self.lesson_txt.tag_configure("cel_%s" % base, elide=False)  # reveal the celebration line
            self.lesson_txt.configure(state="disabled")
            rec = self.state.setdefault("checks", {}).setdefault(lid, {})
            if not rec.get("_bonus"):        # one-time bonus for passing every check
                rec["_bonus"] = True
                self.add_xp(10)
                self._save_state()
        elif total:
            self.done_btn.configure(text="Checks %d/%d" % (passed, total), bg=C["card2"], fg=C["fg"])
        else:
            self.done_btn.configure(text="✓ Done" if self._lesson_done(lid) else "Mark done", bg=C["acc"], fg="#fff")
        self._set_status()

    def _mark_active(self):
        """Record that the user did real work today (drives the streak)."""
        today = self._today()
        days = self.state.setdefault("activeDays", [])
        if today not in days:
            days.append(today)

    def _streak(self):
        """Consecutive days (ending today, or yesterday if nothing yet today) with real activity."""
        days = set(self.state.get("activeDays", []))
        for h in self.state.get("history", []):
            days.add(h["date"])
        if not days:
            return 0
        d = datetime.date.today()
        if d.isoformat() not in days:
            d = d - datetime.timedelta(days=1)
        n = 0
        while d.isoformat() in days:
            n += 1
            d = d - datetime.timedelta(days=1)
        return n

    def _render_capstone(self, tid):
        course = self.courses[tid]
        cap = course["capstone"]
        self._set_test_btn(state="disabled")
        self.done_btn.configure(text="Mark done", state="disabled")

        def draw(w):
            w.insert("end", "🏁 " + cap["name"] + "\n\n", "h")
            w.insert("end", cap["goal"] + "\n\n", "b")
            w.insert("end", "Milestones\n", "h")
            for m in cap["milestones"]:
                d = self.state["capstone"].get(m["id"])
                w.insert("end", "  %s %s\n" % ("✓" if d else "☐", m["text"]), "good" if d else "b")
                w.insert("end", "       hint: %s\n" % m["hint"], "dim")
            w.insert("end", "\nType a milestone number (1..%d) in the editor and press ▶ Run to toggle it.\n" % len(cap["milestones"]), "dim")
        self._set_lesson(draw)
        self._load_editor("", "python")
        self.editor.language = "python"

    # -------- run / test --------
    def _to_tab(self, i):
        try:
            self.console.select(i)
        except Exception:
            pass

    def _print(self, widget, text, tag=None, clear=False):
        widget.configure(state="normal")
        if clear:
            widget.delete("1.0", "end")
        widget.insert("end", text, tag or ())
        widget.see("end")
        widget.configure(state="disabled")

    def _set_busy(self, on):
        self._busy = on
        for b in (self.run_btn, self.test_btn, getattr(self, "grade_btn", None)):
            if b is not None:
                b.configure(state="disabled" if on else "normal")

    def act_run(self):
        if self._busy:
            return
        if self.current and self.current["kind"] == "cap":
            self._toggle_capstone()
            return
        code = self.editor.get_code()
        self._save_code()
        self._to_tab(0)
        self._print(self.out_txt, "running…\n", "dim", clear=True)
        self._set_busy(True)
        lang = self.lang_var.get()

        run_fn = {"c": runner.run_c, "csharp": runner.run_csharp, "asm": runner.run_asm}.get(lang, runner.run_python)

        def work():
            res = run_fn(code)
            self.after(0, lambda: self._show_run(res))
        threading.Thread(target=work, daemon=True).start()

    def _show_run(self, res):
        self._set_busy(False)
        self._print(self.out_txt, "", clear=True)
        if res["stdout"]:
            self._print(self.out_txt, res["stdout"])
        if res["stderr"]:
            self._print(self.out_txt, ("\n" if res["stdout"] else "") + res["stderr"], "err")
        self._print(self.out_txt, "\n\n[exit %s]\n" % res["exit"], "dim" if res["exit"] == 0 else "err")

    def act_test(self):
        if self._busy or not self.current:
            return
        ex = self._current_exercise()
        if ex is None:
            # prose lesson → grade the explain-back if it has one, else the doThis review.
            if getattr(self, "_explain_q", None):
                self.act_grade()
            else:
                self.act_review()
            return
        code = self.editor.get_code()
        self._save_code()
        self._to_tab(1)
        self._print(self.test_txt, "running tests…\n", "dim", clear=True)
        self._set_busy(True)

        def work():
            r = runner.run_tests(code, ex)
            self.after(0, lambda: self._show_tests(r, ex))
        threading.Thread(target=work, daemon=True).start()

    def _current_exercise(self):
        c = self.current
        if c["kind"] == "leet":
            return c["problem"]
        if c["kind"] == "lesson":
            return self.courses[c["tid"]]["lessons"][c["idx"]].get("exercise")
        return None

    # -------- AI-graded explain-back --------
    def act_grade(self):
        """Grade the Workbench/editor answer to the current lesson's explain question."""
        c = self.current
        eq = getattr(self, "_explain_q", None)
        if self._busy or not c or c.get("kind") != "lesson" or not eq:
            return
        key = self._api_keys()
        answer = self.editor.get_code().strip()
        # ignore the seed scaffold / trivially short answers
        clean = "\n".join(l for l in answer.splitlines() if not l.strip().startswith("#")).strip()
        out = self.out_txt
        self._to_tab(0)
        if not key:
            self._print(out, "Add a free Gemini key in ⚙ Settings to get graded.\n", "err", clear=True)
            return
        if len(clean) < 25:
            self._print(out, "Write a real answer first (a few sentences), then grade it.\n", "warn", clear=True)
            return
        lid = self.courses[c["tid"]]["lessons"][c["idx"]]["id"]
        self._print(out, "Grading your explanation…\n", "dim", clear=True)
        self._set_busy(True)
        user = ("QUESTION: %s\n\nRUBRIC (what a full answer must contain): %s\n\n"
                "STUDENT'S ANSWER:\n%s\n\nGrade it per the schema.") % (eq["q"], eq["rubric"], clean)

        def work():
            try:
                data = self._json_call(key, prompts.EXPLAIN_GRADER_SYS, user, self._valid_grade)
                self.after(0, lambda: self._grade_done(lid, data))
            except Exception as e:
                self.after(0, lambda e=e: (self._set_busy(False), self._print(out, "⚠ " + str(e) + "\n", "err", clear=True)))
        threading.Thread(target=work, daemon=True).start()

    @staticmethod
    def _valid_grade(o):
        if not isinstance(o, dict):
            return "reply is not an object"
        if not isinstance(o.get("score"), int) or not 0 <= o["score"] <= 100:
            return "score must be an integer 0-100"
        if o.get("verdict") not in ("pass", "revise"):
            return "verdict must be pass or revise"
        for k in ("strengths", "gaps", "model"):
            if not isinstance(o.get(k), str) or len(o[k]) < 3:
                return "%s must be a non-empty string" % k
        return None

    def _grade_done(self, lid, g):
        self._set_busy(False)
        out = self.out_txt
        self._print(out, "", clear=True)
        passed = g["verdict"] == "pass"
        self._print(out, "Score: %d/100 — %s\n\n" % (g["score"], "PASS ✓" if passed else "revise"),
                    "ok" if passed else "warn")
        self._print(out, "What you got right\n", "acc")
        self._print(out, g["strengths"] + "\n\n")
        self._print(out, "Gaps to close\n", "acc")
        self._print(out, g["gaps"] + "\n\n")
        self._print(out, "Model answer\n", "acc")
        self._print(out, g["model"] + "\n", "dim")
        # record best score; award XP the first time a lesson is passed (experience gained)
        scores = self.state.setdefault("explainScores", {})
        prev = scores.get(lid, {}).get("score", -1)
        first_pass = passed and not scores.get(lid, {}).get("passed")
        if g["score"] > prev or passed:
            scores[lid] = {"score": max(prev, g["score"]), "passed": passed or scores.get(lid, {}).get("passed", False)}
        if first_pass:
            self.add_xp(15)
            self._mark_active()
            self._print(out, "\n+15 XP — explanation accepted.\n", "ok")
        self._save_state()
        self._refresh_marks()

    def _show_tests(self, r, ex):
        self._set_busy(False)
        self._print(self.test_txt, "", clear=True)
        if r["user_output"]:
            self._print(self.test_txt, "your output:\n" + r["user_output"] + "\n\n", "dim")
        if r["error"]:
            self._print(self.test_txt, "✗ " + r["error"] + "\n", "err")
            return
        for i, c in enumerate(r["cases"], 1):
            head = "✓" if c["ok"] else "✗"
            tag = "ok" if c["ok"] else "err"
            self._print(self.test_txt, "%s case %d  " % (head, i), tag)
            self._print(self.test_txt, "args=%s\n" % json.dumps(c["args"]), "dim")
            if not c["ok"]:
                self._print(self.test_txt, "     expected %s, got %s\n" % (json.dumps(c["expect"]), c["got"]), "warn")
        allpass = r["passed"] == r["total"]
        self._print(self.test_txt, "\n%d / %d passed\n" % (r["passed"], r["total"]), "ok" if allpass else "err")
        if allpass:
            self._on_solved(ex)

    def _on_solved(self, ex):
        c = self.current
        sid = c["problem"]["id"] if c["kind"] == "leet" else self.courses[c["tid"]]["lessons"][c["idx"]]["id"]
        title = c["problem"]["title"] if c["kind"] == "leet" else self.courses[c["tid"]]["lessons"][c["idx"]]["title"]
        if not self._solved(sid):
            hard = c["kind"] == "leet" and c["problem"]["difficulty"] == "Hard"
            self.add_xp(40 if hard else 20)
            self.state["solved"][sid] = {"date": self._today()}
            self._mark_active()
            self.log_history("solve", sid, title)
            self._save_state()
            self._refresh_marks()
            self._print(self.test_txt, "\n🎉 Solved! +%d XP — synced to your phone.\n" % (40 if hard else 20), "ok")

    def act_reset(self):
        c = self.current
        if not c:
            return
        if c["kind"] == "leet":
            starter = c["problem"]["starter"]
        elif c["kind"] == "lesson":
            L = self.courses[c["tid"]]["lessons"][c["idx"]]
            starter = (L.get("exercise") or {}).get("starter", "# Experiment here.\n")
        else:
            return
        self.editor.set_code(starter, self.lang_var.get())
        self._save_code()

    def _toggle_capstone(self):
        raw = self.editor.get_code().strip()
        if not raw.isdigit():
            return
        cap = self.courses[self.current["tid"]]["capstone"]
        n = int(raw)
        if 1 <= n <= len(cap["milestones"]):
            mid = cap["milestones"][n - 1]["id"]
            self.state["capstone"][mid] = not self.state["capstone"].get(mid)
            if self.state["capstone"][mid]:
                self.add_xp(10)
            self._save_state()
            self.editor.set_code("", "python")
            self._render_capstone(self.current["tid"])

    # -------- AI --------
    def _context(self):
        c = self.current
        if c["kind"] == "leet":
            p = c["problem"]
            return "LeetCode problem: %s (%s)\n%s\nThey must define %s(...)." % (p["title"], p["difficulty"], p["statement"], p["func"])
        if c["kind"] == "lesson":
            return prompts.context_from_lesson(self.courses[c["tid"]]["title"], self.courses[c["tid"]]["lessons"][c["idx"]])
        return "Capstone project for track " + c["tid"]

    def _ai(self, mode, user, echo=None):
        if self._busy:
            return
        key = self._api_keys()
        if not key:
            self._tutor("Tutor", "Add a free Gemini key in ⚙ Settings to use the tutor.", "err")
            return
        if echo:
            self._tutor("You", echo, "user")
        self._tutor("Tutor", "thinking…", "dim")
        self._set_busy(True)
        sysp = prompts.system_for(mode, self._context())

        def work():
            try:
                out = gemini(key, sysp, user)
            except Exception as e:
                out = "⚠ " + str(e)
            self.after(0, lambda: self._ai_done(out))
        threading.Thread(target=work, daemon=True).start()

    def _ai_done(self, out):
        self._set_busy(False)
        self.tutor_txt.configure(state="normal")
        # remove trailing "thinking…"
        idx = self.tutor_txt.search("thinking…", "end-2l", backwards=True)
        if idx:
            self.tutor_txt.delete(idx + " linestart", "end")
        self.tutor_txt.insert("end", out + "\n")
        self.tutor_txt.see("end")
        self.tutor_txt.configure(state="disabled")

    def _tutor(self, who, text, tag="b"):
        self.tutor_txt.configure(state="normal")
        self.tutor_txt.insert("end", "\n%s\n" % who, "user" if who == "You" else "h")
        self.tutor_txt.insert("end", text + "\n", tag)
        self.tutor_txt.see("end")
        self.tutor_txt.configure(state="disabled")

    def act_hint(self):
        # show the built-in static hint instantly, then offer AI
        ex = self._current_exercise()
        hint = ex.get("hint") if ex else None
        if hint:
            self._tutor("Hint", hint, "good")
        self._ai("hint", "I'm stuck — give me the smallest next step, not the solution.", echo="I'm stuck.")

    def act_ask(self):
        q = self._prompt("Ask the tutor", "Your question:")
        if q:
            self._ai("ask", q, echo=q)

    def act_explain(self):
        q = self._prompt("Explain", "Which concept should I explain?")
        if q:
            self._ai("explain", "Explain: " + q, echo="Explain: " + q)

    def act_review(self):
        code = self.editor.get_code().strip()
        if not code:
            self._tutor("Tutor", "Write something in the editor first.", "dim")
            return
        c = self.current
        rubric = "the lesson task"
        if c["kind"] == "lesson":
            rubric = (self.courses[c["tid"]]["lessons"][c["idx"]].get("doThis") or {}).get("aiRubric", rubric)
        self._ai("review", "Rubric: %s\n\nMy code:\n\n%s\n\nReview it; don't rewrite it." % (rubric, code),
                 echo="[submitted my code for review]")

    def act_guide(self):
        code = self.editor.get_code().strip() or "(nothing written yet)"
        c = self.current
        rubric = "the lesson task"
        if c and c["kind"] == "lesson":
            rubric = (self.courses[c["tid"]]["lessons"][c["idx"]].get("doThis") or {}).get("aiRubric", rubric)
        self._ai("build_coach", "Requirements: %s\n\nMy current code:\n\n%s\n\nGuide me through the next concrete step." % (rubric, code),
                 echo="[asked to be walked through the next step]")

    def act_explain_problem(self):
        # Renders the clarification INLINE in the problem pane, right under the statement —
        # not in the little tutor box — so the fuller explanation is impossible to miss.
        c = self.current
        if not c or c["kind"] != "leet":
            return
        if self._busy:
            return
        key = self._api_keys()
        w = self.lesson_txt
        w.configure(state="normal")
        # drop any previous explanation, then open a fresh inline block at the end
        prev = w.search("PROBLEM, EXPLAINED", "1.0", "end")
        if prev:
            w.delete(prev + " linestart", "end")
        w.insert("end", "\n──────────  PROBLEM, EXPLAINED  ──────────\n", "h")
        if not key:
            w.insert("end", "Add a free Gemini key in ⚙ Settings to explain the problem.\n", "err")
            w.configure(state="disabled")
            return
        w.insert("end", "Clarifying the problem…\n", ("dim", "explain_pending"))
        w.see("end")
        w.configure(state="disabled")
        self._set_busy(True)
        p = c["problem"]
        sysp = prompts.system_for("problem_explainer")
        user = ("Problem: %s [%s]\n\nStatement:\n%s\n\nExamples:\n%s\n\n"
                "Explain this problem fully per your rules — clarify only, never solve.") % (
            p["title"], p["difficulty"], p["statement"], "\n".join(p["examples"]))

        def work():
            try:
                out = gemini(key, sysp, user)
            except Exception as e:
                out = "⚠ " + str(e)
            self.after(0, lambda: self._explain_done(out))
        threading.Thread(target=work, daemon=True).start()

    def _explain_done(self, out):
        self._set_busy(False)
        w = self.lesson_txt
        w.configure(state="normal")
        idx = w.search("Clarifying the problem…", "1.0", "end")
        if idx:
            w.delete(idx + " linestart", idx + " lineend +1c")
        w.insert(idx or "end", out + "\n", "b")
        w.see(idx or "end")
        w.configure(state="disabled")

    # ---- structured (JSON) generation: practice quizzes & the daily AI lesson ----

    def _json_call(self, key, system, user, validate):
        """Blocking helper for worker threads: ask → parse → validate, one retry that
        echoes the exact problem back, raise if it still fails. Nothing partial escapes."""
        prompt = user
        for attempt in range(2):
            raw = gemini(key, system, prompt, temperature=0.4)
            try:
                parsed = extract_json(raw)
                problem = validate(parsed)
            except Exception as e:
                problem = str(e)
            if not problem:
                return parsed
            if attempt == 0:
                time.sleep(4)  # free-tier pacing between the retry calls
                prompt = user + "\n\nYour previous reply was rejected: %s. Reply again with ONLY the corrected valid JSON." % problem
        raise RuntimeError("The AI couldn't produce valid content (%s). Nothing was kept — try again." % problem)

    @staticmethod
    def _valid_quiz_item(q):
        if not isinstance(q, dict) or not isinstance(q.get("q"), str) or not (8 <= len(q["q"]) <= 300):
            return "each question needs q (8-300 chars)"
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) != 4 or any(not isinstance(o, str) or not o.strip() for o in opts):
            return "each question needs exactly 4 non-empty options"
        if len({o.strip().lower() for o in opts}) != 4:
            return "options must be distinct"
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] <= 3:
            return "answer must be an integer 0-3"
        if not isinstance(q.get("why"), str) or len(q["why"]) < 8:
            return "each question needs a why"
        return None

    def _valid_practice(self, o):
        qs = o.get("questions") if isinstance(o, dict) else None
        if not isinstance(qs, list) or len(qs) != 4:
            return "questions must be an array of exactly 4"
        for q in qs:
            err = self._valid_quiz_item(q)
            if err:
                return err
            if not isinstance(q.get("detail"), str) or len(q["detail"]) < 40:
                return "each question needs a detailed explanation (detail, 40+ chars)"
        if len({q["answer"] for q in qs}) == 1:
            return "answer indices must not all be identical"
        return None

    def act_practice(self):
        c = self.current
        if not c or c["kind"] != "lesson":
            self._tutor("Tutor", "Open a lesson first — AI practice builds on the lesson you're viewing.", "dim")
            return
        if self._busy:
            return
        key = self._api_keys()
        if not key:
            self._tutor("Tutor", "Add a free Gemini key in ⚙ Settings first.", "err")
            return
        L = self.courses[c["tid"]]["lessons"][c["idx"]]
        body = "\n".join((s.get("p") or "") + ("\n" + s["code"] if s.get("code") else "") for s in L.get("read", []))[:2600]
        user = "Lesson: %s (track: %s)\n\nLESSON CONTENT:\n<<<\n%s\n>>>\n\nGenerate the 4-question practice set with growing difficulty." % (
            L["title"], c["tid"], body)
        self._tutor("You", "[asked for an AI practice set — 4 questions, growing difficulty]", "user")
        self._tutor("Tutor", "building the practice set…", "dim")
        self._set_busy(True)

        def work():
            try:
                data = self._json_call(key, prompts.QUIZ_GEN_SYS, user, self._valid_practice)
                self.after(0, lambda: (self._ai_done("Practice set ready — answer in the window that just opened."),
                                       self._open_quiz_win(L["title"], data["questions"])))
            except Exception as e:
                self.after(0, lambda e=e: self._ai_done("⚠ " + str(e)))
        threading.Thread(target=work, daemon=True).start()

    def _open_quiz_win(self, title, questions):
        win = tk.Toplevel(self)
        win.title("AI practice — " + title)
        win.configure(bg=C["bg"])
        win.geometry("680x520")
        st = {"i": 0, "score": 0}
        DIFF = {"warm-up": C["good"], "apply": C["warn"], "read": C["warn"], "hard": C["bad"]}

        head = tk.Label(win, bg=C["bg"], fg=C["fg"], font=UIB, anchor="w")
        head.pack(fill="x", padx=14, pady=(12, 2))
        qtxt = tk.Label(win, bg=C["bg"], fg=C["fg"], font=UI, wraplength=640, justify="left", anchor="w")
        qtxt.pack(fill="x", padx=14, pady=(2, 4))
        code = tk.Label(win, bg=C["panel"], fg=C["fg"], font=MONOS, wraplength=640, justify="left", anchor="w")
        btns = []
        for oi in range(4):
            b = tk.Button(win, font=UI, wraplength=600, justify="left", anchor="w", relief="flat",
                          bg=C["panel"], fg=C["fg"], activebackground=C["panel"],
                          command=lambda oi=oi: pick(oi))
            b.pack(fill="x", padx=14, pady=3)
            btns.append(b)
        fb = tk.Label(win, bg=C["bg"], fg=C["fg"], font=UI, wraplength=640, justify="left", anchor="w")
        fb.pack(fill="x", padx=14, pady=(8, 4))
        nxt = tk.Button(win, text="Next →", font=UIB, relief="flat", bg=C["panel"], fg=C["fg"], state="disabled")
        nxt.pack(pady=(2, 12))

        def show():
            q = questions[st["i"]]
            head.configure(text="Question %d/4 · %s" % (st["i"] + 1, q.get("difficulty", "")),
                           fg=DIFF.get(q.get("difficulty"), C["fg"]))
            qtxt.configure(text=q["q"])
            if q.get("code"):
                code.configure(text=q["code"])
                code.pack(fill="x", padx=14, pady=(0, 6), after=qtxt)
            else:
                code.pack_forget()
            for oi, b in enumerate(btns):
                b.configure(text="%s)  %s" % ("abcd"[oi], q["options"][oi]), bg=C["panel"], state="normal")
            fb.configure(text="")
            nxt.configure(state="disabled")

        def pick(oi):
            q = questions[st["i"]]
            for b in btns:
                b.configure(state="disabled")
            btns[q["answer"]].configure(bg="#14532d")
            if oi == q["answer"]:
                st["score"] += 1
                self.add_xp(2)
                self._save_state()
            else:
                btns[oi].configure(bg="#5f1d24")
            fb.configure(text=("✓ " if oi == q["answer"] else "✗ ") + q["why"] + "\n\n" + q.get("detail", ""))
            nxt.configure(state="normal")

        def advance():
            st["i"] += 1
            if st["i"] >= len(questions):
                head.configure(text="Done — %d/4 correct" % st["score"], fg=C["gold"])
                qtxt.configure(text="Growing-difficulty practice complete. Generate a fresh set any time — it's new questions every run.")
                code.pack_forget()
                for b in btns:
                    b.pack_forget()
                fb.configure(text="")
                nxt.configure(text="Close", command=win.destroy)
            else:
                show()
        nxt.configure(command=advance)
        show()

    # ---- AI keys: the Lab's own + the phone app's, synced through the hub ----

    def _api_keys(self):
        """Every usable Gemini key, in priority order: the Lab's own primary, its own BACKUP,
        then the phone app's primary + backup from the relayed app_state.json (the PWA syncs its
        keys through the hub, so pasting a key ONCE — on any device — serves every app).
        De-duplicated. gemini() rotates to the next key the moment one returns 429, which is what
        keeps the hourly background builder alive after the free tier's daily cap is hit."""
        raw = [self.state.get("apiKey", ""), self.state.get("apiKey2", "")]
        try:
            with open(os.path.join(HERE, "app_state.json"), encoding="utf-8") as f:
                s = json.load(f).get("settings") or {}
            raw += [s.get("geminiKey", ""), s.get("geminiKey2", "")]
        except Exception:
            pass
        keys = []
        for k in raw:
            k = (k or "").strip()
            if len(k) >= 20 and k not in keys:
                keys.append(k)
        return keys

    # ---- the daily AI lesson (the track LockIn has in store today) ----

    def _todays_track(self):
        """Rotates through THIS app's tracks by productive day (program days since Jul 14
        minus off-days spent before today, read from the relayed app_state.json)."""
        order = CODE_TRACKS if self.mode == "code" else THEORY_TRACKS
        start = datetime.date(2026, 7, 14)
        today = datetime.date.today()
        cal = max(0, (today - start).days)
        off = 0
        try:
            with open(os.path.join(HERE, "app_state.json"), encoding="utf-8") as f:
                spent = (json.load(f).get("offDays") or {}).get("spent") or []
            for k in spent:
                d = datetime.date(*[int(x) for x in k.split("-")])
                if start <= d < today:
                    off += 1
        except Exception:
            pass
        tid = order[max(0, cal - off) % len(order)]
        name = self.courses[tid]["title"].split("—")[0].strip() if tid in self.courses else tid
        return tid, name

    def _render_dailyai(self):
        self._set_test_btn(state="disabled")
        self.done_btn.configure(state="disabled")
        tid, tname = self._todays_track()
        today = datetime.date.today().isoformat()
        stored = self.state.get("dailyLesson")

        def draw(w):
            if stored and stored.get("date") == today:
                w.insert("end", "✨ TODAY'S AI LESSON · %s\n" % stored.get("trackName", tname), "user")
                w.insert("end", stored["title"] + "\n\n", "h")
                for sec in stored["sections"]:
                    w.insert("end", sec["h"] + "\n", "h")
                    w.insert("end", sec["body"] + "\n\n", "b")
                w.insert("end", "✅  QUICK CHECK — answer, then reveal\n", "h")
                for qi, q in enumerate(stored["quiz"]):
                    w.insert("end", "\n%d. %s\n" % (qi + 1, q["q"]), "b")
                    for oi, opt in enumerate(q["options"]):
                        w.insert("end", "   %s) %s\n" % ("abcd"[oi], opt), "opt")
                    rtag = "dai_rev_%d" % qi
                    atag = "dai_ans_%d" % qi
                    w.insert("end", "   [reveal answer]\n", ("opt", rtag))
                    w.insert("end", "   ✓ %s — %s\n" % ("abcd"[q["answer"]], q["why"]), (atag,))
                    w.tag_configure(atag, foreground=C["good"], elide=True)
                    w.tag_bind(rtag, "<Button-1>",
                               lambda _e, a=atag, r=rtag: (w.configure(state="normal"),
                                                           w.tag_configure(a, elide=False),
                                                           w.tag_configure(r, elide=True),
                                                           w.configure(state="disabled")))
                    w.tag_bind(rtag, "<Enter>", lambda _e: w.configure(cursor="hand2"))
                    w.tag_bind(rtag, "<Leave>", lambda _e: w.configure(cursor=""))
                w.insert("end", "\nA fresh lesson lands here tomorrow — the topic follows LockIn's daily track.\n", "dim")
            else:
                w.insert("end", "✨ TODAY'S AI LESSON\n", "user")
                w.insert("end", "%s — today's track in your LockIn rotation\n\n" % tname, "h")
                w.insert("end", "Every day the Lab can build you ONE extra lesson for the day's track: outline → "
                                "sections → quiz, three staged AI calls, each validated before anything is kept.\n\n", "b")
                w.insert("end", "🤖 Generate today's lesson →\n", ("opt", "genDaily"))
                w.tag_bind("genDaily", "<Button-1>", lambda _e: self._gen_dailyai())
                w.tag_bind("genDaily", "<Enter>", lambda _e: w.configure(cursor="hand2"))
                w.tag_bind("genDaily", "<Leave>", lambda _e: w.configure(cursor=""))
                if stored:
                    w.insert("end", "\nYesterday's lesson (%s): %s — generating replaces it.\n"
                             % (stored.get("date", "?"), stored.get("title", "?")), "dim")
        self._set_lesson(draw)
        self._to_tab(0)

    def _valid_daily_outline(self, o):
        if not isinstance(o, dict) or not isinstance(o.get("title"), str) or not (4 <= len(o["title"]) <= 90):
            return "title must be a 4-90 char string"
        secs = o.get("sections")
        if not isinstance(secs, list) or len(secs) != 3:
            return "sections must be exactly 3"
        for s in secs:
            if not isinstance(s, dict) or not isinstance(s.get("h"), str) or not isinstance(s.get("goal"), str):
                return "every section needs h and goal strings"
        return None

    def _valid_daily_sections(self, o):
        secs = o.get("sections") if isinstance(o, dict) else None
        if not isinstance(secs, list) or len(secs) != 3:
            return "sections must be exactly 3"
        for s in secs:
            if not isinstance(s, dict) or not isinstance(s.get("h"), str) or not isinstance(s.get("body"), str):
                return "every section needs h and body"
            if not (300 <= len(s["body"]) <= 2200):
                return "every body must be 300-2200 chars of teaching text"
        return None

    def _valid_daily_quiz(self, o):
        qs = o.get("quiz") if isinstance(o, dict) else None
        if not isinstance(qs, list) or len(qs) != 4:
            return "quiz must be exactly 4 questions"
        for q in qs:
            err = self._valid_quiz_item(q)
            if err:
                return err
        return None

    def _gen_dailyai(self):
        if self._busy:
            return
        key = self._api_keys()
        if not key:
            self._tutor("Tutor", "Add a free Gemini key in ⚙ Settings first.", "err")
            return
        tid, tname = self._todays_track()
        level = "advanced-beginner (he reads code well; new to this track's depths)"
        self._tutor("Tutor", "Building today's %s lesson — 3 staged calls, ~30s…" % tname, "dim")
        self._set_busy(True)

        def work():
            try:
                outline = self._json_call(key, prompts.DAILY_OUTLINE_SYS,
                    "Track: %s. Level: %s. Outline one lesson that best advances this track today." % (tname, level),
                    self._valid_daily_outline)
                time.sleep(4)
                secs = self._json_call(key, prompts.DAILY_SECTIONS_SYS,
                    "Lesson: %s (track %s).\nOutlined sections:\n%s\nWrite each section's body." % (
                        outline["title"], tname,
                        "\n".join("%d. %s — %s" % (i + 1, s["h"], s["goal"]) for i, s in enumerate(outline["sections"]))),
                    self._valid_daily_sections)
                time.sleep(4)
                full = "\n\n".join("%s\n%s" % (s["h"], s["body"]) for s in secs["sections"])
                quiz = self._json_call(key, prompts.DAILY_QUIZ_SYS,
                    "LESSON TEXT:\n<<<\n%s\n>>>\nWrite the 4-question self-check." % full,
                    self._valid_daily_quiz)
                lesson = {"date": datetime.date.today().isoformat(), "track": tid, "trackName": tname,
                          "title": outline["title"], "sections": secs["sections"], "quiz": quiz["quiz"]}

                def ok():
                    self.state["dailyLesson"] = lesson
                    self._save_state()
                    self._ai_done("✨ \"%s\" is ready — it's open in the lesson pane." % lesson["title"])
                    if self.current and self.current.get("kind") == "dailyai":
                        self._render_dailyai()
                self.after(0, ok)
            except Exception as e:
                self.after(0, lambda e=e: self._ai_done("⚠ " + str(e)))
        threading.Thread(target=work, daemon=True).start()

    # ---- the hourly background lesson builder ----
    # Fills in the curriculum's thin corners by itself: once an hour it picks whichever track of
    # THIS app's mode has the fewest lessons and writes one more for it. Generated lessons are
    # merged into their track as ordinary lessons, so they get the same tree entry, the same
    # graded checks, the same "Mark done" gate and the same phone sync as the authored ones.

    def _generated_to_lesson(self, g):
        """A stored AI lesson in the exact shape the renderer and grader expect."""
        return {
            "id": g["id"],
            "title": g["title"],
            "minutes": g.get("minutes", 20),
            "generated": True,
            "read": [{"h": s.get("h", ""), "p": s.get("body", "")} for s in g.get("sections", [])],
            "quiz": g.get("quiz") or [],
        }

    def _merge_generated(self):
        for tid, items in (self.state.get("genLessons") or {}).items():
            course = self.courses.get(tid)
            if not course:
                continue  # a track that no longer exists — keep the data, just don't show it
            have = {L["id"] for L in course["lessons"]}
            for g in items or []:
                if isinstance(g, dict) and g.get("id") and g["id"] not in have:
                    course["lessons"].append(self._generated_to_lesson(g))

    def _sparsest_track(self):
        """The track most in need of material: fewest lessons, ties broken by whichever went
        longest without being grown (so the builder rotates instead of fixating on one track)."""
        pool = CODE_TRACKS if self.mode == "code" else THEORY_TRACKS
        by = (self.state.get("autoGen") or {}).get("byTrack") or {}
        best = None
        for tid in pool:
            course = self.courses.get(tid)
            if not course:
                continue
            rank = (len(course["lessons"]), by.get(tid, 0))
            if best is None or rank < best[0]:
                best = (rank, tid)
        return best[1] if best else None

    def _autogen_tick(self):
        try:
            self._maybe_autogen()
        finally:
            self.after(AUTOGEN_CHECK_MS, self._autogen_tick)  # keep ticking whatever happens

    def _maybe_autogen(self):
        if self._busy or self._autogen_busy:
            return  # never compete with a call the user is waiting on
        if not self._api_keys():
            return  # no key configured — stay silent, this is a background nicety
        ag = self.state.setdefault("autoGen", {"last": 0, "byTrack": {}})
        if time.time() - (ag.get("last") or 0) < AUTOGEN_PERIOD_S:
            return
        tid = self._sparsest_track()
        if not tid:
            return
        # Claim the hour BEFORE the network call: if generation fails we wait for the next slot
        # rather than hammering the API (and the user's free-tier quota) in a tight retry loop.
        ag["last"] = time.time()
        self._save_state()
        self._autogen(tid)

    def _autogen(self, tid):
        keys = self._api_keys()
        course = self.courses[tid]
        tname = course["title"].split("—")[0].strip()
        known = [L["title"] for L in course["lessons"]]
        self._autogen_busy = True
        self._set_status()

        def work():
            try:
                outline = self._json_call(keys, prompts.AUTO_OUTLINE_SYS,
                    "Track: %s. Level: advanced-beginner (reads code well; new to this track's depths).\n"
                    "Existing lesson titles (pick a genuinely NEW topic):\n%s"
                    % (tname, "\n".join("- " + t for t in known)),
                    self._valid_auto_outline)
                time.sleep(4)  # free-tier pacing between staged calls
                secs = self._json_call(keys, prompts.AUTO_SECTIONS_SYS,
                    "Lesson: %s (track %s).\nOutlined sections:\n%s\nWrite each section's body."
                    % (outline["title"], tname,
                       "\n".join("%d. %s — %s" % (i + 1, s["h"], s["goal"])
                                 for i, s in enumerate(outline["sections"]))),
                    self._valid_auto_sections)
                time.sleep(4)
                full = "\n\n".join("%s\n%s" % (s["h"], s["body"]) for s in secs["sections"])
                quiz = self._json_call(keys, prompts.AUTO_QUIZ_SYS,
                    "LESSON TEXT:\n<<<\n%s\n>>>\nWrite the 6-question graded check." % full,
                    self._valid_auto_quiz)
                lesson = {
                    "id": "gen-%s-%d" % (tid, int(time.time())),
                    "title": outline["title"],
                    "date": datetime.date.today().isoformat(),
                    "minutes": 25,
                    "sections": secs["sections"],
                    "quiz": quiz["quiz"],
                }
                self.after(0, lambda: self._autogen_done(tid, lesson))
            except Exception:
                # Passive feature: a failed hour is a non-event. Never interrupt the user with it.
                self.after(0, lambda: self._autogen_done(tid, None))
        threading.Thread(target=work, daemon=True).start()

    def _autogen_done(self, tid, lesson):
        self._autogen_busy = False
        if lesson:
            self.state.setdefault("genLessons", {}).setdefault(tid, []).append(lesson)
            self.state.setdefault("autoGen", {}).setdefault("byTrack", {})[tid] = time.time()
            self.courses[tid]["lessons"].append(self._generated_to_lesson(lesson))
            self._save_state()
            self._add_lesson_node(tid)
        self._set_status()

    def _add_lesson_node(self, tid):
        """Show a just-generated lesson in the tree without rebuilding the whole thing
        (a rebuild would collapse the user's expanded tracks and drop their selection)."""
        node = "track:" + tid
        if not self.tree.exists(node):
            return
        lessons = self.courses[tid]["lessons"]
        i = len(lessons) - 1
        iid = "lesson:%s#%d" % (tid, i)
        if self.tree.exists(iid):
            return
        cap = "cap:" + tid
        at = self.tree.index(cap) if self.tree.exists(cap) else "end"  # keep the capstone last
        self.tree.insert(node, at, iid=iid, text="    ✨ %s" % lessons[i]["title"])

    def _valid_auto_outline(self, o):
        if not isinstance(o, dict) or not isinstance(o.get("title"), str) or not (4 <= len(o["title"]) <= 90):
            return "title must be a 4-90 char string"
        secs = o.get("sections")
        if not isinstance(secs, list) or len(secs) != 5:
            return "sections must be exactly 5"
        for s in secs:
            if not isinstance(s, dict) or not isinstance(s.get("h"), str) or not isinstance(s.get("goal"), str):
                return "every section needs h and goal strings"
        return None

    def _valid_auto_sections(self, o):
        secs = o.get("sections") if isinstance(o, dict) else None
        if not isinstance(secs, list) or len(secs) != 5:
            return "sections must be exactly 5"
        for s in secs:
            if not isinstance(s, dict) or not isinstance(s.get("h"), str) or not isinstance(s.get("body"), str):
                return "every section needs h and body"
            if not (900 <= len(s["body"]) <= 2600):
                return "every body must be 900-2600 chars (200-320 words) of teaching text"
        return None

    def _valid_auto_quiz(self, o):
        qs = o.get("quiz") if isinstance(o, dict) else None
        if not isinstance(qs, list) or len(qs) != 6:
            return "quiz must be exactly 6 questions"
        for q in qs:
            err = self._valid_quiz_item(q)
            if err:
                return err
            if not isinstance(q.get("detail"), str) or len(q["detail"]) < 40:
                return "every question needs a detail of at least 40 chars"
        return None

    def act_done(self):
        c = self.current
        if not c or c["kind"] != "lesson":
            return
        L = self.courses[c["tid"]]["lessons"][c["idx"]]
        lid = L["id"]
        if self._lesson_done(lid):
            del self.state["progress"][lid]
        else:
            # gate: you must pass every check before a lesson counts as learned
            quiz = L.get("quiz") or []
            checks = self.state.get("checks", {}).get(lid, {})
            passed = sum(1 for i in range(len(quiz)) if checks.get(str(i)))
            if quiz and passed < len(quiz):
                self._tutor("Checks", "Pass all %d checks first — you're at %d/%d. Scroll down and answer them; "
                            "that's how we know it actually stuck. 💪" % (len(quiz), passed, len(quiz)), "warn")
                return
            self.state["progress"][lid] = {"done": True, "date": self._today()}
            self.add_xp(15)
            self._mark_active()
            self.log_history("lesson", lid, L["title"])
        self._save_state()
        self._refresh_marks()
        self._update_check_status()

    # -------- misc --------
    def _lang_changed(self, _e=None):
        self.editor.language = self.lang_var.get()
        self.editor._highlight()

    def _cursor(self, line, col):
        self._set_status(cursor="%d:%d" % (line, col))

    def _save_code(self):
        eid = self._editor_id()
        if eid:
            self.state["code"][eid] = self.editor.get_code()
            if self._save_job:
                self.after_cancel(self._save_job)
            self._save_job = self.after(1200, self._save_state)

    def _set_status(self, cursor="1:1"):
        xp = self.state.get("xp", 0)
        solved = len(self.state.get("solved", {}))
        streak = self._streak()
        fire = "   |   🔥 %d-day streak" % streak if streak else ""
        self.status.config(text="  %s   |   lang: %s   |   ⚡ XP %d%s   |   solved %d   |   phone sync: %s"
                           % (cursor, self.lang_var.get(), xp, fire, solved, getattr(self, "sync_url", "…")))
        ok = bool(self._api_keys())
        if getattr(self, "_autogen_busy", False):
            self.ai_dot.config(text="✨ writing…", fg=C["violet"])  # the hourly builder is working
        else:
            self.ai_dot.config(text="● tutor" if ok else "○ tutor", fg=C["good"] if ok else C["warn"])

    def toggle_panel(self):
        if self.right in self.pw.panes() or str(self.right) in self.pw.panes():
            try:
                self.pw.forget(self.right)
            except Exception:
                pass
        else:
            self.pw.add(self.right, weight=2)

    def _prompt(self, title, label):
        win = tk.Toplevel(self); win.title(title); win.configure(bg=C["bg"]); win.transient(self); win.grab_set()
        tk.Label(win, text=label, bg=C["bg"], fg=C["fg"], font=UI).pack(padx=16, pady=(16, 6), anchor="w")
        e = tk.Text(win, width=52, height=3, bg=C["card"], fg=C["fg"], insertbackground=C["fg"], font=UI, relief="flat")
        e.pack(padx=16, pady=6); e.focus_set()
        out = {"v": None}
        def ok():
            out["v"] = e.get("1.0", "end").strip(); win.destroy()
        self._btn(win, "Send", ok, "primary").pack(pady=(6, 16))
        win.bind("<Control-Return>", lambda _e: ok())
        self.wait_window(win)
        return out["v"]

    def open_settings(self):
        win = tk.Toplevel(self); win.title("Settings"); win.configure(bg=C["bg"]); win.transient(self); win.grab_set()
        tk.Label(win, text="🤖 Gemini 2.5 Flash API key (free)", bg=C["bg"], fg=C["fg"], font=UIB).pack(padx=18, pady=(16, 4), anchor="w")
        tk.Label(win, text="Get one at aistudio.google.com/apikey — or leave this empty: keys pasted in the "
                 "phone app sync over through the hub and the Lab uses them automatically.",
                 bg=C["bg"], fg=C["mut"], font=UI, wraplength=430, justify="left").pack(padx=18, anchor="w")
        e = tk.Entry(win, width=56, bg=C["card"], fg=C["fg"], insertbackground=C["fg"], font=MONOS, relief="flat", show="•")
        e.pack(padx=18, pady=10); e.insert(0, self.state.get("apiKey", ""))
        tk.Label(win, text="🔑 Backup key (used automatically when the first one hits its rate limit)",
                 bg=C["bg"], fg=C["fg"], font=UIB).pack(padx=18, pady=(6, 4), anchor="w")
        tk.Label(win, text="Make a second key on another Google account. The hourly lesson builder runs off "
                 "these — with only one key it stops for the day as soon as the free tier is spent.",
                 bg=C["bg"], fg=C["mut"], font=UI, wraplength=430, justify="left").pack(padx=18, anchor="w")
        e2 = tk.Entry(win, width=56, bg=C["card"], fg=C["fg"], insertbackground=C["fg"], font=MONOS, relief="flat", show="•")
        e2.pack(padx=18, pady=10); e2.insert(0, self.state.get("apiKey2", ""))
        st = tk.Label(win, text="", bg=C["bg"], font=UI); st.pack(padx=18, anchor="w")

        def save():
            self.state["apiKey"] = e.get().strip(); self.state["apiKey2"] = e2.get().strip()
            self._save_state(); self._set_status(); st.config(text="Saved.", fg=C["good"])

        def test():
            self.state["apiKey"] = e.get().strip(); self.state["apiKey2"] = e2.get().strip()
            self._save_state(); self._set_status()
            st.config(text="Testing…", fg=C["mut"]); win.update()
            try:
                gemini(self._api_keys(), "Reply with exactly: OK", "ping", 0)
                st.config(text="✓ Connected (%d key%s available)." % (
                    len(self._api_keys()), "" if len(self._api_keys()) == 1 else "s"), fg=C["good"])
            except Exception as ex:
                st.config(text=str(ex), fg=C["bad"])

        row = tk.Frame(win, bg=C["bg"]); row.pack(padx=18, pady=6, fill="x")
        self._btn(row, "Save", save).pack(side="left"); self._btn(row, "Test", test, "primary").pack(side="left", padx=8)
        tk.Label(win, text="📱 Phone sync URL (type this into the app's Settings → Lab):", bg=C["bg"], fg=C["fg"], font=UIB).pack(padx=18, pady=(14, 2), anchor="w")
        u = tk.Entry(win, width=40, bg=C["card"], fg=C["acc2"], font=MONOS, relief="flat"); u.pack(padx=18, pady=(0, 8), anchor="w")
        u.insert(0, getattr(self, "sync_url", "")); u.configure(state="readonly")
        tk.Label(win, text="Phone and PC must be on the same Wi-Fi.", bg=C["bg"], fg=C["dim"], font=UI).pack(padx=18, anchor="w")
        self._btn(win, "Close", win.destroy).pack(pady=(6, 16))

    # -------- sync snapshot for the phone --------
    def snapshot(self):
        today = self._today()
        completed_today = [h["id"] for h in self.state["history"] if h["date"] == today]
        tracks = {}
        lessons_done = lessons_total = 0
        for tid, c in self.courses.items():
            done = sum(1 for L in c["lessons"] if self._lesson_done(L["id"]) or self._solved(L["id"]))
            tracks[tid] = {"title": c["title"].split("—")[0].strip(), "done": done, "total": len(c["lessons"])}
            lessons_done += done
            lessons_total += len(c["lessons"])
        dp = daily_problem(datetime.date.today().toordinal())
        return {
            "ok": True, "app": "LockIn Lab", "date": today,
            "xp": self.state.get("xp", 0),
            "streak": self._streak(),
            "solvedCount": len(self.state.get("solved", {})),
            "lessonsDone": lessons_done, "lessonsTotal": lessons_total,
            "leetToday": {"id": dp["id"], "title": dp["title"], "difficulty": dp["difficulty"], "solved": self._solved(dp["id"])},
            "tracks": tracks,
            "completedToday": completed_today,
            "completedTodayCount": len(completed_today),
        }


if __name__ == "__main__":
    # `python lockin_lab.py [code|theory|study]` — default is the code IDE.
    _mode = "theory" if (len(sys.argv) > 1 and sys.argv[1] in ("theory", "study")) else "code"
    Lab(mode=_mode).mainloop()
