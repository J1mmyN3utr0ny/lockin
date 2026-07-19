# quizbank_python.py - additional graded checks for the python track.
# Merged onto each lesson's existing quiz by content.build_courses().
# Answer indices balanced across the file so the correct option isn't always first.
EXTRA_QUIZ = {
    "py-1": [
        {
            "q": "In a script, you call greet() on line 4, but greet is not def'd until line 40, further down the same file. What happens?",
            "code": "",
            "options": [
                "NameError, because greet's function object doesn't exist until its def statement actually runs",
                "It works fine — Python scans the whole file for definitions before running anything",
                "SyntaxError at compile time, before the script starts",
                "It silently calls an empty placeholder function"
            ],
            "answer": 0,
            "why": "def is an executable statement; the function object is created only when that line actually runs, so calling it earlier finds nothing bound to the name yet.",
            "detail": "Java resolves method names at class-load time regardless of source order, which is why this trips up Java-trained instincts — Python has no such pre-pass; module code, including every def, runs top to bottom. There is no compile-time check that would catch this before execution, since Python does not know in advance which names will exist by the time a call runs. And Python never invents a placeholder function to call in place of a missing one — a genuinely undefined name always raises immediately."
        },
        {
            "q": "A function reads a variable's current value on its first line, then assigns to that same variable later in the function body — with no global declaration anywhere. What happens on the read?",
            "code": "",
            "options": [
                "It reads the current module-level global value",
                "UnboundLocalError — assigning to the name anywhere in the function makes it local for the function's entire body",
                "It silently evaluates to None",
                "NameError, because the name was never declared anywhere"
            ],
            "answer": 1,
            "why": "Python decides a name is local for the whole function if it's assigned anywhere inside it, even on lines that execute before that assignment.",
            "detail": "This is resolved statically from the function's source before it ever runs — Python does not look ahead at runtime to decide the read should instead fall back to a same-named global. Falling through to the global only happens when the function never assigns to that name at all. Nothing about this situation makes the value quietly become None. And the exception raised is specifically UnboundLocalError, not NameError — UnboundLocalError means the name IS local here but hasn't been assigned yet on this path, which is a more precise and different situation than a name that doesn't exist anywhere in scope."
        },
        {
            "q": "Predict the output.",
            "code": "def add_item(item, bucket=[]):\n    bucket.append(item)\n    return bucket\n\nprint(add_item('a'))\nprint(add_item('b'))",
            "options": [
                "['a'] then ['b']",
                "Raises an error on the second call",
                "['a'] then ['a', 'b']",
                "['b'] then ['a', 'b']"
            ],
            "answer": 2,
            "why": "The default list is created exactly once, when def runs, and every call that omits bucket reuses that same list object.",
            "detail": "Both calls share the identical list because Python evaluates default argument expressions once, at function-definition time, not fresh on every call. The first call appends 'a' to that shared list and returns it; the second call appends 'b' to the SAME list, so it now holds both values. A fresh empty list on every call, giving ['a'] then ['b'], is what a beginner expects but is not what actually happens. Getting the second result right while assuming the first call already forgot 'a' misunderstands which list is shared. And no error occurs at all here — the code runs, it just doesn't do what its author probably intended."
        },
        {
            "q": "Predict the output.",
            "code": "fns = []\nfor i in range(3):\n    fns.append(lambda: i)\n\nprint([f() for f in fns])",
            "options": [
                "[0, 1, 2]",
                "[0, 0, 0]",
                "TypeError: lambda takes no arguments",
                "[2, 2, 2]"
            ],
            "answer": 3,
            "why": "All three lambdas share the same enclosing variable i, which holds its final value, 2, by the time any of them is actually called.",
            "detail": "A closure captures the VARIABLE i itself, not a snapshot of its value at creation time — this is late binding. By the time the list comprehension calls each f(), the for loop has already finished and i is 2 for all three lambdas equally. Each lambda 'remembering' the value it had when created, giving [0, 1, 2], is what many beginners wish would happen, but that requires an explicit trick like `lambda i=i: i` to actually capture the value at that point. Getting the same wrong constant for a different reason, like [0, 0, 0], misidentifies which value i ends up holding. And the lambda is defined with zero parameters and called with zero arguments, so no TypeError occurs at all."
        },
        {
            "q": "A teammate's compute_total() gives a different answer each time you call it with the exact same argument. It has no default arguments and no randomness anywhere. What's the most likely cause?",
            "code": "",
            "options": [
                "compute_total silently reads a global/module-level variable that other code mutates between calls",
                "Python caches function results and sometimes serves a stale one",
                "Integers in Python are mutable, so the argument itself changed",
                "compute_total behaves differently depending on which file imported it from"
            ],
            "answer": 0,
            "why": "A function that reaches outside its own parameters and locals, via the LEGB chain, is silently coupled to whatever else mutates that global state between calls.",
            "detail": "This is the practical cost of Python's scoping rules: a function that doesn't take everything it needs as a parameter can produce different results purely because something else in the program changed a global between calls, with nothing at the call site hinting at that dependency. Python functions have no automatic result caching by default, so nothing is being silently reused here. Python ints are immutable — a passed-in int argument cannot change value out from under the function. And where a function was imported from has no bearing on what it computes; only the code inside it and whatever state it reads determine that."
        },
        {
            "q": "You fix the mutable-default-argument bug with `def add_item(item, bucket=None): if bucket is None: bucket = []`. A colleague suggests simplifying the check to `if not bucket:` instead. Why is that a worse fix?",
            "code": "",
            "options": [
                "`not bucket` never works on lists, so this would crash",
                "`not bucket` would also treat a caller's deliberately-passed empty list as 'not provided,' silently replacing it with a brand new list instead of reusing the caller's actual object",
                "There's no real difference — both checks are equally correct",
                "It would raise a TypeError the first time bucket is None"
            ],
            "answer": 1,
            "why": "An empty list is falsy, so `not bucket` can't tell 'caller passed nothing' apart from 'caller passed an empty list on purpose.'",
            "detail": "If a caller explicitly passes their own empty list, intending later appends to affect that specific object, `if not bucket:` wrongly treats it as 'not provided' and swaps in a different new list — any reference the caller kept to their original list is now silently disconnected from what add_item is filling. `is None` correctly tests only for the one case that should trigger the fallback: nothing was passed at all. `not []` evaluates to True in Python, so the check works, just on the wrong cases (ruling out the crash claim). And no TypeError occurs at any point in either version of this code — the bug is purely a logic error, not a runtime failure."
        }
    ],
    "py-2": [
        {
            "q": "car.describe() and Car.describe(car) do exactly the same thing. Why?",
            "code": "",
            "options": [
                "self is a reserved keyword that Python substitutes automatically",
                "Car.describe is compiled into a separate copy of the method for every instance",
                "describe is a function object living on the class; accessing it through an instance produces a bound method that injects car as the first argument automatically",
                "Python special-cases every method call with dedicated bytecode different from an ordinary function call"
            ],
            "answer": 2,
            "why": "Functions are descriptors — looking one up through an instance produces a bound method that has already been paired with that instance, filling in the first argument automatically.",
            "detail": "This descriptor protocol (a __get__ method on the function object) is exactly how car.describe() becomes Car.describe(car) with no special-case bytecode required beyond ordinary attribute lookup. self is genuinely just a conventional parameter name, not a reserved keyword — you could rename it, though nobody should. And there is exactly one function object shared by the class; only a lightweight bound-method wrapper is created per lookup, not a full copy of the method's code."
        },
        {
            "q": "Why does defining __eq__ on a class, without also defining __hash__, make its instances unhashable?",
            "code": "",
            "options": [
                "Python requires every class to define __hash__ manually, with no exceptions",
                "This is unrelated — it's a known inconsistency in CPython",
                "Only classes decorated with @dataclass are allowed to be hashable",
                "Because equal objects must hash equally, and the inherited identity-based hash could violate that once __eq__ redefines what equal means"
            ],
            "answer": 3,
            "why": "Python removes the inherited __hash__ the moment you override __eq__, because reusing the old identity-based hash could break the rule that equal objects must hash equally.",
            "detail": "object supplies a working identity-based __hash__ by default, but that hash has nothing to do with your new field-based equality — reusing it could put two 'equal' objects into different hash buckets, corrupting sets and dicts. Plenty of ordinary classes keep the default hash just fine, as long as they never override __eq__, so there's no blanket requirement to write __hash__ yourself. This is a deliberate, documented safety behavior, not an inconsistency or bug. And while it's true that @dataclass can auto-generate a compatible hash for you, hashability isn't restricted to dataclasses at all — it's about whether __eq__ and __hash__ are consistent with each other."
        },
        {
            "q": "Predict the output.",
            "code": "class Player:\n    inventory = []\n    def __init__(self, name):\n        self.name = name\n\np1 = Player('Ari')\np2 = Player('Ben')\np1.inventory.append('sword')\nprint(p2.inventory)",
            "options": [
                "['sword']",
                "[]",
                "AttributeError",
                "['Ari', 'Ben']"
            ],
            "answer": 0,
            "why": "inventory is a single class-level list shared by every instance, so mutating it through p1 is visible through p2 too.",
            "detail": "Because inventory is written directly in the class body rather than assigned per-instance in __init__ via self, there is only ONE list object, stored on the class, and both p1 and p2 fall through to that same object whenever their own instance __dict__ has no 'inventory' entry of its own. Appending through p1.inventory mutates that one shared object in place, so p2 sees the change too. Each instance having its own fresh, independent list would give an empty list here, but that is not what this code does. Attribute lookup succeeds cleanly through the class, so no AttributeError occurs. And this prints inventory contents, not the instances' names, so the two are not related here at all."
        },
        {
            "q": "Predict the output.",
            "code": "class Vector:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n    def __eq__(self, other):\n        return self.x == other.x and self.y == other.y\n\na = Vector(1, 2)\nb = Vector(1, 2)\nprint(a == b, a is b)",
            "options": [
                "True True",
                "True False",
                "False False",
                "False True"
            ],
            "answer": 1,
            "why": "== routes through the custom __eq__ and finds matching fields, but is always checks object identity, and a and b are two separately constructed objects.",
            "detail": "__eq__ explicitly compares x and y, so a == b is True since both vectors hold (1, 2). is never consults __eq__ at all — it only asks whether the two names refer to the same object in memory, and since a and b were built from two separate Vector(...) calls, they are not the same object, so a is b is False. is somehow also returning True would require Python to treat value-equal objects as identical, which it never does. And swapping which comparison is True and which is False the other way around does not match how == and is are each actually defined here."
        },
        {
            "q": "Your Inventory class defines __slots__ = ('items',). A teammate's subclass tries to add `self.owner = 'p1'` inside its own __init__ and gets AttributeError: 'Inventory' object has no attribute 'owner'. What's going on?",
            "code": "",
            "options": [
                "owner is misspelled somewhere else in the class",
                "self was not passed correctly to __init__",
                "__slots__ removes the per-instance __dict__, so only attribute names declared in __slots__ — on this class or the subclass — can ever be set",
                "Subclasses in Python can never add new attributes beyond their parent's"
            ],
            "answer": 2,
            "why": "A slotted class has no instance __dict__ to absorb arbitrary new attributes — only names explicitly declared in __slots__ somewhere in the class hierarchy are allowed.",
            "detail": "This is the direct tradeoff of __slots__: faster, smaller instances, at the cost of losing free-form attribute creation. The fix is for the subclass to declare its own __slots__ = ('owner',) to add that slot. The error message given is exact and specific to attribute storage, not a sign of a typo elsewhere. This also isn't an argument-passing problem — self is bound normally here; the failure happens specifically when trying to CREATE a new attribute that has nowhere to live. And ordinary, non-slotted subclasses add new attributes freely all the time, so the restriction here is specifically about __slots__, not subclassing in general."
        },
        {
            "q": "@dataclass auto-generates __init__, __repr__, and __eq__ from a class's annotated fields. For a class that must enforce 'balance can never go negative' at construction time, why can't a plain @dataclass do the whole job by itself?",
            "code": "",
            "options": [
                "Dataclasses cannot define any methods of their own at all",
                "@dataclass is incompatible with __slots__ and always will be",
                "Dataclasses can only hold string-typed fields",
                "The generated __init__ is a straight-line series of field assignments, with no hook for conditional validation logic before assigning"
            ],
            "answer": 3,
            "why": "The auto-generated constructor just assigns each field directly — there's no branching or validation step built into that generated code.",
            "detail": "You can still add a __post_init__ method to a dataclass to run validation right after the generated __init__ finishes, or fall back to a hand-written property with a real setter body for one specific field, but the generated constructor itself contains no conditional logic at all. Dataclasses can absolutely define ordinary methods alongside the generated ones, so that isn't the limitation. Python has supported slots=True on dataclasses since 3.10 specifically to combine both features, so they aren't fundamentally incompatible. And dataclass fields can be annotated with any type at all, not just strings."
        }
    ],
    "py-3": [
        {
            "q": "Two threads in the same Python process both run a tight CPU-bound loop doing pure arithmetic, on an 8-core machine. What actually happens?",
            "code": "",
            "options": [
                "They run no faster than a single thread, because the GIL lets only one thread execute Python bytecode at a time",
                "They run roughly twice as fast, using two of the eight cores",
                "The program deadlocks immediately",
                "Python automatically moves one of them to a separate process"
            ],
            "answer": 0,
            "why": "CPython's GIL allows only one thread to execute Python bytecode at any instant, so two purely CPU-bound threads simply take turns rather than running in parallel.",
            "detail": "This is exactly why threading does not speed up CPU-bound work in CPython — the GIL exists because CPython's reference-counting memory management is not thread-safe without some form of serialization. Genuine parallelism for CPU-bound work needs multiprocessing instead — separate processes, each with its own interpreter and its own GIL. Nothing about two arithmetic-only threads causes a deadlock; they simply alternate. And Python never silently reassigns a thread to a new process — that requires explicitly using the multiprocessing module yourself."
        },
        {
            "q": "Why does learning socket's bind/listen/accept/connect/send/recv methods transfer so directly to networking code you'll later write in C or C#?",
            "code": "",
            "options": [
                "It doesn't — each language's networking API is unrelated to the others",
                "Because socket is a thin wrapper around the same underlying OS sockets API that other languages' networking calls expose almost directly",
                "Because Python's socket module is written in pure Python with no OS involvement at all",
                "Because every language shares one single universal standard library"
            ],
            "answer": 1,
            "why": "socket.socket(...) maps closely onto the operating system's own networking API, so the concepts — not just Python's syntax — carry over to any language built on the same OS primitives.",
            "detail": "This is the point of thinking of the stdlib as a thin wrapper: you are learning the underlying OS concept, the socket lifecycle, through Python's forgiving skin, not a Python-only abstraction invented from scratch. The concepts absolutely do carry across languages — that's precisely why this transfers. socket is not pure Python; it calls directly into the operating system's real networking stack. And there is no single shared standard library across all languages — what's actually shared is the OS-level primitive that each language's own library wraps."
        },
        {
            "q": "In this threaded echo server, what does the main thread do while a specific client connection is being handled?",
            "code": "import socket, threading\n\ndef handle(conn):\n    with conn:\n        while True:\n            data = conn.recv(1024)\n            if not data:\n                break\n            conn.sendall(data)\n\nsrv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nsrv.bind(('0.0.0.0', 5050))\nsrv.listen()\nwhile True:\n    conn, addr = srv.accept()\n    threading.Thread(target=handle, args=(conn,), daemon=True).start()",
            "options": [
                "It blocks inside handle() until that specific client disconnects",
                "It crashes, because only one thread can use a socket at a time",
                "It immediately loops back to accept(), ready for the next client, while the new thread handles the current one independently",
                "It waits for every previously started handler thread to finish before accepting a new connection"
            ],
            "answer": 2,
            "why": "accept() runs in the main thread's own loop, and each accepted connection is handed off to a brand-new thread, freeing the main thread to call accept() again immediately.",
            "detail": "This is the classic thread-per-connection server shape: the main thread's only job is looping on accept(), while every connection gets its own dedicated thread running handle(). The main thread never enters handle() itself, so it cannot block inside it. Nothing here causes a crash — different threads using different socket objects for different connections is exactly the intended, safe pattern. And daemon threads run independently of one another; the main loop does not wait for any of them to finish before accepting the next connection."
        },
        {
            "q": "Two threads both run `counter += 1` on a shared module-level counter, a million times each, with no lock anywhere. The final value is consistently less than two million. Why?",
            "code": "",
            "options": [
                "Python ints have a maximum value, and counter silently wrapped around",
                "+= is atomic in Python, so this should be impossible — the bug must be a typo elsewhere",
                "The GIL prevents this from ever happening; the real bug must be in how counter is printed",
                "counter += 1 is really a read, an add, and a write as separate steps, and the GIL can switch threads between any of them, so both threads can read the same stale value before either writes back"
            ],
            "answer": 3,
            "why": "A read-modify-write like += 1 is not one atomic bytecode operation; a thread switch between its steps can cause two threads to both read the same old value and lose an increment.",
            "detail": "The fix is wrapping the read-modify-write in a threading.Lock, so the three steps complete as one uninterrupted unit for whichever thread holds the lock. Python ints have no fixed maximum and never silently wrap around. += is convenient syntax, not a guaranteed-atomic operation — the GIL only guarantees that individual bytecode instructions aren't interrupted mid-instruction, not that a multi-instruction sequence like this one is safe from interleaving. And the GIL being present does not prevent this particular race at all; it only prevents corruption within a single bytecode instruction, which is a much narrower guarantee than protecting this whole three-step sequence."
        },
        {
            "q": "A code review flags `hashlib.sha256(password.encode()).hexdigest()` being used to store user passwords. What's the core problem, even though SHA-256 itself is a legitimate, secure hash function?",
            "code": "",
            "options": [
                "SHA-256 is deliberately fast, which is exactly the wrong property for a password hash — it lets an attacker with a stolen hash database try billions of guesses per second",
                "SHA-256 doesn't produce a fixed-length output, making it unsuitable for storage",
                "SHA-256 is deprecated and no longer available in Python's hashlib",
                "The .hexdigest() call is the mistake; storing raw bytes instead would fix the problem"
            ],
            "answer": 0,
            "why": "A password hash needs to be deliberately slow and salted; SHA-256's speed, a virtue for file-integrity checks, becomes a liability the moment it's used for password storage.",
            "detail": "The professional fix is a purpose-built slow algorithm — bcrypt, scrypt, or PBKDF2 via hashlib.pbkdf2_hmac with a high iteration count — which costs meaningful CPU time per guess and typically salts automatically. SHA-256 does produce a fixed-length digest regardless of input size, so output length isn't the issue. SHA-256 remains fully available and secure as a general-purpose hash in hashlib to this day. And switching from hexdigest() to raw bytes only changes the encoding of the output, not the fundamental speed problem that makes it unsuitable for passwords."
        },
        {
            "q": "A developer 'fixes' a potential SQL injection by writing name.replace(chr(39), chr(39)+chr(39)) to escape single quotes before building an f-string query, instead of using a parameterized query. Why is this still considered unsafe compared to execute(sql, (name,))?",
            "code": "",
            "options": [
                "It isn't unsafe — manual escaping is exactly what parameterization does internally, just spelled out by hand",
                "Hand-rolled escaping is easy to get wrong or incomplete across different contexts, encodings, and quoting rules, while parameterization sends the value through a channel the engine never parses as SQL at all",
                "str.replace() doesn't exist in Python, so this code wouldn't run",
                "This only matters for numeric fields, never for text fields like name"
            ],
            "answer": 1,
            "why": "Manual escaping tries to out-guess every way user input could be interpreted as SQL syntax, while parameterized queries sidestep the problem entirely by never parsing the value as code in the first place.",
            "detail": "This is why parameterized queries are the rule with no exceptions, rather than 'parameterize unless you've carefully escaped instead' — escaping approaches have a long history of being subtly incomplete, missing alternate quote characters, encoding tricks, or database-specific syntax, in ways a protocol-level separation of code and data avoids by construction. Parameterization is not simply automated escaping under the hood in most drivers — the value is typically sent as a genuinely separate parameter, never concatenated into the SQL text at all. str.replace is an ordinary, always-available string method. And injection risk applies to any value interpolated into SQL text, not only numeric-looking ones."
        }
    ],
    "py-4": [
        {
            "q": "What does calling gen.send(5) do, as opposed to next(gen), when gen is already paused at an `x = yield` expression?",
            "code": "",
            "options": [
                "It's identical to next(gen); the argument passed to send is simply ignored",
                "It restarts the generator from the very beginning with x set to 5",
                "It resumes the generator and makes 5 the value the paused yield expression evaluates to, assigning it to x",
                "It raises TypeError, since generators can only ever be resumed with next()"
            ],
            "answer": 2,
            "why": "send(value) resumes a suspended generator frame and delivers value as the result of the yield expression it's paused on, making the generator a genuine two-way channel rather than a one-way producer.",
            "detail": "This differs from next(gen), which behaves like send(None) — it resumes the generator, but the paused yield expression then evaluates to None rather than to a value you chose. A generator cannot be restarted from the beginning at all; it represents a single, one-way journey through its body, so send() cannot rewind it. And send() is a completely ordinary, always-available generator method — calling it never raises TypeError by itself."
        },
        {
            "q": "What gets printed, and in what order?",
            "code": "from contextlib import contextmanager\n\n@contextmanager\ndef timer(label):\n    print('start')\n    try:\n        yield 'handle'\n    finally:\n        print('end')\n\nwith timer('x') as h:\n    print('inside', h)",
            "options": [
                "inside handle / start / end",
                "start / end / inside handle",
                "Only 'inside handle' prints — start and end never run",
                "start / inside handle / end"
            ],
            "answer": 3,
            "why": "Code before the yield runs as __enter__ (printing start), the yielded value binds to h, the with block's body runs next, and code after the yield runs as __exit__ once the block finishes (printing end).",
            "detail": "The generator runs up to `yield 'handle'` first, printing start — that's when the with block's body begins, with h bound to 'handle'. Only once the body finishes does the generator resume past the yield, running the finally clause and printing end last. Printing the block's body before start would require the with statement to run the block before entering it, which is backwards from how context managers work. Printing end before the block's body has even executed is similarly out of order. And nothing here suppresses start or end — both are guaranteed to run as the normal entry and exit of this context manager."
        },
        {
            "q": "Predict the output.",
            "code": "def counter():\n    for i in range(3):\n        yield i\n\ng = counter()\nfirst_pass = list(g)\nsecond_pass = list(g)\nprint(first_pass, second_pass)",
            "options": [
                "[0, 1, 2] []",
                "[0, 1, 2] [0, 1, 2]",
                "[] [0, 1, 2]",
                "Raises StopIteration, uncaught, on the second list() call"
            ],
            "answer": 0,
            "why": "A generator is single-pass; once list() has fully consumed it, calling list() again on that same, already-exhausted generator object produces nothing.",
            "detail": "g represents one journey through the data, already completed by the first list(g) call, so the second call immediately hits StopIteration on its very first internal next() and returns an empty list — it does not restart from the beginning. Getting the full sequence twice would require calling counter() again to get a genuinely fresh generator object, which this code never does. Getting nothing on the first pass and everything on the second reverses what actually happens, since the generator hasn't been touched yet on the first call. And list() itself catches StopIteration internally as part of the iteration protocol, so it never escapes as an uncaught exception here."
        },
        {
            "q": "What happens when this code runs?",
            "code": "class Guard:\n    def __enter__(self):\n        return self\n    def __exit__(self, exc_type, exc_val, exc_tb):\n        if exc_type is not None:\n            print('logged:', exc_val)\n        return True\n\nwith Guard():\n    raise ValueError('boom')\nprint('after the with block')",
            "options": [
                "The ValueError propagates normally after being logged, and 'after the with block' never prints",
                "'logged: boom' prints, the ValueError is suppressed entirely, and 'after the with block' prints normally",
                "It raises a TypeError because __exit__ has the wrong signature",
                "Nothing prints, because __enter__ doesn't return anything usable"
            ],
            "answer": 1,
            "why": "__exit__ returning True tells the with statement to swallow the exception rather than let it propagate, so execution continues right after the with block as if nothing had gone wrong.",
            "detail": "This is exactly the failure mode where returning True unconditionally for any exception silently swallows real errors that the caller of this code never learns about — logging it is not the same as re-raising it. The signature (self, exc_type, exc_val, exc_tb) is the correct, required one for __exit__, so no TypeError occurs. And __enter__ returning self here is a perfectly usable value, even though this particular with statement doesn't bother to bind it with `as`."
        },
        {
            "q": "A generator function opens a file before its first yield and closes it in a finally block placed after the loop. A caller does `next(stream_records(path))` exactly once and then lets the returned generator go out of scope shortly after, without calling close(). What's the risk?",
            "code": "",
            "options": [
                "None — Python always closes the file the instant next() returns",
                "The file is guaranteed to stay open for the entire remaining life of the process",
                "Cleanup depends on the generator eventually being closed — via garbage collection reaching it, or an explicit close() — so the file's closure timing is not guaranteed the way a `with` block's would be",
                "This code cannot compile, since a generator cannot contain a try/finally wrapped around a yield"
            ],
            "answer": 2,
            "why": "Only when the generator is actually closed, whether explicitly or by garbage collection eventually reaching it, does its finally clause run and release the file — an abandoned, unfinished generator's cleanup timing is not guaranteed.",
            "detail": "This is exactly the leaky-generator failure mode: the file closes only once something drives the generator to completion or calls close() on it (which raises GeneratorExit at the paused point, triggering the finally clause) — relying on that happening eventually via reference counting is very different from a deterministic, guaranteed release. Python does not close the file the instant next() returns, since the generator is still paused mid-function at that point, not finished. It's also not guaranteed to stay open forever — it's simply undetermined exactly when it closes. And a try/finally wrapped around a yield inside a generator function is completely valid, ordinary Python that compiles and runs fine."
        },
        {
            "q": "Before async/await existed as dedicated syntax, early asyncio code implemented coroutines using @asyncio.coroutine-decorated generator functions with yield from. Why was that possible at all?",
            "code": "",
            "options": [
                "It wasn't really possible — those old code examples never actually worked in practice",
                "yield from is unrelated to coroutines; it was only ever meant for delegating to sub-iterators",
                "Generators and coroutines share nothing in common; the old syntax was a complete hack with no underlying connection",
                "A generator's suspend-and-resume-a-frame mechanism, driven by the same send/throw/close protocol this lesson covers, is structurally what async/await was later built on top of"
            ],
            "answer": 3,
            "why": "async/await compiles into something structurally close to a generator, reusing the exact suspend-and-resume machinery this lesson describes rather than inventing an unrelated mechanism.",
            "detail": "This is why the old yield-from-based coroutine style genuinely worked in production for years before dedicated async/await syntax replaced it with cleaner keywords — it wasn't a hack layered on top of an unrelated feature, it was a direct, working use of the same frame-suspension mechanism. yield from does support delegating to sub-generators, but that isn't its only relevant property here — it also propagates send/throw/close through to the delegated generator, exactly the plumbing coroutines needed. And dismissing the connection between generators and coroutines misses the documented, real history of how asyncio evolved from exactly this mechanism."
        }
    ],
    "py-5": [
        {
            "q": "An exception is raised deep inside function C, called by B, called by A. A has a try/except around its call to B; B has its own try/finally (no except at all) around its call to C. What runs, and in what order, before A's except block executes?",
            "code": "",
            "options": [
                "B's finally block runs first, as the exception unwinds past it, then A's except block runs",
                "A's except block runs immediately; B's finally never runs because B has no except",
                "B's finally block never runs, since it belongs to a different function than the one that raised",
                "The program crashes immediately, since B doesn't catch the exception"
            ],
            "answer": 0,
            "why": "Every finally block the exception passes through on its way up the call stack runs, regardless of whether that frame has a matching except — only the search for a HANDLER skips over B.",
            "detail": "The exception unwinds from C into B, where there's no except to catch it but there is a finally, which runs unconditionally as the unwinding continues, and only then does the search reach A's except, which finally matches and handles it. A finally block is not tied to having an except in the same try statement — the two are independent, so 'no except' does not mean 'skip finally too.' And 'no matching except in this particular frame' is exactly why the exception keeps unwinding rather than crashing outright — it only crashes if no frame anywhere up the chain has a matching handler."
        },
        {
            "q": "Inside an except block handling a KeyError, a new ValueError is raised with a plain `raise ValueError('bad state')` — no `from` clause at all. What relationship does Python record between the two exceptions?",
            "code": "",
            "options": [
                "None at all — the KeyError is discarded the instant the new exception is raised",
                "The KeyError is recorded as the ValueError's __context__ automatically, and both tracebacks print chained together, even though this chaining was never explicitly requested",
                "Python raises a SyntaxError, since you must use `from` when raising inside an except block",
                "The KeyError becomes the ValueError's __cause__, exactly as if `from` had been written"
            ],
            "answer": 1,
            "why": "__context__ is set automatically whenever a new exception is raised while another is already being handled, whether or not you use `from`.",
            "detail": "This implicit chaining is why an unrelated bug inside an except block still shows both tracebacks connected with 'During handling of the above exception, another exception occurred.' __cause__ is different — it's set only deliberately, by writing `raise ... from original_error`, producing the 'was the direct cause of' wording instead; a plain raise with no `from` never sets __cause__. And there is no requirement to use `from` inside an except block at all — the code compiles and runs perfectly well without it, it just gets the weaker, automatic __context__ link rather than an explicit __cause__ one."
        },
        {
            "q": "What does this print?",
            "code": "class ConfigError(Exception):\n    pass\n\ntry:\n    try:\n        1 / 0\n    except ZeroDivisionError as e:\n        raise ConfigError('bad config') from e\nexcept ConfigError as ce:\n    print(type(ce).__name__, '<-', type(ce.__cause__).__name__)",
            "options": [
                "ConfigError <- ConfigError",
                "ZeroDivisionError <- ConfigError",
                "ConfigError <- ZeroDivisionError",
                "This raises an uncaught ZeroDivisionError; the outer except never runs"
            ],
            "answer": 2,
            "why": "raise ConfigError(...) from e raises a ConfigError whose __cause__ attribute is explicitly set to the original ZeroDivisionError e.",
            "detail": "The outer except ConfigError as ce catches the newly raised ConfigError, and ce.__cause__ points at exactly the exception named after `from` — the original ZeroDivisionError — so printing both type names in that order gives ConfigError <- ZeroDivisionError. The cause is the original, lower-level exception, not another ConfigError, so that pairing is wrong. It's the ConfigError that propagates outward and gets caught here, not the ZeroDivisionError, so that ordering is also wrong. And the ZeroDivisionError is fully caught by the inner except clause and never escapes uncaught at all."
        },
        {
            "q": "What does this print?",
            "code": "def risky():\n    try:\n        raise ValueError('bad')\n    finally:\n        return 'recovered'\n\nprint(risky())",
            "options": [
                "It raises ValueError: bad, uncaught",
                "It prints 'recovered', but a warning is also logged about the swallowed exception",
                "It raises a RuntimeError combining both the exception and the return value",
                "recovered — the ValueError is discarded entirely, with no error and no warning"
            ],
            "answer": 3,
            "why": "A return statement inside finally unconditionally overrides any exception propagating through the try block — the exception is silently discarded, not merely delayed.",
            "detail": "This is exactly the dangerous, little-known finally-with-return trap: there is no warning and no log message anywhere — the ValueError simply never happens as far as any caller of risky() can tell, and the function returns 'recovered' as if the try block had succeeded normally. Python does not raise the ValueError afterward, since finally's return has already replaced it. Python also does not emit any automatic warning about this — it's a real, silent, documented behavior. And nothing combines the exception and the return value into any kind of compound error; the return simply wins outright."
        },
        {
            "q": "An authorization check looks like: try: allowed = check_permissions(user, resource) / except Exception: allowed = True. A security review flags this immediately. What's the core problem?",
            "code": "",
            "options": [
                "It fails OPEN — any unexpected bug or edge case inside check_permissions silently grants access instead of denying it",
                "except Exception should be a bare except: instead, so it also catches KeyboardInterrupt",
                "check_permissions should never be wrapped in a try/except at all",
                "This code has a syntax error, since except blocks cannot assign to a variable like allowed"
            ],
            "answer": 0,
            "why": "Defaulting to allowed = True inside the except means any exception at all — a bug, a malformed input, an unrelated failure — accidentally grants access rather than denying it.",
            "detail": "The fail-secure fix is the opposite default, allowed = False in the except, so any unexpected failure denies access rather than granting it, since a permission check should never fail open. Widening this to a bare except: would make the problem worse, not better, by also swallowing KeyboardInterrupt and SystemExit. Wrapping check_permissions in a try/except isn't inherently wrong — handling unexpected exceptions from it is reasonable — the actual bug is entirely in which value the except block defaults to. And assigning to a plain variable inside an except block is completely ordinary, valid Python with no syntax error involved."
        },
        {
            "q": "A web app's error handler catches every unhandled exception and returns the full Python traceback as the HTTP response body, 'to make debugging easier.' Beyond looking unprofessional, what's the concrete security risk?",
            "code": "",
            "options": [
                "None — tracebacks only contain generic Python syntax, never anything specific to this particular application",
                "It discloses real, specific information an attacker can use directly: file system paths, internal module and function names, sometimes library versions with known vulnerabilities",
                "Tracebacks are encrypted by default, so this is actually safe as long as HTTPS is used",
                "This only matters if the attacker already has valid login credentials"
            ],
            "answer": 1,
            "why": "A raw traceback reveals real, application-specific detail, paths, internal names, versions, that helps an attacker fingerprint and target the exact stack in use, not generic language trivia.",
            "detail": "This is precisely why production deployments should catch broadly at the outermost boundary, show a generic message to the client, and log the real detail somewhere only the operators can see. Tracebacks are full of application-specific detail, not generic boilerplate, so nothing about them is inherently safe to expose. HTTPS protects data in transit between client and server; it does nothing to change what information the response body itself contains, so it does not make disclosing a traceback safe. And this risk applies to any attacker who can trigger an error at all, authenticated or not — unauthenticated attackers probing for information are often exactly who benefits most from a leaked traceback."
        }
    ],
    "py-6": [
        {
            "q": "A junior dev writes `assert user.is_authenticated, 'must be logged in'` inside a request handler as the ONLY check gating access to sensitive data. What's the critical flaw, independent of whether the logic itself is correct?",
            "code": "",
            "options": [
                "assert statements can only compare numbers, never object attributes",
                "assert always raises AssertionError, even when the condition given to it is True",
                "Running Python with the -O flag strips every assert statement out of the compiled bytecode entirely, silently turning this security check into a no-op",
                "assert requires importing a special module before it can be used on objects"
            ],
            "answer": 2,
            "why": "Python compiles assert as a check guarded by __debug__, and the -O flag sets __debug__ to False, causing the compiler to remove every assert statement, expression and all, from the compiled bytecode.",
            "detail": "This is a real, documented consequence, not a theoretical edge case: asserts are for catching your OWN bugs during development, never for gatekeeping real users or real data, which belongs in an explicit if statement raising a genuine exception regardless of any optimization flag. assert works perfectly well on any truthy or falsy expression, including object attributes, not just numeric comparisons. assert only raises when its condition is falsy, never unconditionally. And assert is a language keyword requiring no special import at all to use on any kind of value."
        },
        {
            "q": "Five asserts for a clamp(value, low, high) function all use values comfortably in the middle of the range, just with different numbers each time. What's the real weakness of this test set?",
            "code": "",
            "options": [
                "Five asserts is too many for one function; a single assert is always sufficient",
                "assert cannot legally be called more than once inside the same function",
                "The numbers used should have been generated randomly instead of hand-picked",
                "All five exercise the exact same code path — value already inside the range — so a broken clamp specifically at the boundaries would sail through completely undetected"
            ],
            "answer": 3,
            "why": "Partitioning the input space into meaningfully different regions matters more than the raw count of asserts — five tests of the same region catch the same one bug, or none at all.",
            "detail": "The actual skill is identifying genuinely different regions first, value below low, value above high, value exactly equal to low or high, an ordinary in-range value, and writing one assert per region, rather than adding more assertions that all happen to land in the same, already-covered territory. There's no rule that a single assert is always enough — the right number depends on how many meaningfully distinct cases actually exist. Nothing prevents calling assert many times within one function or file. And hand-picked boundary values are usually MORE useful here than random ones, precisely because you can deliberately target the exact edges a random generator might easily miss."
        },
        {
            "q": "What happens when this runs?",
            "code": "total = 0.1 + 0.1 + 0.1\nassert total == 0.3, f'got {total}'",
            "options": [
                "AssertionError, with a message showing something like 'got 0.30000000000000004'",
                "It passes silently, since 0.1 + 0.1 + 0.1 equals 0.3 exactly",
                "TypeError, because you cannot use == on float values",
                "It passes, but Python prints a floating-point rounding warning first"
            ],
            "answer": 0,
            "why": "0.1 has no exact binary floating-point representation, so the accumulated sum is very slightly off from the literal 0.3, and == demands exact bit-for-bit equality.",
            "detail": "This is the canonical floating-point-assert trap; the fix is never comparing floats with ==, and instead checking the difference is within a small tolerance, such as abs(total - 0.3) < 1e-9, or using math.isclose. Floats fully support == in Python — the operator itself works fine, it's simply that these particular values genuinely aren't bit-for-bit equal. And Python does not print any automatic warning for this at all; the assertion simply fails with whatever message string you provided, nothing more."
        },
        {
            "q": "What happens when both of these run, in this order?",
            "code": "shared_cache = {}\n\ndef test_first():\n    shared_cache['x'] = 1\n    assert shared_cache.get('x') == 1\n\ndef test_second():\n    assert 'x' not in shared_cache\n\ntest_first()\ntest_second()",
            "options": [
                "Both pass — they test unrelated, independent things",
                "test_first() passes, but test_second() fails, because test_first already inserted 'x' into the shared_cache dict that test_second also reads",
                "test_second() raises NameError because shared_cache doesn't exist yet at that point",
                "Both fail, because this dict access syntax is invalid"
            ],
            "answer": 1,
            "why": "Both tests read and write the same shared, mutable module-level dict, so running them in this order leaves state behind that the second test's assertion doesn't expect.",
            "detail": "This is exactly the test-independence bug this lesson describes: test_second() would pass fine if run entirely on its own, but fails specifically because it ran after test_first() left 'x' behind in the shared dict — a bug that's notoriously confusing because neither test looks wrong when read in isolation. The two tests are not unrelated at all; they share shared_cache directly, which is exactly the problem. shared_cache is defined at module level before either function runs, so no NameError occurs. And the dict syntax used here, `in`, `.get`, and item assignment, is entirely valid, ordinary Python."
        },
        {
            "q": "A test suite has 40 hand-written asserts covering a parsing function's known edge cases. Security wants MORE confidence that the parser can't crash on malformed input. What's the professional next step, beyond simply writing even more asserts by hand?",
            "code": "",
            "options": [
                "Rewrite all 40 asserts using unittest instead of plain assert statements — that alone closes the coverage gap",
                "Add more print statements around the parser to manually observe its behavior",
                "Introduce fuzzing: generate large volumes of random or mutated inputs automatically, and assert the weaker, universal claim that the parser must never crash, hang, or corrupt memory, regardless of input",
                "Delete the 40 existing asserts, since fuzzing makes them entirely redundant"
            ],
            "answer": 2,
            "why": "Fuzzing scales the exact same edge-case mindset up mechanically, covering far more of the input space automatically than a human enumerating cases by hand ever realistically could.",
            "detail": "This is the direct connection this lesson draws to real security work: hand-written asserts are precise but limited to whatever a human thought to test, while a fuzzer explores enormous swaths of malformed, boundary, and adversarial input automatically, checking one broad invariant rather than one specific expected output per case. Switching to unittest changes test organization and reporting, not the fundamental coverage gap being described here. Print statements require a human to notice something wrong by eye; they don't systematically generate new inputs at all. And fuzzing complements hand-written asserts rather than replacing them outright — the specific, known edge cases the 40 asserts already encode remain valuable and worth keeping."
        },
        {
            "q": "What is the most accurate way to describe the relationship between 'thinking in edge cases' when testing your own stats.py, and the mindset behind real vulnerability research?",
            "code": "",
            "options": [
                "They are unrelated; vulnerability research requires entirely different skills like reverse engineering, not testing habits",
                "Vulnerability research is really about memorizing known CVEs, not about generating new edge cases",
                "Edge-case testing only matters for beginner code; mature production software no longer has this class of bug",
                "They are the same underlying habit at a different scale and intent — a vulnerability is usually a case the original developer's mental test suite never considered, and vulnerability research asks that same smallest/empty/negative/huge/wrong-typed question more completely and often adversarially"
            ],
            "answer": 3,
            "why": "A buffer overflow, integer overflow, or injection bug is, at its root, exactly the kind of untested input-space region this lesson teaches you to hunt for in your own five-line functions.",
            "detail": "The difference between testing your own code and testing someone else's authentication endpoint is scale and adversarial intent, not method — reverse engineering and other specialized skills matter for finding WHERE to apply this mindset inside unfamiliar binaries, but the mindset itself, systematically enumerating the input space and checking a claim at each boundary, is the very one this lesson builds. Vulnerability research is not fundamentally memorization-based; CVEs are the output of this process, not the process itself. And this class of bug is still very much found in mature, widely-used production software today, which is exactly why fuzzing and manual edge-case auditing remain active, valuable disciplines rather than beginner-only concerns."
        }
    ]
}
