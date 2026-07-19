# quizbank_csharp.py - additional graded checks for the csharp track.
# Merged onto each lesson's existing quiz by content.build_courses().
# Answer indices balanced across the file so the correct option isn't always first.
EXTRA_QUIZ = {
    "cs-1": [
        {
            "q": "In C#, what is the practical difference between a `struct` and a `class`?",
            "code": "",
            "options": [
                "struct is a value type (copied on assignment); class is a reference type (shared)",
                "There is no difference; struct is just an alias for class",
                "struct can have methods but a class cannot",
                "class is a value type; struct is a reference type"
            ],
            "answer": 0,
            "why": "structs are value types stored/copied by value; classes are reference types accessed through a reference.",
            "detail": "Assigning a struct copies all its fields; assigning a class copies only the reference, so both names point at one object. This is exactly the Java distinction between primitives and objects, except C# lets YOU define value types. Saying there is no difference, or that only classes have methods, ignores the copy-vs-share semantics that cause the most surprising bugs. The last option reverses the two."
        },
        {
            "q": "A Java developer writes `if (a == b)` to compare two string objects in C#. What actually happens?",
            "code": "string a = \"hi\";\nstring b = \"h\" + \"i\";\nConsole.WriteLine(a == b);",
            "options": [
                "It compares references and prints False",
                "It compares VALUES and prints True, because C# overloads == for string",
                "It throws a compile error; you must use .Equals",
                "It prints True only by luck of string interning"
            ],
            "answer": 1,
            "why": "C# overloads == for string to compare contents, unlike Java where == on strings compares references.",
            "detail": "This is a genuine Java-to-C# trap in the opposite direction: in Java `==` on strings is reference comparison and burns beginners, but C# defines == on string to compare characters, so it prints True reliably. It is not luck-of-interning (that would make it fragile) and it is not a compile error. Knowing which languages overload == for strings prevents porting bugs in both directions."
        },
        {
            "q": "What does the `var` keyword do in `var list = new List<int>();`?",
            "code": "",
            "options": [
                "Makes the variable dynamically typed like JavaScript's var",
                "Creates a variable whose type can change at runtime",
                "Infers the static type at compile time (here List<int>) — it is NOT dynamic typing",
                "Is a syntax error outside of a loop"
            ],
            "answer": 2,
            "why": "var is compile-time type inference; the variable has a fixed static type, just written more briefly.",
            "detail": "The compiler deduces List<int> from the initializer and the variable is exactly as statically typed as if you had spelled it out. It is emphatically not JavaScript's dynamic var or Python's untyped names — the type cannot change. C# does have `dynamic` for runtime typing, which is a different keyword. Confusing var with dynamic leads people to expect flexibility that does not exist."
        },
        {
            "q": "What prints?",
            "code": "int? x = null;\nint y = x ?? -1;\nConsole.WriteLine(y);",
            "options": [
                "0",
                "null",
                "A NullReferenceException",
                "-1"
            ],
            "answer": 3,
            "why": "int? is a nullable value type; the ?? null-coalescing operator yields the right side when the left is null.",
            "detail": "`int?` (Nullable<int>) can hold null, and `??` returns its right operand (-1) when the left is null, so y is -1. It does not default to 0 (that would ignore ??), y is a non-nullable int so it cannot be null, and no exception occurs because ?? handles the null explicitly. Java's rough equivalent is Optional or a manual null check; C#'s ?? is the concise idiom."
        },
        {
            "q": "You port Java code that used `final int MAX = 10;`. What is the C# equivalent for a true compile-time constant?",
            "code": "",
            "options": [
                "const int MAX = 10;",
                "final int MAX = 10;",
                "readonly int MAX = 10; (as a local variable)",
                "static int MAX = 10;"
            ],
            "answer": 0,
            "why": "C# uses const for compile-time constants; readonly is for run-time-initialized fields, and final is not a C# keyword.",
            "detail": "`const` is the direct analogue of Java's `final` for compile-time constants. `final` itself does not exist in C#. `readonly` is close but different — it is a field set once at construction time (run time), not a compile-time constant, and it cannot be a plain local. `static` controls sharing across instances, not immutability. Reaching for final out of Java habit is a compile error; const is the fix."
        },
        {
            "q": "What is the output, and why does it differ from the naive expectation?",
            "code": "object o = 5;\nint n = (int)o;\nConsole.WriteLine(n);\ndouble d = (double)o;   // does this line work?",
            "options": [
                "Prints 5, then prints 5.0 with no error",
                "Prints 5, then the last line THROWS InvalidCastException at runtime",
                "Fails to compile on the (double)o line",
                "Prints 5, then the cast silently yields 0.0"
            ],
            "answer": 1,
            "why": "Unboxing must match the boxed type exactly; a boxed int can be unboxed to int but not directly cast to double.",
            "detail": "Boxing put an int into the object; unboxing requires the exact type, so `(int)o` works but `(double)o` throws InvalidCastException at run time even though int-to-double normally widens freely. It compiles (the compiler allows object-to-double casts), which is exactly the trap — the error is deferred to run time. To get a double you must unbox to int first, then convert: `(double)(int)o`. This boxing subtlety has no Java analogue since Java autoboxing follows different rules."
        }
    ],
    "cs-2": [
        {
            "q": "Why is LINQ said to use DEFERRED execution?",
            "code": "var q = numbers.Where(n => n > 5);",
            "options": [
                "It runs immediately and caches the result in q",
                "It runs on a background thread automatically",
                "The query is not run until you iterate it (foreach, ToList, Count, etc.)",
                "It only defers when the source is a database"
            ],
            "answer": 2,
            "why": "A LINQ query describes a computation; it executes lazily when enumerated, not when defined.",
            "detail": "`Where` returns an IEnumerable that yields results on demand, so nothing happens until you foreach it or force it with ToList/Count/ToArray. It does NOT run and cache at definition — that is the whole point and the source of a classic bug: if you change `numbers` after defining q but before iterating, you see the new values. It is not automatically threaded, and deferral applies to in-memory sequences too, not only databases."
        },
        {
            "q": "What is the danger in this code?",
            "code": "var evens = list.Where(x => x % 2 == 0);\nlist.Add(4);\nforeach (var e in evens) Console.Write(e);",
            "options": [
                "evens was fixed when defined, so the 4 is not included",
                "It throws because you modified list after querying",
                "The 4 is included only if list was a List<int>",
                "evens reflects the Add because it executes at the foreach, after 4 was added"
            ],
            "answer": 3,
            "why": "Deferred execution means the Where runs during the foreach, over the current contents of list including the added 4.",
            "detail": "Because LINQ is lazy, the filter runs when you enumerate — by then list contains 4, so it appears. Assuming the query froze at definition is the deferred-execution misconception. It does not throw here (that happens if you modify a collection DURING its own foreach, which is different). The behavior is not type-dependent in this way. To snapshot the results at definition time, call ToList() immediately."
        },
        {
            "q": "Which collection gives O(1) average lookup by key?",
            "code": "",
            "options": [
                "Dictionary<TKey, TValue>",
                "List<T>",
                "Queue<T>",
                "SortedList<TKey, TValue>"
            ],
            "answer": 0,
            "why": "Dictionary is the hash table with average O(1) key lookup; List is O(n), SortedList is O(log n).",
            "detail": "Dictionary is C#'s hash map (Java's HashMap), giving amortized O(1) lookup, insert, and remove by key. List requires a linear scan to find by value, O(n). Queue is FIFO with no keyed lookup. SortedList keeps keys ordered and does O(log n) binary-search lookup, trading speed for order. Choosing List and searching it is the commonest performance mistake when a Dictionary was the right tool."
        },
        {
            "q": "What does this produce?",
            "code": "var r = new[]{1,2,3,4}.Where(x => x>1).Select(x => x*x).ToList();\nConsole.WriteLine(string.Join(\",\", r));",
            "options": [
                "1,4,9,16",
                "4,9,16",
                "2,3,4",
                "9,16"
            ],
            "answer": 1,
            "why": "Where keeps 2,3,4 (x>1), then Select squares each to 4,9,16; ToList forces evaluation.",
            "detail": "The pipeline filters out 1, leaving 2,3,4, then squares them to 4,9,16. Including 1 (option b) forgets the Where. 2,3,4 forgets the Select. 9,16 wrongly drops the 2. The chained-then-materialized pattern (Where/Select/ToList) is the everyday LINQ shape, and reading it correctly means applying each stage in order to the surviving elements."
        },
        {
            "q": "You call `.First()` on a filtered sequence that turns out to be empty. What happens?",
            "code": "var x = list.Where(n => n > 100).First();",
            "options": [
                "It returns null",
                "It returns 0",
                "It throws InvalidOperationException (\"Sequence contains no elements\")",
                "It returns default(T) silently"
            ],
            "answer": 2,
            "why": "First throws on an empty sequence; FirstOrDefault is the variant that returns default instead.",
            "detail": "`First()` demands at least one element and throws if there are none — a common runtime crash when a filter matches nothing. To get a safe default (null for reference types, 0 for int) use `FirstOrDefault()`. Assuming First returns null or 0 is exactly the mistake; those are FirstOrDefault's behavior. Knowing the OrDefault family (FirstOrDefault, SingleOrDefault) is essential for robust LINQ."
        },
        {
            "q": "What is the subtle difference between `Single()` and `First()` on a sequence with several matches?",
            "code": "var a = list.Where(x => x > 0).First();\nvar b = list.Where(x => x > 0).Single();",
            "options": [
                "They are identical",
                "Single returns the last match; First returns the first",
                "First throws on multiple matches; Single does not",
                "First returns the first match; Single THROWS if there is more than one match"
            ],
            "answer": 3,
            "why": "Single asserts exactly one element exists and throws on zero OR more than one; First just takes the first.",
            "detail": "`Single` encodes the expectation that precisely one element matches — it throws if there are two or more (and if there are none). `First` simply returns the earliest and ignores the rest. They are not identical, and Single does not return the last. Using Single where duplicates are possible is a deliberate assertion that will surface data problems as exceptions, which is sometimes exactly what you want and sometimes an accidental crash."
        }
    ],
    "cs-3": [
        {
            "q": "What can an abstract class do that an interface (classically) could not?",
            "code": "",
            "options": [
                "Provide fields and full method implementations with state, not just a contract",
                "Be implemented by multiple classes",
                "Declare method signatures",
                "Be used as a variable's type"
            ],
            "answer": 0,
            "why": "An abstract class can hold fields and concrete implementations/state; an interface is (classically) only a contract.",
            "detail": "Abstract classes can carry instance fields, constructors, and fully implemented methods that subclasses inherit — real shared state and behavior. Interfaces (before default interface methods) only declared signatures. Both can be implemented/inherited by many classes and used as variable types, so those options do not distinguish them. The single-base-class limit vs many-interfaces is the other half of the tradeoff, and it is why you pick an interface for capability and an abstract class for shared implementation."
        },
        {
            "q": "What does `IDisposable` plus `using` accomplish that a C++ destructor also does, but a C# finalizer does NOT reliably do?",
            "code": "using (var f = File.OpenRead(path)) { /* ... */ }",
            "options": [
                "Cleanup that never runs",
                "Deterministic cleanup at a known point (end of the using block)",
                "Cleanup only when the garbage collector decides, at an unpredictable time",
                "Automatic memory freeing of the object itself"
            ],
            "answer": 1,
            "why": "using calls Dispose() deterministically at block end; a finalizer runs whenever the GC gets around to it.",
            "detail": "`using` guarantees Dispose() is called the moment control leaves the block, even on exception — deterministic, like a C++ destructor at scope exit. A C# FINALIZER (~ClassName) runs nondeterministically during garbage collection, so it is unreliable for timely release of files or sockets. This is the key Java/C# lesson: use IDisposable+using for resources, not finalizers. Dispose does not free the object's memory (the GC does that); it releases the unmanaged resource the object held."
        },
        {
            "q": "What is wrong here?",
            "code": "interface IShape { double Area(); }\nclass Circle : IShape {\n    double Area() => 3.14 * r * r;\n}",
            "options": [
                "Interfaces cannot declare methods",
                "Circle must be abstract",
                "The interface method must be public; an implicit interface implementation cannot be private",
                "Area must be marked override"
            ],
            "answer": 2,
            "why": "An implicitly-implemented interface member must be public; C# does not let it default to private.",
            "detail": "Interface members are implicitly public, and the implementing method must match that accessibility, so `Area` needs `public`. Interfaces certainly can declare methods (that is their purpose). Circle need not be abstract since it implements the one member. And interface implementations do not use `override` (that keyword is for virtual base-class methods) — this is a subtle C# distinction from overriding an abstract class method, which DOES use override."
        },
        {
            "q": "A class implements two interfaces that both declare a method `Run()`. How does C# let you give them different implementations?",
            "code": "",
            "options": [
                "It is impossible; the names collide fatally",
                "You must rename one method",
                "C# merges them into a single implementation automatically",
                "Explicit interface implementation: void IA.Run() { } and void IB.Run() { }"
            ],
            "answer": 3,
            "why": "Explicit interface implementation qualifies the method with the interface name, allowing distinct bodies.",
            "detail": "Writing `void IA.Run()` and `void IB.Run()` gives each interface its own implementation, selected by which interface reference you call through. It is not impossible and you need not rename anything. C# does not silently merge them — if you provide one implicit `public void Run()` it satisfies both, but explicit implementation is how you separate them. This is C#'s answer to the diamond-style naming clash that other languages handle differently."
        },
        {
            "q": "What does `sealed` do to a class or method?",
            "code": "sealed class Config { }",
            "options": [
                "Prevents further inheritance (class) or further overriding (method)",
                "Makes all its members private",
                "Prevents the class from being instantiated",
                "Marks it for garbage collection"
            ],
            "answer": 0,
            "why": "sealed blocks inheritance of a class or overriding of a virtual method further down the hierarchy.",
            "detail": "A sealed class cannot be subclassed; a sealed override cannot be overridden again by deeper subclasses. It does not change member accessibility, does not prevent instantiation (you can still `new Config()`), and has nothing to do with garbage collection. Java's `final` on a class is the analogue. Sealing is used for correctness (locking behavior) and sometimes performance (the JIT can devirtualize calls)."
        },
        {
            "q": "Why might this finalizer-based design leak the file handle for a long time?",
            "code": "class Log {\n    FileStream fs = File.OpenWrite(\"log.txt\");\n    ~Log() { fs.Dispose(); }\n}",
            "options": [
                "Finalizers run immediately when the last reference drops",
                "The handle is only released when the GC finalizes the object, which may be much later",
                "FileStream does not need disposing",
                "The finalizer runs before the object is used"
            ],
            "answer": 1,
            "why": "Relying on the finalizer defers cleanup to a nondeterministic GC pass, holding the OS handle far longer than needed.",
            "detail": "Finalizers run whenever the garbage collector chooses, potentially seconds or minutes after the object is unreachable — meanwhile the file handle stays open, risking sharing conflicts and resource exhaustion. Finalizers do NOT run promptly when references drop (that is a reference-counting model like C++/Python, not .NET's GC). FileStream absolutely needs disposing. The correct design is to implement IDisposable and use `using`, releasing the handle deterministically."
        }
    ],
    "cs-4": [
        {
            "q": "What does `await` actually do to the method it appears in?",
            "code": "async Task<int> GetAsync() {\n    var data = await FetchAsync();\n    return data.Length;\n}",
            "options": [
                "Blocks the current thread until the task finishes",
                "Spawns a new thread to run FetchAsync",
                "Returns control to the caller until the awaited task completes, then resumes after it",
                "Runs FetchAsync synchronously"
            ],
            "answer": 2,
            "why": "await yields control to the caller and schedules the rest of the method to resume when the task completes.",
            "detail": "The compiler rewrites the async method into a state machine: at the await it returns a Task to the caller and registers the remainder as a continuation that runs when FetchAsync finishes. It does NOT block the thread (that would defeat async), does not necessarily start a new thread (async is about not blocking, not about threads), and does not run synchronously. Believing await blocks is the deepest async misconception and leads to deadlocks when people mix it with .Result."
        },
        {
            "q": "A delegate in C# is best described as what, in Java terms?",
            "code": "Func<int,int> square = x => x * x;",
            "options": [
                "A subclass of Object",
                "A dynamically typed variable",
                "A thread",
                "A type-safe reference to a method — like a functional interface / method reference"
            ],
            "answer": 3,
            "why": "A delegate is a type-safe function pointer; Func/Action are built-in delegate types, akin to Java functional interfaces.",
            "detail": "A delegate holds a reference to a method (or lambda) with a specific signature, invoked like a method — the closest Java analogue is a functional interface plus a method reference or lambda. It is not merely an Object subclass in any meaningful sense, not dynamically typed (the signature is fixed and checked), and not a thread. Func<int,int> means 'takes an int, returns an int'; Action is the void-returning family. Delegates underpin events and LINQ."
        },
        {
            "q": "What is the risk in this event handler pattern?",
            "code": "publisher.SomeEvent += Handler;\n// ... object lives on, never does:\n// publisher.SomeEvent -= Handler;",
            "options": [
                "The subscription keeps the subscriber alive, a common managed memory leak",
                "Events cannot be unsubscribed once added",
                "+= throws if the event already has a handler",
                "Handler runs on a background thread"
            ],
            "answer": 0,
            "why": "An event holds a reference to the subscriber via the delegate, so failing to unsubscribe can prevent GC — a leak.",
            "detail": "The publisher's event references Handler, which references the subscribing object, so as long as the publisher lives the subscriber cannot be collected — a genuine managed-memory leak despite the GC. You CAN and should unsubscribe with -=. += does not throw on multiple handlers (it chains them). Threading is unrelated. This lapsed-listener leak is one of the few ways to leak memory in a garbage-collected language, which is why it is worth knowing."
        },
        {
            "q": "What does this print, and why?",
            "code": "async Task Main() {\n    var t = Task.Delay(100).ContinueWith(_ => 42);\n    Console.WriteLine(\"before\");\n    Console.WriteLine(await t);\n}",
            "options": [
                "42, then before",
                "before, then 42 — 'before' prints while the delay is pending",
                "before, then blocks forever",
                "Only 42"
            ],
            "answer": 1,
            "why": "The code after starting the task runs immediately; await only pauses at the point it is written.",
            "detail": "Starting the task does not block, so 'before' prints right away; then `await t` waits for the 100ms delay and its continuation, yielding 42. Printing 42 first would require the await to happen before the WriteLine, which it does not. It does not block forever (the task completes). Both lines print. This illustrates that async code runs synchronously up to the first await on an incomplete task."
        },
        {
            "q": "Why is `async void` discouraged except for event handlers?",
            "code": "async void DoWork() { await Task.Delay(10); throw new Exception(); }",
            "options": [
                "It runs slower than async Task",
                "It cannot use await",
                "Its exceptions cannot be caught by the caller and can crash the process",
                "The compiler rejects it"
            ],
            "answer": 2,
            "why": "An async void method returns no Task to await, so exceptions escape to the synchronization context and are uncatchable by callers.",
            "detail": "Because there is no Task, the caller cannot await it or catch its exceptions — a throw in an async void propagates to the sync context and often crashes the app. It is not inherently slower, it certainly can use await, and the compiler allows it (that is the danger). The rule: return `async Task` so callers can await and observe exceptions; reserve `async void` for event handlers whose signature forces void."
        },
        {
            "q": "What does the lambda capture here, and what prints?",
            "code": "var actions = new List<Action>();\nfor (int i = 0; i < 3; i++) actions.Add(() => Console.Write(i));\nforeach (var a in actions) a();",
            "options": [
                "3 3 3 always",
                "0 0 0",
                "A compile error about capturing a loop variable",
                "0 1 2 in modern C# — each iteration has its own i captured"
            ],
            "answer": 3,
            "why": "Since C# 5, the for-each and for loop variable is scoped per iteration, so each lambda captures its own i (0,1,2).",
            "detail": "Modern C# gives each loop iteration a fresh copy of the variable, so the three lambdas capture 0, 1, and 2 respectively. The '3 3 3' answer is the classic closure-over-shared-variable bug — it was true in very old C# and is still true in some other languages, but current C# fixed it for loop variables. It does not print 0 0 0 and it compiles fine. This is a subtle version-dependent point worth knowing when reading older code."
        }
    ],
    "cs-5": [
        {
            "q": "When is a `finally` block guaranteed to run?",
            "code": "",
            "options": [
                "Whether the try block succeeds, throws, or returns early",
                "Only if no exception was thrown",
                "Only if an exception was thrown",
                "Only if you do not return inside try"
            ],
            "answer": 0,
            "why": "finally runs on all exits from try — normal completion, exception, or an early return.",
            "detail": "The guarantee of finally is that it executes no matter how control leaves the try — success, a thrown exception (before it propagates), or a return statement. Restricting it to the no-exception or exception-only case misunderstands its purpose. And it runs even when you return inside try (the return value is computed, finally runs, then control returns). This is why finally is the classic place for cleanup, though `using` is preferred for IDisposable resources."
        },
        {
            "q": "What is poor about this catch?",
            "code": "try { Risky(); }\ncatch (Exception e) { }",
            "options": [
                "You cannot catch the base Exception type",
                "It swallows every exception silently, hiding bugs and making failures invisible",
                "catch must always rethrow",
                "It will not compile without a finally"
            ],
            "answer": 1,
            "why": "An empty catch of the base Exception hides all errors, turning failures into silent, undebuggable misbehavior.",
            "detail": "Catching Exception and doing nothing swallows everything — real bugs, out-of-memory, everything — so the program limps on in a broken state with no trace. You CAN catch the base type (that is part of the problem — it is too broad). catch need not rethrow, and finally is not required. Good practice is to catch the SPECIFIC exceptions you can handle, and at minimum log what you catch so failures are visible."
        },
        {
            "q": "What does `using (var f = File.OpenRead(path))` guarantee even if the block throws?",
            "code": "",
            "options": [
                "The file contents are cached in memory",
                "Exceptions inside the block are suppressed",
                "f.Dispose() is called, closing the file, on every exit including exceptions",
                "The file is deleted afterward"
            ],
            "answer": 2,
            "why": "using compiles to try/finally that calls Dispose(), so the stream is closed on all exits, exceptions included.",
            "detail": "The `using` statement is syntactic sugar for a try/finally whose finally calls Dispose(), so the file handle is released whether the block finishes normally or throws. It does not cache contents, does not suppress the exception (the exception still propagates after Dispose runs), and certainly does not delete the file. This deterministic release is why using is the correct pattern for files, connections, and any IDisposable."
        },
        {
            "q": "What does this catch, and what does it re-expose?",
            "code": "try { int x = int.Parse(s); }\ncatch (FormatException ex) {\n    throw new InvalidOperationException(\"bad input\", ex);\n}",
            "options": [
                "Catches all exceptions and discards the original",
                "Silently ignores the parse error",
                "Re-throws the exact same FormatException",
                "Catches a parse failure and wraps it, preserving the original as InnerException"
            ],
            "answer": 3,
            "why": "It catches the specific FormatException and throws a new exception that carries the original in InnerException.",
            "detail": "Passing `ex` as the second constructor argument sets InnerException, so the original cause is preserved for diagnostics while presenting a higher-level error. It catches only FormatException, not everything, and does not ignore or blindly rethrow the same object — it wraps. Exception wrapping with an inner exception is good practice for translating low-level failures into meaningful ones without losing the root cause (which a bare `throw new ...()` without `ex` would discard)."
        },
        {
            "q": "What is the difference between `throw;` and `throw ex;` inside a catch?",
            "code": "catch (Exception ex) {\n    // option A: throw;\n    // option B: throw ex;\n}",
            "options": [
                "throw; preserves the original stack trace; throw ex; resets it to this line",
                "They are identical",
                "throw ex; preserves the stack trace; throw; resets it",
                "throw; is a syntax error"
            ],
            "answer": 0,
            "why": "Bare `throw;` rethrows preserving the original stack trace; `throw ex;` restarts the trace from the current line.",
            "detail": "`throw;` re-raises the caught exception with its stack trace intact, so you can still see where it originated. `throw ex;` throws the same object but RESETS the stack trace to the rethrow point, destroying the original location — a common debugging headache. They are not identical, and the roles are not reversed. `throw;` is valid syntax (only legal inside a catch). Always use bare `throw;` to rethrow unless you deliberately want a fresh trace."
        },
        {
            "q": "What happens if `int.Parse` fails and you used `int.TryParse` instead?",
            "code": "bool ok = int.TryParse(s, out int n);",
            "options": [
                "TryParse throws FormatException like Parse",
                "TryParse returns false and sets n to 0 — no exception is thrown",
                "TryParse returns true and n is null",
                "It does not compile without a try/catch"
            ],
            "answer": 1,
            "why": "TryParse signals failure by returning false (and n=0) rather than throwing, avoiding exception overhead for expected bad input.",
            "detail": "The Try* pattern converts an expected failure (invalid user input) into a boolean instead of an exception, so you branch on `ok` — n is 0 on failure, not null (int cannot be null). It does not throw, which is the whole point versus Parse. No try/catch is needed. Using TryParse for input that is routinely malformed is both cleaner and faster than catching FormatException, since exceptions are costly and meant for the exceptional."
        }
    ],
    "cs-6": [
        {
            "q": "How does C# generics' handling of `List<int>` fundamentally differ from Java's `List<Integer>`?",
            "code": "",
            "options": [
                "They are implemented identically",
                "C# erases generic types at compile time like Java",
                "C# reifies generics — List<int> stores real ints with no boxing; Java erases types and boxes",
                "Java stores primitive ints directly; C# boxes them"
            ],
            "answer": 2,
            "why": "C# generics are reified (the runtime knows the real type argument); Java erases them, forcing boxing of primitives.",
            "detail": "C# keeps the type argument at run time, so List<int> is a genuine list of unboxed ints — efficient and type-known via reflection. Java ERASES generics to Object under the hood, so List<Integer> must box each int into an Integer object. The options claiming identical or erased-like-Java implementations are wrong, and the last one reverses reality — it is Java that boxes, not C#. This reification is a real performance and expressiveness advantage of C# generics."
        },
        {
            "q": "What does a generic constraint `where T : IComparable<T>` enable?",
            "code": "T Max<T>(T a, T b) where T : IComparable<T>\n    => a.CompareTo(b) > 0 ? a : b;",
            "options": [
                "Nothing; constraints are documentation only",
                "Automatic conversion of T to int",
                "Making T nullable",
                "Calling CompareTo on T, because the constraint guarantees T implements it"
            ],
            "answer": 3,
            "why": "The constraint guarantees T has IComparable<T>'s members, so the compiler permits a.CompareTo(b).",
            "detail": "Without the constraint the compiler knows nothing about T and would reject `a.CompareTo(b)`. The `where T : IComparable<T>` promises every T implements that interface, unlocking its methods with full type safety. Constraints are enforced, not mere documentation. They do not auto-convert T to int or make it nullable (that is `where T : struct`/`class` and `?`). Constraints are how generic code does more than shuffle opaque values around."
        },
        {
            "q": "What does `default(T)` yield for a generic type parameter T?",
            "code": "T x = default(T);",
            "options": [
                "null for reference types, the zero-value (0, false, etc.) for value types",
                "Always null",
                "Always 0",
                "A compile error unless T is constrained"
            ],
            "answer": 0,
            "why": "default(T) is null for reference types and the all-zero value for value types (0, false, '\\0', empty struct).",
            "detail": "`default(T)` produces the type's natural zero: null for classes, 0 for numeric structs, false for bool, and a zeroed struct for custom value types. It is not always null (that fails for int) nor always 0 (that is wrong for reference types). It compiles without any constraint — that is precisely why default(T) exists, to give generic code a valid initial value for an unknown T. Modern C# also allows the shorthand `default`."
        },
        {
            "q": "What happens when this compiles and runs?",
            "code": "var stack = new Stack<int>();\nstack.Push(1);\nobject o = stack.Pop();\nint n = (int)o;",
            "options": [
                "Pop returns object, so no boxing happens",
                "Works: Pop returns int 1, boxed into o, then unboxed back to n=1",
                "Throws because Stack<int> cannot store value types",
                "n is 0 due to a failed cast"
            ],
            "answer": 1,
            "why": "Stack<int> returns a real int from Pop; assigning it to object boxes it, and (int)o unboxes it correctly.",
            "detail": "Because generics are reified, Stack<int>.Pop returns an actual int (no boxing inside the stack). Assigning that int to `object o` boxes it, and `(int)o` unboxes to 1. Stack<int> stores value types fine — that is the benefit over a non-generic object stack. The cast succeeds because the boxed type matches. The only boxing here is the deliberate assignment to object, illustrating that generics AVOID the boxing a pre-generics object-based stack would have forced on every Push and Pop."
        },
        {
            "q": "Why does a non-generic `ArrayList` of ints perform worse than `List<int>`?",
            "code": "",
            "options": [
                "ArrayList uses a linked list internally",
                "List<int> is always multithreaded",
                "ArrayList stores object, boxing every int on add and unboxing on read",
                "ArrayList cannot resize"
            ],
            "answer": 2,
            "why": "ArrayList holds object references, so each int is boxed (heap-allocated) going in and unboxed coming out.",
            "detail": "Pre-generics collections store `object`, forcing every value type to be boxed onto the heap and unboxed on retrieval — allocation and cast overhead on every element. List<int> stores ints inline thanks to reification. ArrayList is array-backed (not a linked list) and can resize, so those options are wrong, and neither collection is inherently multithreaded. This boxing cost is the concrete performance reason generics replaced the old object-based collections."
        },
        {
            "q": "What does covariance let you do here, and why is it safe?",
            "code": "IEnumerable<string> strings = new List<string>();\nIEnumerable<object> objects = strings;",
            "options": [
                "It fails to compile; generics are never assignable across type arguments",
                "It works because arrays and generics behave identically",
                "It boxes each string",
                "Assign IEnumerable<string> to IEnumerable<object> because IEnumerable<out T> is covariant and read-only"
            ],
            "answer": 3,
            "why": "IEnumerable<out T> is declared covariant, so a sequence of strings is usable as a sequence of objects safely, since you can only read.",
            "detail": "The `out` variance annotation on IEnumerable<out T> permits assigning IEnumerable<string> to IEnumerable<object> because you can only pull items OUT (every string IS an object, so reads are safe). It does compile — variance is exactly the feature that allows this specific cross-type assignment. It is not because arrays and generics are identical (array covariance is actually unsafe and can throw at run time, unlike this). No boxing occurs since string is already a reference type. Covariance is a subtle but powerful part of C#'s type system."
        }
    ]
}
