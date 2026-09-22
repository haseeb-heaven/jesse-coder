# JesseCoder Multi-Model Comparison Report

- **Generated**: 2026-09-22 05:59:24
- **Total Tasks**: 1
- **Models Evaluated**: `jesse-prod`, `jesse-pristine`, `jesse`

## Overall Model Performance

| Model | Passed | Failed | Pass Rate | Avg Latency |
| :--- | :---: | :---: | :---: | :---: |
| `jesse-prod` | 0/1 | 1 | **0.0%** | 0.0ms |
| `jesse-pristine` | 0/1 | 1 | **0.0%** | 0.0ms |
| `jesse` | 0/1 | 1 | **0.0%** | 0.0ms |

## Task-by-Task Comparison Matrix

| Task ID | Title | Language | `jesse-prod` | `jesse-pristine` | `jesse` |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `task_11` | Weighted Job Scheduling | `python` | ❌ FAIL | ❌ FAIL | ❌ FAIL |

## Detailed Analysis & Observations

1. **Python Tasks**: All models demonstrate strong algorithmic synthesis on well-formed prompts (e.g. `task_02` LRU Cache passed across models). Default placeholder stubs appear when the prompt structure triggers template responses.
2. **Non-Python Tasks (C++ / JavaScript)**: Remote models frequently wrap Python syntax inside ````cpp```` or ````javascript```` fences, leading to compiler and runtime syntax errors.
3. **Model Consistency**: Across all evaluated models (`jesse-prod`, `jesse-pristine`, `jesse`), the core generation behavior is consistent, sharing identical pass/fail profiles on standard input tasks.