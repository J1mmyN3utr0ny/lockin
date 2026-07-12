// cs_milestones.js — a SOCRATIC breakdown of the Local-CyberComm assignment.
// Rule enforced by design: guide, never solve. Hints escalate nudge → specific → pseudocode
// OUTLINE (never a full solution). Library cards jog memory without giving code.

export const project = {
  name: "Local-CyberComm (CS summer project)",
  summary: "A LAN chat/comms app: multithreaded server, SQLite auth, a custom framed protocol, GUI, file transfer, and WebRTC audio/video calls. Build it in loopback first (127.0.0.1), then the LAN.",
  learnGoal: "You want EXPERIENCE, not just a finished file. Each milestone starts with design questions you answer yourself; code hints are a last resort and never complete.",
  gutCheck: "If you couldn't re-explain a milestone's code to your teacher tomorrow, you're not done with it yet."
};

export const milestones = [
  {
    id: "cs1", name: "1 · Loopback echo",
    goal: "One client talks to one server on 127.0.0.1 and gets a reply. Nail the socket lifecycle.",
    designQuestions: [
      "What are the exact server-side steps between creating a socket and reading data? (You know this term set.)",
      "Who calls connect() and who calls accept()?",
      "What does recv() return when the peer disconnects, and how will you detect it?"
    ],
    libs: ["socket"],
    hints: [
      "Server side is a 4-step sequence you already have flashcards for. Say the sequence out loud first.",
      "The server loops on accept(); each accepted connection is its own socket you recv/send on.",
      "OUTLINE: socket → bind((host,port)) → listen() → loop: conn=accept() → loop: data=recv(n); if not data: break; send back."
    ],
    reflection: "In your own words: why does a server need BOTH a listening socket and a per-connection socket?"
  },
  {
    id: "cs2", name: "2 · Framed protocol",
    goal: "Send whole messages over a byte stream reliably — no half-messages, no merged messages.",
    designQuestions: [
      "TCP is a byte STREAM, not messages. If you send two JSON objects fast, how does the receiver know where one ends?",
      "What did your old protocol.py do with a fixed-width length header? Can you reuse that idea?",
      "What happens if recv() returns fewer bytes than you asked for?"
    ],
    libs: ["json", "socket"],
    hints: [
      "You've solved this before: length-prefix each message. Look at your own protocol.py pattern.",
      "Fixed-width header (e.g. 10 chars, zero-padded) = the byte count of the JSON that follows.",
      "OUTLINE: send = zfilled_len(json)+json; recv = read exactly 10 bytes → int → read exactly that many bytes → json.loads. Write a recv_all(n) helper that loops until it has n bytes."
    ],
    reflection: "Why is 'read exactly N bytes' a loop and not a single recv() call?"
  },
  {
    id: "cs3", name: "3 · Multi-client server",
    goal: "Many clients connected at once, each handled independently.",
    designQuestions: [
      "If accept() and recv() block, how can one server serve two clients at the same time?",
      "What's the trade-off between a thread-per-client and a single asyncio event loop?",
      "What shared state do multiple clients touch, and what could go wrong when two touch it at once?"
    ],
    libs: ["threading", "asyncio"],
    hints: [
      "Two classic answers: a thread per client, or async I/O. Pick ONE and know why.",
      "Thread-per-client: accept in a loop, hand each conn to a new thread running your handle_client.",
      "OUTLINE (threads): loop: conn=accept() → Thread(target=handle_client, args=(conn,)).start(). Keep a shared clients dict; guard it if you mutate it from many threads."
    ],
    reflection: "Name one bug that can ONLY happen with concurrency that can't happen with one client."
  },
  {
    id: "cs4", name: "4 · Registration & Auth (SQLite)",
    goal: "Sign-up + login backed by a database, with passwords that are never stored in plaintext.",
    designQuestions: [
      "What columns does a users table need? What must be UNIQUE?",
      "Why is storing the raw password a security failure even on a LAN project? What do you store instead?",
      "What's the difference between hashing and encryption here?"
    ],
    libs: ["sqlite3", "hashlib"],
    hints: [
      "Store a hash, never the password. On login, hash the attempt and compare.",
      "Use a salt so identical passwords don't produce identical hashes.",
      "OUTLINE: CREATE TABLE users(id, username UNIQUE, pw_hash, salt). register → make salt, hash(salt+pw), INSERT. login → SELECT by username, re-hash attempt with stored salt, compare."
    ],
    reflection: "Explain to yourself what a salt defends against."
  },
  {
    id: "cs5", name: "5 · Chat: broadcast + private relay",
    goal: "Public messages to everyone, and 1-to-1 private messages routed through the server.",
    designQuestions: [
      "How does the server know which socket belongs to which logged-in user?",
      "For a private message, how do you find the recipient's socket from their username?",
      "What should happen if the recipient is offline?"
    ],
    libs: ["socket", "json"],
    hints: [
      "Keep a mapping username → connection once a client authenticates.",
      "Broadcast = iterate all connections; private = look up the one target connection and send only to it.",
      "OUTLINE: on a 'msg' command with a 'to' field, if to in clients: send to that socket; else return an error status to the sender."
    ],
    reflection: "Why is routing through the server (relay) simpler on a LAN than direct client-to-client for TEXT?"
  },
  {
    id: "cs6", name: "6 · File transfer",
    goal: "Send a file between users through your protocol.",
    designQuestions: [
      "Your protocol carries JSON text. How do you put raw bytes (an image) inside a JSON message?",
      "How will the receiver know the filename and when the file is complete?",
      "Would you send a huge file in one message or in chunks — and why?"
    ],
    libs: ["json", "os"],
    hints: [
      "Bytes don't fit in JSON directly — encode them to text first (think base64) and decode on arrival.",
      "Include metadata: filename + size, then the data field.",
      "OUTLINE: read file bytes → base64 encode → send {command:'file', name, size, data} → receiver base64-decodes and writes to disk. For big files, chunk and reassemble."
    ],
    reflection: "What's the cost of base64 (hint: size), and when would chunking matter?"
  },
  {
    id: "cs7", name: "7 · GUI (AI-assisted, but understood)",
    goal: "A desktop UI over your client. Your teacher ALLOWS AI for colors/animations — as long as you can explain the code.",
    designQuestions: [
      "What does the GUI actually need from your client layer — which functions does it call?",
      "The GUI runs an event loop; your networking also loops. How do you keep the UI from freezing while waiting on the socket?",
      "For every widget the AI generates, can you say what line creates it and what its callback does?"
    ],
    libs: ["customtkinter", "threading"],
    hints: [
      "Keep networking OFF the UI thread — run recv in a background thread and hand messages to the UI.",
      "Design the seam first: your GUI should call clean client functions (login(), send_msg()), not raw sockets.",
      "OUTLINE: build the client API as plain functions; let the AI style the CustomTkinter shell that calls them; walk through the generated file and annotate each block in your own words."
    ],
    reflection: "Point to the exact spot where a UI callback triggers a network send. Could you rewrite that wiring yourself?"
  },
  {
    id: "cs8", name: "8 · WebRTC audio/video calls",
    goal: "Peer-to-peer voice/video, with your server only helping the two peers find each other (signaling).",
    designQuestions: [
      "What job does your existing TCP server play in a WebRTC call — does the audio flow through it?",
      "What are SDP and ICE candidates, in one sentence each?",
      "Why is P2P media better than relaying audio through the server on a LAN?"
    ],
    libs: ["aiortc", "asyncio"],
    hints: [
      "Your server is the SIGNALING channel: it passes SDP offers/answers + ICE candidates between the two peers. Media goes peer-to-peer.",
      "This is the hardest milestone — get text + files rock-solid first so signaling is 'just another message type'.",
      "OUTLINE: peer A creates an offer (SDP) → send through your protocol → peer B sets remote desc, makes an answer → exchange ICE candidates the same way → aiortc handles the media once connected."
    ],
    reflection: "Draw the message flow of a call setup. Which parts are your code vs aiortc's?"
  }
];

