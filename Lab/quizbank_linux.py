# quizbank_linux.py - additional graded checks for the linux track.
# Merged onto each lesson's existing quiz by content.build_courses().
# Answer indices balanced across the file so the correct option isn't always first.
EXTRA_QUIZ = {
    "lx-1": [
        {
            "q": "What does `ls -ltr` show, and why is it useful?",
            "code": "ls -ltr",
            "options": [
                "Files sorted by time OLDEST first, so the newest are at the bottom near your prompt",
                "Files in reverse alphabetical order",
                "Only hidden files",
                "Files sorted by size"
            ],
            "answer": 0,
            "why": "-l long form, -t sorts by time, -r reverses it, so newest lands at the bottom of the output.",
            "detail": "-t sorts by modification time (newest first by default), and -r reverses that, putting the most recent files at the bottom where they are easy to see right above your prompt — ideal for spotting what just changed. It is not alphabetical (that is the default without -t), not hidden-only (-a does that), and not size (-S sorts by size). `ls -ltr` is one of the most-used 'what happened recently?' commands."
        },
        {
            "q": "What does `cd -` do?",
            "code": "cd -",
            "options": [
                "Goes up one level",
                "Returns to the PREVIOUS directory you were in (a toggle between two dirs)",
                "Goes to the root",
                "Goes to your home directory"
            ],
            "answer": 1,
            "why": "cd - jumps back to the last directory, letting you bounce between two locations quickly.",
            "detail": "`cd -` switches to the directory you were in before the last cd — a toggle useful when working across two locations. `cd ..` goes up one level, `cd /` goes to root, and `cd` alone (or `cd ~`) goes home. Confusing `cd -` (previous) with `cd ..` (parent) is common. The toggle behavior saves retyping long paths when you alternate between two working directories."
        },
        {
            "q": "Why is `rm -rf $DIR/` dangerous if $DIR is unset?",
            "code": "rm -rf $DIR/",
            "options": [
                "It is always safe",
                "rm refuses empty variables",
                "An unset $DIR expands to nothing, making it `rm -rf /` — deleting from the root",
                "It only deletes $DIR literally"
            ],
            "answer": 2,
            "why": "The shell expands an unset variable to empty, so the command becomes rm -rf / — a catastrophic delete.",
            "detail": "If $DIR is unset or empty, `$DIR/` becomes just `/`, so `rm -rf $DIR/` runs `rm -rf /`, recursively force-deleting the entire filesystem. rm does NOT refuse empty variables (the shell already expanded them away before rm sees them), it is not safe, and it does not delete '$DIR' literally (the shell substitutes first). This is why scripts quote and check variables before destructive commands, and why `set -u` (error on unset vars) is protective."
        },
        {
            "q": "What is the difference between an absolute and a relative path?",
            "code": "/home/you/file.txt   vs   file.txt",
            "options": [
                "They are the same",
                "Relative starts from root",
                "Absolute is shorter",
                "Absolute starts from / (root), unambiguous anywhere; relative is interpreted from the current directory"
            ],
            "answer": 3,
            "why": "An absolute path begins at the root / and is location-independent; a relative path is resolved from wherever you currently are.",
            "detail": "Absolute paths (starting with /) name a location unambiguously regardless of your current directory, so they are used in scripts for reliability; relative paths are resolved against the current directory (pwd), convenient interactively. They are not the same, relative does NOT start from root (that is absolute), and absolute is often longer, not shorter. Choosing absolute for scripts and relative for interactive use is a practical habit."
        },
        {
            "q": "What does `mkdir -p a/b/c` do that `mkdir a/b/c` does not?",
            "code": "mkdir -p a/b/c",
            "options": [
                "Creates intermediate parents (a and a/b) and does not error if they already exist",
                "Nothing different",
                "Makes the directories hidden",
                "Sets permissions to 777"
            ],
            "answer": 0,
            "why": "-p creates any missing parent directories and silently succeeds if the path already exists.",
            "detail": "Without -p, `mkdir a/b/c` fails if a or a/b do not already exist; with -p it creates the whole chain and does not complain if parts exist — making it safe and idempotent in scripts. It does not make directories hidden (a leading dot does) or set 777 permissions (that is chmod). The -p flag's dual role (create parents AND ignore-if-exists) is exactly why it is preferred in automation."
        },
        {
            "q": "What does `touch existing.txt` do to a file that already exists?",
            "code": "touch existing.txt",
            "options": [
                "Empties the file",
                "Updates its modification timestamp to now, without changing contents",
                "Deletes it",
                "Duplicates it"
            ],
            "answer": 1,
            "why": "touch updates an existing file's access/modification time (or creates it empty if absent), leaving contents intact.",
            "detail": "On an existing file, touch just bumps the timestamps to the current time — it does NOT alter or empty the contents. That is different from `> existing.txt`, which truncates the file to empty. touch does not delete or duplicate. Its two behaviors — create-if-absent and update-timestamp-if-present — make it useful both for making placeholder files and for triggering timestamp-based tools like make."
        }
    ],
    "lx-2": [
        {
            "q": "What is the difference between `cmd > f 2>&1` and `cmd 2>&1 > f`?",
            "code": "cmd > f 2>&1\ncmd 2>&1 > f",
            "options": [
                "They are identical",
                "The first is a syntax error",
                "The first sends both stdout and stderr to f; the second sends only stdout to f (stderr goes to the terminal)",
                "Both send everything to the terminal"
            ],
            "answer": 2,
            "why": "Redirections apply left to right: 2>&1 points stderr wherever stdout points AT THAT MOMENT, so order matters.",
            "detail": "In `> f 2>&1`, stdout is set to f first, then 2>&1 makes stderr follow to f — both land in f. In `2>&1 > f`, stderr is pointed at stdout's CURRENT target (the terminal) first, then stdout is moved to f — so stderr still goes to the terminal. They are not identical (that is the whole trap), neither is a syntax error, and the first does capture both. This order-dependence is one of the most misunderstood shell behaviors."
        },
        {
            "q": "Why must `sort` come before `uniq` in `sort file | uniq`?",
            "code": "sort file | uniq",
            "options": [
                "uniq requires sorted input to run at all",
                "sort removes duplicates so uniq is redundant",
                "Order does not matter",
                "uniq only collapses ADJACENT duplicate lines, so duplicates must be grouped by sorting first"
            ],
            "answer": 3,
            "why": "uniq compares only consecutive lines, so unsorted duplicates scattered through the file are not collapsed unless sorted first.",
            "detail": "uniq removes only adjacent repeated lines, so 'a b a' stays 'a b a' unless sorted to 'a a b' first. It does not strictly require sorted input to RUN (it just gives wrong results otherwise), sort alone with -u could dedupe but plain sort does not, and order absolutely matters. The `sort | uniq -c` idiom (sort to group, count with -c) is the canonical frequency-count pipeline built on this requirement."
        },
        {
            "q": "What does this pipeline output?",
            "code": "printf 'b\\na\\nb\\nc\\na\\n' | sort | uniq -c | sort -rn | head -1",
            "options": [
                "'2 a' or '2 b' — the most frequent line with its count (both a and b appear twice)",
                "The alphabetically first line",
                "The total line count",
                "All lines with counts"
            ],
            "answer": 0,
            "why": "sort groups, uniq -c counts, sort -rn orders by count descending, head -1 takes the top — the most frequent line.",
            "detail": "The pipeline counts occurrences (a:2, b:2, c:1), sorts by count descending, and takes the first — the most common line with its tally (a and b tie at 2). It is not the alphabetically first line, the total count, or all lines (head -1 limits to one). This sort|uniq -c|sort -rn|head pattern is the standard 'top talker' analysis used constantly on logs."
        },
        {
            "q": "What does `grep -v '^#' config` do?",
            "code": "grep -v '^#' config",
            "options": [
                "Prints only comment lines",
                "Prints lines that do NOT start with # — filtering out comment lines",
                "Deletes comments from the file",
                "Counts the comments"
            ],
            "answer": 1,
            "why": "-v inverts the match and ^# anchors to a line starting with #, so it shows all non-comment lines.",
            "detail": "^ anchors the pattern to the line start, so '^#' matches comment lines, and -v inverts to print everything else — a clean way to view a config without its comments. It does not print only comments (that would omit -v), does not modify the file (grep reads, it does not edit), and does not count (that is -c). The -v inversion flag is invaluable for filtering out noise you do not want."
        },
        {
            "q": "Why does `sort file > file` destroy the file's contents?",
            "code": "sort file > file",
            "options": [
                "sort is broken",
                "It works fine",
                "The shell truncates file to empty for the redirect BEFORE sort opens it to read",
                "sort deletes the file when done"
            ],
            "answer": 2,
            "why": "Output redirection opens (and truncates) the target before the command runs, so sort reads an already-emptied file.",
            "detail": "The shell sets up `> file` by opening it for writing — which truncates it to zero — before sort even starts reading, so sort sees an empty file and writes nothing. sort is not broken and it does not work fine (this is a real data-loss trap), nor does sort delete the file. The fixes are `sort file -o file` (sort's in-place option, which reads first) or a temp file. This redirect-truncates-first behavior burns people editing files in place."
        },
        {
            "q": "What is the practical difference between `grep pattern *.log` and `grep pattern file.log`?",
            "code": "grep pattern *.log",
            "options": [
                "grep expands the glob itself",
                "They search the same single file",
                "*.log is a grep regex",
                "The shell expands *.log to all matching files, so grep searches many files (and prefixes matches with filenames)"
            ],
            "answer": 3,
            "why": "The SHELL expands *.log into the list of matching filenames before grep runs, so grep receives multiple files and labels each match with its filename.",
            "detail": "Globs like *.log are expanded by the shell, not grep, so grep is handed every matching filename and, searching multiple files, prefixes each result with the filename. grep does not expand the glob (the shell already did), it is not one file, and *.log is a shell glob not a grep regex (grep uses . and * differently). Understanding that the shell expands globs before the command runs explains a great deal of command-line behavior."
        }
    ],
    "lx-3": [
        {
            "q": "In `-rwxr-xr--`, what can the GROUP do?",
            "code": "-rwxr-xr--",
            "options": [
                "Read and execute, but not write (the group triplet is r-x)",
                "Read, write, and execute",
                "Only read",
                "Nothing"
            ],
            "answer": 0,
            "why": "The three triplets are owner(rwx), group(r-x), other(r--); the middle r-x is read+execute, no write.",
            "detail": "After the leading file-type character, permissions come in three groups: owner rwx, group r-x, others r--. So the group has read and execute but not write. It is not full rwx (that is the owner), not read-only (that is others r--), and not nothing. Reading the ten-character permission string by splitting it into type + three triplets is a fundamental skill for auditing access."
        },
        {
            "q": "What does `chmod 600 ~/.ssh/id_ed25519` accomplish, and why does SSH require it?",
            "code": "chmod 600 ~/.ssh/id_ed25519",
            "options": [
                "Makes it world-readable",
                "Makes the key readable/writable only by the owner (rw-------); SSH refuses keys others can read",
                "Makes it executable",
                "Deletes the key"
            ],
            "answer": 1,
            "why": "600 is rw------- (owner-only); SSH rejects a private key with looser permissions as a security safeguard.",
            "detail": "600 grants read+write to the owner and nothing to group/others, so only you can read the private key — SSH enforces this and refuses a key that group or others can read (printing 'UNPROTECTED PRIVATE KEY FILE'). It does not make the key world-readable (that is the opposite and unsafe), executable, or delete it. The owner-only 600 mode is the standard for secrets like SSH keys precisely because of this check."
        },
        {
            "q": "What does the execute (x) bit mean on a DIRECTORY?",
            "code": "",
            "options": [
                "Permission to run the directory as a program",
                "Permission to list its contents",
                "Permission to ENTER the directory (cd into it) and access files by name",
                "Nothing; x is meaningless on directories"
            ],
            "answer": 2,
            "why": "On a directory, x means you may traverse into it and access files inside by name; r means you may list the names.",
            "detail": "For directories the bits are reinterpreted: r lets you LIST names, w lets you create/delete entries, and x lets you ENTER (cd) and access files by path. So a directory with r but not x shows names but denies access to the files. You cannot 'run' a directory, listing is the r bit (not x), and x is definitely meaningful. This read-versus-execute subtlety on directories confuses many and explains odd 'permission denied' situations."
        },
        {
            "q": "Why prefer `kill` (SIGTERM) over `kill -9` (SIGKILL) as a first step?",
            "code": "kill 1234   # vs  kill -9 1234",
            "options": [
                "SIGKILL is slower",
                "They are identical",
                "SIGTERM cannot be caught",
                "SIGTERM lets the process clean up (flush buffers, close files); SIGKILL gives it no chance and can corrupt data"
            ],
            "answer": 3,
            "why": "SIGTERM is a catchable request to shut down gracefully; SIGKILL is uncatchable and immediate, risking data loss.",
            "detail": "SIGTERM (the default kill signal) asks a process to terminate, letting it flush buffers, close files, and release locks first; SIGKILL (-9) is enforced by the kernel with no cleanup, which can corrupt data or leave stale locks. SIGKILL is not slower, they are not identical, and it is SIGKILL (not SIGTERM) that cannot be caught. Escalating from SIGTERM to SIGKILL only when necessary is the disciplined way to stop processes."
        },
        {
            "q": "What does `ps aux | grep firefox` do?",
            "code": "ps aux | grep firefox",
            "options": [
                "Lists all processes, then filters to lines mentioning firefox (finding its PID and details)",
                "Kills firefox",
                "Starts firefox",
                "Shows only firefox's memory"
            ],
            "answer": 0,
            "why": "ps aux lists every process; piping to grep firefox keeps only the matching lines, revealing the process and its PID.",
            "detail": "`ps aux` produces a full process listing (user, PID, CPU, memory, command), and grep filters it to lines containing 'firefox' — the standard way to find a specific process and its PID. It does not kill or start anything (that is kill/launching it), and it shows the full line, not just memory. This ps-pipe-grep pattern is how you locate a running program before inspecting or signaling it."
        },
        {
            "q": "What does making a file `chmod 777` actually risk?",
            "code": "chmod 777 script.sh",
            "options": [
                "It becomes read-only",
                "Anyone can read, write, AND execute it — a security hole if others can modify what runs",
                "Only you can access it",
                "It cannot be executed"
            ],
            "answer": 1,
            "why": "777 is rwxrwxrwx — full access for everyone, so any user can alter the file, which for a script means altering what it does.",
            "detail": "777 grants read/write/execute to owner, group, AND others, so any user (or compromised process) can modify a world-writable script and thereby control what it executes — a real vulnerability. It is the opposite of read-only, does not restrict to you, and remains executable. 777 is a lazy 'fix' for permission errors that opens a hole; the correct fix is usually adjusting ownership or using a narrower mode."
        }
    ],
    "lx-4": [
        {
            "q": "Why must there be NO spaces around the = in a bash assignment?",
            "code": "name=world   # vs  name = world",
            "options": [
                "Spaces are allowed and optional",
                "It makes name a number",
                "`name = world` is parsed as running the command `name` with arguments = and world",
                "Bash requires spaces"
            ],
            "answer": 2,
            "why": "Bash treats `name = world` as a command invocation (name) with two arguments, not an assignment.",
            "detail": "Assignment syntax is strict: `name=world` with no spaces. Adding spaces makes bash interpret `name` as a command and `=` and `world` as its arguments, usually giving 'command not found'. Spaces are not optional, it does not create a number, and bash does NOT require spaces (it forbids them here). This no-spaces rule is one of the first and most common bash gotchas."
        },
        {
            "q": "What is the difference between `\"$var\"` and `'$var'`?",
            "code": "echo \"$var\"\necho '$var'",
            "options": [
                "They are identical",
                "Single quotes expand, double are literal",
                "Both print the literal $var",
                "Double quotes expand $var to its value; single quotes are literal, printing $var unchanged"
            ],
            "answer": 3,
            "why": "Double quotes allow variable/command expansion; single quotes are fully literal, so $ has no special meaning inside them.",
            "detail": "Inside double quotes, $var is replaced by its value (while spaces are preserved as one word); inside single quotes everything is literal, so '$var' prints the four characters $var. They are not identical, and the roles are not reversed — double expands, single is literal. Choosing the right quote controls whether substitution happens, and quoting `\"$var\"` (double) is the standard way to safely use a variable that might contain spaces."
        },
        {
            "q": "What does this test check?",
            "code": "if [ -f \"$path\" ]; then echo yes; fi",
            "options": [
                "Whether $path exists and is a regular file",
                "Whether $path is empty",
                "Whether $path is a directory",
                "Whether $path is executable"
            ],
            "answer": 0,
            "why": "-f tests that the path exists and is a regular file (not a directory or special file).",
            "detail": "The `-f` file-test operator is true when the path exists and is a regular file. Emptiness of a string is `-z`, a directory is `-d`, and executable is `-x`. Note the mandatory spaces inside `[ ]` (it is really the `test` command) and the quoting of \"$path\" to handle spaces. Knowing the file-test operators (-f, -d, -e, -x, -r, -w) is essential for writing scripts that check before they act."
        },
        {
            "q": "Why does `set -euo pipefail` at the top of a script matter?",
            "code": "#!/bin/bash\nset -euo pipefail",
            "options": [
                "It makes the script run faster",
                "-e exits on any command failure, -u errors on unset variables, pipefail catches failures inside pipelines",
                "It enables color output",
                "It is just a comment"
            ],
            "answer": 1,
            "why": "These flags turn silent failures into immediate errors: stop on error, catch unset variables, and fail on any pipeline stage failure.",
            "detail": "By default bash ignores command failures and unset variables, so a failed `cd` can let later commands run in the wrong place. `-e` aborts on any error, `-u` treats unset variables as errors (catching typos), and `pipefail` makes a pipeline fail if any stage fails (not just the last). It does not affect speed, color, and is definitely not a comment. This safety header prevents a whole category of dangerous silent bugs and is recommended at the top of every serious script."
        },
        {
            "q": "What does this loop do?",
            "code": "for f in *.txt; do\n    mv \"$f\" \"${f%.txt}.bak\"\ndone",
            "options": [
                "Deletes all .txt files",
                "Concatenates them",
                "Renames every .txt file to .bak, using ${f%.txt} to strip the extension",
                "Prints their contents"
            ],
            "answer": 2,
            "why": "The glob loops over each .txt file, and ${f%.txt} removes the .txt suffix so mv renames it to .bak.",
            "detail": "The for loop iterates the .txt files; `${f%.txt}` is parameter expansion that strips the shortest matching .txt suffix, so mv renames each file to the same name with .bak. It does not delete, concatenate, or print. Quoting \"$f\" protects filenames with spaces. This combination — glob loop plus suffix-stripping parameter expansion — is a common batch-rename idiom worth recognizing."
        },
        {
            "q": "What is wrong with `if [ \"$a\"=\"$b\" ]`?",
            "code": "if [ \"$a\"=\"$b\" ]; then ...",
            "options": [
                "It correctly compares a and b",
                "It compares numbers",
                "It is a syntax error that stops the script",
                "Missing spaces around = makes it a single non-empty string test, which is always true"
            ],
            "answer": 3,
            "why": "Without spaces, `\"$a\"=\"$b\"` is one string argument to test, which is non-empty and therefore always true.",
            "detail": "test needs spaces around its operators: `[ \"$a\" = \"$b\" ]`. Written as `\"$a\"=\"$b\"` (no spaces), the whole thing is a single string like 'foo=bar', and `[ nonempty-string ]` is always true, so the condition never fails. It does not correctly compare (that is the bug), is for strings not numbers (numbers use -eq), and it does not error out — it silently misbehaves, which is worse. Spaces around `[`, `]`, and operators are mandatory in bash tests."
        }
    ],
    "lx-5": [
        {
            "q": "Why does `cut -f2` sometimes fail on space-separated data?",
            "code": "echo 'a   b   c' | cut -f2",
            "options": [
                "cut's default delimiter is TAB, so on space-separated text it cannot split fields; use awk instead",
                "cut always works on spaces",
                "cut needs -n for numbers",
                "cut only handles one field"
            ],
            "answer": 0,
            "why": "cut defaults to a TAB delimiter and cannot treat runs of spaces as one separator, so awk is better for whitespace fields.",
            "detail": "cut splits on a single TAB by default (change with -d), and it cannot collapse multiple spaces into one separator, so space-aligned columns break it. awk, by contrast, treats any run of whitespace as one field separator by default, making `awk '{print $2}'` the right tool for space-separated data. cut does not always work on spaces, -n is unrelated, and it can handle multiple fields (-f1,3). Knowing cut-for-tabs versus awk-for-whitespace prevents a lot of frustration."
        },
        {
            "q": "What does `awk '{sum += $1} END {print sum}'` compute?",
            "code": "awk '{sum += $1} END {print sum}' nums.txt",
            "options": [
                "The number of lines",
                "The total of the first column across all lines",
                "The first line only",
                "The maximum value"
            ],
            "answer": 1,
            "why": "It accumulates $1 (the first field) into sum on every line, then the END block prints the total after the last line.",
            "detail": "awk runs the main block per line (adding the first field to a running sum) and the special END block once after all input, printing the accumulated total. It is not a line count (that is `END {print NR}`), not the first line, and not the max (that needs a comparison). The pattern of a per-line accumulator plus an END summary is awk's signature strength — computing across columns in one tool, replacing several piped commands."
        },
        {
            "q": "What does `sed 's/foo/bar/g'` do that `sed 's/foo/bar/'` does not?",
            "code": "sed 's/foo/bar/g'",
            "options": [
                "g makes it global across files",
                "g is case-insensitive",
                "The g flag replaces ALL occurrences on each line, not just the first",
                "They are identical"
            ],
            "answer": 2,
            "why": "Without g, sed replaces only the first match per line; the g (global) flag replaces every match on the line.",
            "detail": "By default `s/foo/bar/` substitutes the first 'foo' on each line; adding `g` replaces all of them. g does not mean across files (sed already processes every line of its input), is not case-insensitivity (that is the I flag), and they are not identical. Forgetting g when you meant to replace every occurrence is a common sed mistake that silently leaves later matches unchanged."
        },
        {
            "q": "What is the danger of `sed -i 's/a/b/g' file` versus without -i?",
            "code": "sed -i 's/a/b/g' file",
            "options": [
                "-i makes it case-insensitive",
                "They do the same thing",
                "-i previews the change",
                "-i edits the file IN PLACE with no undo; without -i, sed writes to stdout leaving the file unchanged"
            ],
            "answer": 3,
            "why": "-i modifies the file directly and irreversibly; without it, sed only prints the result, leaving the original intact.",
            "detail": "Without -i, sed is safe — it streams the edited text to stdout and the file is untouched, so you can preview. With -i it overwrites the file in place with no backup (unless you use -i.bak), so a bad pattern destroys data irreversibly. -i is not case-insensitivity (that is I on the s command), the two are not the same, and -i does the opposite of previewing. The safe workflow is to run without -i first to verify, then add -i."
        },
        {
            "q": "What does `sort -t: -k3 -n /etc/passwd` do?",
            "code": "sort -t: -k3 -n /etc/passwd",
            "options": [
                "Sorts the colon-delimited file numerically by its third field (the UID)",
                "Sorts alphabetically by the whole line",
                "Reverses the file",
                "Removes duplicates"
            ],
            "answer": 0,
            "why": "-t: sets the delimiter to colon, -k3 sorts by the third field, -n sorts numerically — so it orders by UID.",
            "detail": "/etc/passwd is colon-delimited, so -t: sets that separator, -k3 keys on the third field (the numeric user ID), and -n ensures numeric (not lexical) ordering, so users sort by UID. It is not whole-line alphabetical (that is plain sort), not a reverse (-r), and not dedup (-u). Combining -t, -k, and -n to sort structured data by a specific numeric column is a everyday text-processing skill."
        },
        {
            "q": "What does `uniq -c` add to its output?",
            "code": "sort file | uniq -c",
            "options": [
                "Line numbers",
                "A count prefix showing how many times each unique (adjacent) line occurred",
                "Nothing; -c is invalid",
                "The character count of each line"
            ],
            "answer": 1,
            "why": "-c prefixes each output line with the number of consecutive occurrences it collapsed.",
            "detail": "uniq -c prepends the occurrence count to each unique line, which (after sorting to group duplicates) gives a frequency tally — the heart of the sort|uniq -c counting idiom. It is not line numbers (that is `nl` or grep -n), -c is valid, and it counts occurrences of the line, not characters within it (that is `wc -c`). The -c count flag turns uniq into a frequency counter, one of the most useful text-analysis tools."
        }
    ],
    "lx-6": [
        {
            "q": "What does `ssh-keygen -t ed25519` produce, and which file must stay secret?",
            "code": "ssh-keygen -t ed25519",
            "options": [
                "A single shared password",
                "Only a public key",
                "A key pair; the private key (id_ed25519) stays secret, the public key (.pub) is shared",
                "An encrypted disk"
            ],
            "answer": 2,
            "why": "It generates a private/public key pair; the private key must never leave the machine, the public key is safe to distribute.",
            "detail": "ssh-keygen creates two files: the private key (kept secret, mode 600) and the matching .pub public key (safe to install on servers). The security rests on never sharing the private key. It is not a shared password, not public-only (both are made), and not disk encryption. This asymmetric pair is what enables passwordless, secure SSH login: the server holds your public key and challenges you to prove you hold the private one."
        },
        {
            "q": "What does `ss -tulpn` show?",
            "code": "ss -tulpn",
            "options": [
                "All files on disk",
                "The routing table",
                "DNS records",
                "Listening TCP/UDP sockets with numeric ports and the owning process"
            ],
            "answer": 3,
            "why": "-t TCP, -u UDP, -l listening, -p process, -n numeric — so it lists what services are listening and which programs own them.",
            "detail": "ss (the modern netstat replacement) with -tulpn shows listening TCP and UDP sockets, numeric ports (fast, no name lookups), and the owning process — answering 'what is listening on this box and what program is it?', a first-move on any machine. It does not list disk files, the routing table (that is `ip route`), or DNS records. Enumerating listening services is core to both administration and security assessment."
        },
        {
            "q": "Why might SSH refuse to use your private key?",
            "code": "",
            "options": [
                "Its permissions are too open (must be 600); SSH rejects a key others can read",
                "The key is too long",
                "SSH always needs a password too",
                "The public key is missing"
            ],
            "answer": 0,
            "why": "SSH enforces strict private-key permissions (owner-only, 600) and refuses a key that group/others can read.",
            "detail": "A private key with permissions looser than owner-only is a security risk, so SSH refuses it, printing 'UNPROTECTED PRIVATE KEY FILE' — fix with `chmod 600`. It is not about key length, SSH does not always need a password (key auth replaces it), and the public key's absence on the client is not the issue (the private key is what you present). This permission check is a deliberate safeguard, not a bug."
        },
        {
            "q": "What does `apt update` do, and why run it before `apt install`?",
            "code": "sudo apt update\nsudo apt install nmap",
            "options": [
                "Upgrades all installed software",
                "Refreshes the local package index so install finds current versions and available packages",
                "Installs updates automatically",
                "Deletes old packages"
            ],
            "answer": 1,
            "why": "apt update refreshes the list of available packages; without it, install may use a stale index and miss or mis-version packages.",
            "detail": "`apt update` downloads the latest package lists from the repositories so apt knows what versions exist; running it before install ensures you get current packages and avoids 'package not found' from a stale index. It does NOT upgrade installed software (that is `apt upgrade`), does not auto-install updates, and does not remove packages. The update-then-install habit is standard on Debian/Ubuntu systems."
        },
        {
            "q": "A 'REMOTE HOST IDENTIFICATION HAS CHANGED' warning on SSH means what?",
            "code": "",
            "options": [
                "Your password expired",
                "The network is slow",
                "The server's host key differs from the stored one — possibly a rebuilt server OR a man-in-the-middle attack",
                "SSH needs an update"
            ],
            "answer": 2,
            "why": "The stored host key no longer matches, which is a genuine security alert — verify before trusting the new key.",
            "detail": "SSH remembers each server's host key in known_hosts; a mismatch means either the server was legitimately rebuilt/reinstalled or someone is intercepting your connection (man-in-the-middle). It is a real security event to investigate out-of-band, not a password, network-speed, or update issue. Blindly deleting the old key to silence the warning defeats the protection — you should confirm the change is legitimate first."
        },
        {
            "q": "What does `curl -I https://example.com` return?",
            "code": "curl -I https://example.com",
            "options": [
                "The full page body",
                "Nothing",
                "The server's IP only",
                "Only the HTTP response headers (status, content-type, etc.), not the body"
            ],
            "answer": 3,
            "why": "-I (capital i) issues a HEAD request, fetching just the response headers without the body.",
            "detail": "`curl -I` sends a HEAD request so the server returns only headers — status code, content-type, content-length, server — useful for checking a URL's status or type without downloading the content. It is not the full body (that is curl without -I), not nothing, and not just the IP (that is DNS resolution). curl for command-line HTTP, and -I for headers-only, are staples of web debugging and reconnaissance."
        }
    ]
}
