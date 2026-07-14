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
import threading
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

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(HERE, "lab_state.json")
MODEL = "gemini-2.5-flash"
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


def gemini(api_key, system, user, temperature=0.6):
    if not api_key or len(api_key) < 20:
        raise RuntimeError("No API key set — open ⚙ Settings and paste a free Gemini key.")
    url = ENDPOINT % (MODEL, urllib.parse.quote(api_key))
    body = {"system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            # 2.5 Flash thinks by default; disable it so the token budget produces a visible answer.
            "generationConfig": {"temperature": temperature, "maxOutputTokens": 2048,
                                 "thinkingConfig": {"thinkingBudget": 0}}}
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        m = {400: "Bad request — the key looks wrong. Re-check it in Settings.",
             403: "Access denied (403) — make a fresh free key at aistudio.google.com/apikey.",
             429: "Rate limit hit (free tier). Wait a minute."}.get(e.code, "Gemini error %s." % e.code)
        raise RuntimeError(m)
    except urllib.error.URLError:
        raise RuntimeError("Network error — are you online?")
    cands = data.get("candidates") or []
    if not cands:
        raise RuntimeError("The tutor returned nothing — rephrase and retry.")
    return "".join(p.get("text", "") for p in cands[0].get("content", {}).get("parts", [])).strip()


