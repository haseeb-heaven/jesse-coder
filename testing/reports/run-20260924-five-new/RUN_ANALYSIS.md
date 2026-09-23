# Five New Python Benchmark Tasks — Run Analysis

## Scope and result

On 24 September 2026, the `jesse-prod` model was evaluated on **only five newly added complex Python tasks**: three code-generation tasks (`task_46`–`task_48`) and two bug-fixing tasks (`bug_34`–`bug_35`). Each task received an initial attempt and, after failure, all five configured auto-repair retries. The runner used its default tolerant output comparison and submitted the verified `exact_code` to `/feedback` after each initial failure.

| Category | Tasks | Passed initially | Recovered on retry | Final passed | Final pass rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| New code generation | 3 | 0 | 0 | 0 | 0% |
| New bug fixing | 2 | 0 | 0 | 0 | 0% |
| **Combined** | **5** | **0** | **0** | **0** | **0%** |

The runner reports five correction submissions recorded by `/feedback`, with `learning_active` true for all five. This confirms the API response to the submissions, **not** that a later model run will pass.

## Per-task evidence

| Task | What was requested | Observed result after five retries |
| :--- | :--- | :--- |
| `task_46` | Count prime-sum paths on Pythagorean-sized grids | No runnable Python code returned; no execution |
| `task_47` | Implement a versioned circular ledger with snapshots and rotations | No runnable Python code returned; no execution |
| `task_48` | Find a prime-toll route using exactly one red edge | No runnable Python code returned; no execution |
| `bug_34` | Repair signed prime-sum grid-path counting | No corrected Python code returned; no execution |
| `bug_35` | Repair snapshot isolation after rotation | No corrected Python code returned; no execution |

The exact model replies, expected outputs, retry counts, and diagnostics are preserved in the [generation report](generation/TASKS_CODE_GENERATION_REPORT.md) and [bug-fixing report](repairs/TASK_BUG_ISSUES_REPORT.md). Machine-readable evidence is in the corresponding [generation JSON](generation/tasks_code_generation_report.json) and [bug-fixing JSON](repairs/task_bug_issues_report.json).

## Main issue by task type

**Generating new code:** Jesse did not return a Python program for any of the three specifications. Its final replies said it did not have a solution it could verify and would not guess at Python code. The benchmark therefore failed at **answer generation / required output format**, before any algorithm, runtime, or output could be judged.

**Fixing bugs:** Jesse also did not return a corrected program for either buggy input. In the snapshot task, it recognized command names such as `SNAP`, `ADD`, and `LOAD`, but still declined to provide a verified fix. This is likewise a **failure to produce repair code**, not evidence that a submitted repair had a particular logic bug.

**Shared pattern:** Across the five tasks, the last saved response is a refusal-style explanation rather than a fenced Python program. The runner's diagnostic is `No valid code block extracted from model response.` With zero extracted code and zero execution time, this run cannot measure the model's algorithmic correctness on these tasks. The model's references to "checked components" suggest a verification or component-coverage gate, but the reports alone do not establish the service's internal cause.

## Dataset validity and follow-up

The five cases are in [the generation dataset](../../tasks/tasks_code_generation.json) and [the bug-fixing dataset](../../tasks/task_bug_issues.json). Local reference-code tests execute the generation examples and additional edge cases; the bug-fixing tests check that each buggy program fails its expected output and each reference repair passes. These checks validate the benchmark cases independently of the live model result.

The next useful investigation is to inspect why `jesse-prod` responds with "checked components" rather than code when given these specifications. After that behavior changes, rerun the same five IDs to measure real code-generation and repair accuracy. Do not interpret the current 0% as an algorithmic pass-rate estimate.
