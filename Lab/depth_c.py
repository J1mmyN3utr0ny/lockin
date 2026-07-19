# depth_c.py — extended teaching content for the c track.
# Auto-attached by depth.py. One entry per lesson id.

DEPTH = {

    "c-1": {
        "title_check": "Compile, run, and types",
        "sections": [
            {"h": "WHAT COMPILING ACTUALLY PRODUCES", "body": r"""When you run gcc hello.c -o hello.exe you are not asking gcc to run your code - you are asking it to translate C source text into a binary image that the operating system's loader knows how to turn into a process later. Think of the finished executable as a blueprint for a future process, not a program that is alive yet. Inside that blueprint, memory is already divided into regions before a single instruction executes: a .text region holding your compiled machine code (read-only, executable), a .data region holding initialized globals, a .bss region reserved for zero-initialized globals (not even stored in the file - just a size the loader zero-fills at load time), and space that will later become the stack and heap once the process actually runs. On Windows this blueprint is a PE (Portable Executable) file; on Linux the same idea is called ELF - different container formats, same underlying concept. When you double-click hello.exe, Windows' loader reads this blueprint, maps .text/.data/.bss into a fresh virtual address space, sets up an initial stack, and jumps to an entry point that eventually calls your main. Nothing about compiling involves execution - that is the mental-model shift from Python, where the interpreter reads and runs source in one breath, with no separate blueprint stage."""},

            {"h": "VARIADIC PRINTF, DEFAULT PROMOTION, AND FORMAT-STRING UB", "body": r"""printf is a variadic function - its prototype is int printf(const char *fmt, ...) - and the ... means the compiler cannot check that your arguments match your format specifiers. Worse, arguments passed through ... undergo "default argument promotion": any char or short is promoted to int, and any float is promoted to double, before it is ever pushed or placed in a register. This is why %d works whether you pass a char or an int - by the time printf sees it, it is already an int-sized value on the argument path. But promotion only fixes width, not interpretation. If you pass an int where printf expects a %s, printf will read the bits as if they were a pointer and try to dereference garbage - undefined behavior, often a crash. If you pass a long on a 64-bit build where %d expects a 4-byte int, the extra bytes are simply read from whatever register or stack slot the ABI parks them in, producing garbage output rather than a compile error, because C's variadic mechanism has zero type information at the call site. The compiler's -Wformat warnings are the only real defense; the language itself will not stop you."""},

            {"h": "WORKED EXAMPLE: A TYPE-AWARE DEBUG PRINT UTILITY", "body": r"""Suppose you are debugging a struct-heavy program and want one line that prints a value along with its raw hex bytes, its decimal form, and its size - the kind of utility every low-level programmer eventually writes.

    #include <stdio.h>
    void dump_int(const char *name, int v) {
        printf("%-8s dec=%-6d hex=0x%08x size=%zubytes\n",
               name, v, (unsigned)v, sizeof(v));
    }
    int main(void) {
        int a = -1;
        dump_int("a", a);
        return 0;
    }

Reading this line by line: %-8s left-justifies the name in an 8-char field; %-6d does the same for the decimal value; %08x zero-pads the hex to 8 digits, and casting v to unsigned before printing it as hex avoids sign-extension surprises when v is negative (a signed -1 passed to %x on some libc builds still prints as all-F's because %x reinterprets the same bit pattern, but the explicit cast makes the intent unambiguous instead of relying on implementation behavior). %zu is the correct, portable specifier for a size_t returned by sizeof - using %d here would be undefined behavior on any platform where size_t is wider than int."""},

            {"h": "FAILURE MODES: WIDTH AND SIGN MISMATCHES THAT CORRUPT OUTPUT", "body": r"""Three format-string bugs show up constantly in real code. First, printing a size_t (unsigned, often 8 bytes on x64) with %d (which expects a signed 4-byte int): on a 64-bit ABI where the value simply sits in a full register, %d reads only the low 32 bits, so a size_t of 5000000000 can print as a small or even negative number. Second, printing a pointer with %d or %x instead of %p: a 64-bit address truncated to 32 bits silently loses its top half, which looks like the program is reading the wrong memory when actually it is only your printf call that is lying about what address it saw. Third, mixing signed and unsigned in the SAME expression - if (v < 0 && v > some_size_t) - the signed v is implicitly converted to unsigned for the comparison, so a genuinely negative v becomes a huge positive number and the "less than zero" branch never fires. None of these are syntax errors; they compile cleanly and produce wrong answers only at runtime, which is exactly why format-string and signedness bugs survive in shipped code for years."""},

            {"h": "HOW A PROFESSIONAL INSPECTS THE BUILD ARTIFACTS", "body": r"""A professional does not trust that gcc did what they think - they check the artifacts. gcc hello.c -S -o hello.s stops after compiling to assembly, letting you read the exact instructions your C produced without ever calling the assembler or linker; gcc hello.c -c -o hello.o stops after assembling, producing an object file with unresolved symbol references you can inspect with objdump -d hello.o (or, since this environment is MSYS2 ucrt64, the same objdump ships alongside gcc, so the commands are identical to Linux). To inspect the finished hello.exe, dumpbin /headers hello.exe (from a Visual Studio developer prompt) or objdump -x hello.exe from the MSYS2 shell shows you the PE header, the section table (.text, .data, .rdata), and the import table listing which DLL functions (like printf's underlying ucrtbase.dll routines) the loader must resolve at startup. This workflow - compile partially, inspect the intermediate artifact, only then trust the next stage - is the same discipline used when reverse engineering an unfamiliar binary: never assume, always look."""},

            {"h": "WHERE THIS IS GOING: TYPES ARE A COMPILE-TIME FICTION", "body": r"""Every type you write in C - int, char, double, struct Point - exists only for the compiler's bookkeeping. It uses your declared types to decide how many bytes to reserve, how to interpret the bits during arithmetic, and which instructions to emit (an int add becomes add or imul; a double add becomes addsd using an XMM register instead of a general-purpose one). But once the compiler finishes, all of that information is gone. The resulting machine code manipulates raw bytes in registers and memory with zero notion of "this is an int" versus "this is a pointer" versus "this is a char" - a disassembler sees only mov, add, and register names like eax or rax, and must guess a value's meaning from how surrounding instructions use it. This is precisely why the asm track spends so much time on register widths (eax vs rax vs al) and instruction selection: those are the only fossils left of your C types once compilation is done, and learning to read them is learning to reconstruct a program's data model from nothing but its actions."""},
        ],
    },

    "c-2": {
        "title_check": "Pointers",
        "sections": [
            {"h": "A POINTER IS A NUMBER WITH COMPILE-TIME TYPE INFORMATION", "body": r"""At runtime, a pointer is nothing more than an unsigned integer holding a memory address - on this x64 environment, a 64-bit value that fits in one register. int *p and char *p, if they held the same address, would contain the exact same bits. What differs is entirely compile-time: the compiler remembers that p "is a pointer to int" so it knows *p should read 4 bytes and interpret them as a signed integer, that p + 1 should add 4 (sizeof(int)) to the address, and that assigning a double* to an int* should be an error or at least a warning. None of that bookkeeping survives into the compiled instructions - a mov [rax], 5 that writes through an int* looks identical to one writing through a different 4-byte type. This is why casting a pointer, e.g. (double *)p, is "free" at runtime (it emits no instructions at all) yet completely changes how subsequent code interprets the bytes at that address - the danger of C's pointer casts is exactly that the machine performs no check, only the compiler's now-vanished type system did."""},

            {"h": "LEVELS OF INDIRECTION: DOUBLE POINTERS AND CONST CORRECTNESS", "body": r"""A pointer to a pointer, int **pp, is the tool for when a function must modify the caller's pointer variable itself, not just the thing it points to - ordinary pass-by-value means a plain int *p parameter can change what p points to inside the function, but that change is lost the moment the function returns, because the caller's own pointer variable was never touched. To let a function reseat the caller's pointer (point it somewhere new, or realloc it), you must pass &p, i.e. an int **, and the function writes through it: *pp = malloc(...). Separately, const correctness has three distinct meanings that read left to right: const int *p means "p can change, but you cannot write through it to change the int"; int *const p means "you cannot reseat p, but you can write through it"; and const int *const p locks both. The common beginner error is misreading const int *p as "p itself is constant" - it is not; the object p points to is what is protected."""},

            {"h": "WORKED EXAMPLE: GROWING A CALLER'S ARRAY THROUGH A DOUBLE POINTER", "body": r"""    #include <stdlib.h>
    int grow(int **arr, int old_n, int new_n) {
        int *tmp = realloc(*arr, new_n * sizeof(int));
        if (!tmp) return 0;          // original *arr still valid
        for (int i = old_n; i < new_n; i++) tmp[i] = 0;
        *arr = tmp;                  // write through pp to caller
        return 1;
    }
    int main(void) {
        int *data = malloc(3 * sizeof(int));
        data[0] = 1; data[1] = 2; data[2] = 3;
        if (grow(&data, 3, 6)) {
            // data now points at a (possibly new) 6-int block
        }
        free(data);
        return 0;
    }

The function takes int **arr precisely because it may need to replace the caller's pointer with a new address from realloc. Note the defensive pattern: realloc's result is captured in a local tmp first, and *arr is only overwritten after confirming tmp is non-NULL - if realloc fails and returns NULL, the original allocation in *arr is still valid and would otherwise leak if you had written *arr = realloc(*arr, ...) directly."""},

            {"h": "FAILURE MODES: DANGLING, WILD, AND ALIASING POINTER BUGS", "body": r"""A dangling pointer points at memory that used to be valid but is not anymore - the classic case is returning the address of a local variable: int *bad(void) { int x = 5; return &x; } - x's storage is the function's stack frame, which is reclaimed the instant the function returns, so the caller receives a pointer to memory that is about to be overwritten by the next function call. A wild pointer is one that was never initialized at all - int *p; *p = 5; - it holds whatever garbage bits happened to be in that stack slot, which might be a small number interpreted as an address, and writing through it corrupts essentially random memory, sometimes silently. Use-after-free is the heap version of dangling: free(p) does not erase p's value, so *p still "works" syntactically while reading or writing memory the allocator may have already handed to someone else. Strict aliasing UB is subtler: the compiler is allowed to assume a float* and an int* never point to the same memory unless you use a union or char*, so "reinterpreting" bytes through mismatched pointer types can be legally miscompiled under optimization."""},

            {"h": "HOW A PROFESSIONAL CHASES POINTERS IN A DEBUGGER", "body": r"""In gdb, p ptr prints a pointer's raw address; p *ptr dereferences it once to show the pointed-to value; for a linked structure, p *ptr->next->next repeats the dereference to walk the chain by hand. x/4gx ptr examines memory directly - 4 giant (8-byte) words in hex starting at the address ptr holds - which is how you inspect what a pointer refers to without knowing its C type at all, exactly the situation a reverse engineer is in when working from a stripped binary. Because Windows and most modern operating systems randomize the load address of each region on every run (ASLR - Address Space Layout Randomization), the actual numeric address you see changes between runs; professionals instead reason about offsets - "this pointer is always 0x20 bytes after that one" - which stay constant regardless of where the process is loaded. Exploit developers exploit this same fact deliberately: given one "leaked" pointer value at runtime (from a crash log or an info-leak bug), they compute every other address they need by adding a fixed, previously-determined offset, since ASLR moves the whole module together, not each byte independently."""},

            {"h": "WHERE THIS IS GOING: POINTERS ARE WHAT REGISTERS HOLD", "body": r"""Every pointer operation you do in C has a one-to-one flavor in assembly. &x, "the address of x," compiles to a lea (load effective address) instruction - lea computes an address without touching memory at all, which is exactly what &x means: give me the location, not the contents. *p, dereferencing, compiles to a mov that uses a register as a memory operand, like mov eax, [rbx] - "read four bytes starting at the address currently in rbx." Pointer arithmetic, p + 1, becomes an add on the register holding the address, scaled by the pointed-to type's size (the compiler bakes that scaling in as a constant, since the CPU has no idea what "int" means). This means that once you can read x86 addressing modes fluently (the asm track's addressing-modes lesson covers exactly this), you can look at raw disassembly and immediately recognize "this is a pointer being dereferenced" versus "this is an address being computed," which is the single most load-bearing skill in reverse engineering unfamiliar C binaries - the source's pointer types are gone, but their behavior is still visible in which instruction touches memory and which only computes."""},
        ],
    },

    "c-3": {
        "title_check": "Structs & strings",
        "sections": [
            {"h": "A STRUCT IS A CONTIGUOUS BLOB; ASSIGNMENT COPIES THE WHOLE THING", "body": r"""Unlike in Python or Java, a C struct variable IS its data, laid out contiguously in memory - there is no hidden object header, no reference, just the fields back to back (plus possible padding, covered by the "struct packing" material you've already seen). This has a consequence beginners routinely miss: struct assignment, struct b = a;, performs a full field-by-field memory copy of the entire blob, not a reference copy. If Student a is 40 bytes, struct Student b = a; copies all 40 bytes - change b.grade afterward and a.grade is untouched, because they are now two entirely separate blobs. This is usually what you want for small structs, but becomes expensive and dangerous once a struct contains a pointer field: copying the struct copies the POINTER (the address), not what it points to, so a and b now both contain a pointer to the SAME heap block - a shallow copy. Passing a struct by value to a function copies it onto the callee's stack frame in exactly the same way, which is why large structs are usually passed by pointer instead."""},

            {"h": "-> IS SUGAR, AND ARRAYS OF STRUCTS ARE REPEATED BLOBS", "body": r"""ptr->field is defined to mean exactly (*ptr).field - dereference the pointer to get the struct, then access the field - the arrow exists purely for readability since (*ptr).field with its parentheses is awkward to type and read at scale. Both forms compile to the identical instruction sequence: compute the struct's base address (already in ptr), add the field's fixed byte offset, then load or store there. An array of structs, struct Student roster[3];, is laid out as three copies of the blob back to back with no gaps between elements (only internal padding within each struct, not between them) - so roster[i] is computed as base + i * sizeof(struct Student), the same base+index*scale idea as an int array, just with a larger, compiler-computed scale instead of 4 or 8. This is why you cannot compare two structs with ==: the compiler has no built-in notion of "structural equality" for an arbitrary blob (padding bytes may hold garbage that differs between two otherwise-equal structs), so you must write your own field-by-field comparison or use memcmp with full awareness of padding."""},

            {"h": "WORKED EXAMPLE: SORTING STUDENTS WITH A GENERIC COMPARATOR", "body": r"""    #include <stdlib.h>
    #include <string.h>
    struct Student { char name[32]; int grade; };

    int cmp_by_grade(const void *a, const void *b) {
        const struct Student *sa = a, *sb = b;
        return sa->grade - sb->grade;   // ascending
    }
    int main(void) {
        struct Student roster[3] = {
            {"Dan", 88}, {"Avi", 95}, {"Noa", 72}
        };
        qsort(roster, 3, sizeof(struct Student), cmp_by_grade);
        for (int i = 0; i < 3; i++)
            printf("%s: %d\n", roster[i].name, roster[i].grade);
        return 0;
    }

qsort is generic - it knows nothing about struct Student - so it hands your comparator two void * pointers into the array (each pointing at the start of one element's blob) and relies on sizeof(struct Student) to know how far apart elements are when swapping them internally. Inside the comparator you cast back to the real type before touching ->grade; this cast-through-void* pattern is exactly how C fakes generic (type-independent) functions decades before templates or generics existed in the language."""},

            {"h": "FAILURE MODES: SHALLOW COPIES, DOUBLE FREES, strncpy'S TERMINATOR", "body": r"""If a struct holds a pointer to heap memory, struct Buffer { char *data; } and you do struct Buffer b = a;, both a.data and b.data now point at the same block. Free it through a, and b.data is left dangling; free it again through b later and you have a double free - heap corruption that can be steered into arbitrary code execution by an attacker who controls allocation timing. The fix is a deep copy: malloc a new block for b.data and memcpy the contents, or design an explicit copy function. Separately, strncpy(dest, src, n) is infamous for a trap: if src is n or more characters long, strncpy copies exactly n bytes and does NOT null-terminate dest - unlike strcpy, which always terminates but has no length limit at all. Programmers "fixing" a strcpy overflow by switching to strncpy(dest, src, sizeof(dest)) often introduce a silent missing-terminator bug instead, and the next strlen or printf("%s", dest) reads past the buffer until it happens to find a zero byte somewhere in adjacent memory - a real, still-common source of information disclosure bugs."""},

            {"h": "HOW A REVERSE ENGINEER RECOVERS A STRUCT FROM DISASSEMBLY", "body": r"""Source-level struct definitions do not exist in a compiled binary - a disassembler only sees a base pointer (in some register) with a series of fixed-offset accesses: mov eax, [rbx+0x20], mov [rbx+0x24], ecx, and so on. A reverse engineer's job, when recovering a struct layout from a stripped binary, is to collect every distinct offset touched relative to the same base pointer across the function, note each access's size (4-byte mov implies an int or similar; 1-byte implies a char; 8-byte implies a pointer or a long), and infer field boundaries and likely types from that pattern - tools like IDA Pro and Ghidra have a "structure" view built exactly for this reconstruction process, letting you name offset+0x20 as "grade" once you're confident, after which every reference in the function updates to show ->grade instead of a bare hex offset. Gaps between offsets that don't align with any observed access size are usually padding, inferred the same way you'd predict it from the alignment rules you already know from the struct-packing material - the disassembly literally shows you the padding as "dead space" no instruction ever touches."""},

            {"h": "WHERE THIS IS GOING: STRUCT FIELDS AS EXPLOITATION TARGETS", "body": r"""Because a struct is just contiguous bytes with no runtime boundary checking between fields, an overflow in one array field can silently corrupt a NEIGHBORING field in the same struct - if struct Account { char name[16]; int balance; }; and you strcpy an attacker-controlled 30-byte name into it, the extra bytes don't stop at name's boundary, they keep writing straight into balance (and beyond, into whatever comes after the struct in memory). This is the C-level ancestor of a huge class of real vulnerabilities: overflowing a fixed-size buffer field to corrupt an adjacent function pointer, a size field, or - in C++ - a vtable pointer that the program will later use to decide what code to jump to, turning a simple buffer bug into arbitrary code execution. It's also why struct field ORDER matters defensively: putting a length-checked or non-attacker-controlled field directly after a buffer, rather than something security-critical, is a deliberate (if fragile) mitigation you'll see discussed in real hardening guides, and it's exactly why this lesson's earlier "no bounds checking, ever" point about C strings deserves to be taken seriously rather than treated as trivia."""},
        ],
    },

    "c-4": {
        "title_check": "Dynamic memory & bits",
        "sections": [
            {"h": "WHAT malloc REALLY RETURNS: HIDDEN HEAP METADATA", "body": r"""malloc(n) does not simply carve out exactly n bytes and hand you the start of them - the heap allocator (on Windows, the UCRT heap; the concept is identical under Linux's glibc ptmalloc) actually reserves a slightly larger block: your n bytes PLUS a hidden header immediately before the pointer you receive, typically storing at least the chunk's size and a couple of bookkeeping bits (such as whether the previous chunk is in use). The pointer malloc returns points just AFTER that header, so free(p) works by walking backward from p to find the header again, reading the size from it, and returning the whole chunk (header included) to the allocator's free list. This is precisely why writing even one byte before the pointer malloc gave you - a common off-by-one when computing an offset - can corrupt that header rather than "wasted padding," and why free() needs no length argument: the size was never yours to forget, it was recorded by the allocator the moment you called malloc, in memory you never see or touch directly."""},

            {"h": "realloc, calloc, AND THE ARITHMETIC THAT SIZES AN ALLOCATION", "body": r"""calloc(n, size) is not just "malloc plus zeroing" for convenience - it also multiplies n by size internally with an overflow check the naive malloc(n * size) does not get for free; if n * size would overflow a size_t, calloc detects it and returns NULL, whereas malloc(n * size) silently wraps around to a tiny number, succeeds, and hands back a buffer far smaller than the caller assumed - a classic integer-overflow-to-heap-overflow bug. realloc(p, new_size) may return the SAME address (if there's room to grow in place) or a completely DIFFERENT address (if the allocator must move your data elsewhere) - you must always capture its return value in a new variable rather than overwriting p directly, because if realloc fails and returns NULL, doing p = realloc(p, ...) leaks the original block and loses your only pointer to it. A frequent, subtler bug: malloc(strlen(s)) to hold a copy of a string forgets the trailing null terminator, which strlen deliberately does not count, so the copy is one byte too small before you've written anything into it."""},

            {"h": "WORKED EXAMPLE: A GROWABLE INT ARRAY WITH realloc", "body": r"""    #include <stdlib.h>
    typedef struct { int *data; int len, cap; } IntVec;

    void push(IntVec *v, int x) {
        if (v->len == v->cap) {
            int newcap = v->cap ? v->cap * 2 : 4;
            int *tmp = realloc(v->data, newcap * sizeof(int));
            if (!tmp) return;          // v->data still valid, growth aborted
            v->data = tmp;
            v->cap = newcap;
        }
        v->data[v->len++] = x;
    }
    int main(void) {
        IntVec v = {0};
        for (int i = 0; i < 10; i++) push(&v, i * i);
        free(v.data);
        return 0;
    }

Doubling capacity (v->cap * 2) rather than growing by a fixed amount each time is the standard strategy real dynamic arrays (C++'s std::vector, Python's list) use internally - it keeps the total cost of n pushes proportional to n rather than n squared, because reallocations become exponentially rarer as the array grows, even though each one copies more data."""},

            {"h": "FAILURE MODES: DOUBLE FREE, UAF, AND OVERFLOW IN SIZE MATH", "body": r"""A double free - calling free() twice on the same pointer without an intervening malloc - corrupts the allocator's internal free list, because the allocator typically links freed chunks together by writing pointers INTO the freed memory itself; freeing the same chunk twice can make the free list point to itself or to attacker-influenced data, a well-known primitive real exploits use to eventually get malloc to hand back an attacker-chosen address. Use-after-free is the same idea without the second free call: you keep using p after free(p), and because the memory hasn't necessarily been overwritten yet, it often still "looks right" during testing and only misbehaves once something else reuses that memory - making UAF bugs notoriously hard to reproduce and a favorite for exploit developers, who deliberately trigger a reallocation of attacker-controlled data into the freed slot. Bitwise operations have their own overflow trap: shifting a signed int left until it overflows the sign bit, or shifting by an amount greater than or equal to the type's bit width (x << 32 on a 32-bit int), are both undefined behavior in C, not a defined wraparound - the compiler is permitted to assume it never happens and optimize accordingly."""},

            {"h": "HOW A PROFESSIONAL FINDS HEAP BUGS", "body": r"""Nobody debugs heap corruption by staring at source code alone - the bug usually manifests instructions or even function calls away from its true cause. AddressSanitizer (compile with gcc -fsanitize=address) instruments every malloc/free and every memory access, inserting "poisoned" guard regions around allocations so that reading even one byte out of bounds crashes IMMEDIATELY with a precise report, instead of silently corrupting an unrelated variable that only misbehaves much later. Valgrind's memcheck tool (Linux-only, but conceptually mirrored by Dr. Memory on Windows) runs your program in a software emulator that tracks every byte's "defined-ness," catching uninitialized reads, leaks, and use-after-free even without special compiler flags. Beyond tooling, a professional reading raw heap memory in a debugger recognizes the chunk header pattern directly - on glibc, a size field with its low bits used as flag bits (prev-in-use, etc.) sitting just before the pointer you'd normally use - which is exactly the "hidden metadata" from this lesson's first section, made visible in a memory dump rather than left as an abstract claim."""},

            {"h": "WHERE THIS IS GOING: HEAP CORRUPTION AS AN EXPLOIT PRIMITIVE", "body": r"""Everything in this lesson - hidden chunk headers, double free corrupting the free list, use-after-free reusing stale memory, integer overflow undersizing an allocation - is not academic trivia, it is the literal vocabulary of heap exploitation, one of the two or three core skill areas expected of the technical units you're preparing for. A heap overflow that overwrites the NEXT chunk's header can trick the allocator into believing a chunk is a different size than it really is, or into writing a "fake" free-list pointer during the next free(), which some classic techniques (like the historical unlink attack, or more modern tcache poisoning on Linux glibc) turn into an arbitrary write anywhere in the process's memory - often enough to overwrite a function pointer or a saved return address and redirect execution entirely. None of these techniques require anything beyond what you've learned here: they require KNOWING, precisely, what malloc and free actually do to memory around your pointer, which is exactly the gap between "I can call malloc" and "I can read and steer what malloc does" that separates a beginner from someone doing real vulnerability research."""},
        ],
    },

    "c-5": {
        "title_check": "Arrays & the pointer-array duality",
        "sections": [
            {"h": "sizeof DOES NOT LIE: DECAY ONLY HAPPENS ON PASSAGE", "body": r"""The single most misunderstood fact about C arrays is that decay-to-pointer is NOT universal - it happens only in most expression contexts and when an array is passed to a function, but NOT when sizeof or & is applied directly to the array itself. int arr[10]; sizeof(arr) correctly yields 40 (10 ints of 4 bytes) because sizeof sees the true array type, not a decayed pointer - this is one of exactly three contexts where decay does not occur (the others being & applied to the array, and string literals used to initialize a char array). The confusion arises because the moment that SAME array is passed into a function, void f(int arr[10]) or void f(int *arr) (identical to the compiler - the [10] is silently ignored in a parameter list), sizeof(arr) INSIDE that function now yields 8 (the size of a pointer on this x64 build), because arr inside f really is just a pointer parameter, having decayed the instant it crossed the function boundary. The array "remembers" its size only where the compiler can still see the original declaration."""},

            {"h": "ARRAY OF POINTERS VS POINTER TO ARRAY: READING THE DECLARATION", "body": r"""int *arr[5] and int (*arr)[5] look almost identical but declare completely different things, and C's declaration syntax reads by a "spiral" or right-left rule that resolves this. In int *arr[5], [] binds tighter than *, so arr is first "an array of 5," and each element is "pointer to int" - it is an array of 5 separate int pointers, each potentially pointing to a different, unrelated block of memory (this is how you build a jagged/ragged 2D structure, or an array of C strings: char *names[3] = {"a","bb","ccc"};). In int (*arr)[5], the parentheses force arr to first be "a pointer," specifically "pointer to an array of 5 ints" - a single pointer to one contiguous block of 20 bytes, used when passing a true fixed-width 2D array's row to a function. Misreading one for the other is a common, genuinely confusing bug source - a good habit is to read the declaration outward from the identifier name, applying whichever of * or [] is closest first, exactly as the parentheses (or their absence) dictate."""},

            {"h": "WORKED EXAMPLE: PASSING A TRUE 2D ARRAY TO A FUNCTION CORRECTLY", "body": r"""    #include <stdio.h>
    #define COLS 4
    void print_grid(int rows, int grid[][COLS]) {
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < COLS; c++)
                printf("%d ", grid[r][c]);
    }
    int main(void) {
        int grid[3][COLS] = {{1,2,3,4},{5,6,7,8},{9,10,11,12}};
        print_grid(3, grid);
        return 0;
    }

The parameter grid[][COLS] MUST specify every dimension except the first, because the compiler needs COLS to compute each row's stride: grid[r][c] is really *(grid + r*COLS + c) after grid decays to a pointer to "array of COLS ints." Omitting COLS would leave the compiler unable to compute where row r even starts - this is exactly why a 2D array parameter can never be written as int grid[][] with both dimensions blank, only the first."""},

            {"h": "FAILURE MODES: THE sizeof TRAP INSIDE A FUNCTION", "body": r"""    void process(int arr[]) {
        int n = sizeof(arr) / sizeof(arr[0]);  // BUG: always 2 on x64
        for (int i = 0; i < n; i++) { /* ... */ }
    }
    int main(void) {
        int data[100];
        process(data);   // caller's real length is lost
    }

Inside process, arr has already decayed to a plain int *, so sizeof(arr) is 8 (a pointer's size) and sizeof(arr[0]) is 4, giving n = 2 regardless of how large the caller's actual array was - this exact idiom, sizeof(arr)/sizeof(arr[0]), only computes the true element count when it is used in the SAME scope as the original array declaration, never inside a function that merely received the array as a parameter. This is arguably the most common real C bug related to array decay: it compiles without even a warning, silently processes only the first 2 elements (or whatever 8/sizeof(element) happens to be) of a 100-element array, and the fix is always the same - the caller must explicitly pass the length as a separate parameter, because C never attaches it to the pointer itself."""},

            {"h": "HOW A REVERSE ENGINEER SPOTS ARRAY INDEXING IN DISASSEMBLY", "body": r"""In a compiled binary, an int array access like arr[i] reliably shows up as a memory operand of the form [base + index*4] (or *8 for a pointer/long array, *1 for a char/byte array) - the scale IS the element size, made concrete rather than left as an abstract "sizeof." A 2D array access grid[r][c] compiles to more work: the compiler first multiplies r by the row width in bytes (an imul instruction, since the scale field in an addressing mode caps out at 8 and most row widths are larger), adds that to the base, THEN applies the familiar +c*4 indexing on top - so seeing an imul immediately before an indexed memory access is a strong tell that you're looking at multi-dimensional or struct-array indexing rather than flat 1D access. When auditing unfamiliar assembly or reverse-engineering a stripped binary, spotting this base+stride*row+c*element pattern is frequently how you first infer that a block of memory is actually a 2D grid or an array of structs, well before you have any other evidence of the original source's data layout."""},

            {"h": "WHERE THIS IS GOING: BASE+INDEX*SCALE IS A REAL ADDRESSING MODE", "body": r"""Everything about "arrays decay to pointers" and "arr[i] equals *(arr+i)" that you've learned across this lesson and the earlier one is not just a C-language quirk - it exists because x86 CPUs have hardware support for exactly this pattern. The addressing mode [base + index*scale + displacement] is not something the compiler builds out of several instructions; it is a single memory operand that one mov (or add, or cmp, or anything else that touches memory) can use directly, with scale restricted to 1, 2, 4, or 8 - which is not a coincidence, it is precisely the byte sizes of char, short, int/float, and double/pointer/long. C's array indexing was designed, and the hardware's addressing modes were designed, around the exact same idea: an array is a base address plus a scaled offset. When you reach the asm track's addressing-modes lesson, arr[i] * sizeof matching a scale of 4 or 8 will not be new information - you will already know exactly why the hardware only offers those four scale factors and no others."""},
        ],
    },

    "c-6": {
        "title_check": "Multi-file programs & the preprocessor",
        "sections": [
            {"h": "TRANSLATION UNITS: EACH .c FILE COMPILES IN ISOLATION", "body": r"""When you run gcc main.c utils.c -o app, gcc does not read both files together as one program - it compiles main.c into main.o and utils.c into utils.o as two entirely separate, independent compilation jobs, each called a "translation unit." While compiling main.c, the compiler has absolutely no idea utils.c even exists; it only knows what main.c's own #includes told it - typically a prototype in utils.h declaring int add(int, int);, which is enough for the compiler to generate a call instruction to a symbol named add and TRUST that something, somewhere, will supply it. Only after both .o files exist does the LINKER (a completely separate tool, invoked automatically by gcc as its last step) read both object files, find that main.o has an unresolved reference to a symbol "add" and that utils.o DEFINES a symbol "add," and patch main.o's call instruction to point at add's actual address. This two-phase ignorance-then-resolution is why a missing function produces a linker error ("undefined reference"), not a compiler error - the compiler was perfectly happy, it was the linker that couldn't find the promised piece."""},

            {"h": "extern AND static: SHARING AND HIDING ACROSS FILES", "body": r"""By default, a global variable or function defined in one .c file has EXTERNAL linkage - the linker will happily connect a matching declaration in another file to it. extern int counter; in a header (or another .c file) is a pure DECLARATION - "a variable named counter exists somewhere, with this type, I'm not creating storage for it here" - while exactly one .c file must contain the actual DEFINITION, int counter = 0; (no extern), which is where the linker-visible storage is created. The opposite tool, static, applied to a global variable or function, gives it INTERNAL linkage instead - it becomes invisible to every other translation unit, even if they somehow declare a matching prototype, which is how you create genuinely private helper functions inside a .c file with zero risk of another file accidentally calling or colliding with them. A frequent mistake is defining (not just declaring) a non-static function or variable directly inside a header file that gets #included by more than one .c file - each translation unit then generates its own definition, and the linker reports a "multiple definition" error once it tries to merge them."""},

            {"h": "WORKED EXAMPLE: A SHARED COUNTER AND A FILE-PRIVATE HELPER", "body": r"""    // stats.h
    extern int total_calls;          // declaration only
    void record_call(void);

    // stats.c
    int total_calls = 0;             // the one true definition
    static int scale_factor = 2;     // private to stats.c only
    static int scaled(int x) { return x * scale_factor; }
    void record_call(void) { total_calls = scaled(total_calls + 1); }

    // main.c
    #include "stats.h"
    #include <stdio.h>
    int main(void) {
        record_call(); record_call();
        printf("%d\n", total_calls);   // reads stats.c's global
        return 0;
    }

    // gcc main.c stats.c -o app

main.c can read total_calls because stats.h's extern declaration told it the symbol exists and stats.c supplies it at link time; main.c CANNOT call scaled() or read scale_factor, even by declaring its own prototype, because static locked both to stats.c's translation unit alone."""},

            {"h": "FAILURE MODES: LINKER ERRORS AND MACRO BUGS", "body": r"""Two failure classes dominate multi-file C. The first is purely linker-level: forgetting to list a .c file in the build command (gcc main.c -o app when add lives in utils.c) produces "undefined reference to add," while defining the SAME non-static function or global in two different .c files (or in a header lacking static/inline, included by two .c files) produces "multiple definition of add" - both are link errors, not compile errors, and both are fixed by getting exactly one real definition into the final build. The second class is macro misuse, since #define is pure text substitution with no parentheses inserted for you: #define SQUARE(x) x*x looks correct for SQUARE(5) (expands to 5*5=25) but SQUARE(a+b) expands to a+b*a+b, which due to operator precedence is NOT (a+b) squared at all - the fix is #define SQUARE(x) ((x)*(x)), parenthesizing both the parameter and the whole expression. A second macro trap: SQUARE(i++) expands to i++*i++, evaluating and incrementing i twice in one statement - undefined behavior from multiple unsequenced modifications, invisible until you actually run it."""},

            {"h": "HOW A PROFESSIONAL READS SYMBOLS AND BUILDS WITH make", "body": r"""nm utils.o lists every symbol an object file defines or requires - a defined symbol shows a type letter and address (T for a function in .text, D for an initialized global in .data, B for an uninitialized one in .bss), while an undefined symbol the file still needs shows U, letting you answer "does this .o actually define add, or does it just expect someone else to?" without opening any source at all - useful when auditing a build you didn't write, or a binary blob you're reverse engineering. For anything beyond a couple of files, professionals don't retype the full gcc command by hand every time - a Makefile expresses "app depends on main.o and utils.o; utils.o depends on utils.c and utils.h" as rules, and running make recompiles ONLY the files whose dependencies changed since the last build (checked via file modification timestamps), which matters enormously once a project has dozens of files and a full rebuild takes minutes rather than seconds."""},

            {"h": "WHERE THIS IS GOING: THE BINARY REMEMBERS NONE OF THIS", "body": r"""Headers, #include, extern, static, translation units, even the preprocessor's macro expansion - every single one of these is a SOURCE-LEVEL organizational tool with zero trace left in the compiled binary. By the time gcc has produced app.exe, there is no concept of "which .c file" a function came from, no header boundaries, no macro names (SQUARE(x) has been fully textually replaced before the compiler even ran) - just a flat address space of instructions and data, with function symbols optionally preserved as debug/linker metadata that a stripped release binary typically discards entirely. This is exactly why reverse engineering a binary is harder than reading its original source: you are reconstructing the multi-file structure, the meaningful names, and the macro-level intent PURELY from instruction patterns and cross-references between functions, with none of the organizational scaffolding this lesson just taught you left standing. Every remaining lesson in the asm track effectively asks the same question this one answers in reverse: given only what survives compilation, how much of the original design can you recover?"""},
        ],
    },

}