class Lab(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LockIn Lab")
        self.configure(bg=C["bg"])
        self.geometry("1280x820")
        self.minsize(1040, 640)

        self.courses = content.build_courses()
        self.state = self._load_state()
        self.current = None
        self.language = "python"
        self._busy = False
        self._save_job = None

        self._style()
        self._build()
        self._populate_tree()

        # sync server for the phone
        self.sync = SyncServer(self.snapshot, port=self.state.get("syncPort", 8765))
        self.sync_url = self.sync.start() or "(sync off)"
        self._set_status()
        self._select_default()

    # -------- state --------
    def _load_state(self):
        base = {"apiKey": "", "syncPort": 8765, "progress": {}, "solved": {}, "code": {},
                "capstone": {}, "xp": 0, "history": [], "checks": {}, "activeDays": []}
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
        tk.Label(tb, text="◆ LockIn Lab", bg=C["panel"], fg=C["acc"], font=H1).pack(side="left", padx=(14, 8))
        self.run_btn = self._btn(tb, "▶ Run", self.act_run, "run"); self.run_btn.pack(side="left", padx=4, pady=6)
        self.test_btn = self._btn(tb, "✓ Run Tests", self.act_test, "test"); self.test_btn.pack(side="left", padx=4)
        self.reset_btn = self._btn(tb, "⟲ Reset", self.act_reset); self.reset_btn.pack(side="left", padx=4)
        tk.Label(tb, text="lang", bg=C["panel"], fg=C["dim"], font=UI).pack(side="left", padx=(12, 4))
        self.lang_var = tk.StringVar(value="python")
        self.lang_menu = ttk.Combobox(tb, textvariable=self.lang_var, values=["python", "c", "csharp", "asm"], width=9, state="readonly")
        self.lang_menu.pack(side="left")
        self.lang_menu.bind("<<ComboboxSelected>>", self._lang_changed)

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
        self.editor = CodeEditor(edwrap, C, MONO, on_cursor=self._cursor)
        self.editor.pack(fill="both", expand=True)
        cpw.add(edwrap, weight=4)

        console = tk.Frame(cpw, bg=C["bg"])
        self.console = ttk.Notebook(console)
        self.console.pack(fill="both", expand=True)
        self.out_txt = self._console_text()
        self.test_txt = self._console_text()
        self.console.add(self.out_txt.master, text="  Output  ")
        self.console.add(self.test_txt.master, text="  Tests  ")
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
        self._btn(aibar, "🏗 Guide me", self.act_guide).pack(side="left", padx=4)
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
        self.tree.insert("", "end", iid="daily", text="  ⭐  LeetCode — Daily")
        base_order = ["python", "csharp", "c", "asm", "linux", "cyber_high", "cyber_low", "cmd"]

        dsa = self.courses["dsa"]
        dnode = self.tree.insert("", "end", iid="track:dsa", text="  🧠  Data Structures & Algorithms", open=True)
        self._track_children(dnode, "dsa", dsa)

        cnode = self.tree.insert("", "end", iid="courses", text="  📚  Cyber courses", open=True)
        for tid in base_order:
            c = self.courses[tid]
            tnode = self.tree.insert(cnode, "end", iid="track:" + tid, text="   " + c["title"].split("—")[0].strip())
            self._track_children(tnode, tid, c)

        bnode = self.tree.insert("", "end", iid="leetbrowse", text="  🧩  LeetCode — Browse")
        for p in content.PROBLEMS:
            mark = "✓ " if self._solved(p["id"]) else "•  "
            self.tree.insert(bnode, "end", iid="leet:" + p["id"], text="   %s%s" % (mark, p["title"]))

    def _track_children(self, node, tid, course):
        for i, L in enumerate(course["lessons"]):
            done = self._lesson_done(L["id"]) or self._solved(L["id"])
            mark = "✓ " if done else "•  "
            self.tree.insert(node, "end", iid="lesson:%s#%d" % (tid, i), text="    %s%s" % (mark, L["title"]))
        self.tree.insert(node, "end", iid="cap:" + tid, text="    🏁 " + course["capstone"]["name"])

    def _refresh_marks(self):
        for iid in self.tree.get_children("leetbrowse"):
            pid = iid.split(":", 1)[1]
            p = content.BY_ID[pid]
            self.tree.item(iid, text="   %s%s" % ("✓ " if self._solved(pid) else "•  ", p["title"]))
        for tid, course in self.courses.items():
            node = "track:" + tid
            for i, L in enumerate(course["lessons"]):
                iid = "lesson:%s#%d" % (tid, i)
                if self.tree.exists(iid):
                    done = self._lesson_done(L["id"]) or self._solved(L["id"])
                    self.tree.item(iid, text="    %s%s" % ("✓ " if done else "•  ", L["title"]))

    def _select_default(self):
        self.tree.selection_set("daily")
        self.tree.focus("daily")
        self.on_select()

    # -------- selection & rendering --------
    def on_select(self, _e=None):
        sel = self.tree.focus()
        if sel == "daily":
            p = daily_problem(datetime.date.today().toordinal())
            self.current = {"kind": "leet", "problem": p, "daily": True}
            self._render_leet(p, daily=True)
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
            w.insert("end", "\nWrite %s(...) in the editor, then press ✓ Run Tests.\n" % p["func"], "dim")
        self._set_lesson(draw)
        self._load_editor(p["starter"], "python")
        self._to_tab(1)

    def _render_lesson(self, tid, idx):
        course = self.courses[tid]
        L = course["lessons"][idx]
        ex = L.get("exercise")
        self.test_btn.configure(text="✓ Run Tests" if ex else "✓ AI Check", state="normal")
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
                    w.insert("end", "Do it in your terminal; use the editor to experiment (▶ Run), then ✓ AI Check.\n", "dim")
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
                    w.tag_configure(extag, foreground=C["good"], elide=not solved_q)
                allpassed = all(checks.get(str(i)) for i in range(n))
                celtag = "cel_%s" % base
                w.insert("end", "\n🎉  All checks passed — you've PROVEN this one. Hit “Finish lesson”. \n", (celtag,))
                w.tag_configure(celtag, foreground=C["gold"], font=UIB, elide=not allpassed)
        self._set_lesson(draw)
        if L.get("quiz"):
            self._update_check_status()
        starters = {
            "c": ("c", "#include <stdio.h>\n\nint main(void) {\n    // Experiment here — press ▶ Run.\n    return 0;\n}\n"),
            "csharp": ("csharp", "using System;\n\nclass Program {\n    static void Main() {\n        // Experiment here — press ▶ Run.\n    }\n}\n"),
            "asm": ("asm", "; Intel syntax (nasm). Link with gcc: declare a global main and you can use printf.\n"
                           "global main\nextern printf\n\nsection .text\nmain:\n    ; experiment here — press ▶ Run\n    ret\n"),
        }
        if ex:
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
        self.test_btn.configure(state="disabled")
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
        for b in (self.run_btn, self.test_btn):
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
            # prose lesson → AI review
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
        key = self.state.get("apiKey", "")
        if len(key) < 20:
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
        ok = len(self.state.get("apiKey", "")) >= 20
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
        tk.Label(win, text="Get one at aistudio.google.com/apikey — stored only on this PC.", bg=C["bg"], fg=C["mut"], font=UI, wraplength=430, justify="left").pack(padx=18, anchor="w")
        e = tk.Entry(win, width=56, bg=C["card"], fg=C["fg"], insertbackground=C["fg"], font=MONOS, relief="flat", show="•")
        e.pack(padx=18, pady=10); e.insert(0, self.state.get("apiKey", ""))
        st = tk.Label(win, text="", bg=C["bg"], font=UI); st.pack(padx=18, anchor="w")

        def save():
            self.state["apiKey"] = e.get().strip(); self._save_state(); self._set_status(); st.config(text="Saved.", fg=C["good"])

        def test():
            self.state["apiKey"] = e.get().strip(); self._save_state(); self._set_status()
            st.config(text="Testing…", fg=C["mut"]); win.update()
            try:
                gemini(self.state["apiKey"], "Reply with exactly: OK", "ping", 0); st.config(text="✓ Connected.", fg=C["good"])
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
    Lab().mainloop()
