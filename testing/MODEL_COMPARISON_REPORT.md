# JesseCoder Multi-Model Comparison Report

- **Generated**: 2026-09-22 05:29:29
- **Total Tasks**: 10
- **Models Evaluated**: `jesse-prod`, `jesse-pristine`, `jesse`

## Overall Model Performance

| Model | Passed | Failed | Pass Rate | Avg Latency |
| :--- | :---: | :---: | :---: | :---: |
| `jesse-prod` | 1/10 | 9 | **10.0%** | 63.3ms |
| `jesse-pristine` | 1/10 | 9 | **10.0%** | 35.6ms |
| `jesse` | 1/10 | 9 | **10.0%** | 40.7ms |

## Task-by-Task Comparison Matrix

| Task ID | Title | Language | `jesse-prod` | `jesse-pristine` | `jesse` |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `task_01` | Circular Queue | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_02` | LRU Cache | `python` | ✅ PASS | ✅ PASS | ✅ PASS |
| `task_03` | Sliding Window Rate Limiter | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_04` | Shortest Path | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_05` | Inventory Transaction | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_06` | Payment Aggregation | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_07` | Merge Time Intervals | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_08` | Binary Search Tree | `cpp` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_09` | Dependency Build Order | `javascript` | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| `task_10` | Video Watch Time | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |

## Detailed Analysis & Observations

1. **Python Tasks**: All models demonstrate strong algorithmic synthesis on well-formed prompts (e.g. `task_02` LRU Cache passed across models). Default placeholder stubs appear when the prompt structure triggers template responses.
2. **Non-Python Tasks (C++ / JavaScript)**: Remote models frequently wrap Python syntax inside ````cpp```` or ````javascript```` fences, leading to compiler and runtime syntax errors.
3. **Model Consistency**: Across all evaluated models (`jesse-prod`, `jesse-pristine`, `jesse`), the core generation behavior is consistent, sharing identical pass/fail profiles on standard input tasks.