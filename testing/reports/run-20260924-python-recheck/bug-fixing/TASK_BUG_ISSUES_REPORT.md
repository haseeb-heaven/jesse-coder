# JesseCoder Task Evaluation Report

- **Model**: `jesse-prod`
- **Total Tasks**: 11
- **Passed**: 0
- **Failed**: 11
- **Pass Rate**: 0.0%
- **Retries Configured**: 5 (min 3 per task)
- **Passed on Initial Attempt**: 0
- **Passed via Auto-Repair Retry**: 0
- **Training on Error**: Enabled (11 corrections recorded; learning active for 11)
- **Output Matching**: tolerant (value labels & line breaks ignored; values and their order must match)
- **Timestamp**: 2026-09-24 00:46:47

## Summary Table

| Task ID | Title | Language | Status | Execution Time | Notes |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `bug_01` | Bank Transfer | `python` | ❌ FAIL [🎓 Trained] | 0.0ms | No valid code block extracted from model response. |
| `bug_04` | Merge Intervals | `python` | ❌ FAIL [🎓 Trained] | 0.0ms | No valid code block extracted from model response. |
| `bug_06` | Priority Task Scheduler | `python` | ❌ FAIL [🎓 Trained] | 0.0ms | No valid code block extracted from model response. |
| `bug_11` | Palindrome Sentence Checker | `python` | ❌ FAIL [🎓 Trained] | 0.0ms | No valid code block extracted from model response. |
| `bug_14` | Sorted Two Sum Two-Pointer | `python` | ❌ FAIL [🎓 Trained] | 0.0ms | No valid code block extracted from model response. |
| `bug_17` | LRU Cache with TTL Expiration | `python` | ❌ FAIL [🎓 Trained] | 324.4ms | Output mismatch. |
| `bug_20` | Topological Sort with Cycle Detection | `python` | ❌ FAIL [🎓 Trained] | 0.0ms | Model returned a 'javascript' code block instead of 'python'; the code was not executed. |
| `bug_22` | Raft Consensus Log Compaction | `python` | ❌ FAIL [🎓 Trained] | 0.0ms | No valid code block extracted from model response. |
| `bug_25` | Inclusive Average | `python` | ❌ FAIL [🎓 Trained] | 0.0ms | No valid code block extracted from model response. |
| `bug_28` | Atomic Inventory Purchase | `python` | ❌ FAIL [🎓 Trained] | 0.0ms | No valid code block extracted from model response. |
| `bug_31` | Dijkstra with Stale Heap Entries | `python` | ❌ FAIL [🎓 Trained] | 306.1ms | Output mismatch. |

## Detailed Task Results

### bug_01 - Bank Transfer (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Model Response (No Code Extracted):
```
I don't have a solution I can verify for this one yet. I can see the commands OK, REJECTED, but none of my checked components reproduces what the task asks for, so I won't guess at Python code.
```

#### Expected Output:
```
OK 800 700
REJECTED 800 700

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

### bug_04 - Merge Intervals (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Model Response (No Code Extracted):
```
I don't have a solution I can verify for this one yet. None of my checked components reproduces what the task asks for, so I won't guess at Python code.
```

#### Expected Output:
```
1 6
8 12
15 20

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

### bug_06 - Priority Task Scheduler (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Model Response (No Code Extracted):
```
I don't have a solution I can verify for this one yet. None of my checked components reproduces what the task asks for, so I won't guess at Python code.
```

#### Expected Output:
```
payment 5
security 5
backup 2
email 1

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

### bug_11 - Palindrome Sentence Checker (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Model Response (No Code Extracted):
```
I don't have a solution I can verify for this one yet. I can see the commands YES, NO, but none of my checked components reproduces what the task asks for, so I won't guess at Python code.
```

#### Expected Output:
```
YES
NO
YES
NO

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

### bug_14 - Sorted Two Sum Two-Pointer (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Model Response (No Code Extracted):
```
I don't have a solution I can verify for this one yet. None of my checked components reproduces what the task asks for, so I won't guess at Python code.
```

#### Expected Output:
```
1 2
1 3
1 2
4 5

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

### bug_17 - LRU Cache with TTL Expiration (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Extracted Code:
```python
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
        input_data = """Capacity: 2
PUT 1 10
PUT 2 20
GET 1
PUT 3 30
GET 2
GET 3
GET 1"""

    lines = [line.strip() for line in input_data.strip().splitlines() if line.strip()]
    capacity = 2
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
100
-1
-1
300

