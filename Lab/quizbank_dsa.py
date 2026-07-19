# quizbank_dsa.py - additional graded checks for the dsa track.
# Merged onto each lesson's existing quiz by content.build_courses().
# Answer indices balanced across the file so the correct option isn't always first.
EXTRA_QUIZ = {
    "dsa-1": [
        {
            "q": "What is the time complexity of appending n items to a Python list one at a time?",
            "code": "a = []\nfor i in range(n): a.append(i)",
            "options": [
                "O(n) amortized — each append is O(1) amortized despite occasional resizing",
                "O(n^2) because the list resizes",
                "O(n log n)",
                "O(1) total"
            ],
            "answer": 0,
            "why": "Dynamic-array appends are amortized O(1), so n appends total O(n); resizing doubles capacity, spreading its cost.",
            "detail": "Python lists over-allocate and double their capacity on growth, so most appends are O(1) and the rare O(n) copy is spread across many cheap ones — amortized O(1) per append, O(n) for n. Calling it O(n^2) is the classic mistake of counting each resize as if it happened every append. It is not O(n log n), and n appends obviously cannot be O(1) total. Amortized analysis is exactly why dynamic arrays are efficient despite occasional resizes."
        },
        {
            "q": "Which is asymptotically fastest for large n?",
            "code": "",
            "options": [
                "O(n)",
                "O(log n)",
                "O(n log n)",
                "O(n^2)"
            ],
            "answer": 1,
            "why": "For large n the ordering is O(log n) < O(n) < O(n log n) < O(n^2); logarithmic grows slowest.",
            "detail": "O(log n) grows extremely slowly — doubling n adds only a constant — so it beats all the others for large inputs. The ordering from fastest-growing-slowest to fastest-growing is log n, n, n log n, n^2. Recognizing this hierarchy lets you compare algorithms at a glance and target the right complexity class for a problem, which is the practical payoff of Big-O."
        },
        {
            "q": "What is the complexity of this nested loop?",
            "code": "for i in range(n):\n    for j in range(i, n):\n        work()",
            "options": [
                "O(n) because the inner loop shrinks",
                "O(n log n)",
                "O(n^2) — the inner loop runs ~n/2 times on average, and n * n/2 is still quadratic",
                "O(log n)"
            ],
            "answer": 2,
            "why": "The inner loop runs n + (n-1) + ... + 1 ~ n^2/2 total iterations, which is O(n^2).",
            "detail": "Even though the inner loop starts at i and shrinks, the total iterations sum to n(n+1)/2 ~ n^2/2, and constant factors drop in Big-O, so it is O(n^2). Thinking the shrinking makes it O(n) is a common error — the sum is still quadratic. It is not n log n or log n. Summing the iteration counts (an arithmetic series) rather than eyeballing the loop is how you analyze triangular nested loops correctly."
        },
        {
            "q": "Why is O(n) space sometimes worth trading for better time?",
            "code": "",
            "options": [
                "Space never affects time",
                "More space always means slower",
                "O(n) space is illegal",
                "Using a hash set/map to remember seen values can cut an O(n^2) scan to O(n) time"
            ],
            "answer": 3,
            "why": "Spending O(n) extra memory (e.g., a hash set) often replaces a repeated linear search with O(1) lookups, dropping time from O(n^2) to O(n).",
            "detail": "The space-time tradeoff is central to DSA: storing seen elements in a hash set lets you check membership in O(1) instead of re-scanning, turning a nested-loop O(n^2) into a single O(n) pass. Space and time are deeply related (that is the whole tradeoff), more space does not inherently mean slower, and O(n) space is perfectly normal. Recognizing when to 'buy' speed with memory is one of the most common optimization moves in interviews and practice."
        },
        {
            "q": "What does 'amortized O(1)' mean, precisely?",
            "code": "",
            "options": [
                "Averaged over a sequence of operations each is O(1), even if a few individual ones are costlier",
                "Every single operation is exactly O(1)",
                "It is the same as worst-case O(1)",
                "It means usually O(n)"
            ],
            "answer": 0,
            "why": "Amortized O(1) means the total cost of m operations is O(m), so the average per operation is O(1), though some may be expensive.",
            "detail": "Amortized analysis considers a whole sequence: a hash insert or list append is O(1) on average because the occasional expensive resize is paid for by many cheap operations. It is NOT that every single operation is O(1) (a resize is O(n)), and it differs from worst-case O(1) (which forbids any expensive operation). It does not mean 'usually O(n)'. This distinction matters when a single worst-case latency spike is unacceptable, even if the average is fine."
        },
        {
            "q": "Two algorithms are O(n). One does 3 passes, the other 1. What does Big-O say?",
            "code": "",
            "options": [
                "The 3-pass one is O(3n), a different class",
                "Both are O(n) — Big-O ignores constant factors, though the 1-pass one is ~3x faster in practice",
                "The 1-pass one is O(log n)",
                "They cannot be compared"
            ],
            "answer": 1,
            "why": "Constant factors are dropped in Big-O, so both are O(n); the constant still matters for real-world speed but not the class.",
            "detail": "Big-O captures growth RATE, not exact operation counts, so 3n and n are both O(n) — the same class. There is no separate 'O(3n)' class (constants are absorbed), the one-pass version is not logarithmic, and they are directly comparable (same class, different constant). This is why Big-O tells you scalability but not which of two same-class algorithms wins on a given input — for that you measure or count constants."
        }
    ],
    "dsa-2": [
        {
            "q": "Two pointers works most naturally on what kind of array?",
            "code": "",
            "options": [
                "Any unsorted array equally well",
                "Only arrays of unique values",
                "A SORTED array, where moving pointers based on comparison makes monotonic progress",
                "Only arrays of even length"
            ],
            "answer": 2,
            "why": "Two pointers typically relies on sorted order so that moving a pointer predictably increases or decreases a value.",
            "detail": "The classic converging two-pointer pattern (for pair-sum, etc.) needs sorted input so that moving the left pointer right increases the sum and moving the right pointer left decreases it — that monotonicity is what lets you discard possibilities. On unsorted data this reasoning fails (you would sort first, O(n log n), or use a hash set instead). It does not require unique values or even length. Recognizing the sorted-input prerequisite is key to knowing when two pointers applies."
        },
        {
            "q": "What does this print?",
            "code": "a = [1,2,3,4,5]\nl, r = 0, len(a)-1\nwhile l < r:\n    a[l], a[r] = a[r], a[l]\n    l += 1; r -= 1\nprint(a)",
            "options": [
                "[1, 2, 3, 4, 5] unchanged",
                "[5, 4, 3, 4, 5]",
                "An index error",
                "[5, 4, 3, 2, 1] — it reverses the array in place with two pointers"
            ],
            "answer": 3,
            "why": "The two pointers swap ends moving inward, reversing the array in O(n) time and O(1) space.",
            "detail": "Swapping a[l] and a[r] while l and r converge reverses the list: 1<->5, 2<->4, middle stays — giving [5,4,3,2,1]. It is not unchanged (swaps happen), not the partial-swap artifact of option c, and there is no index error since l<r guards it. This is the canonical in-place reversal with two pointers, O(n) time and O(1) extra space, a pattern reused in many problems."
        },
        {
            "q": "For finding a pair that sums to a target in a SORTED array, two pointers gives what complexity, and why beat the hash-set approach here?",
            "code": "",
            "options": [
                "O(n) time, O(1) space — no extra memory, since the array is already sorted",
                "O(n^2) time",
                "O(n log n) because it sorts again",
                "O(1) time"
            ],
            "answer": 0,
            "why": "On already-sorted data, converging pointers find the pair in one O(n) pass with no extra memory, unlike the hash set's O(n) space.",
            "detail": "With the array sorted, two pointers move inward based on whether the current sum is too big or small, finding the answer in O(n) time and O(1) space. The hash-set method is also O(n) time but uses O(n) space, so two pointers wins on memory when the data is already sorted. It is not O(n^2), does not re-sort (it is given sorted), and cannot be O(1) time (you must scan). Choosing between the two hinges on whether the input is sorted and whether space matters."
        },
        {
            "q": "What subtle bug does this pair-sum loop have?",
            "code": "def has_pair(a, t):  # a is sorted\n    l, r = 0, len(a)-1\n    while l <= r:\n        s = a[l] + a[r]\n        if s == t: return True\n        elif s < t: l += 1\n        else: r -= 1\n    return False",
            "options": [
                "It should use a hash set",
                "l <= r lets l and r point at the SAME element, allowing a number to pair with itself",
                "The comparisons are backwards",
                "It never terminates"
            ],
            "answer": 1,
            "why": "With l <= r, when l == r the code adds a[l]+a[l], falsely allowing an element to pair with itself.",
            "detail": "If the problem forbids using one element twice, the guard should be `l < r` so the pointers never coincide; `l <= r` lets a[l]+a[l] be checked. The comparisons are correct (sum too small -> move left up), and it does terminate (the range shrinks each step). Whether `<` or `<=` is right depends on the problem's rules about reusing an element — a classic off-by-one boundary decision that separates a correct solution from a subtly wrong one."
        },
        {
            "q": "Which problem is a poor fit for two pointers?",
            "code": "",
            "options": [
                "Reversing an array in place",
                "Merging two sorted arrays",
                "Finding whether ANY two unsorted values sum to a target (a hash set is better)",
                "Removing duplicates from a sorted array"
            ],
            "answer": 2,
            "why": "For an unsorted pair-sum, sorting first costs O(n log n); a hash set solves it in O(n) without sorting, so two pointers is not ideal.",
            "detail": "Unsorted pair-sum is better with a hash set (O(n), no sort) than two pointers (which needs sorting first). In-place reversal, merging sorted arrays, and deduping a sorted array are all natural two-pointer problems where the data is already ordered or the pointers move independently. Knowing when a hash set beats two pointers — specifically when sorting is not already free — is part of choosing the right tool rather than forcing a favorite pattern."
        },
        {
            "q": "In the 'remove duplicates from sorted array in place' pattern, what do the two pointers represent?",
            "code": "slow = 0\nfor fast in range(1, len(a)):\n    if a[fast] != a[slow]:\n        slow += 1\n        a[slow] = a[fast]",
            "options": [
                "Both scan from opposite ends",
                "slow is always faster than fast",
                "They mark a window's size",
                "slow marks the end of the deduped region; fast scans ahead for the next new value"
            ],
            "answer": 3,
            "why": "The slow pointer builds the unique prefix while the fast pointer explores, copying each new value just past slow.",
            "detail": "This is the fast/slow (read/write) two-pointer variant: fast reads every element, and whenever it finds a value different from a[slow], slow advances and receives it, compacting uniques to the front. The pointers do not move from opposite ends (that is the converging variant), slow is by definition behind fast, and this is not a sliding window. Recognizing the fast/slow read-write pattern is key to in-place array compaction problems."
        }
    ],
    "dsa-3": [
        {
            "q": "What does a Python dict guarantee about O(1) lookup?",
            "code": "",
            "options": [
                "Average-case O(1); worst case can degrade, but practically it is constant-time",
                "Guaranteed O(1) in all cases",
                "Always O(log n)",
                "O(n) for lookups"
            ],
            "answer": 0,
            "why": "Hash maps give average O(1) lookup; pathological hash collisions can degrade it, but for normal use it is constant.",
            "detail": "Dict/set operations are O(1) on average because hashing spreads keys across buckets; adversarial or unlucky collisions could theoretically degrade performance, so it is average not guaranteed worst-case. It is not O(log n) (that is a balanced tree) or O(n) (that is a linear scan). This average-case O(1) is what makes hash maps the default tool for membership tests and counting, as long as you are not facing hash-collision attacks."
        },
        {
            "q": "What does this code detect?",
            "code": "seen = set()\nfor x in a:\n    if x in seen: return True\n    seen.add(x)\nreturn False",
            "options": [
                "Whether the array is sorted",
                "Whether the array contains any duplicate value",
                "The maximum element",
                "Whether the array sums to zero"
            ],
            "answer": 1,
            "why": "It returns True the moment a value is seen twice, so it detects duplicates in O(n) time using O(n) space.",
            "detail": "Each element is checked against a set of previously seen values; a hit means a duplicate. It has nothing to do with sortedness, the maximum, or a sum. This is the canonical 'contains duplicate' solution and a template for many hash-set problems: remember what you have seen, then test membership in O(1). Trading O(n) space for O(n) time here beats the O(n^2) nested-loop comparison."
        },
        {
            "q": "For two-sum, what does the hash map store as you scan?",
            "code": "seen = {}\nfor i, x in enumerate(a):\n    if t - x in seen: return [seen[t-x], i]\n    seen[x] = i",
            "options": [
                "The running sum",
                "The sorted array",
                "Each value mapped to its index, so you can look up the needed complement instantly",
                "Only the maximum so far"
            ],
            "answer": 2,
            "why": "It maps value -> index; for each x it checks if the complement (t - x) was already seen, giving O(n) two-sum.",
            "detail": "The map remembers value->index; at each element you ask whether its complement t-x is already in the map, and if so you have the pair — one pass, O(n). It does not store a running sum, a sorted copy, or just the max. This complement-lookup trick is the definitive improvement over the O(n^2) double loop and a template you will reuse for many 'find two things that relate' problems."
        },
        {
            "q": "Predict the output.",
            "code": "from collections import Counter\nc = Counter('abracadabra')\nprint(c['a'], c['z'])",
            "options": [
                "5 with a KeyError on 'z'",
                "1 1",
                "11 0",
                "5 0 — Counter tallies occurrences; missing keys default to 0"
            ],
            "answer": 3,
            "why": "Counter counts each character (5 a's) and returns 0 for absent keys instead of raising KeyError.",
            "detail": "'abracadabra' has five a's, so c['a'] is 5, and Counter (a dict subclass) returns 0 for a missing key rather than raising — so c['z'] is 0, no KeyError. It is not 1 1 or 11 (the string length). Counter is the go-to for frequency problems (anagrams, most-common element), and its zero-default behavior is exactly what makes counting code clean, unlike a plain dict which would raise on a missing key."
        },
        {
            "q": "Why does using a set for membership beat a list for the same purpose?",
            "code": "if x in my_set:   # vs  if x in my_list:",
            "options": [
                "Set membership is O(1) average; list membership is O(n) (a linear scan)",
                "They are the same speed",
                "Lists are faster for membership",
                "Sets cannot test membership"
            ],
            "answer": 0,
            "why": "A set hashes the value for O(1) average lookup, while `x in list` scans every element, O(n).",
            "detail": "`x in set` uses hashing for average O(1), but `x in list` compares against each element until found or exhausted, O(n). They are not the same speed, lists are slower for membership, and sets absolutely support `in`. Swapping a list for a set when you repeatedly test membership is one of the easiest and most impactful optimizations, turning an accidental O(n^2) into O(n)."
        },
        {
            "q": "What is the risk of using a mutable object like a list as a dict key?",
            "code": "d = {}\nd[[1,2]] = 'x'   # what happens?",
            "options": [
                "It works fine",
                "It raises TypeError — lists are unhashable, so they cannot be keys",
                "It stores by value",
                "It silently converts to a tuple"
            ],
            "answer": 1,
            "why": "Dict keys must be hashable and immutable; a list is mutable and unhashable, so this raises TypeError.",
            "detail": "Hash maps require keys whose hash never changes, so only immutable, hashable objects (tuples, strings, numbers) qualify — a list raises TypeError. It does not work, does not store by value, and does not auto-convert to a tuple (you must do that yourself: `d[(1,2)]`). This is why you convert lists to tuples for use as keys, a frequent need when memoizing on multiple values or keying by a coordinate pair."
        }
    ],
    "dsa-4": [
        {
            "q": "The sliding window technique applies to problems about what?",
            "code": "",
            "options": [
                "Any subset of elements",
                "Sorted arrays only",
                "Contiguous subarrays or substrings meeting some condition (max sum, longest without repeats)",
                "Tree traversals"
            ],
            "answer": 2,
            "why": "Sliding window optimizes problems over CONTIGUOUS ranges by expanding/shrinking a window instead of re-examining every range.",
            "detail": "The pattern fits contiguous-subarray/substring problems — longest substring without repeats, max sum of size k, smallest window covering a set — where you slide boundaries rather than recompute every range. It does not apply to arbitrary (non-contiguous) subsets, is not restricted to sorted arrays, and is unrelated to trees. Recognizing 'contiguous range with a condition' is the trigger to reach for a sliding window instead of nested loops."
        },
        {
            "q": "What does the fixed-size window sum in this code cost?",
            "code": "s = sum(a[:k])\nbest = s\nfor i in range(k, len(a)):\n    s += a[i] - a[i-k]\n    best = max(best, s)",
            "options": [
                "O(n*k) because it re-sums",
                "O(n^2)",
                "O(k) total",
                "O(n) total — each step updates the sum in O(1) by adding one element and removing one"
            ],
            "answer": 3,
            "why": "Sliding maintains the sum incrementally (add the new element, subtract the one leaving), so each of n steps is O(1): O(n) total.",
            "detail": "Instead of re-summing each window (which would be O(n*k)), the code adds the entering element and subtracts the leaving one in O(1), so the whole scan is O(n). It is not O(n*k) (that is the naive re-sum), not O(n^2), and not O(k) total (that is one window). This incremental-update trick is the essence of sliding window: reuse the previous computation rather than redo it."
        },
        {
            "q": "What technique does this variable-size window use, and to solve what?",
            "code": "left = 0; seen = set(); best = 0\nfor right, ch in enumerate(s):\n    while ch in seen:\n        seen.remove(s[left]); left += 1\n    seen.add(ch)\n    best = max(best, right - left + 1)",
            "options": [
                "A variable-size sliding window finding the longest substring without repeating characters",
                "Binary search",
                "A fixed-size window",
                "Two pointers on a sorted array"
            ],
            "answer": 0,
            "why": "The window grows by moving right and shrinks from the left whenever a repeat appears, tracking the longest valid window.",
            "detail": "This is the variable-size window: right expands the window, and when a duplicate character appears, left advances (shrinking) until the window is valid again, recording the maximum length. It is not binary search or a fixed window (the size changes), and though it uses two indices, it is specifically the shrinking-window pattern, not sorted-array two pointers. The shrink-on-violation loop is the hallmark of variable-size window problems."
        },
        {
            "q": "In a variable window, when do you SHRINK from the left?",
            "code": "",
            "options": [
                "After every single expansion",
                "When the window violates the constraint (e.g., a duplicate, or sum exceeds a limit)",
                "Never — the window only grows",
                "Only at the end"
            ],
            "answer": 1,
            "why": "You shrink from the left precisely when the current window breaks the required condition, restoring validity before continuing.",
            "detail": "The shrink step fires only when the window becomes invalid — a repeated element, a sum over target, too many distinct characters — advancing left until validity returns. Shrinking after every expansion would make it a fixed window, never shrinking makes it just a growing scan, and shrinking only at the end misses the point. The 'expand right always, shrink left on violation' rhythm is the core control flow of variable-size windows."
        },
        {
            "q": "Why is recomputing each window's sum from scratch a common performance bug?",
            "code": "for i in range(len(a)-k+1):\n    s = sum(a[i:i+k])   # the bug",
            "options": [
                "It is actually optimal",
                "sum() is O(1)",
                "Each sum is O(k), and doing it for ~n windows is O(n*k), when O(n) incremental updates suffice",
                "It uses too much memory"
            ],
            "answer": 2,
            "why": "Re-summing each window is O(k) per window times n windows = O(n*k); the sliding update makes it O(n).",
            "detail": "`sum(a[i:i+k])` costs O(k) and repeating it for every window gives O(n*k), redoing work the incremental add/subtract avoids. It is not optimal (the sliding version is), sum() over k elements is O(k) not O(1), and the issue is time not memory. This is the exact inefficiency the sliding window eliminates — recognizing the redundant recomputation is what prompts the O(1)-update rewrite."
        },
        {
            "q": "Which problem does NOT fit a sliding window?",
            "code": "",
            "options": [
                "Longest substring without repeats",
                "Max sum subarray of size k",
                "Smallest subarray with sum >= target",
                "Finding the longest INCREASING subsequence (not necessarily contiguous)"
            ],
            "answer": 3,
            "why": "Longest increasing subsequence allows non-contiguous elements, so a contiguous window cannot capture it — it needs DP.",
            "detail": "A subsequence can skip elements, so a sliding window (which handles only contiguous ranges) cannot solve longest increasing subsequence — that is a dynamic-programming or patience-sorting problem. The other three are all contiguous-range problems ideal for windows. The tell is the word 'subsequence' (non-contiguous) versus 'subarray/substring' (contiguous): only the latter fits a sliding window, a distinction worth checking before choosing the technique."
        }
    ],
    "dsa-5": [
        {
            "q": "A stack provides which access order?",
            "code": "",
            "options": [
                "LIFO — last in, first out",
                "FIFO — first in, first out",
                "Sorted order",
                "Random access by index"
            ],
            "answer": 0,
            "why": "A stack is LIFO: the most recently pushed element is the first popped.",
            "detail": "Stacks are last-in-first-out — push adds to the top, pop removes the top, so the newest element leaves first. FIFO is a queue, sorted order is a heap/sorted structure, and index access is an array. LIFO is exactly what you want for matching nested structures (brackets, recursion, undo), where the most recent open must be closed first. In Python a list with append/pop serves as a stack."
        },
        {
            "q": "What does this stack-based code check?",
            "code": "st = []\npairs = {')':'(', ']':'[', '}':'{'}\nfor c in s:\n    if c in '([{': st.append(c)\n    elif not st or st.pop() != pairs[c]: return False\nreturn not st",
            "options": [
                "Whether s is a palindrome",
                "Whether brackets in s are balanced and correctly nested",
                "The length of s",
                "Whether s is sorted"
            ],
            "answer": 1,
            "why": "It pushes openers and pops to match each closer, returning True only if every bracket matched and none are left over.",
            "detail": "Each opening bracket is pushed; each closer must match the most recent opener (popped from the top) — LIFO exactly models nesting. Ending with an empty stack means all matched. It does not test palindromes, length, or sortedness. This is the canonical valid-parentheses problem and the classic demonstration of why a stack fits nested-matching: the last opened bracket must be the first closed."
        },
        {
            "q": "For BFS (breadth-first, level by level), which structure do you use?",
            "code": "",
            "options": [
                "A stack (LIFO)",
                "A heap",
                "A queue (FIFO), so nodes are processed in the order discovered",
                "A hash map"
            ],
            "answer": 2,
            "why": "BFS uses a FIFO queue so it visits all nodes at the current level before the next, giving level-order traversal.",
            "detail": "A queue processes nodes in discovery order, so BFS finishes one level before moving deeper — the defining behavior. A stack gives DFS (depth-first), a heap gives priority order (used in Dijkstra), and a hash map tracks visited. Swapping the queue for a stack literally turns BFS into DFS, which is why the data structure choice IS the algorithm here. collections.deque is the efficient Python queue."
        },
        {
            "q": "What does this print?",
            "code": "from collections import deque\nq = deque([1,2,3])\nq.append(4)\nprint(q.popleft(), q.pop())",
            "options": [
                "3 4",
                "1 2",
                "4 1",
                "1 4 — popleft removes the front (1), pop removes the back (4)"
            ],
            "answer": 3,
            "why": "deque.popleft() removes from the front (1) and pop() removes from the back (4).",
            "detail": "A deque supports O(1) operations at both ends: popleft() takes the leftmost (1, the oldest), pop() takes the rightmost (4, the newest after the append). It is not 3 4, 1 2, or 4 1. deque is the right structure for a queue (append + popleft = FIFO) because using a plain list's pop(0) is O(n). Knowing deque's end-specific methods prevents both correctness and performance bugs in BFS and queue code."
        },
        {
            "q": "Why is a Python list's `pop(0)` a poor way to implement a queue?",
            "code": "q = [1,2,3]\nq.pop(0)   # the issue",
            "options": [
                "pop(0) is O(n) because every remaining element shifts left; deque.popleft is O(1)",
                "pop(0) is O(1)",
                "It raises an error",
                "It removes the last element"
            ],
            "answer": 0,
            "why": "Removing from the front of a list shifts all other elements down by one, costing O(n); deque avoids this.",
            "detail": "A list stores elements contiguously, so removing index 0 forces every other element to shift, making pop(0) O(n) and a list-based queue O(n^2) overall. deque uses a doubly linked structure of blocks for O(1) both ends. pop(0) is not O(1), does not error, and removes the FIRST element (index 0), not the last. This is a classic hidden performance trap — always use collections.deque for a queue."
        },
        {
            "q": "What problem is this monotonic stack solving?",
            "code": "res = [0]*len(temps); st = []\nfor i, t in enumerate(temps):\n    while st and temps[st[-1]] < t:\n        j = st.pop(); res[j] = i - j\n    st.append(i)",
            "options": [
                "Sorting the temperatures",
                "Next-greater-element: for each day, how many days until a warmer temperature",
                "Summing the array",
                "Reversing the list"
            ],
            "answer": 1,
            "why": "The stack holds indices awaiting a greater value; when a warmer day arrives it resolves them, giving the wait distance.",
            "detail": "This is a monotonic stack solving 'daily temperatures' / next-greater-element: indices wait on the stack until a larger value appears, then get popped and their answer (distance to the warmer day) recorded — O(n) total since each index is pushed and popped once. It does not sort, sum, or reverse. The monotonic-stack pattern efficiently answers 'next greater/smaller element' queries that would otherwise be O(n^2)."
        }
    ],
    "dsa-6": [
        {
            "q": "Detecting a cycle in a linked list classically uses which technique?",
            "code": "",
            "options": [
                "Sorting the nodes",
                "A binary search",
                "Floyd's fast/slow pointers — if they meet, there is a cycle",
                "A stack of all values"
            ],
            "answer": 2,
            "why": "Floyd's tortoise-and-hare moves one pointer 1 step and another 2; they meet inside a cycle, using O(1) space.",
            "detail": "The fast pointer gains on the slow one each step, so if a cycle exists they eventually collide; if fast reaches null, there is none — all in O(1) space, unlike storing seen nodes in a set (O(n)). Sorting and binary search do not apply to unordered linked structures, and a stack of all values costs O(n) space. Floyd's algorithm is the elegant, space-efficient cycle detector worth memorizing."
        },
        {
            "q": "What does this loop do?",
            "code": "prev = None\ncur = head\nwhile cur:\n    nxt = cur.next\n    cur.next = prev\n    prev = cur\n    cur = nxt\nreturn prev",
            "options": [
                "Deletes the list",
                "Finds the middle node",
                "Counts the nodes",
                "Reverses the singly linked list in place, returning the new head"
            ],
            "answer": 3,
            "why": "It flips each node's next pointer to its predecessor, walking the list once; prev ends at the old tail = new head.",
            "detail": "Saving nxt, redirecting cur.next to prev, then advancing both reverses the links one node at a time in O(n) time and O(1) space; prev finishes as the new head. It does not delete (all nodes remain), find the middle, or count. In-place list reversal with the three-pointer (prev/cur/nxt) dance is a fundamental linked-list operation and a frequent building block in harder problems."
        },
        {
            "q": "Why does finding the middle of a linked list use fast/slow pointers?",
            "code": "slow = fast = head\nwhile fast and fast.next:\n    slow = slow.next\n    fast = fast.next.next",
            "options": [
                "When fast (2x speed) reaches the end, slow is at the middle — one pass, O(1) space",
                "It sorts the list first",
                "It requires knowing the length in advance",
                "It uses O(n) extra space"
            ],
            "answer": 0,
            "why": "Fast moves twice as fast, so when it hits the end slow has covered half — the middle — in a single pass without counting.",
            "detail": "Because fast advances two nodes per slow's one, fast finishes the list when slow is halfway, pinpointing the middle in one traversal with O(1) space and no length precomputation. It does not sort, does not need the length known ahead (that is the point — you avoid a counting pass), and uses no extra space. The fast/slow trick appears in cycle detection, middle-finding, and splitting lists."
        },
        {
            "q": "What is a common bug when deleting a node from a singly linked list?",
            "code": "",
            "options": [
                "Linked lists cannot be modified",
                "Losing the reference to the rest of the list by reassigning next before saving it",
                "Deletion is always O(n)",
                "You must sort first"
            ],
            "answer": 1,
            "why": "If you overwrite a node's next pointer before saving the following node, you lose access to the remainder of the list.",
            "detail": "Pointer surgery must preserve the chain: reassigning cur.next without first capturing the node you are skipping (or its successor) strands the rest of the list. Linked lists are certainly modifiable, deletion is O(1) if you already have the predecessor, and no sorting is needed. Careful ordering of pointer updates — save before overwrite — is the core discipline of linked-list manipulation, and getting it wrong drops or corrupts the list."
        },
        {
            "q": "Why do many linked-list problems use a 'dummy head' node?",
            "code": "dummy = Node(0); dummy.next = head\n# ... build result off dummy.next",
            "options": [
                "It sorts the list",
                "It saves memory",
                "It removes special-casing for the head, since every real node then has a predecessor",
                "It is required by the language"
            ],
            "answer": 2,
            "why": "A sentinel dummy node before the head means insertions/deletions at the front need no special code — every node has a prev.",
            "detail": "The dummy (sentinel) node gives a uniform predecessor for every real node, so operations that would otherwise special-case an empty list or the head (like deleting the first node, or merging) become uniform, then you return dummy.next. It does not sort, does not save memory (it adds a node), and is a technique not a language requirement. The dummy-head trick dramatically simplifies edge cases in list-building and merging problems."
        },
        {
            "q": "What does merging two sorted linked lists cost, and how?",
            "code": "",
            "options": [
                "O(n*m)",
                "O(n log n) because it sorts",
                "O(1)",
                "O(n + m) time by walking both with a pointer each, splicing the smaller node each step"
            ],
            "answer": 3,
            "why": "Two pointers advance through the lists once, linking the smaller current node each time — linear in the total length.",
            "detail": "Because both inputs are already sorted, a single simultaneous pass (two pointers, often with a dummy head) splices nodes in order in O(n+m) time and O(1) extra space. It is not O(n*m) (no nested scan), not O(n log n) (nothing is re-sorted — they arrive sorted), and cannot be O(1) time (you must traverse). Merging sorted lists in linear time is the merge step of merge sort and a common interview building block."
        }
    ],
    "dsa-7": [
        {
            "q": "What is the safe way to compute the midpoint in binary search, and why?",
            "code": "",
            "options": [
                "mid = lo + (hi - lo) // 2, avoiding potential overflow from lo + hi in fixed-width integers",
                "mid = (lo + hi) // 2 is always fine",
                "mid = hi // 2",
                "mid = lo // 2"
            ],
            "answer": 0,
            "why": "lo + (hi - lo)//2 avoids the overflow that (lo + hi) can cause in languages with fixed-size ints.",
            "detail": "In languages with bounded integers, lo + hi can overflow when both are large, so lo + (hi - lo)//2 computes the same midpoint without that risk. In Python integers are arbitrary precision so (lo+hi)//2 is safe there, but the overflow-avoiding form is the portable habit and appears in famous bug postmortems. `hi//2` and `lo//2` are simply wrong midpoints. This is a classic detail interviewers probe."
        },
        {
            "q": "What is the classic binary-search bug in this code?",
            "code": "def bs(a, t):\n    lo, hi = 0, len(a)\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if a[mid] == t: return mid\n        elif a[mid] < t: lo = mid + 1\n        else: hi = mid - 1\n    return -1",
            "options": [
                "The comparisons are reversed",
                "hi is initialized to len(a) but used as an index; with lo <= hi it can access a[len(a)] out of bounds",
                "It should use recursion",
                "mid is computed wrong"
            ],
            "answer": 1,
            "why": "Mixing an exclusive hi=len(a) with an inclusive `lo <= hi` loop lets mid reach len(a), an out-of-bounds index.",
            "detail": "The bounds convention must be consistent: either hi = len(a)-1 with `lo <= hi` (inclusive), or hi = len(a) with `lo < hi` (exclusive). This code mixes them — hi=len(a) but `lo <= hi` — so mid can equal len(a) and index past the end. The comparisons are correct, recursion is optional, and mid is fine given consistent bounds. Off-by-one boundary errors are THE classic binary-search bug, which is why nailing the convention matters."
        },
        {
            "q": "Binary search requires the data to be in what state?",
            "code": "",
            "options": [
                "Unique values only",
                "A power-of-two length",
                "Sorted — the algorithm relies on order to discard half the range each step",
                "Stored in a hash map"
            ],
            "answer": 2,
            "why": "Binary search works only on sorted data, since comparing the middle tells you which half can contain the target.",
            "detail": "Sortedness is the prerequisite: the middle comparison is meaningful only if everything left is smaller and everything right is larger, letting you eliminate half. It does not require unique values (you can find any matching index or a boundary), any particular length, or a hash map (that is a different O(1) lookup approach). If the data is unsorted you must sort first (O(n log n)) or use another method — binary search's power comes entirely from order."
        },
        {
            "q": "What does this variant compute?",
            "code": "lo, hi = 0, len(a)\nwhile lo < hi:\n    mid = (lo + hi) // 2\n    if a[mid] < t: lo = mid + 1\n    else: hi = mid\nreturn lo",
            "options": [
                "The exact index of t only",
                "The maximum element",
                "The array length",
                "The leftmost insertion point for t (first index where a[i] >= t) — a lower_bound"
            ],
            "answer": 3,
            "why": "This half-open search converges lo to the first position where a[i] >= t, i.e., bisect_left / lower_bound.",
            "detail": "By moving hi = mid (not mid-1) on the >= side, it converges to the leftmost index where t could be inserted keeping sorted order — the lower bound, equivalent to Python's bisect_left. It is not just an exact-match search (it returns an insertion point even if t is absent), not the max or length. This boundary-finding variant is extremely useful for 'first/last occurrence' and 'insertion position' problems, a step beyond plain membership search."
        },
        {
            "q": "Binary search runs in what time, and why is that powerful?",
            "code": "",
            "options": [
                "O(log n) — halving the search space each step means even a billion items take ~30 comparisons",
                "O(n)",
                "O(n log n)",
                "O(1)"
            ],
            "answer": 0,
            "why": "Each step discards half the remaining elements, so the number of steps is log2(n) — about 30 for a billion.",
            "detail": "Halving the candidates every comparison gives O(log n): log2(1e9) is about 30, so a billion sorted items are searched in roughly 30 steps — dramatically better than an O(n) linear scan. It is not O(n) (that is scanning), O(n log n) (that is sorting), or O(1). This logarithmic scaling is why binary search and log-time structures matter so much for large data, and why keeping data sorted can be worth the cost."
        },
        {
            "q": "Binary search can apply to problems with no array at all. What is the key requirement?",
            "code": "",
            "options": [
                "The data must literally be an array",
                "A monotonic predicate — a condition that is false then true (or vice versa) over the search range",
                "Only integers work",
                "There must be exactly one answer"
            ],
            "answer": 1,
            "why": "Binary search works on any monotonic yes/no condition, letting you 'binary search on the answer' even without an explicit sorted array.",
            "detail": "If some property is false up to a threshold and true after (monotonic), you can binary search for the boundary — 'binary search on the answer' (minimum capacity, smallest feasible value, etc.), no literal array needed. It is not restricted to arrays or integers (you can search over a numeric answer range, including with a tolerance for reals), and there need not be a unique element. Recognizing a monotonic predicate is what unlocks binary search for optimization problems that do not look like search at first."
        }
    ],
    "dsa-8": [
        {
            "q": "Every correct recursion must have what?",
            "code": "",
            "options": [
                "A loop inside it",
                "At least two parameters",
                "A base case that stops recursing, and progress toward it on each call",
                "A global variable"
            ],
            "answer": 2,
            "why": "Without a base case and movement toward it, recursion never terminates and overflows the stack.",
            "detail": "Recursion needs a base case (a condition handled without further recursion) and each recursive call must move closer to that base, or it recurses forever and hits a stack overflow (RecursionError in Python). It does not require an internal loop, multiple parameters, or a global. Identifying the base case and the shrinking of the problem is the first step in writing any correct recursion, and forgetting either is the commonest recursion bug."
        },
        {
            "q": "What does f compute?",
            "code": "def f(n):\n    if n <= 1: return 1\n    return n * f(n-1)",
            "options": [
                "The nth Fibonacci number",
                "2 to the n",
                "The sum 1..n",
                "n factorial (n!)"
            ],
            "answer": 3,
            "why": "f multiplies n by f(n-1) down to the base case, computing n * (n-1) * ... * 1 = n!.",
            "detail": "Each call multiplies n by the factorial of n-1, bottoming out at 1, so it builds n! = n*(n-1)*...*1. Fibonacci would add two previous calls, 2^n would multiply by 2, and the sum would add rather than multiply. Factorial is the textbook first recursion because it maps directly to the mathematical definition — recognizing that structure (combine n with the solution for n-1) is the recursive-thinking skill this teaches."
        },
        {
            "q": "In backtracking, what is the critical step AFTER recursing on a choice?",
            "code": "path.append(choice)\nsolve(...)      # recurse\n# what goes here?",
            "options": [
                "Undo the choice (path.pop()) so the next option starts from a clean state",
                "Return immediately",
                "Append the choice again",
                "Sort the path"
            ],
            "answer": 0,
            "why": "Backtracking must UNDO the choice after recursing so sibling choices are explored from the correct state — the 'backtrack' step.",
            "detail": "The pattern is choose, recurse, un-choose: after exploring one option you pop it so the loop can try the next option without contamination from the last. Returning immediately would explore only one branch, appending again corrupts the path, and sorting is irrelevant. This undo step is literally what puts the 'back' in backtracking and is the piece beginners most often forget, causing wrong or duplicated results in permutation/subset/combination problems."
        },
        {
            "q": "Predict the output.",
            "code": "def f(n):\n    if n == 0: return 0\n    return n + f(n-1)\nprint(f(4))",
            "options": [
                "24",
                "10 — it sums 4+3+2+1+0",
                "4",
                "5"
            ],
            "answer": 1,
            "why": "f adds n to the sum of everything below it, so f(4) = 4+3+2+1+0 = 10.",
            "detail": "Each call adds n to f(n-1) down to the base f(0)=0, computing the sum 4+3+2+1 = 10. 24 would be 4! (multiplication, not addition), 4 and 5 misread the recursion. Tracing recursive calls by expanding them (f(4)=4+f(3)=4+3+f(2)...) is the reliable way to predict output, and distinguishing this additive form from the multiplicative factorial is exactly the kind of careful reading recursion demands."
        },
        {
            "q": "Why can naive recursion for problems like Fibonacci be exponentially slow?",
            "code": "def fib(n):\n    if n < 2: return n\n    return fib(n-1) + fib(n-2)",
            "options": [
                "Recursion is always exponential",
                "It uses too much memory only",
                "It recomputes the same subproblems many times, giving O(2^n) overlapping calls",
                "It never terminates"
            ],
            "answer": 2,
            "why": "Naive fib recomputes fib of the same values repeatedly across the two branches, producing an exponential call tree.",
            "detail": "fib(n) calls fib(n-1) and fib(n-2), which re-call overlapping subproblems, so fib(5) computes fib(2) several times — the call count grows like 2^n. Recursion is NOT always exponential (factorial recursion is linear); the issue here is OVERLAPPING subproblems. It does terminate (there is a base case), and the problem is time, not just memory. Memoization or DP fixes it by caching each subproblem's result, dropping it to O(n) — the motivation for dynamic programming."
        },
        {
            "q": "What limits how deep Python recursion can go, and what error signals it?",
            "code": "",
            "options": [
                "There is no limit",
                "It raises MemoryError only at gigabytes",
                "It silently returns None",
                "A recursion depth limit (~1000 by default); exceeding it raises RecursionError"
            ],
            "answer": 3,
            "why": "Python caps recursion depth (default ~1000) to prevent unbounded stack growth, raising RecursionError when exceeded.",
            "detail": "Each recursive call adds a stack frame, and Python limits depth (about 1000 by default, adjustable with sys.setrecursionlimit) to avoid a C-level stack overflow, raising RecursionError past it. There is definitely a limit, it is not primarily a MemoryError, and it raises rather than silently returning None. This is why very deep recursions (like recursing over a long list) are sometimes rewritten iteratively or with an explicit stack — a real practical constraint."
        }
    ],
    "dsa-9": [
        {
            "q": "DFS on a tree is naturally implemented with what?",
            "code": "",
            "options": [
                "Recursion (or an explicit stack) — going deep before backtracking",
                "A FIFO queue",
                "A heap",
                "Binary search"
            ],
            "answer": 0,
            "why": "DFS explores as deep as possible before backtracking, which maps directly to recursion or an explicit stack (LIFO).",
            "detail": "Depth-first traversal dives down one path fully before backing up, which recursion expresses naturally (the call stack IS the stack), or you use an explicit stack iteratively. A FIFO queue gives BFS (level order), a heap gives priority order, and binary search is unrelated. The stack-vs-queue choice is precisely what distinguishes DFS from BFS, so knowing DFS = stack/recursion is fundamental to tree and graph traversal."
        },
        {
            "q": "What does this return?",
            "code": "def depth(node):\n    if not node: return 0\n    return 1 + max(depth(node.left), depth(node.right))",
            "options": [
                "The number of nodes",
                "The height (max depth) of the binary tree",
                "The sum of values",
                "The number of leaves"
            ],
            "answer": 1,
            "why": "It returns 1 plus the deeper of the two subtrees, computing the longest root-to-leaf path length — the height.",
            "detail": "Each node reports 1 + the maximum height of its subtrees, so the root returns the overall height; an empty node contributes 0. It is not the node count (that would sum both subtrees, not max them), the value sum, or the leaf count. This max-of-subtrees recursion is the template for tree-height and many tree-DP problems, and recognizing it distinguishes 'longest path' logic (max) from 'count everything' logic (sum)."
        },
        {
            "q": "Processing tree nodes with a FIFO queue produces which traversal?",
            "code": "",
            "options": [
                "Preorder DFS",
                "Inorder DFS",
                "Level-order (BFS) — nodes visited top to bottom, left to right by level",
                "Postorder DFS"
            ],
            "answer": 2,
            "why": "A queue processes nodes in discovery order, so a tree is visited level by level — breadth-first / level-order.",
            "detail": "Enqueuing children as you dequeue parents visits an entire level before the next, giving level-order (BFS) traversal. Preorder, inorder, and postorder are all DFS orderings produced by recursion or a stack, not a queue. This is the same stack-vs-queue distinction: queue = BFS = level order. Level-order is what you want for shortest-path-in-unweighted-tree and level-based problems."
        },
        {
            "q": "What does this inorder traversal print for a binary SEARCH tree?",
            "code": "def inorder(n):\n    if not n: return\n    inorder(n.left); print(n.val); inorder(n.right)",
            "options": [
                "The values in random order",
                "Only the leaves",
                "The values largest first",
                "The values in sorted ascending order"
            ],
            "answer": 3,
            "why": "Inorder traversal of a BST (left, node, right) visits values in ascending sorted order.",
            "detail": "Because a BST keeps smaller values left and larger right, visiting left subtree, then the node, then the right subtree yields ascending order — a defining, useful property. It is not random, not just leaves, and not descending (that would be right, node, left). Inorder-on-a-BST-gives-sorted-order is a frequently exploited fact, used to validate a BST, find the kth smallest, or extract a sorted sequence."
        },
        {
            "q": "Why does BFS mark a node as visited when ENQUEUING it, not when dequeuing?",
            "code": "",
            "options": [
                "To avoid enqueuing the same node multiple times before it is processed",
                "It does not matter when you mark",
                "Marking at dequeue is always correct",
                "To save memory"
            ],
            "answer": 0,
            "why": "Marking at enqueue prevents a node with multiple parents/edges from being added to the queue several times before processing.",
            "detail": "In a graph (or a tree treated as a graph), a node can be reachable from several already-queued nodes; if you mark visited only at dequeue, it may be enqueued multiple times, inflating the queue and doing redundant work (and in some formulations causing bugs). Marking at enqueue guarantees each node enters the queue once. It DOES matter, dequeue-time marking is not always safe, and the benefit is correctness/efficiency more than raw memory. This is a subtle but important BFS detail on graphs."
        },
        {
            "q": "What is the space cost of recursive DFS on a tree, in the worst case?",
            "code": "",
            "options": [
                "Always O(1)",
                "O(h) where h is the tree height — the recursion stack depth, up to O(n) for a skewed tree",
                "Always O(n) regardless of shape",
                "O(n^2)"
            ],
            "answer": 1,
            "why": "Recursive DFS uses stack space proportional to the current depth, so O(h); a balanced tree is O(log n), a skewed one O(n).",
            "detail": "The recursion stack holds one frame per level currently being explored, so peak space is the height h: O(log n) for a balanced tree but O(n) for a degenerate (linked-list-shaped) tree. It is not O(1) (there is a stack), not always O(n) (balanced trees are logarithmic), and not O(n^2). Distinguishing height from node count is key: DFS space depends on how deep, not how many, which matters for very deep or unbalanced trees."
        }
    ],
    "dsa-10": [
        {
            "q": "Popping the minimum from a binary min-heap costs what?",
            "code": "",
            "options": [
                "O(1)",
                "O(n)",
                "O(log n) — remove the root, then sift the last element down to restore the heap",
                "O(n log n)"
            ],
            "answer": 2,
            "why": "Extract-min removes the root and re-heapifies by sifting down, which takes O(log n) for the tree height.",
            "detail": "The minimum is at the root (O(1) to read), but removing it requires moving the last element to the root and sifting it down to its correct level, costing O(log n) for the height. Peeking is O(1) but popping is O(log n), not O(1). It is not O(n) or O(n log n). This log-time extraction is why heaps are ideal for repeatedly getting the smallest/largest element, as in Dijkstra, top-k, and heap sort."
        },
        {
            "q": "What does heappop return?",
            "code": "import heapq\nh = [3,1,4,1,5]\nheapq.heapify(h)\nprint(heapq.heappop(h))",
            "options": [
                "5 — the largest",
                "3 — the first element",
                "The whole sorted list",
                "1 — the smallest element (Python heapq is a min-heap)"
            ],
            "answer": 3,
            "why": "Python's heapq is a MIN-heap, so heappop removes and returns the smallest element, 1.",
            "detail": "heapify arranges the list into a min-heap, and heappop extracts the minimum — here 1. It is not the max (Python has no built-in max-heap; you negate values to simulate one), not the original first element, and not the whole list. Knowing heapq is a min-heap is essential: for a max-heap or top-k-largest you push negated values or use heapq.nlargest, a frequent source of bugs when people expect max-heap behavior."
        },
        {
            "q": "For finding the k largest elements of n, why is a heap of size k better than sorting everything?",
            "code": "",
            "options": [
                "O(n log k) with a size-k heap beats O(n log n) sorting when k is much smaller than n",
                "Sorting is always faster",
                "They are identical",
                "A heap cannot do top-k"
            ],
            "answer": 0,
            "why": "Maintaining a heap of the k best runs in O(n log k), which beats O(n log n) full sort when k << n.",
            "detail": "You scan all n elements, keeping a min-heap of the k largest seen (pushing and popping in O(log k)), for O(n log k) total — better than sorting all n at O(n log n) when k is small. Sorting is not always faster, they are not identical, and heaps are exactly the tool for top-k. This is a classic 'do you need the whole thing sorted, or just the top k?' optimization that heaps enable."
        },
        {
            "q": "What does this print?",
            "code": "import heapq\nh = []\nfor x in [5,2,8,1]:\n    heapq.heappush(h, x)\nprint(heapq.heappop(h), heapq.heappop(h))",
            "options": [
                "5 2 — insertion order",
                "1 2 — pops come out in ascending order from the min-heap",
                "8 5 — descending",
                "1 8"
            ],
            "answer": 1,
            "why": "A min-heap always yields the smallest first, so successive pops give 1 then 2.",
            "detail": "Regardless of insertion order, heappop returns the current minimum each time: first 1, then 2. It does not preserve insertion order (that is a queue), is not descending (Python heapq is a min-heap), and 1 8 misreads the second pop. Repeated heappop yields elements in sorted ascending order — which is essentially heap sort, and why a heap is perfect for streaming out items smallest-first."
        },
        {
            "q": "What general-purpose comparison sorts achieve O(n log n), and can any comparison sort beat it?",
            "code": "",
            "options": [
                "Any sort can reach O(n)",
                "Comparison sorts are all O(n^2)",
                "Mergesort/heapsort/quicksort(avg) are O(n log n); no comparison sort can beat O(n log n) in the worst case",
                "Only quicksort is O(n log n)"
            ],
            "answer": 2,
            "why": "O(n log n) is the proven lower bound for comparison-based sorting; the standard efficient sorts hit it.",
            "detail": "Merge sort, heap sort, and average-case quicksort all run in O(n log n), and information theory proves no comparison sort can do better than O(n log n) in the worst case (there are n! orderings to distinguish). Non-comparison sorts like counting/radix sort can be O(n) but only under special constraints (small integer range), so 'any sort can reach O(n)' is false. Not all comparison sorts are O(n^2), and quicksort is not the only O(n log n) one. This lower bound is a fundamental result."
        },
        {
            "q": "Why is quicksort O(n^2) in the worst case despite averaging O(n log n)?",
            "code": "",
            "options": [
                "It is never O(n^2)",
                "Because it uses extra memory",
                "Only if the array is already sorted randomly",
                "A bad pivot (e.g., always the smallest) makes partitions of size n-1 and 0, giving n levels of O(n) work"
            ],
            "answer": 3,
            "why": "If the pivot repeatedly splits off just one element, recursion depth is n with O(n) work each, giving O(n^2).",
            "detail": "Quicksort's performance depends on pivot choice: a pivot that is always the min or max produces maximally unbalanced partitions (n-1 and 0), so depth is n and each level does O(n) work, totaling O(n^2). It is not immune to O(n^2), the issue is partition balance not memory, and worst case famously hits on ALREADY-sorted input with a naive first-element pivot (random pivots avoid this). Understanding the pivot's role explains why real implementations randomize or use median-of-three."
        }
    ],
    "dsa-11": [
        {
            "q": "To traverse a graph without looping forever, what must you maintain?",
            "code": "",
            "options": [
                "A visited set marking nodes already seen, so you never re-process them",
                "A sorted list of nodes",
                "The total edge count",
                "A heap of nodes"
            ],
            "answer": 0,
            "why": "Graphs can have cycles, so a visited set prevents revisiting nodes and looping infinitely.",
            "detail": "Unlike trees, graphs can contain cycles, so without a visited set a traversal would revisit nodes endlessly. Sorting nodes, counting edges, or using a heap are unrelated to cycle prevention (a heap matters for weighted shortest paths, a different concern). The visited set is THE essential addition that turns tree DFS/BFS into graph DFS/BFS, and forgetting it on a cyclic graph is the classic graph-traversal bug — the subject of the next question."
        },
        {
            "q": "What breaks if you forget the visited set on a cyclic graph?",
            "code": "",
            "options": [
                "Nothing; it still works",
                "Infinite recursion/looping — nodes in a cycle get revisited forever",
                "It runs faster",
                "It uses less memory but is correct"
            ],
            "answer": 1,
            "why": "Without tracking visited nodes, a cycle causes the traversal to revisit the same nodes endlessly and never terminate.",
            "detail": "A cycle means a path leads back to an already-visited node; with no visited set the algorithm follows it again and again, recursing or looping infinitely (stack overflow or hang). It does not still work, is not faster, and is certainly not correct. This is exactly why the visited set is mandatory for graphs but optional for trees (trees have no cycles). The bug is dramatic — a non-terminating program — which makes it memorable."
        },
        {
            "q": "What is being built here?",
            "code": "graph = {}\nfor u, v in edges:\n    graph.setdefault(u, []).append(v)\n    graph.setdefault(v, []).append(u)",
            "options": [
                "An adjacency matrix",
                "A directed graph",
                "An adjacency list for an UNDIRECTED graph (each edge added both ways)",
                "A binary tree"
            ],
            "answer": 2,
            "why": "It maps each node to a list of neighbors, adding both directions per edge — an undirected adjacency list.",
            "detail": "setdefault builds a dict of node -> neighbor list, and adding both u->v and v->u makes it undirected. An adjacency matrix would be a 2D grid (O(V^2) space), a directed graph would add only one direction, and it is not a tree. The adjacency list is the standard space-efficient graph representation (O(V+E)), and recognizing the both-directions insertion as 'undirected' is a key reading skill for graph code."
        },
        {
            "q": "Counting connected components in an undirected graph means doing what?",
            "code": "",
            "options": [
                "Counting the edges",
                "Sorting the nodes",
                "Finding the shortest path",
                "Running DFS/BFS from each unvisited node; each new traversal that starts is one component"
            ],
            "answer": 3,
            "why": "Each time you start a fresh traversal from a not-yet-visited node, you have found a new connected component.",
            "detail": "You iterate over all nodes; whenever you find one not yet visited, you launch a DFS/BFS that marks its whole component, incrementing a counter — the number of such launches is the component count. Counting edges, sorting, or shortest paths do not answer connectivity. This 'loop over nodes, traverse each unvisited component once' pattern is the standard way to count components or, with a tweak, detect whether a graph is fully connected."
        },
        {
            "q": "What does BFS give you on an UNWEIGHTED graph that DFS does not?",
            "code": "",
            "options": [
                "Shortest paths (fewest edges) from the source, because it explores by increasing distance",
                "Nothing different",
                "Lower memory always",
                "Sorted output"
            ],
            "answer": 0,
            "why": "BFS visits nodes in order of edge-distance, so the first time it reaches a node is via a shortest (fewest-edge) path.",
            "detail": "Because BFS expands level by level, it reaches every node by the minimum number of edges, making it the algorithm for shortest paths in unweighted graphs; DFS does not guarantee this (it may reach a node via a long path first). BFS is not universally lower memory (it can hold a whole level), and neither produces sorted output inherently. For WEIGHTED shortest paths you need Dijkstra (a heap), but for unweighted, BFS is the tool — a key distinction."
        },
        {
            "q": "Which representation is better for a SPARSE graph (few edges), and why?",
            "code": "",
            "options": [
                "Adjacency matrix, always",
                "Adjacency list — O(V + E) space, versus the adjacency matrix's O(V^2)",
                "They use the same space",
                "Neither can store sparse graphs"
            ],
            "answer": 1,
            "why": "An adjacency list stores only actual edges (O(V+E)), far less than a matrix's O(V^2) when edges are few.",
            "detail": "For a sparse graph, most node pairs have no edge, so an adjacency matrix wastes O(V^2) space storing mostly zeros, while an adjacency list stores only the E real edges plus the V nodes — O(V+E). The matrix is better only for dense graphs or O(1) edge-existence queries. They do not use the same space, and both can represent any graph. Choosing the list for sparse graphs (the common case) is a standard space optimization."
        }
    ],
    "dsa-12": [
        {
            "q": "Dynamic programming pays off when a problem has which two properties?",
            "code": "",
            "options": [
                "Sorted input and unique values",
                "A single base case",
                "Overlapping subproblems and optimal substructure",
                "No recursion possible"
            ],
            "answer": 2,
            "why": "DP applies when subproblems recur (overlapping) and an optimal solution is built from optimal sub-solutions (optimal substructure).",
            "detail": "DP is the right tool when the same subproblems are solved repeatedly (so caching helps) AND the optimal answer combines optimal answers to subproblems (optimal substructure). Sorted input, unique values, or a single base case are not the defining criteria, and DP is deeply tied to recursion (it optimizes it). Checking for these two properties is how you recognize a DP problem versus greedy or divide-and-conquer, which is the hardest part of applying DP."
        },
        {
            "q": "What technique does this line come from?",
            "code": "if n in memo: return memo[n]\nresult = solve(n-1) + solve(n-2)\nmemo[n] = result",
            "options": [
                "Binary search",
                "Greedy selection",
                "Backtracking",
                "Memoization — caching subproblem results to avoid recomputation (top-down DP)"
            ],
            "answer": 3,
            "why": "Storing and reusing computed results in a memo dict is memoization, the top-down form of dynamic programming.",
            "detail": "Checking a cache before computing and storing the result after is memoization — it turns exponential recursion (like naive Fibonacci) into linear by ensuring each subproblem is solved once. It is not binary search, greedy, or backtracking. Memoization (top-down) and tabulation (bottom-up) are the two DP styles; recognizing the cache-check-then-store pattern identifies top-down DP, the most natural way to add DP to an existing recursion."
        },
        {
            "q": "What is the difference between top-down and bottom-up DP?",
            "code": "",
            "options": [
                "Top-down memoizes a recursion on demand; bottom-up fills a table iteratively from base cases up",
                "They give different answers",
                "Top-down is always faster",
                "Bottom-up cannot use a table"
            ],
            "answer": 0,
            "why": "Top-down recurses and caches subproblems as needed; bottom-up iteratively computes all subproblems from the smallest.",
            "detail": "Top-down (memoization) starts from the target and recurses, caching results lazily; bottom-up (tabulation) starts from base cases and builds a table upward until it reaches the target. They compute the same answers (just different orders), neither is universally faster (bottom-up avoids recursion overhead but may compute unneeded states), and bottom-up is literally table-based. Knowing both styles lets you pick based on which subproblems are needed and whether recursion depth is a concern."
        },
        {
            "q": "For the coin-change 'minimum coins to make amount' problem, what does dp[i] represent?",
            "code": "dp[0] = 0\nfor i in range(1, amount+1):\n    dp[i] = min(dp[i-c]+1 for c in coins if c <= i)",
            "options": [
                "The number of ways to make i",
                "The fewest coins needed to make amount i, built from smaller amounts",
                "The largest coin usable",
                "The total value of all coins"
            ],
            "answer": 1,
            "why": "dp[i] is the minimum coin count for amount i, computed as 1 plus the best solution for i minus each coin.",
            "detail": "The state dp[i] holds the minimum number of coins for amount i; each i is solved using already-computed smaller amounts (dp[i-c]+1), the essence of bottom-up DP. It is not the number of WAYS (that is a different, additive DP), the largest coin, or a total value. Defining the state correctly (what does dp[i] MEAN) is the crux of DP, and this min-over-choices transition is the template for many optimization DPs."
        },
        {
            "q": "Why does memoization alone NOT make every exponential problem polynomial?",
            "code": "",
            "options": [
                "Memoization always makes things polynomial",
                "It makes things slower",
                "It only helps if the number of DISTINCT subproblems is polynomial; an exponential state space stays exponential",
                "It only works on Fibonacci"
            ],
            "answer": 2,
            "why": "Caching helps only when distinct subproblems are few; if the state space itself is exponential, there is nothing to save.",
            "detail": "Memoization eliminates REPEATED work, so it helps when there are polynomially many distinct subproblems (Fibonacci: n states). But if a problem has exponentially many distinct states (e.g., subsets of a large set), caching cannot shrink that — the work is genuinely exponential. So memoization is not a universal polynomial-izer, does not slow things down, and applies far beyond Fibonacci. Recognizing when the state space is small enough for DP to help is a crucial, subtle judgment."
        },
        {
            "q": "What is a common way to reduce the SPACE of a bottom-up DP?",
            "code": "# fib with two variables instead of a full array\na, b = 0, 1\nfor _ in range(n): a, b = b, a + b",
            "options": [
                "Always store every state forever",
                "Use recursion instead",
                "Space cannot be reduced",
                "Keep only the few previous states the transition needs, not the whole table"
            ],
            "answer": 3,
            "why": "If dp[i] depends only on the last one or two states, you can keep just those variables, dropping O(n) space to O(1).",
            "detail": "When the recurrence looks back only a fixed distance (fib needs dp[i-1] and dp[i-2]), you can replace the full array with a couple of rolling variables, cutting space from O(n) to O(1). Storing everything forever is the unoptimized version, recursion does not save space (it adds stack), and space CAN be reduced here. This rolling-variable optimization is a standard DP space-saving trick, common when the full table is not needed for the final answer."
        }
    ]
}
