# explain_questions.py — one AI-graded "explain-back" question per Lab lesson.
# Keyed "track:index" (matching content.build_courses order). Rendered after the lesson.
EXPLAIN_QUESTIONS = {
    "python:0": {
        "title_check": "Building from a blank file",
        "q": "Explain the purpose of the `if __name__ == '__main__':` guard and why it matters when organizing a Python project.",
        "rubric": "A strong answer identifies that this guard prevents code from running when the module is imported, allows testing in isolation, and distinguishes between direct execution and library reuse. Should mention that it enables both scripts and importable modules.",
    },
    "python:1": {
        "title_check": "OOP the way GAMA asks it",
        "q": "Walk through how inheritance and polymorphism work together in a concrete example, and explain why they matter for code reuse.",
        "rubric": "A strong answer shows a class hierarchy where a subclass overrides a parent method, demonstrates that polymorphism lets you treat subclass instances as parent types, and explains that this reduces duplication and enables flexible designs.",
    },
    "python:2": {
        "title_check": "The stdlib you keep forgetting",
        "q": "Describe three standard library modules that solve common problems and explain what problem each one solves.",
        "rubric": "A strong answer names three different modules (e.g., os, json, re, collections) and clearly states what each handles — file I/O, data parsing, text patterns, or data structures. Each description should be specific, not generic.",
    },
    "python:3": {
        "title_check": "Generators & context managers",
        "q": "Explain what a generator does and how it differs from a regular function that returns a list. When would you use each?",
        "rubric": "A strong answer explains that generators use `yield` to produce values lazily one at a time, while functions return all values at once. Should mention memory efficiency for large datasets and that generators preserve state between calls.",
    },
    "python:4": {
        "title_check": "Errors, exceptions & debugging",
        "q": "Describe the difference between raising an exception and letting an error propagate naturally. When would you catch an exception, and what should you do in the except block?",
        "rubric": "A strong answer explains that raising is explicit signaling of an error condition, catching lets you handle recoverable errors gracefully, and the except block should either fix the problem, log it, or re-raise if unrecoverable. Should reference specific exception types.",
    },
    "python:5": {
        "title_check": "Testing your own code",
        "q": "Explain why unit tests matter and walk through the anatomy of a single test: what it sets up, what it checks, and what happens if the check fails.",
        "rubric": "A strong answer emphasizes that tests catch regressions and document expected behavior. Should describe Arrange-Act-Assert: setting up state, calling the function, and using assert to verify output matches expectation.",
    },
    "csharp:0": {
        "title_check": "Java → C# in one sitting",
        "q": "List three key differences between Java and C# (e.g., syntax, features, or platform), and explain why each difference exists.",
        "rubric": "A strong answer identifies at least three differences such as: `using` vs `import`, value types (struct) vs all-objects, properties with getters/setters, or .NET vs JVM. Each should explain the design choice or consequence.",
    },
    "csharp:1": {
        "title_check": "Collections & LINQ",
        "q": "Explain LINQ and show how it simplifies filtering and transforming a list of objects compared to traditional loops.",
        "rubric": "A strong answer shows a practical LINQ example (e.g., `.Where()`, `.Select()`, `.OrderBy()`) and contrasts it with equivalent foreach loops. Should highlight readability, conciseness, and declarative style.",
    },
    "csharp:2": {
        "title_check": "Interfaces, abstract classes & destructors",
        "q": "Describe when you would use an interface versus an abstract class, and explain why destructors exist in C# when garbage collection is automatic.",
        "rubric": "A strong answer explains interfaces for contracts/multiple inheritance and abstract classes for shared implementation. Should address that destructors handle unmanaged resources (file handles, database connections) that GC does not clean up automatically.",
    },
    "csharp:3": {
        "title_check": "Delegates, events & async",
        "q": "Explain what a delegate is and how events use delegates to enable loose coupling between components.",
        "rubric": "A strong answer defines delegates as type-safe function pointers, shows how events wrap delegates to let subscribers register callbacks, and explains that this decouples the event raiser from the listeners.",
    },
    "csharp:4": {
        "title_check": "Exceptions & files",
        "q": "Walk through a file I/O operation and explain what exceptions can occur, how you would handle them, and why proper cleanup matters.",
        "rubric": "A strong answer mentions FileNotFoundException, IOException, or permission errors, explains try-catch-finally or using statements, and emphasizes that file handles must close even if an error occurs.",
    },
    "csharp:5": {
        "title_check": "Generics & the type system",
        "q": "Explain what generics are and why `List<T>` is safer and more flexible than `ArrayList` (the pre-generics C# collection).",
        "rubric": "A strong answer shows that generics are parameterized types, prevent casting errors at runtime, enable compile-time type checking, and avoid boxing overhead for value types. Should contrast boxing/unboxing in ArrayList.",
    },
    "c:0": {
        "title_check": "Compile, run, and types",
        "q": "Describe the steps from source code to running executable, and explain why C type declarations exist (e.g., `int`, `char`) when memory is ultimately just bytes.",
        "rubric": "A strong answer covers compilation stages (preprocess, compile, assemble, link), and explains that type declarations tell the compiler how to interpret bytes in memory and what operations are valid.",
    },
    "c:1": {
        "title_check": "Pointers",
        "q": "Explain what a pointer is, show how to declare one, and walk through a concrete example of dereferencing to access data.",
        "rubric": "A strong answer defines pointers as addresses in memory, shows `int *p`, explains `&` (address-of) and `*` (dereference), and demonstrates reading/modifying a value through a pointer.",
    },
    "c:2": {
        "title_check": "Structs & strings",
        "q": "Explain how a struct packs data in memory, and describe how C strings (char arrays) differ from higher-level string types in other languages.",
        "rubric": "A strong answer explains structs group fields into contiguous memory, C strings are null-terminated char arrays with no built-in length, and that this requires manual bounds checking and careful manipulation.",
    },
    "c:3": {
        "title_check": "Dynamic memory & bits",
        "q": "Describe the difference between stack and heap allocation, when you'd use malloc/free, and what happens if you don't free memory.",
        "rubric": "A strong answer explains stack is automatic/limited/fast, heap is manual/large/slow, malloc allocates on heap and returns a pointer, free deallocates, and memory leaks occur if you lose the pointer without freeing.",
    },
    "c:4": {
        "title_check": "Arrays & the pointer-array duality",
        "q": "Explain how arrays and pointers are related in C, and show with an example why `array[i]` and `*(array + i)` are equivalent.",
        "rubric": "A strong answer explains arrays decay to pointers in most contexts, show the address arithmetic (`array + i`), and demonstrate that both forms access the same memory. Should clarify that arrays are not pointers (they have size).",
    },
    "c:5": {
        "title_check": "Multi-file programs & the preprocessor",
        "q": "Explain the difference between `.c` and `.h` files, and walk through how `#include` and the preprocessor enable separate compilation.",
        "rubric": "A strong answer describes header files as interface declarations, source files as implementation, explains `#include` copies headers into the translation unit, and notes the preprocessor's role in macro expansion and conditional compilation.",
    },
    "asm:0": {
        "title_check": "Registers & moving data",
        "q": "Name the main x64 registers and explain what MOV does. Why can't you MOV between memory and memory?",
        "rubric": "A strong answer lists registers like rax, rbx, rsp, identifies MOV as copying data, and explains that x64 lacks a memory-to-memory instruction; you must use a register as an intermediate.",
    },
    "asm:1": {
        "title_check": "Control flow & flags",
        "q": "Explain what condition flags (like ZF, CF) are and how conditional jumps (JZ, JNE) use them to branch.",
        "rubric": "A strong answer describes flags as bits set by arithmetic/logic instructions, shows that comparisons set flags without storing results, and explains that JMP variants test flags to decide whether to jump.",
    },
    "asm:2": {
        "title_check": "The stack, call & ret",
        "q": "Walk through what happens on the stack when a function is called and returns, including the return address and any saved registers.",
        "rubric": "A strong answer explains CALL pushes the return address, locals/spill go on stack, saved registers are pushed, RET pops return address and jumps. Should mention the stack frame and RSP/RBP.",
    },
    "asm:3": {
        "title_check": "Syscalls & reading disassembly",
        "q": "Explain what a syscall is, how it differs from a regular function call, and how you would identify a syscall in disassembled code.",
        "rubric": "A strong answer defines syscalls as transitions from user mode to kernel (OS) code, notes they use a special instruction (SYSCALL/INT 80), and explains disassemblers show this as a call to a system function or RAX setup.",
    },
    "asm:4": {
        "title_check": "Addressing modes & memory operands",
        "q": "Describe different ways to address memory in x64 (immediate, register, displacement, SIB) and give a realistic example of each.",
        "rubric": "A strong answer lists addressing modes like `[rax]`, `[rax + rbx]`, `[rax + 8]`, `[rax + rbx*4 + 8]`, explains their use cases (array indexing, struct offsets), and shows concrete MOV/LEA examples.",
    },
    "asm:5": {
        "title_check": "Calling conventions & the ABI",
        "q": "Explain the System V AMD64 ABI calling convention: which registers are used for arguments, which are caller-saved, and why this matters.",
        "rubric": "A strong answer covers parameter registers (rdi, rsi, rdx, rcx, r8, r9), return value (rax/rdx), caller-saved vs callee-saved registers, and emphasizes that both caller and callee must follow these rules or code breaks.",
    },
    "linux:0": {
        "title_check": "Move and manage",
        "q": "Explain what `ls`, `cd`, `mkdir`, `cp`, and `mv` do, and describe how path navigation works (absolute vs relative).",
        "rubric": "A strong answer explains each command's purpose, shows path syntax (/ for root, . for current, .. for parent), and demonstrates practical usage distinguishing absolute paths from relative.",
    },
    "linux:1": {
        "title_check": "Pipes, grep & redirection",
        "q": "Explain how pipes (`|`) connect commands and show an example using grep to filter output. What do `>` and `<` do?",
        "rubric": "A strong answer shows piping as passing stdout of one command to stdin of the next, gives a concrete grep example (e.g., `ps aux | grep python`), and explains stdout redirection (>) and stdin redirection (<).",
    },
    "linux:2": {
        "title_check": "Permissions & processes",
        "q": "Explain how file permissions (rwx for user/group/other) work in Linux, and describe how `ps` and `kill` manage running processes.",
        "rubric": "A strong answer covers chmod numeric/symbolic mode, rwx meanings, shows ps output interpretation (PID, status), and explains kill sends signals (e.g., SIGTERM, SIGKILL) to terminate processes.",
    },
    "linux:3": {
        "title_check": "Your first bash script",
        "q": "Walk through the structure of a bash script: shebang, variables, conditionals, and loops. Show why `#!/bin/bash` matters.",
        "rubric": "A strong answer shows shebang as the interpreter directive, demonstrates variable assignment and referencing ($VAR), shows if-then-else and for/while loops, and explains the shebang lets the OS execute the script directly.",
    },
    "linux:4": {
        "title_check": "Text processing: sort, uniq, cut, sed, awk",
        "q": "Describe what `cut`, `sort`, and `uniq` do, and show how you would use `awk` to extract and process specific fields from lines.",
        "rubric": "A strong answer covers cut for column extraction, sort for ordering, uniq for deduplication, and shows awk as a pattern-action language that splits lines and processes fields. Should include a concrete awk example.",
    },
    "linux:5": {
        "title_check": "SSH, networking & packages",
        "q": "Explain what SSH is, how it differs from telnet, and describe how `apt` or `yum` package managers install software from repositories.",
        "rubric": "A strong answer defines SSH as encrypted remote login (vs telnet's plain text), covers key-based authentication, and explains package managers resolve dependencies and fetch binaries from official repos.",
    },
    "cyber_high:0": {
        "title_check": "The layers",
        "q": "Describe the OSI model layers (1-4 especially) and give an example of what happens at each layer when you visit a website.",
        "rubric": "A strong answer covers Physical (cables), Link (Ethernet), Network (IP), Transport (TCP), and explains that each layer adds headers, abstracts lower layers, and solves specific problems like routing or reliable delivery.",
    },
    "cyber_high:1": {
        "title_check": "TCP vs UDP & the handshake",
        "q": "Explain the TCP three-way handshake (SYN, SYN-ACK, ACK) and contrast it with UDP. When would you use each protocol?",
        "rubric": "A strong answer diagrams the handshake sequence, explains TCP guarantees order/delivery (hence overhead), UDP is fast but unreliable, and gives use cases: TCP for files/email, UDP for streaming/VoIP.",
    },
    "cyber_high:2": {
        "title_check": "Open a website — the full trace",
        "q": "Walk through all the steps from typing a URL to seeing the webpage: DNS, TCP, TLS, HTTP. What does each layer do?",
        "rubric": "A strong answer traces DNS resolution to IP, TCP connection, TLS handshake for encryption, HTTP GET request, and server response. Should mention each step's purpose and how they chain together.",
    },
    "cyber_high:3": {
        "title_check": "See it live in Wireshark",
        "q": "Explain what Wireshark is and what information a typical TCP/IP packet shows. How would you filter to see only HTTP traffic?",
        "rubric": "A strong answer defines Wireshark as a packet sniffer/analyzer, describes packet layers (source/dest IP, port, flags, payload), and shows filtering syntax (e.g., `http` or `tcp.port == 80`). Should mention the importance of seeing raw protocol data.",
    },
    "cyber_high:4": {
        "title_check": "Ports, sockets & the client-server model",
        "q": "Explain what a port is, how sockets work, and describe the client-server model: who listens, who connects, and how they exchange data.",
        "rubric": "A strong answer defines ports as 16-bit identifiers for services (e.g., 80 for HTTP), sockets as endpoints of a connection, and describes servers listening on ports and clients initiating connections. Should cover both TCP and UDP sockets.",
    },
    "cyber_high:5": {
        "title_check": "HTTP & TLS up close",
        "q": "Describe the HTTP request-response cycle and explain how TLS (HTTPS) encrypts the connection. What does the certificate authenticate?",
        "rubric": "A strong answer shows HTTP verbs (GET, POST), headers, and body, explains TLS uses a handshake to establish a shared encryption key, and clarifies certificates authenticate the server's identity to prevent MITM attacks.",
    },
    "cyber_low:0": {
        "title_check": "Bases & bitwise",
        "q": "Explain binary, hexadecimal, and how to convert between them. Show a practical bitwise operation (AND, OR, XOR) and explain its use.",
        "rubric": "A strong answer shows base conversions with examples, explains AND/OR/XOR gate logic, and gives practical uses like bit masking or checking flags. Should show actual binary notation.",
    },
    "cyber_low:1": {
        "title_check": "Endianness & hex dumps",
        "q": "Explain big-endian vs little-endian and show how a value like 0x12345678 appears differently in memory on each architecture. When does this matter?",
        "rubric": "A strong answer diagrams byte order (most significant byte first vs last), shows a concrete hex dump example, and explains endianness matters when sharing data across systems or interpreting raw memory.",
    },
    "cyber_low:2": {
        "title_check": "How a process is laid out",
        "q": "Describe the memory layout of a running process: code, data, BSS, heap, and stack. What lives where and why?",
        "rubric": "A strong answer diagrams the segments from low to high addresses (code/text, initialized data, uninitialized data/BSS, heap, stack), explains static data vs dynamic allocation, and why stack grows downward.",
    },
    "cyber_low:3": {
        "title_check": "PE vs ELF",
        "q": "Explain the difference between PE (Windows) and ELF (Linux) executable formats and why the OS needs these structures.",
        "rubric": "A strong answer covers that PE and ELF are file formats specifying how to load and run code, describe key sections/segments, explain they include headers, entry points, and relocation info, and note OS-specific design.",
    },
    "cyber_low:4": {
        "title_check": "Representing chars, floats & struct padding",
        "q": "Explain how characters are encoded (ASCII/UTF-8), how floats store sign/exponent/mantissa, and why struct padding exists.",
        "rubric": "A strong answer covers char encoding (bytes to characters), IEEE 754 float format, and explains padding aligns fields to word boundaries for CPU efficiency and predictable offsets.",
    },
    "cyber_low:5": {
        "title_check": "How a stack overflow works (conceptually)",
        "q": "Describe how a buffer overflow overwrites the stack, corrupts the return address, and allows an attacker to redirect execution. What defenses exist?",
        "rubric": "A strong answer explains unbounded writes past array bounds overwrite adjacent stack frames, shows how return address corruption hijacks control flow, and mentions canaries, NX bits, and ASLR as defenses.",
    },
    "cmd:0": {
        "title_check": "Files & navigation",
        "q": "Explain what `dir`, `cd`, `mkdir`, `copy`, and `move` do in Windows Command Prompt, and describe path syntax including drive letters.",
        "rubric": "A strong answer covers each command's purpose, shows path format (C:\\\\, relative with ..), explains DIR output (size, date, attributes), and demonstrates navigation between drives.",
    },
    "cmd:1": {
        "title_check": "Network commands",
        "q": "Describe what `ipconfig`, `ping`, `tracert`, and `netstat` reveal about network configuration and connectivity. How would you use each for troubleshooting?",
        "rubric": "A strong answer explains ipconfig shows IP/DNS/gateway, ping tests reachability and latency, tracert traces route to host with hop times, and netstat shows active connections and listening ports.",
    },
    "cmd:2": {
        "title_check": "Live recon",
        "q": "Explain how `tasklist`, `netstat`, and `wmic` (or `Get-Process` in PowerShell) reveal what's running on a system and its network activity.",
        "rubric": "A strong answer shows tasklist/Get-Process output (PID, name), explains netstat output (local/remote IP, state), and describes wmic as a management interface for OS details. Should include practical filtering examples.",
    },
    "cmd:3": {
        "title_check": "Script it with .bat",
        "q": "Explain the structure of a batch file: variables, conditionals, loops, and how `%var%` and `!var!` differ in scope. Show a practical example.",
        "rubric": "A strong answer covers @echo off and setlocal, demonstrates FOR loops and IF statements, explains %var% for simple substitution and !var! for delayed expansion in loops, with a working batch script.",
    },
    "cmd:4": {
        "title_check": "PowerShell basics (and when to use it)",
        "q": "Compare batch files and PowerShell: what's each good for? Explain basic PowerShell syntax: cmdlets, piping, and objects.",
        "rubric": "A strong answer explains batch is legacy/simple, PowerShell is modern/.NET-based with richer features, shows Verb-Noun cmdlets, piping objects (not text), and practical Get-* examples.",
    },
    "cmd:5": {
        "title_check": "Environment, tasks & scheduling",
        "q": "Explain what environment variables are, how to read/set them, and describe how Task Scheduler lets you automate scripts.",
        "rubric": "A strong answer shows environment variables store configuration (PATH, TEMP), demonstrates SET/setx for local/persistent changes, and describes Task Scheduler's UI for running batch/PowerShell on a schedule.",
    },
    "dsa:0": {
        "title_check": "Big-O & thinking about cost",
        "q": "Explain Big-O notation and walk through analyzing the time complexity of a simple loop. Why is O(n) better than O(n²)?",
        "rubric": "A strong answer defines Big-O as worst-case asymptotic growth, shows nested loops are O(n²), linear loops are O(n), and explains that doubling n increases O(n²) work by 4x vs 2x for O(n).",
    },
    "dsa:1": {
        "title_check": "Arrays & two pointers",
        "q": "Explain the two-pointer technique on a sorted array and show a concrete example (e.g., finding a pair that sums to a target).",
        "rubric": "A strong answer describes using fast/slow pointers or left/right pointers from ends, walks through the algorithm eliminating impossible pairs, and shows correctness relies on sorted input.",
    },
    "dsa:2": {
        "title_check": "Hash maps & sets — your #1 tool",
        "q": "Explain how hash tables work: hashing, collisions, load factor. Why are they so fast? Show a use case where a hash map beats an array.",
        "rubric": "A strong answer covers hashing as O(1) lookup, mentions collision handling (chaining, probing), explains load factor for resizing, and gives practical examples like deduplication or frequency counting vs nested loops.",
    },
    "dsa:3": {
        "title_check": "Sliding window",
        "q": "Explain the sliding window technique and show how it solves a problem like finding the longest substring without repeating characters.",
        "rubric": "A strong answer describes maintaining a window of valid/candidate elements, expanding and contracting based on constraints, and demonstrates that it reduces redundant rechecking. Should show the algorithm flow.",
    },
    "dsa:4": {
        "title_check": "Stacks & queues",
        "q": "Explain what stacks and queues are, how LIFO and FIFO differ, and give a real-world use case for each (e.g., parsing, scheduling).",
        "rubric": "A strong answer defines stack push/pop and queue enqueue/dequeue, explains LIFO vs FIFO behavior, and connects each to practical problems like expression evaluation or breadth-first search.",
    },
    "dsa:5": {
        "title_check": "Linked lists",
        "q": "Describe what a linked list is, how it differs from an array (trade-offs in access, insertion, memory), and show how to traverse a linked list.",
        "rubric": "A strong answer explains nodes with data and next pointers, contrasts slow random access with fast insertions, notes they suit problems with frequent middle insertions, and demonstrates traversal with a loop.",
    },
    "dsa:6": {
        "title_check": "Binary search",
        "q": "Explain binary search, why it requires a sorted array, and analyze its time complexity. Show how to avoid off-by-one errors in bounds.",
        "rubric": "A strong answer describes dividing the search space in half each iteration, derives O(log n) by counting halvings, and emphasizes sorted input is essential. Should address mid calculation and loop invariants.",
    },
    "dsa:7": {
        "title_check": "Recursion & backtracking",
        "q": "Explain recursion: base case, recursive case, and the call stack. Show how backtracking builds solutions by exploring and undoing choices.",
        "rubric": "A strong answer defines base case (termination), recursive case (smaller subproblem), and call stack depth. Should show backtracking as trying options, undoing on failure, and efficiently pruning search space.",
    },
    "dsa:8": {
        "title_check": "Trees, BFS & DFS",
        "q": "Describe tree structure (parent, child, root, leaf) and explain BFS and DFS traversals. When would you use each?",
        "rubric": "A strong answer covers tree terminology, shows BFS using a queue (level-order) and DFS using a stack/recursion (pre/in/post-order), and explains BFS finds shortest paths while DFS uses less memory.",
    },
    "dsa:9": {
        "title_check": "Sorting & heaps",
        "q": "Name three sorting algorithms, explain their time complexities, and describe how a heap enables efficient sorting and priority queue operations.",
        "rubric": "A strong answer covers algorithms like quicksort, mergesort, heapsort with their best/worst/average cases, explains heap as a binary tree with parent >= children, and shows heap-sort heapifies then extracts roots.",
    },
    "dsa:10": {
        "title_check": "Graphs & connectivity",
        "q": "Explain how to represent a graph (adjacency list, matrix) and describe algorithms for finding connected components or shortest paths.",
        "rubric": "A strong answer covers graph terminology (vertices, edges, directed/undirected), representation trade-offs (list vs matrix), and shows algorithms like DFS for components or BFS/Dijkstra for shortest paths.",
    },
    "dsa:11": {
        "title_check": "Dynamic programming",
        "q": "Explain dynamic programming: overlapping subproblems, optimal substructure, and memoization. Show how it speeds up recursion with a concrete example.",
        "rubric": "A strong answer defines DP as solving subproblems once and reusing results, contrasts naive recursion (recomputes) with DP (caches), and shows a classic problem like fibonacci where DP reduces from exponential to linear.",
    },
}
