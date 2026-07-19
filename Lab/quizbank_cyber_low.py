# quizbank_cyber_low.py - additional graded checks for the cyber_low track.
# Merged onto each lesson's existing quiz by content.build_courses().
# Answer indices balanced across the file so the correct option isn't always first.
EXTRA_QUIZ = {
    "cl-1": [
        {
            "q": "What is 0b1011 in decimal?",
            "code": "",
            "options": [
                "11",
                "13",
                "9",
                "1011"
            ],
            "answer": 0,
            "why": "1011 in binary is 8 + 0 + 2 + 1 = 11.",
            "detail": "Each bit is a power of two: from the left, 1*8 + 0*4 + 1*2 + 1*1 = 11. 13 would be 1101, 9 would be 1001, and 1011 as decimal ignores the base entirely. Fluent binary-to-decimal conversion (recognizing the place values 1,2,4,8,16...) is fundamental for reading flags, masks, and memory contents at the bit level."
        },
        {
            "q": "What does `x | 0x0F` do to the low nibble of x?",
            "code": "unsigned char x = 0xA0;\nunsigned char y = x | 0x0F;",
            "options": [
                "Clears the low four bits, giving 0xA0",
                "Sets the low four bits to 1, giving 0xAF",
                "Flips the low four bits",
                "Leaves x unchanged"
            ],
            "answer": 1,
            "why": "OR with 1 bits forces those bits to 1, so the low nibble becomes all ones: 0xA0 | 0x0F = 0xAF.",
            "detail": "Bitwise OR sets a bit wherever the mask has a 1, so `| 0x0F` turns the low four bits on regardless of their previous value, yielding 0xAF. It does not clear (that is AND with 0), does not flip (that is XOR), and does change x's low nibble. OR-with-a-mask is the standard idiom for SETTING specific bits, a core operation for manipulating hardware registers and packed flags."
        },
        {
            "q": "What does `x & 0xF0` extract?",
            "code": "unsigned char x = 0xAB;\nunsigned char y = x & 0xF0;",
            "options": [
                "The low nibble, giving 0x0B",
                "All of x, 0xAB",
                "The high nibble, giving 0xA0",
                "Zero"
            ],
            "answer": 2,
            "why": "AND with a mask keeps only the bits where the mask is 1; 0xF0 keeps the high four bits, giving 0xA0.",
            "detail": "Bitwise AND with 0xF0 preserves the high nibble (A) and zeros the low nibble, producing 0xA0. To get the low nibble you would AND with 0x0F. It does not keep all of x or give zero. AND-with-a-mask is the idiom for EXTRACTING or CLEARING specific bits, the complement of OR-for-setting, and both are everywhere in low-level code that packs multiple values into one byte or word."
        },
        {
            "q": "What is the result and why?",
            "code": "unsigned char a = 0b11001010;\nunsigned char b = a ^ 0b11111111;",
            "options": [
                "0b11001010 — unchanged",
                "0b11111111 — all ones",
                "0b00000000 — all zeros",
                "0b00110101 — XOR with all ones inverts every bit"
            ],
            "answer": 3,
            "why": "XOR with 1 flips a bit, so XOR with all 1s inverts every bit — a bitwise NOT.",
            "detail": "XOR flips a bit wherever the mask is 1, so XORing with 0xFF (all ones) inverts all eight bits: 11001010 becomes 00110101. It is not unchanged (that is XOR with 0), not all ones or all zeros. XOR-with-all-ones is equivalent to the ~ (NOT) operator and is a common trick; XOR also underlies simple checksums and the observation that x ^ x == 0, used in many bit-manipulation puzzles."
        },
        {
            "q": "A permission field uses bits: read=4, write=2, execute=1. A file has permission value 6. What does that grant?",
            "code": "",
            "options": [
                "Read and write (4 + 2), but not execute",
                "Execute only",
                "Read, write, and execute",
                "Write and execute (2+1)"
            ],
            "answer": 0,
            "why": "6 = 4 + 2 = read + write; the execute bit (1) is not set, so no execute permission.",
            "detail": "The value 6 in binary is 110, meaning the read (4) and write (2) bits are set but execute (1) is not — exactly the Unix permission encoding. It is not execute-only (that is 1), not all three (that is 7), and not write+execute (that is 3). This is why `chmod 6` style octal permissions work: each digit is a sum of the bit values, and reading them back is pure bitwise thinking applied to a real system."
        },
        {
            "q": "Why does `(x >> 4) & 0xF` extract the high nibble of a byte?",
            "code": "unsigned char x = 0x9C;\nint hi = (x >> 4) & 0xF;",
            "options": [
                "It gives the low nibble C",
                "The shift moves the high nibble down to the low position, then the mask isolates it (gives 9)",
                "It gives all of x",
                "It gives 0"
            ],
            "answer": 1,
            "why": "Shifting right by 4 brings the high nibble into the low 4 bits, and & 0xF keeps just those, yielding 9.",
            "detail": "0x9C is 1001 1100; shifting right 4 gives 0000 1001 (the high nibble 9 now in the low position), and & 0xF isolates it — so hi is 9. Without the shift you would get the low nibble; without the mask, extra high bits could remain if x were wider. The shift-then-mask pattern is the standard way to extract a bit field from a packed value, used constantly in parsing binary formats and hardware registers."
        }
    ],
    "cl-2": [
        {
            "q": "The 32-bit value 0x12345678 is stored little-endian. What is the byte order in memory (low address first)?",
            "code": "",
            "options": [
                "12 34 56 78",
                "87 65 43 21",
                "78 56 34 12",
                "34 12 78 56"
            ],
            "answer": 2,
            "why": "Little-endian stores the least significant byte first, so 0x12345678 appears as 78 56 34 12.",
            "detail": "Little-endian (used by x86) places the low-order byte (0x78) at the lowest address, ascending to the high-order byte (0x12). Big-endian would store it as 12 34 56 78. '87 65 43 21' wrongly reverses the nibbles within each byte — endianness reorders BYTES, never the bits or nibbles inside a byte, a crucial distinction. Reading hex dumps correctly requires knowing the machine's endianness, or multi-byte values look scrambled."
        },
        {
            "q": "Does endianness affect the order of bits within a single byte?",
            "code": "",
            "options": [
                "Yes, it reverses the bits too",
                "Only for signed values",
                "Only in big-endian systems",
                "No — endianness only reorders BYTES of a multi-byte value, never bits within a byte"
            ],
            "answer": 3,
            "why": "Endianness is strictly about the ordering of whole bytes in memory; the bit order inside a byte is fixed.",
            "detail": "A single byte has a fixed bit order; endianness only concerns how the multiple bytes of a larger value (16/32/64-bit) are arranged in memory. Believing it flips bits within a byte is a very common misconception that makes hex dumps confusing. It applies to both signed and unsigned equally and to both endian conventions (they just differ in byte order). Keeping 'endianness = byte order only' straight is essential for reading binary data."
        },
        {
            "q": "A file begins with the bytes `7F 45 4C 46`. What is it?",
            "code": "7F 45 4C 46 ...",
            "options": [
                "An ELF binary (Linux executable) — those are its magic-number bytes",
                "A Windows PE executable",
                "A JPEG image",
                "A plain text file"
            ],
            "answer": 0,
            "why": "0x7F followed by 'ELF' (45 4C 46 in ASCII) is the ELF magic number identifying a Linux/Unix binary.",
            "detail": "The four bytes 7F 45 4C 46 are 0x7F and the ASCII characters E, L, F — the ELF magic number. A Windows PE starts with 'MZ' (4D 5A), a JPEG with FF D8, and text has no such magic. File-format magic numbers at the start of a file are how tools like `file` identify types regardless of extension, and recognizing common magics (ELF, MZ/PE, PDF's %PDF, PNG) is a routine skill in binary analysis and forensics."
        },
        {
            "q": "In a hex dump, the ASCII column shows a dot '.' for byte 0x00 and byte 0x07. Why?",
            "code": "0x12 0x00 0x41 0x07  ->  '.', '.', 'A', '.'",
            "options": [
                "0x00 and 0x07 are both the letter dot",
                "Non-printable bytes are shown as dots; only printable ASCII (like 0x41='A') displays as its character",
                "The dump is corrupted",
                "Dots mean the bytes are zero"
            ],
            "answer": 1,
            "why": "Hex dump ASCII columns render non-printable bytes as a placeholder dot, showing real characters only for printable codes.",
            "detail": "Bytes outside the printable ASCII range (roughly 0x20-0x7E) have no visible character, so tools like xxd substitute a dot; 0x41 is 'A' and shows normally, while 0x00 (null) and 0x07 (bell) are non-printable and become dots. The dots are not literal periods (0x2E is a real dot), the dump is fine, and dots do not specifically mean zero — 0x07 is nonzero yet still a dot. Understanding this dual hex/ASCII view is key to reading dumps and spotting embedded strings."
        },
        {
            "q": "You see `48 65 6C 6C 6F` in a hex dump's data. What text is this?",
            "code": "48 65 6C 6C 6F",
            "options": [
                "0x48656C6C6F as a number",
                "world",
                "Hello — these are the ASCII codes H,e,l,l,o",
                "An address"
            ],
            "answer": 2,
            "why": "48='H', 65='e', 6C='l', 6C='l', 6F='o' in ASCII, spelling Hello.",
            "detail": "Each byte maps to an ASCII character: 0x48=H, 0x65=e, 0x6C=l, 0x6C=l, 0x6F=o. Reading it as a single big number ignores that these are character codes, and it is certainly not 'world' or an address. Recognizing ASCII byte sequences in a dump lets you spot embedded strings — filenames, messages, URLs — without any tool, a constant task in reverse engineering and malware analysis where strings reveal a binary's behavior."
        },
        {
            "q": "Why must a network protocol specify a byte order for multi-byte fields?",
            "code": "",
            "options": [
                "To encrypt the fields",
                "To compress the data",
                "Endianness does not matter for networks",
                "Different machines use different endianness, so a fixed 'network byte order' prevents misinterpretation"
            ],
            "answer": 3,
            "why": "Hosts may be little- or big-endian, so protocols define a canonical byte order (big-endian) so both sides agree.",
            "detail": "A little-endian sender and a big-endian receiver would read a multi-byte field differently, so protocols mandate 'network byte order' (big-endian) and code converts with htons/ntohs. It has nothing to do with encryption or compression, and endianness absolutely matters across machines — ignoring it is a real interoperability bug. This is why network programming involves byte-order conversion functions, a direct practical consequence of endianness."
        }
    ],
    "cl-3": [
        {
            "q": "In a process's memory layout, where do local variables and function call frames live?",
            "code": "",
            "options": [
                "The stack",
                "The heap",
                "The .text segment",
                "The .bss segment"
            ],
            "answer": 0,
            "why": "Locals and call frames live on the stack, which grows and shrinks with function calls and returns.",
            "detail": "The stack holds each function's frame — its locals, saved registers, and return address — pushed on call and popped on return. The heap is for dynamic allocation (malloc), .text holds code, and .bss holds zero-initialized globals. Knowing that locals are on the stack is essential for understanding stack overflows, recursion limits, and why returning a pointer to a local is a bug — the frame vanishes on return."
        },
        {
            "q": "What does the .text segment contain, and what protection does it usually have?",
            "code": "",
            "options": [
                "Global variables; read + write",
                "The program's machine-code instructions; read + execute, but NOT writable",
                "The call stack; read + write",
                "Heap allocations; read + write"
            ],
            "answer": 1,
            "why": ".text holds executable code and is mapped read-execute but not writable, so the code cannot be modified at runtime.",
            "detail": "The .text segment stores the compiled instructions and is marked read+execute; making it non-writable prevents accidental or malicious modification of code, a key security property (W^X: writable XOR executable). Globals live in .data/.bss (read-write, not executable), the stack and heap are read-write. This separation — code executable-not-writable, data writable-not-executable — is a foundational defense (DEP/NX) against injecting and running code, which the stack-overflow lesson builds on."
        },
        {
            "q": "Which region does `malloc(100)` allocate from, and how is it reclaimed?",
            "code": "char *p = malloc(100);",
            "options": [
                "The stack; reclaimed automatically on return",
                "The .text segment",
                "The heap; reclaimed only when you call free (or at process exit)",
                "The .bss segment"
            ],
            "answer": 2,
            "why": "malloc allocates from the heap, which persists until explicitly freed — unlike stack memory that is automatic.",
            "detail": "Dynamic allocations come from the heap and live until free() (or program exit), giving you control over lifetime but requiring you to manage it (or leak). The stack is for automatic locals reclaimed on return, .text is code, .bss is zero-init globals. The heap-versus-stack distinction governs object lifetime: heap for data that must outlive the allocating function, stack for short-lived locals, and confusing them causes dangling pointers or leaks."
        },
        {
            "q": "The stack grows toward lower addresses and the heap grows toward higher addresses. Why arrange them at opposite ends?",
            "code": "",
            "options": [
                "To make the stack faster",
                "Because the CPU requires it",
                "To encrypt the heap",
                "So both can grow toward the middle, maximizing the space each can use before they collide"
            ],
            "answer": 3,
            "why": "Placing stack and heap at opposite ends growing toward each other lets each expand into shared free space until they meet.",
            "detail": "By putting the stack high (growing down) and the heap low (growing up), the large gap between them is available to whichever needs it, rather than fixing a boundary that might waste space on one side. It is not about speed or encryption, and while conventional, the exact direction is an OS/ABI choice, not a hard CPU rule. Understanding this layout explains stack-heap collisions in memory-starved programs and why addresses hint at which region a pointer targets."
        },
        {
            "q": "Why is a pointer to a local variable invalid after the function returns?",
            "code": "int* f() { int x = 5; return &x; }",
            "options": [
                "x lived in f's stack frame, which is reclaimed on return, leaving the pointer dangling",
                "x is moved to the heap automatically",
                "The pointer becomes NULL safely",
                "Nothing is wrong"
            ],
            "answer": 0,
            "why": "The stack frame holding x is released when f returns, so the returned address points at reclaimed memory.",
            "detail": "Locals live in the function's stack frame, which is popped on return, so &x refers to memory that is no longer valid and may be overwritten by the next call — a dangling pointer and undefined behavior. Locals are NOT auto-promoted to the heap (that is some other languages, not C), the pointer does not become a safe NULL, and it is definitely a bug. This is the memory-layout reason behind the 'never return the address of a local' rule."
        },
        {
            "q": "Where are zero-initialized global variables stored, and why does this save file space?",
            "code": "static int big[1000000];  // uninitialized global",
            "options": [
                ".data, storing all the zeros in the file",
                ".bss — the file records only its SIZE, and the OS zero-fills it at load time",
                ".text with the code",
                "The stack"
            ],
            "answer": 1,
            "why": ".bss holds zero-initialized/uninitialized globals; the executable stores just the size, and the loader zeros the region.",
            "detail": "The .bss segment is for globals that start at zero, so the file need not store a million zero bytes — it records the size and the OS allocates and zeroes the memory at load, keeping executables small. Explicitly-initialized globals go in .data (their values ARE stored). It is not in .text (code) or the stack (locals). This .bss trick is why a program with huge zero arrays has a small binary, a neat consequence of the segment model."
        }
    ],
    "cl-4": [
        {
            "q": "A Windows PE executable begins with which two ASCII bytes?",
            "code": "",
            "options": [
                "'PE' (0x50 0x45)",
                "0x7F 'ELF'",
                "'MZ' (0x4D 0x5A)",
                "'#!' (0x23 0x21)"
            ],
            "answer": 2,
            "why": "PE files start with the DOS 'MZ' signature; the 'PE' signature appears later at an offset it points to.",
            "detail": "Every PE file opens with the legacy DOS header whose magic is 'MZ' (0x4D5A, the initials of a DOS architect), and a field in it points to the 'PE\\0\\0' signature further in. ELF binaries start with 0x7F 'ELF', and '#!' begins a script's shebang. Recognizing 'MZ' at offset 0 instantly identifies a Windows executable in a hex dump, a routine step in file identification and malware triage."
        },
        {
            "q": "What do PE and ELF have in common?",
            "code": "",
            "options": [
                "Both are CPU instruction sets",
                "Both are encryption schemes",
                "Both are network protocols",
                "Both are executable file FORMATS that describe sections, entry point, and how to load the program"
            ],
            "answer": 3,
            "why": "PE (Windows) and ELF (Linux) are container formats specifying how code/data sections are laid out and loaded.",
            "detail": "PE and ELF are the executable/object file formats for Windows and Linux respectively — each defines headers, sections (.text, .data), the entry point, and loading/relocation info the OS loader uses. They are not instruction sets (that is x86/ARM), not encryption, and not network protocols. They are analogous structures solving the same problem on different OSes, which is why understanding one makes the other familiar, useful in cross-platform reverse engineering."
        },
        {
            "q": "Why is the .text section typically read+execute but NOT writable?",
            "code": "",
            "options": [
                "Preventing writes to code stops accidental or malicious modification of instructions at runtime (W^X)",
                "To make the program smaller",
                "Because code cannot be read",
                "To speed up execution only"
            ],
            "answer": 0,
            "why": "Non-writable code enforces write-XOR-execute, blocking runtime code modification and code injection into the text segment.",
            "detail": "Marking code executable but not writable means an attacker cannot overwrite instructions or, combined with a non-executable stack/heap (DEP/NX), cannot inject and run new code easily — the W^X principle. It is not about file size or read-ability (code IS read to execute), and the security benefit is the main point, not raw speed. This memory-protection scheme is a foundational exploit mitigation that shaped how modern binaries are laid out and loaded."
        },
        {
            "q": "The PE header's AddressOfEntryPoint tells the loader what?",
            "code": "",
            "options": [
                "The file's size",
                "Where execution begins once the program is loaded into memory",
                "The encryption key",
                "The number of sections"
            ],
            "answer": 1,
            "why": "The entry point is the address (RVA) where the OS transfers control to start running the program.",
            "detail": "After mapping the sections into memory, the loader jumps to the entry point to begin execution — it is the program's starting instruction. It is not the file size, an encryption key, or the section count (those are other header fields). In reverse engineering, finding the entry point is where you start tracing a binary's behavior, so this field is one of the first things an analyst looks at in a PE or ELF header."
        },
        {
            "q": "A file's extension is .jpg but its first bytes are `4D 5A`. What is the safest conclusion?",
            "code": "4D 5A 90 00 ...",
            "options": [
                "It is a valid JPEG",
                "The bytes are irrelevant",
                "It is actually a Windows executable (MZ); the extension is misleading, a red flag",
                "It is corrupted beyond use"
            ],
            "answer": 2,
            "why": "The 'MZ' magic identifies a PE executable regardless of the .jpg extension — a classic sign of a disguised file.",
            "detail": "File type is determined by magic bytes, not the extension, so 4D 5A ('MZ') means it is an executable masquerading as an image — a common malware and phishing technique. A real JPEG starts with FF D8. The bytes are highly relevant (they are the whole point), and the file is not corrupted, just mislabeled. This is exactly why analysts check magic numbers rather than trusting extensions, and why an executable wearing an image extension is suspicious."
        },
        {
            "q": "What is a 'section' in a PE/ELF file, conceptually?",
            "code": "",
            "options": [
                "A single CPU instruction",
                "A network packet",
                "A user account",
                "A named region (like .text, .data, .rodata) grouping content with the same purpose and memory protection"
            ],
            "answer": 3,
            "why": "Sections group related content — code, initialized data, read-only data — each mapped with appropriate permissions.",
            "detail": "Sections such as .text (code, r-x), .data (read-write globals), .rodata (read-only constants), and .bss (zero-init) organize the file so the loader can map each with the right memory protections. A section is not a single instruction, a packet, or an account. This organization is how the format ties file layout to memory permissions (the W^X model), and reading a binary's section table is a first step in understanding its structure."
        }
    ],
    "cl-5": [
        {
            "q": "Why does `0.1 + 0.2 != 0.3` in most languages?",
            "code": "print(0.1 + 0.2 == 0.3)  # False",
            "options": [
                "0.1, 0.2, 0.3 cannot be represented exactly in binary floating point, so tiny rounding errors accumulate",
                "It is a bug in the language",
                "Floats are always integers",
                "The == operator is broken"
            ],
            "answer": 0,
            "why": "Binary floating point (IEEE-754) cannot represent 0.1 or 0.2 exactly, so their sum differs slightly from 0.3's approximation.",
            "detail": "Just as 1/3 has no exact decimal, 0.1 has no exact binary fraction, so it is stored as a close approximation; the arithmetic produces a result minutely off from the stored 0.3. It is not a language bug (it is the IEEE-754 standard behaving as specified), floats are not integers, and == works correctly on the actual stored values. The fix is to compare with a small tolerance (epsilon). Understanding float representation prevents a whole class of numerical bugs."
        },
        {
            "q": "How is the character 'A' represented, and what is its numeric value?",
            "code": "char c = 'A';",
            "options": [
                "As the string \"A\"",
                "As the integer 65 (its ASCII code) in a single byte",
                "As a float",
                "As two bytes"
            ],
            "answer": 1,
            "why": "A char is a one-byte integer holding the character's code; 'A' is 65 in ASCII.",
            "detail": "Characters are just small integers — 'A' is stored as the byte 65 (0x41). It is not a string (which would be a char array with a terminator), not a float, and a basic char is one byte (though wide/Unicode encodings use more). This integer nature is why 'A' + 1 == 'B' and why you can compare and do arithmetic on characters, a fact used constantly in parsing and encoding work."
        },
        {
            "q": "Why is sizeof this struct usually 12, not 9?",
            "code": "struct S { char c; int n; char d; };",
            "options": [
                "The compiler adds 3 bytes of metadata",
                "char is 3 bytes here",
                "Padding aligns n to a 4-byte boundary and pads the struct to a multiple of its largest member",
                "It is actually 9"
            ],
            "answer": 2,
            "why": "Alignment inserts padding after c so n starts at offset 4, and trailing padding rounds the size to a multiple of 4.",
            "detail": "c at offset 0, then 3 padding bytes so the int n aligns at offset 4 (bytes 4-7), then d at offset 8, then 3 trailing padding bytes to make the total a multiple of 4 (the int's alignment) — 12 bytes. The naive sum is 1+4+1=9. It is not metadata or oversized chars. Reordering to put the int first (int, char, char) would need only 8 bytes. Struct padding matters for memory use, binary layouts, and interpreting raw dumps of structures."
        },
        {
            "q": "What does this expression evaluate to?",
            "code": "float f = 16777217;  // 2^24 + 1 as a 32-bit float\nprintf(\"%.0f\\n\", f);",
            "options": [
                "16777217 exactly",
                "0",
                "An error",
                "16777216 — a 32-bit float cannot represent 2^24+1 exactly and rounds down"
            ],
            "answer": 3,
            "why": "A 32-bit float has 24 bits of mantissa, so it cannot distinguish 2^24+1 from 2^24 and rounds to 16777216.",
            "detail": "Single-precision floats have about 24 bits of precision, so beyond 2^24 consecutive integers can no longer all be represented — 16777217 rounds to the nearest representable value, 16777216. It is not stored exactly, not zero, and not an error (it silently rounds). This is why large integer computations use doubles or actual integer types; float's limited mantissa causes silent precision loss that surprises people working with big numbers."
        },
        {
            "q": "Why can reordering a struct's fields reduce its size?",
            "code": "struct A { char c; int n; char d; };  // 12 bytes\nstruct B { int n; char c; char d; };  // 8 bytes",
            "options": [
                "Grouping the larger-aligned field first minimizes the padding needed between fields",
                "Reordering never changes size",
                "B drops a field",
                "char becomes smaller in B"
            ],
            "answer": 0,
            "why": "Placing the int first lets the two chars pack together afterward, needing less alignment padding than when a char precedes the int.",
            "detail": "In B, the 4-byte int sits at offset 0, then the two 1-byte chars fill offsets 4 and 5, with only 2 trailing padding bytes to reach a multiple of 4 — total 8. In A, padding after the first char wastes space. Reordering DOES change size (that is the whole point), B keeps all fields, and char is still one byte. Ordering struct members from largest to smalltest alignment is a real technique to reduce memory footprint in data-heavy programs."
        },
        {
            "q": "What is the two's-complement representation of -1 in an 8-bit signed byte?",
            "code": "",
            "options": [
                "0x81",
                "0xFF (all bits set)",
                "0x01 with a sign flag",
                "0x00"
            ],
            "answer": 1,
            "why": "In two's complement, -1 is all ones (0xFF), because adding 1 wraps to 0x00 with the carry discarded.",
            "detail": "Two's complement represents -1 as all bits set (0xFF for 8 bits): 0xFF + 0x01 = 0x100, truncated to 0x00, exactly what -1 + 1 should give. 0x81 is -127, there is no separate sign flag (the top bit IS the sign, integrated into the value), and 0x00 is zero. Two's complement lets the CPU add signed and unsigned numbers with the same hardware, which is why it is universal — and why 0xFFFFFFFF read as signed is -1."
        }
    ],
    "cl-6": [
        {
            "q": "In a classic stack buffer overflow, what critical value can get overwritten?",
            "code": "char buf[8];\ngets(buf);  // reads unbounded input",
            "options": [
                "The program's source code",
                "The heap allocator",
                "The saved return address higher on the stack, redirecting where the function returns",
                "The CPU registers directly"
            ],
            "answer": 2,
            "why": "Writing past a stack buffer can overwrite the saved return address, so on return the CPU jumps to an attacker-chosen location.",
            "detail": "Locals and the saved return address share the stack frame, so overflowing a buffer writes into adjacent stack memory including the return address; corrupting it means `ret` transfers control somewhere unintended. It does not alter source code, the heap allocator, or registers directly. This mechanism is why unbounded input functions like gets() are dangerous, and understanding it (defensively) explains why the mitigations in the next question exist."
        },
        {
            "q": "Which defense places a known 'canary' value between local buffers and the saved return address?",
            "code": "",
            "options": [
                "ASLR",
                "DEP/NX",
                "A firewall",
                "Stack canaries — a guard value checked before return to detect overflow"
            ],
            "answer": 3,
            "why": "A stack canary sits before the return address; if an overflow changes it, the corrupted canary is detected and the program aborts.",
            "detail": "The compiler inserts a canary value that must be intact when the function returns; an overflow that reaches the return address also overwrites the canary, and the mismatch is caught, terminating the program before the hijacked return executes. ASLR randomizes addresses, DEP/NX makes the stack non-executable, and a firewall filters network traffic — different defenses. Canaries specifically detect stack-buffer overflows, one layer in the defense-in-depth against memory corruption."
        },
        {
            "q": "What does ASLR (Address Space Layout Randomization) make harder for an attacker?",
            "code": "",
            "options": [
                "Predicting the memory addresses of code and data, so hardcoded exploit addresses fail",
                "Reading the source code",
                "Sending network packets",
                "Compiling the program"
            ],
            "answer": 0,
            "why": "ASLR randomizes where segments load each run, so an exploit relying on fixed addresses cannot reliably find its targets.",
            "detail": "By loading the stack, heap, and libraries at randomized addresses each execution, ASLR breaks exploits that jump to hardcoded locations — the attacker no longer knows where anything is. It does not hide source code, block packets, or affect compilation. ASLR pairs with DEP/NX and stack canaries as complementary mitigations: canaries detect the overflow, DEP stops injected code from executing, and ASLR hides the targets — layered defense, since any one alone can sometimes be bypassed."
        },
        {
            "q": "What does DEP/NX (Data Execution Prevention / No-eXecute) enforce?",
            "code": "",
            "options": [
                "Data cannot be read",
                "Memory pages holding data (stack, heap) are marked non-executable, so injected code there cannot run",
                "The program runs faster",
                "Passwords are encrypted"
            ],
            "answer": 1,
            "why": "NX marks data regions non-executable, so even if an attacker writes code into the stack or heap, the CPU refuses to execute it.",
            "detail": "DEP/NX uses a CPU feature to mark the stack and heap as non-executable, enforcing write-XOR-execute: a region can be writable OR executable, not both. So classic 'inject shellcode onto the stack and jump to it' fails because the stack is not executable. It does not prevent reading data, is not about speed, and is unrelated to password encryption. This is why attackers turned to code-reuse techniques, and why defenders combine NX with the other mitigations."
        },
        {
            "q": "Why is `gets()` considered so dangerous that it was removed from the C standard?",
            "code": "gets(buf);",
            "options": [
                "It is too slow",
                "It only reads one character",
                "It reads input with no length limit, so any oversized input overflows the buffer — unfixable",
                "It encrypts the input"
            ],
            "answer": 2,
            "why": "gets() has no way to bound the input to the buffer size, so a long line always overflows — there is no safe way to use it.",
            "detail": "gets() writes input into a buffer until a newline, with no size parameter, so input longer than the buffer overflows it every time — a guaranteed vulnerability with no safe usage, which is why C11 removed it. It is not slow or single-character, and it does not encrypt. The safe replacement is fgets(), which takes a maximum length. gets() is the textbook example of an inherently unsafe API and a reason bounded input functions matter."
        },
        {
            "q": "These mitigations (canaries, ASLR, DEP/NX) are layered rather than relying on one. Why?",
            "code": "",
            "options": [
                "One is enough; the others are redundant",
                "They are the same mechanism",
                "Only ASLR actually works",
                "Each defends a different step, so defeating one still leaves the others — defense in depth"
            ],
            "answer": 3,
            "why": "Attacks have multiple stages, and each mitigation blocks a different one, so combining them means bypassing all is far harder.",
            "detail": "A canary detects the overflow, DEP/NX stops injected code executing, and ASLR hides target addresses — each targets a distinct stage of an exploit, so an attacker must defeat every layer, which is much harder than beating one. They are not redundant or identical, and none alone is sufficient (each has known bypasses in isolation). This defense-in-depth philosophy — assume any single control can fail, so stack several — is a core security principle beyond just memory safety."
        }
    ]
}
