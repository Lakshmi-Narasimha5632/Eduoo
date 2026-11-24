"""Seeds for Skill Assessment: Coding Problems, Sample/Hidden Test Cases, and Technical Assessments."""

from __future__ import annotations

from typing import List, Dict, Any
from .models import CodingProblem, ProblemTestCase, TechnicalQuiz


def seed_skill_assessments():
    """Seeds default LeetCode / HackerRank style coding problems and technical quizzes."""
    
    # --------------------------------------------------------------------------
    # 1. CODING PROBLEMS CATALOG
    # --------------------------------------------------------------------------
    problems_data = [
        # Arrays - Two Sum (Easy)
        {
            "slug": "two-sum",
            "title": "Two Sum",
            "difficulty": "easy",
            "category": "arrays",
            "acceptance_rate": 84.5,
            "order": 1,
            "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.",
            "input_format": "Line 1: A JSON array of integers `nums`\nLine 2: An integer `target`",
            "output_format": "A list/array of two indices `[i, j]`",
            "constraints": "• 2 <= nums.length <= 10^4\n• -10^9 <= nums[i] <= 10^9\n• -10^9 <= target <= 10^9\n• Only one valid answer exists.",
            "starter_templates": {
                "python": "def twoSum(nums, target):\n    # Return indices [i, j]\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen:\n            return [seen[diff], i]\n        seen[n] = i\n    return []\n",
                "javascript": "function twoSum(nums, target) {\n  const seen = new Map();\n  for (let i = 0; i < nums.length; i++) {\n    const diff = target - nums[i];\n    if (seen.has(diff)) return [seen.get(diff), i];\n    seen.set(nums[i], i);\n  }\n  return [];\n}",
                "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Your O(n) solution here\n        return new int[]{0, 1};\n    }\n}",
                "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        return {0, 1};\n    }\n};",
                "c": "int* twoSum(int* nums, int numsSize, int target, int* returnSize) {\n    *returnSize = 2;\n    int* res = (int*)malloc(2 * sizeof(int));\n    res[0] = 0; res[1] = 1;\n    return res;\n}",
            },
            "solution_explanation": "### Hash Map Lookup (Optimal)\n\nWe iterate through the array once while storing each visited element and its index in a hash map. For each number `n`, we calculate `diff = target - n`. If `diff` exists in our hash table, we have found the matching pair in **O(n)** time and **O(n)** space.",
            "optimal_solutions": {
                "python": "def twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []",
                "javascript": "function twoSum(nums, target) {\n  const map = new Map();\n  for (let i = 0; i < nums.length; i++) {\n    const comp = target - nums[i];\n    if (map.has(comp)) return [map.get(comp), i];\n    map.set(nums[i], i);\n  }\n  return [];\n}",
            },
            "hints": ["Can you check if the complement already exists in O(1) time?", "Use a hash table or dictionary."],
            "test_cases": [
                {"input": "[2, 7, 11, 15]\n9", "expected": "[0, 1]", "is_hidden": False, "order": 1},
                {"input": "[3, 2, 4]\n6", "expected": "[1, 2]", "is_hidden": False, "order": 2},
                {"input": "[3, 3]\n6", "expected": "[0, 1]", "is_hidden": True, "order": 3},
                {"input": "[-1, -2, -3, -4, -5]\n-8", "expected": "[2, 4]", "is_hidden": True, "order": 4},
            ],
        },

        # Strings - Valid Anagram (Easy)
        {
            "slug": "valid-anagram",
            "title": "Valid Anagram",
            "difficulty": "easy",
            "category": "strings",
            "acceptance_rate": 78.2,
            "order": 2,
            "description": "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.\n\nAn Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.",
            "input_format": "Line 1: string `s`\nLine 2: string `t`",
            "output_format": "`true` or `false`",
            "constraints": "• 1 <= s.length, t.length <= 5 * 10^4\n• `s` and `t` consist of lowercase English letters.",
            "starter_templates": {
                "python": "def isAnagram(s, t):\n    # Write your solution\n    return sorted(s) == sorted(t)\n",
                "javascript": "function isAnagram(s, t) {\n  if (s.length !== t.length) return false;\n  return s.split('').sort().join('') === t.split('').sort().join('');\n}",
                "java": "class Solution {\n    public boolean isAnagram(String s, String t) {\n        return true;\n    }\n}",
                "cpp": "class Solution {\npublic:\n    bool isAnagram(string s, string t) {\n        return true;\n    }\n};",
            },
            "solution_explanation": "### Frequency Counter\n\nCount occurrences of each letter using a hash map or 26-element array. Increment for `s` and decrement for `t`. If all frequencies reach zero, they are anagrams in **O(n)** time and **O(1)** auxiliary space.",
            "optimal_solutions": {
                "python": "from collections import Counter\ndef isAnagram(s, t):\n    return Counter(s) == Counter(t)",
                "javascript": "function isAnagram(s, t) {\n  if (s.length !== t.length) return false;\n  const count = {};\n  for (let c of s) count[c] = (count[c] || 0) + 1;\n  for (let c of t) {\n    if (!count[c]) return false;\n    count[c]--;\n  }\n  return true;\n}",
            },
            "hints": ["What if the lengths are different?", "Use a hash table or sort the strings."],
            "test_cases": [
                {"input": "\"anagram\"\n\"nagaram\"", "expected": "true", "is_hidden": False, "order": 1},
                {"input": "\"rat\"\n\"car\"", "expected": "false", "is_hidden": False, "order": 2},
                {"input": "\"aacc\"\n\"ccac\"", "expected": "false", "is_hidden": True, "order": 3},
                {"input": "\"listen\"\n\"silent\"", "expected": "true", "is_hidden": True, "order": 4},
            ],
        },

        # Stacks and Queues - Valid Parentheses (Easy)
        {
            "slug": "valid-parentheses",
            "title": "Valid Parentheses",
            "difficulty": "easy",
            "category": "stacks_queues",
            "acceptance_rate": 79.1,
            "order": 3,
            "description": "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.",
            "input_format": "A single string `s`",
            "output_format": "`true` or `false`",
            "constraints": "• 1 <= s.length <= 10^4\n• `s` consists of parentheses only `'()[]{}'`.",
            "starter_templates": {
                "python": "def isValid(s):\n    stack = []\n    pairs = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in pairs:\n            if not stack or stack.pop() != pairs[char]:\n                return False\n        else:\n            stack.append(char)\n    return len(stack) == 0\n",
                "javascript": "function isValid(s) {\n  const stack = [];\n  const map = { ')': '(', '}': '{', ']': '[' };\n  for (let ch of s) {\n    if (map[ch]) {\n      if (stack.pop() !== map[ch]) return false;\n    } else {\n      stack.push(ch);\n    }\n  }\n  return stack.length === 0;\n}",
            },
            "solution_explanation": "### Stack Invariant\n\nPush open brackets onto a stack. When encountering a closing bracket, pop the top of the stack and check if it matches the expected opening pair. Time complexity: **O(n)**, Space complexity: **O(n)**.",
            "optimal_solutions": {
                "python": "def isValid(s):\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top: return False\n        else:\n            stack.append(char)\n    return not stack",
            },
            "hints": ["A stack is ideal for LIFO matching."],
            "test_cases": [
                {"input": "\"()\"", "expected": "true", "is_hidden": False, "order": 1},
                {"input": "\"()[]{}\"", "expected": "true", "is_hidden": False, "order": 2},
                {"input": "\"(]\"", "expected": "false", "is_hidden": False, "order": 3},
                {"input": "\"([)]\"", "expected": "false", "is_hidden": True, "order": 4},
                {"input": "\"{[]}\"", "expected": "true", "is_hidden": True, "order": 5},
            ],
        },

        # Strings - Longest Substring Without Repeating Characters (Medium)
        {
            "slug": "longest-substring-without-repeating-characters",
            "title": "Longest Substring Without Repeating Characters",
            "difficulty": "medium",
            "category": "strings",
            "acceptance_rate": 62.4,
            "order": 4,
            "description": "Given a string `s`, find the length of the longest substring without repeating characters.",
            "input_format": "A single string `s`",
            "output_format": "An integer representing the maximum length",
            "constraints": "• 0 <= s.length <= 5 * 10^4\n• `s` consists of English letters, digits, symbols, and spaces.",
            "starter_templates": {
                "python": "def lengthOfLongestSubstring(s):\n    char_map = {}\n    left = 0\n    max_len = 0\n    for right, char in enumerate(s):\n        if char in char_map and char_map[char] >= left:\n            left = char_map[char] + 1\n        char_map[char] = right\n        max_len = max(max_len, right - left + 1)\n    return max_len\n",
                "javascript": "function lengthOfLongestSubstring(s) {\n  const seen = new Map();\n  let left = 0, maxLen = 0;\n  for (let right = 0; right < s.length; right++) {\n    const ch = s[right];\n    if (seen.has(ch) && seen.get(ch) >= left) {\n      left = seen.get(ch) + 1;\n    }\n    seen.set(ch, right);\n    maxLen = Math.max(maxLen, right - left + 1);\n  }\n  return maxLen;\n}",
            },
            "solution_explanation": "### Sliding Window with Hash Map\n\nMaintain a dynamic window `[left, right]`. Store the last seen index of each character. When a duplicate is found inside the current window, advance `left` past the duplicate. Time complexity: **O(n)**, Space complexity: **O(min(n, m))**.",
            "optimal_solutions": {
                "python": "def lengthOfLongestSubstring(s):\n    seen = {}\n    l = max_len = 0\n    for r, c in enumerate(s):\n        if c in seen and seen[c] >= l:\n            l = seen[c] + 1\n        seen[c] = r\n        max_len = max(max_len, r - l + 1)\n    return max_len",
            },
            "hints": ["Use a sliding window [i, j]. When character is repeated, slide the left pointer."],
            "test_cases": [
                {"input": "\"abcabcbb\"", "expected": "3", "is_hidden": False, "order": 1},
                {"input": "\"bbbbb\"", "expected": "1", "is_hidden": False, "order": 2},
                {"input": "\"pwwkew\"", "expected": "3", "is_hidden": False, "order": 3},
                {"input": "\"\"", "expected": "0", "is_hidden": True, "order": 4},
                {"input": "\"au\"", "expected": "2", "is_hidden": True, "order": 5},
            ],
        },

        # Dynamic Programming - Coin Change (Medium)
        {
            "slug": "coin-change",
            "title": "Coin Change",
            "difficulty": "medium",
            "category": "dynamic_programming",
            "acceptance_rate": 54.2,
            "order": 5,
            "description": "You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money.\n\nReturn the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return `-1`.\n\nYou may assume that you have an infinite number of each kind of coin.",
            "input_format": "Line 1: JSON array of integer coins\nLine 2: integer amount",
            "output_format": "Integer representing minimum coins or -1",
            "constraints": "• 1 <= coins.length <= 12\n• 1 <= coins[i] <= 2^31 - 1\n• 0 <= amount <= 10^4",
            "starter_templates": {
                "python": "def coinChange(coins, amount):\n    dp = [float('inf')] * (amount + 1)\n    dp[0] = 0\n    for c in coins:\n        for i in range(c, amount + 1):\n            dp[i] = min(dp[i], dp[i - c] + 1)\n    return dp[amount] if dp[amount] != float('inf') else -1\n",
                "javascript": "function coinChange(coins, amount) {\n  const dp = new Array(amount + 1).fill(Infinity);\n  dp[0] = 0;\n  for (let c of coins) {\n    for (let i = c; i <= amount; i++) {\n      dp[i] = Math.min(dp[i], dp[i - c] + 1);\n    }\n  }\n  return dp[amount] === Infinity ? -1 : dp[amount];\n}",
            },
            "solution_explanation": "### Bottom-Up DP\n\nDefine `dp[i]` as the minimum coins needed for amount `i`. Base case `dp[0] = 0`. For each coin `c`, transition: `dp[i] = min(dp[i], dp[i - c] + 1)`. Time complexity: **O(amount * len(coins))**, Space complexity: **O(amount)**.",
            "optimal_solutions": {
                "python": "def coinChange(coins, amount):\n    dp = [float('inf')] * (amount + 1)\n    dp[0] = 0\n    for coin in coins:\n        for x in range(coin, amount + 1):\n            dp[x] = min(dp[x], dp[x - coin] + 1)\n    return dp[amount] if dp[amount] != float('inf') else -1",
            },
            "hints": ["Think about the subproblem: min coins to make (amount - coin) + 1."],
            "test_cases": [
                {"input": "[1, 2, 5]\n11", "expected": "3", "is_hidden": False, "order": 1},
                {"input": "[2]\n3", "expected": "-1", "is_hidden": False, "order": 2},
                {"input": "[1]\n0", "expected": "0", "is_hidden": False, "order": 3},
                {"input": "[186, 419, 83, 408]\n6249", "expected": "20", "is_hidden": True, "order": 4},
            ],
        },

        # Searching & Sorting - Search in Rotated Sorted Array (Medium)
        {
            "slug": "search-in-rotated-sorted-array",
            "title": "Search in Rotated Sorted Array",
            "difficulty": "medium",
            "category": "searching_sorting",
            "acceptance_rate": 58.7,
            "order": 6,
            "description": "There is an integer array `nums` sorted in ascending order (with distinct values).\n\nPrior to being passed to your function, `nums` is possibly rotated at an unknown pivot index `k` (1 <= k < nums.length).\n\nGiven the array `nums` after the possible rotation and an integer `target`, return the index of `target` if it is in `nums`, or `-1` if it is not in `nums`.\n\nYou must write an algorithm with **O(log n)** runtime complexity.",
            "input_format": "Line 1: JSON array `nums`\nLine 2: integer `target`",
            "output_format": "Index integer or -1",
            "constraints": "• 1 <= nums.length <= 5000\n• -10^4 <= nums[i] <= 10^4\n• All values of nums are unique.\n• Algorithm must be O(log n).",
            "starter_templates": {
                "python": "def search(nums, target):\n    left, right = 0, len(nums) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if nums[mid] == target:\n            return mid\n        # Left half is sorted\n        if nums[left] <= nums[mid]:\n            if nums[left] <= target < nums[mid]:\n                right = mid - 1\n            else:\n                left = mid + 1\n        # Right half is sorted\n        else:\n            if nums[mid] < target <= nums[right]:\n                left = mid + 1\n            else:\n                right = mid - 1\n    return -1\n",
                "javascript": "function search(nums, target) {\n  let left = 0, right = nums.length - 1;\n  while (left <= right) {\n    let mid = Math.floor((left + right) / 2);\n    if (nums[mid] === target) return mid;\n    if (nums[left] <= nums[mid]) {\n      if (nums[left] <= target && target < nums[mid]) right = mid - 1;\n      else left = mid + 1;\n    } else {\n      if (nums[mid] < target && target <= nums[right]) left = mid + 1;\n      else right = mid - 1;\n    }\n  }\n  return -1;\n}",
            },
            "solution_explanation": "### Modified Binary Search\n\nIn a rotated sorted array, one half is always strictly sorted. Determine which half is sorted by comparing `nums[left]` and `nums[mid]`, then check whether `target` falls inside that sorted interval.",
            "optimal_solutions": {
                "python": "def search(nums, target):\n    l, r = 0, len(nums) - 1\n    while l <= r:\n        m = (l + r) // 2\n        if nums[m] == target: return m\n        if nums[l] <= nums[m]:\n            if nums[l] <= target < nums[m]: r = m - 1\n            else: l = m + 1\n        else:\n            if nums[m] < target <= nums[r]: l = m + 1\n            else: r = m - 1\n    return -1",
            },
            "hints": ["At least one half [l, mid] or [mid, r] is guaranteed to be sorted."],
            "test_cases": [
                {"input": "[4, 5, 6, 7, 0, 1, 2]\n0", "expected": "4", "is_hidden": False, "order": 1},
                {"input": "[4, 5, 6, 7, 0, 1, 2]\n3", "expected": "-1", "is_hidden": False, "order": 2},
                {"input": "[1]\n0", "expected": "-1", "is_hidden": False, "order": 3},
                {"input": "[5, 1, 3]\n5", "expected": "0", "is_hidden": True, "order": 4},
            ],
        },

        # SQL - Department Highest Salary (Medium)
        {
            "slug": "department-highest-salary",
            "title": "Department Highest Salary",
            "difficulty": "medium",
            "category": "sql",
            "acceptance_rate": 65.1,
            "order": 7,
            "description": "Write a solution to find employees who have the highest salary in each of the departments.\n\nTable `Employee`: (id, name, salary, departmentId)\nTable `Department`: (id, name)\n\nReturn the result table in any order.",
            "input_format": "SQL Schema pre-loaded with Employee and Department tables.",
            "output_format": "Tabular rows: Department, Employee, Salary",
            "constraints": "• id is the primary key.\n• DepartmentId is a foreign key.",
            "starter_templates": {
                "sql": "-- Write your SQL query statement below\nSELECT \n    d.name AS Department,\n    e.name AS Employee,\n    e.salary AS Salary\nFROM Employee e\nJOIN Department d ON e.departmentId = d.id\nWHERE (e.departmentId, e.salary) IN (\n    SELECT departmentId, MAX(salary)\n    FROM Employee\n    GROUP BY departmentId\n);\n",
            },
            "solution_explanation": "### Subquery with MAX(salary) & JOIN\n\nFilter records using an `IN` tuple `(departmentId, salary)` matching the subquery that groups by `departmentId` and computes `MAX(salary)`.",
            "optimal_solutions": {
                "sql": "SELECT d.name AS Department, e.name AS Employee, e.salary AS Salary\nFROM Employee e\nJOIN Department d ON e.departmentId = d.id\nWHERE (e.departmentId, e.salary) IN (\n    SELECT departmentId, MAX(salary) FROM Employee GROUP BY departmentId\n);",
            },
            "hints": ["Use a GROUP BY departmentId with MAX(salary) in a WHERE clause."],
            "test_cases": [
                {
                    "input": "",
                    "expected": '[{"Department":"IT","Employee":"Randy","Salary":85000},{"Department":"Sales","Employee":"Max","Salary":90000}]',
                    "is_hidden": False,
                    "order": 1,
                },
            ],
        },

        # Recursion & Backtracking - Subsets (Medium)
        {
            "slug": "subsets",
            "title": "Subsets (Power Set)",
            "difficulty": "medium",
            "category": "recursion_backtracking",
            "acceptance_rate": 75.3,
            "order": 8,
            "description": "Given an integer array `nums` of unique elements, return all possible subsets (the power set).\n\nThe solution set must not contain duplicate subsets. Return the solution in any order.",
            "input_format": "JSON array `nums`",
            "output_format": "List of lists containing all subsets",
            "constraints": "• 1 <= nums.length <= 10\n• -10 <= nums[i] <= 10\n• All elements are unique.",
            "starter_templates": {
                "python": "def subsets(nums):\n    res = []\n    def backtrack(start, curr):\n        res.append(list(curr))\n        for i in range(start, len(nums)):\n            curr.append(nums[i])\n            backtrack(i + 1, curr)\n            curr.pop()\n    backtrack(0, [])\n    return res\n",
                "javascript": "function subsets(nums) {\n  const res = [];\n  function backtrack(start, curr) {\n    res.push([...curr]);\n    for (let i = start; i < nums.length; i++) {\n      curr.push(nums[i]);\n      backtrack(i + 1, curr);\n      curr.pop();\n    }\n  }\n  backtrack(0, []);\n  return res;\n}",
            },
            "solution_explanation": "### Cascading Backtracking\n\nGenerate subsets by making a binary decision for each element: include or exclude. Total states: 2^n. Time complexity: **O(n * 2^n)**, Space complexity: **O(n)** recursion stack.",
            "optimal_solutions": {
                "python": "def subsets(nums):\n    result = [[]]\n    for n in nums:\n        result += [curr + [n] for curr in result]\n    return result",
            },
            "hints": ["Each element can either be included or excluded."],
            "test_cases": [
                {"input": "[1, 2, 3]", "expected": "[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]", "is_hidden": False, "order": 1},
                {"input": "[0]", "expected": "[[], [0]]", "is_hidden": False, "order": 2},
            ],
        },

        # Dynamic Programming - Climbing Stairs (Easy)
        {
            "slug": "climbing-stairs",
            "title": "Climbing Stairs",
            "difficulty": "easy",
            "category": "dynamic_programming",
            "acceptance_rate": 81.0,
            "order": 9,
            "description": "You are climbing a staircase. It takes `n` steps to reach the top.\n\nEach time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
            "input_format": "An integer `n`",
            "output_format": "An integer representing the number of ways",
            "constraints": "• 1 <= n <= 45",
            "starter_templates": {
                "python": "def climbStairs(n):\n    if n <= 2: return n\n    a, b = 1, 2\n    for _ in range(3, n + 1):\n        a, b = b, a + b\n    return b\n",
                "javascript": "function climbStairs(n) {\n  if (n <= 2) return n;\n  let a = 1, b = 2;\n  for (let i = 3; i <= n; i++) {\n    const next = a + b;\n    a = b;\n    b = next;\n  }\n  return b;\n}",
            },
            "solution_explanation": "### Fibonacci Recurrence\n\nTo reach step `n`, you can jump from `n-1` (1 step) or `n-2` (2 steps). Therefore `ways(n) = ways(n-1) + ways(n-2)`. Compute in **O(n)** time and **O(1)** memory.",
            "optimal_solutions": {
                "python": "def climbStairs(n):\n    a, b = 1, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a",
            },
            "hints": ["Notice the recurrence relation is equivalent to Fibonacci numbers."],
            "test_cases": [
                {"input": "2", "expected": "2", "is_hidden": False, "order": 1},
                {"input": "3", "expected": "3", "is_hidden": False, "order": 2},
                {"input": "5", "expected": "8", "is_hidden": True, "order": 3},
                {"input": "10", "expected": "89", "is_hidden": True, "order": 4},
            ],
        },
    ]

    for p_info in problems_data:
        test_cases = p_info.pop("test_cases", [])
        slug = p_info["slug"]
        problem, _ = CodingProblem.objects.update_or_create(
            slug=slug,
            defaults=p_info,
        )
        
        # Populate test cases
        ProblemTestCase.objects.filter(problem=problem).delete()
        for tc in test_cases:
            ProblemTestCase.objects.create(
                problem=problem,
                input_data=tc["input"],
                expected_output=tc["expected"],
                is_hidden=tc.get("is_hidden", False),
                order=tc.get("order", 1),
            )

    # --------------------------------------------------------------------------
    # 2. TECHNICAL QUIZZES & MCQS CATALOG
    # --------------------------------------------------------------------------
    quizzes_data = [
        {
            "slug": "python-core-advanced",
            "title": "Python Core & Advanced Architecture Assessment",
            "category": "python",
            "time_limit_minutes": 15,
            "description": "Deep-dive diagnostic evaluating Python memory management, GIL, generators, decorators, and concurrency models.",
            "questions_data": [
                {
                    "id": 1,
                    "question": "How does Python handle memory reclamation for cyclic references that cannot be freed by reference counting alone?",
                    "options": [
                        "It uses the generational cyclic garbage collector (gc module)",
                        "It relies solely on OS page unmapping on process exit",
                        "Cyclic references are automatically freed when scope ends",
                        "Through manual calls to malloc_trim()",
                    ],
                    "correct_index": 0,
                    "explanation": "Python combines reference counting (primary) with a generational cyclic garbage collector that tracks container objects across 3 generations (Gen 0, 1, 2) to identify unreachable reference cycles.",
                },
                {
                    "id": 2,
                    "question": "What is the primary architectural consequence of the Global Interpreter Lock (GIL) in standard CPython?",
                    "options": [
                        "It forbids threads from sharing memory",
                        "It prevents true parallel execution of CPU-bound Python bytecode across multiple CPU cores within a single OS process",
                        "It disables asynchronous I/O with asyncio",
                        "It forces all functions to execute sequentially in the OS kernel",
                    ],
                    "correct_index": 1,
                    "explanation": "The GIL ensures only one native OS thread executes CPython bytecode at a time, making multiprocessing or native extensions necessary for CPU-bound multi-core concurrency.",
                },
                {
                    "id": 3,
                    "question": "What will `[x * 2 for x in (1, 2, 3)]` versus `(x * 2 for x in (1, 2, 3))` produce?",
                    "options": [
                        "Both return lists with identical memory footprints",
                        "The first returns a list; the second returns a lazy generator iterator that evaluates on demand",
                        "The second creates an immutable tuple in memory immediately",
                        "A syntax error because parentheses cannot enclose comprehensions",
                    ],
                    "correct_index": 1,
                    "explanation": "Square brackets evaluate a list comprehension eagerly. Parentheses create a generator expression yielding items lazily, saving significant memory for large sequences.",
                },
                {
                    "id": 4,
                    "question": "Which method must a class implement to participate in Python's context management protocol (`with` statement)?",
                    "options": [
                        "__open__ and __close__",
                        "__enter__ and __exit__",
                        "__start__ and __stop__",
                        "__init__ and __del__",
                    ],
                    "correct_index": 1,
                    "explanation": "Context managers require `__enter__()` and `__exit__(exc_type, exc_val, exc_tb)`.",
                },
            ],
        },
        {
            "slug": "javascript-async-web",
            "title": "Modern JavaScript, Event Loop & Web Performance",
            "category": "javascript",
            "time_limit_minutes": 15,
            "description": "Test understanding of JS concurrency, microtasks vs macrotasks, prototypal inheritance, and async patterns.",
            "questions_data": [
                {
                    "id": 1,
                    "question": "In what order will the following execute in the Node.js / Browser event loop?\nconsole.log(1);\nsetTimeout(() => console.log(2), 0);\nPromise.resolve().then(() => console.log(3));\nconsole.log(4);",
                    "options": [
                        "1, 4, 3, 2",
                        "1, 2, 3, 4",
                        "1, 3, 4, 2",
                        "1, 4, 2, 3",
                    ],
                    "correct_index": 0,
                    "explanation": "Synchronous statements log 1 and 4 first. Microtasks (Promise.then) run immediately after the current macrotask stack clears (logging 3). Macrotasks (setTimeout) execute in the next tick (logging 2).",
                },
                {
                    "id": 2,
                    "question": "How does `Object.create(proto)` differ from object literal `{}`?",
                    "options": [
                        "It creates a deep clone of proto",
                        "It creates a new object whose internal [[Prototype]] is explicitly linked to proto",
                        "It merges proto properties onto the global scope",
                        "It seals the prototype so no new properties can be added",
                    ],
                    "correct_index": 1,
                    "explanation": "Object.create(proto) sets the internal [[Prototype]] of the newly created object to the argument proto, enabling prototypal delegation without constructor functions.",
                },
                {
                    "id": 3,
                    "question": "What is the primary benefit of `Promise.allSettled()` over `Promise.all()`?",
                    "options": [
                        "It executes requests sequentially instead of concurrently",
                        "It never rejects; it waits for all promises to resolve or reject and returns an array of status descriptors",
                        "It automatically retries rejected promises up to 3 times",
                        "It reduces network payload size",
                    ],
                    "correct_index": 1,
                    "explanation": "Promise.all() short-circuits on the first rejection. Promise.allSettled() waits for all promises and provides {status: 'fulfilled' | 'rejected', value/reason}.",
                },
            ],
        },
        {
            "slug": "dsa-core-mastery",
            "title": "Data Structures & Algorithms Diagnostic",
            "category": "dsa",
            "time_limit_minutes": 20,
            "description": "Assess mastery of asymptotic time complexity, tree traversals, shortest path, and dynamic programming paradigms.",
            "questions_data": [
                {
                    "id": 1,
                    "question": "What is the worst-case time complexity of inserting n elements into a Binary Search Tree (BST)?",
                    "options": [
                        "O(n log n)",
                        "O(n^2)",
                        "O(n)",
                        "O(1)",
                    ],
                    "correct_index": 1,
                    "explanation": "If elements are inserted in sorted order, an un-balanced BST degenerates into a linked list of height n, making n insertions take 1 + 2 + ... + n = O(n^2) total time.",
                },
                {
                    "id": 2,
                    "question": "Which data structure is optimal for implementing Dijkstra's single-source shortest path algorithm on sparse graphs with non-negative weights?",
                    "options": [
                        "Stack",
                        "Min-Heap / Priority Queue",
                        "FIFO Queue",
                        "Disjoint Set (Union-Find)",
                    ],
                    "correct_index": 1,
                    "explanation": "A Min-Heap yields O((V + E) log V) complexity by extracting the minimum distance vertex in O(log V) time.",
                },
                {
                    "id": 3,
                    "question": "What distinguishes Dynamic Programming from Greedy algorithms?",
                    "options": [
                        "Greedy guarantees globally optimal solutions for all NP-hard problems",
                        "DP considers all overlapping subproblems and makes choices globally, whereas Greedy commits locally to the best immediate step without backtracking",
                        "DP only works on sorted input arrays",
                        "Greedy requires O(n^3) memory tables",
                    ],
                    "correct_index": 1,
                    "explanation": "Greedy algorithms make myopic, local choices. Dynamic programming systematically optimizes overlapping subproblems with optimal substructure.",
                },
            ],
        },
        {
            "slug": "sql-database-mastery",
            "title": "SQL, Indexing & Relational Architecture",
            "category": "sql",
            "time_limit_minutes": 15,
            "description": "Query optimization, ACID guarantees, B-tree indexes, window functions, and normalization.",
            "questions_data": [
                {
                    "id": 1,
                    "question": "What is the key advantage of a B+ Tree index over a Hash index for relational databases like PostgreSQL/MySQL?",
                    "options": [
                        "B+ Trees have O(1) point lookups for equality queries",
                        "B+ Trees maintain sorted order at leaf nodes, efficiently supporting range queries (BETWEEN, >, <) and ORDER BY",
                        "B+ Trees do not require disk storage",
                        "B+ Trees automatically encrypt table columns",
                    ],
                    "correct_index": 1,
                    "explanation": "Hash indexes only support exact equality (=). B+ Trees link leaf pages in a doubly linked list, enabling fast sequential range scans and range lookups in O(log n).",
                },
                {
                    "id": 2,
                    "question": "In ACID database transactions, what does the 'I' (Isolation) guarantee?",
                    "options": [
                        "Transactions are stored on isolated backup servers",
                        "Concurrent transactions execute without interfering with one another or seeing dirty uncommitted state (governed by isolation levels)",
                        "Transactions must complete in under 1 millisecond",
                        "Indexes are automatically partitioned across disk blocks",
                    ],
                    "correct_index": 1,
                    "explanation": "Isolation prevents concurrent transactions from generating inconsistent states (dirty reads, non-repeatable reads, phantom reads) through concurrency control mechanisms like MVCC or 2PL.",
                },
            ],
        },
        {
            "slug": "aptitude-logical-reasoning",
            "title": "Aptitude & Logical Reasoning Diagnostic",
            "category": "aptitude",
            "time_limit_minutes": 15,
            "description": "Quantitative analysis, logical deductions, data sufficiency, and pattern discovery for campus & company recruitment.",
            "questions_data": [
                {
                    "id": 1,
                    "question": "A train running at 72 km/h crosses a 260m long platform in 23 seconds. What is the length of the train?",
                    "options": [
                        "200 meters",
                        "220 meters",
                        "240 meters",
                        "180 meters",
                    ],
                    "correct_index": 0,
                    "explanation": "Speed = 72 * (5/18) = 20 m/s. Total distance covered in 23s = 20 * 23 = 460m. Total distance = Train Length + Platform Length. Train Length = 460 - 260 = 200m.",
                },
                {
                    "id": 2,
                    "question": "Find the missing number in the sequence: 3, 8, 18, 38, 78, ?",
                    "options": [
                        "158",
                        "148",
                        "168",
                        "138",
                    ],
                    "correct_index": 0,
                    "explanation": "Each term follows the pattern: current * 2 + 2. (3*2+2=8, 8*2+2=18, 18*2+2=38, 38*2+2=78, 78*2+2=158).",
                },
            ],
        },
    ]

    for q_info in quizzes_data:
        slug = q_info["slug"]
        TechnicalQuiz.objects.update_or_create(
            slug=slug,
            defaults={
                "title": q_info["title"],
                "category": q_info["category"],
                "description": q_info["description"],
                "time_limit_minutes": q_info["time_limit_minutes"],
                "total_questions": len(q_info["questions_data"]),
                "questions_data": q_info["questions_data"],
            },
        )

