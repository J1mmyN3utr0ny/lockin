# expansions_2.py — deep-dive expansions for Lab lessons (tracks: asm, linux, cmd).
# Rendered by lockin_lab.py after the lesson body. Pure data.
EXPANSIONS = {
    "asm:0": {
        "title_check": "Registers & moving data",
        "sections": [
            {
                "h": "Register hierarchy & cache locality",
                "body": "x86-64 has 16 general-purpose registers, but they're part of a 64-bit name hierarchy: RAX (64-bit) aliases EAX (32-bit, zero-extends), AX (16-bit), AH/AL (8-bit halves). CPU cache lines are 64 bytes; using adjacent memory stalls the pipeline if not aligned. A mov qword [rsp], rax deposits 8 bytes at the stack pointer. Modern CPUs execute multiple movs per cycle via micro-ops if the operands don't conflict—but mov r64, r64 with different registers is free (register renaming), while mov r64, [mem] stalls until memory delivers."
            },
            {
                "h": "Data size & sign extension",
                "body": "Moving an 8-bit value into a 64-bit register does NOT zero the upper 56 bits unless you use movzx. movsx sign-extends (fills the upper bits with the sign bit of the source). This matters: movsxd eax, [addr] reads 32 bits from memory, sign-extends to 64-bit RAX. A common bug: mov rax, dword [mem] moves 32 bits but leaves the upper 32 bits of RAX unchanged. Always use movzx or explicit zero-extension if you need it."
            }
        ],
        "links": [
            {"label": "Felix Cloutier x86 – MOV instruction", "url": "https://felixcloutier.com/x86/"},
            {"label": "man7.org – register preservation", "url": "https://man7.org/linux/man-pages/"}
        ]
    },
    "asm:1": {
        "title_check": "Control flow & flags",
        "sections": [
            {
                "h": "The FLAGS register & condition codes",
                "body": "Compare instructions (cmp, test) set flags but don't store results. cmp rax, rbx subtracts rbx from rax, setting ZF (zero flag) if equal, CF (carry) for unsigned underflow, SF (sign flag) if result is negative, OF (overflow) for signed overflow. Conditional jumps (jz, jne, ja, js, jo) read these flags to decide. A trap: jae (jump if above or equal, unsigned) uses CF, while jge (signed >=) uses SF and OF. Mixing them is a security bug."
            },
            {
                "h": "Branch prediction & pipeline stalls",
                "body": "A jump clears the CPU's instruction pipeline unless the branch predictor guesses correctly. Modern CPUs use 2-level adaptive history—if the same jump pattern repeats, it's often predicted right. The penalty: 15+ cycles if wrong on an Intel CPU. Example: a tight loop with cmp and je usually predicts correctly the first N-1 iterations, then mispredicts the exit. Mitigating: loop-unrolling or cmov (conditional move, no branch) replaces short conditional code: cmov rax, rcx (rax = ZF ? rax : rcx)."
            }
        ],
        "links": [
            {"label": "Felix Cloutier x86 – CMP instruction", "url": "https://felixcloutier.com/x86/"},
            {"label": "man7.org – x86 branch prediction", "url": "https://man7.org/linux/man-pages/"}
        ]
    },
    "asm:2": {
        "title_check": "The stack, call & ret",
        "sections": [
            {
                "h": "Stack frames & return addresses",
                "body": "call pushes the return address (next instruction's RIP) onto the stack and jumps to the target. ret pops that address and jumps back. Stack frames group local variables and saved registers. A function prologue (push rbp; mov rbp, rsp) saves the old base pointer and sets up RBP to frame the current activation. The saved return address sits at [rsp] after the call; local variables grow downward (negative offsets from RBP). Example: sub rsp, 32 reserves 32 bytes for locals. Forgetting to align the stack before calling another function causes segment faults if that function uses SSE instructions (movaps requires 16-byte alignment)."
            },
            {
                "h": "Stack overflow & red zone pitfalls",
                "body": "The 128-byte 'red zone' below RSP (in System V AMD64 ABI) is reserved for leaf functions and signal handlers, but interrupt/exception handlers DON'T respect it, so signal handlers writing to the red zone corrupt local variables. Also, recursion without a base case quickly exhausts stack space. Detecting: the kernel raises SIGSEGV when you cross the stack limit. Deep recursion (or stack-based allocation) requires either tail-call optimization or explicit stack size management."
            }
        ],
        "links": [
            {"label": "Felix Cloutier x86 – CALL instruction", "url": "https://felixcloutier.com/x86/"},
            {"label": "man7.org – System V AMD64 ABI", "url": "https://man7.org/linux/man-pages/"}
        ]
    },
    "asm:3": {
        "title_check": "Syscalls & reading disassembly",
        "sections": [
            {
                "h": "The syscall instruction & kernel transition",
                "body": "syscall saves RIP in RCX and RFLAGS in R11, loads the kernel entry point into RIP, and switches to ring 0. Arguments go in RAX (syscall number), RDI, RSI, RDX, R10, R8, R9. Example: to read from fd 3 into buffer at rdi for 1024 bytes, use mov rax, 0 (read); mov rsi, rdi; mov rdx, 1024; mov rdi, 3; syscall. The kernel fills RAX with the byte count or error (negative values are errno). A common mistake: forgetting that R10 (not RCX) holds the 4th arg; using RCX causes ioctl and fcntl to fail."
            },
            {
                "h": "Reading disassembly & instruction prefixes",
                "body": "objdump -d shows machine code, mnemonics, and operands. Prefixes (0x48 for 64-bit, 0x66 for 16-bit) modify instruction size. rex.W (0x48) forces 64-bit registers; without it, 32-bit operands default to 64-bit in some contexts. A confusing pattern: add eax, 1 is 5 bytes (1 opcode, 4-byte immediate), but add rax, 1 is 3 bytes (rex.W, opcode, sign-extended 8-bit immediate). Longer encodings mean slower fetch-decode; compact code is faster, but clarity matters more in learning."
            }
        ],
        "links": [
            {"label": "man7.org – syscall(2)", "url": "https://man7.org/linux/man-pages/"},
            {"label": "Felix Cloutier x86 – SYSCALL instruction", "url": "https://felixcloutier.com/x86/"}
        ]
    },
    "asm:4": {
        "title_check": "Addressing modes & memory operands",
        "sections": [
            {
                "h": "Effective address calculation & LEA",
                "body": "Addressing modes compute the memory address from registers and immediates. [base + index*scale + disp] allows base, index (scaled by 1/2/4/8), and displacement. lea rax, [rbx + rcx*8 + 16] loads the address (no memory fetch); this is free for address arithmetic. mov rax, [rbx + rcx*8 + 16] fetches the 8 bytes at that address. AGU (address generation unit) runs in parallel with ALU, but multiple complex address calculations stall the pipeline. Example: lea rax, [rsi + rdi*2] + add rax, [rax + 8] requires two address computations; mov rax, [rsi + 16]; add rax, [rdi*2 + 8] is faster because the second access has a simpler address."
            },
            {
                "h": "Memory operand encoding & instruction length",
                "body": "mod-rm byte encodes register/memory operands and the addressing mode. Simple modes (direct register, [rsp]) are 2–3 bytes; complex modes ([base+index*scale+disp]) are 4+ bytes. Avoiding displacement saves instruction size: [rax] is 3 bytes, [rax + 0] is 4 bytes due to the disp8 encoding. This matters for code density and cache utilization: tighter code fits more in an L1-I cache line."
            }
        ],
        "links": [
            {"label": "Felix Cloutier x86 – LEA instruction", "url": "https://felixcloutier.com/x86/"},
            {"label": "man7.org – x86-64 memory operands", "url": "https://man7.org/linux/man-pages/"}
        ]
    },
    "asm:5": {
        "title_check": "Calling conventions & the ABI",
        "sections": [
            {
                "h": "System V AMD64 ABI register preservation",
                "body": "The ABI dictates which registers a function must preserve (callee-saved: RBX, RSP, RBP, R12-R15) and which it may clobber (caller-saved: RAX, RCX, RDX, RSI, RDI, R8-R11). If your function uses RBX, you must push it on entry and pop it on exit. RAX holds the return value; RDX:RAX for 128-bit results. Example: a function that loops over array elements can clobber RCX (loop counter) without saving it, but must save RBX if using it. Violating this breaks the caller's state silently, a hard-to-debug bug."
            },
            {
                "h": "Stack alignment & 16-byte boundary",
                "body": "Before call, RSP must be 16-byte aligned (RSP % 16 == 0). After call, RSP is misaligned by 8 (because call pushes 8 bytes). Functions with SSE instructions (movaps qword [rsp], xmm0) require alignment and will segfault if misaligned. A function prologue must adjust RSP to maintain alignment: if you push RBP, you lose 8 bytes, leaving RSP misaligned; sub rsp, N (where N is odd) fixes it. Example: push rbp; sub rsp, 8; mov rsp, rbp is the canonical 16-byte-aligned prologue for a leaf function."
            }
        ],
        "links": [
            {"label": "man7.org – System V AMD64 ABI", "url": "https://man7.org/linux/man-pages/"},
            {"label": "Felix Cloutier x86 – instruction reference", "url": "https://felixcloutier.com/x86/"}
        ]
    },
    "linux:0": {
        "title_check": "Move and manage",
        "sections": [
            {
                "h": "Inodes & hard links",
                "body": "A file's data and metadata (owner, permissions, timestamps) live in an inode. A directory is a special file containing entries that map names to inode numbers. Hard links are directory entries pointing to the same inode; deleting one doesn't delete the data until the link count reaches zero. Example: ln /etc/passwd /tmp/copy creates a hard link; both paths reference the same inode, same data. ls -i shows inode numbers. Symlinks are different: ln -s creates a symlink, a small file containing a path string that the kernel dereferences. mv (on the same filesystem) is a rename—it just updates the directory entry, not the data. Cross-filesystem moves copy and delete, which is slow for large files."
            },
            {
                "h": "File permissions & umask",
                "body": "Permissions (rwx for owner/group/other) are stored in the inode. umask masks out bits when creating files: umask 0022 makes new files 0644 (rw-r--r--) and directories 0755. A file created with mode 0666 minus umask 0022 becomes 0644. Executability for directories means 'can enter'; a non-executable directory can't be listed or traversed. Special bits: setuid runs a binary as the owner (security risk), setgid runs as the group, sticky bit prevents deletion in shared directories (/tmp)."
            }
        ],
        "links": [
            {"label": "man7.org – inode(7)", "url": "https://man7.org/linux/man-pages/"},
            {"label": "man7.org – chmod(1)", "url": "https://man7.org/linux/man-pages/"}
        ]
    },
    "linux:1": {
        "title_check": "Pipes, grep & redirection",
        "sections": [
            {
                "h": "Pipes & data flow",
                "body": "A pipe connects stdout of one process to stdin of another. The kernel allocates a 64KB buffer (Linux); when full, the writer blocks. grep filters lines matching a regex. Example: cat /etc/passwd | grep root finds the root entry. ps aux | grep ssh finds SSH processes. Buffering: if your pipeline has many slow readers, the buffer fills and the producer stalls. Unbuffering (stdbuf -o0 cmd) helps but costs CPU. A pipe requires both reader and writer; kill the reader and the writer gets SIGPIPE."
            },
            {
                "h": "Output redirection & file descriptors",
                "body": "Each process has file descriptors (0=stdin, 1=stdout, 2=stderr). > redirects stdout to a file (truncates); >> appends. 2> redirects stderr. 2>&1 merges stderr into stdout. Example: cmd > out.txt 2>&1 logs both. Redirection happens before execution; cmd 2>&1 | grep error redirects before piping. A trap: cmd | tee file | grep X writes to file AND pipes to grep, but might lose data if grep reads ahead before tee flushes."
            }
        ],
        "links": [
            {"label": "man7.org – grep(1)", "url": "https://man7.org/linux/man-pages/"},
            {"label": "man7.org – pipe(7)", "url": "https://man7.org/linux/man-pages/"}
        ]
    },
    "linux:2": {
        "title_check": "Permissions & processes",
        "sections": [
            {
                "h": "Real vs effective UID & privilege escalation",
                "body": "A process has real UID (who ran it), effective UID (used for permission checks), and saved UID. When executing a setuid binary, the kernel sets eUID to the binary's owner. Example: sudo runs as root (eUID=0), so it can read /etc/shadow. A non-setuid binary keeps eUID=rUID. seteuid(uid) lets a process drop privilege: if eUID=0, seteuid(1000) switches to user 1000. Once dropped, privilege can't be regained unless the binary was setuid and saved UID is still 0. A security principle: drop privilege as early as possible."
            },
            {
                "h": "Process hierarchy & signals",
                "body": "Every process has a parent (ppid). The init process (PID 1) is the ancestor. Killing a process leaves its children orphaned; the kernel reparents them to init. Signals interrupt a process: SIGTERM asks politely, SIGKILL forces termination (can't be caught). Example: kill -9 PID sends SIGKILL; the process has 0ms to clean up. A zombie process has exited but its parent hasn't called wait(); it wastes a PID slot. Reaping: the parent must wait or the kernel never frees the zombie entry."
            }
        ],
        "links": [
            {"label": "man7.org – setuid(2)", "url": "https://man7.org/linux/man-pages/"},
            {"label": "man7.org – signal(7)", "url": "https://man7.org/linux/man-pages/"}
        ]
    },
    "linux:3": {
        "title_check": "Your first bash script",
        "sections": [
            {
                "h": "Shebang & script execution",
                "body": "The shebang (#!) on the first line tells the kernel which interpreter to use. #!/bin/bash runs the file with /bin/bash; #!/usr/bin/env python3 finds python3 in $PATH. The kernel reads only the first line and splits on whitespace once, so #!/bin/bash -x works (runs bash with -x flag), but #!/bin/bash -x -e fails (treats -x -e as a single argument). When you run ./script, the kernel executes the shebang interpreter, passing the script path as an argument. Direct execution (source script or . script) skips the shebang and runs in the current shell."
            },
            {
                "h": "Variables & quoting",
                "body": "Double quotes expand variables and command substitution; single quotes are literal. Example: echo \"$USER\" prints the username; echo '$USER' prints the literal string. Unquoted variables split on whitespace and glob-expand: x='a b'; echo $x produces 'a b', but echo \"$x\" produces the literal string. Undeclared variables are empty; set -u makes them an error. Local variables (foo=bar) export to subshells only if exported: export PATH extends PATH in children."
            }
        ],
        "links": [
            {"label": "man7.org – bash(1)", "url": "https://man7.org/linux/man-pages/"},
            {"label": "w3schools.com – bash tutorial", "url": "https://www.w3schools.com/whatis/whatis_bash.asp"}
        ]
    },
    "linux:4": {
        "title_check": "Text processing: sort, uniq, cut, sed, awk",
        "sections": [
            {
                "h": "Sorting & uniqueness",
                "body": "sort orders lines; sort -n sorts numerically (1 < 10 < 2), sort -r reverses. sort -k2 sorts by field 2 (whitespace-delimited). uniq removes adjacent duplicates; uniq -c counts occurrences. Example: cat /var/log/auth.log | grep 'Failed' | cut -d' ' -f10 | sort | uniq -c | sort -rn shows the top failed usernames. A trap: uniq only removes consecutive duplicates; you must sort first. cut -d: -f1 extracts field 1 delimited by colons (useful for /etc/passwd parsing)."
            },
            {
                "h": "sed & awk for transformation",
                "body": "sed (stream editor) applies regex substitutions: sed 's/old/new/' replaces the first 'old' per line; sed 's/old/new/g' replaces all. Example: echo 'foo bar' | sed 's/bar/baz/' outputs 'foo baz'. awk is a programming language for line processing: awk '{print $2}' prints field 2. awk '/pattern/ {print}' prints matching lines. Example: ps aux | awk '$3 > 50 {print $2, $11}' finds processes using >50% CPU and prints PID and command. Both tools work line-by-line; large files stream efficiently."
            }
        ],
        "links": [
            {"label": "man7.org – sed(1)", "url": "https://man7.org/linux/man-pages/"},
            {"label": "man7.org – awk(1)", "url": "https://man7.org/linux/man-pages/"}
        ]
    },
    "linux:5": {
        "title_check": "SSH, networking & packages",
        "sections": [
            {
                "h": "SSH keys & public-key authentication",
                "body": "SSH uses asymmetric cryptography: a private key (kept secret, ~/.ssh/id_rsa) and public key (uploaded to the server, ~/.ssh/authorized_keys). The server signs a challenge with your public key; only the private key can decrypt it, proving identity without transmitting the password. Example: ssh-keygen -t rsa -N '' generates a keypair; ssh-copy-id user@host installs your public key. ssh -i /path/key uses a specific key. A passphrase protects the private key if stolen, but defeats password-less login (use ssh-agent to cache it). Ed25519 keys are smaller and faster than RSA; prefer them for new keys."
            },
            {
                "h": "Package managers & dependencies",
                "body": "apt (Debian/Ubuntu) and yum/dnf (Red Hat) manage software. apt update fetches package lists; apt install foo installs a package. apt-cache search keyword finds packages; apt-file list package shows files in a package. Dependencies are automatic: apt install vim installs vim and its dependencies. A conflict: two packages provide the same file or require incompatible versions. apt hold marks a package to skip upgrades. dpkg -l lists installed packages. Uninstalling: apt remove foo keeps config files; apt purge foo deletes them."
            }
        ],
        "links": [
            {"label": "man7.org – ssh(1)", "url": "https://man7.org/linux/man-pages/"},
            {"label": "man7.org – apt(8)", "url": "https://man7.org/linux/man-pages/"}
        ]
    },
    "cmd:0": {
        "title_check": "Files & navigation",
        "sections": [
            {
                "h": "NTFS, file handles & directory traversal",
                "body": "Windows NTFS stores files in a B-tree indexed by filename within each directory. dir lists files; dir /s recurses subdirectories. Type (or Get-Content in PowerShell) reads file contents. A path like C:\\\\Users\\\\username\\\\Desktop uses backslashes. UNC paths (\\\\\\\\server\\\\share) access network drives. File handles are kernel objects; opening too many (without closing) exhausts the handle table. Example: for %F in (*.txt) do type %F prints each .txt file. Directory traversal follows symlinks (mklink) and junctions; a circular symlink causes infinite loops in recursive operations."
            },
            {
                "h": "Attributes & NTFS streams",
                "body": "Files have attributes (hidden, system, read-only). attrib +h file.txt hides it; attrib -r removes read-only. NTFS supports alternate data streams: file.txt:stream holds metadata without changing file size. Example: dir /s in PowerShell shows standard data; streams are hidden. del file:stream removes a stream. Compressed files save space on disk. icacls shows and modifies access control lists (ACLs), which are more fine-grained than Unix permissions."
            }
        ],
        "links": [
            {"label": "learn.microsoft.com – Windows commands", "url": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands"},
            {"label": "learn.microsoft.com – dir command", "url": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/dir"}
        ]
    },
    "cmd:1": {
        "title_check": "Network commands",
        "sections": [
            {
                "h": "TCP/IP diagnostics & trace routes",
                "body": "ipconfig /all shows network adapters and IP addresses; ipconfig /release and /renew cycle DHCP. ping host tests reachability by sending ICMP echo requests. Example: ping 8.8.8.8 checks internet connectivity. netstat -an lists active connections and listening ports (state ESTABLISHED, LISTEN). Example: netstat -an | find ':443' shows HTTPS connections. A listening port like LISTENING 0.0.0.0:8080 means all interfaces. tracert (like Linux traceroute) shows the path to a host: tracert example.com prints the hops. nslookup hostname resolves DNS; nslookup 1.1.1.1 does reverse lookup."
            },
            {
                "h": "Connection troubleshooting",
                "body": "netstat -ano shows process IDs (PID) owning ports; tasklist finds the process name by PID. Example: netstat -ano | find ':8080' + tasklist /fi 'PID eq 1234' identifies which app uses port 8080. getmac shows MAC addresses. arp -a shows the ARP cache (IP to MAC mappings). firewall rules (netsh advfirewall) block or allow ports. A common issue: port conflicts when multiple services bind to the same port; the first wins, others fail silently."
            }
        ],
        "links": [
            {"label": "learn.microsoft.com – netstat", "url": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat"},
            {"label": "learn.microsoft.com – ipconfig", "url": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig"}
        ]
    },
    "cmd:2": {
        "title_check": "Live recon",
        "sections": [
            {
                "h": "Process enumeration & WMI queries",
                "body": "tasklist /v shows running processes with detailed info (PID, memory, user). tasklist /fi 'USERNAME eq DOMAIN\\\\user' filters by user. tasklist /fi 'STATUS eq running' shows active processes. Get-Process (PowerShell) is more powerful: Get-Process | Where-Object {$_.WorkingSet -gt 100MB} finds memory hogs. wmic process list brief queries via WMI. Example: wmic process get name,processid,workingsetsize returns process inventory. Priorities (tasklist /fi 'PRIORITY eq high') and CPU usage reveal resource contention."
            },
            {
                "h": "Registry & system information",
                "body": "reg query HKLM\\\\Software lists registry keys. Example: reg query HKLM\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion lists Windows version info. systeminfo dumps OS details (build, memory, network). whoami /priv shows current user privileges. A red flag: SeDebugPrivilege or SeTcbPrivilege means elevated rights. Get-LocalUser lists user accounts. Scheduled tasks: tasklist /v | find /i 'schtasks' or wmic scheduledtask list show automation. Security event logs (Event Viewer, wevtutil qe Security /c:10) reveal login attempts, privilege changes, and failed operations."
            }
        ],
        "links": [
            {"label": "learn.microsoft.com – wmic", "url": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wmic"},
            {"label": "learn.microsoft.com – reg command", "url": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg"}
        ]
    },
    "cmd:3": {
        "title_check": "Script it with .bat",
        "sections": [
            {
                "h": "Batch file parsing & control flow",
                "body": "Batch files (.bat) are line-by-line; comments start with REM. Variables use %name% (set name=value). Example: @echo off; set user=%USERNAME%; echo Hello %user%. Delayed expansion (setlocal enabledelayedexpansion) uses !var! to expand inside loops (percent expansion happens once before the loop). Control flow: if %x%==1 goto label; goto end; :label; ... :end. for loops: for %%A in (*.txt) do echo %%A iterates files. Batch is interpreted, not compiled, so it's slow; recursion and deep loops stall. User input: set /p var='Prompt: ' reads a line."
            },
            {
                "h": "Environment & exit codes",
                "body": "Commands return exit codes (0 = success, non-zero = error). if errorlevel 1 checks the last code. Example: cmd /c 'exit /b 5'; if errorlevel 5 echo failed. Chaining: command1 && command2 runs 2 only if 1 succeeds; || runs on failure. A trap: exit /b 0 exits the batch; missing /b kills the parent shell. call subroutine.bat invokes another batch file. Scope: set x=1 is global; setlocal / endlocal creates a scope (changes inside endlocal are discarded)."
            }
        ],
        "links": [
            {"label": "learn.microsoft.com – batch file commands", "url": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands"},
            {"label": "learn.microsoft.com – for command", "url": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/for"}
        ]
    },
    "cmd:4": {
        "title_check": "PowerShell basics (and when to use it)",
        "sections": [
            {
                "h": "Object pipelines & type system",
                "body": "PowerShell pipes objects (not text strings like Unix shells). Get-Process returns process objects; piping to Select-Object, Where-Object filters them. Example: Get-Process | Where-Object {$_.CPU -gt 50} | Select-Object -Property Name, Id finds processes over 50% CPU, showing name and ID. Object properties are accessed via $_.Property. Piping to Format-Table or Format-List displays results. A difference from Unix: Get-Process | grep chrome fails because grep expects strings; use Select-String or Where-Object {$_.Name -match 'chrome'} instead."
            },
            {
                "h": "Execution policy & script safety",
                "body": "Execution policies prevent accidental script execution: Restricted (default) blocks scripts; AllSigned requires signing; RemoteSigned allows local scripts. Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser allows unsigned scripts for the current user. A trap: Set-ExecutionPolicy is per-scope (CurrentUser, LocalMachine); changing one doesn't change the other. Scripts (.ps1) require explicit paths: . .\\script.ps1 (dot-sourcing) runs in the current scope; & .\\script.ps1 runs in a subshell. Cmdlets (verbs-noun): Get-Help topic, Get-ChildItem, Set-Variable, Start-Process. Aliases (ls = Get-ChildItem) speed typing but complicate scripts."
            }
        ],
        "links": [
            {"label": "learn.microsoft.com – PowerShell cmdlets", "url": "https://learn.microsoft.com/en-us/powershell/"},
            {"label": "learn.microsoft.com – execution policies", "url": "https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies"}
        ]
    },
    "cmd:5": {
        "title_check": "Environment, tasks & scheduling",
        "sections": [
            {
                "h": "Environment variables & scope",
                "body": "setx VAR value sets an environment variable permanently (writes to registry); set VAR value sets it only for the current shell session. Example: setx PATH %PATH%;C:\\\\NewPath appends to PATH. User variables (HKCU) and system variables (HKLM) have different scope; system variables require admin. get-item env:VAR (PowerShell) reads a variable. A gotcha: changing PATH via setx doesn't affect the current cmd window; close and reopen. Special variables: %USERPROFILE% = home, %TEMP% = temp directory, %OS% = operating system. Environment variable expansion happens once when the command line is parsed; avoid circular references (VAR=%VAR%;new)."
            },
            {
                "h": "Task Scheduler & persistence",
                "body": "tasklist /fi 'STATUS eq running' shows running tasks; schtasks /query lists scheduled tasks. schtasks /create /tn 'TaskName' /tr 'command' /sc hourly schedules a task hourly. A task runs under a specific user (SYSTEM, LOCAL SERVICE, or a user account). Example: schtasks /create /tn 'Backup' /tr 'C:\\\\backup.bat' /sc daily /st 02:00 runs backup daily at 2 AM. Tasks can be triggered on logon, system boot, or event log entries. Attackers abuse task scheduler for persistence; detecting: look for tasks with suspicious commands or unusual schedules. Removal: schtasks /delete /tn 'TaskName' /f."
            }
        ],
        "links": [
            {"label": "learn.microsoft.com – environment variables", "url": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setx"},
            {"label": "learn.microsoft.com – schtasks", "url": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks"}
        ]
    }
}
