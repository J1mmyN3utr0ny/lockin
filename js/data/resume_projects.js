// resume_projects.js — the Portfolio ladder: resume-worthy projects Itamar builds FROM SCRATCH.
//
// Design intent (this is the whole point of the feature):
//  - His documented weakness is starting code from a blank file — past projects were AI-guided.
//    Every project here is built the effective way: retrieval FIRST (answer design questions),
//    hints escalate nudge -> specific -> OUTLINE (never a full solution), then a build-from-scratch
//    rebuild proves he owns it.
//  - Each project is pitched at his real level (he already writes sockets + struct framing + scapy)
//    and maps to GAMA-relevant skill tracks, so finishing them moves both learning AND the résumé.
//  - Each carries a starter résumé bullet + a tech stack; the Résumé view turns shipped projects
//    into a copy-paste CV "Projects" section.

// WHY real, used tools beat toy exercises — surfaced at the top of the Portfolio so the point
// isn't lost: these aren't assignments invented for practice, they're small versions of software
// that professionals run every day. That's what makes them count twice — as deep learning AND as
// real experience an interviewer can poke at.
export const whyProjects = {
  title: "Why these, and not just 'more exercises'",
  blurb: "Every project on this ladder is a real, useful tool — not a textbook problem. That distinction is the entire point.",
  points: [
    { icon: "🛠️", name: "Real tools, not toy problems", text: "A FizzBuzz teaches syntax. A port scanner teaches syntax AND concurrency AND networking AND how actual recon tools work — because it basically IS one, just smaller. Depth of learning tracks the realism of what you build." },
    { icon: "🎤", name: "Something to actually talk about", text: "'I did some Python exercises' ends a conversation. 'I wrote a packet sniffer that parses raw Ethernet/IP/TCP headers' starts one — and you can back it up, because you built it and can explain any line." },
    { icon: "🧩", name: "They compose", text: "The scanner finds hosts, the sniffer reads their traffic, the FIM watches their files, the vault protects secrets on them. Individually they're each a résumé line; together they read as one coherent skill set — offense, defense, and the low-level plumbing under both." },
    { icon: "🚪", name: "A tool is a door into a conversation", text: "When an interviewer or GAMA officer sees a real artifact, the next question is always 'walk me through it' — the best possible position to be in, because you're explaining your own work, not reciting theory." }
  ]
};

// The learning method the whole Portfolio enforces — surfaced so he internalises HOW to learn.
export const principles = {
  title: "How to build so it actually sticks",
  blurb: "Four rules turn 'I watched it get built' into 'I can build it.' The projects below are structured to force all four.",
  rules: [
    { icon: "🧠", name: "Retrieval first", text: "Answer each stage's design questions from memory BEFORE peeking at a hint. The struggle is the learning — a hint you reach for too early erases it." },
    { icon: "📄", name: "Blank file, no AI", text: "Type the first version yourself from an empty file. Docs are allowed; AI writing your logic is not. This is the exact muscle you're here to build." },
    { icon: "🗣️", name: "Explain it back", text: "After each project, explain the core out loud in your own words. If you can't teach it, you don't own it yet." },
    { icon: "🚀", name: "Ship it", text: "A project on your disk isn't a résumé line. Git repo + README + a demo = an artifact someone can see. Every project ends shipped." }
  ]
};

// How to write a bullet that lands — surfaced in the Résumé view.
export const resumeTips = {
  title: "Anatomy of a résumé bullet",
  formula: "Action verb → what you built → the tech → the hard part / result",
  examples: [
    { bad: "Made a port scanner in Python.", good: "Built a multithreaded TCP port scanner (Python, sockets, threading) that sweeps 65k ports in seconds with service-banner detection." },
    { bad: "Did a project with encryption.", good: "Designed a local password vault deriving an AES key from a master password (PBKDF2 + salt) so nothing is ever stored in plaintext." }
  ],
  verbs: ["Built", "Designed", "Implemented", "Engineered", "Wrote", "Reverse-engineered", "Automated", "Optimized"],
  note: "Write it yourself — the generation effect means a bullet you phrase is one you can defend in an interview. The starters below are scaffolding to rewrite, not to copy."
};

