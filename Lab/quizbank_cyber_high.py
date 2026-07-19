# quizbank_cyber_high.py - additional graded checks for the cyber_high track.
# Merged onto each lesson's existing quiz by content.build_courses().
# Answer indices balanced across the file so the correct option isn't always first.
EXTRA_QUIZ = {
    "ch-1": [
        {
            "q": "What is the correct name for the data unit at the transport layer when using TCP?",
            "code": "",
            "options": [
                "A segment",
                "A frame",
                "A packet",
                "A datagram"
            ],
            "answer": 0,
            "why": "TCP's protocol data unit is a segment; a frame is link-layer, a packet is network-layer, a datagram is UDP.",
            "detail": "Each layer names its PDU differently: link=frame, network(IP)=packet, transport TCP=segment, transport UDP=datagram, application=data. Calling a TCP unit a frame or packet confuses the layer it belongs to. UDP uses 'datagram', which is why the two transport protocols have different PDU names. Exam questions probe exactly this naming, because it reflects whether you understand which layer adds which header."
        },
        {
            "q": "A router and a switch operate at which layers, respectively?",
            "code": "",
            "options": [
                "Both at the application layer",
                "Router at the network (IP) layer, switch at the link (MAC) layer",
                "Router at link, switch at network",
                "Both at the transport layer"
            ],
            "answer": 1,
            "why": "Routers forward by IP address (network layer); switches forward by MAC address (link layer).",
            "detail": "A switch reads MAC addresses to move frames within a local network (link layer); a router reads IP addresses to forward packets between networks (network layer). Reversing them is a common mix-up. Neither works at the application or transport layer for forwarding. This is why a switch cannot route between subnets and a router is needed to cross networks — a distinction central to how the layers divide responsibility."
        },
        {
            "q": "In `HTTP over TCP over IP over Ethernet`, what is the physical order of headers on the wire (outermost first)?",
            "code": "",
            "options": [
                "HTTP, TCP, IP, then Ethernet",
                "IP, Ethernet, TCP, HTTP",
                "Ethernet, IP, TCP, then the HTTP data",
                "TCP, IP, Ethernet, HTTP"
            ],
            "answer": 2,
            "why": "Encapsulation wraps each layer inside the next, so the outermost (first on the wire) is the Ethernet frame header.",
            "detail": "The application data is wrapped by TCP, then IP, then Ethernet, so on the wire the Ethernet header comes first (outermost), then IP, then TCP, then the HTTP payload. Listing HTTP first describes the logical creation order, not the wire order. Each receiving layer strips its own header and hands the rest up. Getting the header order right is essential for reading a packet capture byte by byte."
        },
        {
            "q": "Why can you swap Wi-Fi for Ethernet without changing your web browser?",
            "code": "",
            "options": [
                "The browser detects the connection type and rewrites itself",
                "Wi-Fi and Ethernet use the same physical signals",
                "The IP layer is removed when using Wi-Fi",
                "Layering isolates each layer; the link layer changes but the layers above are unaffected"
            ],
            "answer": 3,
            "why": "Each layer only interacts with the ones directly adjacent, so replacing the link layer leaves upper layers untouched.",
            "detail": "The strict separation of concerns means the browser (application) and TCP/IP do not know or care whether the link layer is Wi-Fi or Ethernet — only the bottom layer differs. The browser does not rewrite itself, the two media use very different signaling, and IP is present either way. This modularity is the whole payoff of the layered model: you can change one layer's technology without touching the others."
        },
        {
            "q": "What does a MAC address identify, and what is its scope?",
            "code": "",
            "options": [
                "A network interface, meaningful only on the local link (not routed across the internet)",
                "A globally routable endpoint like an IP address",
                "A port number on a host",
                "A DNS name"
            ],
            "answer": 0,
            "why": "A MAC address names a network interface and is only used within the local network segment, not routed globally.",
            "detail": "MAC addresses operate at the link layer and are used to deliver frames between devices on the same local network; routers do not forward based on MAC across the internet — that is IP's job. A MAC is not a global endpoint, not a port (transport layer), and not a DNS name. This local scope is why a packet's source/destination MAC changes at every router hop while its source/destination IP stays the same end to end."
        },
        {
            "q": "This nesting of headers is called what, and what performs it going DOWN the stack?",
            "code": "[Eth [IP [TCP [HTTP data]]]]",
            "options": [
                "Fragmentation — splitting data into pieces",
                "Encapsulation — each layer wraps the layer above by prepending its own header",
                "Routing — choosing a path",
                "Multiplexing — sharing one channel"
            ],
            "answer": 1,
            "why": "Wrapping each layer's PDU inside the next lower layer's header is encapsulation; de-encapsulation reverses it on receipt.",
            "detail": "As data descends the stack, each layer prepends (encapsulates) its header, producing the nested structure shown; the receiver de-encapsulates layer by layer going up. Fragmentation is splitting an oversized packet (a different operation), routing is path selection, and multiplexing is sharing a link. Encapsulation is the fundamental mechanism the whole layered model rests on, and reading it is how you interpret a raw capture."
        }
    ],
    "ch-2": [
        {
            "q": "What are the three segments of the TCP three-way handshake, in order?",
            "code": "",
            "options": [
                "ACK, SYN, FIN",
                "SYN, ACK, SYN",
                "SYN, SYN-ACK, ACK",
                "HELLO, ACK, DONE"
            ],
            "answer": 2,
            "why": "The client sends SYN, the server replies SYN-ACK, the client confirms with ACK, establishing the connection.",
            "detail": "The handshake is SYN (client proposes, with an initial sequence number), SYN-ACK (server acknowledges and proposes its own sequence number), ACK (client acknowledges). This synchronizes sequence numbers both ways before data flows. FIN is for teardown, not setup, and 'HELLO/DONE' are not TCP flags. Recognizing the SYN/SYN-ACK/ACK pattern is how you spot a connection opening in a packet capture."
        },
        {
            "q": "Why is UDP a good fit for live video streaming or online games?",
            "code": "",
            "options": [
                "UDP guarantees every packet arrives in order",
                "UDP encrypts the data automatically",
                "UDP is the only protocol firewalls allow",
                "Low latency matters more than reliability; UDP skips retransmission and ordering overhead"
            ],
            "answer": 3,
            "why": "UDP trades reliability for speed; for real-time media a late retransmitted packet is useless, so dropping it is better.",
            "detail": "Real-time applications prefer UDP because retransmitting a lost video frame would arrive too late to matter — better to skip it and keep latency low. UDP explicitly does NOT guarantee delivery or ordering (that is TCP), does not encrypt anything (that is TLS/DTLS on top), and firewalls handle both protocols. Choosing UDP is a deliberate latency-over-reliability tradeoff, the opposite of TCP's guarantees."
        },
        {
            "q": "A packet capture shows SYN then SYN-ACK but the final ACK never comes. What does this indicate?",
            "code": "",
            "options": [
                "A half-open connection — possibly a SYN scan or a dropped/blocked client",
                "A completed, healthy connection",
                "Normal connection teardown",
                "A DNS lookup in progress"
            ],
            "answer": 0,
            "why": "SYN and SYN-ACK without the final ACK leaves the connection half-open, a signature of SYN scanning or a network problem.",
            "detail": "The handshake is incomplete without the third ACK, so the connection is half-open. This pattern is characteristic of a SYN (half-open) port scan, where the scanner never completes the handshake, or of a client that was blocked or dropped. It is not a healthy connection (that needs all three), not teardown (which uses FIN/RST), and not DNS. Recognizing incomplete handshakes is a core skill in both network troubleshooting and intrusion detection."
        },
        {
            "q": "What does the TCP sequence number accomplish that UDP has no equivalent for?",
            "code": "",
            "options": [
                "Encrypting the payload",
                "Ordering bytes and detecting loss so data can be reassembled correctly and retransmitted",
                "Choosing the destination port",
                "Compressing the data"
            ],
            "answer": 1,
            "why": "Sequence numbers let TCP order received segments and detect missing ones for retransmission; UDP has none of this.",
            "detail": "TCP's sequence numbers track the byte position of each segment, enabling in-order reassembly and detection of gaps that trigger retransmission — the machinery of reliability. UDP omits them entirely, which is why it is unreliable and unordered. Sequence numbers do not encrypt, select ports (that is the port fields), or compress. This reliability machinery is exactly the overhead UDP skips for speed."
        },
        {
            "q": "How does a TCP connection normally close?",
            "code": "",
            "options": [
                "A single SYN packet",
                "The connection just times out with no signaling",
                "A FIN/ACK exchange in each direction (a four-way teardown)",
                "An ICMP echo"
            ],
            "answer": 2,
            "why": "Graceful close uses FIN and ACK in both directions, since each side must independently signal it is done sending.",
            "detail": "TCP closes with a FIN from each side, each acknowledged, because the connection is full-duplex and each direction is torn down separately (often seen as FIN, ACK, FIN, ACK). SYN is for opening, not closing. A pure timeout with no signaling is abnormal (it happens on crashes), and ICMP echo is ping, unrelated. An RST can also abruptly abort a connection, distinct from the graceful FIN teardown."
        },
        {
            "q": "What is printed as the transport for a DNS query in a typical capture, and why?",
            "code": "",
            "options": [
                "TCP — DNS always uses a three-way handshake",
                "ICMP — DNS is a control protocol",
                "ARP — DNS resolves at the link layer",
                "UDP — DNS queries are small and fit one datagram, favoring speed over connection setup"
            ],
            "answer": 3,
            "why": "DNS normally uses UDP for its small, fast single-message queries, falling back to TCP only for large responses.",
            "detail": "A standard DNS lookup is a small request and reply that fit in one UDP datagram, so it avoids TCP's handshake overhead. DNS DOES use TCP for large responses (like zone transfers or big DNSSEC records), but the common case is UDP. It is not ICMP (a control/diagnostic protocol) or ARP (link-layer address resolution). Knowing DNS is usually UDP helps you filter and interpret it quickly in a capture."
        }
    ],
    "ch-3": [
        {
            "q": "What is the FIRST thing your computer must do to load http://example.com if the name is not cached?",
            "code": "",
            "options": [
                "Resolve the name to an IP via DNS",
                "Open a TCP connection to example.com",
                "Send the HTTP GET request",
                "Perform the TLS handshake"
            ],
            "answer": 0,
            "why": "You need the server's IP before you can connect, so DNS resolution comes first.",
            "detail": "You cannot open a TCP connection without an IP address, and the URL only gives a name, so DNS resolution is the first step. The TCP handshake, TLS handshake, and HTTP request all require knowing the IP first, so they come later in the sequence. This ordering — DNS, then TCP, then (for HTTPS) TLS, then HTTP — is the backbone of what happens when you load any web page."
        },
        {
            "q": "What does NAT do to a packet leaving your home network?",
            "code": "",
            "options": [
                "Encrypts the entire packet",
                "Rewrites the private source IP (and port) to the router's public IP so replies can return",
                "Changes the destination IP to a DNS server",
                "Adds a TLS certificate"
            ],
            "answer": 1,
            "why": "NAT translates the internal private address to the router's public address (and tracks the port) so return traffic maps back.",
            "detail": "Network Address Translation rewrites the source IP from a private address (like 192.168.x.x) to the router's single public IP, recording the port mapping so replies can be sent back to the right internal device. It does not encrypt, does not change the destination to a DNS server, and adds no certificate. NAT is why many devices share one public IP, and why a captured packet's source IP differs inside versus outside your network."
        },
        {
            "q": "Put these in the order they occur when loading an HTTPS page: (1) HTTP GET (2) TCP handshake (3) DNS lookup (4) TLS handshake.",
            "code": "",
            "options": [
                "1, 2, 3, 4",
                "2, 3, 4, 1",
                "3, 2, 4, 1",
                "3, 4, 2, 1"
            ],
            "answer": 2,
            "why": "DNS resolves the name, TCP connects, TLS secures the channel, then the HTTP request is sent over it.",
            "detail": "The correct sequence is DNS (get the IP), TCP handshake (establish the connection), TLS handshake (negotiate encryption), then the HTTP GET over the now-secure channel. Starting with the GET (option b) is impossible — there is no connection yet. TLS must come after TCP because it runs on top of the connection. This full trace is exactly what you would see, in order, in a packet capture of a page load."
        },
        {
            "q": "After DNS returns an IP, your browser reuses it moments later without another lookup. Why?",
            "code": "",
            "options": [
                "DNS results are never cached",
                "The IP is hard-coded in the browser",
                "TCP stores the IP for reuse",
                "The result is cached (in the OS/browser) for its TTL, avoiding repeat queries"
            ],
            "answer": 3,
            "why": "DNS responses carry a TTL and are cached by the resolver, OS, and browser, so repeat lookups are avoided until it expires.",
            "detail": "Each DNS record has a Time To Live telling caches how long to keep it; within that window the cached IP is reused with no new query. Results are definitely cached (that is core to DNS scaling), not hard-coded, and TCP does not store DNS data. This caching is why a changed DNS record takes time to propagate, and why flushing the DNS cache is a troubleshooting step when a site moves."
        },
        {
            "q": "Your machine has IP 192.168.1.50 but a website sees your traffic as coming from 203.0.113.7. What explains the difference?",
            "code": "",
            "options": [
                "NAT at your router translated the private IP to its public IP",
                "The website is misconfigured",
                "DNS changed your address",
                "TLS rewrote the source IP"
            ],
            "answer": 0,
            "why": "The private 192.168.x.x address is NAT-translated to the router's public address before packets reach the internet.",
            "detail": "192.168.1.50 is a private address that is not routable on the internet, so your router's NAT rewrites the source to its public IP (203.0.113.7) on the way out. The website is not misconfigured — it simply sees the public address. DNS resolves names to IPs (it does not change your source), and TLS encrypts payload without touching the IP header. This is the everyday reason your 'local IP' and 'public IP' differ."
        },
        {
            "q": "Which service translated 'example.com' into an IP address during the page load?",
            "code": "",
            "options": [
                "DHCP",
                "DNS (the Domain Name System)",
                "ARP",
                "NAT"
            ],
            "answer": 1,
            "why": "DNS maps human-readable names to IP addresses; DHCP assigns local addresses, ARP maps IP to MAC, NAT translates public/private IPs.",
            "detail": "Name-to-IP translation is DNS's specific job. DHCP hands out IP addresses to devices joining a network, ARP resolves an IP to a MAC address on the local link, and NAT swaps between private and public IPs — each solves a different translation problem. Confusing these four services is common; pinning DNS as the name resolver is fundamental to understanding how a URL becomes a connection."
        }
    ],
    "ch-4": [
        {
            "q": "In Wireshark, what does the display filter `tcp.port == 443` show?",
            "code": "tcp.port == 443",
            "options": [
                "All packets on the network",
                "Only UDP packets",
                "Only TCP packets with source or destination port 443 (typically HTTPS)",
                "Only packets containing the text 443"
            ],
            "answer": 2,
            "why": "The filter matches TCP packets whose source OR destination port is 443, the standard HTTPS port.",
            "detail": "`tcp.port == 443` narrows the view to TCP traffic on port 443 in either direction — usually HTTPS. It does not show all packets (that is no filter), not UDP (the filter says tcp), and not a text search (that would be `frame contains \"443\"`). Display filters operate on protocol FIELDS, not raw text, which is what makes Wireshark precise. Mastering filters like this is how you isolate the conversation you care about in a busy capture."
        },
        {
            "q": "You want to see only DNS traffic. Which display filter is correct?",
            "code": "",
            "options": [
                "port dns",
                "protocol == DNS",
                "filter: dns only",
                "dns"
            ],
            "answer": 3,
            "why": "Wireshark's protocol filters use the protocol name directly, so `dns` shows all DNS packets.",
            "detail": "Typing the protocol name — `dns`, `http`, `tcp`, `arp` — is the filter syntax; Wireshark understands the protocol and shows matching packets. `port dns`, `protocol == DNS`, and `filter: dns only` are not valid Wireshark filter syntax (that is a mix of tcpdump-isms and invented phrasing). Knowing the difference between Wireshark's display-filter syntax and tcpdump's capture-filter syntax prevents a lot of frustration."
        },
        {
            "q": "A TCP handshake in a Wireshark capture appears as which sequence of packets?",
            "code": "",
            "options": [
                "[SYN] then [SYN, ACK] then [ACK]",
                "[GET] then [200 OK]",
                "[FIN] then [FIN, ACK]",
                "A single [PSH] packet"
            ],
            "answer": 0,
            "why": "The three-way handshake shows as SYN, SYN-ACK, ACK — the flag combinations Wireshark labels in the Info column.",
            "detail": "Wireshark labels the handshake packets by their flags: [SYN], [SYN, ACK], [ACK]. GET/200 OK is the HTTP exchange that happens AFTER the connection is up. FIN/FIN-ACK is teardown, not setup. A single PSH is a data push mid-connection. Spotting the SYN/SYN-ACK/ACK trio is how you find where each connection begins in a capture, a routine analysis step."
        },
        {
            "q": "What does the filter `ip.addr == 10.0.0.5` match?",
            "code": "ip.addr == 10.0.0.5",
            "options": [
                "Only packets FROM 10.0.0.5",
                "Packets where 10.0.0.5 is either the source OR the destination",
                "Only packets TO 10.0.0.5",
                "Packets that never involve 10.0.0.5"
            ],
            "answer": 1,
            "why": "ip.addr matches the address in either direction; ip.src or ip.dst would restrict it to source or destination only.",
            "detail": "`ip.addr ==` is bidirectional, matching whether the host is the sender or receiver — ideal for seeing everything a host is involved in. To restrict direction you use `ip.src ==` or `ip.dst ==`. It is not an exclusion filter (that would use `!=`). This source-OR-destination behavior is a subtle but important detail: forgetting it makes people think a filter is broken when it is showing both directions as intended."
        },
        {
            "q": "Why can you see the destination IP and port of an HTTPS connection in Wireshark, but not the URL path or page content?",
            "code": "",
            "options": [
                "Wireshark cannot read any HTTPS traffic at all",
                "The URL is sent in plaintext but the IP is encrypted",
                "TLS encrypts the HTTP payload, but IP/TCP headers (addresses, ports) are outside the encryption",
                "HTTPS uses no IP headers"
            ],
            "answer": 2,
            "why": "TLS encrypts the application data, leaving the lower-layer IP and TCP headers (addresses, ports) visible for routing.",
            "detail": "Encryption protects the HTTP content (path, headers, body), but the IP and TCP headers must stay in the clear so routers can deliver the packets — so you always see the endpoints and ports, just not the payload. Wireshark can absolutely see HTTPS metadata (option b is wrong), the URL path is encrypted not plaintext (option c reverses it), and HTTPS certainly uses IP. This is why metadata analysis works even against encrypted traffic — a key concept for both privacy and network forensics."
        },
        {
            "q": "What does the capture filter (as opposed to display filter) `tcp port 80` do differently?",
            "code": "",
            "options": [
                "It is identical to a display filter",
                "It colors matching packets",
                "It exports packets to a file",
                "It decides which packets are RECORDED, discarding the rest before capture"
            ],
            "answer": 3,
            "why": "Capture filters limit what is saved during capture; display filters only hide/show among already-captured packets.",
            "detail": "A capture filter (BPF syntax like `tcp port 80`) is applied while capturing, so non-matching packets are never recorded — you cannot get them back. A display filter operates on an existing capture, hiding but not deleting. They are NOT identical, use different syntax, and neither colors (that is coloring rules) nor exports. Choosing a capture filter up front reduces file size and noise; a display filter lets you explore what you already have."
        }
    ],
    "ch-5": [
        {
            "q": "An IP address gets you to the machine; what does the port number identify?",
            "code": "",
            "options": [
                "The specific application/service on that machine",
                "The physical network cable",
                "The DNS server",
                "The MAC address"
            ],
            "answer": 0,
            "why": "A port distinguishes among the many services on one host, so traffic reaches the right application.",
            "detail": "One machine runs many services (web on 443, SSH on 22, mail on 25); the port number selects which one a packet is for. It has nothing to do with the physical cable, the DNS server, or the MAC address. The IP+port pair together form a socket endpoint, which is how the OS routes an incoming segment to the correct listening program among all those sharing the same IP."
        },
        {
            "q": "In the client-server model, which side calls bind() and listen() on a port?",
            "code": "",
            "options": [
                "The client — it binds to the server's port",
                "The server — it binds to a known port and waits for connections",
                "Both bind to the same port simultaneously",
                "Neither; ports are assigned by DNS"
            ],
            "answer": 1,
            "why": "The server binds and listens on a well-known port; the client connects to that port from an ephemeral local port.",
            "detail": "The server publishes a service by binding to a fixed port and listening; the client initiates a connection to that port, using an OS-assigned ephemeral port on its own side. The client does not bind the server's port, they do not both bind the same port, and DNS assigns names to IPs, not ports. This asymmetry — server listens, client connects — is the foundation of the socket API and of how services are reached."
        },
        {
            "q": "A host is listening on TCP port 22. Which service is it most likely running?",
            "code": "",
            "options": [
                "HTTP",
                "DNS",
                "SSH",
                "SMTP"
            ],
            "answer": 2,
            "why": "Port 22 is the well-known port for SSH; HTTP is 80, DNS is 53, SMTP is 25.",
            "detail": "The well-known port assignments are worth memorizing: 22=SSH, 80=HTTP, 443=HTTPS, 53=DNS, 25=SMTP, 21=FTP, 3389=RDP. A service on 22 is almost certainly SSH. Knowing these lets you interpret a port scan or a `netstat` listing instantly — an open port 22 signals remote shell access, which matters for both administration and security assessment. (A service COULD run on a non-standard port, but the convention holds broadly.)"
        },
        {
            "q": "What does this server code do?",
            "code": "s = socket(AF_INET, SOCK_STREAM)\ns.bind(('0.0.0.0', 8080))\ns.listen()\nconn, addr = s.accept()",
            "options": [
                "Connects as a client to port 8080",
                "Creates a UDP server",
                "Sends an HTTP request",
                "Creates a TCP server listening on port 8080 on all interfaces, waiting to accept a client"
            ],
            "answer": 3,
            "why": "SOCK_STREAM is TCP, bind('0.0.0.0',8080) listens on all interfaces, and accept() blocks for an incoming client.",
            "detail": "This is the canonical TCP server: SOCK_STREAM selects TCP, binding to 0.0.0.0 means 'all local interfaces' on port 8080, listen() marks it passive, and accept() waits for and returns a client connection. It is a server not a client (bind/listen/accept, not connect), TCP not UDP (SOCK_STREAM, not SOCK_DGRAM), and does not send HTTP. Recognizing the bind/listen/accept trio identifies server code at a glance."
        },
        {
            "q": "Why can a client use an 'ephemeral' port instead of a fixed one?",
            "code": "",
            "options": [
                "The client only needs a temporary port to receive the reply; the OS assigns a free high-numbered one",
                "Clients must always use port 80",
                "Ephemeral ports are more secure by design",
                "The server chooses the client's port"
            ],
            "answer": 0,
            "why": "The client's port just needs to be unique locally so replies map back to it; the OS picks any free high port temporarily.",
            "detail": "Only the server needs a predictable port (so clients can find it); the client's port merely has to identify its side of the connection for return traffic, so the OS grabs a free ephemeral port (typically 49152+) for the connection's lifetime. Clients do not use 80 (that is a server port), ephemeral ports are not inherently more secure, and the server does not assign them. This is why the same client can open many connections, each on a different ephemeral port."
        },
        {
            "q": "What uniquely identifies a single TCP connection on a machine?",
            "code": "",
            "options": [
                "Just the destination port",
                "The 4-tuple: source IP, source port, destination IP, destination port",
                "Only the source IP",
                "The MAC addresses"
            ],
            "answer": 1,
            "why": "A TCP connection is identified by the full four-tuple of both endpoints' IP and port, which is why one server port serves many clients.",
            "detail": "The combination of source IP, source port, destination IP, and destination port uniquely names a connection, so a server on a single port (443) can serve thousands of clients simultaneously — each connection differs in the client's IP and/or ephemeral port. Just the destination port or source IP alone cannot distinguish concurrent connections, and MAC addresses are link-layer and change per hop. This four-tuple is how the OS demultiplexes incoming segments to the right socket."
        }
    ],
    "ch-6": [
        {
            "q": "What does an HTTP 301 status code mean?",
            "code": "",
            "options": [
                "Not Found",
                "Server Error",
                "Moved Permanently — the resource is now at a different URL, given in the Location header",
                "OK"
            ],
            "answer": 2,
            "why": "3xx codes are redirections; 301 specifically means the resource moved permanently to a new URL.",
            "detail": "The status classes are: 2xx success (200 OK), 3xx redirection (301 permanent, 302 temporary), 4xx client error (404 Not Found, 403 Forbidden), 5xx server error (500, 503). A 301 tells the browser to use the new URL from now on, updating bookmarks and caches. Knowing the classes lets you diagnose web issues instantly — a 4xx is your side, a 5xx is the server's — which is why the first digit is the most important."
        },
        {
            "q": "TLS provides three main guarantees. Which set is correct?",
            "code": "",
            "options": [
                "Speed, compression, and caching",
                "Only encryption, nothing else",
                "Anonymity and untraceability",
                "Confidentiality (encryption), integrity (tamper detection), and authentication (server identity)"
            ],
            "answer": 3,
            "why": "TLS encrypts the data, detects tampering, and authenticates the server via its certificate — confidentiality, integrity, authentication.",
            "detail": "TLS gives confidentiality (eavesdroppers cannot read the content), integrity (modifications are detected), and authentication (the certificate proves you are talking to the real server, preventing impersonation). It is not about speed/compression/caching, is more than just encryption (authentication is crucial), and does NOT provide anonymity — the server still sees your IP, and observers still see which server you contacted. Understanding all three guarantees explains why HTTPS matters beyond 'it's encrypted'."
        },
        {
            "q": "During a TLS 1.3 handshake to https://bank.com, what can a network eavesdropper still observe?",
            "code": "",
            "options": [
                "The destination IP and, often, the server name (SNI) — but not the HTTP content",
                "The full URL and page content",
                "Your password in plaintext",
                "Absolutely nothing about the connection"
            ],
            "answer": 0,
            "why": "The IP is always visible, and the SNI (server name) is typically sent in the clear, but the encrypted application data is not.",
            "detail": "An eavesdropper sees the destination IP (needed for routing) and usually the SNI field naming which site you are reaching, but not the URL path, headers, or body once TLS is established. They do NOT see the full URL/content or your password (those are encrypted), and 'nothing at all' is wrong because metadata leaks. Encrypted SNI/ECH aims to hide even the server name. This metadata-versus-content distinction is central to understanding what HTTPS does and does not protect."
        },
        {
            "q": "A request returns HTTP 503. Whose problem is it, most likely?",
            "code": "",
            "options": [
                "The client's request was malformed",
                "The server's — 503 Service Unavailable means it is overloaded or down for maintenance",
                "The URL does not exist",
                "Authentication failed"
            ],
            "answer": 1,
            "why": "5xx codes indicate server-side failures; 503 specifically means the server is temporarily unable to handle the request.",
            "detail": "503 is a 5xx (server error) meaning the service is temporarily unavailable — overloaded, restarting, or in maintenance — so retrying later may work. A malformed request would be 400 (client error), a missing URL is 404, and failed auth is 401/403 — all 4xx client-side. The first digit tells you where to look: 4xx means fix your request, 5xx means the server is at fault. This triage is the practical value of status codes."
        },
        {
            "q": "Why does a valid TLS certificate require a trusted Certificate Authority (CA)?",
            "code": "",
            "options": [
                "The CA encrypts all your traffic",
                "The CA stores your password",
                "The CA vouches that the public key really belongs to that domain, preventing impersonation",
                "The CA speeds up the connection"
            ],
            "answer": 2,
            "why": "A CA's signature binds a public key to a domain name so clients can trust they are talking to the genuine server, not an impostor.",
            "detail": "Without a trusted third party attesting that a public key belongs to bank.com, an attacker could present their own key and impersonate the site. The CA signs the certificate, and browsers trust a set of CAs, so a valid chain proves identity. The CA does not encrypt your traffic (TLS does, using the certified key), does not store your password, and does not affect speed. This chain of trust is what stops man-in-the-middle attacks, the authentication pillar of TLS."
        },
        {
            "q": "What does this HTTP request line indicate?",
            "code": "GET /api/users?id=42 HTTP/1.1\nHost: example.com",
            "options": [
                "A POST submitting id=42 in the body",
                "A response with status 42",
                "An encrypted TLS record",
                "A GET request for /api/users with query parameter id=42, using HTTP/1.1, to host example.com"
            ],
            "answer": 3,
            "why": "The method is GET, the path is /api/users with a query string id=42, the version is HTTP/1.1, and Host names the site.",
            "detail": "This is a request (method GET, path, version) with the query parameter id=42 in the URL and a Host header (required in HTTP/1.1 so one server can host many sites). It is not a POST (which puts data in the body, not the URL), not a response (those start with a status line like 'HTTP/1.1 200 OK'), and not a TLS record (this is plaintext HTTP). Reading a raw HTTP request — method, path, query, headers — is fundamental to web work and to analyzing captured traffic."
        }
    ]
}
