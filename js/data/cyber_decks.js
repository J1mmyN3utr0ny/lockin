// cyber_decks.js — flashcards seeded from the two GAMA self-check sheets the user provided
// (Networks + ASM). Same "can you explain this term?" format, now with a back side to check
// yourself against and spaced repetition on top.

export const decks = {
  net: {
    id: "net", title: "Networks", gama: "Exam-day 'Networks' + invented-protocol section",
    prompt: "Can you explain this to someone else?",
    cards: [
      { id: "net-postget", term: "POST / GET", explain: "HTTP methods. GET reads a resource (params in the URL, no body); POST submits data in the request body (forms, uploads)." },
      { id: "net-dns", term: "DNS", explain: "Domain Name System — resolves names (example.com) to IP addresses, usually over UDP/53. Hierarchical: root → TLD → authoritative." },
      { id: "net-ssh", term: "SSH", explain: "Secure Shell — encrypted remote login / command channel over TCP/22. The secure replacement for Telnet." },
      { id: "net-icmp", term: "ICMP", explain: "IP's control/diagnostic protocol: ping, traceroute, 'destination unreachable'. Carries no application data." },
      { id: "net-bla", term: "bind–listen–accept", explain: "The server-side TCP socket sequence: bind() to IP:port, listen() to make it passive, accept() to take an incoming connection." },
      { id: "net-broadcast", term: "Broadcast", explain: "One packet delivered to every host on a subnet (e.g. 255.255.255.255, ARP 'who has?'). No single target." },
      { id: "net-arp", term: "ARP", explain: "Address Resolution Protocol — maps an IP to a MAC on the local link via a broadcast 'who has this IP?'." },
      { id: "net-telnet", term: "Telnet", explain: "Old plaintext remote-terminal protocol over TCP/23. Insecure — everything is unencrypted; use SSH instead." },
      { id: "net-trace", term: "Trace (traceroute)", explain: "Discovers each router hop to a destination by sending packets with increasing TTL and reading the ICMP time-exceeded replies." },
      { id: "net-dhcp", term: "DHCP", explain: "Auto-assigns IP / mask / gateway / DNS to hosts. Handshake = DORA: Discover, Offer, Request, Ack (over UDP)." },
      { id: "net-hub", term: "Hub", explain: "Dumb Layer-1 device that repeats every incoming signal out all ports (one collision domain). Replaced by switches." },
      { id: "net-nat", term: "NAT", explain: "Network Address Translation — rewrites private IPs to a shared public IP (and back), so many hosts use one address." },
      { id: "net-dmz", term: "DMZ", explain: "A semi-trusted segment exposing public servers (web/mail) to the internet while isolating them from the internal LAN." },
      { id: "net-bridge", term: "Bridge", explain: "A Layer-2 device joining two segments and forwarding frames by MAC. A switch is essentially a multiport bridge." },
      { id: "net-ttl", term: "TTL", explain: "Time To Live — IP-header counter decremented each hop; at 0 the packet is dropped. Prevents loops; powers traceroute." },
      { id: "net-socket", term: "socket", explain: "An endpoint for communication = (IP, port, protocol). The OS API your code uses to send/receive over the network." },
      { id: "net-ipconfig", term: "ipconfig", explain: "Windows command to view/manage IP config: address, mask, gateway, DNS. Flags: /release /renew /flushdns." },
      { id: "net-imap", term: "IMAP", explain: "Email retrieval that keeps mail on the server and syncs folders across devices (POP3 downloads and deletes instead)." },
      { id: "net-wireshark", term: "Wireshark", explain: "Packet capture/analyzer — inspect real traffic frame-by-frame across every layer of the stack." },
      { id: "net-synack", term: "SYN / ACK", explain: "TCP 3-way handshake flags: client SYN → server SYN-ACK → client ACK establishes the connection." },
      { id: "net-tcp", term: "TCP", explain: "Connection-oriented, reliable, ordered byte-stream: handshake, ACKs, retransmission, flow & congestion control." },
      { id: "net-udp", term: "UDP", explain: "Connectionless, unreliable, low-overhead datagrams — no handshake or ordering. Used for DNS, streaming, games." },
      { id: "net-ip", term: "IP", explain: "Internet Protocol — best-effort, connectionless addressing + routing of packets. IPv4 = 32-bit, IPv6 = 128-bit." }
    ]
  },
  asm: {
    id: "asm", title: "Assembly / Low-level", gama: "Exam-day 'ASM' + battle-calculator / memory-32 section",
    prompt: "Can you explain this to someone else?",
    cards: [
      { id: "asm-pe", term: "PE", explain: "Portable Executable — the Windows .exe/.dll format. Starts with an MZ/DOS header, then the PE header and sections (.text/.data/...)." },
      { id: "asm-elf", term: "ELF", explain: "Executable and Linkable Format — the Linux/Unix binary format for executables, object files, and shared libraries." },
      { id: "asm-bss", term: "BSS", explain: "Segment for uninitialized (zero-initialized) globals/statics. Takes no file space; the loader zeroes it in memory." },
      { id: "asm-protmode", term: "Protected Mode", explain: "x86 CPU mode with virtual memory, privilege rings and memory protection — vs real mode's flat 1 MB access." },
      { id: "asm-arm", term: "ARM", explain: "A RISC CPU architecture (phones/embedded): load/store, fixed-length instructions — contrast with x86 (CISC)." },
      { id: "asm-int80", term: "int 0x80", explain: "Classic Linux 32-bit syscall gate: put the syscall number in eax, args in registers, then int 0x80." },
      { id: "asm-rva", term: "RVA", explain: "Relative Virtual Address — an offset relative to the module's base address in memory (used throughout PE files)." },
      { id: "asm-mz", term: "MZ", explain: "The magic bytes 'MZ' at the start of every DOS/PE file (initials of Mark Zbikowski) — the DOS header signature." },
      { id: "asm-loop", term: "loop", explain: "x86 instruction: decrement ecx and jump to a label while ecx ≠ 0. A built-in counted loop." },
      { id: "asm-cache", term: "Cache", explain: "Small fast CPU memory (L1/L2/L3) holding recently used data/instructions to hide slow RAM latency." },
      { id: "asm-farnear", term: "far / near", explain: "Pointer/call types: near = within the current segment (offset only); far = includes the segment selector (crosses segments)." },
      { id: "asm-x86", term: "x86", explain: "The Intel/AMD CISC instruction-set architecture (32-bit, and the base of 64-bit x86-64)." },
      { id: "asm-bt", term: "BT", explain: "Bit Test — copies a chosen bit of an operand into the carry flag. BTS/BTR/BTC also set/reset/complement it." },
      { id: "asm-ip", term: "Instruction pointer", explain: "The register (EIP/RIP) holding the address of the next instruction to execute." },
      { id: "asm-stackframe", term: "Stack frame", explain: "A function's slice of the stack: saved base pointer, return address, locals and args — framed by EBP/ESP." },
      { id: "asm-codeseg", term: "Code segment", explain: "The memory segment holding executable instructions; the CS register selects it." },
      { id: "asm-interrupt", term: "Interrupt", explain: "A signal that pauses the CPU to run a handler (hardware IRQ or software int). A vector table maps number → handler." },
      { id: "asm-register", term: "Register", explain: "A tiny, extremely fast CPU storage cell (eax, ebx, ecx, edx, esi, edi, esp, ebp, ...) where operands live." },
      { id: "asm-carry", term: "Carry flag", explain: "Status bit set when an unsigned add overflows or a subtract borrows; also the target of shifts and BT." },
      { id: "asm-jne", term: "JNE", explain: "Jump if Not Equal — conditional jump taken when the zero flag is 0 (the previous cmp was unequal)." },
      { id: "asm-call", term: "Call", explain: "Pushes the return address and jumps to a subroutine; RET pops it to return to the caller." },
      { id: "asm-label", term: "Label", explain: "A named location in assembly source that jumps/calls target; the assembler resolves it to an address." },
      { id: "asm-int21", term: "int 0x21", explain: "The DOS API software interrupt: choose the service in ah (print string, file I/O, exit, ...)." }
    ]
  },
  linux: {
    id: "linux", title: "Linux", gama: "Exam-day 'Linux' test + the research workshop environment",
    prompt: "Can you explain this to someone else?",
    cards: [
      { id: "lx-pwd", term: "pwd / cd / ls", explain: "The navigation trio: print working directory, change directory, list contents (ls -la shows hidden files + permissions)." },
      { id: "lx-cat", term: "cat / less / head / tail", explain: "Read files: cat dumps all, less pages through, head/tail show the first/last N lines (tail -f follows a growing log)." },
      { id: "lx-cpmv", term: "cp / mv / rm / mkdir / touch", explain: "File ops: copy, move-or-rename, remove (rm -r for folders — no recycle bin!), make directory, create empty file / update timestamp." },
      { id: "lx-find", term: "find", explain: "Search the filesystem by name/type/size, e.g. find / -name '*.conf'. Walks directories recursively." },
      { id: "lx-grep", term: "grep", explain: "Search INSIDE text: grep -r 'password' . finds a string in all files under the current dir. -i ignores case, -n shows line numbers." },
      { id: "lx-pipe", term: "pipes  |", explain: "Chain commands: the output of one becomes the input of the next, e.g. ps aux | grep python. The core Unix idea: small tools composed." },
      { id: "lx-redir", term: "redirection  > >> 2>", explain: "> writes stdout to a file (overwrites), >> appends, 2> redirects stderr. cmd > out.txt 2>&1 captures everything." },
      { id: "lx-perm", term: "rwx permissions", explain: "Each file has read/write/execute for owner/group/others (e.g. rwxr-xr--). chmod changes them (chmod +x script.sh), chown changes the owner." },
      { id: "lx-sudo", term: "sudo / root", explain: "root is the all-powerful admin account; sudo runs a single command with root privileges. Most system files need it." },
      { id: "lx-ps", term: "ps / top / kill", explain: "Processes: ps aux lists them, top is a live monitor, kill <PID> sends a terminate signal (kill -9 forces)." },
      { id: "lx-man", term: "man", explain: "The built-in manual: man grep explains every flag of grep. Fastest way to learn any command." },
      { id: "lx-apt", term: "apt", explain: "Debian/Ubuntu package manager: sudo apt update refreshes the index, sudo apt install <pkg> installs software." },
      { id: "lx-home", term: "~ , / and the filesystem tree", explain: "/ is the root of everything; ~ is your home dir. Key dirs: /etc (config), /home, /var (logs), /bin + /usr/bin (programs), /tmp." },
      { id: "lx-bash", term: "bash script + shebang", explain: "A text file of commands starting with #!/bin/bash; chmod +x it and run ./script.sh. Supports variables, if, for." },
      { id: "lx-ssh", term: "ssh (client)", explain: "ssh user@host opens an encrypted shell on a remote machine; scp copies files over the same channel." },
      { id: "lx-tar", term: "tar / gzip", explain: "Archive + compress: tar -czf out.tar.gz dir/ packs, tar -xzf out.tar.gz unpacks. The .tar.gz you'll meet everywhere." },
      { id: "lx-env", term: "environment variables / PATH", explain: "Key=value pairs processes inherit. PATH lists dirs searched for commands — why 'python' works from anywhere. export sets one." },
      { id: "lx-wsl", term: "WSL", explain: "Windows Subsystem for Linux — a real Ubuntu shell inside Windows (wsl --install). Your easiest daily Linux driver." }
    ]
  },
  cmd: {
    id: "cmd", title: "Windows CMD", gama: "Exam-day 'Windows' test; your course takes CMD to high",
    prompt: "Can you explain this to someone else?",
    cards: [
      { id: "cmd-dir", term: "dir / cd / type", explain: "Navigation: dir lists (like ls), cd changes dir, type prints a file (like cat). cd \\ jumps to the drive root." },
      { id: "cmd-copy", term: "copy / move / del / mkdir", explain: "File ops: copy, move-or-rename, delete (del /s recurses), make directory (rmdir /s /q removes a tree)." },
      { id: "cmd-ipconfig", term: "ipconfig", explain: "Show network config; /all adds MAC + DHCP + DNS details; /release + /renew re-lease the IP; /flushdns clears the DNS cache." },
      { id: "cmd-ping", term: "ping", explain: "Send ICMP echo requests to test reachability + latency. -t pings forever, -n sets the count." },
      { id: "cmd-tracert", term: "tracert", explain: "Windows traceroute — lists every router hop to a target using rising TTLs. Where a connection dies." },
      { id: "cmd-nslookup", term: "nslookup", explain: "Query DNS by hand: nslookup site.com asks the resolver for its records — you literally rebuilt this tool in Python." },
      { id: "cmd-netstat", term: "netstat -ano", explain: "All open connections + listening ports with owning PID. THE command for 'what is talking to the network?'" },
      { id: "cmd-tasklist", term: "tasklist / taskkill", explain: "List running processes; kill by PID (taskkill /PID 1234 /F) or by name (/IM chrome.exe). Pairs with netstat's PID column." },
      { id: "cmd-findstr", term: "findstr", explain: "Windows grep: dir | findstr .py filters output; findstr /s /i \"key\" *.txt searches inside files recursively." },
      { id: "cmd-redir", term: "redirection & chaining  > | && ||", explain: "> writes to a file, | pipes to the next command, && runs the next only on success, || only on failure." },
      { id: "cmd-arp", term: "arp -a", explain: "Show the IP→MAC table your machine learned via ARP — every device it recently talked to on the LAN." },
      { id: "cmd-route", term: "route print", explain: "The routing table: which gateway/interface each destination network uses. 0.0.0.0 is the default route." },
      { id: "cmd-getmac", term: "getmac / whoami / systeminfo", explain: "Quick recon: MAC addresses, current user + privileges, and full OS/hardware/patch info." },
      { id: "cmd-set", term: "set / %PATH%", explain: "set lists environment variables; %VAR% expands one. PATH decides which folders are searched for commands." },
      { id: "cmd-bat", term: ".bat scripts", explain: "A text file of CMD commands. @echo off hides echo, %1 %2 are arguments, pause waits for a key. The publish.bat in this repo is one!" },
      { id: "cmd-help", term: "help /?", explain: "Every command explains itself: netstat /? or help copy. The CMD equivalent of man." }
    ]
  }
};

export const deckList = Object.values(decks);
export function allCards() { return deckList.flatMap((d) => d.cards); }
