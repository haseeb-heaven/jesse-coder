# JesseCoder Task Evaluation Report

- **Model**: `jesse-prod`
- **Total Tasks**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%
- **Retries Configured**: 3 (min 3 per task)
- **Passed on Initial Attempt**: 1
- **Passed via Auto-Repair Retry**: 0
- **Output Matching**: tolerant (value labels & line breaks ignored; values and their order must match)
- **Timestamp**: 2026-09-23 04:21:18

## Summary Table

| Task ID | Title | Language | Status | Execution Time | Notes |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `task_02` | LRU Cache | `python` | ✅ PASS | 40.5ms | Matches expected output |

## Detailed Task Results

### task_02 - LRU Cache (PYTHON) [PASS]

#### Extracted Code:
```python
from collections import OrderedDict
import sys


def main():
    data = [line.strip() for line in sys.stdin.read().splitlines() if line.strip()]
    cap = 2
    if data and all(tok.lstrip("-").isdigit() for tok in data[0].split()):
        header = [int(tok) for tok in data.pop(0).split()]
        if len(header) >= 2 or cap == 0:
            cap = header[0]
    cache = OrderedDict()
    out = []
    for line in data:
        parts = line.split()
        cmd = parts[0].upper()
        if cmd in ("PUT", "SET"):
            key, value = parts[1], parts[2]
            if key in cache:
                cache.pop(key)
            cache[key] = value
            if len(cache) > cap:
                cache.popitem(last=False)
        elif cmd == "GET":
            key = parts[1]
            if key not in cache:
                out.append("-1")
            else:
                cache.move_to_end(key)
                out.append(cache[key])
    print("\n".join(out))

if __name__ == "__main__":
    main()
```

#### Expected Output:
```
10
-1
30
10

```

#### Actual Output:
```
10
-1
30
10

```

---
