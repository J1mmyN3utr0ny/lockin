# runner.py — executes the user's code safely-ish (their own machine, their own code) with a
# timeout, and runs LeetCode/DSA exercises against their test cases. Python always; C if gcc exists.
import json
import os
import shutil
import subprocess
import sys
import tempfile

PY = sys.executable or "python"
TIMEOUT = 8  # seconds


def have_gcc():
    return shutil.which("gcc") is not None


def have_dotnet():
    return shutil.which("dotnet") is not None


def have_nasm():
    return shutil.which("nasm") is not None and shutil.which("gcc") is not None


def _run(cmd, cwd, timeout=TIMEOUT, stdin="", env=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout, env=env)
        return {"stdout": p.stdout, "stderr": p.stderr, "exit": p.returncode, "timed_out": False}
    except subprocess.TimeoutExpired as e:
        return {"stdout": e.stdout or "", "stderr": (e.stderr or "") +
                "\n[stopped after %ss — likely an infinite loop]" % timeout, "exit": -1, "timed_out": True}
    except Exception as e:
        return {"stdout": "", "stderr": "runner error: %r" % e, "exit": -1, "timed_out": False}


def run_python(code, stdin=""):
    """Run free-form Python and capture output."""
    d = tempfile.mkdtemp(prefix="lockin_")
    try:
        path = os.path.join(d, "main.py")
        open(path, "w", encoding="utf-8").write(code)
        return _run([PY, "-I", path], d, stdin=stdin)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def run_c(code, stdin=""):
    """Compile with gcc then run. Returns compile errors if any."""
    if not have_gcc():
        return {"stdout": "", "stderr": "gcc not found — install it (or use WSL) to run C here.\n"
                "The lesson still works: build & run C in your own terminal.", "exit": -1, "timed_out": False}
    d = tempfile.mkdtemp(prefix="lockin_")
    try:
        src = os.path.join(d, "main.c")
        out = os.path.join(d, "a.exe" if os.name == "nt" else "a.out")
        open(src, "w", encoding="utf-8").write(code)
        comp = _run(["gcc", src, "-o", out, "-std=c11", "-Wall"], d, timeout=20)
        if comp["exit"] != 0:
            return {"stdout": "", "stderr": "compile error:\n" + comp["stderr"], "exit": comp["exit"], "timed_out": False}
        res = _run([out], d, stdin=stdin)
        if comp["stderr"].strip():
            res["stderr"] = "warnings:\n" + comp["stderr"] + "\n" + res["stderr"]
        return res
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _dotnet_tfm():
    """Target framework matching the installed SDK (e.g. net9.0), so the temp project builds."""
    try:
        v = subprocess.run(["dotnet", "--version"], capture_output=True, text=True, timeout=15).stdout.strip()
        major = v.split(".")[0]
        return "net%s.0" % major if major.isdigit() else "net8.0"
    except Exception:
        return "net8.0"


_CSPROJ = ('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
           '<OutputType>Exe</OutputType><TargetFramework>%s</TargetFramework>'
           '<Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings>'
           '<AssemblyName>app</AssemblyName></PropertyGroup></Project>')


