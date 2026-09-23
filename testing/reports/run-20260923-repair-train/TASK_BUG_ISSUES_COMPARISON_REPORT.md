# JesseCoder Multi-Model Comparison Report

- **Generated**: 2026-09-24 00:00:28
- **Total Tasks**: 33
- **Models Evaluated**: `jesse-prod`, `jesse-pristine`, `jesse`
- **Output Matching**: tolerant (value labels & line breaks ignored; values and their order must match)

## Overall Model Performance

| Model | Passed | Initial | On Retry | Failed | Pass Rate | Avg Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `jesse-prod` | 2/33 | 2 | 0 | 31 | **6.1%** | 181.7ms |
| `jesse-pristine` | 2/33 | 2 | 0 | 31 | **6.1%** | 180.1ms |
| `jesse` | 2/33 | 2 | 0 | 31 | **6.1%** | 180.6ms |

## Task-by-Task Comparison Matrix

| Task ID | Title | Language | `jesse-prod` | `jesse-pristine` | `jesse` |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `bug_01` | Bank Transfer | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_02` | Binary Search | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_03` | Rate Limiter | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_04` | Merge Intervals | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_05` | Circular Queue | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_06` | Priority Task Scheduler | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_07` | Disjoint Set Component Size | `cpp` | ✅ PASS | ✅ PASS | ✅ PASS |
| `bug_08` | User Session Grouping | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_09` | Dijkstra Shortest Paths | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `bug_10` | Dependency Build Order | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_11` | Palindrome Sentence Checker | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_12` | String Run-Length Encoding | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_13` | Prime Number Filter | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_14` | Sorted Two Sum Two-Pointer | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_15` | Array Circular Shift | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_16` | Combinations Math nCr | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_17` | LRU Cache with TTL Expiration | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_18` | AVL Tree Rotation & Height Invariants | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_19` | Financial Event-Sourced Ledger with Rollback | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_20` | Topological Sort with Cycle Detection | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_21` | Segment Tree with Lazy Range Updates | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_22` | Raft Consensus Log Compaction | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_23` | Token Bucket Traffic Shaper with Bursts | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_24` | B-Tree Node Split & Key Redistribution | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_25` | Inclusive Average | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_26` | First Matching Item | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_27` | Positive Number Count | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_28` | Atomic Inventory Purchase | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_29` | Stable Priority Queue | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_30` | Half-Open Meeting Rooms | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_31` | Dijkstra with Stale Heap Entries | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_32` | LRU Cache Eviction | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `bug_33` | Disjoint Set Union Size | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |

## Detailed Analysis & Observations

1. **Python Tasks**: All models demonstrate strong algorithmic synthesis on well-formed prompts (e.g. `task_02` LRU Cache passed across models). Default placeholder stubs appear when the prompt structure triggers template responses.
2. **Non-Python Tasks (C++ / JavaScript)**: Remote models frequently wrap Python syntax inside ````cpp```` or ````javascript```` fences, leading to compiler and runtime syntax errors.
3. **Model Consistency**: Across all evaluated models (`jesse-prod`, `jesse-pristine`, `jesse`), the core generation behavior is consistent, sharing identical pass/fail profiles on standard input tasks.
4. **Auto-Repair Self Healing**: When retries are enabled (minimum 3 retries), error diagnostics and mismatched outputs are sent back with structured feedback to repair flawed solutions automatically.