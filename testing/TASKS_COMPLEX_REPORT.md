# JesseCoder Task Evaluation Report

- **Model**: `jesse-prod`
- **Total Tasks**: 10
- **Passed**: 0
- **Failed**: 10
- **Pass Rate**: 0.0%
- **Output Matching**: tolerant (value labels & line breaks ignored; values and their order must match)
- **Timestamp**: 2026-09-22 07:16:18

## Summary Table

| Task ID | Title | Language | Status | Execution Time | Notes |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `task_11` | Weighted Job Scheduling | `python` | ❌ FAIL | 0.0ms | No valid code block extracted from model response. |
| `task_12` | Dynamic Connectivity | `cpp` | ❌ FAIL | 0.0ms | Model returned a 'python' code block instead of 'cpp'; the code was not executed. |
| `task_13` | Event Stream Deduplication | `javascript` | ❌ FAIL | 0.0ms | No valid code block extracted from model response. |
| `task_14` | Limit Order Matching Engine | `python` | ❌ FAIL | 0.0ms | No valid code block extracted from model response. |
| `task_15` | Weighted Grid Shortest Path | `cpp` | ❌ FAIL | 0.0ms | Model returned a 'python' code block instead of 'cpp'; the code was not executed. |
| `task_16` | Parallel Dependency Scheduler | `javascript` | ❌ FAIL | 0.0ms | No valid code block extracted from model response. |
| `task_17` | TTL Key Value Store | `python` | ❌ FAIL | 0.0ms | No valid code block extracted from model response. |
| `task_18` | Range Updates and Queries | `cpp` | ❌ FAIL | 0.0ms | No valid code block extracted from model response. |
| `task_19` | LFU Cache | `javascript` | ❌ FAIL | 0.0ms | Model returned a 'python' code block instead of 'javascript'; the code was not executed. |
| `task_20` | DAG Critical Path | `python` | ❌ FAIL | 80.2ms | Output mismatch. |

## Detailed Task Results

### task_11 - Weighted Job Scheduling (PYTHON) [FAIL]

#### Model Response (No Code Extracted):
```
A job starting exactly when another job ends is allowed.
```

#### Expected Output:
```
MAX_PROFIT 22
JOBS A D H J

```

#### Actual Output:
```
(none)
```

#### Diagnostics:
```
No valid code block extracted from model response.
```

---

### task_12 - Dynamic Connectivity (CPP) [FAIL]

#### Extracted Code:
```cpp
def solve(*args, **kwargs):
    """Deterministic algorithmic implementation by Jesse."""
    pass

if __name__ == '__main__':
    print('Jesse coding solver ready.')
```

#### Expected Output:
```
YES
3
NO
5
YES
2
NO

```

#### Actual Output:
```
(none)
```

#### Diagnostics:
```
Model returned a 'python' code block instead of 'cpp'; the code was not executed.
```

---

### task_13 - Event Stream Deduplication (JAVASCRIPT) [FAIL]

#### Model Response (No Code Extracted):
```
An event is accepted only if the same user. Event type has not already been accepted during the previous 5 seconds.
```

#### Expected Output:
```
ACCEPT
DROP
ACCEPT
ACCEPT
ACCEPT
ACCEPT
DROP
ACCEPT
ACCEPT

```

#### Actual Output:
```
(none)
```

#### Diagnostics:
```
No valid code block extracted from model response.
```

---

### task_14 - Limit Order Matching Engine (PYTHON) [FAIL]

#### Model Response (No Code Extracted):
```
A BUY order matches the lowest available SELL price that does not exceed its limit. A SELL order matches the highest available BUY price that meets its limit. Orders at the same price are matched FIFO. The trade price is the price of the resting order.
```

#### Expected Output:
```
TRADE B2 S1 3 101
TRADE B1 S1 1 100
TRADE B3 S2 4 101
TRADE B1 S3 2 100
BIDS
B1 2 100
B4 2 100
ASKS
S2 1 101

```

#### Actual Output:
```
(none)
```

#### Diagnostics:
```
No valid code block extracted from model response.
```

---

### task_15 - Weighted Grid Shortest Path (CPP) [FAIL]

#### Extracted Code:
```cpp
class BSTNode:
    def __init__(self, val: int):
        self.val = val
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, val: int) -> None:
        if not self.root:
            self.root = BSTNode(val)
            return
        curr = self.root
        while True:
            if val < curr.val:
                if curr.left is None:
                    curr.left = BSTNode(val)
                    return
                curr = curr.left
            elif val > curr.val:
                if curr.right is None:
                    curr.right = BSTNode(val)
                    return
                curr = curr.right
            else:
                return  # Duplicate

    def search(self, val: int) -> bool:
        curr = self.root
        while curr:
            if val == curr.val:
                return True
            curr = curr.left if val < curr.val else curr.right
        return False

    def inorder(self) -> list[int]:
        result = []
        def _traverse(node):
            if node:
                _traverse(node.left)
                result.append(node.val)
                _traverse(node.right)
        _traverse(self.root)
        return result

if __name__ == "__main__":
    bst = BinarySearchTree()
    for x in [50, 30, 70, 20, 40, 60, 80]:
        bst.insert(x)
    print(f"In-order traversal: {bst.inorder()}")
    assert bst.search(40) is True
    assert bst.search(99) is False
```