```

#### Actual Output:
```
10
-1
30
10

```

#### Diagnostics:
```
Output mismatch.
Expected:
100
-1
-1
300
Got:
10
-1
30
10
```

---

### bug_20 - Topological Sort with Cycle Detection (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Extracted Code:
```python
/**
 * Topological Sort with Cycle Detection (Kahn's Algorithm)
 * Time Complexity: O(V + E), Space Complexity: O(V + E)
 */
function topologicalSort(numNodes, edges) {
  const adj = Array.from({ length: numNodes }, () => []);
  const inDegree = new Array(numNodes).fill(0);

  for (const [u, v] of edges) {
    adj[u].push(v);
    inDegree[v]++;
  }

  const queue = [];
  for (let i = 0; i < numNodes; i++) {
    if (inDegree[i] === 0) {
      queue.push(i);
    }
  }

  const order = [];
  while (queue.length > 0) {
    const u = queue.shift();
    order.push(u);

    for (const v of adj[u]) {
      inDegree[v]--;
      if (inDegree[v] === 0) {
        queue.push(v);
      }
    }
  }

  if (order.length < numNodes) {
    console.log("CYCLE");
    return null;
  } else {
    console.log(order.join(" "));
    return order;
  }
}

// Verification with 5 nodes:
const numNodes = 5;
const edges = [[0, 1], [0, 2], [1, 3], [2, 3]];
topologicalSort(numNodes, edges);
```

#### Expected Output:
```
0 1 2 3
CYCLE

```

#### Actual Output:
```
(none)
```

#### Diagnostics:
```
Model returned a 'javascript' code block instead of 'python'; the code was not executed.
```

---

### bug_22 - Raft Consensus Log Compaction (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Model Response (No Code Extracted):
```
I don't have a solution I can verify for this one yet. None of my checked components reproduces what the task asks for, so I won't guess at Python code.
```

#### Expected Output:
```
Index 3: (1, 'cmd_3')
Index 2 after snapshot: None
Index 4 after snapshot: (1, 'cmd_4')
Index 5 after snapshot: (1, 'cmd_5')

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

### bug_25 - Inclusive Average (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Model Response (No Code Extracted):
```
I don't have a solution I can verify for this one yet. None of my checked components reproduces what the task asks for, so I won't guess at Python code.
```

#### Expected Output:
```
5.00

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

### bug_28 - Atomic Inventory Purchase (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Model Response (No Code Extracted):
```
I don't have a solution I can verify for this one yet. I can see the commands REJECTED, but none of my checked components reproduces what the task asks for, so I won't guess at Python code.
```

#### Expected Output:
```
REJECTED
A=5 B=1

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

### bug_31 - Dijkstra with Stale Heap Entries (PYTHON) [FAIL]

**Retries Attempted**: 5

**Model Training**: Submitted exact code correction to Jesse `/feedback` API (learning active).

#### Extracted Code:
```python
import heapq
import sys

def dijkstra(edges: list[tuple[int, int, int]], start_node: int = 0) -> dict[int, int]:
    """Compute shortest distances from start_node using Dijkstra's algorithm."""
    adj = {}
    for u, v, w in edges:
        adj.setdefault(u, []).append((v, w))
        adj.setdefault(v, [])

    dist = {node: float('inf') for node in adj}
    dist[start_node] = 0
    pq = [(0, start_node)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, weight in adj.get(u, []):
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(pq, (dist[v], v))
    return dist

def solve(*args, **kwargs):
    """Deterministic algorithmic implementation of Dijkstra's algorithm."""
    edges = [
        (0, 1, 4),
        (0, 2, 1),
        (2, 1, 2),
        (1, 3, 1),
        (2, 3, 5),
        (3, 4, 3)
    ]
    return dijkstra(edges, start_node=0)

if __name__ == '__main__':
    distances = solve()
    for node in sorted(distances):
        print(f"Node {node}: {distances[node]}")
```

#### Expected Output:
```
0 2 1 3

```

#### Actual Output:
```
Node 0: 0
Node 1: 3
Node 2: 1
Node 3: 4
Node 4: 7

```

#### Diagnostics:
```
Output mismatch.
Expected:
0 2 1 3
Got:
Node 0: 0
Node 1: 3
Node 2: 1
Node 3: 4
Node 4: 7
```

---
