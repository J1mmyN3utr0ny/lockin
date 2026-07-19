# editor.py — a lightweight code editor widget: line-number gutter, Python/C syntax highlighting,
# 4-space tabs and auto-indent. Kept separate so lockin_lab.py stays about the app, not text plumbing.
import re
import tkinter as tk

PY_KW = ("def class return if elif else for while in not and or import from as with try except "
         "finally raise pass break continue None True False lambda yield global nonlocal is del "
         "assert await async").split()
PY_BUILTIN = ("print len range int str float list dict set tuple enumerate sorted sum min max abs "
              "map filter zip open input type bool reversed any all round").split()
C_KW = ("int char void float double long short unsigned signed struct typedef return if else for "
        "while do switch case break continue sizeof const static #include #define NULL").split()
CS_KW = ("using namespace class struct interface enum record public private protected internal static "
         "void int long short byte char bool string double float decimal object var new return if else "
         "for foreach while do switch case default break continue this base null true false try catch "
         "finally throw abstract virtual override sealed readonly const async await get set delegate "
         "event in out ref params yield is as typeof nameof").split()
ASM_KW = ("mov add sub mul imul div idiv inc dec cmp test and or xor not neg shl shr sal sar push pop "
          "call ret jmp je jne jz jnz jg jge jl jle ja jae jb jbe loop lea nop int syscall leave enter "
          "eax ebx ecx edx esi edi esp ebp rax rbx rcx rdx rsi rdi rsp rbp rip al bl cl dl ah bh ch dh "
          "section global extern db dw dd dq resb resw resd equ byte word dword qword ptr").split()