#### Expected Output:
```
COST 12
PATHS 1

```

#### Actual Output:
```
(none)
```

#### Diagnostics:
```
Model returned a 'python' code block instead of 'cpp'; the code was not executed.
```

---

### task_16 - Parallel Dependency Scheduler (JAVASCRIPT) [FAIL]

#### Model Response (No Code Extracted):
```
A task can start only after all its dependencies have completed. Tasks are non-preemptive. Finish time in the order tasks are started, followed by the total makespan.
```

#### Expected Output:
```
A W1 0 3
B W2 0 2
C W1 3 7
D W2 3 5
F W2 5 6
E W1 7 10
G W1 10 12
MAKESPAN 12

```

#### Actual Output:
```
(none)
```

#### Diagnostics:
```
No valid code block extracted from model response.
```

---

### task_17 - TTL Key Value Store (PYTHON) [FAIL]

#### Model Response (No Code Extracted):
```
A key is valid only while current_time is strictly less than its expiration time. Input timestamps are non-decreasing.
```

#### Expected Output:
```
10
NULL
30
DELETED
NULL
c=40
NULL

```

#### Actual Output:
```
(none)
```

#### Diagnostics:
```
No valid code block extracted from model response.
```

---

### task_18 - Range Updates and Queries (CPP) [FAIL]

#### Model Response (No Code Extracted):
```
Indices are 1-based.
```

#### Expected Output:
```
36
25
4
23
3
3

```

#### Actual Output:
```
(none)
```

#### Diagnostics:
```
No valid code block extracted from model response.
```

---

### task_19 - LFU Cache (JAVASCRIPT) [FAIL]

#### Extracted Code:
```javascript
from collections import OrderedDict
import re
import sys

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

def solve(*args, **kwargs):
    """Deterministic algorithmic implementation of LRU Cache."""
    input_data = None
    if args:
        if isinstance(args[0], str):
            input_data = args[0]
        elif isinstance(args[0], (list, tuple)):
            input_data = "\n".join(str(x) for x in args[0])
    if input_data is None:
        input_data = """Capacity: 3
GET returns
PUT 1 10
PUT 2 20
PUT 3 30
GET 1
GET 2
PUT 4 40
GET 3
GET 4
GET 1
PUT 5 50
GET 2
GET 4
GET 5"""

    lines = [line.strip() for line in input_data.strip().splitlines() if line.strip()]
    capacity = 3
    output = []
    cache = None

    for line in lines:
        parts = line.split()
        if not parts:
            continue
        op = parts[0].upper()
        if op.startswith("CAPACITY") or op == "CAP":
            val = parts[1] if len(parts) > 1 else parts[0].split(":")[-1]
            try:
                capacity = int(val.replace(":", ""))
                cache = LRUCache(capacity)
            except ValueError:
                continue
        else:
            m_put = re.match(r'(?i)put\s*\(?\s*(\d+)\s*[,\s]\s*(\d+)\s*\)?', line)
            if m_put:
                if cache is None:
                    cache = LRUCache(capacity)
                cache.put(int(m_put.group(1)), int(m_put.group(2)))
                continue
            m_get = re.match(r'(?i)get\s*\(?\s*(\d+)\s*\)?', line)
            if m_get:
                if cache is None:
                    cache = LRUCache(capacity)
                output.append(cache.get(int(m_get.group(1))))
                continue
    return output

if __name__ == '__main__':
    data = None
    if not sys.stdin.isatty():
        try:
            stdin_content = sys.stdin.read().strip()
            if stdin_content:
                data = stdin_content
        except Exception:
            data = None
    results = solve(data)
    for res in results:
        print(res)
```

#### Expected Output:
```
10
20
-1
40
10
-1
40
50

```

#### Actual Output:
```
(none)
```

#### Diagnostics:
```
Model returned a 'python' code block instead of 'javascript'; the code was not executed.
```

---

### task_20 - DAG Critical Path (PYTHON) [FAIL]

#### Extracted Code:
```python
def solve(*args, **kwargs):
    """Deterministic algorithmic implementation by Jesse."""
    pass

if __name__ == '__main__':
    print('Jesse coding solver ready.')
```

#### Expected Output:
```
DURATION 17
PATH A D E G

```

#### Actual Output:
```
Jesse coding solver ready.

```

#### Diagnostics:
```
Output mismatch.
Expected:
DURATION 17
PATH A D E G
Got:
Jesse coding solver ready.
```

---
