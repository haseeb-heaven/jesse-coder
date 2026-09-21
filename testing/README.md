# Automated Testing Suite for JesseCoder

This directory contains the automated end-to-end task testing suite for JesseCoder.

## Structure

- [`automated_testing.py`](file:///Users/haseeb-mir/Documents/Code/Python/jesse-coder/testing/automated_testing.py): Test harness that prompts the model for each task, extracts executable code, runs it with standard input (`stdin`), and verifies stdout against expected outputs.
- [`tasks.json`](file:///Users/haseeb-mir/Documents/Code/Python/jesse-coder/testing/tasks.json): 10 standard evaluation tasks across Python, C++, and JavaScript.
- [`task_eval_report.json`](file:///Users/haseeb-mir/Documents/Code/Python/jesse-coder/testing/task_eval_report.json): Raw structured evaluation metrics and results in JSON format.
- [`TASK_EVAL_REPORT.md`](file:///Users/haseeb-mir/Documents/Code/Python/jesse-coder/testing/TASK_EVAL_REPORT.md): Full human-readable markdown evaluation report with compilation logs, execution times, and diagnostics.

## Usage

### Run All 10 Tasks (Default model: `jesse-prod`)
```bash
python3 testing/automated_testing.py
```

### Run a Specific Task (e.g. `task_02`)
```bash
python3 testing/automated_testing.py --task task_02
```

### Test Against Alternate Models
```bash
python3 testing/automated_testing.py --model jesse-pristine
```
