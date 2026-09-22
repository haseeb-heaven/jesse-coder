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
