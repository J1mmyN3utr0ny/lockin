// lessons_content.js — the rich, visual Learning hub (web app). Long lessons with hand-authored SVG
// diagrams, CSS animations (the "gifs"), curated video links and interactive quizzes. This is the
// theory half of the split: read & understand here, build & run in the Lab. Add lessons as data.
//
// Section types: text {h, body(html)} · svg {caption, svg} · anim {caption, html} ·
//                callout {icon, title, body(html)} · video {title, url, by, note}
// Colours use the app's CSS variables so the diagrams stay theme-correct.

export const lessonTracks = [
  { id: "net", name: "Networking", icon: "🌐", blurb: "How data actually crosses the internet — the most-tested cyber topic." },
  { id: "low", name: "Low-level & memory", icon: "🧠", blurb: "How a program really lives in memory — the heart of the GAMA research track." },
  { id: "asm", name: "Assembly (x86)", icon: "⚙️", blurb: "The language your CPU speaks. You mostly need to READ it — and know the terms cold." },
  { id: "oop", name: "OOP & C#", icon: "🎯", blurb: "The object-oriented thinking GAMA's C# workshop is built to test." },
  // Tracks below start empty by design — grow them on demand with ➕ New AI lesson.
  { id: "linux", name: "Linux", icon: "🐧", blurb: "The terminal, files, processes and permissions — cyber's home turf." },
  { id: "c", name: "C language", icon: "🔧", blurb: "Pointers, memory and the machine — the language under everything." },
  { id: "win", name: "Windows & CMD", icon: "🖥️", blurb: "Processes, the registry and the command line on the other big OS." },
  { id: "dsa", name: "DSA / LeetCode", icon: "🧮", blurb: "The patterns behind the daily problems — recognize them on sight." },
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

// --- low-level / assembly / OOP diagrams ------------------------------------------------------
const memSVG = `
<svg viewBox="0 0 320 300" role="img" aria-label="A process's memory layout" style="width:100%;height:auto">
  <text x="160" y="14" fill="var(--muted)" font-size="10" text-anchor="middle">high addresses ↑</text>
  ${[["Stack","locals, call frames — grows DOWN ↓","#4f8cff",22],
     ["↕ free space","the stack and heap grow toward each other","#1b2536",70],
     ["Heap","malloc/new — grows UP ↑","#22d3ee",118],
     [".bss","zero-initialised globals","#334155",166],
     [".data","initialised globals","#3b5bab",204],
     [".text","the program's CODE (read-only)","#2f6bff",242]].map(([n,d,c,y]) => `
    <g transform="translate(20 ${y})">
      <rect width="280" height="42" rx="7" fill="${c}" opacity=".92"/>
      <text x="12" y="19" fill="#0b0f17" font-size="12.5" font-weight="700">${n}</text>
      <text x="12" y="34" fill="#0b0f17" font-size="9.5" opacity=".85">${d}</text>
    </g>`).join("")}
  <text x="160" y="296" fill="var(--muted)" font-size="10" text-anchor="middle">low addresses ↓</text>
</svg>`;

const frameSVG = `
<svg viewBox="0 0 320 250" role="img" aria-label="A stack frame" style="width:100%;height:auto">
  ${[["arguments","what the caller passed in","#3b5bab",20],
     ["return address","where to jump back after ret ← the prize","#ef4444",64],
     ["saved ebp","the caller's base pointer","#4f8cff",108],
     ["local variables","this function's own space (buffers!)","#22d3ee",152]].map(([n,d,c,y]) => `
    <g transform="translate(20 ${y})">
      <rect width="230" height="36" rx="6" fill="${c}" opacity=".9"/>
      <text x="10" y="16" fill="#0b0f17" font-size="11.5" font-weight="700">${n}</text>
      <text x="10" y="29" fill="#0b0f17" font-size="9" opacity=".85">${d}</text>
    </g>`).join("")}
  <text x="264" y="82" fill="#ef4444" font-size="10" font-weight="700">← ebp+4</text>
  <text x="264" y="170" fill="var(--accent-2)" font-size="10" font-weight="700">← esp</text>
  <text x="160" y="240" fill="var(--muted)" font-size="9.5" text-anchor="middle">grows downward as functions call functions</text>
</svg>`;

const overflowSVG = `
<svg viewBox="0 0 340 170" role="img" aria-label="A stack buffer overflow" style="width:100%;height:auto">
  <text x="10" y="20" fill="var(--muted)" font-size="10.5">char buf[8];  gets(buf);  // no bounds check</text>
  <g transform="translate(10 34)">
    ${[0,1,2,3,4,5,6,7].map(i => `<rect x="${i*26}" y="0" width="24" height="30" rx="3" fill="var(--good)" opacity=".85"/>`).join("")}
    <rect x="208" y="0" width="110" height="30" rx="4" fill="#ef4444"/>
    <text x="104" y="46" fill="var(--good)" font-size="10" text-anchor="middle">buf[8] (safe)</text>
    <text x="263" y="46" fill="#ef4444" font-size="10" text-anchor="middle" font-weight="700">saved return addr</text>
  </g>
  <g transform="translate(10 104)">
    ${[0,1,2,3,4,5,6,7,8,9,10,11].map(i => `<rect x="${i*26}" y="0" width="24" height="30" rx="3" fill="${i<8?'#f59e0b':'#ef4444'}"/>`).join("")}
    <text x="160" y="48" fill="var(--warn)" font-size="10.5" text-anchor="middle" font-weight="700">too much input spills past buf → overwrites the return address → hijacks execution</text>
  </g>
</svg>`;

const regSVG = `
<svg viewBox="0 0 340 190" role="img" aria-label="x86 registers" style="width:100%;height:auto">
  ${[["eax","accumulator · return values","#4f8cff",0,0],["ebx","base / general","#4f8cff",1,0],
     ["ecx","counter (loops)","#22d3ee",0,1],["edx","data / general","#4f8cff",1,1],
     ["esi/edi","source / dest index","#a78bfa",0,2],["esp","stack pointer (top)","#f59e0b",1,2],
     ["ebp","base pointer (frame)","#f59e0b",0,3],["eip","instruction pointer","#ef4444",1,3]].map(
    ([n,d,c,col,row]) => `
    <g transform="translate(${10+col*165} ${8+row*44})">
      <rect width="155" height="38" rx="7" fill="var(--card-2)" stroke="${c}" stroke-width="1.5"/>
      <text x="10" y="17" fill="${c}" font-size="12.5" font-weight="800">${n}</text>
      <text x="10" y="31" fill="var(--muted)" font-size="9">${d}</text>
    </g>`).join("")}
</svg>`;

const flowSVG = `
<svg viewBox="0 0 340 150" role="img" aria-label="cmp sets flags, jumps read them" style="width:100%;height:auto">
  <g><rect x="14" y="50" width="92" height="50" rx="9" fill="var(--card-2)" stroke="var(--accent)"/>
     <text x="60" y="72" fill="var(--fg)" font-size="12" font-weight="700" text-anchor="middle">cmp a, b</text>
     <text x="60" y="88" fill="var(--muted)" font-size="9" text-anchor="middle">(a − b, tossed)</text></g>
  <text x="118" y="79" fill="var(--muted)" font-size="16">→</text>
  <g><rect x="130" y="50" width="80" height="50" rx="9" fill="var(--card-2)" stroke="var(--gold)"/>
     <text x="170" y="70" fill="var(--gold)" font-size="11.5" font-weight="700" text-anchor="middle">FLAGS</text>
     <text x="170" y="86" fill="var(--muted)" font-size="9" text-anchor="middle">ZF · SF · CF</text></g>
  <text x="222" y="79" fill="var(--muted)" font-size="16">→</text>
  <g><rect x="234" y="50" width="92" height="50" rx="9" fill="var(--card-2)" stroke="var(--good)"/>
     <text x="280" y="72" fill="var(--good)" font-size="11.5" font-weight="700" text-anchor="middle">je / jne</text>
     <text x="280" y="88" fill="var(--muted)" font-size="9" text-anchor="middle">jump if…</text></g>
  <text x="170" y="128" fill="var(--muted)" font-size="10.5" text-anchor="middle">an <tspan font-style="italic">if</tspan> in C = a compare that sets flags + a conditional jump that reads them.</text>
</svg>`;

const pillarsSVG = `
<svg viewBox="0 0 340 210" role="img" aria-label="The four pillars of OOP" style="width:100%;height:auto">
  ${[["🧊 Encapsulation","bundle data + methods, hide the internals","var(--accent)",0,0],
     ["🧬 Inheritance","a subclass reuses & extends a base","var(--good)",1,0],
     ["🎭 Polymorphism","same call, different behaviour per type","var(--violet)",0,1],
     ["🗺️ Abstraction","program to an interface, not a concretion","var(--gold)",1,1]].map(
    ([n,d,c,col,row]) => `
    <g transform="translate(${10+col*165} ${10+row*98})">
      <rect width="155" height="86" rx="12" fill="var(--card-2)" stroke="${c}" stroke-width="1.5"/>
      <text x="12" y="26" fill="${c}" font-size="12.5" font-weight="800">${n}</text>
      <foreignObject x="12" y="34" width="132" height="48"><div xmlns="http://www.w3.org/1999/xhtml" style="color:var(--muted);font-size:10px;line-height:1.4">${d}</div></foreignObject>
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

  // ===== Low-level & memory =====
  {
    id: "low-memory", track: "low", title: "How a program lives in memory", minutes: 14,
    summary: "Stack, heap, code, data — knowing where everything sits is knowing where the bodies are buried.",
    sections: [
      { type: "text", h: "One big array of bytes",
        body: `When your program runs, the OS hands it a large block of memory addressed from low numbers to high. That block isn't random — it's carved into <b>regions</b>, each holding a different kind of thing. Knowing this map is the foundation of every low-level topic: debugging, reverse engineering and exploitation all come back to "what lives where."` },
      { type: "svg", caption: "A process's memory, high addresses at the top.", svg: memSVG },
      { type: "text", h: "The regions",
        body: `<ul>
          <li><b>.text</b> — the actual machine code. Read-only, so a bug can't rewrite your instructions.</li>
          <li><b>.data / .bss</b> — global/static variables (<code>.data</code> if you gave them a value, <code>.bss</code> if they start at zero).</li>
          <li><b>Heap</b> — memory you request at runtime with <code>malloc</code>/<code>new</code>. It grows <i>upward</i>, and you must free it.</li>
          <li><b>Stack</b> — automatic storage for function calls: locals, arguments and the all-important <b>return address</b>. It grows <i>downward</i>, toward the heap.</li>
        </ul>` },
      { type: "callout", icon: "⚠️", title: "Why attackers care",
        body: `The stack holds the return address that says "where do I go when this function finishes?" Overwrite it, and you control the program. That single fact seeds the most classic exploit in computing — two lessons from now.` },
      { type: "text", h: "Stack vs heap, one line each",
        body: `<b>Stack</b>: fast, automatic, freed for you when a function returns — but small and fixed-size. <b>Heap</b>: flexible and large, lives as long as you want — but you must free it, and forgetting is a <i>memory leak</i>.` },
      { type: "video", title: "Memory layout of a C program, visualised", url: "https://www.youtube.com/results?search_query=memory+layout+of+a+c+program+stack+heap", by: "YouTube", note: "~8 min" },
    ],
    quiz: [
      { q: "Which region holds a function's locals and its return address?", options: ["Heap", "Stack", ".text", ".bss"], answer: 1, why: "Locals and call frames live on the stack (which grows down)." },
      { q: "malloc / new allocate from…", options: ["the stack", "the heap", "the code segment", "registers"], answer: 1, why: "Dynamic runtime memory comes from the heap, which grows up." },
      { q: "Why is .text read-only?", options: ["to save space", "so running code can't be modified/tampered with", "it's faster", "no reason"], answer: 1, why: "Non-writable code blocks a bug or attacker from rewriting the instructions." },
      { q: "Forgetting to free heap memory is called…", options: ["a stack overflow", "a memory leak", "a segfault", "a race condition"], answer: 1, why: "Unfreed heap memory accumulates — a leak." },
    ],
  },
  {
    id: "low-stack", track: "low", title: "The stack: call, ret & the return address", minutes: 15,
    summary: "How functions call functions — and why the saved return address is the crown jewel of exploitation.",
    sections: [
      { type: "text", h: "A stack of plates",
        body: `The stack is <b>LIFO</b> — last-in, first-out, like a stack of plates: you <code>push</code> onto the top and <code>pop</code> off the top. The CPU keeps a register, <code>esp</code>, always pointing at the top. Every function call uses it.` },
      { type: "text", h: "What call and ret really do",
        body: `<ul>
          <li><code>call f</code> — pushes the <b>return address</b> (the instruction right after the call) onto the stack, then jumps to <code>f</code>.</li>
          <li><code>ret</code> — pops that address back off and jumps to it, resuming where you left off.</li>
        </ul>
        That saved return address is how the CPU remembers where to come back to — and it sits in memory right next to your local variables.` },
      { type: "svg", caption: "One stack frame — the return address sits just above the locals.", svg: frameSVG },
      { type: "text", h: "The stack frame",
        body: `When a function starts it sets up a <b>frame</b>: <code>push ebp; mov ebp, esp</code> anchors <code>ebp</code> so the function can reliably reach its arguments and locals while <code>esp</code> moves around. The epilogue tears it down and <code>ret</code> uses the saved address.` },
      { type: "callout", icon: "🎯", title: "The one sentence to remember",
        body: `The saved <b>return address</b> lives on the stack, next to your local buffers. If input can write past a buffer, it can reach and overwrite that address — and then <code>ret</code> jumps wherever the attacker chose.` },
      { type: "video", title: "How the call stack works (push, call, ret)", url: "https://www.youtube.com/results?search_query=call+stack+return+address+assembly+explained", by: "YouTube" },
    ],
    quiz: [
      { q: "What does `call f` push before jumping to f?", options: ["eax", "the return address", "the stack pointer", "nothing"], answer: 1, why: "call saves the return address so ret can come back." },
      { q: "The stack is what kind of structure?", options: ["FIFO (queue)", "LIFO (last-in first-out)", "a tree", "a hash map"], answer: 1, why: "Push/pop from the top — last in, first out." },
      { q: "`push ebp; mov ebp, esp` is the…", options: ["epilogue", "function prologue (frame setup)", "a syscall", "a loop"], answer: 1, why: "The prologue anchors ebp so params/locals stay reachable." },
      { q: "Why is the saved return address a target?", options: ["it's encrypted", "overwriting it redirects where ret jumps", "it stores passwords", "it's read-only"], answer: 1, why: "Control the return address and you control execution — the classic exploit." },
    ],
  },
  {
    id: "low-overflow", track: "low", title: "Buffer overflow — the classic exploit", minutes: 13,
    summary: "Write past a buffer, overwrite the return address, hijack the program. You learn it to defend against it.",
    sections: [
      { type: "text", h: "The bug in one picture",
        body: `A <b>buffer</b> is a fixed-size chunk of memory — say <code>char buf[8]</code>. If code copies input into it <i>without checking the length</i>, and the input is longer than 8 bytes, the extra bytes don't vanish — they spill into whatever sits next. On the stack, what sits next is the saved <b>return address</b>.` },
      { type: "svg", caption: "Too much input spills past the buffer into the saved return address.", svg: overflowSVG },
      { type: "text", h: "Why it's dangerous",
        body: `Overwrite the return address with one of the attacker's choosing, and when the function runs <code>ret</code>, the CPU jumps there — into attacker-supplied code, or a useful existing function. The root cause is always an <b>unbounded copy</b> — <code>gets()</code>, <code>strcpy()</code>, <code>scanf("%s")</code> with no width — and the fix is always to <b>bound the length</b>.` },
      { type: "callout", icon: "🛡️", title: "How defenders stop it",
        body: `<b>Stack canaries</b> — a secret value before the return address; if it changed, abort. <b>ASLR</b> — randomise addresses so the attacker can't predict where to jump. <b>NX/DEP</b> — mark the stack non-executable so injected code won't run. Modern systems stack all three.` },
      { type: "text", h: "Your stance",
        body: `You learn this to <b>defend</b>: to spot the vulnerable patterns in code review, to understand why those mitigations exist, and to write code that can't be exploited this way. Understanding the attack is what lets you prevent it — never the reverse.` },
      { type: "video", title: "Stack buffer overflow, explained visually", url: "https://www.youtube.com/results?search_query=stack+buffer+overflow+explained+animation", by: "YouTube" },
    ],
    quiz: [
      { q: "A stack buffer overflow overwrites…", options: ["the heap", "the saved return address next to the buffer", "the CPU registers", "the disk"], answer: 1, why: "Writing past a local buffer clobbers the adjacent saved return address." },
      { q: "Which is a classic unbounded, dangerous call?", options: ["printf", "gets()", "malloc", "free"], answer: 1, why: "gets() reads input with no length limit — a textbook overflow source." },
      { q: "Which defence randomises memory addresses?", options: ["ASLR", "a stack canary", "NX/DEP", "gzip"], answer: 0, why: "ASLR randomises layout; canaries detect overwrites; NX blocks executing the stack." },
      { q: "The root fix for buffer overflows is…", options: ["faster CPUs", "bounding the copy length / input size", "more RAM", "encryption"], answer: 1, why: "Never copy more than the buffer holds — bound the length." },
    ],
  },

  // ===== Assembly (x86) =====
  {
    id: "asm-registers", track: "asm", title: "Registers & moving data", minutes: 12,
    summary: "Registers are the CPU's variables. Everything you've written compiles down to moving data between them.",
    sections: [
      { type: "text", h: "The CPU's tiny, ultra-fast variables",
        body: `Assembly is the language your processor actually executes — every high-level language compiles down to it. It works on <b>registers</b>: a handful of tiny, extremely fast slots inside the CPU. On 32-bit x86 the main ones are <code>eax, ebx, ecx, edx</code>, plus special-purpose <code>esi/edi, esp, ebp, eip</code>.` },
      { type: "svg", caption: "The x86 registers and what each is conventionally for.", svg: regSVG },
      { type: "text", h: "mov and friends",
        body: `The workhorse is <code>mov dest, src</code> — copy a value. Intel syntax always puts the <b>destination first</b>:<br><br>
          <code>mov eax, 5</code> → eax = 5 · <code>add eax, 3</code> → eax = 8 · <code>mov ebx, eax</code> → ebx = 8 · <code>dec ebx</code> → ebx = 7.<br><br>
          Memory uses brackets: <code>mov eax, [ebx]</code> loads "the value <i>at</i> the address in ebx", and <code>[ebx + ecx*4]</code> is exactly how <code>array[i]</code> compiles.` },
      { type: "callout", icon: "💡", title: "You mostly READ this",
        body: `For GAMA you don't write big programs — you <b>read</b> disassembly and know the terms cold. Paste a tiny C function into <code>godbolt.org</code> and watch it become these instructions; reading C↔ASM side by side is the fastest way to learn.` },
      { type: "video", title: "x86 assembly basics: registers and mov", url: "https://www.youtube.com/results?search_query=x86+assembly+registers+mov+tutorial", by: "YouTube" },
    ],
    quiz: [
      { q: "In `mov eax, ebx`, which way does the data go?", options: ["ebx → eax (dest first)", "eax → ebx", "they swap", "neither"], answer: 0, why: "Intel syntax: destination first, so ebx is copied into eax." },
      { q: "After `mov eax, 5` then `add eax, 3`, eax is…", options: ["5", "8", "3", "15"], answer: 1, why: "5 + 3 = 8." },
      { q: "`[ebx + ecx*4]` usually compiles from…", options: ["a function call", "array[i] indexing", "a syscall", "a string"], answer: 1, why: "base + index*scale is exactly arr[ecx] for a 4-byte element." },
      { q: "Which register is 'the counter' used by loops?", options: ["eax", "ecx", "esp", "eip"], answer: 1, why: "ecx is the counter register (the loop instruction decrements it)." },
    ],
  },
  {
    id: "asm-control", track: "asm", title: "Control flow: cmp, flags & jumps", minutes: 12,
    summary: "No if-statements down here — just compare, set a flag, and jump. That's every decision a computer makes.",
    sections: [
      { type: "text", h: "How a CPU makes a decision",
        body: `At this level there's no <code>if</code>. The CPU does two steps: <b>compare</b> two values (which quietly sets status <b>flags</b>), then a <b>conditional jump</b> reads those flags and decides whether to branch. Every loop and every if you've written becomes this pattern.` },
      { type: "svg", caption: "cmp sets the flags; the jump reads them.", svg: flowSVG },
      { type: "text", h: "cmp and the jumps",
        body: `<code>cmp a, b</code> computes <code>a − b</code> but <i>throws away the result</i>, keeping only the flags — chiefly the <b>Zero Flag</b> (set if the result was 0, i.e. a == b). Then:<br><br>
          <code>je/jz</code> equal · <code>jne/jnz</code> not equal · <code>jg/jl</code> greater/less (signed) · <code>ja/jb</code> above/below (unsigned).<br><br>
          So <code>if (x == 5)</code> becomes <code>cmp x, 5</code> then <code>jne skip</code>.` },
      { type: "callout", icon: "🔁", title: "Loops, too",
        body: `A <code>for</code> loop is the same trick plus the <code>loop</code> instruction, which decrements <code>ecx</code> and jumps back while it's non-zero — which is exactly why ecx is "the counter register."` },
      { type: "video", title: "Assembly control flow: cmp & conditional jumps", url: "https://www.youtube.com/results?search_query=assembly+cmp+conditional+jumps+control+flow", by: "YouTube" },
    ],
    quiz: [
      { q: "What does `cmp a, b` keep?", options: ["a − b in a register", "only the CPU flags", "nothing", "the larger value"], answer: 1, why: "cmp discards the result and keeps only the flags for a following jump." },
      { q: "`je` jumps when…", options: ["always", "the zero flag is set (operands were equal)", "a > b", "never"], answer: 1, why: "cmp sets ZF if a==b; je jumps on ZF." },
      { q: "An `if` in C becomes, in ASM…", options: ["a single mov", "a cmp plus a conditional jump", "a syscall", "a push"], answer: 1, why: "Compare to set flags, then branch on them." },
      { q: "The `loop` instruction decrements which register?", options: ["eax", "ecx", "esp", "eip"], answer: 1, why: "loop decrements ecx and jumps while it's non-zero." },
    ],
  },

  // ===== OOP & C# =====
  {
    id: "oop-pillars", track: "oop", title: "OOP: the four pillars", minutes: 14,
    summary: "GAMA's C# workshop is an OOP design test. These are the four ideas it's really checking for.",
    sections: [
      { type: "text", h: "Why objects",
        body: `Object-oriented programming organises code around <b>objects</b> — bundles of data (fields) and the behaviour that acts on them (methods). Done well, it lets you model a problem in pieces that extend without breaking each other. GAMA's recommended workshop is, underneath, a test of whether you can design that way.` },
      { type: "svg", caption: "The four pillars — the vocabulary of the workshop.", svg: pillarsSVG },
      { type: "text", h: "The four pillars",
        body: `<ul>
          <li><b>Encapsulation</b> — bundle data with its methods and hide the internals behind a clean interface (private fields, public methods/properties). The outside can't reach in and break your invariants.</li>
          <li><b>Inheritance</b> — a subclass reuses and extends a base class. <code>Car</code> and <code>Truck</code> both derive from <code>Vehicle</code> and share its code.</li>
          <li><b>Polymorphism</b> — the same call does the right thing per type: <code>vehicle.Describe()</code> runs Car's version for a Car, Truck's for a Truck.</li>
          <li><b>Abstraction</b> — program to an <i>interface</i>, not a concrete type; depend on "something drawable", not a specific class, so implementations swap freely.</li>
        </ul>` },
      { type: "callout", icon: "🏗️", title: "The workshop's real test: open/closed",
        body: `GAMA adds requirements <b>stage by stage</b> and watches whether your earlier code survives. Good OOP means you <i>add</i> a feature by adding a new class — <b>open for extension, closed for modification</b> — instead of rewriting what already works. Design for that from stage one.` },
      { type: "text", h: "Abstract class vs interface (they love this one)",
        body: `An <b>abstract class</b> can hold state and some implemented methods, but a class extends only <i>one</i>. An <b>interface</b> is a pure contract of signatures, and a class implements <i>many</i>. Rule of thumb: "is-a" with shared code → abstract class; "can-do" capability → interface. And C# has a destructor/finalizer (<code>~Class()</code>) plus <code>IDisposable</code>; C++ has real destructors; Java has neither — a classic exam question.` },
      { type: "video", title: "The four pillars of OOP, explained", url: "https://www.youtube.com/results?search_query=four+pillars+of+oop+explained", by: "YouTube" },
    ],
    quiz: [
      { q: "Hiding an object's internals behind a clean public interface is…", options: ["inheritance", "encapsulation", "polymorphism", "abstraction"], answer: 1, why: "Encapsulation bundles data + methods and hides the internals." },
      { q: "'Same call, different behaviour per type' is…", options: ["polymorphism", "encapsulation", "inheritance", "abstraction"], answer: 0, why: "That's polymorphism — one interface, many concrete behaviours." },
      { q: "A class can extend how many abstract classes / implement how many interfaces?", options: ["one / one", "many / one", "one abstract class / many interfaces", "many / many"], answer: 2, why: "Single inheritance of an abstract class, but many interfaces." },
      { q: "'Open for extension, closed for modification' means you add features by…", options: ["rewriting old classes", "adding new classes without changing working ones", "deleting code", "using globals"], answer: 1, why: "Extend via new types; don't modify what already works — what the workshop tests." },
    ],
  },
];

export function lessonById(id) { return lessons.find((l) => l.id === id); }
export function lessonsInTrack(trackId) { return lessons.filter((l) => l.track === trackId); }
