# leet.py — the LeetCode-style problem bank used by the daily challenge and browse list.
# Each problem: id, title, difficulty, statement, examples, func (name the user must define),
# starter, tests [{args, expect}], and compare mode ("exact" | "unordered" | "groups" |
# "intervals" | "approx"). Keep expected outputs correct — the harness trusts them.

PROBLEMS = [
    # ---------------------------------------------------------------- EASY
    {
        "id": "two-sum", "title": "Two Sum", "difficulty": "Easy",
        "statement": "Given an array of integers nums and an integer target, return the indices of the two numbers that add up to target. Exactly one solution exists; you may not use the same element twice.",
        "examples": ["two_sum([2,7,11,15], 9) -> [0,1]", "two_sum([3,2,4], 6) -> [1,2]"],
        "func": "two_sum", "compare": "unordered",
        "starter": "def two_sum(nums, target):\n    # return the two indices\n    pass\n",
        "tests": [
            {"args": [[2, 7, 11, 15], 9], "expect": [0, 1]},
            {"args": [[3, 2, 4], 6], "expect": [1, 2]},
            {"args": [[3, 3], 6], "expect": [0, 1]},
        ],
        "hint": "A hash map from value -> index lets you check for target-x in O(1) as you scan.",
    },
    {
        "id": "valid-parentheses", "title": "Valid Parentheses", "difficulty": "Easy",
        "statement": "Given a string s of just '()[]{}', decide if the brackets are validly opened and closed in the right order.",
        "examples": ["is_valid('()[]{}') -> True", "is_valid('(]') -> False"],
        "func": "is_valid", "compare": "exact",
        "starter": "def is_valid(s):\n    pass\n",
        "tests": [
            {"args": ["()"], "expect": True},
            {"args": ["()[]{}"], "expect": True},
            {"args": ["(]"], "expect": False},
            {"args": ["([)]"], "expect": False},
            {"args": ["{[]}"], "expect": True},
            {"args": ["]"], "expect": False},
        ],
        "hint": "A stack: push openers, and on a closer check the top matches. Empty stack at the end = valid.",
    },
    {
        "id": "fizzbuzz", "title": "Fizz Buzz", "difficulty": "Easy",
        "statement": "Return a list for 1..n where multiples of 3 are 'Fizz', of 5 are 'Buzz', of both 'FizzBuzz', else the number as a string.",
        "examples": ["fizzbuzz(5) -> ['1','2','Fizz','4','Buzz']"],
        "func": "fizzbuzz", "compare": "exact",
        "starter": "def fizzbuzz(n):\n    pass\n",
        "tests": [
            {"args": [5], "expect": ["1", "2", "Fizz", "4", "Buzz"]},
            {"args": [15], "expect": ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]},
        ],
        "hint": "Check %15 first (or build the string by appending Fizz/Buzz), then %3, then %5.",
    },
    {
        "id": "max-subarray", "title": "Maximum Subarray", "difficulty": "Easy",
        "statement": "Find the contiguous subarray with the largest sum and return that sum (Kadane's algorithm).",
        "examples": ["max_sub_array([-2,1,-3,4,-1,2,1,-5,4]) -> 6"],
        "func": "max_sub_array", "compare": "exact",
        "starter": "def max_sub_array(nums):\n    pass\n",
        "tests": [
            {"args": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "expect": 6},
            {"args": [[1]], "expect": 1},
            {"args": [[5, 4, -1, 7, 8]], "expect": 23},
            {"args": [[-3, -1, -2]], "expect": -1},
        ],
        "hint": "Keep a running sum; if it drops below the current element, restart from it. Track the max seen.",
    },
    {
        "id": "contains-duplicate", "title": "Contains Duplicate", "difficulty": "Easy",
        "statement": "Return True if any value appears at least twice in nums, else False.",
        "examples": ["contains_duplicate([1,2,3,1]) -> True"],
        "func": "contains_duplicate", "compare": "exact",
        "starter": "def contains_duplicate(nums):\n    pass\n",
        "tests": [
            {"args": [[1, 2, 3, 1]], "expect": True},
            {"args": [[1, 2, 3, 4]], "expect": False},
            {"args": [[]], "expect": False},
        ],
        "hint": "A set removes duplicates — compare len(set(nums)) to len(nums).",
    },
    {
        "id": "valid-anagram", "title": "Valid Anagram", "difficulty": "Easy",
        "statement": "Return True if t is an anagram of s (same letters, same counts).",
        "examples": ["is_anagram('anagram','nagaram') -> True"],
        "func": "is_anagram", "compare": "exact",
        "starter": "def is_anagram(s, t):\n    pass\n",
        "tests": [
            {"args": ["anagram", "nagaram"], "expect": True},
            {"args": ["rat", "car"], "expect": False},
            {"args": ["a", "ab"], "expect": False},
        ],
        "hint": "Compare character counts (collections.Counter) or sorted(s) == sorted(t).",
    },
    {
        "id": "best-time-stock", "title": "Best Time to Buy/Sell Stock", "difficulty": "Easy",
        "statement": "Given daily prices, return the max profit from one buy then one later sell. 0 if impossible.",
        "examples": ["max_profit([7,1,5,3,6,4]) -> 5"],
        "func": "max_profit", "compare": "exact",
        "starter": "def max_profit(prices):\n    pass\n",
        "tests": [
            {"args": [[7, 1, 5, 3, 6, 4]], "expect": 5},
            {"args": [[7, 6, 4, 3, 1]], "expect": 0},
            {"args": [[2, 4, 1]], "expect": 2},
        ],
        "hint": "Track the minimum price so far; at each day the best profit is price - min_so_far.",
    },
    {
        "id": "single-number", "title": "Single Number", "difficulty": "Easy",
        "statement": "Every element appears twice except one. Find the one, in O(n) time and O(1) space.",
        "examples": ["single_number([4,1,2,1,2]) -> 4"],
        "func": "single_number", "compare": "exact",
        "starter": "def single_number(nums):\n    pass\n",
        "tests": [
            {"args": [[2, 2, 1]], "expect": 1},
            {"args": [[4, 1, 2, 1, 2]], "expect": 4},
            {"args": [[7]], "expect": 7},
        ],
        "hint": "XOR is its own inverse: a^a=0. XOR everything together — pairs cancel, the loner remains.",
    },
    {
        "id": "move-zeroes", "title": "Move Zeroes", "difficulty": "Easy",
        "statement": "Move all 0s to the end while keeping the order of non-zero elements. Return the resulting list.",
        "examples": ["move_zeroes([0,1,0,3,12]) -> [1,3,12,0,0]"],
        "func": "move_zeroes", "compare": "exact",
        "starter": "def move_zeroes(nums):\n    # return the modified list\n    pass\n",
        "tests": [
            {"args": [[0, 1, 0, 3, 12]], "expect": [1, 3, 12, 0, 0]},
            {"args": [[0, 0, 1]], "expect": [1, 0, 0]},
            {"args": [[1, 2, 3]], "expect": [1, 2, 3]},
        ],
        "hint": "Two pointers: keep a write index for the next non-zero slot, then fill the rest with zeros.",
    },
    {
        "id": "first-unique-char", "title": "First Unique Character", "difficulty": "Easy",
        "statement": "Return the index of the first non-repeating character in s, or -1 if none.",
        "examples": ["first_uniq_char('leetcode') -> 0", "first_uniq_char('loveleetcode') -> 2"],
        "func": "first_uniq_char", "compare": "exact",
        "starter": "def first_uniq_char(s):\n    pass\n",
        "tests": [
            {"args": ["leetcode"], "expect": 0},
            {"args": ["loveleetcode"], "expect": 2},
            {"args": ["aabb"], "expect": -1},
        ],
        "hint": "Count characters first, then scan again for the first with count 1.",
    },
    {
        "id": "palindrome-number", "title": "Palindrome Number", "difficulty": "Easy",
        "statement": "Return True if the integer x reads the same forwards and backwards. Negatives are never palindromes.",
        "examples": ["is_palindrome(121) -> True", "is_palindrome(-121) -> False"],
        "func": "is_palindrome", "compare": "exact",
        "starter": "def is_palindrome(x):\n    pass\n",
        "tests": [
            {"args": [121], "expect": True},
            {"args": [-121], "expect": False},
            {"args": [10], "expect": False},
            {"args": [0], "expect": True},
        ],
        "hint": "s = str(x); return s == s[::-1]. (For a challenge, do it without converting to a string.)",
    },
    {
        "id": "valid-palindrome", "title": "Valid Palindrome", "difficulty": "Easy",
        "statement": "Considering only alphanumeric characters and ignoring case, is s a palindrome?",
        "examples": ["is_pal('A man, a plan, a canal: Panama') -> True"],
        "func": "is_pal", "compare": "exact",
        "starter": "def is_pal(s):\n    pass\n",
        "tests": [
            {"args": ["A man, a plan, a canal: Panama"], "expect": True},
            {"args": ["race a car"], "expect": False},
            {"args": [" "], "expect": True},
        ],
        "hint": "Filter with c.isalnum(), lowercase, then compare to its reverse (or use two pointers).",
    },
    # ---------------------------------------------------------------- MEDIUM
    {
        "id": "group-anagrams", "title": "Group Anagrams", "difficulty": "Medium",
        "statement": "Group the words that are anagrams of each other. Return a list of groups (any order).",
        "examples": ["group_anagrams(['eat','tea','tan','ate','nat','bat'])"],
        "func": "group_anagrams", "compare": "groups",
        "starter": "def group_anagrams(strs):\n    pass\n",
        "tests": [
            {"args": [["eat", "tea", "tan", "ate", "nat", "bat"]], "expect": [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]},
            {"args": [[""]], "expect": [[""]]},
            {"args": [["a"]], "expect": [["a"]]},
        ],
        "hint": "Key each word by its sorted letters (a tuple), and bucket into a dict of lists.",
    },
    {
        "id": "top-k-frequent", "title": "Top K Frequent Elements", "difficulty": "Medium",
        "statement": "Return the k most frequent elements (any order).",
        "examples": ["top_k_frequent([1,1,1,2,2,3], 2) -> [1,2]"],
        "func": "top_k_frequent", "compare": "unordered",
        "starter": "def top_k_frequent(nums, k):\n    pass\n",
        "tests": [
            {"args": [[1, 1, 1, 2, 2, 3], 2], "expect": [1, 2]},
            {"args": [[1], 1], "expect": [1]},
            {"args": [[4, 4, 5, 5, 6], 2], "expect": [4, 5]},
        ],
        "hint": "Count with a dict, then take the k keys with the largest counts (sort by count or a heap).",
    },
    {
        "id": "product-except-self", "title": "Product of Array Except Self", "difficulty": "Medium",
        "statement": "Return an array where each element is the product of all others, without using division.",
        "examples": ["product_except_self([1,2,3,4]) -> [24,12,8,6]"],
        "func": "product_except_self", "compare": "exact",
        "starter": "def product_except_self(nums):\n    pass\n",
        "tests": [
            {"args": [[1, 2, 3, 4]], "expect": [24, 12, 8, 6]},
            {"args": [[-1, 1, 0, -3, 3]], "expect": [0, 0, 9, 0, 0]},
        ],
        "hint": "Two passes: prefix products left→right, then multiply by suffix products right→left.",
    },
    {
        "id": "longest-substring", "title": "Longest Substring Without Repeating", "difficulty": "Medium",
        "statement": "Return the length of the longest substring of s with no repeating characters.",
        "examples": ["length_of_longest('abcabcbb') -> 3", "length_of_longest('pwwkew') -> 3"],
        "func": "length_of_longest", "compare": "exact",
        "starter": "def length_of_longest(s):\n    pass\n",
        "tests": [
            {"args": ["abcabcbb"], "expect": 3},
            {"args": ["bbbbb"], "expect": 1},
            {"args": ["pwwkew"], "expect": 3},
            {"args": [""], "expect": 0},
        ],
        "hint": "Sliding window: a set of current chars, move the right edge; when a repeat appears shrink the left edge.",
    },
    {
        "id": "three-sum", "title": "3Sum", "difficulty": "Medium",
        "statement": "Return all unique triplets [a,b,c] that sum to 0. No duplicate triplets.",
        "examples": ["three_sum([-1,0,1,2,-1,-4]) -> [[-1,-1,2],[-1,0,1]]"],
        "func": "three_sum", "compare": "groups",
        "starter": "def three_sum(nums):\n    pass\n",
        "tests": [
            {"args": [[-1, 0, 1, 2, -1, -4]], "expect": [[-1, -1, 2], [-1, 0, 1]]},
            {"args": [[0, 0, 0]], "expect": [[0, 0, 0]]},
            {"args": [[1, 2, 3]], "expect": []},
        ],
        "hint": "Sort, then fix each i and two-pointer the rest for -nums[i]. Skip duplicates to avoid repeats.",
    },
    {
        "id": "coin-change", "title": "Coin Change", "difficulty": "Medium",
        "statement": "Fewest coins to make amount from the given denominations, or -1 if impossible.",
        "examples": ["coin_change([1,2,5], 11) -> 3"],
        "func": "coin_change", "compare": "exact",
        "starter": "def coin_change(coins, amount):\n    pass\n",
        "tests": [
            {"args": [[1, 2, 5], 11], "expect": 3},
            {"args": [[2], 3], "expect": -1},
            {"args": [[1], 0], "expect": 0},
        ],
        "hint": "DP: dp[a] = min coins for amount a; dp[a] = 1 + min(dp[a-coin]) over coins that fit.",
    },
    {
        "id": "num-islands", "title": "Number of Islands", "difficulty": "Medium",
        "statement": "Given a grid of '1' (land) and '0' (water), count the islands (4-directionally connected land).",
        "examples": ["num_islands(grid) -> 3"],
        "func": "num_islands", "compare": "exact",
        "starter": "def num_islands(grid):\n    pass\n",
        "tests": [
            {"args": [[["1", "1", "0", "1"], ["0", "0", "0", "1"], ["1", "0", "0", "0"]]], "expect": 3},
            {"args": [[["1", "1", "1"], ["1", "1", "1"]]], "expect": 1},
            {"args": [[["0"]]], "expect": 0},
        ],
        "hint": "Scan the grid; when you hit '1', flood-fill (DFS/BFS) all connected land to '0' and count once.",
    },
    {
        "id": "merge-intervals", "title": "Merge Intervals", "difficulty": "Medium",
        "statement": "Merge all overlapping intervals and return the non-overlapping result.",
        "examples": ["merge([[1,3],[2,6],[8,10],[15,18]]) -> [[1,6],[8,10],[15,18]]"],
        "func": "merge", "compare": "intervals",
        "starter": "def merge(intervals):\n    pass\n",
        "tests": [
            {"args": [[[1, 3], [2, 6], [8, 10], [15, 18]]], "expect": [[1, 6], [8, 10], [15, 18]]},
            {"args": [[[1, 4], [4, 5]]], "expect": [[1, 5]]},
        ],
        "hint": "Sort by start; walk through, extending the last interval when the next one overlaps it.",
    },
    {
        "id": "binary-search", "title": "Binary Search", "difficulty": "Medium",
        "statement": "Return the index of target in a sorted array nums, or -1. Must be O(log n).",
        "examples": ["binary_search([-1,0,3,5,9,12], 9) -> 4"],
        "func": "binary_search", "compare": "exact",
        "starter": "def binary_search(nums, target):\n    pass\n",
        "tests": [
            {"args": [[-1, 0, 3, 5, 9, 12], 9], "expect": 4},
            {"args": [[-1, 0, 3, 5, 9, 12], 2], "expect": -1},
            {"args": [[5], 5], "expect": 0},
        ],
        "hint": "lo, hi pointers; check the middle; discard the half that can't contain target. Mind lo<=hi.",
    },
    # ---------------------------------------------------------------- HARD
    {
        "id": "trapping-rain", "title": "Trapping Rain Water", "difficulty": "Hard",
        "statement": "Given bar heights, compute how much rain water is trapped between them.",
        "examples": ["trap([0,1,0,2,1,0,1,3,2,1,2,1]) -> 6"],
        "func": "trap", "compare": "exact",
        "starter": "def trap(height):\n    pass\n",
        "tests": [
            {"args": [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], "expect": 6},
            {"args": [[4, 2, 0, 3, 2, 5]], "expect": 9},
            {"args": [[]], "expect": 0},
        ],
        "hint": "Water above each bar = min(maxLeft, maxRight) - height. Two pointers from both ends is O(1) space.",
    },
    {
        "id": "longest-valid-paren", "title": "Longest Valid Parentheses", "difficulty": "Hard",
        "statement": "Return the length of the longest valid (well-formed) parentheses substring.",
        "examples": ["longest_valid(')()())') -> 4"],
        "func": "longest_valid", "compare": "exact",
        "starter": "def longest_valid(s):\n    pass\n",
        "tests": [
            {"args": ["(()"], "expect": 2},
            {"args": [")()())"], "expect": 4},
            {"args": [""], "expect": 0},
            {"args": ["()(()"], "expect": 2},
        ],
        "hint": "Stack of indices seeded with -1; on ')' pop, and the length is current index minus the new stack top.",
    },
    {
        "id": "median-two-sorted", "title": "Median of Two Sorted Arrays", "difficulty": "Hard",
        "statement": "Return the median of two sorted arrays as a float.",
        "examples": ["median([1,3],[2]) -> 2.0", "median([1,2],[3,4]) -> 2.5"],
        "func": "median", "compare": "approx",
        "starter": "def median(a, b):\n    pass\n",
        "tests": [
            {"args": [[1, 3], [2]], "expect": 2.0},
            {"args": [[1, 2], [3, 4]], "expect": 2.5},
            {"args": [[], [1]], "expect": 1.0},
        ],
        "hint": "Merging then indexing the middle is O(n+m) and totally fine to start. The O(log) binary-search version is the stretch goal.",
    },
]

BY_ID = {p["id"]: p for p in PROBLEMS}


def daily_problem(ordinal):
    """Deterministic pick for a given date ordinal. Every 7th day is a Hard one."""
    easy_med = [p for p in PROBLEMS if p["difficulty"] != "Hard"]
    hard = [p for p in PROBLEMS if p["difficulty"] == "Hard"]
    if ordinal % 7 == 0 and hard:
        return hard[(ordinal // 7) % len(hard)]
    return easy_med[ordinal % len(easy_med)]
