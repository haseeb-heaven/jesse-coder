# Automated Testing Suite for JesseCoder

This directory contains the automated end-to-end task testing suite for JesseCoder.

## Directory Structure

```text
testing/
├── automated_testing.py   # Multi-model test runner with retries, repair mode & learning
├── tasks/                 # Benchmark task datasets (all JSON files stored here)
│   ├── task_bug_issues.json       # Dataset 2: Fixing bugs/issues in code (10 tasks, mode: fix_bugs)
│   ├── tasks_code_generation.json # Dataset 1: Generating new code (20 tasks, mode: generate)
│   ├── task_code_generation.json  # Alias to tasks_code_generation.json
│   └── tasks_bug_fixing.json      # Alias to task_bug_issues.json
├── reports/               # Output directory where report JSON & Markdown files are written
│   └── .gitkeep
└── README.md              # Testing suite documentation
```

## Datasets

The suite is organized into **2 official datasets** located in `testing/tasks/`:

1. **Generating New Code**: [`tasks/tasks_code_generation.json`](tasks/tasks_code_generation.json) (`mode: generate`)
   - 20 algorithmic coding tasks written from a natural-language specification (14 `python`, 3 `cpp`, 3 `javascript`).
2. **Fixing Bugs / Issues in Code**: [`tasks/task_bug_issues.json`](tasks/task_bug_issues.json) (`mode: fix_bugs` / `repair`)
   - 10 multi-language bug-fixing tasks (`python`, `cpp`, `javascript`).
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
When `--train` (or `--train-model` / `--correct`) is enabled, any failed task with verified `exact_code` in the JSON dataset submits an active correction via Jesse's `POST /feedback` endpoint (`learning_active: True`):
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

## Reports Output (`testing/reports/`)

All generated evaluation reports are automatically written to `testing/reports/`:
- **JSON summary & per-task diagnostics**: `testing/reports/<dataset>_report.json`
- **Markdown human-readable report**: `testing/reports/<DATASET>_REPORT.md`
- **Multi-model comparison report**: `testing/reports/<dataset>_comparison_report.json` / `<DATASET>_COMPARISON_REPORT.md`

You can also specify a custom output directory using `--output-dir <path>`.

## Dataset Comparison

| Dataset | Mode | File | Description | Tasks |
| :--- | :--- | :--- | :--- | :---: |
| **Generating new code** | `generate` | [`tasks/tasks_code_generation.json`](tasks/tasks_code_generation.json) | Write new standalone program from natural-language spec. | 20 |
| **Fixing Bugs / Issues** | `fix_bugs` | [`tasks/task_bug_issues.json`](tasks/task_bug_issues.json) | Locate and repair bugs in existing programs. | 10 |

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