// Library memory-jog cards — API SURFACE + what to look up. No code, on purpose.
export const libs = {
  socket: { name: "socket", whatFor: "Raw TCP/UDP networking.",
    keyAPI: ["socket(AF_INET, SOCK_STREAM)", "bind / listen / accept (server)", "connect (client)", "send / sendall / recv", "close"],
    gotcha: "recv(n) can return fewer than n bytes — always loop to read a full message.",
    quiz: "Which two calls are server-only, and which is client-only?" },
  threading: { name: "threading", whatFor: "Run each client handler concurrently.",
    keyAPI: ["Thread(target=, args=)", ".start() / .join()", "Lock() for shared state", "daemon threads"],
    gotcha: "Shared dict/list mutated from many threads needs a Lock or you get race conditions.",
    quiz: "When do you actually need a Lock?" },
  asyncio: { name: "asyncio", whatFor: "Single-threaded concurrency via an event loop (alt to threads).",
    keyAPI: ["async def / await", "asyncio.run()", "start_server / open_connection", "reader.read / writer.write+drain"],
    gotcha: "One blocking call (time.sleep, blocking recv) stalls the WHOLE loop.",
    quiz: "Why can't you call a normal blocking socket.recv inside an async handler?" },
  sqlite3: { name: "sqlite3", whatFor: "Local file database for users/messages.",
    keyAPI: ["connect('app.db')", "cursor()", "execute(sql, params)", "fetchone / fetchall", "commit / close"],
    gotcha: "Use parameterized queries (?), never f-string SQL — that's SQL injection.",
    quiz: "Why is `execute(f\"... {username}\")` dangerous?" },
  json: { name: "json", whatFor: "Serialize your protocol messages.",
    keyAPI: ["dumps(obj) → str", "loads(str) → obj", "only JSON-safe types"],
    gotcha: "Raw bytes aren't JSON-serializable — encode (base64) first.",
    quiz: "Which Python types survive a dumps→loads round trip unchanged?" },
  hashlib: { name: "hashlib", whatFor: "Hash passwords for storage.",
    keyAPI: ["sha256(b'...')", ".hexdigest()", "combine with a per-user salt", "consider bcrypt/scrypt for real apps"],
    gotcha: "A hash is one-way — you compare hashes, you never 'decrypt' them.",
    quiz: "How do you verify a login if you can't reverse the hash?" },
  customtkinter: { name: "customtkinter", whatFor: "Nicer-looking Tkinter GUI (AI-allowed layer).",
    keyAPI: ["CTk() window", "CTkFrame / CTkButton / CTkEntry", "command= callbacks", "pack / grid / place", "mainloop()"],
    gotcha: "mainloop() blocks — do networking on a separate thread and marshal updates back.",
    quiz: "What freezes the UI, and how do you avoid it?" },
  aiortc: { name: "aiortc", whatFor: "WebRTC (audio/video) in Python.",
    keyAPI: ["RTCPeerConnection", "createOffer / createAnswer (SDP)", "onicecandidate", "MediaStreamTrack"],
    gotcha: "aiortc is async — it lives in your asyncio loop; your server only relays SDP/ICE.",
    quiz: "Does the call audio travel through your TCP server? Why/why not?" },
  os: { name: "os / subprocess", whatFor: "Files on disk + opening received files.",
    keyAPI: ["os.path.exists / join / getsize", "open(path,'wb')", "os.startfile (Windows)", "subprocess.run"],
    gotcha: "Never pass untrusted input straight to a shell command.",
    quiz: "How would you safely open a file the user just received?" }
};
