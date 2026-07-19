# quizbank_cmd.py - additional graded checks for the cmd track.
# Merged onto each lesson's existing quiz by content.build_courses().
# Answer indices balanced across the file so the correct option isn't always first.
EXTRA_QUIZ = {
    "cd-1": [
        {
            "q": "From the C: prompt, what does `cd D:\\data` do?",
            "code": "C:\\> cd D:\\data",
            "options": [
                "Sets D's remembered directory to \\data but leaves you on C: — you must use cd /d to switch drives",
                "Switches you to D:\\data",
                "Errors out",
                "Creates D:\\data"
            ],
            "answer": 0,
            "why": "CMD tracks a current directory per drive; cd alone changes another drive's directory without moving you there.",
            "detail": "Because CMD keeps a separate current directory for each drive, `cd D:\\data` only updates D's remembered location; you stay on C:. To actually switch drive AND directory you use `cd /d D:\\data` (or type `D:` then cd). It does not switch you (that is the trap), does not error, and does not create anything. This per-drive-current-directory quirk surprises everyone coming from Unix's single tree."
        },
        {
            "q": "What does `dir /b` output?",
            "code": "dir /b",
            "options": [
                "Hidden files only",
                "Bare filenames only — no size, date, or header, ideal for scripting",
                "A recursive listing",
                "Files sorted by size"
            ],
            "answer": 1,
            "why": "/b gives 'bare' output — just names, one per line — which is easy for scripts to consume.",
            "detail": "`dir /b` strips the header, size, and date columns, printing only filenames one per line, which is convenient to pipe into other commands or loop over. /a shows hidden/system files, /s recurses, and /o-s would sort by size. The bare format is the CMD analogue of a clean `ls` for scripting, avoiding the need to parse dir's verbose default output."
        },
        {
            "q": "What is the key difference between CMD and PowerShell?",
            "code": "",
            "options": [
                "They are the same shell",
                "CMD is newer",
                "PowerShell passes OBJECTS with properties between commands; CMD passes plain text",
                "PowerShell cannot run programs"
            ],
            "answer": 2,
            "why": "PowerShell's pipeline carries structured objects (with typed properties), while CMD pipes unstructured text.",
            "detail": "The defining difference is that PowerShell commands emit objects you can filter by real properties (Get-ChildItem | Where Length -gt 1MB), whereas CMD emits text you must parse. They are not the same, CMD is the OLDER shell (PowerShell is newer and built on .NET), and PowerShell certainly runs programs. This object-vs-text distinction is why PowerShell is far more robust for automation, while CMD remains valued for ubiquity and simplicity."
        },
        {
            "q": "Why does `cd \"C:\\Program Files\"` need the quotes?",
            "code": "cd \"C:\\Program Files\"",
            "options": [
                "Quotes are never needed",
                "Quotes make it case-sensitive",
                "Quotes hide the folder",
                "The space would otherwise split the path into two arguments; quotes keep it as one"
            ],
            "answer": 3,
            "why": "Without quotes the space breaks the path into separate arguments; quoting keeps 'Program Files' as a single path.",
            "detail": "Spaces separate arguments, so `cd C:\\Program Files` would pass 'C:\\Program' and 'Files' as two things; quoting the whole path keeps it intact. Quotes are needed exactly when a path contains spaces (not never), do not affect case (Windows paths are case-insensitive regardless), and do not hide anything. Quoting space-containing paths is a constant necessity on Windows, where 'Program Files' and similar are everywhere."
        },
        {
            "q": "What does `type file.txt` do?",
            "code": "type file.txt",
            "options": [
                "Prints the file's contents to the screen (like Unix cat)",
                "Shows the file's type/extension",
                "Creates the file",
                "Deletes the file"
            ],
            "answer": 0,
            "why": "type displays a text file's contents, the CMD equivalent of Unix cat.",
            "detail": "`type file.txt` dumps the file contents to the console — CMD's counterpart to `cat`. It does not report the file's type despite the name, does not create it (that would be `echo. > file` or copy con), and does not delete it (that is del). Knowing CMD-to-Unix command mappings (type=cat, dir=ls, copy=cp, del=rm, move=mv) helps when switching between the two shells."
        },
        {
            "q": "What does `del *.tmp` do, and what makes it risky?",
            "code": "del *.tmp",
            "options": [
                "Moves them to the Recycle Bin",
                "Deletes all .tmp files in the current directory with no Recycle Bin — gone permanently",
                "Lists them",
                "Renames them"
            ],
            "answer": 1,
            "why": "del removes files immediately without sending them to the Recycle Bin, so a wrong wildcard is irreversible.",
            "detail": "`del *.tmp` permanently removes matching files — del from CMD bypasses the Recycle Bin, so there is no easy undo, making a mistaken wildcard (or wrong directory) dangerous. It does not go to the Recycle Bin, does not list (that is dir), and does not rename (ren). Because del is irreversible, previewing with `dir *.tmp` before deleting, and using /p to prompt, are prudent habits — the same caution as Unix rm."
        }
    ],
    "cd-2": [
        {
            "q": "What does `ipconfig /all` show that plain `ipconfig` does not?",
            "code": "ipconfig /all",
            "options": [
                "Nothing extra",
                "Only the default gateway",
                "Full details: MAC addresses, DHCP status, DNS servers, and lease info",
                "The routing table"
            ],
            "answer": 2,
            "why": "/all gives the complete interface configuration including MAC, DHCP, DNS, and lease times, not just addresses.",
            "detail": "Plain ipconfig shows IP addresses and the gateway; `/all` adds MAC (physical) addresses, whether DHCP is enabled, the DNS servers in use, and lease details — the go-to for full network configuration. It shows much more than nothing, more than just the gateway, and the routing table is a separate command (`route print`). `ipconfig /all` is the first command for understanding a Windows machine's network setup."
        },
        {
            "q": "What does `netstat -ano` reveal, and why is the -o important?",
            "code": "netstat -ano",
            "options": [
                "Only the IP address",
                "The DNS cache",
                "Installed programs",
                "All connections and listening ports with numeric addresses AND the owning process ID (PID)"
            ],
            "answer": 3,
            "why": "-a all connections/ports, -n numeric, -o the owning PID — so you see not just open ports but which process owns each.",
            "detail": "`netstat -ano` lists every connection and listening port (-a), with numeric addresses/ports for speed (-n), and crucially the PID of the owning process (-o), which you then map with tasklist. Without -o you know a port is open but not what opened it — half the story in incident response. It is more than an IP, not the DNS cache (`ipconfig /displaydns`), and not installed programs. Mapping ports to processes is essential for spotting malware or unexpected services."
        },
        {
            "q": "You run `netstat -ano`, find suspicious port 4444 with PID 5678. How do you identify the program?",
            "code": "netstat -ano | findstr :4444",
            "options": [
                "tasklist | findstr 5678 — maps the PID to its executable name",
                "ipconfig 5678",
                "del 5678",
                "ping 5678"
            ],
            "answer": 0,
            "why": "tasklist lists processes with PIDs; filtering by the PID reveals the executable behind the connection.",
            "detail": "`tasklist | findstr 5678` finds the process with PID 5678, showing its image name — connecting the suspicious port to a concrete program. ipconfig is for network config (not PIDs), del deletes files, and ping tests reachability — none map a PID to a program. This netstat-then-tasklist workflow (find the port's PID, then name the process) is the standard way to investigate a suspicious connection on Windows."
        },
        {
            "q": "Why can a failed `ping host` NOT prove the host is down?",
            "code": "ping host",
            "options": [
                "ping is unreliable software",
                "Many hosts and firewalls block ICMP echo, so a live server can still ignore pings",
                "ping only works locally",
                "A failed ping always means down"
            ],
            "answer": 1,
            "why": "ICMP (which ping uses) is frequently firewalled, so a non-responding host may simply be dropping pings while serving traffic.",
            "detail": "ping relies on ICMP echo, which many firewalls and hosts block for security, so a server can be fully operational yet not answer pings. It is not that ping is buggy or local-only, and a failed ping definitely does NOT always mean the host is down (the misconception this targets). To truly test a service, check its actual port (with a tool or PowerShell's Test-NetConnection) rather than trusting ping alone."
        },
        {
            "q": "What does `nslookup example.com 8.8.8.8` do differently from `nslookup example.com`?",
            "code": "nslookup example.com 8.8.8.8",
            "options": [
                "Nothing different",
                "Pings the domain",
                "Queries a SPECIFIC DNS server (8.8.8.8) instead of your default resolver",
                "Changes your DNS server permanently"
            ],
            "answer": 2,
            "why": "Naming a server after the domain directs the query to that resolver, useful for comparing answers or bypassing a local cache.",
            "detail": "Appending 8.8.8.8 sends the DNS query to Google's resolver rather than your configured one, letting you check whether different servers return different results (spotting stale caches or DNS-based redirection). It does something different from the default, does not ping, and does NOT change your system DNS permanently (it is a one-off query). Querying a specific resolver is a handy diagnostic and reconnaissance technique."
        },
        {
            "q": "What does `arp -a` display, and why is it useful?",
            "code": "arp -a",
            "options": [
                "All DNS records",
                "The routing table",
                "Your public IP",
                "The ARP cache: IP-to-MAC mappings of machines recently contacted on the local network"
            ],
            "answer": 3,
            "why": "arp -a shows cached IP-to-MAC mappings, revealing which local machines this host has recently talked to.",
            "detail": "The ARP cache maps local IP addresses to MAC addresses for machines the host has recently communicated with, so `arp -a` hints at network neighbors worth investigating. It is not DNS records (nslookup), the routing table (route print), or your public IP (which NAT hides). On a local network, the ARP cache is a quiet source of reconnaissance data about nearby devices, useful in both defense and authorized testing."
        }
    ],
    "cd-3": [
        {
            "q": "What does `whoami /priv` show, and why does it matter?",
            "code": "whoami /priv",
            "options": [
                "Your account's privileges (like SeDebugPrivilege), which determine what powerful actions you can take",
                "Your password",
                "Your IP address",
                "The current time"
            ],
            "answer": 0,
            "why": "It lists the security privileges held by your token; certain privileges enable powerful, security-relevant actions.",
            "detail": "`whoami /priv` enumerates your privileges — some, like SeDebugPrivilege or SeImpersonatePrivilege, are significant because they enable powerful operations relevant to privilege escalation. It does not reveal your password (never stored in readable form), your IP (ipconfig), or the time. Checking your own privileges is an early recon step: it tells you what you can already do on a system before considering anything further."
        },
        {
            "q": "What does `net localgroup administrators` list?",
            "code": "net localgroup administrators",
            "options": [
                "All local files",
                "The members of the local Administrators group — the high-privilege accounts",
                "Network shares",
                "Running processes"
            ],
            "answer": 1,
            "why": "It enumerates who belongs to the Administrators group, identifying accounts with full local control.",
            "detail": "`net localgroup administrators` shows which users are local admins — the accounts that can do nearly anything on the machine, so they are high-value both to defend and (in authorized testing) to understand. It does not list files, shares (`net share`), or processes (tasklist). Enumerating administrators is a standard recon step because those accounts define the machine's most powerful access."
        },
        {
            "q": "What does `sc qc <service>` reveal that is security-relevant?",
            "code": "sc qc spooler",
            "options": [
                "The service's memory usage",
                "The service's network traffic",
                "The service's binary path and the account it runs as — a misconfigured one can be an escalation avenue",
                "Nothing useful"
            ],
            "answer": 2,
            "why": "sc qc shows a service's executable path and run-as account; a writable path or unquoted path running as SYSTEM is a classic weakness.",
            "detail": "`sc qc` displays a service's configuration, including the binary it runs and the account (e.g., SYSTEM) it runs under. A service running as SYSTEM with a writable binary or an unquoted path with spaces is a well-known privilege-escalation avenue that defenders audit and testers check. It is not memory usage (tasklist) or network traffic, and it is very useful. Inspecting service configs is a core part of enumerating a Windows machine's weak points."
        },
        {
            "q": "Why does `systeminfo` matter for security assessment?",
            "code": "systeminfo",
            "options": [
                "It lists your files",
                "It shows your password",
                "It changes the OS version",
                "It shows the OS build and installed patches (hotfixes); missing patches map to known vulnerabilities"
            ],
            "answer": 3,
            "why": "systeminfo reveals the exact OS version and patch level, letting you match missing updates to known CVEs.",
            "detail": "`systeminfo` dumps OS version, build number, installed hotfixes, architecture, and domain membership; the patch list is security-relevant because unpatched systems are vulnerable to known exploits tied to specific missing updates. It does not list files, show passwords, or change anything (it is read-only). Identifying the precise build and patch level is how an assessor gauges a machine's attack surface from known vulnerabilities."
        },
        {
            "q": "Your recon commands return partial data. What is the most likely cause?",
            "code": "tasklist /v",
            "options": [
                "You lack administrator rights, so commands silently omit information about other users' processes/services",
                "The commands are broken",
                "The machine has no processes",
                "You must reinstall Windows"
            ],
            "answer": 0,
            "why": "Many enumeration commands need elevation; without admin they silently return only what your privilege level permits.",
            "detail": "Commands like `tasklist /v` (other users' processes), `netstat -anob` (executable names), and many service queries require administrator rights and quietly show less without them — so incomplete output often reflects your privilege level, not the machine's true state. The commands are not broken, the machine certainly has processes, and reinstalling is absurd. Recognizing that your privileges shape what you can see prevents drawing wrong conclusions during enumeration."
        },
        {
            "q": "What is the essential constraint on running recon commands like these?",
            "code": "",
            "options": [
                "They require an internet connection",
                "They must only be run on systems you own or are explicitly authorized to test",
                "They only work on Linux",
                "They must run as a scheduled task"
            ],
            "answer": 1,
            "why": "Enumeration is a security-relevant activity; on someone else's system the same commands are reconnaissance and require authorization.",
            "detail": "The same commands that audit your own machine constitute reconnaissance on another's, and the only difference is permission — so they must be run only where you have ownership or explicit authorization (a pentest engagement, a lab, your own systems). They do not require the internet, are Windows commands (not Linux-only), and need not be scheduled. Operating strictly within authorized scope is a non-negotiable rule of all security work, not just a technicality."
        }
    ],
    "cd-4": [
        {
            "q": "Why must you use `%%f` instead of `%f` for a FOR variable inside a .bat file?",
            "code": "for %%f in (*.txt) do echo %%f",
            "options": [
                "They are interchangeable",
                "%f is for numbers",
                "Batch files require doubled percent (%%f); a single %f is only for the interactive prompt",
                "%%f is a syntax error"
            ],
            "answer": 2,
            "why": "Inside a batch file FOR variables use %%; at the command prompt they use a single %, so the same loop needs different syntax.",
            "detail": "In a .bat file you must write `%%f`, but typed directly at the prompt it is `%f` — the same loop, different syntax depending on context, which is why copy-pasting between them fails. They are not interchangeable, %f is not for numbers, and %%f is correct (not an error) in a batch file. This single-versus-double percent rule is a classic batch gotcha that breaks loops mysteriously."
        },
        {
            "q": "What does `set /a count=count+1` do that `set count=count+1` does not?",
            "code": "set /a count=count+1",
            "options": [
                "Nothing different",
                "/a makes it a string",
                "/a prompts for input",
                "/a performs ARITHMETIC, so count becomes the number+1; without /a it stores the literal text 'count+1'"
            ],
            "answer": 3,
            "why": "set /a evaluates the expression numerically; plain set assigns the literal string, so 'count+1' would be stored verbatim.",
            "detail": "`set /a` treats the right side as an arithmetic expression, incrementing count numerically. Plain `set count=count+1` would literally store the text 'count+1'. /a does not make it a string (it does the opposite), and /p (not /a) prompts for input. The /a switch is required for any math in batch, and forgetting it is why arithmetic 'does not work' — the value ends up as a string expression instead of a number."
        },
        {
            "q": "What is the bug, and how is it fixed?",
            "code": "set count=0\nfor %%f in (a b c) do (\n    set /a count=count+1\n    echo %count%\n)",
            "options": [
                "%count% is expanded when the block is parsed, so it always prints 0; use delayed expansion !count!",
                "The loop is infinite",
                "set /a is wrong",
                "echo needs quotes"
            ],
            "answer": 0,
            "why": "The whole parenthesized block is parsed once before running, so %count% is the pre-loop value (0); !count! with delayed expansion reads the current value.",
            "detail": "Batch expands %var% when it parses a block, so inside the loop %count% is frozen at its pre-loop value (0) even as set /a updates it. The fix is `setlocal enabledelayedexpansion` at the top and `!count!` (exclamation marks) which expand at execution time, printing 1, 2, 3. The loop is not infinite, set /a is correct, and quotes are irrelevant. This delayed-expansion trap is THE most common batch bug with loop variables."
        },
        {
            "q": "Why do errors not stop a batch script by default?",
            "code": "",
            "options": [
                "Errors always halt the script",
                "Batch continues to the next line after a failed command; you must check %errorlevel% explicitly",
                "Batch cannot detect errors",
                "Only syntax errors stop it"
            ],
            "answer": 1,
            "why": "By default batch ignores command failures and proceeds, so a failed cd followed by del could run in the wrong place.",
            "detail": "Unlike bash with `set -e`, batch plows on after a command fails, so you must test `%errorlevel%` (0 usually means success) after important commands and `exit /b 1` on failure, or the script continues in a broken state — dangerous if, say, a failed cd is followed by a delete. Errors do not auto-halt, batch CAN detect them (via errorlevel), and it is not limited to syntax errors. Explicit error checking is the batch equivalent of bash's safety flags."
        },
        {
            "q": "What does `for /f \"tokens=1,2 delims=,\" %%a in (data.csv) do echo %%a %%b` do?",
            "code": "for /f \"tokens=1,2 delims=,\" %%a in (data.csv) do echo %%a %%b",
            "options": [
                "Reads the whole file as one string",
                "Only reads the first line",
                "Reads each line of data.csv, splitting on commas into %%a and %%b (the first two fields)",
                "Deletes data.csv"
            ],
            "answer": 2,
            "why": "for /f parses each line, delims=, sets the separator, and tokens=1,2 assigns the first two fields to %%a and %%b.",
            "detail": "`for /f` iterates file lines; `delims=,` splits on commas and `tokens=1,2` puts field one in %%a and field two in the next variable %%b (tokens auto-assign to consecutive letters). So it prints the first two CSV columns of every line — batch's version of cut/awk. It does not read the file as one string, is not limited to the first line, and does not delete anything. `for /f` with tokens and delims is the batch tool for parsing structured text."
        },
        {
            "q": "What does the shebang-like first line `@echo off` accomplish?",
            "code": "@echo off",
            "options": [
                "Turns off the computer",
                "Disables error messages",
                "Runs the script silently with no output",
                "Stops CMD from printing each command before running it (the @ also hides this line itself)"
            ],
            "answer": 3,
            "why": "echo off suppresses the echoing of each command line; the leading @ hides the echo off command itself.",
            "detail": "By default CMD prints every command as it executes; `echo off` disables that so only real output shows, and the `@` prefix suppresses printing of the echo off line too. It does not turn off the computer, disable error messages (those still appear), or silence all output (the script's actual output still prints). `@echo off` at the top of a batch file gives clean output and is near-universal in .bat scripts."
        }
    ],
    "cd-5": [
        {
            "q": "In PowerShell, why is `Get-ChildItem | Where-Object {$_.Length -gt 1MB}` more robust than parsing `dir` text?",
            "code": "Get-ChildItem | Where-Object {$_.Length -gt 1MB}",
            "options": [
                "It filters on the real .Length PROPERTY of file objects, with no fragile text parsing",
                "It runs faster only",
                "dir cannot list files",
                "PowerShell converts everything to text first"
            ],
            "answer": 0,
            "why": "PowerShell pipes objects, so you filter by a typed property (.Length) directly instead of scraping columns from text.",
            "detail": "Get-ChildItem returns file objects with a numeric .Length property, so Where-Object compares it directly and reliably — no parsing of dir's formatted text, which could break if the format changes. The benefit is robustness (typed properties), not merely speed; dir can list files; and PowerShell does NOT convert to text first (that is exactly what it avoids). Operating on objects rather than text is the core reason PowerShell is better for automation."
        },
        {
            "q": "Why does `if ($x > 5)` NOT compare x to 5 in PowerShell?",
            "code": "if ($x > 5) { ... }",
            "options": [
                "It compares correctly",
                "> is redirection in PowerShell; comparison uses word operators like -gt",
                "> means greater-than here",
                "$x must be quoted"
            ],
            "answer": 1,
            "why": "PowerShell uses -gt/-lt/-eq for comparison because < and > are reserved for redirection; `$x > 5` writes output to a file named 5.",
            "detail": "In PowerShell `>` redirects output to a file, so `if ($x > 5)` actually writes $x to a file called '5' and the condition sees the result — not a comparison. Comparison operators are words: -gt, -lt, -eq, -ne, -ge, -le. So it does not compare correctly, > does not mean greater-than, and quoting $x is not the fix. This is a frequent trap for people bringing C/JavaScript comparison habits to PowerShell."
        },
        {
            "q": "Why must Format-Table appear at the END of a pipeline?",
            "code": "Get-Process | Format-Table | Where-Object CPU -gt 100   # broken",
            "options": [
                "Format-Table must be first",
                "It works anywhere",
                "Format-* emits display-formatting objects that later cmdlets cannot process, so filtering after it breaks",
                "Format-Table deletes data"
            ],
            "answer": 2,
            "why": "Formatting cmdlets convert objects into display-only formatting objects, so any Where-Object/Export after them receives unusable input.",
            "detail": "Format-Table and Format-List produce objects meant only for on-screen display, not further processing, so a Where-Object or Export-Csv placed after them sees formatting objects instead of the real data and fails. So it must be LAST (not first), does not work anywhere, and does not delete data (it just transforms for display). The rule 'filter and select first, format last' is essential to correct PowerShell pipelines."
        },
        {
            "q": "What does `$_` represent in `Where-Object {$_.Name -like '*.log'}`?",
            "code": "Get-ChildItem | Where-Object {$_.Name -like '*.log'}",
            "options": [
                "A global variable",
                "The previous command's name",
                "An error placeholder",
                "The current object being processed in the pipeline (each file, here)"
            ],
            "answer": 3,
            "why": "$_ is the automatic variable for the current pipeline object, so $_.Name is each item's Name property.",
            "detail": "Inside a script block, `$_` (or `$PSItem`) refers to the object currently flowing through the pipeline, so `$_.Name` accesses that file's Name and `-like '*.log'` does wildcard matching. It is not a global variable, the previous command's name, or an error placeholder. Understanding `$_` as 'the current item' is fundamental to using Where-Object, ForEach-Object, and other pipeline cmdlets."
        },
        {
            "q": "What does `try { } catch { }` give PowerShell that batch lacks?",
            "code": "try { Risky } catch { Write-Error $_ }",
            "options": [
                "Real structured error handling — catch runs on a terminating error, unlike batch's errorlevel checks",
                "Faster execution",
                "Automatic retries",
                "Nothing; batch has try/catch too"
            ],
            "answer": 0,
            "why": "PowerShell supports try/catch for terminating errors (with -ErrorAction Stop), far cleaner than batch's manual %errorlevel% tests.",
            "detail": "PowerShell's try/catch catches terminating errors (and you promote non-terminating ones with -ErrorAction Stop), giving structured, readable error handling. Batch has no try/catch — it relies on checking %errorlevel% after each command. It is about correctness/structure, not speed or automatic retries, and batch definitely lacks try/catch. Real error handling is one of the main reasons PowerShell scales to serious automation where batch becomes fragile."
        },
        {
            "q": "Running a .ps1 script gives 'running scripts is disabled on this system'. What is this?",
            "code": "",
            "options": [
                "A syntax error in the script",
                "The Execution Policy — a safety setting controlling whether scripts may run; adjust it appropriately per scope",
                "The script is corrupted",
                "PowerShell is not installed"
            ],
            "answer": 1,
            "why": "The Execution Policy is a security control that restricts script execution; you set it for the appropriate scope rather than disabling security blindly.",
            "detail": "The Execution Policy governs whether and which .ps1 scripts can run (Restricted, RemoteSigned, etc.) as a safeguard against running untrusted scripts. It is not a syntax error, corruption, or a missing install (PowerShell clearly ran to give the message). The right response is to understand it and set it suitably for your scope (e.g., RemoteSigned for CurrentUser), treating it as the security control it is rather than reflexively turning protection off."
        }
    ],
    "cd-6": [
        {
            "q": "What is the difference between `set NAME=value` and `setx NAME value`?",
            "code": "set PATH=...\nsetx PATH ...",
            "options": [
                "They are identical",
                "setx is temporary, set is permanent",
                "set changes only the current session (temporary); setx writes a PERSISTENT variable for future sessions",
                "setx affects the current session immediately"
            ],
            "answer": 2,
            "why": "set is session-only and vanishes when the window closes; setx persists to the registry for future sessions but does NOT change the current one.",
            "detail": "`set` creates a variable in the current process only, gone when you close the shell; `setx` writes it persistently (to the registry) so future sessions inherit it — but crucially setx does NOT affect the CURRENT session, so you often need both. They are not identical, the roles are not reversed (set=temporary, setx=persistent), and setx does not update the running session. This session-versus-persistent distinction causes the frequent 'I set it but it did not take' confusion."
        },
        {
            "q": "Why does the ORDER of directories in PATH matter?",
            "code": "PATH=C:\\A;C:\\B",
            "options": [
                "Order is irrelevant",
                "Later directories always win",
                "PATH ignores duplicates automatically",
                "PATH is searched left to right, so a program in an earlier directory wins if two share a name (a hijack risk)"
            ],
            "answer": 3,
            "why": "The shell searches PATH entries left to right and runs the first match, so an earlier directory can shadow a later program.",
            "detail": "When you type a command, Windows searches PATH directories in order and runs the first matching executable, so a directory earlier in PATH takes precedence — which means a malicious or mistaken entry near the front can cause the WRONG program to run (a PATH hijack). Order is very relevant, EARLIER (not later) directories win, and duplicates are not auto-removed. PATH order is both a functional and a security consideration on Windows."
        },
        {
            "q": "What does `schtasks /query /fo LIST /v` do, and why is it a security step?",
            "code": "schtasks /query /fo LIST /v",
            "options": [
                "Lists all scheduled tasks with their triggers and run-as accounts — revealing legitimate jobs AND persistence",
                "Deletes all tasks",
                "Creates a task",
                "Only shows Microsoft tasks"
            ],
            "answer": 0,
            "why": "It enumerates every scheduled task verbosely; a task launching a program at logon/startup, especially as SYSTEM, is a classic persistence mechanism to audit.",
            "detail": "`schtasks /query /fo LIST /v` gives a detailed list of all scheduled tasks, their triggers, and the accounts they run under — essential because a task that runs a script at every logon or startup (particularly as SYSTEM) is a standard persistence and privilege technique that defenders hunt for. It does not delete or create tasks, and it shows all tasks, not just Microsoft's. Auditing scheduled tasks is routine threat hunting."
        },
        {
            "q": "Which registry keys are classic AUTOSTART locations to check?",
            "code": "reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "options": [
                "They store user passwords",
                "The 'Run' keys (HKLM and HKCU CurrentVersion\\Run) list programs launched automatically at logon",
                "They hold the routing table",
                "They contain DNS records"
            ],
            "answer": 1,
            "why": "The Run keys under HKLM and HKCU launch their listed programs at logon, so malware often adds itself there — a key persistence location.",
            "detail": "The CurrentVersion\\Run keys (machine-wide HKLM and per-user HKCU) enumerate programs that start automatically at logon, so enumerating them is standard for auditing a machine and hunting persistence, since malware commonly registers itself there. They do not store passwords, routing tables, or DNS records. Together with scheduled tasks, the Startup folder, and auto-start services, the Run keys form the persistence-enumeration checklist."
        },
        {
            "q": "Why can `setx PATH \"%PATH%;C:\\new\"` be dangerous?",
            "code": "setx PATH \"%PATH%;C:\\new\"",
            "options": [
                "It is always safe",
                "setx cannot modify PATH",
                "setx has a length limit and %PATH% may already be long, so it can TRUNCATE PATH and break the system",
                "It only adds, never removes"
            ],
            "answer": 2,
            "why": "A long existing PATH plus setx's length cap can truncate PATH, dropping essential directories and breaking commands.",
            "detail": "PATH is often already near or over setx's character limit, so `setx PATH \"%PATH%;...\"` can silently cut it off, removing directories the system needs and breaking many commands — with no easy undo. It is not always safe, setx CAN modify PATH (that is the risk), and truncation means it effectively DOES remove entries. Always back up the current PATH value before editing it, and prefer careful, verified edits over this pattern."
        },
        {
            "q": "Before editing a critical registry key, what is the prudent step?",
            "code": "reg export HKLM\\Software\\...\\Key backup.reg",
            "options": [
                "There is no need; edits are reversible",
                "Restart first",
                "Delete the key first",
                "Export the key to a .reg file as a backup, since registry edits have no easy undo"
            ],
            "answer": 3,
            "why": "reg export saves the key so you can restore it; a wrong registry change can break the system with limited undo.",
            "detail": "`reg export` writes the key to a .reg file you can re-import to restore it, which matters because a mistaken value or deletion in a critical key can prevent the system from working, with no recycle-bin-style undo. Registry edits are NOT freely reversible, restarting does not help after a bad change, and deleting the key first is the opposite of safe. Export-before-edit is the standard precaution for registry work, mirroring 'back up before you break it.'"
        }
    ]
}
