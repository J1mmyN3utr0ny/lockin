# depth_dsa.py — extended teaching content for the dsa track.
# Auto-attached by depth.py. One entry per lesson id.

DEPTH = {

    "dsa-1": {
        "title_check": "Big-O & thinking about cost",
        "sections": [
            {"h": "COUNTING OPERATIONS, NOT SECONDS", "body": r"""Big-O describes how the number of operations your code performs grows as the input size n grows without bound - it is a shape, not a stopwatch reading. Code that does 3n+7 operations and code that does n operations are both "O(n)" because Big-O deliberately throws away constants and lower-order terms: at n=10 the difference between 3n and n might matter, but at n=10,000,000 the shape - linear vs quadratic vs logarithmic - is what decides whether your program finishes in milliseconds or hours, and the constant factor becomes noise by comparison. This is why the first thing a competent engineer does with any problem, before writing a line of code, is read the input bound. If n <= 20, the problem is quietly telling you an O(2^n) brute force is fine. If n <= 1000, O(n^2) survives. If n <= 100,000, you need O(n log n) or better. If n <= 10^9, you need O(log n) or O(1) - no algorithm that even touches every element can finish in time. Reading the constraint line is reverse-engineering the intended solution's complexity class before you have designed the solution."""},

            {"h": "READING COST OUT OF CODE, LINE BY LINE", "body": r"""To count cost you assign a cost to each line and multiply by how many times it runs, then keep only the dominant term.

    def has_pair(nums, target):        # n = len(nums)
        for i in range(len(nums)):     # runs n times
            for j in range(i+1, len(nums)):   # runs up to n times
                if nums[i] + nums[j] == target:  # O(1) work
                    return True
        return False

The outer loop runs n times; for each outer iteration the inner loop runs roughly n times too, so total work is proportional to n * n = n^2 - two nested loops over the same input is the single most common source of O(n^2) in real code, even when neither loop looks alarming on its own. Compare that to a single loop building a running sum: one pass, O(1) work per step, O(n) total. The rule of thumb: count NESTING DEPTH of loops over the input, not the number of lines. A loop containing a call to sorted() is not O(n) even though it looks like "one loop" - the sort inside costs O(n log n) per call, and if that call sits inside another loop you are silently at O(n^2 log n)."""},

            {"h": "WORKED PROBLEM: TWO SUM, THREE COMPLEXITY CLASSES", "body": r"""LeetCode 1, Two Sum: given nums and target, return indices of two numbers that add to target. Brute force checks every pair with nested loops - O(n^2) time, O(1) space, and it is the code from the previous section. A sort-then-two-pointer approach sorts the array (O(n log n)), then walks pointers from both ends: if the pair-sum is too small, advance the left pointer; too large, retreat the right pointer; this pass is O(n), so total is O(n log n) - but it loses the ORIGINAL indices unless you carry them alongside the values, since sorting scrambles position. The hash-map approach beats both:

    def two_sum(nums, target):
        seen = {}                      # value -> index
        for i, x in enumerate(nums):
            need = target - x
            if need in seen:
                return [seen[need], i]
            seen[x] = i
        return []

One pass, O(n) time, O(n) space - for each element you ask "have I already seen its complement?" in O(1), which is only possible because a hash map trades memory for that constant-time lookup. This progression - nested loops, then sort+scan, then hash map - is the single most common complexity ladder you will climb in an interview."""},

            {"h": "THE INVARIANT: COUNT THE SAME UNIT, EVERY TIME", "body": r"""The invariant behind any Big-O claim is that you are counting a CONSISTENT unit of work per step - the moment one "O(1) step" secretly costs O(n), your whole analysis is wrong even though every individual line still runs. The classic trap: building a string with result += piece inside a loop looks like n cheap appends, but strings are immutable, so each += copies the entire string built so far - that single loop is actually O(n^2), not O(n), because "append" is not O(1) for strings the way it is for a list. Edge cases stress this further. An empty input (n=0) should make your loops simply not execute - if your code instead does setup work proportional to some OTHER quantity before checking for emptiness, your "O(n)" claim was already wrong at n=0. A single element (n=1) makes nested loops indistinguishable from single loops, which can hide an O(n^2) bug until test cases grow. Duplicate values do not change the complexity CLASS of a hash-based algorithm, but they do change how many buckets actually get used. And because Python integers never overflow, a sum growing arbitrarily large costs more digits to store and manipulate as it grows - genuinely slower per operation - a subtlety fixed-width languages like C or Java simply do not have."""},

            {"h": "TIME YOU CLAIM VS TIME YOU GET: AVERAGE, WORST, AMORTIZED", "body": r"""A single Big-O label can hide three different guarantees, and interviewers expect you to know which one you are making. Average case is what typically happens - a hash map lookup is O(1) on average because a good hash function spreads keys evenly across buckets. Worst case is the guarantee that holds no matter what - a hash map degrades to O(n) per lookup if every key collides into the same bucket (pathological input, or a broken hash function), and quicksort's O(n log n) average hides an O(n^2) worst case on already-sorted input with a naive pivot choice. Amortized is a third, subtler guarantee: any ONE operation might be expensive, but averaged over a long sequence of operations the cost per operation is small - Python's list.append() is O(1) amortized because the underlying array occasionally doubles in size (an O(n) copy), but that expensive resize happens so rarely that spread across n appends the average cost per append is still O(1). Space complexity deserves the same honesty: auxiliary space (what you allocate beyond the input) is what interviewers mean by "O(n) space," and it includes the call stack - a recursive solution that looks like "no extra data structures" can still be O(n) space purely from n stacked function calls."""},

            {"h": "SPOTTING THE COMPLEXITY A PROBLEM IS ASKING FOR", "body": r"""Every LeetCode-style problem statement telegraphs its expected complexity through its constraints, and learning to read that signal is itself a skill worth drilling. "1 <= n <= 20" or "1 <= n <= 24" is almost always a green light for exponential brute force - bitmask DP or full subset enumeration, because 2^20 is only about a million. "1 <= n <= 10^5" rules out anything O(n^2) and points you at O(n) or O(n log n) - a hash map, sorting, two pointers, or a heap. "1 <= n <= 10^9" or a value bound rather than a count usually means the intended solution does not touch every element at all - binary search, math, or O(log n) is expected. Contains Duplicate (LeetCode 217) is the simplest version of this ladder: brute force O(n^2), sort-then-scan O(n log n), hash set O(n) - three valid answers, ranked by constraint tolerance, not correctness. Longest Consecutive Sequence (LeetCode 128) hides the same ladder one level deeper: sorting gets you O(n log n) trivially, but the O(n) hash-set answer requires the extra insight of only starting a sequence count from a number whose predecessor (num - 1) is absent from the set - without that check, every element re-walks its whole sequence and you are back to O(n^2) despite "using a hash set." The set alone does not guarantee the better complexity; how you use it does."""},
        ],
    },

    "dsa-2": {
        "title_check": "Arrays & two pointers",
        "sections": [
            {"h": "TWO INDICES DOING THE WORK OF NESTED LOOPS", "body": r"""Two pointers replaces a nested loop with two indices that walk toward each other (or in the same direction at different speeds) across a SORTED or otherwise monotonic sequence, turning an O(n^2) pair-search into a single O(n) pass. The technique is only safe when moving one pointer inward can never cause you to miss the answer - which is precisely what sortedness (or a similar ordering guarantee) buys you. The right tool the moment a problem says "sorted array" and asks about pairs, triplets, reversing in place, merging two sequences, or partitioning around a pivot. It is the wrong tool the instant the array is unsorted and you cannot sort it without losing information you need (like original indices) - in that case a hash map (next lesson) is usually the fix instead. The mental shift from brute force is this: instead of asking "for every i, check every j," you ask "given what I know about the sorted order, which single pointer HAS to move, and in which direction, to make progress toward the answer?" - answering that question correctly is the entire skill."""},

            {"h": "THE CONVERGING-POINTERS TEMPLATE, LINE BY LINE", "body": r"""The canonical shape for a sorted-array pair problem:

    def two_sum_sorted(nums, target):
        lo, hi = 0, len(nums) - 1
        while lo < hi:
            s = nums[lo] + nums[hi]
            if s == target:
                return [lo, hi]
            elif s < target:
                lo += 1                # sum too small, need a bigger left value
            else:
                hi -= 1                # sum too big, need a smaller right value
        return []

lo starts at the smallest element, hi at the largest. while lo < hi is the loop guard - note strictly less than, because a pointer should never compare an element against itself. If the current sum is too small, the ONLY way to increase it is to advance lo (every value to its right is >= nums[lo], since the array is sorted) - decreasing hi could only make the sum smaller, which is the wrong direction, so that move is provably useless and skipping it is what makes the pass O(n) instead of O(n^2). Symmetric logic drives hi downward when the sum is too big. Each iteration moves exactly one pointer by one step, and the two pointers can move at most n times combined before they meet."""},

            {"h": "WORKED PROBLEM: CONTAINER WITH MOST WATER", "body": r"""LeetCode 11: given heights of vertical lines, find two lines that, with the x-axis, form the container holding the most water - area = min(height[l], height[r]) * (r - l).

    def max_area(height):
        l, r = 0, len(height) - 1
        best = 0
        while l < r:
            h = min(height[l], height[r])
            best = max(best, h * (r - l))
            if height[l] < height[r]:
                l += 1                 # the shorter wall is the bottleneck
            else:
                r -= 1
        return best

Start with the widest possible container (both ends). At each step, the shorter of the two walls is what caps the area - the taller wall could not do better paired with anything closer in, since width can only shrink from here and height is still capped by the SAME shorter wall or worse. So the only pointer worth moving is the shorter one; moving the taller one can never beat the area you already recorded, because width strictly decreases while the cap stays the same or gets worse. This is a genuine proof, not a heuristic - it is why the greedy pointer move is provably safe and the algorithm is O(n) instead of the O(n^2) all-pairs check."""},

            {"h": "THE INVARIANT SORTEDNESS BUYS YOU, AND WHERE IT BREAKS", "body": r"""The invariant every converging two-pointer algorithm relies on is: once you decide a pointer's current position cannot be part of a BETTER answer than what moving it achieves, you may discard it forever without rechecking. That reasoning is only valid because of monotonic order - on an unsorted array, moving lo forward could skip straight past the actual answer, because you have no guarantee about what value comes next. This is why "sort first" is often step zero even when the problem does not say "sorted array" - as long as you only need existence, a count, or a value (not the original index), sorting for free unlocks the technique; if you need original indices, you must carry them alongside the sorted values or fall back to a hash map. Edge cases: an empty array or one with fewer than two elements has no valid pair - guard with lo < hi so the loop body never runs on a length-0 or length-1 input. Duplicate values do not break pair-existence checks, but they DO require an explicit skip step in variants like 3Sum, where failing to skip past repeated values produces duplicate triplets in the output. And while Python's integers cannot overflow, summing two very large values in a language with fixed-width ints is exactly where this pattern silently corrupts results in C or Java - a habit worth carrying even though it costs nothing here."""},

            {"h": "WHY THIS IS O(n) AND NEVER DEGRADES", "body": r"""The complexity argument for two pointers is an aggregate one: lo only ever increases, hi only ever decreases, and the loop stops the moment they meet or cross - so across the ENTIRE run, lo can advance at most n times and hi can retreat at most n times, for a hard cap of O(n) total steps, regardless of the input's values. This is a genuine worst-case bound, not an average - unlike a hash map, there is no adversarial input that degrades two pointers to O(n^2), because the bound comes from pointer arithmetic, not from data distribution or collisions. Space is O(1) auxiliary when you only need indices or a max/count, since you are reading the existing array in place with two integers - no copy of the data is made. If the array was not already sorted and you must sort it first, that sort costs O(n log n), which then dominates the overall complexity - the two-pointer scan itself is still O(n), it is just no longer the bottleneck. It is worth stating both facts out loud in an interview: "the scan is O(n), but sorting first makes the whole solution O(n log n)" - conflating the two is a common, avoidable mistake."""},

            {"h": "SPOTTING TWO POINTERS WHEN IT IS NOT LABELED", "body": r"""The obvious tell is the word "sorted" plus "pair," "triplet," or "closest sum." The disguised version shows up as: reversing or rearranging in place ("move all zeroes to the end," "reverse a string in place" - fast/slow or left/right pointers with no sorting needed at all, since the array's OWN structure, not sortedness, provides the guarantee), or a geometry-flavored problem like Container With Most Water and Trapping Rain Water that never mentions "array" or "sorted" but is really about two indices bounding a shrinking search space. 3Sum (LeetCode 15) is the standard escalation: fix one index, then run the exact two-pointer pattern from this lesson on the remaining subarray, for O(n^2) total instead of the naive O(n^3) - recognizing that a "triplet" problem reduces to "fix one, two-pointer the rest" is the actual skill being tested, not the two-pointer loop itself, which you already know. Trapping Rain Water (LeetCode 42) pushes the same converging-pointer idea further by tracking a running max from each side instead of a single comparison. Two Sum II - Input Array Is Sorted (LeetCode 167) is the purest, least disguised version, worth drilling first if the pattern still feels shaky."""},
        ],
    },

    "dsa-3": {
        "title_check": "Hash maps & sets — your #1 tool",
        "sections": [
            {"h": "O(1) LOOKUP CHANGES WHAT PROBLEMS ARE EASY", "body": r"""A dict or set answers one question - "have I seen this?" or "what does this map to?" - in O(1) average time, by hashing the key to a bucket index instead of scanning to find it. That single capability collapses an enormous fraction of interview problems: counting frequencies, detecting duplicates, finding a complement that sums to a target, grouping items by some derived property, and checking membership all stop being O(n) scans-within-scans and become a single O(n) pass with O(1) work per element. The instruction "try it first" is not a platitude - whenever a problem contains the words "have I seen," "count," "pair that sums to," "group by," or "duplicate," write a dict or set before you consider anything fancier, because even when a hash map is not the FINAL answer, it almost always reveals the shape of the real one. The trade being made is explicit: you spend O(n) extra memory to buy O(1) lookup, converting what would be an O(n^2) nested-loop problem into an O(n) single pass - the single most common complexity win in this entire course."""},

            {"h": "THE FREQUENCY-COUNT AND SEEN-SET TEMPLATES", "body": r"""Two shapes cover most hash-map problems.

    from collections import Counter
    def freq(nums):
        counts = {}
        for x in nums:
            counts[x] = counts.get(x, 0) + 1   # or: counts[x] = counts.get(x,0)+1
        return counts
        # equivalent, faster: return Counter(nums)

    def has_complement(nums, target):
        seen = set()
        for x in nums:
            if target - x in seen:
                return True
            seen.add(x)
        return False

counts.get(x, 0) reads the current count or 0 if x is new, avoiding a KeyError from counts[x] on a first sighting - Counter does exactly this internally and is the idiomatic choice in real code. The seen-set pattern checks for the complement BEFORE adding the current element, which matters: checking after would let an element pair with itself when it should not (e.g. target=8, x=4, you do not want x to "find" itself unless the problem allows reusing the same index twice). This ordering-before-insertion detail is a one-line difference that silently changes correctness."""},

            {"h": "WORKED PROBLEM: GROUP ANAGRAMS BY A DERIVED KEY", "body": r"""LeetCode 49: given a list of strings, group the ones that are anagrams of each other.

    def group_anagrams(strs):
        groups = {}
        for s in strs:
            key = tuple(sorted(s))          # canonical form of an anagram class
            groups.setdefault(key, []).append(s)
        return list(groups.values())

The insight is that a hash map's key does not have to be the raw value - it can be any hashable DERIVED property that is identical for everything you want grouped together. Here, sorting a word's letters produces the same key for every anagram of it ("eat," "tea," and "ate" all sort to "aet"), so the dict naturally buckets them without you ever comparing strings pairwise. tuple(sorted(s)) rather than a plain sorted list is required because Python lists are not hashable - only immutable, hashable types can be dict keys or set members, which is why you convert to a tuple (or, alternatively, a character-count signature as a tuple of 26 counts, which avoids the sort's O(k log k) cost per word in favor of O(k) counting). This is the "derived key" pattern: whenever a problem says "group by," "same anagram," or "same signature," the real work is choosing the canonical key, not the hash map itself."""},

            {"h": "THE HASHABILITY INVARIANT AND WHERE COUNTING BREAKS", "body": r"""The invariant a hash map depends on is: two keys that are equal (by ==) MUST hash to the same value, and a key, once inserted, must never change in a way that alters its hash - which is exactly why Python refuses to let you use a list as a dict key or set member (mutable, unhashable) but happily accepts a tuple (immutable). Violate this by hashing a mutable object some other way and you get silent bugs: a key that "changes underneath" the dict can become permanently unreachable, still occupying space but never matching a future lookup. Edge cases worth naming explicitly: an empty input produces an empty dict or set - always confirm your code path handles "not found" (a missing key) via .get(key, default) or the in operator rather than counts[key], which raises KeyError on first sight of a new key. A single element trivially has frequency 1 and no possible pair. Duplicates are not a bug for frequency counting - colliding onto the same key IS the point - but for a pure "have I seen this value" existence set, duplicates collapse silently, which is a real bug if the problem actually needed a count rather than a yes/no. And while overflow is not a Python concern, pathologically many hash collisions are: an adversarial input engineered to collide into the same bucket degrades every operation from O(1) to O(n)."""},

            {"h": "AVERAGE O(1) IS NOT A GUARANTEE, AND WHY PYTHON RANDOMIZES HASHES", "body": r"""Dict and set operations are O(1) time on AVERAGE, assuming a reasonably uniform hash function - but the worst case, when many keys collide into the same bucket, degrades to O(n) per operation, because the implementation must then fall back to comparing keys one by one within that bucket. This is not a theoretical footnote: an attacker who can predict a hash function's behavior can craft input specifically designed to cause mass collisions, turning an expected O(n) algorithm into O(n^2) - a real denial-of-service technique historically used against web frameworks that hashed user-supplied form keys with a fixed, guessable seed. Python's defense is exactly why str and bytes hashing is RANDOMIZED per process run by default (seeded from os.urandom unless PYTHONHASHSEED is fixed) - the same string can hash to a different bucket in two different runs of your program, specifically so an attacker cannot precompute a collision set offline. Space is the other honest cost: a hash map or set is O(n) space for n stored keys, plus the underlying table is deliberately kept larger than the element count (a load factor below roughly two-thirds) to keep collision chains short - you are trading real, measurable memory for that average-case constant-time lookup, not getting it for free."""},

            {"h": "SPOTTING A HASH MAP PROBLEM WHEN IT DOES NOT ANNOUNCE ITSELF", "body": r"""The obvious tell is "have I seen this," "count occurrences," or "find the complement." The disguised version is subtler: Subarray Sum Equals K (LeetCode 560) does not look like a hash map problem at all - it looks like it wants nested loops checking every subarray's sum - until you notice that a running PREFIX sum turns "does some subarray sum to k" into "have I seen the prefix sum (current_sum - k) before," which is exactly the seen-set/seen-map pattern from this lesson applied to running sums instead of raw values, collapsing an O(n^2) all-subarrays scan into O(n). Longest Consecutive Sequence (LeetCode 128), covered from the complexity angle in the previous lesson, is really a hash-set problem in disguise: put every number in a set, then only START counting a sequence from a number whose predecessor is absent, so each number is visited a bounded number of times total rather than once per sequence it belongs to. Two Sum (LeetCode 1) is the canonical, least-disguised version - if it still is not automatic, drill it before the harder two. The general tell to internalize: any problem where brute force is "for each thing, search for some related thing" is very likely an O(n) hash map away from its intended solution."""},
        ],
    },

    "dsa-4": {
        "title_check": "Sliding window",
        "sections": [
            {"h": "A WINDOW THAT GROWS AND SHRINKS OVER CONTIGUOUS DATA", "body": r"""Sliding window is two pointers specialized for problems about CONTIGUOUS subarrays or substrings - a window [left, right] that grows by advancing right and shrinks by advancing left, while maintaining a running aggregate (a sum, a character count, a distinct-element count) incrementally rather than recomputing it from scratch for every possible window. The tell is unmistakable once you know it: "longest," "shortest," "maximum," "at most k," or "exactly k" combined with "contiguous subarray" or "substring" is sliding window, almost without exception. There are two shapes: a FIXED-size window (the problem gives you k directly - "every window of size k") just adds the incoming element and removes the outgoing one, no conditional shrinking needed; a VARIABLE-size window (the problem asks for the longest/shortest window satisfying some condition) grows right unconditionally each step, then shrinks left in a while loop whenever the current window violates the condition. Confusing these two shapes - writing a while-shrink loop when a simple add/remove would do, or vice versa - is the most common implementation mistake once the pattern is otherwise recognized correctly."""},

            {"h": "THE GROW-THEN-SHRINK TEMPLATE, LINE BY LINE", "body": r"""The canonical variable-size window:

    def longest_valid_window(s):
        left = 0
        best = 0
        window = {}                      # tracks whatever makes a window "valid"
        for right in range(len(s)):
            c = s[right]
            window[c] = window.get(c, 0) + 1     # grow: absorb the new element
            while not is_valid(window):          # shrink while broken
                out = s[left]
                window[out] -= 1
                if window[out] == 0:
                    del window[out]
                left += 1
            best = max(best, right - left + 1)   # record only once valid
        return best

right sweeps forward exactly once, unconditionally - that single for loop is what keeps the outer cost at O(n). The while loop shrinks left as many times as needed to restore validity BEFORE you record the answer - recording best inside the while loop, or before it finishes, would let an invalid window count, which is the single most common correctness bug in sliding-window code. Each shrink step must undo exactly what the corresponding grow step did (decrement the count, delete the key at zero) - forgetting to update the aggregate on shrink, only ever updating it on grow, is the second most common bug, and it silently corrupts every window after the first shrink."""},

            {"h": "WORKED PROBLEM: MINIMUM WINDOW SUBSTRING", "body": r"""LeetCode 76: given strings s and t, find the smallest substring of s that contains every character of t (with at least its required multiplicity).

    def min_window(s, t):
        need = Counter(t)
        missing = len(t)                 # count of chars still owed, not distinct
        left = 0
        best = (0, len(s) + 1)
        for right, c in enumerate(s):
            if need[c] > 0:
                missing -= 1
            need[c] -= 1
            while missing == 0:                       # window is currently valid
                if right - left < best[1] - best[0]:
                    best = (left, right + 1)
                out = s[left]
                need[out] += 1
                if need[out] > 0:
                    missing += 1                       # window just broke
                left += 1
        lo, hi = best
        return s[lo:hi] if hi <= len(s) else ""

missing counts total characters still owed (not distinct characters), which is the detail that trips people up - need[c] can go negative for characters s has extra of, and only crossing from 0 to positive on removal (or positive to 0 on addition) should change missing. Because we want the MINIMUM valid window, we shrink aggressively every single time the window is valid, recording best before each shrink attempt - the inverse emphasis from "longest," where you shrink only until valid and stop."""},

            {"h": "THE INVARIANT: VALID BEFORE YOU RECORD, UPDATED ON BOTH ENDS", "body": r"""The loop invariant every sliding-window solution depends on is: at the moment you record or compare against best, the window [left, right] must currently satisfy the problem's condition - not "used to," not "will after one more shrink." Two specific bugs break this. First, recording best on every iteration of the outer for loop regardless of validity, instead of only when the while-shrink loop has finished (or only outside the while body, for the "longest" shape) - this silently counts invalid windows as candidates. Second, updating the tracked aggregate only when growing and never when shrinking (or the reverse) - the moment left moves, whatever count, sum, or distinct-set the window tracks must be updated to reflect the element that just LEFT, or every subsequent comparison uses stale state. Edge cases: an empty string has no valid window - guard for len(s) == 0 up front, since an empty for-loop body already handles it correctly if best is initialized sensibly. A single character is a window of size one, trivially valid or invalid on its own. A string of all-identical or all-distinct characters forces the window to shrink on almost every step or never shrink at all - both are useful mental stress tests to run your logic against by hand before trusting it on real input. A fixed window size k larger than the input length must be guarded explicitly, or the loop silently does nothing useful."""},

            {"h": "WHY THE NESTED LOOP IS SECRETLY O(n)", "body": r"""Sliding window LOOKS like a nested loop - a for loop containing a while loop - which makes it tempting to call it O(n^2), but that is wrong, and proving why is a genuinely useful aggregate-analysis argument to be able to give out loud. left only ever increases, moving forward one step at a time, and it can move at most n times across the ENTIRE run of the algorithm, regardless of how the while loop is nested inside the for loop - every "shrink" permanently consumes one unit of left's total forward budget. So although the while loop's TOTAL iteration count across the whole algorithm can be as large as n, that cost is amortized across all n iterations of the outer for loop rather than paid fresh on each one - the true total work is O(n) + O(n) = O(n), not O(n) * O(n). This is the exact same aggregate argument used for the monotonic-stack pattern two lessons from now - both rely on "each element is added once and removed at most once" to collapse an apparently quadratic shape into a linear one. Space is typically O(min(n, alphabet size)) for the tracking dict or set - often effectively O(1) when the alphabet is bounded, like 26 lowercase letters or 256 byte values, even though n itself is unbounded."""},

            {"h": "SPOTTING A WINDOW PROBLEM AND ITS EXACTLY-K TRICK", "body": r"""The obvious tell is "contiguous subarray/substring" plus a longest/shortest/max-sum/at-most-k phrasing. Fixed-size windows are the easy special case - "every window of size k" tells you immediately there is no shrink logic needed at all, just add-then-remove each step. The genuinely disguised trick is "exactly k": problems phrased as "exactly k distinct characters" or "exactly k odd numbers" rarely have a clean direct window condition, because "exactly" is neither monotonically easier nor harder as the window grows the way "at most" is - the fix is computing atMost(k) - atMost(k-1), since both of those ARE well-behaved at-most-k window problems you already know how to solve, and their difference is exactly the exact-k count. Longest Repeating Character Replacement (LeetCode 424) hides the pattern behind a "replace up to k characters" framing - the real condition is (window length - count of the most frequent character) <= k. Permutation in String (LeetCode 567) is a fixed-size window in disguise, since a permutation check is just "does this window's character-count signature match the target's" for a window sized exactly len(target). Minimum Window Substring, just worked above, is the hardest common variant and worth returning to once the easier ones are automatic."""},
        ],
    },

    "dsa-5": {
        "title_check": "Stacks & queues",
        "sections": [
            {"h": "LIFO FOR NESTING, FIFO FOR ORDER", "body": r"""A stack is last-in-first-out: the most recently added item is the first one removed, which matches any problem shaped like nesting, matching, undoing, or "what is the most recent unresolved thing" - matching brackets, undo history, evaluating an expression with operator precedence, and depth-first traversal (explicitly, via your own stack, when you are not using recursion's implicit call stack to do the same job). A queue is first-in-first-out: items leave in the same order they arrived, which matches "process in arrival order" or "explore level by level" - breadth-first search is a queue's defining use case. In Python, a plain list already IS an efficient stack: append() and pop() both operate on the end and are O(1). A list is a BAD queue, though - pop(0) or insert(0, x) must shift every remaining element down one slot, making them O(n) each; collections.deque is the fix, giving O(1) appends and pops from BOTH ends, and is what a real queue (or a fast stack, for that matter) should be built from. Reaching for list.pop(0) in a hot loop is a fast way to silently turn an O(n) algorithm into O(n^2)."""},

            {"h": "THE MONOTONIC STACK TEMPLATE, LINE BY LINE", "body": r"""A monotonic stack keeps its contents in strictly increasing or decreasing order by popping elements that violate that order before pushing the new one - the classic use is "find the next greater element for every position."

    def next_greater(nums):
        n = len(nums)
        result = [-1] * n
        stack = []                        # holds INDICES, kept decreasing in value
        for i, x in enumerate(nums):
            while stack and nums[stack[-1]] < x:
                j = stack.pop()
                result[j] = x              # x is the next greater element for j
            stack.append(i)
        return result

The stack holds indices, not values, specifically so you can write the answer back to the right position. The while loop pops every previously-seen index whose value is smaller than the CURRENT value - each of those popped indices has just found its answer (the current x), because x is the first value to its right that beats it. Only after the while loop settles do you push the current index - at that point everything left in the stack is still waiting for something bigger to come along later. Values that never get popped keep their -1 default, meaning "no greater element exists to the right.\""""},

            {"h": "WORKED PROBLEM: DAILY TEMPERATURES", "body": r"""LeetCode 739: given daily temperatures, for each day return how many days you must wait for a warmer temperature (0 if none).

    def daily_temperatures(temps):
        n = len(temps)
        answer = [0] * n
        stack = []                        # indices of days awaiting a warmer day
        for i, t in enumerate(temps):
            while stack and temps[stack[-1]] < t:
                j = stack.pop()
                answer[j] = i - j          # distance to the day that beat it
            stack.append(i)
        return answer

This is the exact same monotonic-stack skeleton as the previous section, with one change: instead of recording the VALUE that beat a popped index, you record the DISTANCE (i - j) between the popped day and today, since the question asks "how many days" rather than "what temperature." Recognizing that Daily Temperatures and Next Greater Element are the identical algorithm with a one-line difference in what gets stored at the moment of a pop is exactly the kind of pattern-transfer this whole course is trying to build - once you have written the skeleton once, every "next greater/smaller, or how far until one" problem is the same four lines with a different payload."""},

            {"h": "THE INVARIANT THAT MAKES A MONOTONIC STACK WORK", "body": r"""The invariant is that the stack's contents remain strictly monotonic (here, strictly increasing bottom-to-top) at every point BETWEEN iterations - the while loop's entire job is to restore that invariant before pushing, by evicting everything the new element has just outgrown. Whether the comparison is strict (<) or non-strict (<=) is not a stylistic choice - it decides how EQUAL values are treated, and getting it backwards is a common off-by-one: using < means an equal value does not count as "greater" and is left for a strictly larger one later, while using <= would treat equal values as already resolved. Edge cases: an empty input means the stack never receives a push and the loop body never runs - result should default sensibly (usually to -1 or 0, as in the two worked examples). A single element has nothing to compare against and keeps its default. A strictly decreasing sequence (each new value smaller than the last) means the while loop never fires - the stack grows to hold every index, and every position ends up with the sentinel default, since nothing to the right is ever bigger. A strictly increasing sequence is the opposite extreme: every new element immediately pops the previous one, so the stack never holds more than one item at a time, which is the best case for the number of pop operations but does not change the asymptotic bound at all."""},

            {"h": "WHY THE WHILE LOOP DOES NOT MAKE IT O(n^2)", "body": r"""As with sliding window, the nested while-inside-for shape looks like it should be O(n^2), and again the correct argument is an aggregate one, not a per-iteration one: every index is pushed onto the stack EXACTLY once (during its own iteration of the for loop) and popped AT MOST once (whenever some later, larger element evicts it) - across the whole run, total pushes are n and total pops are at most n, so total stack operations are bounded by 2n regardless of how unevenly they are distributed across iterations. That gives O(n) total time, even though a single iteration of the for loop can, in the worst case, trigger a burst of many pops back to back (imagine a strictly decreasing run followed by one huge value - that one value pops the entire stack in a single iteration, but it can only ever do that once, because every one of those elements is now gone for good). Space is O(n) worst case, when the input is monotonic in the "wrong" direction and nothing ever gets popped before the end. Recognize this same "pushed once, popped at most once" aggregate argument by name - it recurs constantly in stack, window, and two-pointer analyses, and being able to state it out loud is often the difference between an interviewer trusting your complexity claim and asking you to prove it."""},

            {"h": "SPOTTING STACK VS QUEUE UNDER A DIFFERENT NAME", "body": r"""Plain stack problems announce themselves with nesting or matching language - "valid parentheses," "undo," "simplify a path," "evaluate an expression." Monotonic-stack problems are subtler because the word "stack" never appears - "next greater/smaller element," "daily temperatures," "span" (how far back does a comparable or larger value extend), and "largest rectangle in a histogram" (a harder variant using the same skeleton on bar heights) all scream monotonic stack once you know the shape, but read as ordinary array problems on first sight. Queue problems are usually easier to spot because "level by level," "shortest path in an unweighted graph," and "process in the order received" are hard to phrase without giving away FIFO. Named problems worth drilling: Valid Parentheses (LeetCode 20) for the plain-stack baseline, Daily Temperatures (LeetCode 739) and Next Greater Element I (LeetCode 496) for the monotonic-stack skeleton, and Min Stack (LeetCode 155) for a genuinely different stack trick - augmenting every push with the current running minimum so that getMin() is O(1), which is less about traversal order and more about a stack that carries extra state alongside each element."""},
        ],
    },

    "dsa-6": {
        "title_check": "Linked lists",
        "sections": [
            {"h": "NODES INSTEAD OF INDICES", "body": r"""A linked list trades an array's O(1) random access for O(1) insertion and deletion GIVEN a reference to the relevant node - there is no arr[i], only "follow .next from wherever you currently are." Each node holds a value and a reference to the next node (or None at the end); the list itself is just a reference to the first node, head. This is the right tool whenever a problem hands you a head directly (which tells you the intended solution manipulates pointers rather than indices) or whenever insertions and deletions vastly outnumber lookups by position - a real-world LRU cache's internal ordering, for instance, is exactly this trade made deliberately. The mental shift from arrays is total: you cannot ask "what is the 5th element" without walking five .next hops from the start, an O(n) operation that would be O(1) on an array - but you CAN splice a node out of the middle in O(1) once you are standing at it, which an array can only do in O(n) because every following element must shift down. Every linked-list problem is really asking: can you rewire a small, fixed number of .next references to achieve a global effect, without ever needing an index?"""},

            {"h": "THE THREE-POINTER REVERSAL TEMPLATE, LINE BY LINE", "body": r"""Reversing a singly linked list in place is the single most important template in this lesson, because nearly every other linked-list trick is a variation of "carefully rewire pointers while walking forward."

    class Node:
        def __init__(self, val, nxt=None):
            self.val = val
            self.next = nxt

    def reverse(head):
        prev = None
        cur = head
        while cur:
            nxt = cur.next        # save before overwriting - the whole trick
            cur.next = prev       # rewire this node to point backward
            prev = cur            # advance prev to where cur just was
            cur = nxt             # advance cur to the node saved in step 1
        return prev                # prev is the new head once cur runs out

The critical line is nxt = cur.next, executed BEFORE cur.next is reassigned - skip it and the moment you write cur.next = prev, you have permanently lost your only reference to the rest of the original list, since nothing else pointed at it. prev starts as None specifically so the OLD head's .next correctly becomes None (the new tail) rather than dangling. The loop's invariant, covered in a later section, is that prev always points to a fully-reversed sublist and cur to the first not-yet-reversed node."""},

            {"h": "WORKED PROBLEM: MERGE TWO SORTED LISTS WITH A DUMMY HEAD", "body": r"""LeetCode 21: merge two already-sorted linked lists into one sorted list by rewiring, not by copying values into a new structure.

    def merge_two_lists(l1, l2):
        dummy = Node(0)               # placeholder, never part of the real answer
        tail = dummy
        while l1 and l2:
            if l1.val <= l2.val:
                tail.next = l1
                l1 = l1.next
            else:
                tail.next = l2
                l2 = l2.next
            tail = tail.next
        tail.next = l1 if l1 else l2   # attach whatever remains, already sorted
        return dummy.next              # skip the placeholder

The dummy node exists purely to eliminate a special case: without it, you would need extra code to decide which of l1 or l2 becomes the head, since "the head" is not known until you compare the first two values. Instead you always attach nodes to tail.next and advance tail, and only at the very end do you return dummy.next, discarding the placeholder itself. This dummy-head trick generalizes to almost any linked-list problem that BUILDS a new list by splicing existing nodes - it removes the "what if the new list is empty so far" branch entirely."""},

            {"h": "TWO INVARIANTS, AND WHAT BREAKS THEM", "body": r"""Reversal's invariant: at the top of every loop iteration, prev is the head of a CORRECTLY reversed sublist of everything processed so far, and cur is the first node not yet touched - this holds from the very first iteration (prev=None is vacuously "a reversed empty sublist") and is preserved by each iteration's four lines, which is exactly why the loop is correct by induction rather than by careful case-counting. It breaks the instant nxt is not saved before cur.next is overwritten - a silent, catastrophic bug, since the rest of the list simply vanishes with no error raised. Floyd's cycle detection (fast pointer moves two steps, slow moves one) has its own invariant: if a cycle exists, fast is gaining exactly one node on slow per iteration relative to the cycle's length, so by the pigeonhole principle they MUST meet within one full lap of the cycle - it breaks if you advance fast before confirming both fast and fast.next are non-None, which crashes on any list without a cycle. Edge cases across both: an empty list (head is None) must be checked before dereferencing head.next anywhere. A single node is either its own trivial reversal or, if it points to itself, a cycle of length one. And cycle detection must compare NODE IDENTITY, never value - two nodes can legitimately hold equal values with no cycle at all, so "have I seen this value" is the wrong check entirely; you need "have I seen this exact node," which for genuine cycle detection is what makes Floyd's pointer-based approach necessary rather than a value-based seen-set."""},

            {"h": "O(1) SPACE ITERATIVELY, O(n) RECURSIVELY - AND A REAL LIMIT", "body": r"""Iterative reversal is O(n) time and O(1) auxiliary space - three pointer variables, regardless of list length. A recursive reversal (reverse the rest of the list first, then fix up the current node's links on the way back up) is also O(n) time but O(n) SPACE, because every recursive call adds a frame to the call stack that is not released until the base case returns and everything unwinds - n nodes means n stack frames alive simultaneously at the deepest point. This is not a minor footnote in Python specifically: Python's default recursion limit is around 1000 frames, so a naive recursive reversal (or any recursive linked-list traversal) on a list of even a few thousand nodes raises RecursionError before it produces a wrong answer - the iterative version has no such ceiling. Floyd's cycle detection is the space-complexity payoff of this entire lesson: the alternative "obvious" approach, storing every visited node in a hash set and checking membership each step, is also O(n) time but costs O(n) SPACE for that set, while two pointers moving at different speeds solve the identical problem in O(1) space - the same time complexity, a strictly better space complexity, purchased entirely by a cleverer invariant instead of extra memory."""},

            {"h": "RECOGNIZING POINTER PROBLEMS UNDER A DIFFERENT PHRASING", "body": r""""Given a head," "reverse," "detect a cycle," "find the middle," "kth node from the end," and "is this list a palindrome" are all tells for pointer manipulation rather than array-style indexing. The disguised skill in several of these is realizing you do not need a separate pass to count length first: "kth from the end" is solved by advancing one pointer k steps ahead, then moving both pointers together until the lead pointer hits the end - the trailing pointer is now exactly k from the end, without ever computing the list's total length. "Middle of the list" uses the same fast/slow idea as cycle detection - advance fast two steps for every one step of slow, and when fast reaches the end, slow is standing at the middle, again with no length-counting pass needed. Named problems worth drilling in order: Reverse Linked List (LeetCode 206) for the raw template, Middle of the Linked List (LeetCode 876) and Linked List Cycle (LeetCode 141) / Linked List Cycle II (LeetCode 142) for the fast/slow family, and Merge Two Sorted Lists (LeetCode 21) for the dummy-head splicing pattern - between them these cover essentially every pointer-rewiring idea the rest of this track will assume you already have on reflex."""},
        ],
    },

    "dsa-7": {
        "title_check": "Binary search",
        "sections": [
            {"h": "HALVING A SEARCH SPACE, NOT JUST AN ARRAY", "body": r"""Binary search's textbook form - find a target in a sorted array by repeatedly checking the middle and discarding the half that cannot contain it - is only the entry point. The generalization that actually matters in interviews is: binary search works on ANY monotonic predicate over a range, not just a literal sorted array. If you can write a function feasible(x) that is False for small x and True for all x above some threshold (or vice versa) - even if you never materialize an array at all - you can binary search directly on the ANSWER, searching over possible answer values rather than over array indices. This reframing is why the tell "smallest value that satisfies some condition" or "minimize the maximum" is binary search even when no array is sorted anywhere in the problem statement. The right tool the moment you can phrase the problem as "find the boundary where a yes/no answer flips," because a monotonic yes/no boundary is exactly what halving the search space each step is designed to locate in O(log n) checks instead of testing every candidate one at a time."""},

            {"h": "THE lo/hi TEMPLATE AND ITS BOUNDARY VARIANTS", "body": r"""    def binary_search(nums, target):
        lo, hi = 0, len(nums) - 1
        while lo <= hi:
            mid = lo + (hi - lo) // 2      # not (lo+hi)//2 - avoids overflow
            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1

lo + (hi - lo) // 2 rather than (lo + hi) // 2 avoids overflow in fixed-width languages where lo and hi could both be near the maximum representable integer - Python's arbitrary-precision ints never overflow, but writing it the safe way is a habit worth keeping since interviews are not always in Python. while lo <= hi (not <) is required so a search space of exactly one remaining element still gets checked, not skipped. The four boundary variants that trip people up: for "find ANY match," lo=mid+1 and hi=mid-1 as above; for "find the LEFTMOST match," you narrow hi=mid even on a match (never stop early) and only shrink lo=mid+1 when nums[mid] < target; for "find the RIGHTMOST match," symmetrically lo=mid on a match. Getting lo=mid instead of lo=mid+1 wrong causes an infinite loop the moment lo and hi become adjacent."""},

            {"h": "WORKED PROBLEM: BINARY SEARCH ON THE ANSWER", "body": r"""LeetCode 875, Koko Eating Bananas: given piles of bananas and h hours, find the minimum eating speed k such that Koko finishes all piles within h hours.

    def min_eating_speed(piles, h):
        def hours_needed(k):
            return sum((p + k - 1) // k for p in piles)   # ceil division per pile

        lo, hi = 1, max(piles)
        while lo < hi:
            mid = lo + (hi - lo) // 2
            if hours_needed(mid) <= h:      # mid is fast enough - maybe go slower
                hi = mid
            else:
                lo = mid + 1                # too slow - must eat faster
        return lo

Notice there is no array of "speeds" to index into at all - lo and hi bound a RANGE of possible answers (1 to the largest pile), and hours_needed(k) is the monotonic predicate: as k increases, hours needed can only decrease or stay the same, never increase. That monotonicity is exactly what makes discarding half the range valid at every step, identical in spirit to discarding half a sorted array, even though nothing here is literally sorted. This is "binary search on the answer" - the single most commonly disguised form of the pattern in real interviews."""},

            {"h": "THE INVARIANT, AND THE OFF-BY-ONE THAT BREAKS IT", "body": r"""The invariant every correct binary search maintains is: if the answer exists, it is ALWAYS still somewhere within [lo, hi] at the top of every loop iteration - each branch must narrow the range without ever discarding the region that could contain the answer. This is exactly why lo = mid + 1 (not lo = mid) is required after ruling out mid entirely: mid has been checked and eliminated, so the next search must start strictly past it - using lo = mid instead can leave lo and hi stuck adjacent forever, an infinite loop, because mid = lo + (hi-lo)//2 rounds down and can re-select lo itself indefinitely. The leftmost-match variant's hi = mid (not hi = mid - 1) on an exact match is the mirror case: mid might BE the leftmost match, so you cannot discard it, only continue searching to its left. Edge cases: an empty array gives lo=0, hi=-1, so the loop condition is false immediately and you correctly return "not found" without ever computing mid. A single-element array must still run the loop body exactly once and terminate correctly - a common bug is a loop guard that accidentally skips arrays of length one. Duplicate values are the entire REASON leftmost/rightmost variants exist - plain binary search only guarantees finding "a" match, with no guarantee about which one among several equal values."""},

            {"h": "O(log n) CHECKS, BUT THE CHECK ITSELF HAS A COST", "body": r"""Binary search is O(log n) time because each iteration discards HALF the remaining search space - a million elements needs at most about 20 comparisons to exhaust, a billion needs about 30, which is what makes it viable at input sizes where even a single O(n) pass would be too slow. Space is O(1) for the iterative form (two or three integer variables) versus O(log n) for a recursive formulation, since each recursive call that halves the range adds one stack frame, and there are about log2(n) halvings before the base case. The subtlety worth stating honestly in an interview: for "binary search on the answer," the OVERALL complexity is O(log(range) * cost of one feasibility check), and the check itself is very often not O(1) - in the Koko Eating Bananas example above, hours_needed(k) is an O(number of piles) scan every single time it is called, so the true total cost is O(log(max_pile) * len(piles)), not simply O(log n). Interviewers specifically probe whether you notice that the "cheap" O(log n) search wraps an expensive predicate, since conflating "binary search is fast" with "the whole algorithm is fast" is a common and revealing mistake."""},

            {"h": "SPOTTING THE SEARCH-SPACE REFRAME", "body": r"""The obvious form is "sorted array, find X," which is Binary Search (LeetCode 704) itself and should be automatic. The first escalation is Find First and Last Position of Element in Sorted Array (LeetCode 34), which forces you to actually implement the leftmost/rightmost boundary variants rather than plain existence search. The real skill this lesson is building toward is recognizing binary-search-on-the-answer where no array is sorted anywhere in sight: "minimum speed/capacity/time to finish by a deadline," "smallest divisor such that the sum stays under a limit," and similar "minimize the maximum" or "maximize the minimum" phrasings are the tell - whenever increasing a candidate answer makes a yes/no feasibility check monotonically easier or harder, you can binary search directly over candidate answers instead of testing each one linearly. Search in Rotated Sorted Array (LeetCode 33) drills a different disguise: the array is sorted but ROTATED, so plain nums[mid] < target logic breaks, and the real skill is figuring out which HALF (left of mid or right of mid) is still guaranteed sorted before deciding which side to discard - the invariant survives, but which comparison proves it takes more care."""},
        ],
    },

    "dsa-8": {
        "title_check": "Recursion & backtracking",
        "sections": [
            {"h": "A BASE CASE, A SMALLER CASE, AND AN UNDO STEP", "body": r"""Recursion needs exactly two pieces to be correct: a base case that stops it (the smallest input you can answer directly, with no further recursive call), and a recursive case that solves a strictly smaller version of the same problem and combines that result into the current answer. Backtracking is recursion specialized for exploring every possible sequence of choices - at each step you try a choice, recurse into the consequences of having made it, and then explicitly UNDO that choice before trying the next sibling option, so that every recursive call starts from a clean, shared state rather than an accumulating one. That undo step is the single detail beginners omit, because it is invisible when it works and catastrophic when it does not - forgetting it means every later branch of the exploration silently inherits leftover state from branches that have already finished, corrupting results in a way that often only shows up on inputs large enough to reach a second sibling branch. The right tool whenever a problem says "all subsets," "all permutations," "all combinations," or describes a search through a maze or decision tree of choices where you need every valid path, not just one."""},

            {"h": "THE GENERIC BACKTRACKING SKELETON, LINE BY LINE", "body": r"""    def backtrack(path, choices, results):
        if is_complete(path):              # base case: a full candidate
            results.append(path[:])        # COPY - path itself keeps mutating
            return
        for choice in remaining(choices, path):
            path.append(choice)            # make the choice
            backtrack(path, choices, results)
            path.pop()                     # undo it before the next sibling

path[:] (or list(path)) is not decoration - path is a single shared list mutated throughout the entire recursion, so appending the SAME reference to results without copying means every entry in results ends up pointing at the same, eventually-empty list once all the pop() calls unwind. path.append(choice) followed later by path.pop() is the make/undo pair - between them, the recursive call sees path WITH the choice included, but the moment that call returns, path is restored to exactly its pre-choice state so the next iteration of the for loop starts clean. remaining(choices, path) is a placeholder for whatever choice-filtering logic a specific problem needs - "elements not yet used," "elements after the current index," or "values that keep a partial sum under a target" are all just different remaining() implementations wrapped around the identical skeleton."""},

            {"h": "WORKED PROBLEM: COMBINATION SUM, PRUNING THE TREE", "body": r"""LeetCode 39: given distinct candidates and a target, find every combination (candidates can repeat) that sums exactly to target.

    def combination_sum(candidates, target):
        candidates.sort()                      # enables pruning below
        results = []
        def backtrack(start, path, remaining):
            if remaining == 0:
                results.append(path[:])
                return
            for i in range(start, len(candidates)):
                c = candidates[i]
                if c > remaining:               # sorted: everything after is worse too
                    break
                path.append(c)
                backtrack(i, path, remaining - c)   # i, not i+1 - reuse allowed
                path.pop()
        backtrack(0, [], target)
        return results

Sorting first is not cosmetic - it turns "c > remaining, skip and keep checking" into "c > remaining, BREAK entirely," since every candidate after i in sorted order is at least as large, so none of them could work either. This pruning is the difference between exploring a genuinely bounded tree and exploring every combination blindly. Passing i (not i+1) into the recursive call is what allows reusing the same candidate multiple times, contrasted with permutations or subsets, which advance the start index and never revisit an element."""},

            {"h": "THE INVARIANT recursion DEPENDS ON, AND HOW STATE LEAKS", "body": r"""The invariant is that at the moment backtrack is called, path accurately represents the sequence of choices made so far on the CURRENT branch only - no residue from a sibling branch that already finished exploring and returned. This holds only if every mutation made before a recursive call (append to a list, mark a value used in a visited set, add to a running sum) is undone in the exact reverse order immediately after that call returns - skip the pop(), or forget to un-mark a "used" flag, and the very next sibling iteration explores with corrupted state that looks locally correct but produces wrong or duplicate answers, often only on inputs deep enough to reach a second sibling. Edge cases: an empty candidate list or an already-zero target should hit the base case immediately - trace through what remaining == 0 evaluates to before any loop iteration runs to be sure. Duplicate VALUES in the input (not duplicate choices of index) are the classic backtracking trap distinct from every earlier lesson: if candidates contains repeated values, naively looping over indices in Subsets II or Permutations II style problems generates duplicate OUTPUT combinations unless you explicitly skip over a repeated value when it is not the first occurrence at the current recursion depth. And because Python's default recursion limit is roughly 1000, a backtracking search whose PATH LENGTH (not branching factor) can grow past that - not a typical concern for combination/subset problems, but a real one for maze or grid-path problems - needs either an iterative rewrite or sys.setrecursionlimit."""},

            {"h": "WHY THE STATE SPACE, NOT A CLEVER TRICK, SETS THE COST", "body": r"""Backtracking's complexity is fundamentally the size of the decision tree it explores, and there is rarely a way to make that asymptotically smaller than the number of valid outputs plus the dead ends actually visited - Subsets is O(2^n) because every element is independently in or out; Permutations is O(n!) because every ordering is distinct; Combination Sum's complexity depends on both the target and the candidate values, since pruning (the sorted-break trick above) reduces the CONSTANT factor and cuts off entire dead subtrees early, but does not change the fact that the underlying search space is exponential in the worst case. This is the most important honest fact in this lesson: pruning makes exponential algorithms tractable at competition and interview scale, but it does not make them polynomial - do not claim "O(n)" or even "O(n^2)" for a backtracking solution just because it "usually finishes fast" on typical test inputs, since the worst-case bound is still exponential and an interviewer checking your complexity analysis will notice the gap immediately. Space is O(depth of recursion) for the call stack plus O(depth) for path itself, since path's length never exceeds how deep the current branch has gone - separate from results, which can be as large as the total number of valid outputs and dominates space whenever that count is itself exponential."""},

            {"h": "RECOGNIZING BACKTRACKING WHEN THE WORD NEVER APPEARS", "body": r""""All subsets," "all permutations," "all combinations that sum to," and "every way to partition/arrange" are the direct tells. The disguised version shows up as grid or board search: "find a path through this maze," "does this word exist in this letter grid," or "place n queens so none attack each other" never say "backtracking," but each one is "make a choice (a direction, a placement), recurse into its consequences, undo it if that path fails, try the next choice" - identical in structure to Combination Sum, just with a spatial choice-space instead of a list of candidates. A second disguise worth naming: some problems that LOOK like they want a greedy or purely iterative answer ("can this string be segmented into dictionary words") actually need backtracking (or its memoized cousin, dynamic programming, two lessons ahead) because a greedy first choice can lead down a dead end that only reveals itself several choices later - the giveaway is that no simple local rule decides the right first choice without looking ahead. Named problems worth drilling: Subsets (LeetCode 78), Permutations (LeetCode 46) for the raw templates, Combination Sum (LeetCode 39) for pruning, and N-Queens (LeetCode 51) for backtracking over a 2D constraint rather than a flat list."""},
        ],
    },

    "dsa-9": {
        "title_check": "Trees, BFS & DFS",
        "sections": [
            {"h": "DEEP FIRST OR LEVEL FIRST: TWO WAYS TO WALK A BRANCHING STRUCTURE", "body": r"""A binary tree node holds a value plus references to a left and right child (either or both possibly None); there is no indexing, only "start at the root and follow child references." DFS (depth-first search) commits to one branch and follows it all the way down before backtracking - implemented either with plain recursion (the call stack IS the DFS stack, implicitly) or with an explicit stack if you need iterative control. BFS (breadth-first search) instead explores every node at the current depth before moving to the next depth, which requires a queue, since you need to process nodes in the order you discovered them, not the order you most recently discovered them. The right tool split is clean: DFS naturally answers "does a path exist," "what is the total/deepest/shallowest," or anything expressible as "combine this node's answer with its children's answers" - a recursive definition mirrors a recursive structure. BFS naturally answers "what is here level by level" or "what is the SHORTEST path in an unweighted tree or grid," because BFS visits nodes in strictly non-decreasing distance-from-start order, which DFS does not guarantee at all."""},

            {"h": "THE RECURSIVE DFS AND QUEUE-BASED BFS TEMPLATES", "body": r"""    class TreeNode:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    def max_depth(node):                    # DFS: combine children's answers
        if node is None:
            return 0                        # base case: empty tree has depth 0
        return 1 + max(max_depth(node.left), max_depth(node.right))

    from collections import deque
    def level_order(root):                  # BFS: queue, layer by layer
        if root is None:
            return []
        result, queue = [], deque([root])
        while queue:
            level = []
            for _ in range(len(queue)):     # freeze this layer's size first
                node = queue.popleft()
                level.append(node.val)
                if node.left:  queue.append(node.left)
                if node.right: queue.append(node.right)
            result.append(level)
        return result

max_depth's base case (None returns 0) is what makes the recursive combination correct for a leaf: a leaf's two children are both None, both contribute 0, so a leaf correctly reports depth 1. In level_order, for _ in range(len(queue)) freezing the current queue's length BEFORE the inner loop starts is what separates levels - without it, children appended during this layer's processing would get consumed in the same iteration, merging levels together."""},

            {"h": "WORKED PROBLEM: VALIDATE A BINARY SEARCH TREE", "body": r"""LeetCode 98: determine whether a binary tree satisfies the BST property - every node's value strictly between a valid LOW and HIGH bound, not merely greater than its immediate left child and less than its immediate right child.

    def is_valid_bst(node, low=float('-inf'), high=float('inf')):
        if node is None:
            return True                       # empty subtree is vacuously valid
        if not (low < node.val < high):
            return False
        return (is_valid_bst(node.left,  low,       node.val) and
                is_valid_bst(node.right, node.val,  high))

The bug this problem is specifically designed to catch: checking only node.left.val < node.val < node.right.val locally, at every node, LOOKS like it validates the whole tree, but it does not - a node three levels down could be locally fine relative to its immediate parent while still violating the bound set by an ANCESTOR further up. The fix is threading a shrinking (low, high) RANGE down through the recursion - every recursive call narrows the valid range for its subtree using the parent's value as one new bound, so violations against a distant ancestor are caught, not just against an immediate parent. This is the single most common wrong-but-plausible submission for this problem on LeetCode."""},

            {"h": "THE GLOBAL-BOUND INVARIANT, AND WHAT SKEWS BREAK", "body": r"""The invariant Validate BST depends on is: at every recursive call, (low, high) already encodes every constraint imposed by every ancestor visited so far, not just the immediate parent - each call narrows that window using its own value before handing it down, so no ancestor's constraint is ever "forgotten" by the time you reach a distant descendant. This generalizes: any tree recursion whose correctness depends on more than immediate-parent-child comparisons needs some accumulated state threaded downward as extra parameters, not just the two child pointers. Edge cases: an empty tree (root is None) is vacuously valid for BST checking and has depth 0 - both base cases return immediately with no recursive call, which is easy to get backwards (returning False or -1 by mistake). A single node is trivially a valid BST and has depth 1. Duplicate values raise a real design question rather than a bug: does the BST property use strict < or allow <=? - LeetCode's Validate BST requires STRICT inequality, so a tree with two equal values anywhere in an ancestor-descendant relationship is invalid, which surprises people who assume "greater or equal" is fine. The recursion-depth concern from earlier lessons is sharpest here: a completely SKEWED tree (every node has only a left child, or only a right child) has height n rather than log n, so recursive DFS on a skewed tree of a few thousand nodes can hit Python's recursion limit exactly the way a naive linked-list recursion does - a tree is not automatically "shallow" just because it is a tree."""},

            {"h": "O(n) TIME ALWAYS, BUT SPACE DEPENDS ON SHAPE", "body": r"""Both DFS and BFS visit every node exactly once, so both are O(n) time regardless of tree shape - the honest complexity difference between them is entirely in SPACE, and it depends on the tree's shape in opposite ways. DFS space is O(h), the height of the tree, because that is the deepest the call stack (or an explicit stack) ever gets - for a balanced tree, h is O(log n), a real savings; for a completely skewed tree, h degrades to O(n), no better than BFS in the worst case. BFS space is O(w), the maximum WIDTH of the tree at any single level, because the queue must hold an entire level at once before moving to the next - for a balanced tree, the last level can hold close to n/2 nodes, so BFS space is O(n) even though the tree itself is shallow. The practical consequence: for a very wide, shallow tree, DFS is the more memory-efficient traversal; for a very deep, narrow (skewed) tree, BFS's queue never gets very large while DFS's recursion depth becomes the bottleneck - "just use DFS" or "just use BFS" is not a universal answer, the tree's actual shape decides which space bound you are really paying."""},

            {"h": "SPOTTING WHICH TRAVERSAL A PROBLEM WANTS", "body": r""""Depth," "path sum," "is this a valid X," and anything phrased as "combine a node's answer with its children's" are DFS tells, because the natural recursive definition mirrors the recursive structure directly. "Level," "level order," "shortest path in an unweighted tree or grid," and "minimum number of steps" are BFS tells, because only BFS guarantees you reach nodes in strictly increasing distance order, which matters enormously the instant "shortest" or "minimum steps" appears - a DFS-based shortest-path attempt on an unweighted structure is not simply slower, it can be OUTRIGHT WRONG unless you additionally track and compare full path lengths, which defeats the point of using DFS in the first place. Grids deserve a specific callout: a 2D grid is a tree/graph in disguise where each cell's neighbors (up, down, left, right) play the role of children, and "shortest path from corner to corner" or "minimum steps to reach a target" on a grid is BFS, full stop, exactly as it would be on an explicit tree. Named problems worth drilling: Maximum Depth of Binary Tree (LeetCode 104) for the rawest DFS template, Binary Tree Level Order Traversal (LeetCode 102) for the rawest BFS template, Validate Binary Search Tree (LeetCode 98) for bound-threading DFS, and Symmetric Tree (LeetCode 101) for a DFS that compares two subtrees against each other rather than validating one alone."""},
        ],
    },

    "dsa-10": {
        "title_check": "Sorting & heaps",
        "sections": [
            {"h": "ORDER FOR CORRECTNESS, PRIORITY FOR EFFICIENCY", "body": r"""Sorting answers "put everything in order" and costs O(n log n) for any comparison-based algorithm - that bound is not a limitation of any one algorithm, it is a proven lower bound for comparison sorts in general, which is why you will never see a comparison sort beat O(n log n) in the worst case. You rarely implement one yourself; you use sorting to UNLOCK other techniques - two pointers and greedy algorithms both typically require sorted input as a precondition, so "sort first" is frequently step zero of a larger solution rather than the whole solution. A heap (Python's heapq, a binary min-heap) solves a narrower but extremely common question - "what is the smallest (or largest) element right now, as the collection changes over time" - in O(log n) per insert or removal, without maintaining full sorted order at every step, which is strictly cheaper than re-sorting after every change. The right tool the instant a problem says "top k," "kth largest/smallest," or describes a continuous STREAM where you repeatedly need the current max or min - full sorting would be correct but wasteful when you only ever need the extreme value, not the whole order."""},

            {"h": "heapq'S MIN-HEAP, AND THE NEGATION TRICK FOR A MAX-HEAP", "body": r"""Python's heapq module only provides a MIN-heap - heappop always returns the smallest element - so a max-heap is simulated by negating every value on the way in and out.

    import heapq

    def k_smallest(nums, k):
        heap = []
        for x in nums:
            heapq.heappush(heap, x)          # O(log n) per push
        return [heapq.heappop(heap) for _ in range(k)]   # O(log n) per pop

    def top_k_frequent_bruteish(nums, k):
        from collections import Counter
        counts = Counter(nums)
        heap = []
        for val, freq in counts.items():
            heapq.heappush(heap, (freq, val))    # tuples compare element-wise
            if len(heap) > k:
                heapq.heappop(heap)              # evict the current smallest freq
        return [val for freq, val in heap]

heapq.heappush(heap, x) maintains the heap invariant after insertion; heapq.heappop(heap) removes and returns the current minimum in O(log n). Pushing tuples (freq, val) works because Python compares tuples element-wise, so the heap orders by freq first automatically - this is the size-k-heap trick: keep the heap capped at size k, evicting the current smallest whenever it grows past k, so it always holds the k LARGEST frequencies seen so far, not the k smallest."""},

            {"h": "WORKED PROBLEM: TOP K FREQUENT ELEMENTS", "body": r"""LeetCode 347: given nums and k, return the k most frequent elements.

    def top_k_frequent(nums, k):
        from collections import Counter
        counts = Counter(nums)                    # O(n)
        heap = []
        for val, freq in counts.items():           # O(distinct values)
            heapq.heappush(heap, (freq, val))
            if len(heap) > k:
                heapq.heappop(heap)                 # keep only the top k so far
        return [val for freq, val in heap]

The naive approach - sort all distinct (value, frequency) pairs by frequency and take the top k - costs O(d log d) where d is the number of distinct values, which can be as large as n. The heap approach instead maintains a heap that NEVER exceeds size k: every time it would grow to k+1, immediately pop the smallest, so at every point in time the heap holds exactly the k largest frequencies encountered so far, discarding anything smaller the moment something better arrives. This is why the complexity is O(d log k) rather than O(d log d) - when k is small relative to d (a common real situation, "top 10 out of a million"), that difference is substantial, and it is exactly the case a full sort would waste effort on by fully ordering values you will never look at."""},

            {"h": "THE PARENT-CHILD INVARIANT, NOT A FULL ORDER", "body": r"""The heap invariant is much weaker than a sorted array's: every parent is <= (or >=, for a max-heap) both of its children, recursively, but siblings and cousins have NO guaranteed order relative to each other - only the path from root to any node is guaranteed monotonic. This is precisely why heappop() in O(log n) only ever gives you the ROOT (the global min), never any other element in sorted position - asking for "the third smallest" requires three pops, not a single O(1) index into position 2, because nothing below the root is actually sorted. Edge cases: calling heappop on an empty heap raises IndexError - always guard with a length or emptiness check first. A heap of one element trivially satisfies the invariant with nothing to compare against. Duplicate values are handled correctly by heap operations (ties do not break anything), but a heap gives you NO stability guarantee about which equal element comes out first, unlike Python's sort, which is guaranteed stable. k larger than the number of distinct elements (or larger than n) must be guarded explicitly, since the size-k-heap trick's "evict when > k" condition never fires and you simply keep everything - correct, but worth recognizing as the boundary case rather than assuming it. Building a heap from an existing list via heapq.heapify is a genuinely different, cheaper operation than pushing elements one at a time, covered next."""},

            {"h": "heapify IS O(n), NOT O(n log n) - AND WHY", "body": r"""heappush and heappop are each O(log n) - a single element bubbles up or down at most the height of the heap, log n levels. Building a heap from scratch by pushing n elements one at a time is therefore O(n log n) total. But heapq.heapify(existing_list) builds a valid heap from an unordered list in O(n), not O(n log n) - a genuinely surprising result the first time you see it, and worth being able to explain rather than just cite. The reason: heapify works bottom-up, "sifting down" each node starting from the last internal node toward the root, and the vast majority of nodes in a heap sit near the BOTTOM, where a sift-down touches only a small number of levels - only the few nodes near the root ever pay close to the full log n cost, and summing that cost across all nodes (most of them cheap, a few of them expensive) converges to O(n) rather than O(n log n). The top-k-via-heap approach from this lesson, by contrast, pushes elements one at a time while capping size at k, giving O(n log k) - genuinely better than O(n log n) full sorting whenever k is meaningfully smaller than n, and this is the concrete payoff of choosing a heap over a full sort for a top-k-shaped problem. Space for any heap-based approach is O(n) or O(k) respectively, holding the elements currently tracked."""},

            {"h": "SPOTTING A HEAP PROBLEM BEHIND A STREAM OR A MERGE", "body": r""""Kth largest/smallest," "top k," and "k closest points to the origin" are the direct tells for a size-k heap. A subtler disguise is any problem describing a continuous STREAM of incoming values where you must answer "what is the current median/max/min" after each new arrival - a single heap (for max or min) or two heaps working together (a max-heap for the lower half, a min-heap for the upper half, for a running median) is the standard answer, and "as data arrives" or "design a class that supports adding a number and querying X" is the language to watch for. Merge k Sorted Lists (LeetCode 23) hides a heap behind what looks like a pure linked-list problem: instead of comparing all k list heads pairwise every step (expensive as k grows), push all k current heads into a heap keyed by value, repeatedly pop the smallest, and push that popped node's .next - reducing an O(k) comparison per step to an O(log k) heap operation, since the heap is doing the "which of these k is smallest" job that a bare loop would otherwise redo from scratch every single time. Named problems worth drilling: Kth Largest Element in an Array (LeetCode 215), Top K Frequent Elements (LeetCode 347), and Merge k Sorted Lists (LeetCode 23) once the linked-list lesson's pointer mechanics are solid."""},
        ],
    },

    "dsa-11": {
        "title_check": "Graphs & connectivity",
        "sections": [
            {"h": "NODES AND EDGES, WITH NO SINGLE CORRECT SHAPE", "body": r"""A graph is nodes joined by edges, and unlike a tree it has no required root and can contain cycles - a node can have any number of neighbors, and there is no guarantee any traversal ever "finishes" a branch the way a tree's leaves guarantee termination. Trees and linked lists, from earlier lessons, are actually special cases of graphs (a tree is a connected, acyclic graph; a linked list is a tree where every node has at most one child) - so every DFS and BFS instinct from those lessons carries over directly, with one addition that becomes mandatory rather than optional: a VISITED set, because without one, a cycle sends your traversal in circles forever. The right tool whenever a problem's language is "connected," "reachable from," "path exists between," "components," or a grid-flavored version of the same idea - "islands," "provinces," "friend circles" - all of these are graph connectivity questions wearing a different vocabulary. The first real step in almost every graph problem is deciding the REPRESENTATION - an adjacency list (a dict mapping each node to its neighbors) versus an adjacency matrix (an n-by-n grid of connections) - and that choice has real complexity consequences covered later in this lesson."""},

            {"h": "BUILDING AN ADJACENCY LIST, AND MARKING VISITED AT THE RIGHT MOMENT", "body": r"""    from collections import defaultdict, deque

    def build_graph(n, edges):
        graph = defaultdict(list)
        for a, b in edges:
            graph[a].append(b)
            graph[b].append(a)        # undirected: add both directions
        return graph

    def bfs(graph, start):
        visited = {start}             # mark at ENQUEUE time, not dequeue
        queue = deque([start])
        order = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)     # mark here
                    queue.append(neighbor)
        return order

graph[a].append(b) AND graph[b].append(a) both run for an undirected edge, since "a connects to b" implies "b connects to a" - a directed graph would only add one direction. The visited.add(neighbor) line sitting INSIDE the neighbor-scanning loop, at the moment a node is discovered and enqueued, is deliberate and load-bearing: if you instead mark a node visited only when it is DEQUEUED and processed, the same node can be pushed onto the queue multiple times by different neighbors before any of those pushes gets processed, wasting work and, in counting-flavored variants, silently double-counting."""},

            {"h": "WORKED PROBLEM: NUMBER OF ISLANDS", "body": r"""LeetCode 200: given a grid of '1' (land) and '0' (water), count the number of islands - connected groups of land, where connectivity is up/down/left/right only.

    def num_islands(grid):
        if not grid:
            return 0
        rows, cols = len(grid), len(grid[0])
        visited = set()

        def bfs(r, c):
            queue = deque([(r, c)])
            visited.add((r, c))                 # mark at enqueue
            while queue:
                cr, cc = queue.popleft()
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = cr + dr, cc + dc
                    if (0 <= nr < rows and 0 <= nc < cols
                            and grid[nr][nc] == '1' and (nr, nc) not in visited):
                        visited.add((nr, nc))    # mark at enqueue, again
                        queue.append((nr, nc))

        count = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == '1' and (r, c) not in visited:
                    bfs(r, c)
                    count += 1                   # one new traversal = one island
        return count

The grid IS the graph - each cell's neighbors are computed with the four (dr, dc) offsets instead of stored in an explicit adjacency list, but the traversal logic is identical to the generic bfs() above. Counting islands is exactly "count connected components": the outer double loop tries every cell as a potential BFS start, but the visited check ensures a fresh BFS only launches from a cell no earlier traversal has already claimed - each such launch is, by definition, a previously undiscovered island."""},

            {"h": "THE VISITED-SET INVARIANT AND WHAT AN UNGUARDED CYCLE DOES", "body": r"""The invariant is: a node is added to visited at the exact moment it is discovered (enqueued or pushed), so that no two different paths through the graph can ever enqueue the SAME node twice - this is what keeps the queue or stack bounded by the number of nodes rather than growing without limit. Marking visited at dequeue/pop time INSTEAD of enqueue/push time breaks this: between the moment a node is first enqueued and the moment it is eventually dequeued, every OTHER neighbor that also points at it can enqueue it again, since it does not look "visited" yet - the traversal still terminates on a finite graph, but can enqueue the same node many times over, wasting real work and, in any variant that increments a counter per visit rather than per unique node, producing a wrong count. On a graph with an actual cycle and NO visited set at all, the traversal does not merely waste work, it never terminates. Edge cases: an empty graph (no nodes) returns immediately. A single isolated node with no edges is its own connected component of size one. Self-loops (an edge from a node to itself) and multi-edges (two nodes joined by more than one edge) must not break the visited check - once a node is marked, revisiting it through a redundant edge should be a no-op, not a re-enqueue. A DISCONNECTED graph is precisely why counting components requires looping over EVERY node as a possible start, launching a fresh traversal from each one the main loop finds still unvisited - a single BFS or DFS from one arbitrary start only ever explores that node's own component."""},

            {"h": "O(V + E), AND WHY THE REPRESENTATION MATTERS", "body": r"""BFS and DFS are both O(V + E) time and O(V) space on an adjacency-list representation: every vertex is enqueued/pushed and visited exactly once (the O(V) term), and every edge is examined at most once from each endpoint it touches (the O(E) term, or O(2E) for an undirected graph, which is still O(E) after dropping the constant). This is the graph-traversal analogue of the "pushed once, processed at most a constant number of times" aggregate argument from the stack and window lessons - it is the same style of reasoning applied to a different structure. The representation choice has a real, sometimes decisive complexity consequence: an adjacency LIST costs O(V + E) space total, proportional to how many edges actually exist, while an adjacency MATRIX costs a flat O(V^2) space regardless of edge count, and checking "are a and b connected" is O(1) on a matrix versus O(degree of a) on a list. For a SPARSE graph (edges much fewer than V^2, the common case in interview problems), a list is both faster to traverse and dramatically smaller; for a DENSE graph close to fully connected, the matrix's O(1) adjacency check can be worth its larger footprint. Choosing the wrong representation for a graph with V in the hundreds of thousands can be the entire difference between a solution that runs and one that times out or exhausts memory."""},

            {"h": "SPOTTING CONNECTIVITY UNDER GRID AND DEPENDENCY LANGUAGE", "body": r""""Connected," "reachable," "components," "provinces," and "friend circles" are direct tells. Grid problems ("islands," "count enclosed regions," "rotting oranges") are graphs wearing a spatial disguise - the giveaway is that "neighbors" are computed from coordinates (up/down/left/right, or sometimes diagonals) rather than stored in an explicit adjacency structure, but every algorithm from this lesson applies unchanged once you see the grid as an implicit graph. A second, less obvious disguise is DEPENDENCY language: Course Schedule (LeetCode 207) - "can you finish all courses given prerequisite pairs" - is a DIRECTED graph cycle-detection problem (a valid course ordering exists if and only if the prerequisite graph has no cycle), which reads like a scheduling puzzle rather than a graph problem until you notice "prerequisite" is just a directed edge. Clone Graph (LeetCode 133) drills a different skill entirely - traversal combined with building a parallel copy, using a visited map from original node to its clone instead of a plain visited set, so that already-cloned nodes are reused rather than duplicated when a cycle leads back to them. Weighted shortest-path algorithms like Dijkstra's build on this same BFS/DFS foundation but are a deliberately separate, harder topic once plain connectivity is automatic."""},
        ],
    },

    "dsa-12": {
        "title_check": "Dynamic programming",
        "sections": [
            {"h": "OVERLAPPING SUBPROBLEMS, SOLVED ONCE AND REMEMBERED", "body": r"""Dynamic programming applies when a problem breaks into subproblems that OVERLAP - the same smaller question gets asked repeatedly across different branches of a naive recursive solution - and stores each subproblem's answer the first time it is computed so every later request for it is a lookup instead of a recomputation. This is different from backtracking's exponential tree from two lessons ago in exactly one way: backtracking's subproblems are typically distinct paths that never repeat, while DP's defining feature is that the SAME subproblem is reachable via multiple different sequences of choices. The right tool the instant a problem says "count the number of ways," "minimum/maximum cost to reach," or describes choices that carry a FUTURE consequence rather than an immediately-resolvable one - naive recursive Fibonacci is the canonical illustration: fib(5) calls fib(4) and fib(3), but fib(4) ALSO calls fib(3), and without memoization that identical subproblem gets recomputed from scratch every time it is reached, with the redundant recomputation compounding exponentially as n grows. The entire discipline of DP is: notice the repetition, then eliminate it by remembering."""},

            {"h": "THE STATE-AND-TRANSITION TEMPLATE, LINE BY LINE", "body": r"""The two hard parts of any DP problem are defining what dp[i] MEANS (the state) and writing the one-line relationship between dp[i] and smaller states (the transition) - the code itself, once those two are right, is almost mechanical.

    def climb_stairs(n):
        if n <= 2:
            return n
        dp = [0] * (n + 1)
        dp[1], dp[2] = 1, 2
        for i in range(3, n + 1):
            dp[i] = dp[i-1] + dp[i-2]     # the transition: two smaller states
        return dp[n]

dp[i] here MEANS "the number of distinct ways to climb to step i" - stating that sentence out loud, precisely, before writing any code, is the actual skill this lesson is teaching; the array is just where the answer to that sentence gets stored. The transition, dp[i] = dp[i-1] + dp[i-2], encodes "your last move to reach step i was either a single step from i-1, or a double step from i-2" - every valid DP transition is a sentence like that, translated directly into an index arithmetic expression. The loop fills dp in an order (increasing i) that guarantees dp[i-1] and dp[i-2] are ALREADY computed before dp[i] needs them - get that fill order wrong and the transition reads uninitialized or wrong data."""},

            {"h": "WORKED PROBLEM: LONGEST COMMON SUBSEQUENCE", "body": r"""LeetCode 1143: given two strings text1 and text2, find the length of their longest common subsequence (not necessarily contiguous, but in order).

    def longest_common_subsequence(text1, text2):
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = 1 + dp[i-1][j-1]        # extend a shared subsequence
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])  # drop one character
        return dp[m][n]

dp[i][j] MEANS "the LCS length of the first i characters of text1 and the first j characters of text2" - a 2D state, because the problem genuinely has two independent positions advancing at once, unlike Climbing Stairs' single index. The transition is a two-way branch: if the current characters match, extend the best subsequence found WITHOUT either of these two characters by one (dp[i-1][j-1] + 1); if they do not match, the answer is the better of dropping one character from either string (max of dp[i-1][j] and dp[i][j-1]). The dp[i-1] row and dp[i][j-1] entry earlier in the same row must both already be filled, which is exactly why the loops go in increasing i and j order."""},

            {"h": "THE FILL-ORDER INVARIANT, AND HOW A WRONG STATE SILENTLY MERGES CASES", "body": r"""The invariant every DP table depends on is: by the time dp[i] (or dp[i][j]) is computed, every smaller state its transition reads from is ALREADY final and correct - which requires filling the table in an order consistent with the transition's dependencies (a topological order over the "depends on" relationship), not simply "in index order" by coincidence. This is where 0/1 knapsack-style problems break most often: iterating the capacity dimension FORWARD while allowing an item to be used only once requires care about which array (a fresh row, or the same row read right-to-left) you read from - iterating in the wrong direction on a space-optimized 1D version silently turns a "use each item at most once" problem into "use each item unlimited times," a bug that produces a plausible-looking but wrong number rather than a crash. Edge cases: an empty input must make the base case (dp[0] or dp[0][0]) correct on its own terms - an off-by-one in array sizing (dp = [0]*(n+1) versus [0]*n) is the most common DP bug, since the +1 exists specifically to hold the "zero elements considered" base case alongside n real ones. The deeper trap the brief for this lesson exists to name explicitly: the STATE must capture every dimension the answer actually depends on - if two genuinely different subproblems (say, "used 3 coins so far" versus "used 4 coins so far, same remaining target") collapse onto the SAME dp cell because your state definition omitted a dimension that distinguishes them, you get a wrong answer that looks like correctly-working memoization, because the code runs fine and returns a number - it is just the wrong number, for a problem your chosen state was never actually expressive enough to represent."""},

            {"h": "MEMOIZATION ALONE DOES NOT TAME AN EXPONENTIAL STATE SPACE", "body": r"""The honest complexity of a DP solution is (number of distinct states) times (cost of one transition) - Climbing Stairs has O(n) states with O(1) transitions, giving O(n) time and, in the array version, O(n) space (reducible to O(1) by keeping only the last two values, since the transition only ever looks back two steps - a real, common space optimization once the table version is verified correct). Longest Common Subsequence has O(m*n) states with O(1) transitions each, giving O(m*n) time and space (reducible to O(min(m,n)) space with a rolling array, keeping only the current and previous rows). The single most important honest caveat in this entire lesson: memoization (caching results, whether via a dict or functools.lru_cache) only helps when the number of DISTINCT reachable states is polynomial in the input size - if your state definition still allows exponentially many distinct configurations (a classic case: a state that encodes an entire SUBSET of elements considered so far, rather than a single running index or sum), adding a cache decorator does not make the algorithm polynomial, it just avoids recomputing any single exponential-sized state more than once, which is a real but much smaller win than people assume. "I memoized it" is not automatically "I fixed the complexity" - always name the state and count how many distinct values it can actually take before claiming a complexity bound. A second real caveat: naive top-down recursion, even memoized, still costs O(n) call-stack depth in the worst case, hitting Python's recursion limit on large n exactly as earlier lessons' recursive traversals did - bottom-up tabulation has no such ceiling."""},

            {"h": "SPOTTING DP BEHIND GREEDY AND SEARCH-SHAPED PHRASING", "body": r""""Count the number of ways," "minimum/maximum cost," and "longest/shortest subsequence" are the direct tells. The most common disguise is a problem that LOOKS greedy - "make change with the fewest coins," "can you partition this array into two equal-sum subsets" - where a locally-obvious choice (always take the largest coin; always assign the next number to whichever subset is currently smaller) fails on some inputs and only DP, which considers every relevant choice rather than committing early, gets the right answer; the tell that greedy is unsafe here is the absence of any proof that the locally best choice can never be undone by a later one, exactly the kind of proof Container With Most Water's two-pointer move DID have and a coin-change greedy choice does NOT. The second common disguise is a problem that looks like plain backtracking (from two lessons ago) until you notice the SAME subproblem - the same remaining target, the same remaining index - keeps recurring across different branches of the search tree; the moment you notice that repetition, adding memoization on top of an otherwise-unchanged backtracking function is often the entire fix. Named problems worth drilling in rough order of difficulty: Climbing Stairs (LeetCode 70) and House Robber (LeetCode 198) for 1D states, Longest Increasing Subsequence (LeetCode 300) for an O(n^2)-to-O(n log n) escalation, and Coin Change (LeetCode 322) once the state-and-transition habit from this lesson is solid enough to apply to a new problem cold."""},
        ],
    },
}
