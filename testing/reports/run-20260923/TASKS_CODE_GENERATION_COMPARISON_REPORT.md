# JesseCoder Multi-Model Comparison Report

- **Generated**: 2026-09-23 23:48:54
- **Total Tasks**: 45
- **Models Evaluated**: `jesse-prod`, `jesse-pristine`, `jesse`
- **Output Matching**: tolerant (value labels & line breaks ignored; values and their order must match)

## Overall Model Performance

| Model | Passed | Initial | On Retry | Failed | Pass Rate | Avg Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `jesse-prod` | 16/45 | 16 | 0 | 29 | **35.6%** | 47.2ms |
| `jesse-pristine` | 16/45 | 16 | 0 | 29 | **35.6%** | 38.5ms |
| `jesse` | 16/45 | 16 | 0 | 29 | **35.6%** | 34.8ms |

## Task-by-Task Comparison Matrix

| Task ID | Title | Language | `jesse-prod` | `jesse-pristine` | `jesse` |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `task_01` | Circular Queue | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_02` | LRU Cache | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_03` | Sliding Window Rate Limiter | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_04` | Shortest Path | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_05` | Inventory Transaction | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_06` | Payment Aggregation | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_07` | Merge Time Intervals | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_08` | Binary Search Tree | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_09` | Dependency Build Order | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_10` | Video Watch Time | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_11` | Weighted Job Scheduling | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_12` | Dynamic Connectivity | `cpp` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_13` | Event Stream Deduplication | `javascript` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_14` | Limit Order Matching Engine | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_15` | Weighted Grid Shortest Path | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_16` | Parallel Dependency Scheduler | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_17` | TTL Key Value Store | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_18` | Range Updates and Queries | `cpp` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_19` | LFU Cache | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_20` | DAG Critical Path | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_21` | Word Frequency Counter | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_22` | CSV Column Formatter | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_23` | Matrix Transposition | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_24` | Balanced Delimiters Checker | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_25` | Interval Intersections | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_26` | Sliding Window Maximum | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_27` | Trie Autocomplete with Frequency | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_28` | A* 2D Grid Pathfinding | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_29` | Distributed Consistent Hash Ring | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_30` | Regex NFA Engine | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_31` | Stable Deduplication | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_32` | Word Length Summary | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_33` | Column Totals | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_34` | Run Length Encoding | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_35` | Balanced Brackets | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_36` | Top K Frequencies | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_37` | Minimum Meeting Rooms | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_38` | Bounded Coin Change | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_39` | Island Count | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_40` | Prefix Sum Queries | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_41` | Shortest Paths with Negative Edges | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_42` | Offline Range Order Statistics | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_43` | Maximum Flow | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_44` | Minimum Spanning Forest | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_45` | Lexicographically Smallest Topological Order | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |

## Detailed Analysis & Observations

1. **Python Tasks**: All models demonstrate strong algorithmic synthesis on well-formed prompts (e.g. `task_02` LRU Cache passed across models). Default placeholder stubs appear when the prompt structure triggers template responses.
2. **Non-Python Tasks (C++ / JavaScript)**: Remote models frequently wrap Python syntax inside ````cpp```` or ````javascript```` fences, leading to compiler and runtime syntax errors.
3. **Model Consistency**: Across all evaluated models (`jesse-prod`, `jesse-pristine`, `jesse`), the core generation behavior is consistent, sharing identical pass/fail profiles on standard input tasks.
4. **Auto-Repair Self Healing**: When retries are enabled (minimum 3 retries), error diagnostics and mismatched outputs are sent back with structured feedback to repair flawed solutions automatically.