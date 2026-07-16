// cs_milestones.js — the Local-CyberComm assignment as FULL LESSONS (user decision:
// the Socratic hint-cap wasn't enough — each milestone now teaches everything from
// scratch: precise requirements, the actual code, and a line-by-line walkthrough).
// The gut-check still applies: type the code yourself and be able to re-explain
// every line — the lesson gives you the material, owning it is still on you.

export const project = {
  name: "Local-CyberComm (CS summer project)",
  summary: "A LAN chat/comms app: multithreaded server, SQLite auth, a custom framed protocol, GUI, file transfer, and WebRTC audio/video calls. Build it in loopback first (127.0.0.1), then the LAN.",
  learnGoal: "Each milestone is a full lesson: exact requirements, the code you need with every line explained, the classic bugs, and how to verify it works. Type it yourself — don't paste.",
  gutCheck: "If you couldn't re-explain a milestone's code to your teacher tomorrow, you're not done with it yet."
};

export const milestones = [
  {
    id: "cs1", name: "1 · Loopback echo",
    goal: "One client talks to one server on 127.0.0.1 and gets a reply. Nail the socket lifecycle.",
    designQuestions: [
      "What are the exact server-side steps between creating a socket and reading data?",
      "Who calls connect() and who calls accept()?",
      "What does recv() return when the peer disconnects, and how will you detect it?"
    ],
    libs: ["socket"],
    lesson: {
      intro: "A socket is your program's handle on a network conversation — the OS does the actual TCP work; you just read and write bytes through the handle. TCP needs two different roles: a SERVER that sits on a known address waiting, and a CLIENT that dials that address. 127.0.0.1 (loopback) is a fake network wire inside your own PC — perfect for developing, because both programs run on your machine and no Wi-Fi/firewall is involved yet.",
      requirements: [
        "Two separate files: server.py and client.py, run in two separate terminals.",
        "Server binds 127.0.0.1:5050, accepts ONE client, and echoes every message back unchanged.",
        "Client reads lines from input(), sends each to the server, prints the echoed reply.",
        "Typing quit in the client closes the connection cleanly (no traceback on either side).",
        "Server survives the client leaving: it prints 'disconnected' and goes back to accept() for the next client."
      ],
      steps: [
        {
          title: "server.py — the whole file",
          teach: "The server lifecycle is a fixed 4-step ritual: socket() makes the handle, bind() claims an address, listen() tells the OS to queue incoming dials, accept() blocks until someone dials — and hands you a SECOND socket that represents that one conversation. The listening socket never carries data; it only produces connection sockets.",
          code: "import socket\n\nHOST = \"127.0.0.1\"   # loopback = this machine only; swap for your LAN IP later\nPORT = 5050          # any free port above 1024\n\nserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\nserver.bind((HOST, PORT))\nserver.listen()\nprint(f\"listening on {HOST}:{PORT}\")\n\nwhile True:                      # outer loop: one client after another\n    conn, addr = server.accept() # BLOCKS until a client connects\n    print(\"connected:\", addr)\n    while True:                  # inner loop: this one client's messages\n        data = conn.recv(1024)   # BLOCKS until bytes arrive (or the peer leaves)\n        if not data:             # b\"\" means: the client closed the connection\n            break\n        conn.sendall(data)       # echo the exact bytes back\n    conn.close()\n    print(\"disconnected:\", addr)",
          lines: [
            "socket.socket(AF_INET, SOCK_STREAM) — AF_INET means IPv4 addresses, SOCK_STREAM means TCP (reliable, ordered bytes). UDP would be SOCK_DGRAM.",
            "setsockopt(SO_REUSEADDR, 1) — lets you restart the server immediately after killing it; without it the port stays 'busy' for ~a minute and bind() throws 'address already in use'.",
            "bind((HOST, PORT)) — takes ONE argument: a (host, port) tuple. Forgetting the double parentheses is the #1 beginner error.",
            "listen() — doesn't block; it just switches the socket into 'accepting dials' mode.",
            "conn, addr = accept() — conn is a NEW socket for this client; addr is their (ip, port). You recv/send on conn, never on server.",
            "recv(1024) — 'give me up to 1024 bytes'. It blocks until there's something. The 1024 is a maximum, not a promise.",
            "if not data — recv() returning empty bytes is THE disconnect signal. Miss this and your loop spins forever on b\"\".",
            "sendall(data) — send() may send only part of the buffer; sendall() loops internally until everything went out. Always prefer sendall."
          ]
        },
        {
          title: "client.py — the whole file",
          teach: "The client is simpler: make a socket, connect() to the server's address, then send and recv in whatever rhythm your app needs. Text must become bytes before sending — that's what .encode()/.decode() do.",
          code: "import socket\n\nsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nsock.connect((\"127.0.0.1\", 5050))   # dial the server; blocks until accepted\n\nwhile True:\n    text = input(\"you> \")\n    if text == \"quit\":\n        break\n    sock.sendall(text.encode(\"utf-8\"))   # str -> bytes\n    reply = sock.recv(1024)\n    if not reply:                        # server vanished\n        print(\"server closed the connection\")\n        break\n    print(\"echo>\", reply.decode(\"utf-8\"))  # bytes -> str\n\nsock.close()",
          lines: [
            "connect((host, port)) — the client-side counterpart of accept(). Also takes a tuple.",
            "text.encode(\"utf-8\") — sockets carry BYTES, not strings. encode turns str into bytes; decode does the reverse on arrival.",
            "sock.close() — sends TCP's goodbye; on the server side this is what makes recv() return b\"\"."
          ]
        }
      ],
      pitfalls: [
        "bind(HOST, PORT) instead of bind((HOST, PORT)) — TypeError. The address is one tuple argument.",
        "recv()ing on the listening socket instead of the accepted conn — data never arrives.",
        "Assuming one send() equals one recv() — TCP may merge or split them. It happens to look 1:1 on loopback with tiny messages; milestone 2 fixes this properly.",
        "Forgetting SO_REUSEADDR, then getting OSError: address already in use on every restart."
      ],
      verify: [
        "Terminal 1: python server.py → prints 'listening'. Terminal 2: python client.py → type hello → see 'echo> hello'.",
        "Type quit in the client — the server should print 'disconnected' and NOT crash.",
        "Start the client again without restarting the server — it should connect (outer accept loop works)."
      ]
    },
    hints: [
      "Server side is a 4-step sequence: say it out loud before reading the lesson.",
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
      "What happens if recv() returns fewer bytes than you asked for?",
      "Why must 'read exactly N bytes' be a loop?"
    ],
    libs: ["json", "socket"],
    lesson: {
      intro: "TCP guarantees your bytes arrive in order — but it does NOT preserve message boundaries. send('abc'); send('def') can arrive as 'abcdef', or 'ab' then 'cdef'. So every real protocol adds FRAMING: a rule for where a message starts and ends. The simplest solid rule is a length prefix — every message starts with a fixed-width field saying how many bytes follow. This module (protocol.py) becomes the foundation EVERYTHING later builds on: chat, auth, files, and call signaling are all just JSON dicts pushed through these two functions.",
      requirements: [
        "One shared file protocol.py imported by BOTH server and client — one implementation, zero drift.",
        "send_msg(sock, obj): any JSON-able dict goes out as: 10-digit zero-padded length header + UTF-8 JSON payload.",
        "recv_msg(sock): returns the parsed dict, or None if the peer disconnected — never a half message.",
        "A recv_all(sock, n) helper that loops until it has EXACTLY n bytes (or the peer is gone).",
        "Test: send 100 messages back-to-back; the receiver gets exactly 100 intact dicts."
      ],
      steps: [
        {
          title: "protocol.py — the whole file",
          teach: "Receiving is where framing pays off. recv(n) means 'AT MOST n bytes', so reading a 42-byte payload may take several recv calls. recv_all() hides that loop. After it, recv_msg is simple: read exactly 10 bytes → parse the number → read exactly that many bytes → json.loads.",
          code: "import json\n\nHEADER = 10  # every message starts with a 10-char length field, e.g. b\"0000000042\"\n\n\ndef send_msg(sock, obj):\n    \"\"\"Serialize obj and send it with a fixed-width length prefix.\"\"\"\n    payload = json.dumps(obj).encode(\"utf-8\")\n    header = str(len(payload)).zfill(HEADER).encode(\"utf-8\")\n    sock.sendall(header + payload)\n\n\ndef recv_all(sock, n):\n    \"\"\"Read EXACTLY n bytes, or None if the peer disconnected mid-way.\"\"\"\n    data = b\"\"\n    while len(data) < n:\n        chunk = sock.recv(n - len(data))\n        if not chunk:          # peer closed — can't complete the message\n            return None\n        data += chunk\n    return data\n\n\ndef recv_msg(sock):\n    \"\"\"One whole message as a dict, or None when the peer is gone.\"\"\"\n    header = recv_all(sock, HEADER)\n    if header is None:\n        return None\n    length = int(header)               # b\"0000000042\" -> 42\n    payload = recv_all(sock, length)\n    if payload is None:\n        return None\n    return json.loads(payload.decode(\"utf-8\"))",
          lines: [
            "HEADER = 10 — fixed width means the receiver ALWAYS knows the first read is exactly 10 bytes. 10 digits allows messages up to ~9.5 GB — plenty.",
            "json.dumps(obj).encode() — dict → JSON string → bytes. JSON is your wire format; every feature later is just a dict with a \"command\" key.",
            "str(len(payload)).zfill(10) — zfill left-pads with zeros: 42 → '0000000042'. Fixed width is what makes the header parseable without a delimiter.",
            "sendall(header + payload) — one call so header and payload can't be separated by a bug between two sends.",
            "recv(n - len(data)) — ask only for what's still missing, so you never swallow the START of the NEXT message.",
            "return None on disconnect — every caller uses 'msg = recv_msg(sock); if msg is None: peer left'. One convention everywhere."
          ]
        },
        {
          title: "Prove it: the merge test",
          teach: "The whole point of framing is surviving message merges. Force one: fire many sends instantly, then check every message arrives intact. Update server.py's inner loop to use protocol.recv_msg/send_msg, then run this client.",
          code: "# test_client.py\nimport socket\nimport protocol\n\nsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nsock.connect((\"127.0.0.1\", 5050))\n\nfor i in range(100):                       # no pauses — force TCP to merge them\n    protocol.send_msg(sock, {\"n\": i, \"text\": \"message number %d\" % i})\n\nok = 0\nfor i in range(100):\n    reply = protocol.recv_msg(sock)\n    assert reply is not None and reply[\"echo\"][\"n\"] == i, f\"broken at {i}: {reply}\"\n    ok += 1\nprint(\"all\", ok, \"messages intact\")\nsock.close()",
          lines: [
            "The server side pairs with this: msg = protocol.recv_msg(conn); if msg is None: break; protocol.send_msg(conn, {\"echo\": msg}).",
            "assert reply[\"echo\"][\"n\"] == i — order AND integrity: TCP guarantees order, framing guarantees boundaries; together every dict survives."
          ]
        }
      ],
      pitfalls: [
        "Using a delimiter (like \\n) instead of a length prefix — breaks the moment a message CONTAINS the delimiter.",
        "Reading the header with a bare recv(10) — it may return 3 bytes. EVERY exact-size read goes through recv_all.",
        "Mixing raw send() calls with protocol messages on the same socket — one stray raw send desyncs the stream permanently.",
        "Forgetting that json.loads needs the WHOLE payload — half a JSON string is a ValueError."
      ],
      verify: [
        "Run the merge test: all 100 intact.",
        "Kill the client mid-run — the server's recv_msg returns None and it exits the inner loop without a traceback.",
        "Manually check: len header of a 42-byte payload prints as b'0000000042'."
      ]
    },
    hints: [
      "Length-prefix each message — a fixed-width header carrying the byte count.",
      "Fixed-width header (e.g. 10 chars, zero-padded) = the byte count of the JSON that follows.",
      "OUTLINE: send = zfilled_len(json)+json; recv = read exactly 10 bytes → int → read exactly that many → json.loads. recv_all(n) loops until it has n bytes."
    ],
    reflection: "Why is 'read exactly N bytes' a loop and not a single recv() call?"
  },
  {
    id: "cs3", name: "3 · Multi-client server",
    goal: "Many clients connected at once, each handled independently.",
    designQuestions: [
      "If accept() and recv() block, how can one server serve two clients at the same time?",
      "What shared state do multiple clients touch, and what could go wrong when two touch it at once?",
      "Why daemon threads?"
    ],
    libs: ["threading"],
    lesson: {
      intro: "Your echo server is single-client: while it's blocked in recv() for client A, client B's accept() never happens. The fix in this project is thread-per-client: the main thread does nothing but accept(), and every accepted connection gets its own thread running handle_client(). Threads share memory, which is both the superpower (a shared registry of who's online) and the danger (two threads mutating one dict mid-iteration). Rule: every touch of shared state goes inside a Lock.",
      requirements: [
        "Server keeps accepting while any number of clients are connected and chatting.",
        "Each client is handled by its own thread running one function: handle_client(conn, addr).",
        "A shared clients dict exists (it becomes username→conn in milestone 5), guarded by a threading.Lock.",
        "A client disconnecting (cleanly or by crash) ends ONLY its own thread; everyone else keeps working.",
        "Ctrl+C still kills the whole server (threads are daemon=True)."
      ],
      steps: [
        {
          title: "server.py — restructured for threads",
          teach: "The main loop shrinks to accept-and-spawn. All per-client logic lives in handle_client, which runs simultaneously in as many threads as there are clients. The try/finally guarantees the socket closes and (later) the user is removed from the registry no matter HOW the thread dies.",
          code: "import socket\nimport threading\nimport protocol\n\nHOST, PORT = \"127.0.0.1\", 5050\n\nclients = {}                     # shared: filled with username -> conn in milestone 5\nclients_lock = threading.Lock()  # EVERY read/write of `clients` holds this\n\n\ndef handle_client(conn, addr):\n    \"\"\"Runs in its own thread — one instance per connected client.\"\"\"\n    print(\"connected:\", addr)\n    try:\n        while True:\n            msg = protocol.recv_msg(conn)\n            if msg is None:              # client left\n                break\n            print(addr, \"->\", msg)\n            protocol.send_msg(conn, {\"status\": \"ok\", \"echo\": msg})\n    except ConnectionResetError:\n        pass                             # client crashed instead of closing — same outcome\n    finally:\n        conn.close()\n        print(\"disconnected:\", addr)\n\n\ndef main():\n    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n    server.bind((HOST, PORT))\n    server.listen()\n    print(f\"listening on {HOST}:{PORT}\")\n    while True:\n        conn, addr = server.accept()\n        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)\n        t.start()\n\n\nif __name__ == \"__main__\":\n    main()",
          lines: [
            "threading.Thread(target=handle_client, args=(conn, addr)) — target is the FUNCTION (no parentheses!), args the tuple it's called with. handle_client(conn, addr) with parens would run it in the MAIN thread and block forever.",
            "daemon=True — daemon threads die with the main thread, so Ctrl+C actually stops the server instead of hanging on live client threads.",
            "clients_lock — 'with clients_lock:' around every access. Python dicts aren't safe to mutate while another thread iterates them.",
            "except ConnectionResetError — a crashed client (killed process, dropped Wi-Fi) raises this instead of returning b\"\". Treat it as a normal goodbye.",
            "finally: conn.close() — runs on clean exit, on crash, on anything. In milestone 5 the 'remove me from clients' line joins it."
          ]
        },
        {
          title: "The race condition you're defending against",
          teach: "Concurrency bugs don't crash reliably — they corrupt rarely, which is worse. Here is the exact pattern the lock prevents, so you know WHY it's there, not just that it is.",
          code: "# WITHOUT the lock — two threads, interleaved by the OS at any point:\n#   Thread A (broadcast):        Thread B (client disconnects):\n#   for user, c in clients.items():\n#                                 del clients[\"dana\"]      # dict changed size!\n#   -> RuntimeError: dictionary changed size during iteration\n#\n# WITH the lock — B waits until A's loop finishes:\nwith clients_lock:\n    targets = list(clients.values())   # snapshot inside the lock\nfor c in targets:                       # long work OUTSIDE the lock\n    protocol.send_msg(c, {\"info\": \"...\"})",
          lines: [
            "Snapshot-then-work: hold the lock only long enough to COPY what you need, then do slow sends outside it — or one slow client stalls every other thread.",
            "This exact pattern (snapshot targets, send outside) is your broadcast implementation in milestone 5."
          ]
        }
      ],
      pitfalls: [
        "Thread(target=handle_client(conn, addr)) — calling instead of passing. The server 'works' for one client and mysteriously never accepts a second.",
        "Doing network sends while holding the lock — one slow/frozen client blocks the entire server.",
        "Forgetting daemon=True and wondering why Ctrl+C doesn't exit.",
        "Sharing ONE sqlite connection across threads (next milestone): sqlite3 objects are per-thread — open a connection inside each function call instead."
      ],
      verify: [
        "Open THREE client terminals at once — all three connect and each gets its own echoes.",
        "Kill one client mid-conversation — the other two keep working; server prints one 'disconnected'.",
        "Ctrl+C on the server exits immediately."
      ]
    },
    hints: [
      "Thread-per-client: accept in a loop, hand each conn to a new thread.",
      "Thread(target=handle_client, args=(conn,)).start() — target without parentheses.",
      "OUTLINE: loop: conn=accept() → Thread(target=handle_client, args=(conn,), daemon=True).start(). Guard the shared clients dict with a Lock."
    ],
    reflection: "Name one bug that can ONLY happen with concurrency that can't happen with one client."
  },
  {
    id: "cs4", name: "4 · Registration & Auth (SQLite)",
    goal: "Sign-up + login backed by a database, with passwords that are never stored in plaintext.",
    designQuestions: [
      "What columns does a users table need? What must be UNIQUE?",
      "Why is storing the raw password a failure even on a LAN project? What do you store instead?",
      "What does a salt defend against?"
    ],
    libs: ["sqlite3", "hashlib"],
    lesson: {
      intro: "SQLite is a full SQL database living in one file (app.db) — no install, no service, import sqlite3 and go. The security rule of this milestone: the database NEVER contains a password. It contains a HASH — a one-way fingerprint (SHA-256 here). You verify a login by hashing the attempt the same way and comparing fingerprints. The salt (random per-user string mixed in before hashing) makes two identical passwords produce different hashes, which kills precomputed 'rainbow table' lookups and cross-user comparisons.",
      requirements: [
        "db.py module with: setup(), register(username, password) → bool, login(username, password) → bool.",
        "users table: id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, pw_hash TEXT NOT NULL, salt TEXT NOT NULL.",
        "register hashes sha256(salt + password), stores hash + salt, returns False (not a crash) for a taken username.",
        "login re-hashes the attempt with the STORED salt and compares — no hash ever 'decrypted'.",
        "ALL SQL uses ? parameters. Zero f-strings in SQL — that's the SQL-injection door.",
        "The server understands two new protocol commands: {\"command\": \"register\"|\"login\", \"username\": ..., \"password\": ...} and answers {\"status\": \"ok\"} or {\"status\": \"error\", \"reason\": ...}."
      ],
      steps: [
        {
          title: "db.py — the whole file",
          teach: "Connections are opened per call, not shared — sqlite3 connections can't hop threads, and your server IS multithreaded now. Opening per operation is cheap at this scale and makes the module thread-safe by construction.",
          code: "import hashlib\nimport secrets\nimport sqlite3\n\nDB = \"app.db\"\n\n\ndef _connect():\n    return sqlite3.connect(DB)\n\n\ndef setup():\n    \"\"\"Create the users table once. Safe to call every server start.\"\"\"\n    con = _connect()\n    con.execute(\"\"\"CREATE TABLE IF NOT EXISTS users(\n        id       INTEGER PRIMARY KEY AUTOINCREMENT,\n        username TEXT UNIQUE NOT NULL,\n        pw_hash  TEXT NOT NULL,\n        salt     TEXT NOT NULL)\"\"\")\n    con.commit()\n    con.close()\n\n\ndef _hash(password, salt):\n    return hashlib.sha256((salt + password).encode(\"utf-8\")).hexdigest()\n\n\ndef register(username, password):\n    \"\"\"True on success, False if the username is taken.\"\"\"\n    salt = secrets.token_hex(16)          # 32 hex chars of real randomness\n    con = _connect()\n    try:\n        con.execute(\"INSERT INTO users(username, pw_hash, salt) VALUES(?, ?, ?)\",\n                    (username, _hash(password, salt), salt))\n        con.commit()\n        return True\n    except sqlite3.IntegrityError:        # UNIQUE(username) violated\n        return False\n    finally:\n        con.close()\n\n\ndef login(username, password):\n    \"\"\"True only if the username exists AND the password matches.\"\"\"\n    con = _connect()\n    row = con.execute(\"SELECT pw_hash, salt FROM users WHERE username = ?\",\n                      (username,)).fetchone()\n    con.close()\n    if row is None:\n        return False\n    pw_hash, salt = row\n    return _hash(password, salt) == pw_hash",
          lines: [
            "CREATE TABLE IF NOT EXISTS — idempotent setup; the server just calls setup() on boot.",
            "username TEXT UNIQUE — the DATABASE enforces no duplicates; register() catches IntegrityError instead of racing a check-then-insert.",
            "secrets.token_hex(16) — cryptographic randomness for the salt. random module is NOT for security.",
            "_hash(salt + password) — same recipe at register and login; the stored salt is read back so the comparison lines up.",
            "execute(sql, (username,)) — the ? placeholder + params tuple. sqlite escapes the value; injection like username = \"x'; DROP TABLE users;--\" becomes just a weird literal string.",
            "(username,) — one-element tuple needs the comma. (username) is just parentheses."
          ]
        },
        {
          title: "Wiring auth into handle_client",
          teach: "Your protocol carries dicts, so auth is just two new command handlers. The pattern below — read a msg, switch on msg[\"command\"], answer with a status dict — is the server's shape for EVERY later feature.",
          code: "# inside handle_client(conn, addr), replacing the echo loop:\nusername = None                          # set once this client logs in\nwhile True:\n    msg = protocol.recv_msg(conn)\n    if msg is None:\n        break\n    cmd = msg.get(\"command\")\n\n    if cmd == \"register\":\n        ok = db.register(msg.get(\"username\", \"\"), msg.get(\"password\", \"\"))\n        protocol.send_msg(conn, {\"status\": \"ok\"} if ok else\n                          {\"status\": \"error\", \"reason\": \"username taken\"})\n\n    elif cmd == \"login\":\n        if db.login(msg.get(\"username\", \"\"), msg.get(\"password\", \"\")):\n            username = msg[\"username\"]\n            protocol.send_msg(conn, {\"status\": \"ok\"})\n        else:\n            protocol.send_msg(conn, {\"status\": \"error\", \"reason\": \"bad credentials\"})\n\n    elif username is None:               # everything else requires a login first\n        protocol.send_msg(conn, {\"status\": \"error\", \"reason\": \"log in first\"})\n\n    else:\n        protocol.send_msg(conn, {\"status\": \"error\", \"reason\": \"unknown command\"})",
          lines: [
            "msg.get(\"command\") — .get() instead of [\"command\"]: a malformed message returns None instead of crashing the thread.",
            "username = None gate — one variable makes 'must be logged in' checks trivial for every later command.",
            "Every branch answers with a status dict — the client can always recv_msg exactly once per request. Request/response symmetry keeps the client simple."
          ]
        }
      ],
      pitfalls: [
        "f\"SELECT ... WHERE username='{username}'\" — SQL injection. The ? placeholder is not optional.",
        "One global sqlite connection shared by all threads — sqlite3.ProgrammingError: objects created in a thread can only be used in that same thread.",
        "Forgetting con.commit() after INSERT — the row silently never lands.",
        "Storing the password 'temporarily, will hash later' — later never comes. Hash from the first commit.",
        "Comparing hashes with 'in' or startswith instead of == (yes, it happens)."
      ],
      verify: [
        "register('itamar', 'pass1') → True; second register('itamar', ...) → False, no crash.",
        "login('itamar', 'pass1') → True; login('itamar', 'wrong') → False; login('ghost', 'x') → False.",
        "Open app.db (DB Browser for SQLite or sqlite3 CLI): the pw_hash column is 64 hex chars, and the raw password appears NOWHERE.",
        "Two users with the SAME password have DIFFERENT hashes (salt working)."
      ]
    },
    hints: [
      "Store a hash, never the password. On login, hash the attempt and compare.",
      "Use a per-user salt so identical passwords don't produce identical hashes.",
      "OUTLINE: CREATE TABLE users(id, username UNIQUE, pw_hash, salt). register → salt=secrets.token_hex, hash(salt+pw), INSERT. login → SELECT by username, re-hash attempt with stored salt, compare."
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
    lesson: {
      intro: "This is where the clients dict earns its keep. The moment a login succeeds, the server records username → conn. Now 'send to dana' is a dict lookup, and 'send to everyone' is a loop over the values. All messages RELAY through the server — clients never talk directly to each other for text. That's deliberate: the server is the one place that knows who's online, and clients behind different machines don't need to accept incoming connections at all.",
      requirements: [
        "On successful login: clients[username] = conn (inside the lock). On ANY disconnect: removed (in the finally).",
        "A second login for an already-online username is rejected: {\"status\": \"error\", \"reason\": \"already logged in\"}.",
        "{\"command\": \"msg\", \"text\": ...} → delivered to every OTHER online user as {\"event\": \"msg\", \"from\": sender, \"text\": ...}.",
        "{\"command\": \"msg\", \"to\": \"dana\", \"text\": ...} → delivered only to dana; sender gets {\"status\": \"error\", \"reason\": \"user offline\"} if she isn't there.",
        "{\"command\": \"who\"} → {\"status\": \"ok\", \"users\": [...]} — the online list.",
        "A client that is mid-recv on its own request never receives someone else's broadcast as its 'response' — see the events note in the GUI milestone (7): requests get \"status\" replies, pushed messages arrive as \"event\" dicts."
      ],
      steps: [
        {
          title: "Registry in, registry out",
          teach: "Two edits to what you already have: record the user at login, remove them in the finally. The finally is the crucial half — a crashed client that stays in the dict becomes a ghost that everyone's broadcasts crash into.",
          code: "# login success branch becomes:\nwith clients_lock:\n    if msg[\"username\"] in clients:\n        protocol.send_msg(conn, {\"status\": \"error\", \"reason\": \"already logged in\"})\n        continue\n    username = msg[\"username\"]\n    clients[username] = conn\nprotocol.send_msg(conn, {\"status\": \"ok\"})\n\n# and handle_client's finally grows one block:\nfinally:\n    if username is not None:\n        with clients_lock:\n            clients.pop(username, None)\n    conn.close()",
          lines: [
            "The duplicate check and the insert happen inside ONE lock hold — check-then-set across two lock acquisitions would let two 'dana's race in between.",
            "clients.pop(username, None) — pop with a default never raises, even if the user somehow was never registered."
          ]
        },
        {
          title: "Broadcast and private delivery",
          teach: "Snapshot inside the lock, send outside it (the milestone-3 pattern, now for real). Private is even simpler: one lookup. Both wrap the outgoing text in an \"event\" dict so receivers can tell pushed chat apart from replies to their own requests.",
          code: "elif cmd == \"msg\":\n    text = str(msg.get(\"text\", \"\"))[:2000]      # cap length; never trust input\n    to = msg.get(\"to\")\n    if to:                                       # ---- private ----\n        with clients_lock:\n            target = clients.get(to)\n        if target is None:\n            protocol.send_msg(conn, {\"status\": \"error\", \"reason\": \"user offline\"})\n        else:\n            protocol.send_msg(target, {\"event\": \"msg\", \"from\": username,\n                                       \"to\": to, \"text\": text})\n            protocol.send_msg(conn, {\"status\": \"ok\"})\n    else:                                        # ---- broadcast ----\n        with clients_lock:\n            targets = [(u, c) for u, c in clients.items() if u != username]\n        for _, c in targets:\n            try:\n                protocol.send_msg(c, {\"event\": \"msg\", \"from\": username, \"text\": text})\n            except OSError:\n                pass                             # dying socket — its own thread cleans it up\n        protocol.send_msg(conn, {\"status\": \"ok\"})\n\nelif cmd == \"who\":\n    with clients_lock:\n        users = sorted(clients)\n    protocol.send_msg(conn, {\"status\": \"ok\", \"users\": users})",
          lines: [
            "\"event\" vs \"status\" — REPLIES to your requests carry status; PUSHED messages carry event. This one convention is what keeps the GUI's reader thread sane in milestone 7.",
            "targets snapshot — the lock is held for a list comprehension, not for N network sends.",
            "except OSError: pass — sending to a half-dead socket raises; the owner thread's recv will fail too and do the real cleanup. Don't clean up someone else's state here.",
            "[:2000] — every string a client sends gets a sanity cap before it's relayed."
          ]
        }
      ],
      pitfalls: [
        "Forgetting the finally-removal — ghosts accumulate and broadcast crashes with OSError on dead sockets.",
        "Sending inside the lock — one frozen client freezes all chat.",
        "Letting a client send {\"from\": \"someone_else\"} — the SERVER stamps from=username; never relay a client-claimed identity.",
        "Two sockets for one username overwriting each other in the dict — hence the already-logged-in rejection."
      ],
      verify: [
        "Three logged-in clients: a broadcast from A appears at B and C, not back at A.",
        "A private A→B appears only at B.",
        "A private to an offline name returns the error to the sender.",
        "Kill B mid-chat; A's next broadcast still reaches C, and 'who' no longer lists B."
      ]
    },
    hints: [
      "Keep a mapping username → connection once a client authenticates.",
      "Broadcast = iterate a snapshot of connections; private = one dict lookup.",
      "OUTLINE: on 'msg' with a 'to': if to in clients → send there, else error to sender. Remove from the dict in the handler's finally."
    ],
    reflection: "Why is routing through the server (relay) simpler on a LAN than direct client-to-client for TEXT?"
  },
  {
    id: "cs6", name: "6 · File transfer",
    goal: "Send a file between users through your protocol.",
    designQuestions: [
      "Your protocol carries JSON text. How do you put raw bytes (an image) inside a JSON message?",
      "How will the receiver know the filename and size?",
      "Why must the receiver never trust the sender's filename as a path?"
    ],
    libs: ["json", "os"],
    lesson: {
      intro: "JSON can't carry raw bytes — but it carries strings fine, and base64 is the standard way to write bytes AS text: every 3 bytes become 4 safe characters (a 33% size tax). So a file message is just a bigger chat message: filename + size + base64 data, framed by the same protocol.py as everything else. The receiver's #1 job is DISTRUST: the 'filename' arriving from the network is attacker-controlled input — strip it to a bare name before using it in a path, or a peer can write to ..\\..\\startup\\evil.exe.",
      requirements: [
        "{\"command\": \"file\", \"to\": user, \"name\": ..., \"size\": ..., \"data\": base64} — private-only (files always have one recipient).",
        "Server relays it as {\"event\": \"file\", \"from\": sender, \"name\": ..., \"size\": ..., \"data\": ...} after checking the recipient is online and the size is sane.",
        "Server rejects files over 10 MB with a clear error (LAN + base64 + one message = keep it bounded).",
        "Receiver saves into a downloads/ folder it creates, using ONLY os.path.basename(name), and verifies the decoded size matches \"size\".",
        "A received file opens correctly afterwards (send a real image, not just .txt)."
      ],
      steps: [
        {
          title: "Sender side (client)",
          teach: "Read bytes, encode, send. base64.b64encode returns BYTES of the encoded form, so it needs one more .decode('ascii') to become the JSON-safe string.",
          code: "import base64\nimport os\n\n\ndef send_file(sock, to, path):\n    \"\"\"Read a local file and push it through the protocol to `to`.\"\"\"\n    size = os.path.getsize(path)\n    if size > 10 * 1024 * 1024:\n        raise ValueError(\"file too big for one message (10 MB cap)\")\n    with open(path, \"rb\") as f:                    # rb: bytes, not text\n        raw = f.read()\n    protocol.send_msg(sock, {\n        \"command\": \"file\",\n        \"to\": to,\n        \"name\": os.path.basename(path),            # send a bare name, not your disk layout\n        \"size\": size,\n        \"data\": base64.b64encode(raw).decode(\"ascii\"),\n    })",
          lines: [
            "open(path, 'rb') — 'b' matters: text mode would mangle image bytes on Windows (\\r\\n translation).",
            "b64encode(raw).decode('ascii') — bytes → base64-bytes → str. The str is what JSON can hold.",
            "size travels separately so the receiver can verify the decode round-tripped completely."
          ]
        },
        {
          title: "Receiver side (client) + the server relay",
          teach: "The server branch is five lines — check online, check size, restamp from, relay. The receiver decodes and writes, sanitizing the name first.",
          code: "# --- server: inside the command switch ---\nelif cmd == \"file\":\n    to = msg.get(\"to\")\n    if not isinstance(msg.get(\"size\"), int) or msg[\"size\"] > 10 * 1024 * 1024:\n        protocol.send_msg(conn, {\"status\": \"error\", \"reason\": \"bad size\"})\n        continue\n    with clients_lock:\n        target = clients.get(to)\n    if target is None:\n        protocol.send_msg(conn, {\"status\": \"error\", \"reason\": \"user offline\"})\n    else:\n        protocol.send_msg(target, {\"event\": \"file\", \"from\": username,\n                                   \"name\": msg.get(\"name\", \"file\"),\n                                   \"size\": msg[\"size\"], \"data\": msg.get(\"data\", \"\")})\n        protocol.send_msg(conn, {\"status\": \"ok\"})\n\n# --- client: when an {\"event\": \"file\"} dict arrives ---\nimport base64, os\n\ndef save_file(evt):\n    os.makedirs(\"downloads\", exist_ok=True)\n    name = os.path.basename(evt.get(\"name\", \"file\"))     # kills ../../ tricks\n    raw = base64.b64decode(evt.get(\"data\", \"\"))\n    if len(raw) != evt.get(\"size\"):\n        print(\"size mismatch — transfer corrupted, discarding\")\n        return None\n    path = os.path.join(\"downloads\", name)\n    with open(path, \"wb\") as f:\n        f.write(raw)\n    print(f\"received {name} ({len(raw)} bytes) -> {path}\")\n    return path",
          lines: [
            "os.path.basename('..\\\\..\\\\evil.exe') → 'evil.exe' — the single call that turns a path-traversal attack into a harmless filename.",
            "len(raw) != size — cheap integrity check; catches truncated/corrupted transfers before you save garbage.",
            "makedirs(exist_ok=True) — creates downloads/ on first use, no error the second time.",
            "The server never decodes the data — it relays the string untouched. Only the endpoints pay the decode cost."
          ]
        }
      ],
      pitfalls: [
        "Forgetting .decode('ascii') after b64encode → 'Object of type bytes is not JSON serializable'.",
        "Opening files in text mode ('r'/'w') instead of binary ('rb'/'wb') — corrupts every non-text file.",
        "Trusting msg['name'] as a full path — directory traversal. basename() ALWAYS.",
        "No size cap: one 2 GB send balloons +33% in base64 and stalls the whole server thread."
      ],
      verify: [
        "Send a real .png between two clients — it opens in a viewer afterwards.",
        "Send to an offline user → clean error at the sender.",
        "Craft a message with name='..\\\\evil.txt' — the file lands INSIDE downloads/ as evil.txt.",
        "A file just over 10 MB is rejected with 'bad size'."
      ]
    },
    hints: [
      "Bytes don't fit in JSON — base64-encode to text, decode on arrival.",
      "Include metadata: filename + size, then the data field.",
      "OUTLINE: read rb → b64encode → {command:'file', name, size, data} → receiver b64decodes, basename()s the name, writes wb into downloads/."
    ],
    reflection: "What's the cost of base64 (hint: size), and when would chunking matter?"
  },
  {
    id: "cs7", name: "7 · GUI (built on a clean client API)",
    goal: "A desktop UI over your client. AI may style it — but the wiring is yours and you can explain every line.",
    designQuestions: [
      "What does the GUI actually need from your client layer — which functions does it call?",
      "The GUI runs an event loop; your networking also loops. How do you keep the UI from freezing?",
      "Why must a background thread never touch widgets directly?"
    ],
    libs: ["customtkinter", "threading"],
    lesson: {
      intro: "The mistake that sinks GUI milestones is wiring sockets directly into button callbacks. Instead you build a SEAM: a ChatClient class that owns the socket and exposes login(), send_chat(), send_file() — plus a background reader thread that turns pushed \"event\" dicts into a callback. The GUI then knows nothing about sockets, and the AI can style widgets all it wants without touching networking. Two golden rules: (1) the UI thread never blocks on the network, (2) the network thread never touches a widget — it hands data to the UI thread via .after().",
      requirements: [
        "client.py: a ChatClient class — connect/login/register/send_chat/send_file/who; NO tkinter imports in it.",
        "One background reader thread that dispatches: \"event\" dicts → an on_event callback; \"status\" dicts → the reply queue for the request that's waiting.",
        "GUI: login screen → chat screen; messages list, entry box + Send, online-users sidebar (who), file-send button.",
        "The window NEVER freezes: every server call from a callback finishes fast, and pushed events repaint via .after().",
        "You can point at the exact line where a button click becomes a network send, and where a network event becomes a widget update."
      ],
      steps: [
        {
          title: "client.py — the seam (the part that matters)",
          teach: "One socket, two kinds of traffic: replies to YOUR requests (status dicts) and pushed events (someone chatted). The reader thread receives EVERYTHING and sorts: events go to the callback, replies go into a Queue that the request method is blocking on. A Queue is thread-safe by design — it's the standard hand-off between threads.",
          code: "import queue\nimport socket\nimport threading\nimport protocol\n\n\nclass ChatClient:\n    def __init__(self, host, port, on_event):\n        \"\"\"on_event(dict) is called (from the READER thread!) for every pushed event.\"\"\"\n        self.on_event = on_event\n        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n        self.sock.connect((host, port))\n        self.replies = queue.Queue()\n        threading.Thread(target=self._reader, daemon=True).start()\n\n    def _reader(self):\n        \"\"\"The only place that ever recv()s. Sorts pushed events from request replies.\"\"\"\n        while True:\n            msg = protocol.recv_msg(self.sock)\n            if msg is None:\n                self.on_event({\"event\": \"disconnected\"})\n                return\n            if \"event\" in msg:\n                self.on_event(msg)          # pushed: chat, files, call signals\n            else:\n                self.replies.put(msg)       # reply to whatever request is waiting\n\n    def _request(self, obj, timeout=5):\n        protocol.send_msg(self.sock, obj)\n        return self.replies.get(timeout=timeout)   # blocks THIS caller only\n\n    # ---- the API the GUI calls ----\n    def register(self, user, pw):\n        return self._request({\"command\": \"register\", \"username\": user, \"password\": pw})\n\n    def login(self, user, pw):\n        return self._request({\"command\": \"login\", \"username\": user, \"password\": pw})\n\n    def send_chat(self, text, to=None):\n        m = {\"command\": \"msg\", \"text\": text}\n        if to:\n            m[\"to\"] = to\n        return self._request(m)\n\n    def who(self):\n        return self._request({\"command\": \"who\"})",
          lines: [
            "queue.Queue() — thread-safe FIFO. The reader puts replies in; _request blocks on .get(). No lock needed; Queue IS the synchronization.",
            "\"event\" in msg — the convention from milestone 5 doing its job: one if statement splits pushed traffic from replies.",
            "on_event fires FROM THE READER THREAD — the GUI must trampoline it to the UI thread (next step). The client stays tkinter-free.",
            "_request(...).get(timeout=5) — a dead server raises queue.Empty after 5s instead of hanging the app forever."
          ]
        },
        {
          title: "gui.py — the wiring skeleton (style it however you want)",
          teach: "tkinter/customtkinter widgets may only be touched by the thread running mainloop(). The bridge is window.after(0, fn): callable from any thread, it schedules fn to run on the UI thread. Your on_event handler is literally one line of trampoline.",
          code: "import customtkinter as ctk\nfrom client import ChatClient\n\n\nclass App(ctk.CTk):\n    def __init__(self):\n        super().__init__()\n        self.title(\"Local-CyberComm\")\n        self.geometry(\"720x480\")\n        # networking: events arrive on the reader thread -> trampoline to UI thread\n        self.client = ChatClient(\"127.0.0.1\", 5050,\n                                 on_event=lambda e: self.after(0, self.handle_event, e))\n        self.messages = ctk.CTkTextbox(self, state=\"disabled\")\n        self.messages.pack(fill=\"both\", expand=True, padx=10, pady=10)\n        self.entry = ctk.CTkEntry(self, placeholder_text=\"message…\")\n        self.entry.pack(side=\"left\", fill=\"x\", expand=True, padx=(10, 4), pady=(0, 10))\n        self.entry.bind(\"<Return>\", self.on_send)\n        ctk.CTkButton(self, text=\"Send\", command=self.on_send).pack(\n            side=\"left\", padx=(4, 10), pady=(0, 10))\n\n    def on_send(self, _ev=None):\n        \"\"\"UI thread. THE line where a click becomes a network send:\"\"\"\n        text = self.entry.get().strip()\n        if not text:\n            return\n        self.client.send_chat(text)          # fast round-trip to the server\n        self.entry.delete(0, \"end\")\n        self.show(\"me\", text)\n\n    def handle_event(self, e):\n        \"\"\"UI thread (thanks to .after). THE line where an event becomes pixels:\"\"\"\n        if e.get(\"event\") == \"msg\":\n            self.show(e[\"from\"], e[\"text\"])\n        elif e.get(\"event\") == \"disconnected\":\n            self.show(\"system\", \"connection lost\")\n\n    def show(self, who, text):\n        self.messages.configure(state=\"normal\")\n        self.messages.insert(\"end\", f\"{who}: {text}\\n\")\n        self.messages.configure(state=\"disabled\")\n        self.messages.see(\"end\")\n\n\nApp().mainloop()",
          lines: [
            "lambda e: self.after(0, self.handle_event, e) — the entire threading story of the GUI in one line: reader thread calls it, .after moves handle_event onto the UI thread.",
            "send_chat inside on_send — it blocks for ONE quick server round-trip (~1 ms on LAN). Fine. Anything slow (a big file) belongs in threading.Thread(target=...).",
            "state='disabled' textbox toggled around insert — a read-only log the user can't type into.",
            "Login screen: same pattern — a frame with two entries; login button calls self.client.login(...), checks reply[\"status\"], swaps frames on ok. Build it yourself; the AI may style it."
          ]
        }
      ],
      pitfalls: [
        "Calling widget methods from the reader thread — random crashes/freezes that appear 'sometimes'. ALWAYS .after().",
        "recv() inside a button callback — freezes the UI until a message happens to arrive.",
        "Letting the AI generate one 400-line blob of GUI+sockets — you can't explain it and can't debug it. The seam is non-negotiable.",
        "Two places recv()ing the same socket (a callback AND the reader) — messages vanish into the wrong reader. The reader thread is the ONLY recv."
      ],
      verify: [
        "Two GUI clients chatting: messages appear instantly on both, window never freezes (drag it around mid-chat).",
        "Kill the server: both GUIs show 'connection lost' instead of hanging or crashing.",
        "Explain-back test: point at the exact line where click→send and event→pixels happen. If you can't, re-read the seam."
      ]
    },
    hints: [
      "Networking OFF the UI thread — a reader thread hands events to the UI via after().",
      "Design the seam first: the GUI calls clean client functions (login(), send_chat()), never raw sockets.",
      "OUTLINE: ChatClient(reader thread + Queue for replies) → GUI trampolines on_event with self.after(0, ...). Requests = status dicts; pushes = event dicts."
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
    lesson: {
      intro: "WebRTC splits a call into two problems. SIGNALING: the peers must exchange two blobs of text — an SDP offer/answer ('here are my codecs and formats') and ICE candidates ('here are IP:port pairs where you can reach me') — over ANY channel you already have. Your chat server IS that channel: call setup is just two new relayed message types. MEDIA: once both sides have each other's SDP+ICE, aiortc opens a direct UDP flow between the two machines — audio never touches your server. On a LAN, ICE finds the direct route immediately (no STUN/TURN servers needed), which is why this project is the perfect place to learn it.",
      requirements: [
        "Two new relayed events using the milestone-5 relay pattern: {\"command\": \"call-offer\", \"to\": user, \"sdp\": ..., \"type\": ...} and {\"command\": \"call-answer\", \"to\": user, \"sdp\": ..., \"type\": ...}.",
        "The server treats them EXACTLY like private messages — restamp from, relay, offline error. No SDP parsing server-side.",
        "Caller flow: create RTCPeerConnection → add mic track → createOffer → setLocalDescription → send offer through the chat protocol.",
        "Callee flow: receive offer → setRemoteDescription → add own mic track → createAnswer → setLocalDescription → send answer back.",
        "Proof of life: a voice call between two machines on your LAN where each side hears the other (start with audio only; video is the same pattern with a camera track).",
        "You can draw the box diagram: which arrows go through YOUR server (SDP), which are direct UDP (media)."
      ],
      steps: [
        {
          title: "Server side: two relay branches (that's all)",
          teach: "Signaling doesn't need new machinery — it's the private-message relay with different command names. Notice the server understands NOTHING about SDP; it moves opaque text between two users.",
          code: "elif cmd in (\"call-offer\", \"call-answer\", \"call-ice\"):\n    to = msg.get(\"to\")\n    with clients_lock:\n        target = clients.get(to)\n    if target is None:\n        protocol.send_msg(conn, {\"status\": \"error\", \"reason\": \"user offline\"})\n    else:\n        relay = dict(msg)                 # copy the whole signal payload\n        relay.pop(\"command\", None)\n        relay[\"event\"] = cmd              # arrives as an event on the other side\n        relay[\"from\"] = username          # server stamps identity, as always\n        protocol.send_msg(target, relay)\n        protocol.send_msg(conn, {\"status\": \"ok\"})",
          lines: [
            "cmd in (...) — offer, answer and (if you use trickle ICE) candidate messages all share one relay branch.",
            "relay[\"from\"] = username — same identity rule as chat: the server stamps the sender, never trusts the payload.",
            "The server never json-parses the SDP text — opaque relay is the whole design."
          ]
        },
        {
          title: "Caller and callee with aiortc",
          teach: "aiortc is asyncio-based, so the call logic lives in async functions (run them on an asyncio loop in one more background thread; asyncio.run_coroutine_threadsafe is the bridge from your tkinter world). The offer/answer dance below is THE core of WebRTC — the same five calls exist letter-for-letter in browser JavaScript.",
          code: "import asyncio\nfrom aiortc import RTCPeerConnection, RTCSessionDescription\nfrom aiortc.contrib.media import MediaPlayer, MediaRecorder\n\n\nasync def start_call(client, to):\n    \"\"\"CALLER: build the offer and ship it through the chat server.\"\"\"\n    pc = RTCPeerConnection()               # the WebRTC engine for this call\n    mic = MediaPlayer(\"default\", format=\"dshow\")   # Windows mic via DirectShow\n    pc.addTrack(mic.audio)                 # what WE will transmit\n\n    @pc.on(\"track\")\n    async def on_track(track):             # what THEY transmit, once connected\n        rec = MediaRecorder(\"default\", format=\"dshow\")  # or save: MediaRecorder(\"call.wav\")\n        rec.addTrack(track)\n        await rec.start()\n\n    offer = await pc.createOffer()         # SDP text describing our side\n    await pc.setLocalDescription(offer)    # also starts LAN ICE gathering\n    await ice_complete(pc)                 # LAN: candidates arrive ~instantly\n    client.send_signal(\"call-offer\", to,   # -> through YOUR protocol\n                       sdp=pc.localDescription.sdp,\n                       type=pc.localDescription.type)\n    return pc\n\n\nasync def on_call_offer(client, evt):\n    \"\"\"CALLEE: consume the offer, answer it.\"\"\"\n    pc = RTCPeerConnection()\n    await pc.setRemoteDescription(RTCSessionDescription(evt[\"sdp\"], evt[\"type\"]))\n    mic = MediaPlayer(\"default\", format=\"dshow\")\n    pc.addTrack(mic.audio)\n    answer = await pc.createAnswer()\n    await pc.setLocalDescription(answer)\n    await ice_complete(pc)\n    client.send_signal(\"call-answer\", evt[\"from\"],\n                       sdp=pc.localDescription.sdp, type=pc.localDescription.type)\n    return pc\n\n\nasync def on_call_answer(pc, evt):\n    \"\"\"Back at the CALLER: the moment this lands, media starts flowing P2P.\"\"\"\n    await pc.setRemoteDescription(RTCSessionDescription(evt[\"sdp\"], evt[\"type\"]))\n\n\nasync def ice_complete(pc):\n    while pc.iceGatheringState != \"complete\":\n        await asyncio.sleep(0.05)",
          lines: [
            "RTCPeerConnection — one per call; it owns codecs, ICE, encryption, everything.",
            "createOffer/setLocalDescription — generate our SDP and commit to it. setLocalDescription is also what kicks off ICE gathering.",
            "ice_complete then send — the lazy-but-solid approach: wait until all LAN candidates are IN the SDP, send one complete blob, skip per-candidate 'trickle' messages entirely. On a LAN this costs milliseconds.",
            "@pc.on(\"track\") — fires when the remote side's audio starts arriving; wire it to speakers (or a .wav recorder while debugging).",
            "client.send_signal(...) — a two-line helper on ChatClient: self._request({\"command\": kind, \"to\": to, \"sdp\": sdp, \"type\": type}).",
            "The SAME pc object must receive the answer — keep it (e.g. self.active_call = pc) between offer and answer."
          ]
        }
      ],
      pitfalls: [
        "Trying to run aiortc inside tkinter's thread — it needs a live asyncio loop; give it its own thread with loop.run_forever() and feed it via run_coroutine_threadsafe.",
        "Sending the offer before ICE gathering finished (without trickle) — the SDP has no candidates and the connection never forms.",
        "Making a NEW RTCPeerConnection when the answer arrives — the answer belongs to the pc that made the offer.",
        "Debugging audio+network at once. First get offer/answer text arriving on both sides (print the first 80 chars), THEN plug in the mic.",
        "pip install aiortc needs a working build environment on Windows — install it early, not on demo day."
      ],
      verify: [
        "Milestone-5 test still passes with the new branches (signaling is 'just messages').",
        "Caller prints the callee's answer SDP (proof signaling round-trips through your server).",
        "pc.connectionState reaches 'connected' on both sides on your LAN.",
        "Talk into machine A's mic, hear it on machine B — while the SERVER shows zero media traffic (only the two SDP relays)."
      ]
    },
    hints: [
      "Your server is the SIGNALING channel: it relays SDP offers/answers between the peers. Media goes peer-to-peer.",
      "Get text + files rock-solid first so signaling is 'just another message type'.",
      "OUTLINE: A: pc.createOffer → setLocalDescription → wait ICE → relay SDP. B: setRemoteDescription → createAnswer → setLocalDescription → relay back. A: setRemoteDescription(answer) → media flows."
    ],
    reflection: "Draw the message flow of a call setup. Which parts are your code vs aiortc's?"
  }
];

// Library memory-jog cards — API surface + the gotcha. The full code now lives in each
// milestone's lesson; these stay as quick-recall drills.
export const libs = {
  socket: { name: "socket", whatFor: "Raw TCP/UDP networking.",
    keyAPI: ["socket(AF_INET, SOCK_STREAM)", "bind / listen / accept (server)", "connect (client)", "send / sendall / recv", "close"],
    gotcha: "recv(n) can return fewer than n bytes — always loop to read a full message.",
    quiz: "Which two calls are server-only, and which is client-only?" },
  threading: { name: "threading", whatFor: "Run each client handler concurrently.",
    keyAPI: ["Thread(target=, args=)", ".start() / .join()", "Lock() for shared state", "daemon threads"],
    gotcha: "Shared dict/list mutated from many threads needs a Lock or you get race conditions.",
    quiz: "When do you actually need a Lock?" },
  asyncio: { name: "asyncio", whatFor: "Single-threaded concurrency via an event loop (aiortc lives here).",
    keyAPI: ["async def / await", "asyncio.run()", "run_coroutine_threadsafe(coro, loop)", "loop.run_forever()"],
    gotcha: "One blocking call (time.sleep, blocking recv) stalls the WHOLE loop.",
    quiz: "Why can't you call a normal blocking socket.recv inside an async handler?" },
  sqlite3: { name: "sqlite3", whatFor: "Local file database for users/messages.",
    keyAPI: ["connect('app.db')", "execute(sql, params)", "fetchone / fetchall", "commit / close"],
    gotcha: "Use parameterized queries (?), never f-string SQL — that's SQL injection. And connections don't cross threads.",
    quiz: "Why is `execute(f\"... {username}\")` dangerous?" },
  json: { name: "json", whatFor: "Serialize your protocol messages.",
    keyAPI: ["dumps(obj) → str", "loads(str) → obj", "only JSON-safe types"],
    gotcha: "Raw bytes aren't JSON-serializable — encode (base64) first.",
    quiz: "Which Python types survive a dumps→loads round trip unchanged?" },
  hashlib: { name: "hashlib", whatFor: "Hash passwords for storage.",
    keyAPI: ["sha256(b'...')", ".hexdigest()", "salt from secrets.token_hex(16)", "consider bcrypt/scrypt for real apps"],
    gotcha: "A hash is one-way — you compare hashes, you never 'decrypt' them.",
    quiz: "How do you verify a login if you can't reverse the hash?" },
  customtkinter: { name: "customtkinter", whatFor: "Nicer-looking Tkinter GUI (AI may style it; you own the wiring).",
    keyAPI: ["CTk() window", "CTkFrame / CTkButton / CTkEntry / CTkTextbox", "command= callbacks", ".after(0, fn) from other threads", "mainloop()"],
    gotcha: "Widgets belong to the mainloop thread — background threads hand off with .after().",
    quiz: "What freezes the UI, and how do you avoid it?" },
  aiortc: { name: "aiortc", whatFor: "WebRTC (audio/video) in Python.",
    keyAPI: ["RTCPeerConnection", "createOffer / createAnswer (SDP)", "setLocal/RemoteDescription", "@pc.on('track')", "MediaPlayer / MediaRecorder"],
    gotcha: "aiortc is async — it needs a running asyncio loop; your server only relays SDP.",
    quiz: "Does the call audio travel through your TCP server? Why/why not?" },
  os: { name: "os / base64", whatFor: "Files on disk + bytes-as-text for the protocol.",
    keyAPI: ["os.path.basename / getsize / join", "os.makedirs(exist_ok=True)", "open(path,'rb'/'wb')", "base64.b64encode / b64decode"],
    gotcha: "NEVER trust a received filename as a path — basename() it first.",
    quiz: "What attack does basename() on a received filename prevent?" }
};
