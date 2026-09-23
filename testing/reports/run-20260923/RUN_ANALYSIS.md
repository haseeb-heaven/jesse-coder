# Benchmark Run Analysis

Run window: 2026-09-23 to 2026-09-24. All benchmark evaluations used tolerant output matching. The retry/training run used up to five retries and enabled feedback training. Training was only submitted with a dataset reference or code that passed the task sample. The model targets were `jesse-prod`, `jesse-pristine`, and `jesse`.

## Local benchmark checks

The benchmark-focused test suite finished with **141 passed, 1 deselected**. The deselected test calls the live chat endpoint and is outside this benchmark-only test set. Coverage included retry and training behavior, strict/tolerant output matching, dataset invariants, execution of buggy and reference programs, and benchmark HTTP endpoints. The frontend bundle also built successfully.

JUnit output: [`benchmark-focused-tests.junit.xml`](benchmark-focused-tests.junit.xml).

## Model results

| Dataset | Target | First-attempt passes | Final passes | Recovered by retry | Feedback recorded | Learning active |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Code generation (45) | each of the 3 targets | 16 | 16 | 0 | 0 | 0 |
| Bug fixing (33) | `jesse-prod` | 2 | 2 | 0 | 31 | 31 |
| Bug fixing (33) | `jesse-pristine` | 2 | 2 | 0 | 30 | 0 |
| Bug fixing (33) | `jesse` | 2 | 2 | 0 | 31 | 31 |

All three targets had identical pass/fail task profiles in both datasets. The code-generation baseline and five-retry run both scored 16/45 per target. The bug-fixing run scored 2/33 per target. Five retries did not recover any additional task.

### Difficulty and language pattern

| Dataset | Easy | Medium | Complex |
| --- | ---: | ---: | ---: |
| Code generation | 6/15 (40.0%) | 7/15 (46.7%) | 3/15 (20.0%) |
| Bug fixing | 0/11 (0%) | 2/11 (18.2%) | 0/11 (0%) |

| Dataset | Python | C++ | JavaScript |
| --- | ---: | ---: | ---: |
| Code generation | 13/25 (52.0%) | 2/10 (20.0%) | 1/10 (10.0%) |
| Bug fixing | 1/11 (9.1%) | 1/11 (9.1%) | 0/11 (0%) |

Passing IDs were `task_01`–`task_14`, `task_18`, and `task_41` for code generation, and `bug_07` and `bug_09` for bug fixing. The same IDs passed on each model target.

## Failure pattern

Most failures happen before execution because the response contains no extractable code. In the baseline, 26 of 29 generation failures had no valid code block; the other three returned Python code where C++ or JavaScript was required. The five-retry run ended with 25 no-code failures and four wrong-language responses. In bug fixing, 23 of 31 failures had no code block, four had output mismatches, three returned the wrong language, and one failed compilation.

Some no-code responses explicitly declined to guess because the system could not verify a solution. Others were unrelated responses, including hotel/restaurant and OAuth content. Retries repeated these response types instead of turning them into code. That points to a response-generation or retrieval/gating problem ahead of code execution, with wrong-language selection as another clear failure mode.

This is an inference from the returned responses and identical target profiles; the reports alone do not reveal the API's internal routing. Complexity contributes to lower code-generation scores, but it does not explain the main failure pattern: easy and medium tasks also often fail before execution, while some complex tasks pass.

## Feedback/training result

All bug-fixing failures had sample-verified reference code. `jesse-prod` and `jesse` recorded 31 corrections each and reported `learning_active=true`. `jesse-pristine` recorded 30 corrections but reported `learning_active=false` for every response; one additional feedback request for `bug_03` disconnected. Therefore, “feedback recorded” must not be counted as “learning active.” The runner now reports these as separate counters for future runs.

The code-generation dataset has no trusted reference implementations. No retry produced a sample-passing correction, so the runner correctly skipped feedback for those failures instead of training on wrong or unverified code. To train code-generation failures safely, add verified reference solutions or improve the generation layer so retries can produce sample-passing programs.

## Reports

- Baseline generation: [`tasks_code_generation_report.json`](tasks_code_generation_report.json), [`tasks_code_generation_comparison_report.json`](tasks_code_generation_comparison_report.json), and Markdown counterparts.
- Five-retry generation: [`tasks_code_generation_report.json`](../run-20260923-repair-train/tasks_code_generation_report.json) and comparison report.
- Five-retry bug fixing: [`task_bug_issues_report.json`](../run-20260923-repair-train/task_bug_issues_report.json) and comparison report.
- Raw task-level responses, diagnostics, retry counts, and feedback responses are in the JSON reports.
