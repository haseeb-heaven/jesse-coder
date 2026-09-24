# Automated Testing Suite for JesseCoder

This directory contains the automated end-to-end task testing suite for JesseCoder.

## Directory Structure

```text
testing/
├── automated_testing.py   # Multi-model test runner with retries, repair mode & learning
├── tasks/                 # Benchmark task datasets (all JSON files stored here)
│   ├── task_bug_issues.json       # Dataset 2: Fixing bugs/issues in code (35 tasks, mode: fix_bugs)
│   ├── tasks_code_generation.json # Dataset 1: Generating new code (48 tasks, mode: generate)
│   ├── task_code_generation.json  # Alias to tasks_code_generation.json
│   └── tasks_bug_fixing.json      # Alias to task_bug_issues.json
├── reports/               # Output directory where report JSON & Markdown files are written
│   └── .gitkeep
└── README.md              # Testing suite documentation
```

## Datasets

The suite is organized into **2 official datasets** located in `testing/tasks/`:

1. **Generating New Code**: [`tasks/tasks_code_generation.json`](tasks/tasks_code_generation.json) (`mode: generate`)
   - 48 algorithmic coding tasks written from natural-language specifications (28 `python`, 10 `cpp`, 10 `javascript`): 15 easy, 15 medium, 18 complex.
2. **Fixing Bugs / Issues in Code**: [`tasks/task_bug_issues.json`](tasks/task_bug_issues.json) (`mode: fix_bugs` / `repair`)
   - 35 multi-language bug-fixing tasks (`python`, `cpp`, `javascript`): 11 easy, 11 medium, 13 complex.
   - Each task embeds a small buggy program, sample inputs, expected outputs, and verified `exact_code` / `fixed_code`.

## How to Run Automated Testing

### 1. Run with 5 Retries and Repair Mode Enabled
```bash
# Using --mode repair and --retries 5
python3 testing/automated_testing.py --mode repair --retries 5

# Or using the --repair flag
python3 testing/automated_testing.py --repair --retries 5

# Or using the --dataset bugs shortcut
python3 testing/automated_testing.py --dataset bugs --retries 5
```

### 2. Run a Specific Task in Repair Mode with 5 Retries
```bash
python3 testing/automated_testing.py --mode repair --task bug_01 --retries 5
```

### 3. Run Repair Mode with Active Model Training (`--train`)
When `--train` (or `--train-model` / `--correct`) is enabled, an initially failed task submits a trusted `exact_code`/`fixed_code` reference when available. If a retry passes the sample and the task has no reference solution, the passing retry code is submitted instead. Unverified failures without a reference are never submitted. Reports distinguish feedback that was recorded from models where learning is active; some model targets accept feedback without enabling learning:
```bash
python3 testing/automated_testing.py --mode repair --task bug_01 --retries 5 --train
```

### 4. Run Code Generation Dataset (Default)
```bash
python3 testing/automated_testing.py --dataset generate --retries 5
```

### 5. Filter by Language
```bash
python3 testing/automated_testing.py --mode repair --lang python --retries 5
python3 testing/automated_testing.py --dataset generate --lang cpp
```

### 6. Compare Across All Models
```bash
python3 testing/automated_testing.py --mode repair --all-models --retries 5
```

### 7. Rerun a Selected Set of Tasks
Use `--task-ids` with `--lang` to repeat only a specific set of failed tasks in one process. This keeps the per-key request pacing shared across the selected calls:
```bash
python3 testing/automated_testing.py --dataset generate \
  --task-ids task_17,task_20,task_21 --lang python \
  --all-models --retries 5
```

## Reports Output (`testing/reports/`)

All generated evaluation reports are automatically written to `testing/reports/`:
- **JSON summary & per-task diagnostics**: `testing/reports/<dataset>_report.json`
- **Markdown human-readable report**: `testing/reports/<DATASET>_REPORT.md`
- **Multi-model comparison report**: `testing/reports/<dataset>_comparison_report.json` / `<DATASET>_COMPARISON_REPORT.md`

You can also specify a custom output directory using `--output-dir <path>`.

## Dataset Comparison

| Dataset | Mode | File | Description | Tasks |
| :--- | :--- | :--- | :--- | :---: |
| **Generating new code** | `generate` | [`tasks/tasks_code_generation.json`](tasks/tasks_code_generation.json) | Write new standalone program from natural-language spec; 15 easy, 15 medium, 18 complex. | 48 |
| **Fixing Bugs / Issues** | `fix_bugs` | [`tasks/task_bug_issues.json`](tasks/task_bug_issues.json) | Locate and repair bugs in existing programs; 11 easy, 11 medium, 13 complex. | 35 |

### Bug Fixing Tasks Summary (`task_bug_issues.json`)

| Task ID | Language | Title | Focus Area |
| :--- | :---: | :--- | :--- |
| `bug_01` | `python` | Bank Transfer | Balance mutation arithmetic |
| `bug_02` | `cpp` | Binary Search | Search bounds inverted updates |
| `bug_03` | `javascript` | Rate Limiter | Sliding window boundary and admission |
| `bug_04` | `python` | Merge Intervals | Sort comparator and interval overlap logic |
| `bug_05` | `cpp` | Circular Queue | Capacity off-by-one and front peek indexing |
| `bug_06` | `python` | Priority Task Scheduler | Max-heap priority ordering with min-heap |
| `bug_07` | `cpp` | Disjoint Set Component Size | Union-by-size tracking on root merge |
| `bug_08` | `javascript` | User Session Grouping | Independent per-user inactivity window grouping |
| `bug_09` | `python` | Dijkstra Shortest Paths | Min-priority relaxation comparator |
| `bug_10` | `cpp` | Dependency Build Order | Indegree computation and queue initialization |

## Output Matching

By default the harness grades output by **value equivalence**: value-label prefixes (such as `Node 0: `, `dist[3] = ` or `Result -> `) and line breaks are ignored, while every value and its order must still match exactly.

Use `--strict-output` to require an exact one-to-one `stdout` match instead:
```bash
python3 testing/automated_testing.py --strict-output
```

## API Request Pacing

The Jesse API allows **5 requests per second per API key**, so requests must be spaced at least **200 ms apart**. There is no daily cap. Benchmark initial attempts, each auto-repair retry, and feedback submissions all use `JesseClient`, which applies this pacing to chat, streaming, feedback, and other REST requests. Its HTTP transport hook spaces every wire attempt, including SDK retries, and shares pacing across client instances and concurrent benchmark runs that use the same key within one process. Separate Python processes do not share the local pacer; the service still enforces the account-wide limit across processes.

Pacing is covered by `tests/test_client.py` and `test_benchmark_attempts_retries_and_feedback_are_paced_per_key` in `tests/test_automated_testing_retries.py`. These tests use a fake clock and mock HTTP transport, verify a minimum **200 ms between requests** for the same key, and do not make live API calls.
