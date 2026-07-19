# depth_cyber_high.py — extended teaching content for the cyber_high track.
# Auto-attached by depth.py. One entry per lesson id.
DEPTH = {
    "ch-1": {
        "title_check": "The layers",
        "sections": [
            {
                "h": "MENTAL MODEL: NESTED ENVELOPES, NOT STACKED PANCAKES",
                "body": (
                    "Picture mailing a letter through four different postal systems, each one stuffing the previous "
                    "envelope inside a bigger envelope addressed for its own leg of the trip. That is encapsulation, "
                    "and it is the single fact that makes the whole TCP/IP model click. The application layer "
                    "produces raw data (an HTTP request, a DNS question). The transport layer wraps that data in a "
                    "TCP segment or UDP datagram, adding source and destination PORT numbers that only it understands "
                    "- IP has no concept of a port. The internet layer wraps that segment inside an IP packet, adding "
                    "source and destination IP addresses - the link layer has no concept of an IP address. The link "
                    "layer wraps the IP packet inside an Ethernet frame, adding source and destination MAC addresses "
                    "- the physical wire has no concept of any of that, it just sees signal.\n\n"
                    "The PDU (protocol data unit) has a different name at each layer, and exam questions test whether "
                    "you know which: a FRAME at the link layer, a PACKET at the internet layer, a SEGMENT (TCP) or "
                    "DATAGRAM (UDP) at the transport layer, and simply DATA at the application layer. Each layer's "
                    "device only ever reads its own envelope: a switch reads MAC addresses and ignores everything "
                    "inside the frame; a router reads IP addresses and does not care what TCP port is in use. This "
                    "strict ignorance is a feature - it is what lets you swap Wi-Fi for Ethernet without touching a "
                    "single line of your browser's code."
                ),
            },
            {
                "h": "HEADER ORDER: WHAT ACTUALLY SITS ON THE WIRE",
                "body": (
                    "Bytes on the wire have a fixed, non-negotiable order. An Ethernet frame starts with 14 bytes: "
                    "6 bytes destination MAC, 6 bytes source MAC, then a 2-byte EtherType telling the receiver what "
                    "is inside - 0x0800 means IPv4 follows, 0x0806 means ARP, 0x86DD means IPv6. Strip that off and "
                    "you find the IPv4 header: a version+IHL byte (usually 0x45 - version 4, header length 5 words "
                    "= 20 bytes), total length, an identification field and flags/fragment-offset used for "
                    "fragmentation, a TTL byte, a PROTOCOL byte (6 = TCP, 17 = UDP, 1 = ICMP - this is IP's own "
                    "EtherType-equivalent), a header checksum, then the 4-byte source IP and 4-byte destination IP.\n\n"
                    "Strip that off and you reach the TCP header: 2-byte source port, 2-byte destination port, a "
                    "4-byte sequence number, a 4-byte acknowledgment number, a data-offset+flags byte (SYN, ACK, FIN, "
                    "RST, PSH, URG live here as individual bits), a 2-byte window size, checksum, and urgent "
                    "pointer - 20 bytes minimum, options after. Only then does your actual data begin. Notice the "
                    "pattern: every layer has its own 'what's inside' field (EtherType, then IP protocol number, then "
                    "a TCP/UDP port implying an application) - that chain of fields is literally how a machine "
                    "de-encapsulates a packet without ever having to guess."
                ),
            },
            {
                "h": "A WORKED HEX DUMP, BYTE BY BYTE",
                "body": (
                    "Run `tcpdump -i eth0 -xx -c1 tcp` and you get a raw hex line like this for one frame:\n\n"
                    "    aa bb cc dd ee ff  11 22 33 44 55 66  08 00\n"
                    "    45 00 00 3c 1a 2b 40 00 40 06 5f 3a\n"
                    "    c0 a8 01 0a  5d b8 d8 22\n"
                    "    c1 f0 00 50  00 00 12 34  00 00 00 00  a0 02 ff ff\n\n"
                    "Read it left to right: `aa bb cc dd ee ff` is the destination MAC, `11 22 33 44 55 66` the "
                    "source MAC, `08 00` the EtherType - IPv4 follows. Next `45` says IPv4, 20-byte header; `00 3c` "
                    "is total length (60 bytes); skip ahead to `40` = TTL 64; `06` = protocol TCP; then "
                    "`c0 a8 01 0a` = 192.168.1.10 (source IP) and `5d b8 d8 22` = 93.184.216.34 (destination IP, "
                    "example.com). Now the TCP header: `c1 f0` = source port 49648, `00 50` = destination port 80, "
                    "`00 00 12 34` the sequence number, `00 00 00 00` the ack number (0 because this is a SYN), and "
                    "`a0 02` packs the flags byte - bit 0x02 set means SYN. This is exactly the skill GAMA and any "
                    "packet-analysis test actually wants: turning raw hex into named fields without a tool doing it "
                    "for you."
                ),
            },
            {
                "h": "WHEN LAYERS LIE: SPOOFING AND CROSS-LAYER ATTACKS",
                "body": (
                    "Every layer boundary is also a trust boundary, and most link/internet-layer protocols were "
                    "designed with zero authentication - which is exactly what makes spoofing possible. ARP replies "
                    "are accepted by hosts with no proof the replier actually owns that IP, so ARP cache poisoning "
                    "lets an attacker on the same LAN tell everyone 'I am the gateway,' silently inserting themselves "
                    "as a man-in-the-middle. IP itself carries a source address field that the sender fills in "
                    "unchecked - IP spoofing forges it, which is why reflected DDoS and blind injection attacks "
                    "exist, and why ingress/egress filtering (BCP38) matters at network edges.\n\n"
                    "VLAN hopping abuses the fact that 802.1Q tags sit in the middle of the Ethernet header: double "
                    "tagging a frame can make a switch strip the outer tag and forward the inner-tagged frame into a "
                    "VLAN the attacker was never authorized to reach. MAC flooding overwhelms a switch's "
                    "CAM (MAC address) table so it fails open into hub-like broadcast mode, letting an attacker "
                    "sniff traffic meant for other hosts. The common thread: each layer trusts unauthenticated "
                    "claims from the layer at or below it, and understanding the header fields from section 2 is "
                    "exactly what lets you see why these attacks are structurally possible, not just 'a hacker "
                    "trick.'"
                ),
            },
            {
                "h": "HOW ANALYSTS USE LAYERS TO TRIAGE A PROBLEM",
                "body": (
                    "'The network is broken' is not a diagnosis - a working analyst walks the stack bottom-up (or "
                    "top-down) to localize the fault to one layer. Start at the link layer: is the interface up, "
                    "does `arp -a` show a MAC for the gateway? Move to the internet layer: does `ping <gateway>` "
                    "succeed (ICMP echo, confirms IP reachability on-segment) and does `ping 8.8.8.8` succeed "
                    "(confirms routing off-segment)? Move to transport: does `ss -tan` or `netstat -an` show the "
                    "expected socket in ESTABLISHED state, or is it stuck in SYN_SENT (server never replied - "
                    "firewall drop or the service is down)? Finally application: does `curl -v` or `dig` get a "
                    "sane response?\n\n"
                    "Wireshark encodes this same discipline in its Statistics > Protocol Hierarchy view, which shows "
                    "what percentage of captured bytes belong to each layer's protocol - a capture that is 90% "
                    "TCP retransmissions with almost no HTTP tells a very different story than one full of clean "
                    "HTTP 200s. Filtering by layer (`eth.addr==`, `ip.addr==`, `tcp.port==`, then finally `http` or "
                    "`dns`) lets you isolate 'is this a wiring problem, a routing problem, a connection problem, or "
                    "an application bug' in minutes instead of guessing."
                ),
            },
            {
                "h": "OSI'S SEVEN LAYERS VS TCP/IP'S FOUR, AND WHAT COMES NEXT",
                "body": (
                    "You will see both models in interviews and exams, and they are not competitors - OSI is a "
                    "teaching/reference model, TCP/IP is what actually runs the internet. OSI splits things TCP/IP "
                    "merges: OSI's layer 7 (Application), 6 (Presentation - encoding/encryption like TLS) and 5 "
                    "(Session - who's talking to whom) all collapse into TCP/IP's single Application layer. OSI's "
                    "layer 2 (Data Link) and layer 1 (Physical) are both inside TCP/IP's Link layer. The middle "
                    "maps cleanly: OSI layer 4 Transport = TCP/IP Transport, OSI layer 3 Network = TCP/IP Internet. "
                    "When someone says 'TLS operates at layer 6' or 'that's a layer 2 attack,' they are using OSI "
                    "numbering even though the traffic is running over TCP/IP - both vocabularies describe the same "
                    "wire.\n\n"
                    "This lesson is the map for the entire rest of the track. ch-2 zooms into one layer - transport "
                    "- and the handshake that makes TCP reliable. ch-3 walks every layer in order for one real "
                    "action (loading a page). ch-4 gives you the tool to watch all of this happen live. ch-5 goes "
                    "back into the transport layer to explain sockets and ports precisely. ch-6 zooms into the "
                    "application layer plus the OSI presentation-layer concern of encryption. Every later lesson is "
                    "really just 'layer 1 through 6, in more depth.'"
                ),
            },
        ],
    },
    "ch-2": {
        "title_check": "TCP vs UDP & the handshake",
        "sections": [
            {
                "h": "MENTAL MODEL: SEQUENCE NUMBERS ARE THE PROTOCOL",
                "body": (
                    "It is tempting to think TCP's reliability comes from the handshake alone - it doesn't. The "
                    "handshake just establishes two starting sequence numbers (ISNs, Initial Sequence Numbers), one "
                    "per direction, and from then on every single byte TCP sends is numbered. If the client's ISN "
                    "is 5000, the first byte of data it sends is sequence number 5001, and if it sends 200 bytes the "
                    "next segment starts at 5201. The receiver's ACK number is not 'yes I got a packet' - it is "
                    "literally 'I have successfully received everything up through byte N-1, send me byte N next.' "
                    "That is what makes TCP self-healing: if a segment is lost, the receiver keeps ACKing the old "
                    "number, the sender notices no forward progress and retransmits exactly the missing bytes.\n\n"
                    "ISNs are randomized (not counted up from 0) specifically as a security measure - if an "
                    "off-path attacker could predict your ISN, they could forge segments into an existing connection "
                    "without ever seeing your traffic (classic TCP sequence prediction attacks from the 1990s, e.g. "
                    "Kevin Mitnick's IP spoofing attack against Tsutomu Shimomura). Sequence numbers are also how a "
                    "sliding window works: the window size field tells the sender how many unacknowledged bytes it "
                    "is allowed to have in flight before pausing, which is TCP's flow-control mechanism."
                ),
            },
            {
                "h": "THE HEADERS, FIELD BY FIELD",
                "body": (
                    "TCP's flags live in a single byte, each flag one bit: URG(0x20) ACK(0x10) PSH(0x08) RST(0x04) "
                    "SYN(0x02) FIN(0x01). A flags byte of 0x02 is a bare SYN; 0x12 is SYN+ACK (0x10|0x02); 0x18 is "
                    "PSH+ACK (0x10|0x08), the common flag combo for 'here is data, and yes I got yours'; 0x04 alone "
                    "is a RST, an immediate, unilateral connection abort with no handshake. Beyond the flags, TCP "
                    "carries a 16-bit window size (flow control), a checksum covering a pseudo-header (source IP, "
                    "dest IP, protocol, TCP length) plus the segment itself - meaning TCP's checksum actually "
                    "verifies the IP addresses too, one reason NAT devices must rewrite it.\n\n"
                    "UDP's header, by contrast, is 8 bytes total: source port, destination port, length, checksum - "
                    "nothing else. No sequence numbers, no ACKs, no window, no flags, no handshake. That absence is "
                    "not a missing feature, it is the whole design point: UDP hands your datagram to IP and gets out "
                    "of the way, which is exactly why DNS (one query, one reply, retry yourself if needed) and "
                    "real-time media (a late packet is worse than a lost one) prefer it over TCP's guarantees."
                ),
            },
            {
                "h": "A FULL CONNECTION, OPEN TO CLOSE",
                "body": (
                    "The three-way handshake only opens the connection; a real session also has data transfer and "
                    "an orderly close, and every step moves sequence/ack numbers forward:\n\n"
                    "    1. Client -> Server  SYN               seq=100\n"
                    "    2. Server -> Client  SYN, ACK          seq=500 ack=101\n"
                    "    3. Client -> Server  ACK               seq=101 ack=501\n"
                    "    4. Client -> Server  PSH, ACK  (data)  seq=101 ack=501  [50 bytes]\n"
                    "    5. Server -> Client  ACK               seq=501 ack=151\n"
                    "    6. Server -> Client  FIN, ACK           seq=501 ack=151\n"
                    "    7. Client -> Server  ACK               seq=151 ack=502\n"
                    "    8. Client -> Server  FIN, ACK           seq=151 ack=502\n"
                    "    9. Server -> Client  ACK               seq=502 ack=152\n\n"
                    "Notice each ACK number equals 'the other side's last seq plus however many bytes they sent' - "
                    "after 50 bytes of data at seq=101, the next expected byte is 151, so ack=151. A four-way close "
                    "(FIN/ACK each direction, since TCP is full-duplex and each side closes independently) is normal; "
                    "a bare RST instead of this sequence means an abrupt abort, not a graceful close - a detail "
                    "worth spotting in any capture."
                ),
            },
            {
                "h": "ABUSING THE HANDSHAKE: SYN FLOODS AND RESET ATTACKS",
                "body": (
                    "A SYN flood exploits the asymmetry of step 1 vs step 2: the server must allocate state (a "
                    "half-open connection entry in its backlog queue) the instant it sees a SYN, before it has any "
                    "proof the client is real or will ever send the final ACK. An attacker spoofing thousands of "
                    "source IPs and sending only SYNs can exhaust that backlog queue, and legitimate clients get "
                    "refused - the server never even sees their SYN. SYN cookies are the classic defense: instead "
                    "of storing state, the server encodes the connection info into the ISN it sends back in the "
                    "SYN-ACK, cryptographically, so it can verify a returning ACK without having remembered "
                    "anything.\n\n"
                    "RST injection is a different abuse: since a bare RST tears down a connection instantly with no "
                    "handshake, an attacker who can guess (or is on-path and can see) the correct sequence number can "
                    "forge a RST and kill someone else's TCP connection - this is exactly the technique the Great "
                    "Firewall of China has historically used to sever connections to blocked sites. Both attacks "
                    "work precisely because the fields you just learned - SYN, ACK, sequence numbers - are the "
                    "entire trust mechanism, and TCP has no built-in authentication of who sent a given flag."
                ),
            },
            {
                "h": "READING CONNECTION STATE LIKE AN ANALYST",
                "body": (
                    "TCP is a state machine, and `ss -tan` or `netstat -an` show you exactly which state every "
                    "connection is in: LISTEN (server bound, waiting), SYN_SENT (client sent SYN, awaiting "
                    "SYN-ACK - stuck here means the server or a firewall is silently dropping it), SYN_RECV "
                    "(server got a SYN, sent SYN-ACK, awaiting final ACK - many of these is a SYN flood signature), "
                    "ESTABLISHED (data can flow), FIN_WAIT_1/2 and CLOSE_WAIT (mid-close), and TIME_WAIT (closed but "
                    "held briefly so any delayed duplicate segments don't confuse a future connection reusing the "
                    "same port - a huge pile of TIME_WAIT sockets on a busy server is a well-known scaling problem, "
                    "not a bug.\n\n"
                    "In Wireshark, retransmissions are flagged directly - look for '[TCP Retransmission]' or "
                    "'[TCP Dup ACK]' in the packet list, which means the sender resent data or the receiver is "
                    "signalling a gap. A connection full of retransmissions but no RSTs usually means packet loss "
                    "on the path, not an application bug; a connection that gets an immediate RST right after SYN "
                    "usually means 'port closed' or 'firewall actively refusing,' versus a SYN that gets no reply at "
                    "all, which usually means 'silently dropped.' That distinction - refused vs dropped - is exactly "
                    "how port scanners like nmap infer firewall behavior."
                ),
            },
            {
                "h": "WINDOWS, CONGESTION, AND WHERE PORTS COME IN",
                "body": (
                    "The window field you saw in the header is TCP's receiver-side flow control: 'don't send me "
                    "more than this many unacknowledged bytes, I only have so much buffer.' Separately, TCP also "
                    "does sender-side congestion control - a concept not in the header at all but implemented in "
                    "the sending OS's TCP stack (slow start, then congestion avoidance, backing off when losses are "
                    "detected). Together these two mechanisms are why TCP throughput ramps up gradually at the "
                    "start of a connection and backs off under loss, rather than blasting at full line rate "
                    "immediately - UDP has neither, so a UDP flood can saturate a link instantly, another reason "
                    "it is favored for both real-time media and, less charitably, for flood-style DoS traffic.\n\n"
                    "Everything in this lesson - flags, sequence numbers, the handshake - happens between a source "
                    "port and a destination port, and it is the pairing of an IP and a port that actually identifies "
                    "'who is talking to whom' on a machine running many services at once. ch-5 picks up exactly "
                    "there: what a port and a socket really are, and how the operating system routes an incoming "
                    "segment to the one process that owns it."
                ),
            },
        ],
    },
    "ch-3": {
        "title_check": "Open a website — the full trace",
        "sections": [
            {
                "h": "MENTAL MODEL: CACHES BEFORE WIRES",
                "body": (
                    "The 'full trace' most people memorize (DNS, ARP, TCP, TLS, HTTP) is actually the worst case - "
                    "the slow path taken only when every local cache is empty. Your machine checks, in order: the "
                    "browser's own DNS cache, the OS resolver cache (`systemd-resolved` or Windows DNS client "
                    "service), and the ARP cache (`arp -a`) - each populated from a previous lookup and given a "
                    "TTL (time to live) after which it must be re-verified. Only a genuine cache miss at each stage "
                    "triggers the corresponding protocol on the wire. This is why the second time you visit a site "
                    "loads faster and generates a visibly smaller packet capture than the first: fewer of these "
                    "steps actually have to happen.\n\n"
                    "This matters for analysis, not just performance: if you are staring at a capture wondering "
                    "'why is there no DNS query for this domain the browser clearly just contacted,' the answer is "
                    "almost always a cache hit somewhere in this chain, not a broken capture. Understanding the "
                    "trace as 'a chain of caches with a fallback protocol at each layer' rather than 'five things "
                    "that always happen' is what separates rote memorization from being able to explain an "
                    "unexpected capture."
                ),
            },
            {
                "h": "DNS RESOLUTION, STEP BY STEP",
                "body": (
                    "Your machine is a stub resolver - it does almost no work itself, it asks a recursive resolver "
                    "(your ISP's, or 1.1.1.1 / 8.8.8.8) to do the full job over UDP port 53. That recursive resolver, "
                    "on a cache miss, walks the DNS hierarchy from the top: it asks a root server 'who handles "
                    ".com?', gets back a referral to the .com TLD (top-level domain) servers, asks one of those "
                    "'who handles example.com?', gets a referral to example.com's authoritative name servers, then "
                    "finally asks one of those 'what is the A record for example.com?' and gets the actual IP "
                    "address back. Each referral is cached with its own TTL so the next lookup for any .com domain "
                    "skips the root step entirely.\n\n"
                    "Record types matter: an A record maps a name to an IPv4 address, AAAA to IPv6, CNAME is an "
                    "alias pointing to another name (which itself then needs resolving), MX points at mail servers, "
                    "and NS records are exactly the referrals described above. If UDP's 512-byte-ish practical limit "
                    "is exceeded (many records, DNSSEC signatures), DNS falls back to TCP port 53 - proof that even "
                    "a 'DNS is UDP' fact from ch-2 has a documented, spec-defined exception."
                ),
            },
            {
                "h": "A TIMED TRACE, PACKET BY PACKET",
                "body": (
                    "A cold-cache load of http://example.com looks like this in a capture, roughly in order:\n\n"
                    "    t=0ms    DHCP already done earlier (not re-run per page load)\n"
                    "    t=0ms    DNS query  A example.com   (UDP/53)\n"
                    "    t=8ms    DNS response  93.184.216.34\n"
                    "    t=8ms    ARP who-has 192.168.1.1 (the gateway, not the server!)\n"
                    "    t=9ms    ARP reply  192.168.1.1 is-at aa:bb:cc:dd:ee:ff\n"
                    "    t=9ms    TCP SYN  -> 93.184.216.34:80\n"
                    "    t=30ms   TCP SYN-ACK\n"
                    "    t=30ms   TCP ACK\n"
                    "    t=31ms   HTTP GET /\n"
                    "    t=52ms   HTTP 200 OK + body\n\n"
                    "Two details trip people up every time: the ARP request is for the LOCAL GATEWAY's MAC address, "
                    "never the remote server's, because the server is off-segment and every off-segment packet is "
                    "actually addressed at Ethernet level to the router; and DNS resolves BEFORE ARP because you "
                    "need the destination IP decided before you can figure out where (which local device) to send "
                    "the frame at all - a routing decision (is the destination on my subnet or not) that happens "
                    "after DNS but before the frame is built."
                ),
            },
            {
                "h": "WHERE THE CHAIN CAN BE HIJACKED",
                "body": (
                    "Every unauthenticated step in this trace is a documented attack: DNS cache poisoning forges a "
                    "DNS response (racing the real one, or exploiting weak transaction-ID randomization) so your "
                    "resolver caches an attacker-controlled IP for a legitimate name - DNSSEC exists specifically to "
                    "let you cryptographically verify a response's authenticity, but it is far from universally "
                    "deployed. ARP spoofing/poisoning (introduced in ch-1) is the classic on-LAN man-in-the-middle: "
                    "an attacker sends unsolicited ARP replies claiming to be the gateway, and every packet you "
                    "'send off-segment' actually goes to the attacker first, who can then forward it on invisibly "
                    "while reading or altering it.\n\n"
                    "Rogue DHCP is the same idea one step earlier: since DHCP has no built-in server authentication, "
                    "an attacker's rogue DHCP server can race the real one and hand out itself as the default "
                    "gateway or DNS server to new clients, silently controlling both of the next two steps in this "
                    "entire trace before the victim even makes a request. Notice the pattern across all three: "
                    "the attack is not breaking cryptography, it is exploiting the fact that these foundational "
                    "protocols were designed for a cooperative network, not a hostile one."
                ),
            },
            {
                "h": "TOOLS A NETWORK ANALYST REACHES FOR",
                "body": (
                    "`dig example.com` (or `nslookup` on Windows) shows you the DNS answer plus which server "
                    "answered and how long it took - `dig +trace example.com` re-runs the full root->TLD->"
                    "authoritative walk manually, which is the single best way to actually see the hierarchy from "
                    "section 2 instead of just reading about it. `traceroute` (Linux) / `tracert` (Windows) reveals "
                    "every router hop between you and the destination by sending packets with increasing TTL and "
                    "recording who sends back the 'TTL exceeded' ICMP message - useful for spotting where in the "
                    "path latency or loss is actually happening.\n\n"
                    "Real investigations rarely rely on one tool - they correlate logs across the chain: DHCP "
                    "server logs show who got which IP and when, DNS resolver logs show what was queried and by "
                    "whom, and a proxy or firewall log shows the eventual TCP/HTTP connection. If a compromised "
                    "host is calling out to a malicious domain, DNS logs alone often catch it before a full packet "
                    "capture would - which is exactly why 'DNS monitoring' is a standard, cheap detection control "
                    "in real security operations centers, not just an academic topic."
                ),
            },
            {
                "h": "PUTTING IT ALL TOGETHER: WHERE TIME GOES",
                "body": (
                    "If you total the timed trace from section 3, notice where the milliseconds actually go: DNS "
                    "(8ms) and ARP (1ms) are cheap because they are one-shot request/reply exchanges, but the TCP "
                    "handshake (21ms in the example) costs a full network round-trip before a single byte of your "
                    "actual request can be sent - and if this were HTTPS, add another one-to-two round-trips for "
                    "the TLS handshake (ch-6) before the GET even goes out. This is precisely why performance "
                    "engineers obsess over 'round trips before first byte': TCP Fast Open, DNS prefetching, and "
                    "TLS 1.3's 1-RTT handshake all exist specifically to cut steps out of this exact trace.\n\n"
                    "This lesson is the connective tissue of the whole cyber_high track: ch-1 gave you the layers "
                    "each step belongs to, ch-2 gave you the handshake happening at t=9-30ms above, ch-5 will tell "
                    "you precisely how the OS decided which local process gets that HTTP response, and ch-6 zooms "
                    "into the request/response and encryption you see landing at t=31-52ms. Every acronym you drill "
                    "in isolation lives at a specific millisecond in this one trace."
                ),
            },
        ],
    },
    "ch-4": {
        "title_check": "See it live in Wireshark",
        "sections": [
            {
                "h": "MENTAL MODEL: CAPTURE FILTERS VS DISPLAY FILTERS",
                "body": (
                    "Wireshark has two entirely different filter languages, and confusing them is the single most "
                    "common beginner mistake. A CAPTURE filter (set before you start capturing, using BPF - Berkeley "
                    "Packet Filter - syntax like `tcp port 443`) decides what the network card even hands up to "
                    "Wireshark; anything it excludes is gone forever, never written to the file. A DISPLAY filter "
                    "(typed in the bar after capturing, using Wireshark's own syntax like `tcp.port == 443`) only "
                    "hides rows from view - the underlying capture still has everything, and you can change the "
                    "display filter as many times as you like without recapturing.\n\n"
                    "This distinction matters practically: if you are troubleshooting and aren't sure yet what you "
                    "need, capture broadly (or not at all - just `any`) and filter for display afterward, because "
                    "you cannot get back packets a capture filter threw away. Only use a capture filter when you "
                    "know exactly what you want and volume or disk space is a real constraint - e.g. capturing only "
                    "`host 10.0.0.5` on a busy core link so you don't fill the disk with unrelated traffic in "
                    "seconds."
                ),
            },
            {
                "h": "HOW WIRESHARK ACTUALLY PARSES A PACKET",
                "body": (
                    "For a NIC to hand Wireshark every frame instead of only ones addressed to your machine, the "
                    "interface must be in PROMISCUOUS mode (wired) or MONITOR mode (Wi-Fi) - without it, a switch "
                    "will still only deliver frames destined for your MAC, and you will simply never see anyone "
                    "else's traffic no matter what filter you type. This is also why capturing on a switched network "
                    "usually requires a SPAN/mirror port on the switch, or a physical network tap, positioned "
                    "specifically to duplicate the traffic you actually want to see.\n\n"
                    "Once bytes arrive, Wireshark runs them through a chain of DISSECTORS: one dissector reads the "
                    "Ethernet header and, based on the EtherType field from ch-1, hands the remaining bytes to the "
                    "IP dissector; the IP dissector reads the protocol field and hands off to the TCP or UDP "
                    "dissector; that one reads the port number and, if it recognizes it (80, 443, 53...), hands off "
                    "to an HTTP, TLS, or DNS dissector. 'Follow TCP Stream' works by walking every packet on that "
                    "one connection's exact 4-tuple and reassembling the payload bytes back into the original "
                    "ordered byte stream, undoing TCP segmentation for you."
                ),
            },
            {
                "h": "A WORKED CAPTURE SESSION",
                "body": (
                    "A realistic workflow, command-line first: `sudo tcpdump -i eth0 -w cap.pcap 'tcp port 443'` "
                    "captures only HTTPS traffic to a file for later analysis, using BPF syntax at the capture stage "
                    "(section 1). Opening `cap.pcap` in Wireshark, useful display filters to actually try: `tcp.flags.syn"
                    "==1 && tcp.flags.ack==0` isolates only the initial SYNs, one per new connection attempt - a "
                    "spike of these to different destinations is a classic port/host scan signature. `tcp.analysis."
                    "retransmission` finds every retransmitted segment across the whole capture at once, instead of "
                    "scrolling manually. `http.request` shows only outgoing HTTP requests; `dns.flags.response==0` "
                    "shows only outbound queries.\n\n"
                    "Combining filters is normal practice: `ip.addr==10.0.0.5 && tcp.port==443 && tcp.flags.reset==1` "
                    "answers a very specific question - 'did this one host's HTTPS connection get reset, and by "
                    "whom.' Each of these reads directly off header fields you already know from ch-1/ch-2, which "
                    "is the entire point: Wireshark is not new knowledge, it is a window onto knowledge you already "
                    "have."
                ),
            },
            {
                "h": "WHY YOU CAN'T JUST 'SEE EVERYTHING'",
                "body": (
                    "Even a perfect capture position has fundamental limits. TLS (ch-6) encrypts the HTTP payload, "
                    "so a capture of HTTPS traffic to a compromised or malicious server shows you the TCP handshake "
                    "and the TLS handshake in the clear, but the actual request/response content is opaque unless "
                    "you also have the session keys (e.g. via `SSLKEYLOGFILE` in a lab environment) - malware "
                    "command-and-control traffic deliberately rides on ordinary HTTPS specifically to blend into "
                    "normal traffic and defeat plain packet inspection. This is why modern detection increasingly "
                    "relies on metadata - JA3/JA3S TLS fingerprints, connection timing and volume patterns, and DNS "
                    "queries - rather than payload content.\n\n"
                    "Positioning is a second, more physical limit: on a modern switched network, plugging into a "
                    "random port and running Wireshark shows you only your own machine's traffic, because a switch "
                    "forwards frames only to the port owning the destination MAC - a fundamentally different world "
                    "from an old hub, where every frame reached every port. Real visibility requires deliberately "
                    "engineering a vantage point: a SPAN port, a tap, or software agents running on the endpoints "
                    "themselves."
                ),
            },
            {
                "h": "GOING BEYOND SINGLE PACKETS: WIRESHARK'S STATISTICS TOOLS",
                "body": (
                    "Reading packet-by-packet does not scale past a few hundred frames - real investigations lean "
                    "on Wireshark's Statistics menu. Protocol Hierarchy shows what fraction of the whole capture is "
                    "each protocol, instantly answering 'is this mostly DNS noise or a real TCP conversation.' "
                    "Conversations lists every unique pair of endpoints (by IP, or by TCP/UDP 4-tuple) with byte "
                    "and packet counts and duration - sorting by bytes quickly surfaces the single largest data "
                    "transfer in a capture, a common first step in exfiltration investigations. IO Graphs plots "
                    "traffic volume over time, making a sudden spike (a flood, a burst of scanning) visually "
                    "obvious in a capture too large to read line by line.\n\n"
                    "File > Export Objects > HTTP pulls out every file transferred over plain HTTP in the capture "
                    "- images, scripts, downloaded executables - directly to disk for further analysis (e.g. "
                    "hashing and checking against a malware database). None of this replaces understanding the "
                    "protocol fields from earlier lessons; it is what those fields make possible at scale."
                ),
            },
            {
                "h": "FROM THEORY TO THE PACKET LIST - WHAT'S NEXT",
                "body": (
                    "Wireshark is the lab instrument for everything else in this track: ch-1's layers are literally "
                    "the tree structure in Wireshark's packet-detail pane (Frame, then Ethernet, then IP, then TCP, "
                    "then the application protocol, each expandable); ch-2's flags and sequence numbers are fields "
                    "you can click on directly; ch-3's full trace is something you can now capture and watch happen "
                    "end to end in one sitting on your own machine. Treat every remaining lesson's 'do this' "
                    "exercise as an invitation to actually open Wireshark rather than just reasoning about it on "
                    "paper - reading a real, slightly messy capture (with retransmissions, a stray ARP, a "
                    "background service phoning home) builds an intuition that no textbook description can.\n\n"
                    "ch-5 will have you look specifically at the source/destination port pair on packets you "
                    "capture here and connect it to what `ss`/`netstat` reports locally; ch-6 will have you capture "
                    "and read an actual TLS ClientHello, seeing with your own eyes exactly what is and is not "
                    "encrypted. Wireshark turns every abstract claim in this track into something falsifiable."
                ),
            },
        ],
    },
    "ch-5": {
        "title_check": "Ports, sockets & the client-server model",
        "sections": [
            {
                "h": "MENTAL MODEL: THE SOCKET IS A TUPLE, NOT A NUMBER",
                "body": (
                    "The common shorthand 'port 443 is the socket' is wrong in a way that matters: a socket is "
                    "identified by a full 4-tuple - (source IP, source port, destination IP, destination port), "
                    "sometimes called a 5-tuple when the protocol (TCP/UDP) is included. A busy web server has "
                    "exactly one process listening on port 443, but it can have thousands of simultaneous "
                    "ESTABLISHED connections all sharing that same destination port 443 - what makes each one a "
                    "distinct socket, and lets the OS route incoming data to the correct one, is that every client "
                    "has a different source IP and/or a different source (ephemeral) port.\n\n"
                    "This is why 'how can a server handle multiple clients on one port' stops being confusing once "
                    "you see it: the LISTENING socket (bound to 0.0.0.0:443) exists only to accept new connections; "
                    "the moment a handshake completes, the OS creates a brand new socket scoped to that exact "
                    "4-tuple for the actual data exchange, and the listening socket goes right back to waiting for "
                    "the next SYN. 'The port' was never the whole identity - it was always one quarter of it."
                ),
            },
            {
                "h": "THE SYSCALL DANCE: BIND, LISTEN, ACCEPT, CONNECT",
                "body": (
                    "A server-side program calls four syscalls in order: `socket()` creates an endpoint, `bind()` "
                    "claims a specific local IP+port (or 0.0.0.0 for 'any interface'), `listen()` tells the OS "
                    "'queue incoming connection attempts on this socket instead of rejecting them,' and `accept()` "
                    "blocks until a client's handshake (ch-2) completes, then returns a brand-new socket "
                    "file descriptor for that one connection - the original listening socket is untouched and can "
                    "`accept()` again immediately. A client-side program instead calls `socket()` then `connect()` "
                    "directly, which triggers the SYN and blocks until the handshake finishes or fails.\n\n"
                    "Ephemeral ports are how the client side of this actually works without any coordination: the "
                    "OS auto-assigns the client a source port from a reserved high range (historically 32768-61000 "
                    "on Linux, 49152-65535 per IANA), different for every outgoing connection, specifically so that "
                    "two connections from the same client IP to the same server IP:port remain distinguishable by "
                    "their different client-side ports. This is the concrete syscall-level reality behind the "
                    "abstract 'client connects, server listens' sentence from the lesson's read section."
                ),
            },
            {
                "h": "READING A REAL CONNECTION TABLE",
                "body": (
                    "Run `ss -tan` (or `netstat -an` on older systems / Windows) on a busy machine and you might see:\n\n"
                    "    State       Local Address:Port     Peer Address:Port\n"
                    "    LISTEN      0.0.0.0:443             0.0.0.0:*\n"
                    "    ESTABLISHED 10.0.0.5:443            203.0.113.9:51422\n"
                    "    ESTABLISHED 10.0.0.5:443            203.0.113.9:51500\n"
                    "    ESTABLISHED 10.0.0.5:443            198.51.100.7:34211\n\n"
                    "One LISTEN entry, three ESTABLISHED entries, all sharing local port 443 - exactly the point "
                    "from section 1. The first two rows share the same peer IP (203.0.113.9) but differ in peer "
                    "port, meaning the same remote client opened two separate connections (perhaps two browser "
                    "tabs, or a page with a keep-alive plus a second parallel fetch); the third row is a fully "
                    "different client. If you saw hundreds of ESTABLISHED rows from one peer IP with very short "
                    "lifetimes, that pattern itself is worth flagging - possibly a connection-exhaustion attempt "
                    "rather than a real user."
                ),
            },
            {
                "h": "PORT SCANNING AND ATTACK SURFACE",
                "body": (
                    "Every listening socket is a piece of attack surface, which is why port scanning is the "
                    "reconnaissance step of nearly every intrusion. A TCP connect scan (`nmap -sT`) simply calls "
                    "`connect()` on every port and sees which ones complete a full handshake - reliable but noisy, "
                    "logged by the target as full connections. A SYN scan (`nmap -sS`, the default and the reason "
                    "it's nicknamed a 'half-open' scan) sends only a SYN and, if it gets a SYN-ACK back, immediately "
                    "sends a RST instead of completing the handshake - it never finishes a connection, so it "
                    "historically evaded logs that only recorded completed sessions, and it's faster since the "
                    "kernel never has to allocate a full connected socket.\n\n"
                    "A closed port replies RST immediately; an open port replies SYN-ACK; a firewalled/filtered port "
                    "produces no reply at all - the exact three outcomes described in ch-2's RST discussion, now "
                    "used as a deliberate information-gathering signal rather than an accident. This is precisely "
                    "why security guidance says 'minimize listening services': every open port an attacker finds is "
                    "one more program's worth of code they can try to exploit, whether or not that program has any "
                    "known vulnerability yet."
                ),
            },
            {
                "h": "AUDITING WHAT'S LISTENING ON A MACHINE",
                "body": (
                    "A core defensive habit is periodically auditing your own listening sockets rather than only "
                    "worrying about incoming scans: `ss -tlnp` (or `netstat -tlnp` on Linux, needs root to show the "
                    "owning process) lists every LISTEN socket along with the PID and process name that owns it. "
                    "An analyst reviewing this output is looking for exactly one thing: any listener they cannot "
                    "immediately explain - a webserver on 8080 nobody remembers starting, a shell listening on an "
                    "unusual high port, anything bound to 0.0.0.0 that should only ever be reachable on localhost "
                    "(127.0.0.1). Unexplained listeners are one of the plainest signs of a backdoor or an "
                    "already-compromised host.\n\n"
                    "`lsof -i` gives the same information framed around open files/sockets per process, useful when "
                    "you already suspect a specific process and want every network resource it holds. None of these "
                    "tools require exotic knowledge - they require exactly the vocabulary from this lesson (LISTEN "
                    "vs ESTABLISHED, bound address, owning process) to turn a wall of text into a five-second "
                    "verdict of 'normal' or 'investigate this.'"
                ),
            },
            {
                "h": "FROM SOCKETS TO THE APPLICATIONS THAT USE THEM",
                "body": (
                    "Everything in this lesson is the plumbing underneath every application-layer protocol in the "
                    "track: when ch-6 describes a browser sending an HTTP GET, what is actually happening is a "
                    "client socket, opened via `connect()` to the server's listening socket on port 443, carrying "
                    "bytes that only make sense once you know a webserver process was the one that called `bind()` "
                    "and `listen()` on that port in the first place. When ch-3's trace says 'TCP handshake to the "
                    "server's IP on port 443,' this lesson is what 'port 443' concretely means at the OS level on "
                    "both ends.\n\n"
                    "It is also, as the lesson's own hook says, exactly the model behind any client-server code you "
                    "write yourself: a server script that binds a port and loops calling `accept()`, and a client "
                    "script that calls `connect()` to that same IP and port. Once you have written or even just "
                    "traced through five lines of socket code, 'the client connects to the server' stops being an "
                    "abstract sentence and becomes something you can point at in both a terminal and a packet "
                    "capture simultaneously."
                ),
            },
        ],
    },
    "ch-6": {
        "title_check": "HTTP & TLS up close",
        "sections": [
            {
                "h": "MENTAL MODEL: TLS HIDES CONTENT, NOT EVERYTHING",
                "body": (
                    "The single most common misconception about HTTPS is that it hides the fact you visited a site "
                    "at all - it does not. The destination IP address is visible to anyone on the path (it has to "
                    "be, routers need it to deliver the packet, per ch-1). Historically, the SNI (Server Name "
                    "Indication) field - the hostname the client wants, e.g. example.com - was sent in PLAINTEXT "
                    "inside the very first TLS message, the ClientHello, specifically so a server hosting many "
                    "sites on one IP knows which certificate to present before encryption is even set up. Anyone "
                    "capturing that ClientHello can read the hostname directly, even though everything after the "
                    "handshake is encrypted. Encrypted Client Hello (ECH) is a newer extension designed to close "
                    "exactly this gap, but it is not yet universally deployed.\n\n"
                    "What TLS reliably hides is the request path, headers, and body - the actual content of what "
                    "you asked for and what you got back. What it never hides, even with ECH: the destination IP, "
                    "and coarse metadata like packet timing and sizes, which is enough for traffic-analysis "
                    "techniques to sometimes infer which page on a site you loaded even without reading a single "
                    "encrypted byte."
                ),
            },
            {
                "h": "TLS 1.3 HANDSHAKE, MESSAGE BY MESSAGE",
                "body": (
                    "TLS 1.3 (the current standard) does the whole handshake in one round trip, a real improvement "
                    "over TLS 1.2's two. The client sends a ClientHello containing the SNI, a list of supported "
                    "cipher suites, and - critically - a `key_share`: it optimistically sends its Diffie-Hellman "
                    "key material immediately instead of waiting to be asked, gambling that the server supports one "
                    "of its offered groups (almost always true in practice). The server replies with a ServerHello "
                    "(picks a cipher suite and sends its own key_share), and from this single exchange both sides "
                    "can independently derive the same symmetric session keys - this is where encryption actually "
                    "begins.\n\n"
                    "Everything after that first server flight is already encrypted with those freshly derived "
                    "keys: EncryptedExtensions, the server's Certificate, a CertificateVerify (a signature proving "
                    "the server holds the certificate's private key), and a Finished message (a MAC over the whole "
                    "handshake transcript, so any tampering is detected). The client sends its own Finished, and "
                    "application data (the actual HTTP request) can then flow - all told, 1 round trip before your "
                    "GET request goes out, versus TLS 1.2's 2 and versus the un-encrypted TCP-only exchange from "
                    "ch-2's 1."
                ),
            },
            {
                "h": "A REAL TLS HANDSHAKE, READ FIELD BY FIELD",
                "body": (
                    "Run `curl -v https://example.com` and the `-v` flag prints the handshake as it happens:\n\n"
                    "    * Trying 93.184.216.34:443...\n"
                    "    * Connected to example.com (93.184.216.34) port 443\n"
                    "    * ALPN: offering h2,http/1.1\n"
                    "    * TLSv1.3 (OUT), TLS handshake, Client hello (1):\n"
                    "    * TLSv1.3 (IN), TLS handshake, Server hello (2):\n"
                    "    * TLSv1.3 (IN), TLS handshake, Certificate (11):\n"
                    "    * SSL certificate verify ok.\n"
                    "    * using HTTP/2\n"
                    "    > GET / HTTP/2\n"
                    "    > Host: example.com\n"
                    "    < HTTP/2 200\n\n"
                    "In Wireshark, filtering the same capture with `tls.handshake.type==1` isolates just the "
                    "ClientHello, and expanding it shows the SNI field in the clear exactly as section 1 describes - "
                    "you can literally read the hostname in an unencrypted TLS packet, which is a genuinely useful "
                    "thing to have seen with your own eyes rather than taken on faith. ALPN (Application-Layer "
                    "Protocol Negotiation) in the ClientHello is how the client and server agree on HTTP/2 vs "
                    "HTTP/1.1 before any HTTP has actually been exchanged."
                ),
            },
            {
                "h": "WHERE HTTP AND TLS BREAK: DOWNGRADE AND MITM",
                "body": (
                    "A downgrade attack tricks a client into using a weaker, older protocol version where a known "
                    "flaw can be exploited (POODLE against SSLv3, for instance) - modern TLS libraries defend "
                    "against this with explicit downgrade-detection mechanisms baked into the handshake itself. A "
                    "certificate MITM works differently: if an attacker can get their own certificate trusted by "
                    "the victim (a compromised or rogue CA, a victim tricked into installing a malicious root "
                    "certificate - common in corporate SSL-inspection proxies and some malware), they can "
                    "transparently decrypt, read, and re-encrypt traffic in the middle, because trust in TLS "
                    "ultimately rests on trusting the certificate authorities your OS/browser ships with.\n\n"
                    "At the HTTP layer itself, header injection and request smuggling exploit ambiguity in how "
                    "different systems (a proxy vs. the origin server) parse the same request - for example "
                    "disagreeing about where a request body ends because of conflicting Content-Length and "
                    "Transfer-Encoding headers, letting an attacker sneak a second, hidden request into the stream "
                    "that the backend interprets differently than the proxy did. Both classes of attack share ch-1's "
                    "theme exactly: exploiting the gap between what one layer or one component assumes and what "
                    "another actually does."
                ),
            },
            {
                "h": "INVESTIGATING TLS AND HTTP LIKE AN ANALYST",
                "body": (
                    "`openssl s_client -connect example.com:443 -servername example.com` opens a raw TLS connection "
                    "and dumps the entire certificate chain, the negotiated protocol version and cipher suite, and "
                    "the certificate's validity dates - the first thing any analyst checks when a site 'looks "
                    "broken' in one browser but not another is often an expired or soon-to-expire certificate here. "
                    "`curl -vI https://host` (head request, verbose) is a faster daily-driver check for the same "
                    "basics without pulling a full response body.\n\n"
                    "On the HTTP side, response security headers are worth reading directly: HSTS "
                    "(Strict-Transport-Security) tells browsers 'never downgrade this site to plain HTTP again, "
                    "even if a user types http://', directly mitigating a class of downgrade/strip attacks; CSP "
                    "(Content-Security-Policy) restricts which sources a page may load scripts/resources from, "
                    "limiting the damage of an XSS bug even if one exists. A site missing both isn't automatically "
                    "broken, but their presence or absence is a fast, meaningful signal in any quick security review "
                    "of a web application."
                ),
            },
            {
                "h": "CLOSING THE LOOP: FROM BITS ON A WIRE TO A PAGE IN YOUR BROWSER",
                "body": (
                    "Trace the whole track backward from here: this lesson's HTTP request is the DATA that ch-1 "
                    "said gets wrapped in a TCP segment; that segment's ports are exactly what ch-5 explained as a "
                    "socket 4-tuple; the TCP connection carrying it was opened by exactly the handshake ch-2 "
                    "detailed, with real sequence numbers incrementing under the hood; the whole sequence of DNS, "
                    "ARP, TCP, TLS, HTTP is precisely ch-3's full trace, now with the TLS step given the depth it "
                    "deserves; and ch-4's Wireshark is the instrument that makes every one of those claims directly "
                    "verifiable rather than something you have to trust a diagram for.\n\n"
                    "The reason this track insists on this much depth in 'just' loading a web page is that this "
                    "exact chain - encapsulation, addressing, handshakes, encryption, and the application protocol "
                    "riding on top - is the shape of essentially every networked system you will ever analyze, "
                    "defend, or attack-model in a security career: same layers, same trust boundaries, same classes "
                    "of failure, just different application-layer content sitting on top of an otherwise identical "
                    "skeleton."
                ),
            },
        ],
    },
}
