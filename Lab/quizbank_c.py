# quizbank_c.py - additional graded checks for the c track.
# Merged onto each lesson's existing quiz by content.build_courses().
# Answer indices balanced across the file so the correct option isn't always first.
EXTRA_QUIZ = {
    "c-1": [
        {
            "q": "What does `gcc prog.c -S -masm=intel -o prog.s` produce?",
            "code": "",
            "options": [
                "Human-readable assembly, stopping before the assembler and linker run",
                "A finished executable",
                "An object file with unresolved symbols",
                "A preprocessed C file"
            ],
            "answer": 0,
            "why": "-S halts compilation after generating assembly, so you can read the instructions your C became.",
            "detail": "`-S` stops the pipeline at the assembly stage, writing prog.s. A finished executable is the default (no flag) or with linking; an object file with unresolved symbols is `-c`; a preprocessed C file is `-E`. Knowing these stage-stopping flags lets you inspect exactly what each phase produced, which is how you verify what the compiler did rather than assuming."
        },
        {
            "q": "Why does `printf(\"%d\", 3.14)` print garbage rather than 3?",
            "code": "printf(\"%d\", 3.14);",
            "options": [
                "printf rounds 3.14 to 3 automatically",
                "%d expects an int but a double was passed; printf misreads the bytes with no type checking",
                "It is a compile error",
                "printf prints 3 correctly"
            ],
            "answer": 1,
            "why": "printf is variadic with no type checking, so %d reads the argument as an int though a double's bytes were passed.",
            "detail": "The format string is the only thing telling printf how to interpret each argument; passing a double where %d expects an int means printf reads the wrong bytes as an integer, producing garbage. printf does not round or convert — it trusts the specifier. Modern compilers warn with -Wformat but the language does not require it, so it is not a hard compile error, and it does not print 3. Matching specifiers to argument types is entirely the programmer's responsibility in C."
        },
        {
            "q": "What does this print on a typical system?",
            "code": "char c = 'A';\nprintf(\"%d %c\\n\", c, c);",
            "options": [
                "A A",
                "65 65",
                "65 A",
                "A 65"
            ],
            "answer": 2,
            "why": "%d prints the char's integer code (65 for 'A'); %c prints it as the character.",
            "detail": "A char IS a small integer in C, holding 'A''s ASCII code 65. %d displays that number, %c displays the corresponding character — same value, two views. 'A A' ignores %d, '65 65' ignores %c, and 'A 65' reverses the specifiers. This equivalence of characters and small integers is fundamental C: you can do arithmetic on chars, and 'A' + 1 is 'B'."
        },
        {
            "q": "What is the value and type issue in this comparison?",
            "code": "unsigned int a = 1;\nint b = -1;\nprintf(\"%d\\n\", a > b);",
            "options": [
                "Prints 1 — 1 is obviously greater than -1",
                "Prints -1",
                "It is undefined behavior",
                "Prints 0 — b is converted to a huge unsigned value, so a > b is false"
            ],
            "answer": 3,
            "why": "Mixing signed and unsigned converts the signed -1 to a large unsigned number, so 1 > that is false (0).",
            "detail": "In a comparison between unsigned and signed, C converts the signed operand to unsigned, so -1 becomes UINT_MAX (about 4 billion). Then 1 > 4-billion is false, printing 0. The 'obviously 1' answer is the intuition trap this question targets. It is not -1 (the result of > is 0 or 1) and it is well-defined, not UB — the conversion rules are specified. This signed/unsigned mixing bug is a classic source of silent wrong answers."
        },
        {
            "q": "A program compiles but crashes at runtime. Which is the LEAST likely to be caught by the compiler?",
            "code": "",
            "options": [
                "Dereferencing a pointer that happens to be NULL at runtime",
                "A missing semicolon",
                "Calling an undeclared function with -Werror",
                "Assigning a string literal to an int"
            ],
            "answer": 0,
            "why": "A NULL dereference depends on runtime values the compiler cannot know; the others are static errors.",
            "detail": "Whether a pointer is NULL when dereferenced is a runtime property, invisible to the compiler, so it crashes at execution not compilation. A missing semicolon is a syntax error, an undeclared function under -Werror is rejected, and assigning a string to an int is a type error — all caught statically. This is the core lesson that C compiles many things that fail at runtime, which is why memory bugs dominate C debugging."
        },
        {
            "q": "What does `sizeof(int)` typically return on this Windows x64 setup, and what does that tell you?",
            "code": "printf(\"%zu %zu\\n\", sizeof(int), sizeof(void*));",
            "options": [
                "8 8 — everything is 8 bytes on 64-bit",
                "4 8 — int is 4 bytes but a pointer is 8 bytes on 64-bit",
                "4 4 — int and pointer are the same size",
                "2 4 — the old 16-bit sizes"
            ],
            "answer": 1,
            "why": "On typical 64-bit systems int stays 4 bytes while pointers are 8, so they are NOT interchangeable.",
            "detail": "int is 4 bytes on virtually all modern platforms, but a pointer must be 8 bytes to address 64-bit memory. Assuming they are equal (4 4 or 8 8) is exactly the bug that breaks when you store a pointer in an int, truncating it. Using %zu is the correct specifier for size_t. This size difference is why casting pointers to int loses data on 64-bit and why you use intptr_t if you must."
        }
    ],
    "c-2": [
        {
            "q": "What is the difference between `int *p` being NULL and being uninitialized?",
            "code": "int *p1 = NULL;\nint *p2;   // uninitialized",
            "options": [
                "They are identical",
                "Uninitialized pointers are always NULL",
                "NULL is a known invalid value you can test for; uninitialized holds garbage you cannot detect",
                "NULL pointers can be safely dereferenced"
            ],
            "answer": 2,
            "why": "NULL is a defined sentinel you can check; an uninitialized pointer holds indeterminate garbage that may look valid.",
            "detail": "`p1` is reliably NULL, so `if (p1)` detects it. `p2` contains whatever was on the stack — possibly a plausible-looking address — so dereferencing it is undefined behavior that may crash or corrupt silently, and you cannot test for 'uninitialized'. They are not identical, uninitialized pointers are NOT guaranteed NULL, and dereferencing NULL crashes. Always initialize pointers, to NULL if nothing else."
        },
        {
            "q": "After `int a = 5; int *p = &a; *p = 10;`, what is a?",
            "code": "int a = 5;\nint *p = &a;\n*p = 10;",
            "options": [
                "5 — p only copied a's value",
                "The address of a",
                "Undefined",
                "10 — *p = 10 writes through the pointer to a's storage"
            ],
            "answer": 3,
            "why": "p holds a's address; *p = 10 stores 10 at that address, which is a itself, so a becomes 10.",
            "detail": "`&a` takes a's address, `*p = 10` writes 10 through the pointer to that exact storage — a and *p name the same memory, so a is 10. It is not 5 (the write did change a), not an address (a is an int), and not undefined (this is well-defined pointer use). This is the essence of pointers: they let one piece of code modify another's variables by address, the mechanism behind pass-by-reference in C."
        },
        {
            "q": "What does this print, and why?",
            "code": "int arr[3] = {10, 20, 30};\nint *p = arr;\nprintf(\"%d\\n\", *(p + 2));",
            "options": [
                "30 — p+2 advances by two ints to arr[2]",
                "20",
                "12 — p+2 adds 2 to the address",
                "A crash"
            ],
            "answer": 0,
            "why": "Pointer arithmetic scales by the element size, so p+2 points at arr[2], and *(p+2) is 30.",
            "detail": "Adding 2 to an int* advances by 2*sizeof(int) = 8 bytes, landing on arr[2] = 30. This is why *(p+2) equals arr[2]. It is not 20 (that is arr[1]), and crucially not '12' — pointer arithmetic does NOT add 2 to the raw address; it scales by the type size, which is the whole point of typed pointers. No crash since index 2 is in bounds. This scaling is exactly what makes arr[i] and *(arr+i) equivalent."
        },
        {
            "q": "What is wrong with returning this pointer?",
            "code": "int* make() {\n    int local = 42;\n    return &local;\n}",
            "options": [
                "It leaks memory",
                "It returns the address of a local that is destroyed when make returns — a dangling pointer",
                "Nothing; it returns 42 correctly",
                "It returns a copy of local"
            ],
            "answer": 1,
            "why": "local lives on make's stack frame, which is reclaimed on return, so the returned address is dangling.",
            "detail": "`local` exists only during make's execution; once make returns, its stack frame is gone and the address points at reclaimed memory, so any use is undefined behavior — a dangling pointer. It does not leak (nothing was malloc'd), does not safely return 42, and returns an address not a copy. To return data that outlives the function you must either return by value or allocate with malloc (and let the caller free). This is one of the most common C pointer bugs."
        },
        {
            "q": "What does `p` point to after this, and what is the danger?",
            "code": "char *p = malloc(10);\nfree(p);\n// p is not set to NULL",
            "options": [
                "p is automatically set to NULL by free",
                "p now points to new memory",
                "p still holds the freed address — a use-after-free waiting to happen (dangling)",
                "The memory is still safely usable"
            ],
            "answer": 2,
            "why": "free releases the memory but leaves p holding the old address, so any later use is a use-after-free bug.",
            "detail": "free returns the block to the allocator but does NOT change p, which still points at now-invalid memory. Using or freeing p again is undefined behavior (use-after-free / double-free), a serious and exploitable class of bug. free does not NULL the pointer for you, does not repoint it, and the memory is no longer yours. The defensive idiom is `free(p); p = NULL;` so a later accidental use hits a detectable NULL instead of silently corrupting the heap."
        },
        {
            "q": "What is printed?",
            "code": "int x = 5, y = 10;\nint *p = &x, *q = &y;\np = q;\n*p = 20;\nprintf(\"%d %d\\n\", x, y);",
            "options": [
                "20 10 — *p=20 changed x",
                "20 20",
                "5 10",
                "5 20 — p was repointed to y, so *p=20 changed y not x"
            ],
            "answer": 3,
            "why": "p = q makes p point at y; *p = 20 then writes to y, leaving x unchanged at 5.",
            "detail": "After `p = q`, p and q both point at y. `*p = 20` writes through p to y, so y becomes 20 while x stays 5. The '20 10' answer forgets that p was repointed away from x. '20 20' and '5 10' misread the aliasing. The subtlety is that assigning a pointer changes WHERE it points, not the value it pointed at — a distinction between `p = q` (repoint) and `*p = *q` (copy the value) that trips up beginners constantly."
        }
    ],
    "c-3": [
        {
            "q": "How is the string \"Dan\" actually stored in C?",
            "code": "char s[] = \"Dan\";",
            "options": [
                "As 4 bytes: 'D','a','n', and a terminating '\\0'",
                "As 3 bytes with no terminator",
                "As a length-prefixed array",
                "As a pointer to an int array"
            ],
            "answer": 0,
            "why": "C strings are null-terminated char arrays, so \"Dan\" needs 4 bytes including the '\\0'.",
            "detail": "A C string is a sequence of chars ended by a '\\0' byte that marks where it stops — \"Dan\" occupies 4 bytes. It is not 3 bytes (forgetting the terminator is a classic off-by-one that overflows buffers), not length-prefixed (that is Pascal strings or C++ std::string), and not an int array. Every string function (strlen, strcpy) relies on that '\\0'; a string without one runs off the end of its buffer."
        },
        {
            "q": "What does `sizeof(s)` give versus `strlen(s)` here?",
            "code": "char s[] = \"Dan\";\nprintf(\"%zu %zu\\n\", sizeof(s), strlen(s));",
            "options": [
                "3 3",
                "4 3 — sizeof counts the array bytes including '\\0'; strlen counts chars before '\\0'",
                "4 4",
                "3 4"
            ],
            "answer": 1,
            "why": "sizeof reports the full array size (4, with the terminator); strlen counts characters up to but not including '\\0' (3).",
            "detail": "sizeof(s) is the array's total storage, 4 bytes including the null. strlen walks until '\\0', counting 3 real characters. Confusing the two ('3 3' or '4 4') causes off-by-one bugs when allocating or copying. Note this only works because s is an ARRAY; if s were a char* parameter, sizeof would give the pointer size (8), not the string length — a critical distinction covered in the arrays lesson."
        },
        {
            "q": "What is the bug?",
            "code": "struct P { int x; int y; };\nstruct P a = {1, 2};\nstruct P *p = &a;\nprintf(\"%d\\n\", *p.y);",
            "options": [
                "Structs cannot hold two ints",
                "y must be accessed as p.y",
                "*p.y parses as *(p.y); it should be p->y or (*p).y",
                "Nothing is wrong"
            ],
            "answer": 2,
            "why": "The . operator binds tighter than *, so *p.y means *(p.y), which is wrong; use p->y for a pointer.",
            "detail": "Because member access `.` has higher precedence than dereference `*`, `*p.y` is parsed as `*(p.y)` — but p is a pointer with no member y, so it fails. Through a pointer you write `p->y` (the arrow), or `(*p).y` with explicit parentheses. Structs certainly hold multiple ints, and `p.y` is wrong because p is a pointer not a struct. The arrow operator exists precisely to make pointer-to-struct member access clean and unambiguous."
        },
        {
            "q": "How many bytes does this struct likely occupy, and why more than 5?",
            "code": "struct S { char c; int n; };\nprintf(\"%zu\\n\", sizeof(struct S));",
            "options": [
                "5 — 1 for char plus 4 for int",
                "4",
                "9",
                "8 — padding aligns the int to a 4-byte boundary after the 1-byte char"
            ],
            "answer": 3,
            "why": "The compiler inserts 3 padding bytes after the char so the int is 4-byte aligned, giving 8 total.",
            "detail": "Alignment rules require the int to start at a 4-byte boundary, so after the 1-byte char the compiler adds 3 padding bytes, then the 4-byte int — total 8. The naive '5' ignores padding, the commonest struct-size surprise. It is not 4 (that would drop the char) or 9. Reordering fields (int before char) can reduce padding, and understanding this matters for memory layout, binary file formats, and network protocols where exact byte positions count."
        },
        {
            "q": "What does this print?",
            "code": "char s[] = \"hello\";\ns[0] = 'H';\nprintf(\"%s\\n\", s);",
            "options": [
                "Hello — s is a modifiable array copy of the literal",
                "hello — string literals are immutable",
                "A crash",
                "H"
            ],
            "answer": 0,
            "why": "char s[] copies the literal into a writable array, so modifying s[0] works and prints Hello.",
            "detail": "`char s[] = \"hello\"` allocates a local array initialized from the literal, and arrays are writable, so s[0]='H' succeeds. Contrast `char *s = \"hello\"`, where s points at a read-only literal and writing through it is undefined behavior (often a crash) — that is the case the 'immutable/crash' answers describe, but it is not this one. This array-vs-pointer distinction for string literals is a subtle and important C gotcha."
        },
        {
            "q": "What is unsafe about this copy?",
            "code": "char dst[4];\nchar *src = \"hello\";\nstrcpy(dst, src);",
            "options": [
                "strcpy is always safe",
                "src is 6 bytes with '\\0' but dst holds only 4 — strcpy overflows the buffer",
                "dst must be a pointer",
                "Nothing is wrong"
            ],
            "answer": 1,
            "why": "\"hello\" plus its terminator is 6 bytes; copying into a 4-byte buffer overruns it — a buffer overflow.",
            "detail": "strcpy copies until the source's '\\0', writing 6 bytes into a 4-byte array and corrupting adjacent memory (a buffer overflow, historically a major security vulnerability). strcpy is NOT safe when the destination is too small — that is its central danger. dst is correctly an array. The fix is to size the buffer for the string plus terminator, or use bounded copies like strncpy/snprintf that respect the destination size. This overflow class motivates much of memory-safety practice."
        }
    ],
    "c-4": [
        {
            "q": "What must you eventually do with the result of `malloc`, and what if you do not?",
            "code": "int *a = malloc(100 * sizeof(int));",
            "options": [
                "Nothing; the OS handles it during the program",
                "Call delete a;",
                "Call free(a); forgetting to causes a memory leak",
                "Set a = NULL, which frees it"
            ],
            "answer": 2,
            "why": "Heap memory from malloc must be released with free, or it leaks for the program's lifetime.",
            "detail": "malloc reserves heap memory that stays allocated until you free it; never freeing means a leak that grows over a program's run. `delete` is C++, not C. Setting a = NULL does NOT free — it just loses the only pointer to the block, guaranteeing the leak. While the OS reclaims everything at process exit, long-running programs must free to avoid exhausting memory. Every malloc should have a matching free on all paths."
        },
        {
            "q": "What does `x & 1` test?",
            "code": "if (x & 1) { /* ... */ }",
            "options": [
                "Whether x equals 1",
                "Whether x is positive",
                "Whether x is nonzero",
                "Whether x is odd (its lowest bit is set)"
            ],
            "answer": 3,
            "why": "Bitwise AND with 1 isolates the least significant bit, which is 1 exactly when x is odd.",
            "detail": "The lowest bit of a binary number determines parity: it is 1 for odd numbers, 0 for even, so `x & 1` is true iff x is odd. It does not test equality with 1 (that is `x == 1`), positivity, or general nonzero-ness. This is a faster, idiomatic alternative to `x % 2 == 1` and a first taste of using bitwise operations to inspect individual bits, central to low-level and systems programming."
        },
        {
            "q": "What does `x << 3` compute, and why?",
            "code": "int x = 5;\nprintf(\"%d\\n\", x << 3);",
            "options": [
                "40 — left-shifting by 3 multiplies by 2^3 = 8",
                "15 — it multiplies by 3",
                "8",
                "125"
            ],
            "answer": 0,
            "why": "A left shift by n multiplies by 2^n, so 5 << 3 is 5 * 8 = 40.",
            "detail": "Shifting bits left by 3 positions is multiplication by 2^3 = 8, giving 40. It does not multiply by 3 (that confuses the shift amount with a factor), is not 8, and not 125. Shifts are fast power-of-two multiply/divide operations the CPU does cheaply, and recognizing `<< n` as *2^n (and `>> n` as /2^n for unsigned) is essential for reading low-level and optimized code, as well as for manipulating packed bit fields."
        },
        {
            "q": "Predict the output.",
            "code": "int *a = malloc(3 * sizeof(int));\nfor (int i = 0; i < 3; i++) a[i] = i * 10;\nprintf(\"%d\\n\", a[1]);\nfree(a);",
            "options": [
                "0",
                "10",
                "20",
                "Garbage — malloc does not initialize"
            ],
            "answer": 1,
            "why": "The loop sets a[1] = 1 * 10 = 10 before it is printed, so the value is defined.",
            "detail": "Although malloc returns uninitialized memory (unlike calloc, which zeros it), the loop explicitly writes a[i] = i*10, so a[1] is 10 by the time it prints. The 'garbage' answer would be correct if the code read a[1] BEFORE writing it, which is the real malloc-is-uninitialized trap — but here it is initialized first. Not 0 (that is a[0]) or 20 (that is a[2]). Knowing malloc leaves garbage until you write is vital, but so is noticing when the code does initialize."
        },
        {
            "q": "What is the double-free bug's consequence here?",
            "code": "int *p = malloc(8);\nfree(p);\nfree(p);",
            "options": [
                "It is harmless and just a no-op",
                "It reallocates the memory",
                "Undefined behavior — freeing the same block twice can corrupt the heap",
                "A compile error"
            ],
            "answer": 2,
            "why": "Calling free twice on the same pointer is undefined behavior that commonly corrupts allocator metadata.",
            "detail": "After the first free, the block is returned to the allocator; freeing it again corrupts the heap's internal bookkeeping, which is undefined behavior and a well-known exploitable vulnerability class. It is not a harmless no-op, does not reallocate, and compiles fine (the compiler cannot track this). The defense is `free(p); p = NULL;` because free(NULL) IS a safe no-op, so a second free through the nulled pointer does nothing harmful. Double-free and use-after-free are the heap analogues of the stack bugs seen elsewhere."
        },
        {
            "q": "Why use `calloc(n, sizeof(int))` instead of `malloc(n * sizeof(int))`?",
            "code": "",
            "options": [
                "calloc is faster in all cases",
                "calloc does not need to be freed",
                "calloc returns stack memory",
                "calloc zero-initializes the memory and guards against multiplication overflow"
            ],
            "answer": 3,
            "why": "calloc zeros the allocated bytes and internally checks n*size for overflow, unlike a raw malloc multiply.",
            "detail": "calloc gives you zero-initialized memory (handy when you need a clean start) and computes n*size safely, rejecting an overflow that a manual `n * sizeof(int)` could silently wrap into a too-small allocation — a real security concern. It is not universally faster (zeroing has a cost, though the OS often provides zeroed pages cheaply), it still must be freed like any heap memory, and it returns heap not stack memory. Choosing calloc vs malloc is about initialization and overflow safety."
        }
    ],
    "c-5": [
        {
            "q": "When you pass an array to a C function, what does the function actually receive?",
            "code": "void f(int arr[]) { /* ... */ }",
            "options": [
                "A pointer to the first element — the array 'decays' to a pointer",
                "A full copy of the array",
                "The array by reference with its size",
                "Nothing usable"
            ],
            "answer": 0,
            "why": "Array parameters decay to a pointer to the first element; the size information is lost.",
            "detail": "In a function parameter, `int arr[]` is exactly `int *arr` — the array decays to a pointer, so the function gets an address, not a copy, and no length. This is why you almost always pass the size as a separate parameter. It is not a copy (that would be expensive and C does not do it), and the size is NOT carried along, which is the crux. Inside f, sizeof(arr) gives the pointer size, not the array size — a frequent bug."
        },
        {
            "q": "What is `arr[i]` exactly equivalent to?",
            "code": "",
            "options": [
                "*(arr) + i",
                "*(arr + i)",
                "arr + i",
                "&arr[i]"
            ],
            "answer": 1,
            "why": "Subscripting is defined as *(arr + i): add i (scaled) to the base pointer, then dereference.",
            "detail": "By definition `arr[i]` means `*(arr + i)` — pointer arithmetic to element i, then a dereference. `*(arr) + i` dereferences first then adds i (wrong: that is arr[0] + i). `arr + i` is the address without dereferencing. `&arr[i]` is the address of element i. A curious consequence: since addition commutes, `arr[i]` equals `i[arr]`, which is legal if bizarre C. This identity is why arrays and pointers are so intertwined in the language."
        },
        {
            "q": "What does this print, and why is the sizeof surprising?",
            "code": "void f(int a[]) { printf(\"%zu\\n\", sizeof(a)); }\n// called as f(myArrayOf10);",
            "options": [
                "40 — ten ints",
                "10",
                "8 — inside f, a is a pointer, so sizeof is the pointer size, not 40",
                "4"
            ],
            "answer": 2,
            "why": "The array parameter decayed to a pointer, so sizeof(a) is 8 (the pointer), not the original array's 40 bytes.",
            "detail": "Because array parameters are really pointers, sizeof(a) inside f measures the pointer (8 bytes on 64-bit), not the caller's 10-int array (40 bytes). Expecting 40 or 10 is the classic decay bug — the size is gone the moment the array is passed. This is precisely why functions take an explicit length parameter. In the CALLER's scope, where myArray is a true array, sizeof would correctly give 40; the information is lost only across the call."
        },
        {
            "q": "Why does this loop read out of bounds?",
            "code": "int a[5];\nfor (int i = 0; i <= 5; i++) a[i] = 0;",
            "options": [
                "Arrays start at index 1",
                "It is fine",
                "It skips a[0]",
                "Valid indices are 0..4; i <= 5 writes a[5], one past the end"
            ],
            "answer": 3,
            "why": "A 5-element array has indices 0 through 4; the <= condition writes a[5], an out-of-bounds access.",
            "detail": "Indices run 0..n-1, so a[5] does not exist — the `<=` should be `<`. Writing a[5] is undefined behavior that corrupts whatever sits after the array (often other locals or the stack). Arrays do not start at 1, the loop is not fine, and it does not skip a[0]. This off-by-one from `<=` versus `<` is one of the most common C bugs and, when it overwrites a return address, a security vulnerability."
        },
        {
            "q": "What does `int (*p)[5]` declare, and how does it differ from `int *p[5]`?",
            "code": "int (*p)[5];",
            "options": [
                "A pointer to an array of 5 ints; without parens int *p[5] is an array of 5 pointers",
                "They are the same",
                "An array of 5 ints",
                "A function returning int*"
            ],
            "answer": 0,
            "why": "Parentheses bind p to the pointer first: pointer-to-array-of-5; without them it is array-of-5-pointers.",
            "detail": "`int (*p)[5]` is a pointer to an array of 5 ints (used for 2D array rows). `int *p[5]` (no parens) is an array of 5 int-pointers — precedence makes [] bind before *. They are emphatically not the same, and the parentheses are what change the meaning. Reading C declarations right-to-left with precedence in mind is a genuine skill; this pointer-to-array vs array-of-pointers distinction is a classic interview and debugging trap."
        },
        {
            "q": "What is n, and why must the function take it?",
            "code": "int sum(int *a, int n) {\n    int s = 0;\n    for (int i = 0; i < n; i++) s += a[i];\n    return s;\n}",
            "options": [
                "The array's first element",
                "The element count — the function cannot recover the array's length from the pointer alone",
                "A pointer to the size",
                "Optional; sizeof could find it"
            ],
            "answer": 1,
            "why": "Since the array decayed to a pointer, its length is lost, so the caller must pass the count n.",
            "detail": "n is the number of elements, which the function needs because a is just a pointer with no length attached — sizeof(a) would give 8, not the array size. It is not the first element or a size pointer, and sizeof canNOT find it here (that is the whole reason n exists). This 'pass the pointer and the length together' convention is pervasive in C precisely because of array-to-pointer decay, and forgetting n or getting it wrong causes out-of-bounds reads."
        }
    ],
    "c-6": [
        {
            "q": "What does a header (.h) file normally contain?",
            "code": "",
            "options": [
                "The full function implementations",
                "Compiled machine code",
                "Declarations: function prototypes, struct/type definitions, and macros — the interface",
                "Only comments"
            ],
            "answer": 2,
            "why": "Headers hold declarations (the interface) so other files know how to call code defined elsewhere.",
            "detail": "A header declares what exists — prototypes, types, macros — so any .c file that includes it can use those functions and types, while the definitions live in a .c file. It does not hold implementations (that would cause multiple-definition errors when included in several files), is not machine code, and is more than comments. This separation of interface (.h) from implementation (.c) is how C programs split across files and how libraries expose their API."
        },
        {
            "q": "What does `#include \"utils.h\"` literally do?",
            "code": "",
            "options": [
                "It links the compiled utils object file",
                "It imports utils as a module at runtime",
                "It runs utils.h",
                "The preprocessor pastes the entire text of utils.h in place before compilation"
            ],
            "answer": 3,
            "why": "#include is textual: the preprocessor replaces the directive with the full contents of the named file.",
            "detail": "#include is a pure text-substitution done by the preprocessor before the compiler proper runs — it literally copies the file's text in. It does not link objects (that is the linker's separate job), is not a runtime module import (C has no such thing; that is Python/Java), and does not execute the header. Understanding #include as textual paste explains include guards (to avoid pasting the same declarations twice) and why headers hold declarations, not definitions."
        },
        {
            "q": "What is the purpose of this pattern in a header?",
            "code": "#ifndef UTILS_H\n#define UTILS_H\n/* declarations */\n#endif",
            "options": [
                "An include guard — prevents the header's contents being pasted twice in one translation unit",
                "It makes the header run faster",
                "It hides the header from the linker",
                "It defines a function called UTILS_H"
            ],
            "answer": 0,
            "why": "The guard ensures that if the header is included multiple times, its body is processed only once.",
            "detail": "Because #include is textual, a header pulled in twice (directly and transitively) would paste its declarations twice, causing redefinition errors. The #ifndef/#define/#endif guard makes the body compile only the first time — on later includes UTILS_H is already defined, so the block is skipped. It is not about speed, linking, or defining a function; UTILS_H is just a unique marker macro. Every real header uses an include guard (or #pragma once)."
        },
        {
            "q": "Why does linking fail here even though it compiles?",
            "code": "// main.c calls helper(), declared in utils.h\n// but you compile only: gcc main.c -o prog",
            "options": [
                "helper was never declared",
                "utils.c (the definition of helper) was never compiled or linked, so the symbol is undefined",
                "main.c has a syntax error",
                "Headers cannot declare functions"
            ],
            "answer": 1,
            "why": "The declaration lets main.c compile, but the definition in utils.c must also be built and linked, or the symbol is missing.",
            "detail": "The header's declaration satisfies the COMPILER (it knows helper's signature), so main.c compiles, but at LINK time the actual code for helper — living in utils.c — is absent because you never compiled it in. The fix is `gcc main.c utils.c -o prog`. helper WAS declared (in the header), there is no syntax error, and headers do declare functions. This 'undefined reference' error is the classic sign of a missing source file or library at the link step, distinct from a compile error."
        },
        {
            "q": "What does this macro expand to, and what is the trap?",
            "code": "#define SQ(x) x * x\nint r = SQ(2 + 3);",
            "options": [
                "25 correctly",
                "A compile error",
                "2 + 3 * 2 + 3 = 11, not 25 — no parentheses around x",
                "6"
            ],
            "answer": 2,
            "why": "Textual substitution gives 2 + 3 * 2 + 3; precedence makes it 11, not the intended (2+3)*(2+3)=25.",
            "detail": "Macros are pasted literally, so SQ(2 + 3) becomes 2 + 3 * 2 + 3, and multiplication binds tighter, yielding 11. The intended 25 requires the macro to be written `#define SQ(x) ((x) * (x))` with parentheses around each x and the whole expression. This is the canonical macro pitfall: because the preprocessor does text substitution, not evaluation, you must parenthesize defensively. It compiles and runs — silently wrong — which is why function-like macros are dangerous and inline functions are often preferred."
        },
        {
            "q": "What does the `static` keyword do to a function at file scope?",
            "code": "static int helper(void) { return 1; }",
            "options": [
                "Makes it run once",
                "Allocates it on the stack",
                "Makes it a global visible everywhere",
                "Limits the function's visibility to its own .c file (internal linkage)"
            ],
            "answer": 3,
            "why": "static at file scope gives internal linkage, so the function is private to that translation unit.",
            "detail": "A file-scope `static` function is visible only within its own .c file, preventing name clashes with functions of the same name elsewhere and keeping the interface clean — the opposite of a global. It does not mean 'run once' (that is a different concept), and functions are not stack-allocated. Note static means something different on a LOCAL variable (persistent storage across calls), which is a common source of confusion. Using static for file-private helpers is standard C practice for encapsulation."
        }
    ]
}
