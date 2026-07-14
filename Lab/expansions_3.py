# expansions_3.py — deep-dive expansions for Lab lessons (tracks: cyber_high, cyber_low, dsa).
# Rendered by lockin_lab.py after the lesson body. Pure data.
EXPANSIONS = {
    "cyber_high:0": {
        "title_check": "The layers",
        "sections": [
            {"h": "Why the OSI Model Matters for Defense", "body": "The 7-layer model isn't just theory—it's a threat map. Attackers exploit gaps between layers: L4 UDP floods bypass TCP's flow control entirely, L5+ application flaws hide inside encrypted sessions. Understanding layer boundaries helps you recognize where defenses must live: rate-limiting at L3, payload inspection at L7. The IDF cyber doctrine treats each layer as a potential attack surface. Modern defense-in-depth strategies stack controls across multiple layers to ensure that bypassing one doesn't compromise the whole system."},
            {"h": "Real-World Complexity", "body": "Real traffic rarely fits cleanly. TCP retransmissions look like attacks without context (L4 behavior informing L3 decisions). Firewalls often collapse multiple layers—they inspect packet headers (L3), connection state (L4), and even peek at L7 payloads. The key insight: the OSI model is a mental framework, not a rigid law. Different protocols and hardware implementations blur the boundaries."},
        ],
        "links": [
            {"label": "Cloudflare - OSI Model Explained", "url": "https://www.cloudflare.com/learning/ddos/glossary/open-systems-interconnection-model-osi/"},
            {"label": "Wikipedia - OSI model", "url": "https://en.wikipedia.org/wiki/OSI_model"},
        ],
    },
    "cyber_high:1": {
        "title_check": "TCP vs UDP & the handshake",
        "sections": [
            {"h": "Attack Surface & Handshake Vulnerabilities", "body": "TCP's three-way handshake (SYN, SYN-ACK, ACK) creates an opportunity window. SYN floods send millions of SYN packets without completing the handshake, exhausting server memory—this is why syn-cookies and connection rate-limiting are critical IDF monitoring techniques. UDP has no handshake, so it's faster but offers no guarantee of delivery or order. Attackers often weaponize UDP for amplification attacks (DNS, NTP) because responses are sent before the attacker's IP is even verified."},
            {"h": "Protocol Choice in Cyber Defense", "body": "Gaming and VoIP use UDP because real-time delivery matters more than perfect reliability. Banking uses TCP's guaranteed order. In cyber operations, understanding which protocol a command-and-control server uses tells you how urgently it retransmits—TCP's exponential backoff hints at covert channels; constant UDP flooding suggests brute force."},
        ],
        "links": [
            {"label": "Cloudflare - TCP vs UDP", "url": "https://www.cloudflare.com/learning/ddos/glossary/tcp-udp/"},
            {"label": "OWASP - SYN Flood Attacks", "url": "https://owasp.org/"},
        ],
    },
    "cyber_high:2": {
        "title_check": "Open a website — the full trace",
        "sections": [
            {"h": "Full End-to-End Flow & Monitoring Points", "body": "When you type a URL, the system queries DNS (UDP, L4) to resolve the domain—this is your first vulnerability window (DNS spoofing). The browser then initiates TCP to the resolved IP, beginning the TLS handshake. Attacker perspective: each phase is observable and attackable. IDF cyber analysts track DNS queries as early threat indicators; anomalous domains trigger alerts. TLS certificate pinning adds defense by rejecting untrusted certificates even if DNS is compromised. The full path—DNS → TCP → TLS → HTTP requests → server processing → responses → rendering—is where defense-in-depth applies."},
            {"h": "Why the Trace Matters", "body": "Understanding the full flow reveals that 'visiting a website' is actually dozens of separate security decisions. Modern browsers now isolate tabs and use sandboxing at each stage. For GAMA preparedness, you need to identify which stage each attack targets: DNS hijacking (before TCP), TLS stripping (during handshake), injection attacks (during rendering)."},
        ],
        "links": [
            {"label": "Cloudflare - How the Internet Works", "url": "https://www.cloudflare.com/learning/"},
            {"label": "Mozilla - How the Web Works", "url": "https://en.wikipedia.org/wiki/Web_browser"},
        ],
    },
    "cyber_high:3": {
        "title_check": "See it live in Wireshark",
        "sections": [
            {"h": "Wireshark as a Cyber Analyst Tool", "body": "Wireshark decodes every packet in real-time, showing protocol hierarchies: Ethernet → IP → TCP → HTTP. This visibility is essential for IDF cyber defense roles. You'll spot unencrypted credentials in old HTTP requests, identify rogue DHCP servers claiming network routing, detect ARP spoofing (two devices fighting over the same IP). Filtering by IP, port, or protocol lets you isolate suspicious flows. The 'Follow TCP Stream' feature reconstructs entire conversations—critical for forensic investigations."},
            {"h": "Practical Defense Lessons", "body": "Wireshark also teaches what *not* to send unencrypted: hostnames in DNS queries, session tokens, credentials. A single capture session on an unencrypted network reveals far too much. This is why every enterprise deployment mandates TLS, VPNs, and network segmentation. As a cyber operator, Wireshark transforms abstract protocol diagrams into tangible data you can analyze."},
        ],
        "links": [
            {"label": "Wireshark Official Documentation", "url": "https://en.wikipedia.org/wiki/Wireshark"},
            {"label": "Cloudflare - Packet Sniffing", "url": "https://www.cloudflare.com/learning/"},
        ],
    },
    "cyber_high:4": {
        "title_check": "Ports, sockets & the client-server model",
        "sections": [
            {"h": "Port Allocation & Attack Vectors", "body": "Ports 1-1023 are reserved (HTTP=80, HTTPS=443, SSH=22). Misconfigured services on unexpected ports (SSH on 2222 instead of 22) hint at security-through-obscurity defenses, which fail. Port scanning reveals running services; in offensive security, you scan to find weaknesses. The socket is a bidirectional communication endpoint—a metaphor that maps well to actual file descriptors in the OS. Once a connection is established, both client and server see the same socket pair (local_ip:local_port ↔ remote_ip:remote_port)."},
            {"h": "Defense Implications", "body": "Firewalls block ports to limit exposure. A business server should only expose ports 80, 443, and SSH. If port 3389 (RDP) is open to the internet, attackers will brute-force it. The socket model also means connection tracking: firewalls maintain tables of active sockets and allow return traffic from established connections, blocking unsolicited inbound traffic."},
        ],
        "links": [
            {"label": "Cloudflare - What is a TCP/IP Port?", "url": "https://www.cloudflare.com/learning/network-layer/what-is-a-tcp-ip-port/"},
            {"label": "Wikipedia - Network socket", "url": "https://en.wikipedia.org/wiki/Network_socket"},
        ],
    },
    "cyber_high:5": {
        "title_check": "HTTP & TLS up close",
        "sections": [
            {"h": "TLS Handshake & Forward Secrecy", "body": "TLS 1.2+ uses Elliptic Curve Diffie-Hellman (ECDH) for key exchange, ensuring forward secrecy: even if the server's private key is later compromised, past sessions remain secure because session keys are ephemeral. The handshake is expensive—why HTTP/2 multiplexes requests over one connection. HTTP/3 uses QUIC (UDP-based, faster handshake). But HTTP methods (GET, POST) are still defined at L7; no amount of TLS encrypts the URLs or request payloads from the server itself."},
            {"h": "Practical Cyber Insights", "body": "HSTS (HTTP Strict-Transport-Security) forces HTTPS, preventing downgrade attacks where an attacker tricks your browser into HTTP. Certificate pinning adds another layer. Compromised CAs (or those coerced by state actors) can issue valid certificates for any domain—this is a known risk in advanced persistent threat scenarios. Monitoring certificate transparency logs helps detect unauthorized certificates."},
        ],
        "links": [
            {"label": "Cloudflare - What is TLS?", "url": "https://www.cloudflare.com/learning/ssl/what-is-tls/"},
            {"label": "OWASP - Transport Layer Protection", "url": "https://owasp.org/"},
        ],
    },
    "cyber_low:0": {
        "title_check": "Bases & bitwise",
        "sections": [
            {"h": "Binary as Memory Foundation", "body": "Everything in memory is binary: 0x41 is the letter 'A', 0x00 is a null terminator. Bitwise operations (AND, OR, XOR) are how CPUs manipulate memory efficiently. XOR is reversible (A XOR B XOR B = A), making it useful in cryptography primitives. Bit shifting left by 1 multiplies by 2, right by 1 divides by 2—faster than actual multiplication on some architectures. In buffer overflow exploits, you need to understand how bytes are laid out: adjacent memory contains return addresses, function pointers, or saved registers. Flipping bits in the right place crashes the program or hijacks control flow."},
            {"h": "Cryptographic Relevance", "body": "Bitwise operations form the backbone of symmetric ciphers (AES, DES). Understanding XOR patterns helps you reason about weak encryption schemes. A static XOR key against plaintext is trivially breakable because XOR is frequency-preserving: if plaintext has patterns, ciphertext will too."},
        ],
        "links": [
            {"label": "W3Schools - Binary & Bitwise Operators", "url": "https://www.w3schools.com/dsa/"},
            {"label": "Wikipedia - Bitwise operation", "url": "https://en.wikipedia.org/wiki/Bitwise_operation"},
        ],
    },
    "cyber_low:1": {
        "title_check": "Endianness & hex dumps",
        "sections": [
            {"h": "Endianness in Real Exploitation", "body": "Big-endian (network byte order) stores the most significant byte first; little-endian (x86, ARM) stores it last. A 4-byte integer 0x12345678 appears as 12 34 56 78 (big-endian) or 78 56 34 12 (little-endian) in memory. When crafting payloads for buffer overflow attacks, endianness is critical: a return address must be in the target architecture's byte order. Network protocols use big-endian (why it's called 'network byte order'), so socket code often calls hton*() and ntoh*() to convert."},
            {"h": "Hex Dump Reading", "body": "A hex dump shows raw memory in hexadecimal. Left column is the address, middle shows bytes (16 per line), right shows ASCII (non-printable shown as '.'). Reading hex dumps is essential for debugging crashes—you'll see stack canaries, function prologues, and exploit artifacts. Scripting tools to parse hex dumps (or writing parsers in IDA/Ghidra) is a daily skill in reverse engineering."},
        ],
        "links": [
            {"label": "Cloudflare - Endianness", "url": "https://www.cloudflare.com/learning/"},
            {"label": "Wikipedia - Endianness", "url": "https://en.wikipedia.org/wiki/Endianness"},
        ],
    },
    "cyber_low:2": {
        "title_check": "How a process is laid out",
        "sections": [
            {"h": "Memory Segments & Exploitation", "body": "A process layout includes: code (read-only, executable), data (initialized globals), BSS (uninitialized globals, zero-filled), heap (dynamic allocation), stack (local variables, return addresses). Buffer overflows target stack or heap. Heap overflows corrupt adjacent heap structures (metadata, pointers to other objects). Stack overflows overwrite return addresses on the call stack, hijacking execution. The layout varies per OS—Linux/Windows differ in segment sizes and randomization (ASLR). Return-oriented programming (ROP) chains code snippets to bypass DEP/NX (no-execute) protections by reusing existing code in the binary."},
            {"h": "Defense: Stack Canaries & ASLR", "body": "Modern systems place canaries (sentinel values) between local variables and the return address. If a buffer overflow corrupts the canary, the program detects it on function return. ASLR randomizes the base address of code and heap at each run, making hardcoded addresses in exploits fail. These defenses raise the bar significantly but don't eliminate exploitation—they require more work and luck."},
        ],
        "links": [
            {"label": "OWASP - Buffer Overflow", "url": "https://owasp.org/"},
            {"label": "Wikipedia - Memory layout (programming)", "url": "https://en.wikipedia.org/wiki/Data_segment"},
        ],
    },
    "cyber_low:3": {
        "title_check": "PE vs ELF",
        "sections": [
            {"h": "Executable Formats & Reverse Engineering", "body": "PE (Portable Executable) is Windows' format; ELF (Executable and Linkable Format) is Linux/Unix. Both share structure: headers describe the binary's architecture, sections (code, data, imports), entry point. The headers tell the OS how to load and execute the program. Reverse engineers parse these formats to locate code sections, identify imported functions (which functions from DLLs/libraries the binary uses), and find data sections. A malware analyst uses tools like objdump (ELF) or pestudio (PE) to understand the binary's surface without running it—this avoids sandbox escape or trigger conditions in the malware."},
            {"h": "Import Tables & Dependencies", "body": "PE binaries list DLL imports (e.g., kernel32.dll); ELF binaries list shared libraries (e.g., libc.so). These import tables are hijack points: DLL injection/preloading tricks the loader into running attacker code before the actual program. Understanding import tables is crucial for both attack and defense (detecting rogue libraries, validating signatures)."},
        ],
        "links": [
            {"label": "Wikipedia - Portable Executable", "url": "https://en.wikipedia.org/wiki/Portable_Executable"},
            {"label": "Wikipedia - Executable and Linkable Format", "url": "https://en.wikipedia.org/wiki/Executable_and_Linkable_Format"},
        ],
    },
    "cyber_low:4": {
        "title_check": "Representing chars, floats & struct padding",
        "sections": [
            {"h": "Struct Padding Exploitation", "body": "A C struct packs members into memory with alignment constraints: typically, each member's offset is a multiple of its size. A struct {char c; int x;} has padding between c and x because int must be 4-byte aligned. This padding is zeroed but often uninitialized in security contexts—accidentally leaking padding bytes can reveal heap state or prior data. Exploits sometimes write to padding to corrupt adjacent fields. Float representation (IEEE 754) uses sign bit, exponent, mantissa—understanding this helps in attacks using crafted floating-point values to trigger integer overflows or bypass validations."},
            {"h": "Real-World Case", "body": "A socket struct might have padding that remains uninitialized. If the program memcpy()s it over the network, those padding bytes leak information. Defensive practice: zero-initialize structs (memset() or {0}) before use. For GAMA, knowing struct layout is essential for exploitation and defense alike."},
        ],
        "links": [
            {"label": "Wikipedia - Data structure alignment", "url": "https://en.wikipedia.org/wiki/Data_structure_alignment"},
            {"label": "Cloudflare - Number Representation", "url": "https://www.cloudflare.com/learning/"},
        ],
    },
    "cyber_low:5": {
        "title_check": "How a stack overflow works (conceptually)",
        "sections": [
            {"h": "Return Address Hijacking", "body": "A function stores its return address on the stack. If a local buffer overflows, it can overwrite the return address. When the function returns (via RET instruction, which pops the return address from the stack), it jumps to the attacker's address. Classic exploit: overflow a 32-byte buffer with 64 bytes, overwriting a 4-byte return address pointer. The program crashes or executes attacker-controlled code. Defenses: stack canaries detect overwrites; ASLR randomizes target addresses; DEP/NX marks stack as non-executable, blocking shellcode injection (forcing ROP chains instead)."},
            {"h": "Why It Still Matters", "body": "Decades of patches, and stack overflows remain a primary exploitation vector in real-world CVEs. The reason: bounds checking is easy to get wrong. Even modern languages offer unsafe code paths. IDF cyber operators need to spot stack overflow opportunities during code review and testing—a missing length check is a critical finding."},
        ],
        "links": [
            {"label": "OWASP - Stack Overflow", "url": "https://owasp.org/"},
            {"label": "Wikipedia - Stack buffer overflow", "url": "https://en.wikipedia.org/wiki/Stack_buffer_overflow"},
        ],
    },
    "dsa:0": {
        "title_check": "Big-O & thinking about cost",
        "sections": [
            {"h": "Complexity Classes & Practical Thresholds", "body": "O(n²) is \"fine\" up to ~10^4 elements; O(n log n) scales to 10^6+. O(2^n) is only viable for ~20 elements. On a modern CPU, 10^8 operations take ~1 second. So a O(n²) sort on n=10^4 takes ~100 seconds—unusable. Understanding these thresholds guides your algorithm choice. In competitive coding, if you see n ≤ 1000, O(n³) might work; if n ≤ 10^5, aim for O(n log n). Space complexity matters too: O(n) space might exceed memory limits. The 'constant factor' hidden in Big-O can shift practical performance: well-optimized O(n²) sometimes beats unoptimized O(n log n) on small datasets."},
            {"h": "Amortized Analysis", "body": "Arrays dynamic resize (doubling capacity) when full. A single insert is O(1) amortized, not O(n), because resizing happens infrequently. Understanding amortized vs. worst-case complexity prevents misleading analyses. For GAMA interviews, explaining why an algorithm is O(n log n) not O(n²) demonstrates understanding."},
        ],
        "links": [
            {"label": "W3Schools - Big-O Notation", "url": "https://www.w3schools.com/dsa/dsa_intro.php"},
            {"label": "Wikipedia - Time complexity", "url": "https://en.wikipedia.org/wiki/Time_complexity"},
        ],
    },
    "dsa:1": {
        "title_check": "Arrays & two pointers",
        "sections": [
            {"h": "Two-Pointer Technique", "body": "On a sorted array, two pointers (left at start, right at end) converge efficiently. Example: find if two numbers sum to a target. Move left if sum is too small, right if too large. Time: O(n), space: O(1). This technique avoids hash maps when the array is sorted. Common in LeetCode: merge sorted arrays, remove duplicates, container with most water (height by pointers, find max area). The key insight: two pointers avoid nested loops by leveraging sort order. Variants: slow/fast pointers for cycle detection in linked lists, sliding window for subarrays."},
            {"h": "Worked Example: Sum Pair", "body": "Array [1, 3, 5, 7, 9], target=12. left=0 (val 1), right=4 (val 9): sum=10 < 12, move left. left=1 (val 3), right=4 (val 9): sum=12, found [3, 9]. Pointer-based convergence beats nested loops (O(n²))."},
        ],
        "links": [
            {"label": "W3Schools - Array Operations", "url": "https://www.w3schools.com/dsa/dsa_arrays.php"},
            {"label": "Wikipedia - Two pointers technique", "url": "https://en.wikipedia.org/wiki/Two-pointer_technique"},
        ],
    },
    "dsa:2": {
        "title_check": "Hash maps & sets — your #1 tool",
        "sections": [
            {"h": "Hash Map Internals & Trade-Offs", "body": "Hash maps use a hash function to map keys to array indices, achieving O(1) average-case lookup. Collisions (two keys hash to same index) are resolved via chaining or open addressing. Load factor (entries / capacity) affects performance; rehashing happens when load exceeds a threshold (~0.75). Space-time trade-off: hash maps use extra memory for fast lookups. For frequency counts (how many times does element X appear), use a hash map; for checking membership, use a hash set. In Python, dict and set are built-in hash maps."},
            {"h": "Practical Pattern: Frequency Counting", "body": "Track character frequencies: {char: count}. Two-pass: build map, find char with max count. O(n) time, O(k) space where k is alphabet size. This pattern appears in anagram detection, word frequency problems, and many interview questions."},
        ],
        "links": [
            {"label": "W3Schools - Hash Map/Dictionary", "url": "https://www.w3schools.com/dsa/dsa_hash.php"},
            {"label": "Wikipedia - Hash table", "url": "https://en.wikipedia.org/wiki/Hash_table"},
        ],
    },
    "dsa:3": {
        "title_check": "Sliding window",
        "sections": [
            {"h": "Sliding Window Pattern", "body": "Maintain a window (subarray) with two pointers (left, right). Expand by moving right; shrink by moving left. Useful for substring/subarray problems: longest substring without repeating chars, smallest subarray with sum ≥ target. The trick: only move left when the window no longer satisfies the condition, avoiding O(n²) nested loops. Time: O(n), space: O(k) for the window state (hash set of chars). Classic mistake: shrinking too early or not resetting the window correctly. The pattern is: expand right, check condition, shrink left until valid."},
            {"h": "Worked Example: Longest Substring", "body": "s='abcabcbb'. Use set of chars in window. left=0, right moves: [a]→[ab]→[abc]→ (repeat a, shrink): left=1 → [bca]→[bcab] (repeat b, shrink left=2) → [cab]. Max window size: 3 ('abc')."},
        ],
        "links": [
            {"label": "W3Schools - Sliding Window", "url": "https://www.w3schools.com/dsa/dsa_sliding_window.php"},
            {"label": "Wikipedia - Sliding window", "url": "https://en.wikipedia.org/wiki/Sliding_window_protocol"},
        ],
    },
    "dsa:4": {
        "title_check": "Stacks & queues",
        "sections": [
            {"h": "Stack: LIFO & Expression Evaluation", "body": "Stacks (Last-In-First-Out) are crucial for parsing and recursion. Function calls use an implicit stack: each call pushes a frame; return pops it. For expression evaluation, infix 3+4*2 is ambiguous (3+8=11 or 7*2=14?). Operator precedence and associativity resolve this. Algorithm: use a stack for operators and a queue for operands (Shunting Yard). Postfix notation (3 4 * 2 +) is unambiguous and stack-evaluable: push 3, push 4, pop both and push 3*4, push 2, pop both and push 12+2."},
            {"h": "Queue: FIFO & BFS", "body": "Queues (First-In-First-Out) are essential for breadth-first search (BFS) on graphs. Dequeue a node, enqueue its unvisited neighbors. Time: O(V+E) for V vertices and E edges. Stacks do depth-first search (DFS). Both traverse all reachable nodes; BFS finds shortest paths in unweighted graphs, DFS explores deeply."},
        ],
        "links": [
            {"label": "W3Schools - Stacks & Queues", "url": "https://www.w3schools.com/dsa/dsa_stacks_queues.php"},
            {"label": "Wikipedia - Stack (abstract data type)", "url": "https://en.wikipedia.org/wiki/Stack_(abstract_data_type)"},
        ],
    },
    "dsa:5": {
        "title_check": "Linked lists",
        "sections": [
            {"h": "Linked List Operations & Cycle Detection", "body": "A linked list is a chain of nodes; each node holds data and a pointer to the next. Unlike arrays, insertion/deletion at head is O(1); access is O(n) (must traverse). Cycle detection uses Floyd's algorithm: slow pointer moves 1 step, fast pointer moves 2 steps. If they meet, a cycle exists; if fast reaches null, no cycle. Time: O(n), space: O(1). Finding cycle start: after detecting, move one pointer to head and both move 1 step at a time; they meet at the cycle start."},
            {"h": "Reverse a Linked List", "body": "Three pointers: prev, curr, next. Reverse by updating curr→next = prev, then advance. Time: O(n), space: O(1). Recursively: base case (null or single node), reverse rest, then reverse current and next pointers. Iterative is usually preferred for clarity and stack efficiency."},
        ],
        "links": [
            {"label": "W3Schools - Linked Lists", "url": "https://www.w3schools.com/dsa/dsa_linked_lists.php"},
            {"label": "Wikipedia - Linked list", "url": "https://en.wikipedia.org/wiki/Linked_list"},
        ],
    },
    "dsa:6": {
        "title_check": "Binary search",
        "sections": [
            {"h": "Binary Search: Precondition & Variants", "body": "Binary search requires a sorted array and achieves O(log n) by halving the search space each iteration. Set left=0, right=n-1, mid=(left+right)//2. If arr[mid] < target, left=mid+1 (target is right); if arr[mid] > target, right=mid-1 (target is left). Condition: arr[mid]==target → found. Trap: off-by-one errors in left/right updates. Variant: find first occurrence (once found, move right=mid-1 to find earlier matches), find last occurrence, find insert position for sorted insert."},
            {"h": "Worked Example: First Occurrence", "body": "arr=[1,1,2,2,2,3], target=2. Binary search finds 2 at mid=2. To find first, continue: right=mid-1=1. Now arr[mid]=1, left=mid+1=2. Exit when left > right. First 2 is at index 2. "},
        ],
        "links": [
            {"label": "W3Schools - Binary Search", "url": "https://www.w3schools.com/dsa/dsa_search_binary.php"},
            {"label": "Wikipedia - Binary search", "url": "https://en.wikipedia.org/wiki/Binary_search_algorithm"},
        ],
    },
    "dsa:7": {
        "title_check": "Recursion & backtracking",
        "sections": [
            {"h": "Backtracking: Explore All Paths", "body": "Backtracking explores all possible solutions by recursively trying options and undoing (backtracking) when a path fails or reaches a dead end. Use for: permutations, combinations, N-queens, Sudoku solver. Template: base case (found solution?), loop over choices, recursive call, undo choice. Time: exponential (all paths), but pruning reduces it. Example: 0-1 knapsack uses DP; exhaustive search uses backtracking with memoization."},
            {"h": "Worked Example: Permutations", "body": "Generate all permutations of [1,2,3]. Base case: if path length == 3, add path. Loop: try unused element, add to path, recurse, remove from path. DFS tree explores all branches. Time: O(n!), space: O(n) (recursion depth)."},
        ],
        "links": [
            {"label": "W3Schools - Recursion & Backtracking", "url": "https://www.w3schools.com/dsa/dsa_recursion.php"},
            {"label": "Wikipedia - Backtracking", "url": "https://en.wikipedia.org/wiki/Backtracking"},
        ],
    },
    "dsa:8": {
        "title_check": "Trees, BFS & DFS",
        "sections": [
            {"h": "Tree Traversals: In-Order, Pre-Order, Post-Order", "body": "In-order (left→node→right) yields sorted order for BSTs. Pre-order (node→left→right) useful for copying trees. Post-order (left→right→node) useful for deletion. BFS (level-order) uses a queue; DFS uses a stack or recursion. Example: BST [4, 2, 6, 1, 3, 5, 7]. In-order: [1,2,3,4,5,6,7]. Pre-order: [4,2,1,3,6,5,7]. Balanced BST has height O(log n); unbalanced is O(n). Self-balancing trees (AVL, Red-Black) maintain balance via rotations."},
            {"h": "Lowest Common Ancestor (LCA)", "body": "In a BST, LCA of two nodes: traverse from root; if both nodes are in left subtree, recurse left; both in right, recurse right; else root is LCA. Time: O(h) where h is height. Generalizes to trees without binary search property using post-order traversal."},
        ],
        "links": [
            {"label": "W3Schools - Trees & BFS/DFS", "url": "https://www.w3schools.com/dsa/dsa_trees.php"},
            {"label": "Wikipedia - Binary search tree", "url": "https://en.wikipedia.org/wiki/Binary_search_tree"},
        ],
    },
    "dsa:9": {
        "title_check": "Sorting & heaps",
        "sections": [
            {"h": "Sorting Trade-Offs & Stability", "body": "QuickSort: O(n log n) average, O(n²) worst-case (bad pivots), in-place, unstable. MergeSort: O(n log n) guaranteed, stable, but O(n) extra space. HeapSort: O(n log n), in-place, unstable. For interview: know QuickSort (divide-pivot-conquer) and MergeSort (divide-merge). Stability matters if preserving order of equal elements is required (e.g., sorting by multiple keys). Heaps (binary heaps) are used for priority queues: max-heap (parent ≥ children), min-heap (parent ≤ children). Insert: O(log n), extract-min: O(log n)."},
            {"h": "Worked Example: Heap Sort", "body": "Array [3,1,4,1,5]. Build heap: O(n). Extract-min n times: [1,1,3,4,5]. Each extract is O(log n). Total: O(n log n)."},
        ],
        "links": [
            {"label": "W3Schools - Sorting Algorithms", "url": "https://www.w3schools.com/dsa/dsa_sorting.php"},
            {"label": "Wikipedia - Heap (data structure)", "url": "https://en.wikipedia.org/wiki/Binary_heap"},
        ],
    },
    "dsa:10": {
        "title_check": "Graphs & connectivity",
        "sections": [
            {"h": "Graph Representation & Shortest Path", "body": "Graphs are vertices + edges. Represent as adjacency list (better for sparse graphs) or matrix (dense). BFS finds shortest path in unweighted graphs. Dijkstra's algorithm finds shortest path with non-negative weights: greedily pick unvisited node with smallest distance, update neighbors. Time: O((V+E) log V) with a priority queue. Bellman-Ford handles negative weights but is slower: O(VE). Strongly connected components (Tarjan or Kosaraju) identify groups of mutually reachable vertices."},
            {"h": "Worked Example: Dijkstra", "body": "Graph: A→B(1), A→C(4), B→C(2), B→D(5), C→D(1). From A: dist[A]=0. Visit A, update B=1, C=4. Visit B (smallest), update C=3, D=6. Visit C, update D=4. Visit D. Shortest paths: [0,1,3,4]."},
        ],
        "links": [
            {"label": "W3Schools - Graphs & Connectivity", "url": "https://www.w3schools.com/dsa/dsa_graphs.php"},
            {"label": "Wikipedia - Shortest path problem", "url": "https://en.wikipedia.org/wiki/Shortest_path_problem"},
        ],
    },
    "dsa:11": {
        "title_check": "Dynamic programming",
        "sections": [
            {"h": "DP Principles: Overlapping Subproblems & Optimal Substructure", "body": "DP solves problems by breaking them into overlapping subproblems and storing results (memoization). Fibonacci: F(n) = F(n-1) + F(n-2). Naive recursion is exponential; memoized DP is O(n). Two approaches: top-down (recursion + memo) or bottom-up (iterative table). Optimal substructure: optimal solution builds from optimal subsolutions. Example: longest increasing subsequence (LIS) uses DP[i] = longest LIS ending at index i."},
            {"h": "Worked Example: Coin Change", "body": "Coins=[1,2,5], amount=5. DP[i]=min coins for amount i. DP[0]=0, DP[1]=1 (use 1), DP[2]=1 (use 2), DP[3]=2 (use 2+1), DP[4]=2 (use 2+2), DP[5]=1 (use 5). Time: O(n * len(coins)), space: O(n)."},
        ],
        "links": [
            {"label": "W3Schools - Dynamic Programming", "url": "https://www.w3schools.com/dsa/dsa_dynamic_programming.php"},
            {"label": "Wikipedia - Dynamic programming", "url": "https://en.wikipedia.org/wiki/Dynamic_programming"},
        ],
    },
}
