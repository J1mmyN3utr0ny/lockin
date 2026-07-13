// lessons_content.js — the rich, visual Learning hub (web app). Long lessons with hand-authored SVG
// diagrams, CSS animations (the "gifs"), curated video links and interactive quizzes. This is the
// theory half of the split: read & understand here, build & run in the Lab. Add lessons as data.
//
// Section types: text {h, body(html)} · svg {caption, svg} · anim {caption, html} ·
//                callout {icon, title, body(html)} · video {title, url, by, note}
// Colours use the app's CSS variables so the diagrams stay theme-correct.

export const lessonTracks = [
  { id: "net", name: "Networking", icon: "🌐", blurb: "How data actually crosses the internet — the most-tested cyber topic." },
];

// --- reusable SVG helpers (as strings, inlined into the DOM) -----------------------------------
const layersSVG = `
<svg viewBox="0 0 340 260" role="img" aria-label="TCP/IP layer stack" style="width:100%;height:auto">
  <defs>
    <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#4f8cff"/><stop offset="1" stop-color="#22d3ee"/>
    </linearGradient>
  </defs>
  ${[["Application","HTTP · DNS · SSH · TLS","what the program speaks",0],
     ["Transport","TCP · UDP (ports)","program → program",1],
     ["Internet","IP · ICMP · ARP","host → host, across networks",2],
     ["Link","Ethernet · Wi-Fi (MAC)","the actual wire/radio",3]].map(([n,p,s,i]) => `
    <g transform="translate(20 ${16 + i*58})">
      <rect width="300" height="46" rx="10" fill="url(#lg)" opacity="${1 - i*0.14}"/>
      <text x="14" y="20" fill="#0b0f17" font-size="14" font-weight="700">${n}</text>
      <text x="14" y="37" fill="#0b0f17" font-size="10.5" opacity=".85">${p}</text>
      <text x="286" y="28" fill="#0b0f17" font-size="9.5" text-anchor="end" opacity=".8">${s}</text>
    </g>`).join("")}
  <text x="170" y="252" fill="var(--muted)" font-size="10" text-anchor="middle">data travels DOWN to send, UP to receive ↑↓</text>
</svg>`;

const encapSVG = `
<svg viewBox="0 0 360 150" role="img" aria-label="Encapsulation: each layer wraps the one above" style="width:100%;height:auto">
  ${[["Eth","#334155",0,360],["IP","#3b5bab",26,308],["TCP","#2f6bff",52,256],["HTTP data","#22d3ee",78,204]].map(
    ([n,c,x,w]) => `<g><rect x="${x}" y="30" width="${w}" height="70" rx="6" fill="${c}"/>
      <text x="${x+8}" y="52" fill="#e8edf6" font-size="11" font-weight="700">${n}</text></g>`).join("")}
  <text x="180" y="120" fill="var(--muted)" font-size="10.5" text-anchor="middle">Each layer adds its own header — like envelopes inside envelopes.</text>
  <text x="180" y="136" fill="var(--dim)" font-size="9.5" text-anchor="middle">The receiver peels them off in reverse.</text>
</svg>`;

const tcpUdpSVG = `
<svg viewBox="0 0 360 170" role="img" aria-label="TCP vs UDP" style="width:100%;height:auto">
  <g>
    <rect x="10" y="10" width="160" height="150" rx="12" fill="none" stroke="var(--good)" stroke-width="1.5"/>
    <text x="90" y="34" fill="var(--good)" font-size="14" font-weight="800" text-anchor="middle">TCP</text>
    <text x="90" y="54" fill="var(--fg)" font-size="10.5" text-anchor="middle">reliable · ordered</text>
    <text x="90" y="72" fill="var(--fg)" font-size="10.5" text-anchor="middle">connection first</text>
    <text x="90" y="96" fill="var(--muted)" font-size="10" text-anchor="middle">📞 a phone call</text>
    <text x="90" y="122" fill="var(--dim)" font-size="9.5" text-anchor="middle">web · SSH · chat</text>
    <text x="90" y="140" fill="var(--dim)" font-size="9.5" text-anchor="middle">handshake · acks · resends</text>
  </g>
  <g>
    <rect x="190" y="10" width="160" height="150" rx="12" fill="none" stroke="var(--warn)" stroke-width="1.5"/>
    <text x="270" y="34" fill="var(--warn)" font-size="14" font-weight="800" text-anchor="middle">UDP</text>
    <text x="270" y="54" fill="var(--fg)" font-size="10.5" text-anchor="middle">fast · no guarantees</text>
    <text x="270" y="72" fill="var(--fg)" font-size="10.5" text-anchor="middle">just send it</text>
    <text x="270" y="96" fill="var(--muted)" font-size="10" text-anchor="middle">📮 a postcard</text>
    <text x="270" y="122" fill="var(--dim)" font-size="9.5" text-anchor="middle">DNS · video · games</text>
    <text x="270" y="140" fill="var(--dim)" font-size="9.5" text-anchor="middle">fire and forget</text>
  </g>
</svg>`;

