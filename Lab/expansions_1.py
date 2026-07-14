# expansions_1.py — deep-dive expansions for Lab lessons (tracks: python, csharp, c).
# Rendered by lockin_lab.py after the lesson body. Pure data.
EXPANSIONS = {
    "python:0": {
        "title_check": "Building from a blank file",
        "sections": [
            {
                "h": "Module initialization and __name__ guard",
                "body": "Every Python script you write will be imported or executed as __main__. This matters: code at module level runs on import, while code inside `if __name__ == '__main__':` runs only when you execute the file directly. This is not pedantry—it's load-bearing for libraries and testing.\n\nExample:\n```python\ndef greet(name):\n    return f'Hello {name}'\n\nif __name__ == '__main__':\n    print(greet('World'))\n```\n\nWhen another module imports your file, the function is available but the print never executes. This pattern lets you write modules that are also runnable scripts."
            },
            {
                "h": "Bytecode and imports—understanding the .pyc cache",
                "body": "Python compiles to bytecode (.pyc files in __pycache__) on first import. On subsequent runs, Python loads the cached bytecode if the source hasn't changed, which is why imports appear instant. But during development, if you're debugging import issues, the cache can lie—stale .pyc files are a real gotcha. Delete __pycache__ when behavior seems wrong despite code changes. Also: bytecode is not portable between Python versions, so version mismatches can cause import failures even though the source file exists."
            }
        ],
        "links": [
            {"label": "Python if __name__ == '__main__'", "url": "https://docs.python.org/3/library/__main__.html"},
            {"label": "Real Python — Modules and Packages", "url": "https://realpython.com/python-modules-packages/"}
        ]
    },
    "python:1": {
        "title_check": "OOP the way GAMA asks it",
        "sections": [
            {
                "h": "Class attributes vs instance attributes—the namespace depth",
                "body": "Class attributes live on the class object itself; instance attributes live on each instance dict. This distinction matters for inheritance and performance. If you define `shared_list = []` as a class attribute and mutate it in a method, every instance sees the mutation. This is a frequent gotcha:\n\n```python\nclass Config:\n    settings = []  # Class attribute—shared!\n    def add_setting(self, s):\n        self.settings.append(s)  # Mutates the class's shared list\n\nc1 = Config()\nc2 = Config()\nc1.add_setting('a')\nprint(c2.settings)  # ['a'] — c2 sees c1's change\n```\n\nTo avoid this, assign in __init__: `self.settings = []` creates an instance attribute that shadows the class attribute."
            },
            {
                "h": "Method resolution order (MRO) and super()",
                "body": "In multiple inheritance, Python uses C3 linearization to determine which parent method to call. `super()` doesn't mean 'call the parent'; it means 'call the next method in the MRO chain.' This is powerful for cooperative inheritance but confusing in complex hierarchies. You can inspect MRO with `ClassName.__mro__` or `help(ClassName)`. For GAMA-style cybersecurity projects with layered components, MRO discipline prevents attribute shadowing bugs."
            }
        ],
        "links": [
            {"label": "Real Python — Object-Oriented Programming", "url": "https://realpython.com/python3-object-oriented-programming/"},
            {"label": "Python docs — super()", "url": "https://docs.python.org/3/library/functions.html#super"}
        ]
    },
    "python:2": {
        "title_check": "The stdlib you keep forgetting",
        "sections": [
            {
                "h": "collections.defaultdict and Counter for data aggregation",
                "body": "Most Python code reinvents `defaultdict` or writes boilerplate to handle missing keys. `defaultdict(list)` auto-creates an empty list for new keys, eliminating `if key not in dict:` checks. Similarly, `Counter` from the same module is a dict subclass for counting hashables in one line:\n\n```python\nfrom collections import Counter\nwords = ['apple', 'banana', 'apple']\nfreq = Counter(words)\nprint(freq['apple'])  # 2\n```\n\nThese are not fancy—they're labor-saving basics that professionals reach for instinctively."
            },
            {
                "h": "itertools for lazy evaluation and composition",
                "body": "The itertools module provides memory-efficient lazy iterators. `itertools.chain()` flattens nested sequences; `combinations()` and `permutations()` generate all possible tuples without storing them in memory. For cybersecurity tooling or large dataset processing, lazy evaluation keeps memory low. Combine with `for ... in` loops to process on-demand rather than materializing entire lists."
            }
        ],
        "links": [
            {"label": "Python docs — collections", "url": "https://docs.python.org/3/library/collections.html"},
            {"label": "Real Python — itertools", "url": "https://realpython.com/python-itertools/"}
        ]
    },
    "python:3": {
        "title_check": "Generators & context managers",
        "sections": [
            {
                "h": "Generators as stateful iterators",
                "body": "A generator function uses `yield` instead of `return` and pauses at each yield, preserving local state. This means you can write loops that produce infinite sequences without storing everything in memory. The gotcha: calling a generator function returns a generator object, not the first value. You must iterate (with `for` or `next()`) to start execution:\n\n```python\ndef countdown(n):\n    while n > 0:\n        yield n\n        n -= 1\n\ngen = countdown(3)  # No output yet\nfor i in gen:       # Execution starts here\n    print(i)        # 3, 2, 1\n```\n\nGenerators are ideal for lazy parsing of large files or streaming data—you read one chunk at a time on demand."
            },
            {
                "h": "Context managers and resource cleanup",
                "body": "`with` statements ensure cleanup code runs even if an exception occurs. Implement a context manager with `__enter__` and `__exit__` methods, or use the `@contextmanager` decorator from contextlib. This is load-bearing for file handles, network connections, and locks in concurrent code. Without context managers, resource leaks are subtle and hard to track."
            }
        ],
        "links": [
            {"label": "Real Python — Generators", "url": "https://realpython.com/generators-and-yield-in-python/"},
            {"label": "Python docs — contextlib", "url": "https://docs.python.org/3/library/contextlib.html"}
        ]
    },
    "python:4": {
        "title_check": "Errors, exceptions & debugging",
        "sections": [
            {
                "h": "Exception hierarchy and custom exceptions",
                "body": "Python's built-in exceptions form a hierarchy (BaseException → Exception → specific types). Writing custom exceptions by subclassing Exception is standard practice. The gotcha: catching Exception is too broad and hides bugs. Catch specific exceptions, let unexpected ones propagate:\n\n```python\nclass NetworkError(Exception):\n    pass\n\ntry:\n    connect_to_server()\nexcept NetworkError:\n    retry()  # Handle only network failures\nexcept Exception:  # Catch-all—use sparingly\n    raise  # Re-raise to avoid silent bugs\n```\n\nException hierarchy is your first line of defense for robust error handling in security tools."
            },
            {
                "h": "Traceback inspection and pdb for forensics",
                "body": "The `traceback` module lets you inspect the call stack after an exception. In production, log tracebacks to diagnose crashes. For interactive debugging, `pdb` (Python debugger) pauses execution, lets you inspect variables, and step through code. Use `import pdb; pdb.set_trace()` to break into a debugger at any point. For GAMA-level work, understanding stack traces is non-negotiable."
            }
        ],
        "links": [
            {"label": "Real Python — Python Exceptions", "url": "https://realpython.com/python-exceptions/"},
            {"label": "Python docs — pdb", "url": "https://docs.python.org/3/library/pdb.html"}
        ]
    },
    "python:5": {
        "title_check": "Testing your own code",
        "sections": [
            {
                "h": "unittest and test discovery",
                "body": "The `unittest` module provides a framework for writing test cases. Create a TestCase subclass with methods named `test_*`, and unittest discovers and runs them automatically. The key advantage: assertions are built in (`assertEqual`, `assertTrue`, etc.), and test discovery means you don't manually call tests. This scales: as your project grows, a test suite becomes your safety net against regressions.\n\n```python\nimport unittest\n\nclass TestGrader(unittest.TestCase):\n    def test_pass_grade(self):\n        self.assertEqual(grade(90), 'A')\n\nif __name__ == '__main__':\n    unittest.main()\n```\n\nRun with `python -m unittest` and unittest finds all TestCase classes."
            },
            {
                "h": "Mocking dependencies and isolation",
                "body": "Real tests don't call external APIs or databases—they mock them using `unittest.mock`. Mocking replaces expensive or nondeterministic components with stubs, letting you test logic in isolation. `patch()` temporarily replaces a function or class. This is essential for security auditing code: you test your logic without triggering actual network calls or file I/O."
            }
        ],
        "links": [
            {"label": "Real Python — unittest", "url": "https://realpython.com/python-unittest/"},
            {"label": "Python docs — unittest.mock", "url": "https://docs.python.org/3/library/unittest.mock.html"}
        ]
    },
    "csharp:0": {
        "title_check": "Java → C# in one sitting",
        "sections": [
            {
                "h": "Properties vs fields: syntactic convenience",
                "body": "C# introduces properties as first-class citizens. Instead of getters and setters, use `{ get; set; }` syntax. This is not mere sugar—properties enable lazy evaluation, validation, and computed values without changing the call site. A field `public int Value` is mutable by anything; a property `public int Value { get; private set; }` lets only the class mutate it:\n\n```csharp\npublic class Account {\n    private decimal balance;\n    public decimal Balance {\n        get { return balance; }\n        set { if (value >= 0) balance = value; }\n    }\n}\n```\n\nThis discipline matters for security: readonly properties prevent accidental external mutation."
            },
            {
                "h": "Value types vs reference types—structs and the stack",
                "body": "C# distinguishes value types (int, float, custom structs) from reference types (classes). Value types live on the stack and are copied on assignment; reference types live on the heap and are passed by reference. A struct is a lightweight value type ideal for small, immutable data (coordinates, timestamps). Abuse structs and you'll copy large objects repeatedly, tanking performance. Use classes for mutable domain objects and structs for small value containers."
            }
        ],
        "links": [
            {"label": "Microsoft Learn — C# Properties", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/properties"},
            {"label": "Microsoft Learn — Value vs Reference Types", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/value-types"}
        ]
    },
    "csharp:1": {
        "title_check": "Collections & LINQ",
        "sections": [
            {
                "h": "LINQ query syntax and method chaining",
                "body": "LINQ (Language Integrated Query) is C#'s functional query syntax. You can write SQL-like queries on in-memory collections:\n\n```csharp\nvar adults = users.Where(u => u.Age >= 18)\n                   .OrderBy(u => u.Name)\n                   .Select(u => u.Name);\n```\n\nAlternatively, query syntax: `from u in users where u.Age >= 18 ...`. Both compile to the same IL code. LINQ is powerful because it works on IEnumerable, IQueryable (databases), and custom collections. For security auditing, LINQ transforms data pipelines elegantly and safely—far better than manual loops with mutable state."
            },
            {
                "h": "Deferred execution and IEnumerable laziness",
                "body": "LINQ queries don't execute immediately—they're lazy. Calling `.Where()` returns an IEnumerable that wraps the query logic. Only when you iterate (with `foreach` or `.ToList()`) does execution happen. This is powerful for large datasets but tricky: if you iterate twice, the query re-executes. Cache the result with `.ToList()` if you need multiple passes. Understanding laziness prevents performance surprises."
            }
        ],
        "links": [
            {"label": "Microsoft Learn — LINQ Overview", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/linq/"},
            {"label": "Microsoft Learn — Collections and LINQ", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/collections"}
        ]
    },
    "csharp:2": {
        "title_check": "Interfaces, abstract classes & destructors",
        "sections": [
            {
                "h": "Interface contracts and multiple inheritance",
                "body": "An interface is a contract—a set of public members a class must implement. C# supports multiple interface implementation (but only single class inheritance). This is your tool for decoupling: depend on interfaces, not concrete classes. Example:\n\n```csharp\npublic interface ILogger {\n    void Log(string message);\n}\n\npublic class ConsoleLogger : ILogger {\n    public void Log(string message) => Console.WriteLine(message);\n}\n```\n\nAny component that accepts an ILogger can work with any implementation (Console, File, Network). For GAMA-level cybersecurity tools, this flexibility is essential: swap logging implementations without recompiling the core."
            },
            {
                "h": "Destructors and IDisposable",
                "body": "Destructors run during garbage collection but are unpredictable. For reliable cleanup (closing files, releasing handles), implement IDisposable and call Dispose() explicitly or via `using` statements. The Dispose pattern is standard: Dispose() frees resources, and a finalizer (destructor) cleans up if Dispose() wasn't called. Without this discipline, resource leaks fester in production."
            }
        ],
        "links": [
            {"label": "Microsoft Learn — Interfaces", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/interfaces"},
            {"label": "Microsoft Learn — IDisposable", "url": "https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/implementing-dispose"}
        ]
    },
    "csharp:3": {
        "title_check": "Delegates, events & async",
        "sections": [
            {
                "h": "Delegates as type-safe function pointers",
                "body": "A delegate is a type-safe reference to a method. It's C#'s answer to function pointers in C. Define a delegate type, then assign methods (or lambdas) that match its signature:\n\n```csharp\npublic delegate void LogHandler(string message);\n\npublic class Logger {\n    public LogHandler OnLog;\n    public void Log(string msg) => OnLog?.Invoke(msg);\n}\n\nvar logger = new Logger();\nlogger.OnLog = Console.WriteLine;  // Assign a delegate\nlogger.Log(\"Hello\");  // Calls Console.WriteLine\n```\n\nDelegates enable loose coupling: the Logger doesn't know or care what consumes its output. Use `?.Invoke()` to safely call a null delegate."
            },
            {
                "h": "Events and the observer pattern",
                "body": "An event is a delegate wrapped with access control (external code can only subscribe or unsubscribe, not reassign). Events are the publisher-subscriber pattern: publishers raise events, subscribers listen. Use `event` keyword to declare an event on a delegate. This prevents external code from clearing all subscribers or invoking the event directly—essential for defensive programming in large systems."
            }
        ],
        "links": [
            {"label": "Microsoft Learn — Delegates", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/delegates"},
            {"label": "Microsoft Learn — Events", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/events/"}
        ]
    },
    "csharp:4": {
        "title_check": "Exceptions & files",
        "sections": [
            {
                "h": "Exception handling and custom exceptions",
                "body": "C# exceptions follow the same hierarchy as other .NET languages. Create custom exceptions by inheriting from Exception. The golden rule: throw early (at the point of error), catch late (where you can handle it). Catch specific exceptions first, then broad ones:\n\n```csharp\ntry {\n    ReadFile(\"data.txt\");\n} catch (FileNotFoundException) {\n    Console.WriteLine(\"File missing\");\n} catch (IOException) {\n    Console.WriteLine(\"IO error\");\n} catch (Exception) {\n    Console.WriteLine(\"Unexpected\");\n    throw;\n}\n```\n\nRe-throw unexpected exceptions to fail visibly rather than silently swallowing bugs."
            },
            {
                "h": "File I/O and the using statement",
                "body": "The `using` statement automatically disposes file streams, preventing leaks. `File.ReadAllText()` is convenient for small files but loads everything into memory. For large files, use `StreamReader` to process line-by-line. `File.ReadLines()` returns an IEnumerable that reads lazily. Know these options: convenience methods for small files, streams for large data, and always use `using` to guarantee cleanup."
            }
        ],
        "links": [
            {"label": "Microsoft Learn — Exceptions", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/exceptions/"},
            {"label": "Microsoft Learn — File I/O", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/file-system/"}
        ]
    },
    "csharp:5": {
        "title_check": "Generics & the type system",
        "sections": [
            {
                "h": "Generic constraints and type safety",
                "body": "Generics are C#'s answer to templates. A generic class or method is type-safe but reusable:\n\n```csharp\npublic class Cache<T> {\n    private Dictionary<string, T> data = new();\n    public void Set(string key, T value) => data[key] = value;\n    public T Get(string key) => data[key];\n}\n\nvar cache = new Cache<int>();\ncache.Set(\"count\", 42);  // Type-safe: only int allowed\n```\n\nConstraints restrict which types T can be: `where T : class` (reference type), `where T : IComparable` (interface), `where T : new()` (default constructor). Constraints are load-bearing for safe, reusable infrastructure."
            },
            {
                "h": "Variance and covariance in type hierarchies",
                "body": "By default, `List<Animal>` and `List<Dog>` are unrelated types, even if Dog inherits from Animal. Covariance lets you assign `IEnumerable<Dog>` to `IEnumerable<Animal>` (read-only, output-focused). Contravariance goes the opposite way (write-only, input-focused). The `in` and `out` keywords on generic parameters enable this. Understanding variance prevents type-system surprises in complex inheritance hierarchies."
            }
        ],
        "links": [
            {"label": "Microsoft Learn — Generics", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/generics"},
            {"label": "Microsoft Learn — Covariance and Contravariance", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/covariance-contravariance/"}
        ]
    },
    "c:0": {
        "title_check": "Compile, run, and types",
        "sections": [
            {
                "h": "The compilation pipeline: preprocessor, compiler, linker",
                "body": "C compilation has three stages. The preprocessor (cpp) processes `#include` and `#define` directives—it's text substitution, not parsing. The compiler (gcc/clang) parses C and emits object code (.o files). The linker combines object files and libraries into an executable. Errors at each stage differ: preprocessor errors are cryptic (undefined macros), compiler errors are syntax/type issues, linker errors are missing symbols. Understanding this pipeline helps you decode error messages. Compile with `-E` to see preprocessor output: `gcc -E file.c`."
            },
            {
                "h": "Primitive types and integer overflow",
                "body": "C's type system is minimal. `int` size is implementation-defined (usually 4 bytes, 32-bit). Unsigned overflow is well-defined (wraps around); signed overflow is undefined behavior. This matters for security: a buffer size calculated as `int size = length + 1;` can underflow if length is MAX_INT, causing heap overflow. Use fixed-width types: `uint32_t`, `int64_t` from `<stdint.h>` for predictable behavior across platforms."
            }
        ],
        "links": [
            {"label": "C Reference — Compilation", "url": "https://en.cppreference.com/w/c/preprocessor"},
            {"label": "C Reference — Data Types", "url": "https://en.cppreference.com/w/c/language/type"}
        ]
    },
    "c:1": {
        "title_check": "Pointers",
        "sections": [
            {
                "h": "Pointer arithmetic and array indexing",
                "body": "A pointer is a memory address. Pointer arithmetic is tied to type: `int *p` points to an int; `p + 1` advances by sizeof(int) bytes, not 1 byte. This is why types matter. Array indexing is syntactic sugar for pointer arithmetic:\n\n```c\nint arr[3] = {10, 20, 30};\nint *p = &arr[0];\nprintf(\"%d\\\\n\", p[1]);      // 20 (equivalent to arr[1])\nprintf(\"%d\\\\n\", *(p + 1));  // 20 (same thing, explicit pointer arithmetic)\n```\n\nBoundary violations (reading/writing beyond array bounds) don't crash immediately—they silently corrupt memory. This is C's power and danger: no runtime checks, unbounded access."
            },
            {
                "h": "Null pointers and undefined behavior",
                "body": "Dereferencing a NULL pointer causes undefined behavior (often a crash, sometimes silent corruption). Always check pointers before use. A common gotcha: `if (p) { *p = value; }` checks the pointer; without it, you're in undefined-behavior land. For security-critical code, assertions and defensive checks are non-negotiable. Sanitizers like AddressSanitizer catch pointer bugs at runtime during testing."
            }
        ],
        "links": [
            {"label": "C Reference — Pointers", "url": "https://en.cppreference.com/w/c/language/pointer"},
            {"label": "C Reference — Undefined Behavior", "url": "https://en.cppreference.com/w/c/language/behavior"}
        ]
    },
    "c:2": {
        "title_check": "Structs & strings",
        "sections": [
            {
                "h": "Struct packing and memory layout",
                "body": "A struct is a collection of members laid out in memory sequentially (usually). Member order matters: the compiler may add padding to align members on addresses the CPU prefers. A struct with `char, int, char` might allocate 12 bytes (1 + 3 padding + 4 + 1 + 3 padding), not 6. Check alignment with sizeof and offsetof:\n\n```c\nstruct Data { char c; int i; char d; };\nprintf(\"%zu, %zu\\\\n\", sizeof(struct Data), offsetof(struct Data, i));\n```\n\nFor security-critical serialization (network protocols, file formats), explicit padding and byte order matter. Use `#pragma pack` to control packing, but understand the trade-off: tighter packing hurts performance."
            },
            {
                "h": "String handling: null-terminated arrays",
                "body": "C strings are arrays of char terminated by '\\0'. This design is error-prone: buffer overflows occur when you write more data than the array holds. `strcpy()` is notoriously unsafe (no bounds checking); use `strncpy()` with a size limit. Better: use safe functions from C11's `<string.h>` annex. Always allocate +1 for the null terminator: `char buf[101]` for 100-char strings. A gotcha: `strlen()` counts up to the first null but doesn't include it in the count."
            }
        ],
        "links": [
            {"label": "C Reference — Structs", "url": "https://en.cppreference.com/w/c/language/struct"},
            {"label": "C Reference — String Handling", "url": "https://en.cppreference.com/w/c/string/byte"}
        ]
    },
    "c:3": {
        "title_check": "Dynamic memory & bits",
        "sections": [
            {
                "h": "malloc, free, and the heap",
                "body": "Dynamic memory comes from the heap via malloc(). You must free() every malloc() or leak memory. A subtle gotcha: free(NULL) is safe (no-op), but free(invalid_pointer) is undefined behavior. Double-free (freeing twice) is also undefined behavior—often crashes. For security: validate all pointers before freeing. Use tools like valgrind to detect leaks during development:\n\n```c\nint *data = malloc(sizeof(int) * 100);\nif (!data) { perror(\"malloc\"); exit(1); }\n// Use data\nfree(data);\ndata = NULL;  // Good practice: avoid accidental re-use\n```\n\nSetting pointers to NULL after free prevents double-free accidents but doesn't eliminate the root cause."
            },
            {
                "h": "Bitwise operations and flags",
                "body": "C's bitwise operators (|, &, ^, ~, <<, >>) manipulate individual bits. A common pattern: bitmasks for flags. `int flags = 0x01 | 0x04;` sets bits; `if (flags & 0x01)` checks a bit. Bitshifts are efficient: `x << 3` multiplies by 8, `x >> 2` divides by 4 (for unsigned). Gotchas: bitwise AND (`&`) is not logical AND (`&&`); use parentheses to clarify precedence. For low-level security work (cryptography, bit-level protocol parsing), bitwise operations are foundational."
            }
        ],
        "links": [
            {"label": "C Reference — Memory Management", "url": "https://en.cppreference.com/w/c/memory"},
            {"label": "C Reference — Bitwise Operators", "url": "https://en.cppreference.com/w/c/language/operator_arithmetic"}
        ]
    },
    "c:4": {
        "title_check": "Arrays & the pointer-array duality",
        "sections": [
            {
                "h": "Arrays decay to pointers, and the implications",
                "body": "In C, an array name decays to a pointer to its first element in most contexts. This is why `arr[i]` and `*(arr + i)` are equivalent. A function parameter `int arr[100]` is actually `int *arr`—the size information is lost. This is why you must pass size separately:\n\n```c\nvoid process(int *arr, int len) {\n    for (int i = 0; i < len; i++) printf(\"%d \", arr[i]);\n}\n\nint data[10] = { };\nprocess(data, 10);  // Must pass 10; function doesn't know array size\n```\n\nArray-to-pointer decay is a source of bounds-checking bugs: there's no way to know the original array size from a pointer alone. This is why buffer overflows are common in C."
            },
            {
                "h": "Multidimensional arrays and row-major layout",
                "body": "A 2D array `int matrix[3][4]` is laid out in memory row-major (rows are contiguous). Accessing `matrix[i][j]` is equivalent to `*(*(matrix + i) + j)`. Passing a 2D array to a function requires specifying all but the first dimension: `void func(int m[][4])`, not `int m[][]`. Common mistake: treating a 1D array as 2D by calculating indices manually (`arr[i * cols + j]`) is error-prone. Stick to proper array syntax or use dynamic allocation with pointers-to-pointers for safer 2D arrays."
            }
        ],
        "links": [
            {"label": "C Reference — Array Declarations", "url": "https://en.cppreference.com/w/c/language/array"},
            {"label": "C Reference — Pointer Declaration", "url": "https://en.cppreference.com/w/c/language/declarations"}
        ]
    },
    "c:5": {
        "title_check": "Multi-file programs & the preprocessor",
        "sections": [
            {
                "h": "Header files, include guards, and the link model",
                "body": "In a multi-file project, header files (.h) declare interfaces; .c files implement them. Use include guards (`#ifndef`, `#define`, `#endif`) to prevent re-inclusion:\n\n```c\n// math.h\n#ifndef MATH_H\n#define MATH_H\nint add(int a, int b);\n#endif\n\n// main.c\n#include \"math.h\"\nint main() { return add(1, 2); }\n\n// math.c\nint add(int a, int b) { return a + b; }\n```\n\nCompile all files: `gcc -c math.c main.c` produces object files; then link: `gcc math.o main.o -o program`. Without proper header discipline, you get symbol conflicts (multiple definitions) or missing symbol errors (declarations without implementations)."
            },
            {
                "h": "The preprocessor: macros and conditional compilation",
                "body": "The preprocessor is a text-substitution engine. `#define MAX 100` replaces MAX with 100 before compilation. Macros are powerful but dangerous: no type checking, no scope rules. Gotchas: `#define SQUARE(x) x * x` expands `SQUARE(2 + 1)` to `2 + 1 * 2 + 1` (wrong precedence). Use `#define SQUARE(x) ((x) * (x))` for safety. Conditional compilation (`#ifdef DEBUG`, `#if defined(FEATURE)`) is useful for build variants, but abuse leads to unmaintainable code."
            }
        ],
        "links": [
            {"label": "C Reference — Preprocessor", "url": "https://en.cppreference.com/w/c/preprocessor"},
            {"label": "C Reference — Translation Phases", "url": "https://en.cppreference.com/w/c/language/translation_phases"}
        ]
    }
}
