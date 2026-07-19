# quizbank_asm.py - additional graded checks for the asm track.
# Merged onto each lesson's existing quiz by content.build_courses().
# Answer indices balanced across the file so the correct option isn't always first.
EXTRA_QUIZ = {
    "asm-1": [
        {
            "q": "After `mov rax, 0x1111111111111111` then `mov eax, 5`, what is rax?",
            "code": "mov rax, 0x1111111111111111\nmov eax, 5",
            "options": [
                "0x0000000000000005 — writing a 32-bit register zeroes the upper 32 bits",
                "0x1111111100000005 — only the low 32 bits change",
                "0x0000000000000005 only if you also clear rax",
                "0x1111111111111115"
            ],
            "answer": 0,
            "why": "Writing any 32-bit register (eax) zero-extends into the full 64-bit register, clearing the top half.",
            "detail": "The x86-64 rule is that a 32-bit write zeroes the upper 32 bits, so eax=5 makes rax exactly 5. The '0x1111...05' answer describes 8- or 16-bit writes (al/ax), which do NOT clear the high bits — that asymmetry is the trap. You do not need a separate clear, and the last option ignores the zeroing entirely. This is why `xor eax, eax` is the idiom to zero all of rax."
        },
        {
            "q": "What is the difference between `mov rax, [x]` and `lea rax, [x]`?",
            "code": "mov rax, [x]\nlea rax, [x]",
            "options": [
                "They are identical",
                "mov loads the VALUE at address x; lea loads the ADDRESS x itself",
                "mov loads the address; lea loads the value",
                "lea dereferences twice"
            ],
            "answer": 1,
            "why": "mov with brackets reads memory (the value); lea computes the effective address without touching memory.",
            "detail": "`mov rax, [x]` dereferences — it reads the value stored at x. `lea rax, [x]` performs only the address calculation, putting the address into rax without any memory access. They are not identical and the roles are not reversed. lea does not dereference at all (let alone twice). Confusing the two is one of the most common assembly bugs: mov gives the contents, lea gives the pointer."
        },
        {
            "q": "How do you zero the entire rax register most efficiently?",
            "code": "",
            "options": [
                "mov rax, 0 only",
                "and rax, 0",
                "xor eax, eax — the 32-bit XOR zeroes eax and zero-extends to clear all of rax",
                "sub rax, rax, then clear the high bits separately"
            ],
            "answer": 2,
            "why": "xor eax, eax is the shortest encoding and the zero-extension rule clears the upper 32 bits for free.",
            "detail": "`xor eax, eax` produces 0 in eax, and because it is a 32-bit write it also zeroes the top half of rax — clearing all 64 bits in a compact, fast instruction the CPU recognizes specially. `mov rax, 0` works but is a longer encoding, `and rax, 0` is unusual, and sub rax,rax does clear it but you do NOT need a separate high-bit clear (the last option's premise is wrong). xor-self is the universal zeroing idiom."
        },
        {
            "q": "What does `movzx rax, bl` do versus `movsx rax, bl` when bl = 0xFF?",
            "code": "mov bl, 0xFF\nmovzx rax, bl   ; vs movsx rax, bl",
            "options": [
                "Both give 0xFF",
                "movzx sign-extends, movsx zero-extends",
                "Both give 0xFFFF...FF",
                "movzx gives 0x00000000000000FF; movsx gives 0xFFFFFFFFFFFFFFFF (sign-extended)"
            ],
            "answer": 3,
            "why": "movzx zero-extends (high bits 0), movsx sign-extends (copies the top bit), so 0xFF becomes -1 under movsx.",
            "detail": "0xFF as an unsigned byte is 255 (movzx -> 0x...00FF); as a signed byte it is -1, so movsx copies the sign bit to fill the register with ones -> 0xFF...FF. The two are opposites: movzx=zero-extend, movsx=sign-extend, so 'movzx sign-extends' reverses them. Choosing the wrong one corrupts signed values silently — a real bug when widening a byte or word to a full register."
        },
        {
            "q": "Why is `mov [x], [y]` illegal?",
            "code": "mov [x], [y]",
            "options": [
                "x86 forbids two memory operands in one mov; at most one operand may reference memory",
                "The brackets are wrong syntax",
                "You must use lea instead",
                "Memory cannot be written by mov"
            ],
            "answer": 0,
            "why": "An instruction can have at most one memory operand, so a memory-to-memory mov must go through a register.",
            "detail": "x86 allows register-to-memory, memory-to-register, or register-to-register, but not memory-to-memory in one instruction, so you do `mov rax, [y]` then `mov [x], rax`. The brackets are valid syntax, lea is for addresses not copies, and mov certainly can write memory (register-to-memory is fine). This one-memory-operand rule shapes how you structure data moves and is a frequent early stumbling block."
        },
        {
            "q": "What is in al after this, and why?",
            "code": "mov ax, 0x1234\nmov bl, ah",
            "options": [
                "bl = 0x34 — the low byte",
                "bl = 0x12 — ah is the high byte of ax (bits 8-15)",
                "bl = 0x1234",
                "bl = 0x00"
            ],
            "answer": 1,
            "why": "ah accesses bits 8-15 of ax, which hold 0x12 when ax = 0x1234.",
            "detail": "ax = 0x1234 splits into ah = 0x12 (high byte) and al = 0x34 (low byte), so moving ah into bl gives 0x12. 0x34 would be al (the low byte), 0x1234 is the whole 16-bit value (too big for the 8-bit bl), and 0x00 ignores the data. The legacy ah/al sub-registers exposing the two halves of ax are a quirk of x86's history worth knowing when reading older or byte-oriented code."
        }
    ],
    "asm-2": [
        {
            "q": "Which instruction sets flags but discards its result, used to test equality?",
            "code": "cmp rax, rbx",
            "options": [
                "sub — it keeps the difference",
                "mov — it copies without flags",
                "cmp — it computes rax - rbx to set flags but keeps no result",
                "lea — it computes an address"
            ],
            "answer": 2,
            "why": "cmp does a subtraction only to set flags (ZF, SF, etc.), throwing away the difference, so ZF means equal.",
            "detail": "`cmp a, b` computes a-b, updates the flags, and discards the value — after it, ZF is set iff a==b. sub keeps the difference (changing a register), mov does not touch flags at all, and lea computes addresses. cmp is the standard 'compare then conditional jump' setup; pairing it with the right signed/unsigned jump is how all assembly branching works."
        },
        {
            "q": "To loop while a signed counter is greater than a value, which jump do you use after cmp?",
            "code": "cmp ecx, 5",
            "options": [
                "ja (jump if above) — that is for unsigned",
                "jne — only tests equality",
                "jmp — unconditional",
                "jg (jump if greater) — reads SF and OF for signed comparison"
            ],
            "answer": 3,
            "why": "jg is the SIGNED greater-than jump; ja is its unsigned counterpart, and using the wrong one corrupts signed logic.",
            "detail": "Signed comparisons use jg/jl/jge/jle (reading SF and OF together); unsigned use ja/jb/jae/jbe (reading CF). For a signed counter, jg is correct — ja would misinterpret negative numbers as huge unsigned values. jne only checks ZF (equality), and jmp is unconditional. Matching the jump's signedness to your data is essential; a signed/unsigned jump mismatch is a classic silent bug, especially comparing addresses or sizes."
        },
        {
            "q": "What does `test rax, rax` followed by `jz done` do?",
            "code": "test rax, rax\njz done",
            "options": [
                "Jumps to done if rax is zero — ANDing rax with itself sets ZF when rax is 0",
                "Jumps if rax is nonzero",
                "Always jumps",
                "Compares rax to 1"
            ],
            "answer": 0,
            "why": "test rax, rax computes rax AND rax (= rax) to set ZF; jz jumps when the result is zero, i.e., rax is zero.",
            "detail": "ANDing a value with itself yields the value, so ZF ends up set exactly when rax is zero, and jz (jump if zero) then branches. It jumps on ZERO, not nonzero (that would be jnz), does not always jump, and does not compare to 1. `test reg, reg` + jz/jnz is the idiomatic 'is this zero/null?' check, cheaper than `cmp reg, 0`, and appears constantly in null-pointer and loop-termination tests."
        },
        {
            "q": "Trace this: what is in eax when the loop exits?",
            "code": "xor eax, eax\nmov ecx, 3\n.l: add eax, ecx\n    dec ecx\n    jnz .l",
            "options": [
                "3",
                "6 — it adds 3 + 2 + 1 as ecx counts down to 0",
                "0",
                "It loops forever"
            ],
            "answer": 1,
            "why": "eax accumulates ecx (3, then 2, then 1); dec sets ZF when ecx hits 0, so jnz exits, leaving 6.",
            "detail": "Starting eax=0, ecx=3: add makes eax=3, dec ecx=2 (nonzero, loop); eax=5, ecx=1 (loop); eax=6, ecx=0, dec sets ZF so jnz falls through — eax=6. It is not 3 (that is one iteration), not 0, and it terminates because dec updates ZF that jnz reads. Tracing register values through a loop, watching how dec sets the flag the conditional jump consumes, is the core skill of reading assembly loops."
        },
        {
            "q": "Why might inserting `add rdx, 1` between a cmp and its conditional jump break the logic?",
            "code": "cmp rax, rbx\nadd rdx, 1     ; inserted here\njg somewhere",
            "options": [
                "add cannot appear there",
                "jg ignores flags",
                "add modifies the flags, so jg now reads flags set by add, not by the cmp",
                "It is always safe"
            ],
            "answer": 2,
            "why": "Arithmetic instructions like add overwrite the flags, so a jump after them no longer reflects the earlier cmp.",
            "detail": "cmp sets the flags for the intended comparison, but add also updates them, so by the time jg runs it is testing add's result, not rax vs rbx — wrong branch. Note that `mov` is safe to place between a cmp and jcc because mov does NOT touch flags, but add/sub/inc/dec do. jg absolutely reads flags (that is how it decides). This stale-flags hazard is why you keep flag-setting and flag-testing instructions adjacent."
        },
        {
            "q": "What distinguishes jl from jb?",
            "code": "",
            "options": [
                "They are identical",
                "jl is unsigned, jb is signed",
                "jb tests equality",
                "jl is signed less-than (SF/OF); jb is unsigned below (CF)"
            ],
            "answer": 3,
            "why": "jl compares as signed (using SF and OF); jb compares as unsigned (using CF) — the same bits, different interpretation.",
            "detail": "jl/jg treat operands as signed (negative numbers are less than positive); jb/ja treat them as unsigned (the top bit is just a high value bit). So 0xFFFFFFFF is 'less than' 1 under jl (it is -1) but 'above' 1 under ja (it is ~4 billion). They are not identical, the signed/unsigned roles are not reversed, and jb is not an equality test. Choosing jl vs jb wrongly is the signed/unsigned comparison bug in jump form."
        }
    ],
    "asm-3": [
        {
            "q": "What does `push rax` do to rsp?",
            "code": "push rax",
            "options": [
                "Subtracts 8 from rsp, then stores rax at the new [rsp]",
                "Adds 8 to rsp, then stores rax",
                "Only stores rax without changing rsp",
                "Stores rax at [rsp], then subtracts 8"
            ],
            "answer": 0,
            "why": "The stack grows downward, so push first decrements rsp by 8, then writes the value at the new top.",
            "detail": "Because the stack grows toward lower addresses, push subtracts 8 from rsp (making room) and then stores the value at [rsp]. Adding 8 would be the wrong direction (that is closer to pop), and push must change rsp (it is the whole point). The exact order — adjust rsp first, then store — matters for reasoning about the stack. pop does the reverse: read [rsp], then add 8."
        },
        {
            "q": "What does `call foo` push onto the stack?",
            "code": "call foo",
            "options": [
                "The value of foo",
                "The return address (address of the instruction after the call)",
                "The current flags",
                "Nothing — call only jumps"
            ],
            "answer": 1,
            "why": "call pushes the address of the next instruction so ret can return there, then jumps to foo.",
            "detail": "call is 'push the return address, then jmp target' — it saves where to resume (the instruction after the call) so the matching ret can pop it back into the instruction pointer. It does not push foo's value or the flags, and it definitely pushes something (that is how nesting works). Understanding call as push-return-address-then-jump is essential to reasoning about the stack and about how ret finds its way back."
        },
        {
            "q": "On Windows x64, why does a function often start with `sub rsp, 40` rather than 32?",
            "code": "sub rsp, 40",
            "options": [
                "40 is the shadow space size",
                "It reserves 40 bytes of locals",
                "32 bytes shadow space + 8 to keep rsp 16-byte aligned after call pushed the return address",
                "It is a mistake; 32 is correct"
            ],
            "answer": 2,
            "why": "The call pushed 8 bytes (misaligning rsp), so 32 shadow + 8 realigns to a 16-byte boundary for the next call.",
            "detail": "Windows x64 requires 32 bytes of shadow space AND 16-byte stack alignment at each call. Since call pushed the 8-byte return address, rsp is off by 8, so reserving 40 (32+8) both provides shadow space and restores alignment. Shadow space itself is 32 not 40, the 40 is not purely locals, and it is not a mistake — the extra 8 is the alignment fix. Getting this wrong crashes calls into SIMD-using library code."
        },
        {
            "q": "What is wrong with this function?",
            "code": "f:\n    push rbx\n    sub rsp, 32\n    ; ... work ...\n    ret",
            "options": [
                "push rbx is illegal",
                "It should not use the stack",
                "Nothing is wrong",
                "It never restores rsp/rbx — missing add rsp, 32 and pop rbx before ret, so ret reads the wrong value"
            ],
            "answer": 3,
            "why": "The prologue pushed rbx and reserved 32 bytes, but the epilogue does not undo them, so ret pops garbage.",
            "detail": "Every push and every sub rsp must be matched before ret: this function needs `add rsp, 32` then `pop rbx` before `ret`, or rsp points at the reserved space / saved rbx instead of the return address, and ret jumps to the wrong place. push rbx is legal, using the stack is fine, and something is definitely wrong. Balancing the stack — every reservation released, every push popped — is a correctness requirement enforced by ret at runtime."
        },
        {
            "q": "Where on the stack is the saved return address relative to a function's locals?",
            "code": "",
            "options": [
                "At a HIGHER address than the locals (locals are pushed/allocated below it)",
                "At a lower address than the locals",
                "In a register, not the stack",
                "It is not saved"
            ],
            "answer": 0,
            "why": "call pushes the return address first; subsequent locals are allocated at lower addresses, so the return address sits above them.",
            "detail": "Because the stack grows downward, the return address (pushed by call at function entry) is at a higher address, and locals reserved afterward (via sub rsp or push) live below it. This is precisely why a buffer overflow — writing PAST the end of a local upward — can reach and overwrite the saved return address. It is on the stack (not a register), and it is saved (that is call's job). This layout is the mechanism behind stack-smashing."
        },
        {
            "q": "What does `leave` do, and what is it equivalent to?",
            "code": "leave\nret",
            "options": [
                "It is the same as ret",
                "mov rsp, rbp then pop rbp — it tears down a frame built with push rbp; mov rbp, rsp",
                "It pushes a new frame",
                "It clears all registers"
            ],
            "answer": 1,
            "why": "leave restores rsp from rbp and pops the saved rbp, undoing the standard frame-pointer prologue in one instruction.",
            "detail": "leave is shorthand for `mov rsp, rbp` (discard locals by resetting the stack pointer to the frame base) then `pop rbp` (restore the caller's frame pointer) — the epilogue counterpart to the `push rbp; mov rbp, rsp` prologue. It is not ret (though it usually precedes ret), does not push a frame, and does not clear registers. Recognizing enter/leave and the push-rbp prologue helps you bracket functions when reading disassembly."
        }
    ],
    "asm-4": [
        {
            "q": "On Windows x64, the first integer argument to a function goes in which register?",
            "code": "",
            "options": [
                "rdi",
                "rax",
                "rcx",
                "the stack"
            ],
            "answer": 2,
            "why": "Microsoft x64 passes the first four integer args in rcx, rdx, r8, r9; rdi is the SysV (Linux) first register.",
            "detail": "Windows x64 uses rcx, rdx, r8, r9 for the first four integer/pointer arguments. rdi is the FIRST register in the System V (Linux/macOS) convention — mixing them up is the most common bug when porting Linux assembly to Windows. rax holds the return value, and the stack takes arguments only beyond the fourth. Knowing YOUR platform's argument registers cold is essential to making correct library calls."
        },
        {
            "q": "Why does calling printf need `lea rcx, [msg]` and not `mov rcx, [msg]`?",
            "code": "lea rcx, [msg]\ncall printf",
            "options": [
                "mov is required here",
                "They do the same thing",
                "printf takes the value, not the address",
                "printf wants the ADDRESS of the string; mov would pass the first 8 bytes of the string as if a pointer"
            ],
            "answer": 3,
            "why": "A format string argument is a pointer, so lea (address) is correct; mov would load the string's bytes and pass garbage.",
            "detail": "printf's first parameter is a char* (an address), so lea puts the address of msg into rcx. `mov rcx, [msg]` would instead load the first 8 bytes of the string's contents and pass THAT as the pointer, which printf then dereferences — a crash. They do not do the same thing (mov=value, lea=address), and printf does take the address. This mov/lea distinction is critical whenever you pass a pointer argument."
        },
        {
            "q": "On a raw Linux syscall, which register holds the syscall NUMBER?",
            "code": "",
            "options": [
                "rax",
                "rcx",
                "rdi",
                "r10"
            ],
            "answer": 0,
            "why": "Linux x86-64 syscalls take the call number in rax and arguments in rdi, rsi, rdx, r10, r8, r9.",
            "detail": "For the `syscall` instruction on Linux, rax carries the syscall number (e.g., 1 for write) and the return value comes back in rax; arguments use rdi, rsi, rdx, r10, r8, r9. rcx and r10 are not the number register (rcx is even clobbered by syscall). Note Windows apps normally do NOT issue raw syscalls — they call documented DLL functions — so this is Linux-specific knowledge, useful when reading Linux binaries."
        },
        {
            "q": "What would you run to see the assembly a C compiler generates for prog.c, in Intel syntax?",
            "code": "",
            "options": [
                "gcc -c prog.c",
                "gcc -S -masm=intel prog.c",
                "gcc prog.c -o prog",
                "objdump prog.c"
            ],
            "answer": 1,
            "why": "gcc -S stops after producing assembly; -masm=intel selects Intel syntax over the default AT&T.",
            "detail": "`gcc -S -masm=intel prog.c` emits prog.s with the compiler's assembly in Intel syntax. `gcc -c` produces an object file (machine code, not readable assembly), plain `gcc prog.c -o prog` builds an executable, and objdump works on compiled binaries not .c source. Reading gcc -S output is how you learn how C constructs map to instructions and how you check what the compiler actually did."
        },
        {
            "q": "You call a library function and it crashes, though your argument registers look right. What Windows-specific setup did you likely forget?",
            "code": "",
            "options": [
                "Setting rax to the arg count",
                "Pushing all arguments to the stack",
                "The 32 bytes of shadow space (and 16-byte alignment) required before the call",
                "Clearing the flags"
            ],
            "answer": 2,
            "why": "Windows x64 requires 32 bytes of shadow space and 16-byte stack alignment at the call, or the callee corrupts the stack.",
            "detail": "Even with correct argument registers, omitting the shadow-space reservation (sub rsp, 32/40) or leaving rsp misaligned makes the callee's prologue overwrite your return address or fault in SIMD code. You do not set rax to an arg count (that is a variadic-float convention detail on SysV, not this), you do not push register args to the stack, and clearing flags is unrelated. Shadow space and alignment are the usual culprits when Windows library calls crash mysteriously."
        },
        {
            "q": "What is the practical reason Windows applications call DLL functions (like from kernel32) instead of issuing raw syscall instructions?",
            "code": "",
            "options": [
                "Raw syscalls are faster but forbidden",
                "The syscall instruction does not exist on x86-64",
                "DLLs are the only way to pass arguments",
                "Microsoft does not guarantee stable syscall numbers between OS versions, so DLLs provide a stable documented interface"
            ],
            "answer": 3,
            "why": "Windows syscall numbers change between builds, so the stable ABI is the documented DLL functions, not raw syscalls.",
            "detail": "Unlike Linux, where syscall numbers are stable and programs may invoke syscall directly, Windows reserves the right to renumber syscalls between versions, so applications call documented functions in kernel32/ntdll that internally perform the transition. Raw syscalls are not forbidden-but-faster (they are simply unstable), the syscall instruction does exist on x86-64, and DLLs are not the only argument-passing mechanism. This is why Windows assembly targets library functions with the Microsoft x64 convention rather than raw syscalls."
        }
    ],
    "asm-5": [
        {
            "q": "What does `[rbx + rcx*4 + 8]` compute as an address?",
            "code": "mov eax, [rbx + rcx*4 + 8]",
            "options": [
                "rbx + (rcx * 4) + 8 — base plus scaled index plus displacement",
                "rbx + rcx + 4 + 8",
                "(rbx + rcx) * 4 + 8",
                "rbx * rcx * 4 + 8"
            ],
            "answer": 0,
            "why": "The addressing form is base + index*scale + displacement, so it is rbx + rcx*4 + 8.",
            "detail": "x86 effective addresses follow base + index*scale + disp, where scale is 1/2/4/8. So this is rbx (base) + rcx*4 (scaled index, e.g. indexing 4-byte ints) + 8 (displacement). It does not add rcx and 4 separately, does not multiply (rbx+rcx), and does not multiply base by index. This one form directly encodes array indexing (index*element_size) plus a struct-field offset (displacement), which is why it appears everywhere."
        },
        {
            "q": "Why do compilers sometimes use `lea rax, [rbx + rbx*4]` for arithmetic?",
            "code": "lea rax, [rbx + rbx*4]",
            "options": [
                "It reads memory at that address",
                "It computes rbx*5 in one instruction using the address unit, with no memory access",
                "It multiplies by 4 only",
                "It is a bug"
            ],
            "answer": 1,
            "why": "lea does the base+index*scale math (rbx + rbx*4 = rbx*5) and stores the number, exploiting the address unit for fast arithmetic.",
            "detail": "Because lea computes the effective address without dereferencing, compilers repurpose it as a quick multiply-add: rbx + rbx*4 = 5*rbx in a single instruction, no multiply unit needed. It does NOT access memory (that is the point — unlike mov with brackets), it is not just *4 (the base adds another rbx), and it is intentional, not a bug. Recognizing lea-as-arithmetic versus lea-as-address-of is key to reading optimized disassembly."
        },
        {
            "q": "What does this compute into eax?",
            "code": "arr dd 10, 20, 30, 40\n; rbx = address of arr, rcx = 2\nmov eax, [rbx + rcx*4]",
            "options": [
                "20",
                "The address of arr[2]",
                "30 — element index 2 of a 4-byte int array",
                "12"
            ],
            "answer": 2,
            "why": "rcx*4 (2*4=8 bytes) offsets to the third element arr[2]=30, and mov reads its value.",
            "detail": "Scale 4 matches the 4-byte int size, so rcx=2 lands on arr[2] (byte offset 8) = 30, and mov (with brackets) loads the value. It is not 20 (that is arr[1]), not the address (mov reads the value; lea would give the address), and not 12 (the scale is not added raw). This is literally how `arr[i]` compiles: base + i*element_size, then dereference."
        },
        {
            "q": "You index an array of 8-byte quadwords but use scale 4. What happens?",
            "code": "arr dq 100, 200, 300\nmov rax, [rbx + rcx*4]   ; rcx = 1",
            "options": [
                "It correctly reads arr[1]",
                "It reads arr[2]",
                "It crashes at assembly time",
                "It reads a misaligned mix of bytes from the middle of elements — garbage"
            ],
            "answer": 3,
            "why": "Scale must match element size (8 for qword); scale 4 with rcx=1 offsets only 4 bytes, landing halfway into arr[0]/arr[1].",
            "detail": "For 8-byte elements the scale should be 8. Using 4 with rcx=1 gives a 4-byte offset — halfway into the array — so mov rax reads a mix of the high half of arr[0] and low half of arr[1]: garbage. It does not correctly read arr[1] (that needs scale 8) or arr[2], and it assembles fine (the error is logical, at runtime). Matching the scale to the element size is essential; a mismatch silently corrupts array access."
        },
        {
            "q": "In disassembly you see repeated `[rax + 0x0]`, `[rax + 0x8]`, `[rax + 0x10]`. What does this suggest?",
            "code": "mov rcx, [rax + 0x0]\nmov rdx, [rax + 0x8]\nmov r8,  [rax + 0x10]",
            "options": [
                "rax points at a struct/object; the offsets are its fields at 0, 8, 16 bytes",
                "It is an array indexed by rax",
                "The code is corrupted",
                "rax is a loop counter"
            ],
            "answer": 0,
            "why": "Fixed displacements from a base pointer (0, 8, 16) are the signature of struct field access.",
            "detail": "Constant offsets off a base register — 0x0, 0x8, 0x10 — indicate fields of a struct or object at those byte positions (here three 8-byte fields). An array would use a scaled index register ([rax + rcx*8]) rather than fixed displacements. The code is not corrupted, and rax is a base pointer, not a counter. Reading displacement patterns to reconstruct struct layouts is a core reverse-engineering skill, since binaries carry no field names."
        },
        {
            "q": "How do you write a byte value 5 to memory at [rbx] unambiguously?",
            "code": "mov [rbx], 5   ; ambiguous",
            "options": [
                "mov [rbx], 5 works fine",
                "mov byte [rbx], 5 — the size qualifier tells the assembler it is one byte",
                "lea [rbx], 5",
                "mov rbx, 5"
            ],
            "answer": 1,
            "why": "Storing an immediate to memory needs a size qualifier (byte/word/dword/qword) since the assembler cannot infer the width.",
            "detail": "`mov [rbx], 5` is ambiguous — 5 could be 1, 2, 4, or 8 bytes — so you must write `mov byte [rbx], 5` (or word/dword/qword). The bare form is an assembler error (not 'fine'), lea does not store values, and `mov rbx, 5` changes the register, not the memory it points to. Size qualifiers on memory-immediate stores are required whenever the width is not otherwise determined by a register operand."
        }
    ],
    "asm-6": [
        {
            "q": "On Windows x64, where does a function's return value come back?",
            "code": "",
            "options": [
                "rcx",
                "the stack top",
                "rax (or xmm0 for floating point)",
                "rbx"
            ],
            "answer": 2,
            "why": "The return value is placed in rax (integer/pointer) or xmm0 (float), by convention across Windows and SysV.",
            "detail": "rax carries the integer/pointer return value on both Windows x64 and Linux SysV; floating-point returns use xmm0. rcx is the FIRST argument on Windows (not the return), the return value is not on the stack for normal-sized types, and rbx is a callee-saved register. Knowing rax=return is fundamental to reading any function's result and to writing functions that hand values back correctly."
        },
        {
            "q": "Which registers must a Windows x64 function PRESERVE (callee-saved)?",
            "code": "",
            "options": [
                "rax, rcx, rdx — those are caller-saved",
                "all registers",
                "none; the caller saves everything",
                "rbx, rbp, rdi, rsi, r12-r15 (and rsp) — restore them before returning"
            ],
            "answer": 3,
            "why": "Non-volatile registers (rbx, rbp, rdi, rsi, r12-r15) must be preserved by a function that uses them; the volatile ones may be freely clobbered.",
            "detail": "Callee-saved (non-volatile) registers — rbx, rbp, rdi, rsi, r12-r15 — must hold their values across a call, so a function using them pushes/pops them. Volatile (caller-saved) registers — rax, rcx, rdx, r8-r11 — may be destroyed by a callee, so the caller saves them if needed. Not all registers are preserved, and it is a shared responsibility (the split), not all-caller. This volatile/non-volatile division is why you choose non-volatile registers for values that must survive a call."
        },
        {
            "q": "You need a value to survive a call to printf. Which register is the safe choice, and why?",
            "code": "",
            "options": [
                "A non-volatile register like rbx — the ABI requires printf to preserve it",
                "rcx — it is fast",
                "rax — it holds returns",
                "r10 — it is unused"
            ],
            "answer": 0,
            "why": "Non-volatile registers are guaranteed preserved across calls, so a value in rbx survives printf; volatile ones may be destroyed.",
            "detail": "Because the ABI marks rbx non-volatile, any conforming function (including printf) must restore it, so a value kept there survives the call. rcx is volatile (an argument register printf will use), rax is volatile and holds the return, and r10/r11 are volatile scratch. Choosing a non-volatile register (and saving/restoring it yourself in your prologue/epilogue) is exactly how you carry a value across a function call in assembly."
        },
        {
            "q": "What does this prologue tell you about the function?",
            "code": "f:\n    push rbx\n    push rsi\n    sub rsp, 0x28",
            "options": [
                "It takes two stack arguments",
                "It uses rbx and rsi (saving them) and reserves shadow space + alignment (0x28 = 40)",
                "It clears rbx and rsi",
                "It is a leaf function using no stack"
            ],
            "answer": 1,
            "why": "Pushing non-volatile rbx/rsi means the function will use them and must restore them; sub rsp,0x28 is shadow space plus alignment.",
            "detail": "Saving rbx and rsi (both non-volatile) signals the function intends to use them for values that survive its own internal calls, and it must pop them before returning. The 0x28 (40-byte) reservation is the shadow-space-plus-alignment idiom, implying it calls other functions. It does not take stack arguments here, does not clear those registers (it preserves them), and it is not a leaf (it reserves shadow space for calls). Reading prologues this way reveals a function's register usage and whether it calls others."
        },
        {
            "q": "The same instruction stream means different things under Windows and Linux. Why?",
            "code": "",
            "options": [
                "The CPU decodes them differently",
                "Linux uses a different instruction set",
                "The ABIs differ — argument registers, shadow space, and volatile/non-volatile splits are not the same",
                "It does not; they are identical"
            ],
            "answer": 2,
            "why": "Windows x64 and Linux SysV are different calling conventions, so the SAME instructions imply different argument/register meanings.",
            "detail": "The CPU executes identical machine code, but the CONVENTIONS differ: Windows passes args in rcx/rdx/r8/r9 with 32-byte shadow space, while Linux uses rdi/rsi/rdx/rcx/r8/r9 with a red zone and no shadow space, and their preserved-register sets differ. So the same `mov`/`call` sequence implies different argument sources and stack layout depending on the ABI. The CPU does not decode differently, x86-64 is one instruction set, and they are not identical at the convention level. Always know which ABI you are reading."
        },
        {
            "q": "Why does reading disassembly require knowing the ABI even though the CPU ignores it?",
            "code": "",
            "options": [
                "The ABI changes the opcodes",
                "Without it the code will not run",
                "The ABI is only for compilers",
                "The ABI lets you infer argument counts, return values, and register roles that the raw instructions do not state"
            ],
            "answer": 3,
            "why": "Instructions carry no argument or type info; the ABI is the convention that lets you reconstruct a function's signature and register purposes.",
            "detail": "The CPU just executes instructions, but to UNDERSTAND them — which registers set before a call are arguments, which register holds the return, which pushes are saved non-volatiles — you apply the ABI's rules. It does not change opcodes, the code runs regardless (the CPU does not enforce the ABI; violations just produce wrong behavior), and it is for readers and analysts as much as compilers. The ABI is the Rosetta Stone that turns an untyped instruction stream back into meaningful function calls."
        }
    ]
}