class CodeEditor(tk.Frame):
    def __init__(self, master, colors, font, on_cursor=None, **kw):
        super().__init__(master, bg=colors["editor"], **kw)
        self.c = colors
        self.on_cursor = on_cursor
        self.language = "python"

        self.gutter = tk.Text(self, width=4, padx=6, takefocus=0, border=0, background=colors["gutterbg"],
                              foreground=colors["gutterfg"], font=font, state="disabled", wrap="none", cursor="arrow")
        self.gutter.pack(side="left", fill="y")

        self.text = tk.Text(self, wrap="none", undo=True, border=0, padx=10, pady=8,
                            background=colors["editor"], foreground=colors["fg"],
                            insertbackground=colors["caret"], selectbackground=colors["sel"],
                            font=font, tabs=("1c",))
        vs = tk.Scrollbar(self, orient="vertical", command=self._yview)
        vs.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        self.text.configure(yscrollcommand=self._on_scroll, xscrollcommand=lambda *a: None)
        self._scrollbar = vs

        # a subtle full-width highlight on the line the caret is on — a calm "you are here"
        self.text.tag_configure("curline", background=colors.get("curline", colors["editor"]))
        self.text.tag_lower("curline")
        for name, col in (("kw", colors["kw"]), ("bi", colors["bi"]), ("str", colors["str"]),
                          ("com", colors["com"]), ("num", colors["num"]), ("fn", colors["fn"])):
            self.text.tag_configure(name, foreground=col)
        # indentation guides: one faint char-cell at each 4-space stop, drawn on the leading
        # whitespace only (never behind code) and continued through blank lines so they read as
        # clean, continuous vertical rules rather than the old disconnected blocks.
        self.text.tag_configure("guide", foreground=colors.get("guide", "#172131"),
                                background=colors.get("guide", "#172131"))
        self.text.tag_lower("guide")
        self.text.tag_lower("curline", "guide")  # curline sits below the guides

        self.text.bind("<KeyRelease>", self._changed)  # _changed calls _cursor -> _draw_curline
        self.text.bind("<ButtonRelease>", self._cursor)
        self.text.bind("<Tab>", self._tab)
        self.text.bind("<Return>", self._enter)
        self.text.bind("<MouseWheel>", lambda e: self.after(1, self._draw_gutter))
        self._hl_job = None
        self._draw_gutter()
        self._draw_curline()

    # ---- scrolling: keep gutter in lockstep with the code ----
    def _yview(self, *args):
        self.text.yview(*args)
        self.gutter.yview(*args)

    def _on_scroll(self, first, last):
        self._scrollbar.set(first, last)
        self.gutter.yview_moveto(first)

    # ---- public ----
    def set_code(self, code, language="python"):
        self.language = language
        self.text.delete("1.0", "end")
        self.text.insert("1.0", code or "")
        self.text.edit_reset()
        self.text.mark_set("insert", "1.0")
        self._draw_gutter()
        self._draw_guides()
        self._draw_curline()
        self._highlight()

    def get_code(self):
        return self.text.get("1.0", "end-1c")

    def focus_code(self):
        self.text.focus_set()

    # ---- events ----
    def _changed(self, _e=None):
        self._draw_gutter()
        self._draw_guides()
        self._cursor()
        if self._hl_job:
            self.after_cancel(self._hl_job)
        self._hl_job = self.after(140, self._highlight)

    def _cursor(self, _e=None):
        self._draw_curline()
        if self.on_cursor:
            line, col = self.text.index("insert").split(".")
            self.on_cursor(int(line), int(col) + 1)

    def _draw_curline(self):
        """Highlight the caret's line (subtle, full width)."""
        t = self.text
        t.tag_remove("curline", "1.0", "end")
        ln = t.index("insert").split(".")[0]
        t.tag_add("curline", "%s.0" % ln, "%s.0+1lines" % ln)

    def _tab(self, _e):
        self.text.insert("insert", "    ")
        return "break"

    def _enter(self, _e):
        line = self.text.get("insert linestart", "insert")
        indent = re.match(r"[ \t]*", line).group(0)
        stripped = line.rstrip()
        if self.language == "python" and stripped.endswith(":"):
            indent += "    "
        elif self.language in ("c", "csharp") and stripped.endswith("{"):
            indent += "    "
        self.text.insert("insert", "\n" + indent)
        self._draw_gutter()
        self._draw_guides()
        return "break"

    def _draw_guides(self):
        """Indent guides at each 4-space stop, continued through blank lines so a block's guides
        form an unbroken vertical rule. A blank line inherits the indent of the next code line
        (the way real IDEs carry guides across the gaps inside a function)."""
        t = self.text
        t.tag_remove("guide", "1.0", "end")
        total = int(t.index("end-1c").split(".")[0])
        raw = [t.get("%d.0" % ln, "%d.end" % ln) for ln in range(1, total + 1)]
        # level per line; blanks get the level of the NEXT non-blank line (0 if none follows)
        levels = [0] * total
        next_level = 0
        for i in range(total - 1, -1, -1):
            stripped = raw[i].lstrip(" ")
            if stripped:
                next_level = (len(raw[i]) - len(stripped)) // 4
                levels[i] = next_level
            else:
                levels[i] = next_level  # carry the block's indent through the gap
        for i, lvl in enumerate(levels):
            ln = i + 1
            line_len = len(raw[i])
            for lv in range(lvl):
                col = lv * 4
                # only paint where there is actually whitespace (never behind code); on a blank
                # line the cells do not exist, so guard the column against the line length
                if col <= line_len:
                    t.tag_add("guide", "%d.%d" % (ln, col), "%d.%d" % (ln, col + 1))

    def _draw_gutter(self):
        n = int(self.text.index("end-1c").split(".")[0])
        self.gutter.configure(state="normal")
        self.gutter.delete("1.0", "end")
        self.gutter.insert("1.0", "\n".join(str(i) for i in range(1, n + 1)))
        self.gutter.configure(state="disabled")
        self.gutter.yview_moveto(self.text.yview()[0])

    def _highlight(self):
        self._hl_job = None
        t = self.text
        code = t.get("1.0", "end-1c")
        for tag in ("kw", "bi", "str", "com", "num", "fn"):
            t.tag_remove(tag, "1.0", "end")

        def apply(tag, pattern, group=0):
            for m in re.finditer(pattern, code):
                s, e = m.start(group), m.end(group)
                t.tag_add(tag, "1.0+%dc" % s, "1.0+%dc" % e)

        lang = self.language
        kws = {"c": C_KW, "csharp": CS_KW, "asm": ASM_KW}.get(lang, PY_KW)
        apply("num", r"\b\d+\.?\d*\b|\b0x[0-9a-fA-F]+\b")
        apply("kw", r"(?<![\w#.])(" + "|".join(re.escape(k) for k in kws) + r")(?![\w])")
        if lang == "python":
            apply("bi", r"\b(" + "|".join(PY_BUILTIN) + r")\b")
            apply("fn", r"(?:def|class)\s+(\w+)", 1)
        elif lang == "asm":
            apply("fn", r"(?m)^[ \t]*(\w+):", 1)  # labels
        # strings: include <...> only for C #include lines
        apply("str", r"(\"[^\"\n]*\"|'[^'\n]*'" + (r"|<[^>\n]+>" if lang == "c" else "") + r")")
        com = {"c": r"//[^\n]*", "csharp": r"//[^\n]*", "asm": r";[^\n]*"}.get(lang, r"#[^\n]*")
        apply("com", com)
        for tag in ("str", "com"):
            t.tag_raise(tag)
