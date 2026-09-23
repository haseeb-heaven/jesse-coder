# Python-Only Failed-Task Rerun

**Run date:** 2026-09-24

**Scope:** Only Python-language tasks that failed in the previous benchmark

**Targets:** `jesse-prod`, `jesse-pristine`, `jesse`

**Retry policy:** Up to five retries per task

**Feedback:** Enabled, using dataset-verified corrections only

**Request pacing:** At least 200 ms between requests per API key

**Runner/client unit tests:** 24 passed (`tests/test_automated_testing_retries.py` and `tests/test_client.py`)

## Result

The previously failing Python tasks were rerun across all three targets. **No task passed on the new run, and no retry recovered a task.** Each selected task received an initial attempt plus up to five repair attempts. The API continued to return no usable Python program in most cases, so these failures were not execution bugs that could be corrected by the local runner.

| Dataset | Selected failed Python tasks | Result per target | Retry recoveries per target |
| --- | ---: | ---: | ---: |
| Code generation | 12 | 0/12 passed | 0 |
| Bug fixing | 11 | 0/11 passed | 0 |

All three model targets had the same result for every selected task.

## What failed

### Code generation

The rerun selected `task_17`, `task_20`, `task_21`, `task_24`, `task_25`, `task_27`, `task_30`, `task_31`, `task_34`, `task_36`, `task_39`, and `task_44`. Across each target, all 12 tasks failed because the response contained no extractable code block. Five retries did not change those responses.

The code-generation dataset does not contain trusted reference implementations. Since none of the retries produced a sample-passing program, no feedback correction was submitted; training on unverified code would risk teaching an incorrect answer.

### Bug fixing

The rerun selected `bug_01`, `bug_04`, `bug_06`, `bug_11`, `bug_14`, `bug_17`, `bug_20`, `bug_22`, `bug_25`, `bug_28`, and `bug_31`. Per target, **8/11** failed with no code block, **1/11** returned JavaScript instead of Python, and **2/11** returned code with output mismatches. No task was recovered by retries.

All 11 failed bug-fixing tasks had verified corrections in the dataset, and feedback was recorded for all 11 on each target. Jesse-prod and Jesse reported learning active for all 11; Jesse-pristine reported learning inactive for all 11. Recording feedback therefore did not mean that every target was actively learning.

## Evidence files

These machine-readable reports contain per-task responses, errors, retry counts, feedback status, and model comparisons:

- Code generation, primary report: [`tasks_code_generation_report.json`](code-generation/tasks_code_generation_report.json)
- Code generation, model comparison: [`tasks_code_generation_comparison_report.json`](code-generation/tasks_code_generation_comparison_report.json)
- Bug fixing, primary report: [`task_bug_issues_report.json`](bug-fixing/task_bug_issues_report.json)
- Bug fixing, model comparison: [`task_bug_issues_comparison_report.json`](bug-fixing/task_bug_issues_comparison_report.json)
- Runner/client unit test output: [`python-rerun-unit-tests.junit.xml`](python-rerun-unit-tests.junit.xml)

## Conclusion

Restricting the rerun to failed Python tasks did not improve the results. The most persistent issue remained failure to return extractable Python code, including on simple bug-fixing tasks with known corrections. The next useful diagnostic is to inspect the service's task routing/response behavior for these exact IDs; adding more retries alone did not help in this run.