def run_csharp(code, stdin=""):
    """Compile & run C# via the .NET SDK (dotnet run). Slower on the first build; that's normal."""
    if not have_dotnet():
        return {"stdout": "", "stderr": "dotnet not found — install the free .NET SDK "
                "(dotnet.microsoft.com/download) to run C# here. The lesson still works: build & run it "
                "in your own editor.", "exit": -1, "timed_out": False}
    d = tempfile.mkdtemp(prefix="lockin_cs_")
    try:
        open(os.path.join(d, "Program.cs"), "w", encoding="utf-8").write(code)
        open(os.path.join(d, "app.csproj"), "w", encoding="utf-8").write(_CSPROJ % _dotnet_tfm())
        env = dict(os.environ, DOTNET_NOLOGO="1", DOTNET_CLI_TELEMETRY_OPTOUT="1",
                   DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1", DOTNET_CLI_HOME=d)
        res = _run(["dotnet", "run", "--project", d, "-v", "q", "--nologo"], d, timeout=90, stdin=stdin, env=env)
        return res
    finally:
        shutil.rmtree(d, ignore_errors=True)


def run_asm(code, stdin=""):
    """Assemble with nasm and link with gcc (write a global `main:` and you can use the C library)."""
    if not have_nasm():
        return {"stdout": "", "stderr": "assembly needs nasm + gcc on your PATH (or run it in a Linux "
                "VM / WSL). Tip: declare `global main`, write `main:`, and link with gcc so printf/ret work.",
                "exit": -1, "timed_out": False}
    d = tempfile.mkdtemp(prefix="lockin_asm_")
    try:
        src = os.path.join(d, "prog.asm")
        obj = os.path.join(d, "prog.obj" if os.name == "nt" else "prog.o")
        out = os.path.join(d, "prog.exe" if os.name == "nt" else "prog.out")
        open(src, "w", encoding="utf-8").write(code)
        fmt = "win64" if os.name == "nt" else "elf64"
        asm = _run(["nasm", "-f", fmt, src, "-o", obj], d, timeout=20)
        if asm["exit"] != 0:
            return {"stdout": "", "stderr": "assemble error:\n" + asm["stderr"], "exit": asm["exit"], "timed_out": False}
        link = _run(["gcc", obj, "-o", out, "-no-pie"], d, timeout=20)
        if link["exit"] != 0:
            return {"stdout": "", "stderr": "link error:\n" + link["stderr"], "exit": link["exit"], "timed_out": False}
        return _run([out], d, stdin=stdin)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# Harness driver: defines a comparator, runs the user's function against each case, prints results.
_DRIVER = r'''
import json, sys, copy
def __cmp(a, b, mode):
    try:
        if mode == "unordered": return sorted(a) == sorted(b)
        if mode == "groups":
            norm = lambda g: sorted(sorted(x) for x in g)
            return norm(a) == norm(b)
        if mode == "intervals":
            return sorted([list(x) for x in a]) == sorted([list(x) for x in b])
        if mode == "approx": return abs(a - b) < 1e-6
        return a == b
    except Exception:
        return False

# ===================== USER CODE =====================
%(user)s
# =================== END USER CODE ===================

__tests = json.loads(r"""%(tests)s""")
__mode = %(mode)r
__fn = globals().get(%(func)r)
__out = []
if __fn is None:
    for __t in __tests:
        __out.append({"ok": False, "err": "no function named %(func)s defined"})
else:
    for __t in __tests:
        try:
            __args = copy.deepcopy(__t["args"])
            __g = __fn(*__args)
            __ok = bool(__cmp(__g, __t["expect"], __mode))
            __out.append({"ok": __ok, "got": repr(__g)})
        except Exception as __e:
            __out.append({"ok": False, "err": repr(__e)})
sys.stdout.write("\n__LOCKIN_RESULTS__" + json.dumps(__out))
'''

MARKER = "__LOCKIN_RESULTS__"


def run_tests(user_code, exercise):
    """Run user_code against exercise['tests']. Returns {cases:[...], passed, total, user_output, error}."""
    tests = exercise["tests"]
    driver = _DRIVER % {
        "user": user_code,
        "tests": json.dumps(tests),
        "mode": exercise.get("compare", "exact"),
        "func": exercise["func"],
    }
    d = tempfile.mkdtemp(prefix="lockin_")
    try:
        path = os.path.join(d, "harness.py")
        open(path, "w", encoding="utf-8").write(driver)
        res = _run([PY, "-I", path], d)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    raw = res["stdout"]
    idx = raw.rfind(MARKER)
    if idx == -1:
        # crashed before finishing (syntax error, timeout, etc.)
        err = res["stderr"] or "no output"
        if res["timed_out"]:
            err = "timed out — likely an infinite loop."
        return {"cases": [], "passed": 0, "total": len(tests), "user_output": raw,
                "error": err.strip()}
    user_output = raw[:idx].rstrip("\n")
    try:
        results = json.loads(raw[idx + len(MARKER):])
    except Exception:
        return {"cases": [], "passed": 0, "total": len(tests), "user_output": user_output,
                "error": "could not parse test results"}
    cases = []
    passed = 0
    for t, r in zip(tests, results):
        ok = bool(r.get("ok"))
        passed += 1 if ok else 0
        cases.append({
            "ok": ok,
            "args": t["args"],
            "expect": t["expect"],
            "got": r.get("got", r.get("err", "—")),
        })
    return {"cases": cases, "passed": passed, "total": len(tests),
            "user_output": user_output, "error": None}