// The "gif": a looping CSS animation of the 3-way handshake.
const handshakeAnim = `
<div class="hs">
  <div class="hs-col"><div class="hs-node">Client</div><div class="hs-line"></div></div>
  <div class="hs-col"><div class="hs-node">Server</div><div class="hs-line"></div></div>
  <div class="hs-pkt p1">SYN →</div>
  <div class="hs-pkt p2">← SYN-ACK</div>
  <div class="hs-pkt p3">ACK →</div>
  <div class="hs-pkt p4">✓ connected</div>
</div>`;

const traceSVG = `
<svg viewBox="0 0 340 300" role="img" aria-label="What happens when you load a web page" style="width:100%;height:auto">
  ${[["1","DNS","example.com → 93.184.216.34","var(--acc2)"],
     ["2","ARP","find the gateway's MAC address","var(--violet)"],
     ["3","TCP","3-way handshake to port 443","var(--accent)"],
     ["4","TLS","agree keys, turn on encryption","var(--good)"],
     ["5","HTTP","GET /  →  200 OK + the page","var(--gold)"]].map(([n,t,d,c],i) => `
    <g transform="translate(20 ${14 + i*56})">
      <circle cx="18" cy="20" r="16" fill="${c}"/>
      <text x="18" y="25" fill="#0b0f17" font-size="15" font-weight="800" text-anchor="middle">${n}</text>
      <rect x="46" y="2" width="254" height="38" rx="8" fill="var(--card-2)" stroke="var(--line)"/>
      <text x="58" y="19" fill="var(--fg)" font-size="12.5" font-weight="700">${t}</text>
      <text x="58" y="33" fill="var(--muted)" font-size="10">${d}</text>
      ${i<4?`<line x1="18" y1="38" x2="18" y2="54" stroke="var(--line)" stroke-width="2"/>`:""}
    </g>`).join("")}
</svg>`;

