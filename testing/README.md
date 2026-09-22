# Automated Testing Suite for JesseCoder

This directory contains the automated end-to-end task testing suite for JesseCoder.

## Structure

- [`automated_testing.py`](automated_testing.py): Test harness that prompts the model for each task, extracts executable code, runs it with standard input (`stdin`), and verifies stdout against expected outputs.
- [`tasks.json`](tasks.json): Evaluation tasks with standard input and expected output definitions.
- [`tasks_complex.json`](tasks_complex.json): Advanced algorithmic benchmark tasks (Job Scheduling, Order Matching, Union-Find, DAG Critical Path, etc.).
- [`task_eval_report.json`](task_eval_report.json): Raw structured evaluation metrics and results in JSON format.
- [`TASK_EVAL_REPORT.md`](TASK_EVAL_REPORT.md): Full human-readable markdown evaluation report with compilation logs, execution times, and diagnostics.
- [`MODEL_COMPARISON_REPORT.md`](MODEL_COMPARISON_REPORT.md): Cross-model comparative evaluation report across all available Jesse models.

## Usage

### Run All Tasks (Default: `jesse-prod`)
```bash
python3 testing/automated_testing.py
```

### Run Only Python Tasks
```bash
python3 testing/automated_testing.py --lang python
```

### Run a Specific Task
```bash
python3 testing/automated_testing.py --task task_02
```

### Compare Across All Models
```bash
python3 testing/automated_testing.py --all-models
```

### Run Custom / Complex Task Set
```bash
python3 testing/automated_testing.py --tasks-file testing/tasks_complex.json
```

### Bug Fixing Task Set (debug mode)
[`tasks_bugs.json`](tasks_bugs.json) contains five bug-fixing tasks. Each one embeds a
small buggy program (one or two helper functions plus `main()`) and asks the model to
find the bugs, return the complete corrected program, and the file records the exact
output the fixed program must produce for the given `stdin`.

```bash
python3 testing/automated_testing.py --tasks-file testing/tasks_bugs.json --model jesse-prod
```

These tasks set `"mode": "debug"`, which switches the harness prompt from
*"implement a program"* to *"find and fix every bug in the following program"* and
forbids echoing the buggy code back, because the extractor takes the first code block
in the response.

| Task | Difficulty | Planted bug | Fixed output |
| :--- | :--- | :--- | :--- |
| `bug_01` | simple | loop bound skips the final value | `55` |
| `bug_02` | simple | floor division instead of true division | `1.33` |
| `bug_03` | medium | missing key default, plus the documented smallest-value tie-break | `2` |
| `bug_04` | medium | mutable default argument leaks state between calls | `1 3 6` / `10 30` |
| `bug_05` | medium | wrong input delimiter and wrong bound update (first vs last occurrence) | `1` |

### Output Matching
By default the harness grades output by **value equivalence**: value-label prefixes
(such as `Node 0: `, `dist[3] = ` or `Result -> `) and line breaks are ignored, while
every value and its order must still match exactly. So `0 3 1 4 7` and
`Node 0: 0 / Node 1: 3 / Node 2: 1 / Node 3: 4 / Node 4: 7` are equivalent.

Use `--strict-output` to require an exact one-to-one `stdout` match instead:

```bash
python3 testing/automated_testing.py --strict-output
```

Every generated report records the active matching mode, and passes accepted on
equivalence are flagged in the summary table and per-task section.