// tiers, in order
export const tiers = [
  { id: "t1", name: "Foundations", sub: "Build fluency from a blank file" },
  { id: "t2", name: "Security & systems", sub: "Tools a blue team would actually run" },
  { id: "t3", name: "Depth & polish", sub: "Show you understand what's under the framework" },
  { id: "t4", name: "Capstone — after the PET exam (Sep 5 →)", sub: "Everything you've built, integrated into one flagship tool" }
];

export const projects = [
  // ---------------- TIER 1 ----------------
  {
    id: "scanner", tier: "t1", name: "Threaded Port Scanner", icon: "🛰️",
    tagline: "Find open TCP ports on a host, fast — with threads and banner grabbing.",
    stack: ["Python", "sockets", "threading", "argparse"],
    skills: ["python", "cyber_high"],
    why: "The canonical first offensive-security tool. It proves you can turn one protocol fact — a port is a door that's open or shut — into a working recon utility, and that you understand concurrency.",
    realUse: "This is step one of every real penetration test and every CTF: before you attack anything, you find out what's actually running. Nmap — the industry-standard scanner every pentester has installed — does exactly this, just with far more polish. Use it on your own LAN or a VM to see what your own machines expose.",
    resumeBullet: "Built a multithreaded TCP port scanner in Python (sockets + threading) that sweeps a host's port range in seconds, with service/banner detection and a clean argparse CLI.",
    stages: [
      { name: "1 · Single-port check",
        goal: "Given host + port, report open or closed. Nail the connect lifecycle before anything else.",
        dq: ["Which socket call tells you a port is open — and how do you know it succeeded?",
             "Why do you MUST set a timeout, and what happens to a scan without one?",
             "What exception is raised on a refused/filtered port, and how will you catch it?"],
        hints: ["You need connect() (not bind/listen — you're the client here). Success = no exception.",
                "socket.settimeout(seconds) before connect_ex, or wrap connect() in try/except.",
                "OUTLINE: s=socket(AF_INET,SOCK_STREAM); s.settimeout(0.5); rc=s.connect_ex((host,port)); open = (rc==0); s.close()."] },
      { name: "2 · Scan a range",
        goal: "Loop a range of ports, collect the open ones into a result you can print.",
        dq: ["A sequential loop over 65,535 ports is painfully slow — WHY, specifically (what dominates the time)?",
             "What data structure holds your open ports, and in what order do you want them?",
             "How do you let the user pass a range like 1-1024 vs a single port?"],
        hints: ["Each closed/filtered port blocks for the full timeout — the wait dominates, not the CPU.",
                "Collect into a list; sort at the end so output is deterministic.",
                "OUTLINE: open=[]; for p in range(lo,hi+1): if check(host,p): open.append(p). Parse 'lo-hi' by splitting on '-'."] },
      { name: "3 · Go concurrent",
        goal: "Scan ports in parallel so the whole sweep is fast.",
        dq: ["Thread-per-port vs a fixed thread pool — what breaks if you spawn 65,535 threads?",
             "Two threads append to your results list at once — what can go wrong, and how do you make it safe?",
             "How will you know when ALL workers are finished?"],
        hints: ["A pool bounds concurrency; 65k raw threads exhausts memory/OS handles.",
                "concurrent.futures.ThreadPoolExecutor is the clean tool; or a queue of ports + N worker threads.",
                "OUTLINE: with ThreadPoolExecutor(max_workers=200) as ex: results=ex.map(lambda p: (p,check(host,p)), ports). Collect where the flag is True."] },
      { name: "4 · Banner grab + CLI",
        goal: "For open ports, read the service banner; wrap it all in a real command-line tool.",
        dq: ["Some services send a greeting the instant you connect — how do you read it without hanging on ones that don't?",
             "Which flags does a good scanner expose (host, ports, threads, timeout)?",
             "What should `-h` / `--help` show a first-time user?"],
        hints: ["After connect, try a short recv() with a timeout; empty/timeout just means 'no banner'.",
                "argparse: positional host, --ports, --threads, --timeout with sensible defaults.",
                "OUTLINE: banner = try recv(1024).decode(errors='ignore').strip() except: ''. Build argparse, map args to your scan()."] }
    ],
    ship: [
      "Put it under Git — one repo, first commit is the working scanner.",
      "README: what it does, one usage example, and a line on why timeouts/threads matter.",
      "Handle Ctrl-C so a long scan stops cleanly instead of dumping a traceback.",
      "Add a screenshot or copy-pasted sample run to the README.",
      "One stretch shipped (see below)."
    ],
    proveIt: "Delete the file. From a blank editor, rebuild the scan-a-range core (single-port check + loop) in under 20 minutes with no reference. That's the retrieval rep that makes it yours.",
    stretch: "Add a top-1000 common-ports mode, JSON output, or an asyncio version — then compare its speed to the threaded one and note the difference in the README."
  },
  {
    id: "sniffer", tier: "t1", name: "Packet Sniffer & Header Parser", icon: "📡",
    tagline: "Capture live traffic and decode Ethernet/IP/TCP headers byte by byte.",
    stack: ["Python", "raw sockets", "struct", "networking"],
    skills: ["cyber_low", "cyber_high", "python"],
    why: "You already FIRED packets with scapy — this goes the other way and DECODES them from raw bytes. Hand-parsing headers is exactly the low-level networking muscle GAMA's research track rewards.",
    realUse: "This is a miniature Wireshark — the tool every network defender, incident responder, and CTF player has open constantly to see what's actually crossing a wire. Run it while you browse the web or SSH somewhere and you'll watch the TCP handshake happen in real time, not just read about it.",
    resumeBullet: "Wrote a packet sniffer that captures live traffic and parses Ethernet / IP / TCP headers straight from raw bytes (struct), printing a Wireshark-style summary line per packet.",
    stages: [
      { name: "1 · Capture raw frames",
        goal: "Open a raw socket and pull whole frames off the wire.",
        dq: ["Why does a raw/promiscuous socket need admin/root — what is it bypassing?",
             "On your OS, which socket family/type gives you link-layer vs IP-layer bytes?",
             "What's the max size you should recv() to get a full frame?"],
        hints: ["Raw capture reads below the normal stack, so the OS gates it behind privileges.",
                "Linux: socket(AF_PACKET, SOCK_RAW, ntohs(3)). Windows differs — document what you used.",
                "OUTLINE: s=socket(AF_PACKET,SOCK_RAW,ntohs(0x0003)); while True: raw,_=s.recvfrom(65535); parse(raw)."] },
      { name: "2 · Parse the Ethernet header",
        goal: "Pull dest MAC, src MAC, and ethertype out of the first 14 bytes.",
        dq: ["How many bytes is an Ethernet header, and how is it laid out?",
             "Which struct format string unpacks 6+6+2 bytes, and what does '!' mean?",
             "How do you turn 6 raw bytes into aa:bb:cc:dd:ee:ff?"],
        hints: ["14 bytes: 6 dest + 6 src + 2 ethertype.",
                "struct.unpack('!6s6sH', raw[:14]); '!' = network (big-endian) byte order.",
                "OUTLINE: dst,src,proto = unpack('!6s6sH', raw[:14]); mac = ':'.join(f'{b:02x}' for b in dst)."] },
      { name: "3 · Parse the IP header",
        goal: "Decode version, IHL, protocol, and source/dest IPs from the IP header.",
        dq: ["The first byte packs TWO fields — which, and how do you split them with bit ops?",
             "IHL is in 32-bit WORDS, not bytes — how do you get the real header length?",
             "Which byte tells you the payload is TCP (6) vs UDP (17)?"],
        hints: ["High nibble = version, low nibble = IHL. Use >>4 and &0x0F.",
                "header_bytes = ihl * 4. socket.inet_ntoa turns 4 bytes into an IP string.",
                "OUTLINE: b0=raw[14]; ver=b0>>4; ihl=(b0&0xF)*4; proto=raw[14+9]; src=inet_ntoa(raw[14+12:14+16])."] },
      { name: "4 · Parse TCP/UDP + summarise",
        goal: "Pull ports (and TCP flags), then print one clean summary line per packet.",
        dq: ["Where do the source/dest ports sit in the TCP header, and how big is each?",
             "The TCP flags live in specific bits — how do you test if SYN or ACK is set?",
             "What does a genuinely useful one-line summary contain?"],
        hints: ["First 4 bytes of the TCP header = src port (2) + dst port (2), big-endian H each.",
                "Flags are a byte you mask: SYN=0x02, ACK=0x10 — bitwise-AND to test.",
                "OUTLINE: sport,dport = unpack('!HH', tcp[:4]); line = f'{src}:{sport} -> {dst}:{dport} {proto_name} {flags}'."] }
    ],
    ship: [
      "Git repo with a README that explains each header field you parse (this doubles as your study notes).",
      "Document the admin/root requirement and how to run it on your OS.",
      "Add a protocol filter (e.g. only show TCP) via a flag.",
      "Include a screenshot of real captured output."
    ],
    proveIt: "On paper, parse a real IPv4 header out of a hex dump — every field, including splitting version/IHL from the first byte — with no notes.",
    stretch: "Detect a port scan hitting your own machine (many SYNs to different ports from one source) — which ties this directly back to the scanner project."
  },
  // ---------------- TIER 2 ----------------
  {
    id: "vault", tier: "t2", name: "Encrypted Password Vault", icon: "🔐",
    tagline: "A local vault that derives a key from a master password and encrypts every entry.",
    stack: ["Python", "cryptography (AES)", "PBKDF2", "hashlib", "CLI/Tk"],
    skills: ["python", "cyber_low"],
    why: "Applied crypto is catnip on a cyber résumé — and it forces the hashing-vs-encryption distinction you also need for the CS project's auth milestone. Small code, serious signal.",
    realUse: "This is the same design 1Password, Bitwarden and every real password manager use under the hood — a master password, key derivation, and encrypted-at-rest storage. You can genuinely use your own build day to day for your throwaway/practice accounts once it works, and point to it as 'I understand what my password manager is actually doing.'",
    resumeBullet: "Built a local password vault that derives an AES key from a master password (PBKDF2 + per-vault salt) and encrypts all entries — nothing is ever written in plaintext.",
    stages: [
      { name: "1 · Master password → key",
        goal: "Turn a human master password into a strong encryption key.",
        dq: ["Why can't you use the master password directly as an AES key?",
             "What does a Key Derivation Function (PBKDF2) add that a plain hash doesn't?",
             "What do you store to re-derive the key next time, and what do you NEVER store?"],
        hints: ["A password isn't uniformly random or the right length — derive a key from it.",
                "PBKDF2 adds a salt + many iterations, making brute force expensive.",
                "OUTLINE: store the salt (not secret) + iteration count; key = PBKDF2(master, salt, iters). Never store the master or the key."] },
      { name: "2 · Encrypt / decrypt a blob",
        goal: "Round-trip a string through encryption and back with your derived key.",
        dq: ["What library gives you authenticated encryption without you inventing crypto?",
             "Why is 'authenticated' (detects tampering) better than raw AES here?",
             "What happens on decrypt if the master password was wrong?"],
        hints: ["cryptography's Fernet (or AESGCM) — do NOT roll your own cipher.",
                "Authenticated modes fail loudly if the ciphertext or key is wrong — that's your login check.",
                "OUTLINE: f=Fernet(base64_key); token=f.encrypt(plaintext.encode()); f.decrypt(token) raises on a bad key."] },
      { name: "3 · The vault store (CRUD)",
        goal: "Add / get / list entries, persisted as an encrypted file.",
        dq: ["Do you encrypt each entry separately, or the whole store as one blob — trade-offs?",
             "What's the shape of an entry (site, username, password, notes)?",
             "How do you avoid ever writing a decrypted vault to disk?"],
        hints: ["Simplest safe design: keep the whole dict in memory, encrypt the JSON on save.",
                "entry = {site, user, secret}; the vault is {site: entry}.",
                "OUTLINE: load = decrypt(file)->json.loads; save = json.dumps->encrypt->write bytes. Decrypted form lives only in RAM."] },
      { name: "4 · Interface + hygiene",
        goal: "A CLI (or small Tk GUI) to use it, that locks and clears secrets.",
        dq: ["Which commands does a usable vault need (init, add, get, list, lock)?",
             "Why copy a password to the clipboard instead of printing it — and what's the risk left?",
             "How do you re-prompt for the master password rather than keeping it around?"],
        hints: ["argparse subcommands, or a Tk window with a master-password gate.",
                "Clipboard avoids shoulder-surfing the terminal; clear it after a few seconds.",
                "OUTLINE: getpass() for the master (no echo); on 'get', copy secret to clipboard, schedule a clear."] }
    ],
    ship: [
      "Git repo. Add the vault file + salt to .gitignore so you NEVER commit secrets (this is the Git-hygiene lesson).",
      "README with an honest 'learning project, not a production password manager' security note.",
      "A quick demo: init a vault, add an entry, retrieve it (screenshot or asciinema).",
      "Wrong-master-password path fails gracefully, not with a raw stack trace."
    ],
    proveIt: "With no notes, explain why you store the salt but not the master password, and exactly what raising the PBKDF2 iteration count defends against.",
    stretch: "Add a password generator with an entropy estimate, or a strength meter that scores entries already in the vault."
  },
  {
    id: "fim", tier: "t2", name: "File Integrity Monitor", icon: "🛡️",
    tagline: "Hash a directory into a baseline, then alert on anything that changes.",
    stack: ["Python", "hashlib", "os / pathlib", "json"],
    skills: ["python", "linux", "cyber_high"],
    why: "A real blue-team tool — a mini Tripwire. Tiny amount of code, but it says 'I think like a defender': baseline, detect drift, report. Reads great on a résumé aimed at a SOC or GAMA.",
    realUse: "This is literally what enterprise security teams run on critical servers — Tripwire and OSSEC do this exact baseline-and-diff for a living, and it's how tampering with system files gets caught. Point it at a folder you actually care about (your CS project's source, say) and it'll genuinely tell you if something changed when you weren't looking.",
    resumeBullet: "Created a file-integrity monitor that fingerprints a directory tree with SHA-256, snapshots a baseline, and reports created / modified / deleted files on each scan.",
    stages: [
      { name: "1 · Hash one file",
        goal: "Produce a stable SHA-256 for a single file.",
        dq: ["Why read the file in chunks instead of one .read() into memory?",
             "Which hashlib call gives you a hex string you can store in JSON?",
             "Would two identical files ever get different hashes — why not?"],
        hints: ["A 4GB file shouldn't need 4GB of RAM — stream it in fixed-size chunks.",
                "hashlib.sha256(); .update(chunk) in a loop; .hexdigest() at the end.",
                "OUTLINE: h=sha256(); with open(p,'rb') as f: while chunk:=f.read(65536): h.update(chunk); return h.hexdigest()."] },
      { name: "2 · Walk the tree",
        goal: "Produce {relative_path: hash} for every file under a root.",
        dq: ["Which stdlib tool walks a directory recursively?",
             "Should you store absolute or relative paths in the baseline — why?",
             "How do you skip files you can't read without crashing the whole scan?"],
        hints: ["os.walk or pathlib.Path.rglob('*') both work.",
                "Relative paths make the baseline portable and comparable across runs.",
                "OUTLINE: for path in root.rglob('*'): if path.is_file(): try: baseline[str(path.relative_to(root))]=hash(path) except PermissionError: log."] },
      { name: "3 · Baseline vs new scan (the diff)",
        goal: "Compare a fresh scan to the saved baseline and classify changes.",
        dq: ["From two dicts of {path:hash}, how do you find ADDED, REMOVED, and CHANGED files with set logic?",
             "What exactly signals a 'changed' file vs a merely 'present' one?",
             "How do you persist and reload the baseline between runs?"],
        hints: ["Set difference on the keys gives added/removed; compare values on the shared keys for changed.",
                "changed = keys in both where old_hash != new_hash.",
                "OUTLINE: added=new.keys()-old.keys(); removed=old.keys()-new.keys(); changed={k for k in old&new if old[k]!=new[k]}."] },
      { name: "4 · Report / watch loop",
        goal: "A readable report, and an option to re-scan on a schedule.",
        dq: ["What makes a report actionable rather than just a wall of paths?",
             "Continuous watching: a simple sleep-loop vs a real filesystem-watch library — trade-offs?",
             "How do you avoid re-alerting on a change you already acknowledged?"],
        hints: ["Group by category (Added / Modified / Deleted) with counts; colour helps.",
                "A time.sleep loop is fine to start; watchdog gives instant events later.",
                "OUTLINE: print sections per category; on a --update flag, rewrite the baseline to accept current state."] }
    ],
    ship: [
      "Git repo + README with an example run showing a detected change.",
      "Handle large files (chunked hashing) and permission errors without dying.",
      "Ship a sample baseline.json and a screenshot of a diff.",
      "Make the watched directory + interval configurable via flags."
    ],
    proveIt: "Rebuild the baseline-diff logic (the three set operations) from scratch on a blank file, and explain aloud why you hash in chunks.",
    stretch: "Add real-time watching with the watchdog library, or a desktop/email notification when a monitored file changes."
  },
  // ---------------- TIER 3 ----------------
  {
    id: "httpd", tier: "t3", name: "HTTP Server From Scratch", icon: "🌐",
    tagline: "Parse HTTP/1.1 off a raw socket — no Flask, no framework.",
    stack: ["Python", "sockets", "threading", "HTTP/1.1"],
    skills: ["python", "cyber_high"],
    why: "Everyone lists Flask; almost nobody can write the server underneath it. Parsing HTTP straight off a socket proves you understand the web itself — a standout line that invites the best interview questions.",
    realUse: "Every website you've ever loaded was served by something doing exactly this parsing, just heavily optimized — Flask, nginx, Apache are all bigger versions of the same request-line/header/body loop. Serve your own portfolio page or the CS project's static assets with it and you have a server you built, running something real, not a demo that does nothing.",
    resumeBullet: "Implemented an HTTP/1.1 server from scratch on raw TCP sockets — request-line/header parsing, routing, static-file serving and correct status codes — with no web framework.",
    stages: [
      { name: "1 · Accept + read the raw request",
        goal: "Get the exact bytes a browser sends when it requests a page.",
        dq: ["What's the socket server sequence (you know it from the CS project) to accept a connection?",
             "How do you know you've read the whole request head — what marks its end?",
             "Print the raw bytes: what are the very first line and the line endings?"],
        hints: ["socket -> bind -> listen -> accept, then recv on the accepted connection.",
                "The header block ends at a blank line: the sequence CRLF CRLF (\\r\\n\\r\\n).",
                "OUTLINE: read until b'\\r\\n\\r\\n' is in the buffer; that buffer is the request head."] },
      { name: "2 · Parse request line + headers",
        goal: "Turn the raw head into method, path, version, and a headers dict.",
        dq: ["The first line has three parts — what are they and what separates them?",
             "Each header line is 'Name: value' — how do you split safely if the value contains a colon?",
             "Which header must you read to handle a POST body correctly?"],
        hints: ["Request line: METHOD SP PATH SP VERSION (e.g. GET /index.html HTTP/1.1).",
                "Split each header line on the FIRST ': ' only (split(':', 1)).",
                "OUTLINE: lines=head.split('\\r\\n'); method,path,ver=lines[0].split(); headers={k:v for k,v in (l.split(': ',1) for l in lines[1:] if l)}."] },
      { name: "3 · Build a valid response",
        goal: "Send back a well-formed HTTP response the browser accepts.",
        dq: ["What are the mandatory parts of a response, in order?",
             "Which headers does a browser really want (Content-Type, Content-Length)?",
             "What's the exact byte between the headers and the body?"],
        hints: ["Status line, then headers, then a blank line, then the body.",
                "Content-Length must equal the body's byte length or the browser hangs/truncates.",
                "OUTLINE: resp = f'HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\nContent-Length: {len(body)}\\r\\n\\r\\n'.encode()+body."] },
      { name: "4 · Routing, static files, concurrency",
        goal: "Serve real files with correct types + 404s, and handle clients concurrently.",
        dq: ["How do you map a URL path to a file safely (and stop ../ escaping your folder)?",
             "How do you pick the Content-Type for .html vs .png vs .css?",
             "One client at a time blocks everyone — how do you serve several at once?"],
        hints: ["Resolve the path and confirm it stays inside your web root before opening it.",
                "mimetypes.guess_type(path) gives you the Content-Type; fall back to octet-stream.",
                "OUTLINE: a thread per accepted connection (or a pool); on a missing/invalid path return a 404 response."] }
    ],
    ship: [
      "Git repo + a README with a short 'what I learned about HTTP' section.",
      "Test it with BOTH a browser and curl -v; note the difference in the README.",
      "A malformed request returns a 400, it does not crash the server.",
      "Screenshot the server serving a real page you wrote."
    ],
    proveIt: "On paper, write a minimal valid HTTP response for a 200 AND a 404 — every line, including the blank line — from memory.",
    stretch: "Add a tiny routing-decorator API (@route('/path')), gzip responses, or serve your own portfolio page from it and link that in the README."
  },
  {
    id: "reveng", tier: "t3", name: "CrackMe Reverse-Engineering Write-Up", icon: "🧩",
    tagline: "Recover a C program's logic from its disassembly — and document the hunt.",
    stack: ["C", "gcc", "gdb / objdump", "x86 assembly"],
    skills: ["c", "asm", "cyber_low"],
    why: "This turns the C + ASM tracks into an artifact a recruiter or GAMA officer can actually read. A clear reverse-engineering write-up shows you can reason about a binary — the exact mindset the low-level research track selects for.",
    realUse: "This is a scaled-down version of what malware analysts and vulnerability researchers do all day: given only a compiled binary, figure out what it does and where the interesting logic hides. It's also exactly the skill behind crackmes.one and reverse-engineering CTF categories — solve one of those next and you're doing the real thing, not a simulation of it.",
    stages: [
      { name: "1 · Write & compile a target",
        goal: "A tiny C 'password check' you compile with gcc — your own crackme.",
        dq: ["What's the smallest program that has a 'right answer' to hide (a password compare)?",
             "What does gcc actually DO — the compile -> assemble -> link pipeline?",
             "How do optimisation flags (-O0 vs -O2) change how readable the output is?"],
        hints: ["A main() that reads input and compares it to a secret with strcmp is plenty.",
                "gcc runs preprocess -> compile to ASM -> assemble to object -> link to executable.",
                "OUTLINE: write check.c; gcc -O0 -g check.c -o check; keeping -O0 -g makes the disassembly follow the source."] },
      { name: "2 · Read the disassembly",
        goal: "Look at the compiled ASM and map instructions back to your C.",
        dq: ["Which tool dumps a binary's assembly (or which site shows C->ASM live)?",
             "Where in the ASM is your string compare, and which instruction does the actual test?",
             "How does a cmp followed by je/jne implement your C `if`?"],
        hints: ["objdump -d ./check, or paste the C into godbolt.org to see them side by side.",
                "Look for the call to strcmp and the cmp/test right after it.",
                "OUTLINE: cmp sets flags; je jumps when equal, jne when not — that pair IS your if/else branch."] },
      { name: "3 · Step through in gdb",
        goal: "Run it under a debugger and watch registers/memory at the decision point.",
        dq: ["How do you set a breakpoint at the compare and stop there?",
             "Which registers/memory hold the two strings being compared?",
             "How do you read the value the program expects at runtime?"],
        hints: ["gdb ./check; break main (or break at the strcmp); run; then step/next.",
                "info registers, and x/s <addr> to examine the string at an address.",
                "OUTLINE: break the compare; inspect the pointers' target strings; you can literally read the expected password."] },
      { name: "4 · Recover it 'blind' + write it up",
        goal: "Find the check WITHOUT looking at your source, then document the whole process.",
        dq: ["Pretend you never saw check.c — can you find the password from the binary alone?",
             "What's the story a good write-up tells: what you saw -> what it meant -> how you confirmed it?",
             "Which annotated snippets make the write-up convincing?"],
        hints: ["Combine static (objdump) + dynamic (gdb) evidence to pin the answer.",
                "Structure: goal, tools, disassembly with your annotations, the gdb moment it clicked, conclusion.",
                "OUTLINE: a Markdown write-up with the ASM snippet, your notes on each instruction, and a screenshot of the winning gdb run."] }
    ],
    ship: [
      "Git repo whose star file is WRITEUP.md — the write-up IS the deliverable.",
      "Commit the C sources + exact build commands so anyone can reproduce it.",
      "Annotate the key disassembly inline (comment what each instruction does).",
      "Add a screenshot of the gdb session where you recover the secret."
    ],
    proveIt: "From memory, explain how a cmp/je pair implements an if, and point to where the stack frame is set up (the push ebp / mov ebp, esp prologue).",
    stretch: "Solve a real beginner crackme from crackmes.one and add its write-up as a second entry in the same repo."
  },
  {
    id: "sentinel", tier: "t4", name: "Sentinel — Network Intrusion Detection System", icon: "🚨",
    startsNote: "Kicks off Sep 5 — 2 days after the PET exam, when your schedule opens up.",
    tagline: "Sniff live traffic and raise real-time alerts on port scans, SYN floods and other attacks.",
    stack: ["Python", "raw sockets", "struct", "threading", "CustomTkinter"],
    skills: ["cyber_low", "cyber_high", "python"],
    why: "The capstone that ties your whole summer together. It reuses your sniffer to READ packets, stacks a detection engine on top, and presents it like a real product. A working IDS is the single strongest artifact on a security résumé — it proves you understand offense AND defense, and every other project you built feeds into it.",
    realUse: "This is a miniature Snort/Suricata — the intrusion-detection systems that sit on real networks watching for attacks. Run it on your own LAN, then point your Tier-1 port scanner at the machine and watch Sentinel light up. That demo — one tool you built catching another tool you built — is the kind of thing that ends an interview in your favour.",
    resumeBullet: "Built Sentinel, a real-time network intrusion-detection system in Python: it decodes raw IP/TCP packets, detects port scans and SYN floods with a sliding-window rule engine, and streams severity-ranked alerts to a live GUI dashboard.",
    stages: [
      { name: "1 · Capture & decode",
        goal: "Reuse your sniffer to pull (source IP, dest port, TCP flags) off every packet.",
        dq: ["Which socket type gives you raw frames, and which module unpacks the header bytes?",
             "Inside the TCP header, where do the SYN and ACK flags live?",
             "What three fields does a detector actually need out of each packet?"],
        hints: ["A raw socket + struct.unpack on the IP and TCP headers — exactly your Tier-1 sniffer.",
                "The flags are a single byte; SYN and ACK are individual bits you mask out.",
                "OUTLINE: for each packet, emit a small record {src_ip, dst_port, is_syn, is_ack} and feed it to the engine."] },
      { name: "2 · The rule engine",
        goal: "Detect a port scan and a SYN flood from the packet stream.",
        dq: ["What does a port scan look like in the data (one source → many DISTINCT ports, fast)?",
             "How is a SYN flood different (many SYNs, few completed handshakes)?",
             "Why do you need a TIME WINDOW, not just a raw count?"],
        hints: ["Keep a per-source set of ports seen in the last N seconds; scan = the set crosses a threshold.",
                "Count SYNs vs ACKs per source; a flood is lots of SYN with almost no matching ACK.",
                "OUTLINE: a sliding window (timestamps you expire) makes '20 ports in 5 seconds' expressible."] },
      { name: "3 · Alerts & state",
        goal: "Turn detections into clean, ranked, de-duplicated alerts.",
        dq: ["How do you avoid firing 1,000 identical alerts for one ongoing scan?",
             "How do you rank severity (info vs critical)?",
             "What does an alert need to be useful later (time, source, rule, evidence)?"],
        hints: ["Dedupe by (source, rule) with a cooldown; only re-alert after it expires.",
                "Severity from how far over the threshold it went, or which rule fired.",
                "OUTLINE: an Alert dataclass; a dict of active alerts keyed by (src, rule); append to a log file too."] },
      { name: "4 · Live dashboard + config",
        goal: "Show alerts live without freezing capture, and make rules editable without code.",
        dq: ["If capture and the GUI share one thread, what happens — and how do you fix it?",
             "How does the GUI get new alerts without blocking?",
             "How do you let someone tune thresholds without editing Python?"],
        hints: ["Capture on a background thread; push alerts onto a queue the GUI polls on a timer.",
                "A thread-safe queue.Queue decouples the sniffer from the CustomTkinter window.",
                "OUTLINE: load thresholds/rules from a config.json so a non-coder can tune sensitivity."] }
    ],
    ship: [
      "Git repo — first commit is the working capture→detect→alert pipeline.",
      "README with the money demo: run Sentinel, scan yourself with your Tier-1 scanner, screenshot the alert.",
      "Ship the config.json and a sample alerts.log so the behaviour is reproducible.",
      "Run it as root/admin note + a clean Ctrl-C shutdown (threads join, socket closes).",
      "One stretch shipped (see below)."
    ],
    proveIt: "Delete the detection module. From a blank file, rebuild the port-scan detector (per-source sliding-window of distinct ports + threshold) in under 25 minutes, no reference.",
    stretch: "Add an ARP-spoofing rule, replay a captured .pcap through the engine for testing, or fire a desktop/email notification on a critical alert."
  }
];

export function projectById(id) { return projects.find((p) => p.id === id); }
export function projectsInTier(tierId) { return projects.filter((p) => p.tier === tierId); }