export const lessons = [
  {
    id: "net-layers", track: "net", title: "The Layers — how the internet is built", minutes: 15,
    summary: "Every 'how does the internet work?' answer is the same word: layers. Learn to place any protocol on its floor.",
    sections: [
      { type: "text", h: "Why the internet is built in layers",
        body: `The internet moves data between billions of devices that use different hardware, run different software, and sit on different networks. No single program could handle all of that. So engineers split the job into <b>layers</b>, where each layer solves exactly one problem and trusts the layer below it to handle the rest.<br><br>Think of sending a physical letter. <b>You</b> write the message (you don't care how trucks work). The <b>post office</b> routes it (it doesn't care what the letter says). The <b>truck driver</b> drives the roads (they don't care which post office). Each level does one job and hands off to the next. Networking works exactly like that.` },
      { type: "svg", caption: "The TCP/IP model — four layers, each with one job.", svg: layersSVG },
      { type: "text", h: "The four layers, top to bottom",
        body: `<ul>
          <li><b>Application</b> — what your program actually speaks: <code>HTTP</code> for web pages, <code>DNS</code> for names, <code>SSH</code> for remote shells. This is the only layer most developers touch directly.</li>
          <li><b>Transport</b> — gets data from <i>one program to another program</i> using <b>port numbers</b>. <code>TCP</code> (reliable) and <code>UDP</code> (fast) live here.</li>
          <li><b>Internet</b> — gets a packet from <i>one host to another host</i>, possibly across the whole planet, using <b>IP addresses</b> and routing.</li>
          <li><b>Link</b> — the actual wire or radio: Ethernet and Wi-Fi, using <b>MAC addresses</b> to reach the next device on the local network.</li>
        </ul>` },
      { type: "callout", icon: "🎁", title: "Encapsulation — the key idea",
        body: `To <b>send</b>, your data travels <i>down</i> the stack and each layer wraps it in its own header. To <b>receive</b>, it travels <i>up</i> and each layer peels its header off. Your HTTP request literally becomes a TCP segment inside an IP packet inside an Ethernet frame.` },
      { type: "svg", caption: "Encapsulation: envelopes inside envelopes.", svg: encapSVG },
      { type: "text", h: "The one skill this gives you",
        body: `Interviewers and the GAMA exam love to ask you to <b>place a protocol on its layer</b>. Once the model is in your head it's automatic:<br><br>
          <code>MAC / ARP</code> → Link · <code>IP / ICMP</code> → Internet · <code>TCP / UDP / ports</code> → Transport · <code>HTTP / DNS / SSH</code> → Application.<br><br>
          If you can answer "which layer, and what's its job?" for any term, you understand networking better than most people who've been doing it for years.` },
      { type: "video", title: "The OSI & TCP/IP models, explained visually", url: "https://www.youtube.com/results?search_query=osi+model+explained+animated", by: "YouTube", note: "8 min · pick any animated one" },
    ],
    quiz: [
      { q: "Which layer uses PORT numbers to reach the right program?", options: ["Link", "Internet", "Transport", "Application"], answer: 2, why: "Ports live at the Transport layer (TCP/UDP) — IP finds the host, the port finds the program." },
      { q: "You see the term ARP. Which layer is it?", options: ["Link", "Transport", "Application", "Internet"], answer: 0, why: "ARP maps IP→MAC to reach the next device on the local network — that's the Link layer's job." },
      { q: "What does 'encapsulation' mean here?", options: ["Encrypting the data", "Each layer wraps the layer above in its own header", "Compressing packets", "Splitting a file into parts"], answer: 1, why: "Going down the stack, each layer adds a header around the higher layer's data — envelopes inside envelopes." },
      { q: "HTTP, DNS and SSH all live on which layer?", options: ["Transport", "Application", "Internet", "Link"], answer: 1, why: "They're what programs speak — the Application layer." },
    ],
  },
  {
    id: "net-tcp-udp", track: "net", title: "TCP vs UDP & the 3-way handshake", minutes: 16,
    summary: "SYN, SYN-ACK, ACK — three packets that begin every web page, download and chat. The most-asked networking detail there is.",
    sections: [
      { type: "text", h: "Two ways to send data",
        body: `The Transport layer offers two very different tools, and knowing which is which (and why) is one of the most common networking questions you'll ever get.<br><br>
          <b>TCP</b> is like a <b>phone call</b>: you both agree to connect, then everything you say arrives <i>in order</i> and <i>complete</i> — if a word is lost, it's automatically repeated. <b>UDP</b> is like a <b>postcard</b>: you just write it and drop it in the box. It's faster and simpler, but nothing guarantees it arrives, or in order.` },
      { type: "svg", caption: "Same job (program → program), opposite trade-offs.", svg: tcpUdpSVG },
      { type: "text", h: "The 3-way handshake",
        body: `Before TCP sends a single byte of your data, the two sides shake hands to agree they're both ready and to sync their sequence numbers:<br><br>
          <ol>
            <li><b>Client → SYN</b> — "I want to talk. My sequence number starts at X."</li>
            <li><b>Server → SYN-ACK</b> — "Got it (I acknowledge X). I'm ready too — my number starts at Y."</li>
            <li><b>Client → ACK</b> — "Great, I acknowledge Y. Let's go."</li>
          </ol>
          After these three packets the connection is <b>established</b> and real data flows. This is <i>the</i> detail interviewers reach for.` },
      { type: "anim", caption: "The 3-way handshake, in motion (loops).", html: handshakeAnim },
      { type: "callout", icon: "🔢", title: "Why sequence numbers matter",
        body: `Those starting numbers let TCP <b>reorder</b> packets that arrive out of order and <b>detect</b> ones that went missing (a gap in the numbers) so it can resend them. That's the machinery behind "reliable and ordered."` },
      { type: "text", h: "When to use which",
        body: `<ul>
          <li><b>TCP</b>: web (HTTP/S), SSH, email, file downloads, chat — anywhere a missing or out-of-order byte would break things.</li>
          <li><b>UDP</b>: DNS lookups, live video/voice, and online games — where speed matters more than perfection and a dropped frame is better than a laggy one.</li>
        </ul>
        A dropped pixel in a video call vanishes in a fraction of a second; waiting to resend it would just add lag. That's why the trade-off exists.` },
      { type: "video", title: "The TCP 3-way handshake, step by step", url: "https://www.youtube.com/results?search_query=tcp+three+way+handshake+explained", by: "YouTube", note: "~6 min" },
    ],
    quiz: [
      { q: "What are the three packets of the TCP handshake, in order?", options: ["SYN → ACK → FIN", "GET → 200 → CLOSE", "SYN → SYN-ACK → ACK", "PING → PONG → DATA"], answer: 2, why: "Client SYN, server SYN-ACK, client ACK — then the connection is established." },
      { q: "Which is the better fit for a live video call?", options: ["TCP — it's reliable", "UDP — speed beats perfect delivery", "Neither, use HTTP", "Both are identical"], answer: 1, why: "A dropped frame is better than lag; UDP trades reliability for speed." },
      { q: "What do TCP's sequence numbers let it do?", options: ["Encrypt the data", "Reorder packets and detect missing ones", "Find the server's IP", "Compress the stream"], answer: 1, why: "Numbering every byte lets TCP reassemble order and spot gaps to resend." },
      { q: "'Reliable, ordered, connection-first' describes…", options: ["UDP", "IP", "TCP", "ARP"], answer: 2, why: "That's TCP — it handshakes, acknowledges and retransmits." },
      { q: "DNS lookups usually ride on…", options: ["TCP", "UDP", "TLS", "ARP"], answer: 1, why: "A DNS query is tiny and speed matters, so it typically uses UDP." },
    ],
  },
  {
    id: "net-trace", track: "net", title: "Loading a web page — the full trace", minutes: 14,
    summary: "You press Enter and a dozen protocols fire in order. Trace that chain and the whole internet clicks into one story.",
    sections: [
      { type: "text", h: "One click, a whole stack in motion",
        body: `Type <code>example.com</code>, press Enter, and in well under a second a precise sequence of protocols runs — each one a lesson you've already met. Watching them fire <i>in order</i> is the moment networking stops being a list of terms and becomes a single story.` },
      { type: "svg", caption: "The five steps between Enter and the page appearing.", svg: traceSVG },
      { type: "text", h: "Step by step",
        body: `<ol>
          <li><b>DNS</b> — the name <code>example.com</code> means nothing to the network, so your machine asks a DNS server to translate it into an IP address (usually over UDP, port 53).</li>
          <li><b>ARP</b> — to send anything off your network you must reach your <b>gateway</b> (router); ARP finds its MAC address on the local link.</li>
          <li><b>TCP</b> — a 3-way handshake opens a connection to the server's IP on <b>port 443</b> (HTTPS).</li>
          <li><b>TLS</b> — client and server exchange keys so everything from here on is <b>encrypted</b> — no one on the path can read it.</li>
          <li><b>HTTP</b> — finally your browser sends <code>GET /</code>, the server replies <code>200 OK</code> with the HTML, and the page renders.</li>
        </ol>` },
      { type: "callout", icon: "🧩", title: "Supporting cast",
        body: `<b>DHCP</b> gave you your IP, gateway and DNS server when you joined the network. <b>NAT</b> rewrites your private IP to the router's public one on the way out (and back). <b>TTL</b> stops a lost packet from looping forever.` },
      { type: "text", h: "Why this is the best thing to know cold",
        body: `Almost every networking question is really "explain part of this trace." If you can narrate these five steps and say which layer and transport each uses, you can answer nearly anything they throw at you — and you'll actually understand what your future tools (Wireshark, a proxy, a scanner) are showing you.` },
      { type: "video", title: "What happens when you type a URL and press Enter", url: "https://www.youtube.com/results?search_query=what+happens+when+you+type+a+url+and+press+enter", by: "YouTube", note: "great end-to-end walkthroughs" },
    ],
    quiz: [
      { q: "What is the FIRST thing that must happen after you press Enter on example.com?", options: ["The TLS handshake", "DNS resolves the name to an IP", "The HTTP GET", "ARP to the web server"], answer: 1, why: "You can't connect until DNS turns the name into an IP address." },
      { q: "Which step turns on encryption?", options: ["DNS", "ARP", "TLS", "DHCP"], answer: 2, why: "TLS negotiates keys after the TCP handshake so the HTTP exchange is encrypted." },
      { q: "ARP is used to find…", options: ["the server's IP", "the gateway's MAC address on your local network", "the DNS server", "a free port"], answer: 1, why: "To leave your network you reach the gateway; ARP maps its IP to a MAC." },
      { q: "HTTPS uses which port by default?", options: ["80", "22", "443", "53"], answer: 2, why: "443 is HTTPS (80 is plain HTTP, 22 SSH, 53 DNS)." },
    ],
  },
];

export function lessonById(id) { return lessons.find((l) => l.id === id); }
export function lessonsInTrack(trackId) { return lessons.filter((l) => l.track === trackId); }
