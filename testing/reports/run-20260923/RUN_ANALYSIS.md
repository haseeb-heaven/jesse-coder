# Benchmark Execution, Findings, and Evidence

**Run window:** 2026-09-23 to 2026-09-24

**Datasets:** 45 code-generation tasks and 33 bug-fixing tasks

**Models:** `jesse-prod`, `jesse-pristine`, and `jesse`

**Evaluation:** tolerant output matching; up to five repair retries in the retry/training runs.

This report records what was run, where the source data and raw reports live, what passed and failed, and what can—and cannot—be inferred from those results. API credentials and response authorization headers are intentionally omitted.

## Executive findings

The dominant observed failure was not a wrong algorithm: the answer often never became a runnable program. In the five-retry code-generation run, 25 of 29 failed tasks ended without extractable code and four returned code in the wrong language. In bug fixing, 23 of 31 failures had no extractable code; the remaining failures included output mismatches, wrong-language responses, and one compilation failure.

Five retries recovered **zero** additional tasks. All three targets had the same pass/fail task IDs in both datasets. This is consistent with a response-format, task-routing, or retrieval/gating problem occurring before code execution, but it does not prove which internal component caused it. Some responses were refusals and some were unrelated text; retries repeated those response types.

There was a large language gap on code generation: Python passed 13/25, C++ 2/10, and JavaScript 1/10. Difficulty mattered, but was not the whole story: easy and medium tasks also failed before execution, while some complex tasks passed.

Feedback submission was not equivalent to learning being active. For failed bug-fixing tasks, `jesse-prod` and `jesse` each reported 31 recorded corrections and 31 learning-active responses. `jesse-pristine` recorded 30 corrections but reported learning inactive for all of them; one further request disconnected.

## Datasets and source files

| Benchmark | Source dataset | Size | Per-difficulty split |
| --- | --- | ---: | ---: |
| Code generation | [`testing/tasks/tasks_code_generation.json`](../../tasks/tasks_code_generation.json) | 45 | 15 easy, 15 medium, 15 complex |
| Bug fixing | [`testing/tasks/task_bug_issues.json`](../../tasks/task_bug_issues.json) | 33 | 11 easy, 11 medium, 11 complex |

The bug-fixing dataset includes the buggy program, sample input and expected output, and verified correction code. The code-generation dataset does not include trusted reference implementations, so a failed answer was only eligible for feedback if a retry produced a program that passed the executable sample.

## How the runs were performed

All model evaluations used the benchmark runner `testing/automated_testing.py`. The recorded invocations were:

```bash
# Code-generation baseline: three targets, retries disabled
python testing/automated_testing.py \
  --dataset generate --all-models --no-retries \
  --output-dir testing/reports/run-20260923

# Code generation: up to five retries, feedback enabled
python testing/automated_testing.py \
  --dataset generate --all-models --retries 5 --train \
  --output-dir testing/reports/run-20260923-repair-train

# Bug fixing: up to five retries, feedback enabled
python testing/automated_testing.py \
  --dataset bugs --all-models --retries 5 --train \
  --output-dir testing/reports/run-20260923-repair-train

# Benchmark-focused local test suite; excludes an unrelated live-chat test
pytest -q \
  tests/test_automated_testing_retries.py \
  tests/test_output_matching.py \
  tests/test_bug_fixing_tasks.py \
  tests/test_web_server.py \
  tests/test_client.py \
  -k 'not chat_stream_endpoint' \
  --junitxml=testing/reports/run-20260923/benchmark-focused-tests.junit.xml
```

The local tests validate runner options and retry/training behavior, output matching, dataset/reference invariants, bug-program execution, benchmark endpoints, and client request pacing. The frontend bundle was also built successfully. The one deselected test calls the live chat endpoint and is outside the benchmark-focused suite.

### Rate-limit handling

The API limit supplied for these runs is **5 requests per second: at least 200 ms between requests for a given API key; no daily cap**. The client now paces outbound requests per key across JesseClient instances in the same process. Pacing is installed on both HTTP transports, so chat, streaming, feedback, other REST calls, and OpenAI SDK wire retries pass through it. The key registry stores a one-way fingerprint rather than the credential. No daily request counter is imposed by the client.

Automated checks verify six same-key request slots are spaced by 200 ms, different keys do not consume each other's slots, and chat plus feedback calls made through separate clients share the same pacing. The check uses a mock HTTP transport and does not send requests to the live service.

**Historical-run limitation:** the live benchmark reports below were generated before this explicit client-side pacer was added. Requests were issued sequentially, but the reports do not contain per-request timestamps, so they cannot prove every historical request was at least 200 ms apart. The new pacing implementation is covered by local tests; rerun the live benchmark to establish a rate-limit-compliant baseline under the updated client. The prior scores should be read as the recorded historical results, not as proof of request timing compliance.

## Results

### Overall scores

| Dataset/run | Target | First-attempt passes | Final passes | Retry recoveries | Feedback recorded | Learning active |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Code generation, baseline (45) | each target | 16 | 16 | 0 | — | — |
| Code generation, five retries (45) | each target | 16 | 16 | 0 | 0 | 0 |
| Bug fixing, five retries (33) | `jesse-prod` | 2 | 2 | 0 | 31 | 31 |
| Bug fixing, five retries (33) | `jesse-pristine` | 2 | 2 | 0 | 30 | 0 |
| Bug fixing, five retries (33) | `jesse` | 2 | 2 | 0 | 31 | 31 |

All three targets had identical pass/fail task profiles within each dataset. Five retries did not recover any additional task.

### By difficulty

| Dataset | Easy | Medium | Complex |
| --- | ---: | ---: | ---: |
| Code generation | 6/15 (40.0%) | 7/15 (46.7%) | 3/15 (20.0%) |
| Bug fixing | 0/11 (0%) | 2/11 (18.2%) | 0/11 (0%) |

### By language

| Dataset | Python | C++ | JavaScript |
| --- | ---: | ---: | ---: |
| Code generation | 13/25 (52.0%) | 2/10 (20.0%) | 1/10 (10.0%) |
| Bug fixing | 1/11 (9.1%) | 1/11 (9.1%) | 0/11 (0%) |

Passing code-generation IDs were `task_01`–`task_14`, `task_18`, and `task_41`. Passing bug-fixing IDs were `bug_07` and `bug_09`. These IDs were the same across all three model targets.

### Failure categories

| Run | No extractable code | Wrong language | Output mismatch | Compile failure |
| --- | ---: | ---: | ---: | ---: |
| Code generation baseline: 29 failures | 26 | 3 | 0 | 0 |
| Code generation, five retries: 29 failures | 25 | 4 | 0 | 0 |
| Bug fixing, five retries: 31 failures | 23 | 3 | 4 | 1 |

Some no-code responses explicitly declined to provide unverified code. Other responses were unrelated (including hotel/restaurant or OAuth content). In bug fixing, the three wrong-language responses were returned as code blocks for another language. These observations support the “failure before execution” pattern; they do not identify an internal service defect with certainty.

## Feedback and safe training behavior

Every failed bug-fixing task had a dataset-verified correction, so feedback was submitted for those tasks when the API request succeeded. The `jesse-pristine` run had one feedback disconnect (`bug_03`), resulting in 30 recorded corrections out of 31 failures. Its responses all indicated learning inactive. The other two targets reported learning active for all 31 recorded corrections.

No code-generation failure was sent as training in these runs: that dataset had no trusted references and no retry produced a sample-passing correction. Skipping feedback in that case avoids teaching from a wrong or unverified answer. Add validated reference programs if future code-generation runs should be able to train on failed tasks safely.

## Evidence and report files

Raw per-task responses, diagnostics, retry counts, and feedback payload outcomes are in the JSON reports. The Markdown reports give the task-by-task summary. JUnit XML records the local test suite result.

| Evidence | Location |
| --- | --- |
| Local tests | [`benchmark-focused-tests.junit.xml`](benchmark-focused-tests.junit.xml) |
| Run summary and interpretation | This file: `testing/reports/run-20260923/RUN_ANALYSIS.md` |
| Code-generation baseline, primary | [`tasks_code_generation_report.json`](tasks_code_generation_report.json), [`TASKS_CODE_GENERATION_REPORT.md`](TASKS_CODE_GENERATION_REPORT.md) |
| Code-generation baseline, model comparison | [`tasks_code_generation_comparison_report.json`](tasks_code_generation_comparison_report.json), [`TASKS_CODE_GENERATION_COMPARISON_REPORT.md`](TASKS_CODE_GENERATION_COMPARISON_REPORT.md) |
| Code generation, five retries and feedback | [`tasks_code_generation_report.json`](../run-20260923-repair-train/tasks_code_generation_report.json), [`TASKS_CODE_GENERATION_REPORT.md`](../run-20260923-repair-train/TASKS_CODE_GENERATION_REPORT.md) |
| Code generation, five-retry model comparison | [`tasks_code_generation_comparison_report.json`](../run-20260923-repair-train/tasks_code_generation_comparison_report.json), [`TASKS_CODE_GENERATION_COMPARISON_REPORT.md`](../run-20260923-repair-train/TASKS_CODE_GENERATION_COMPARISON_REPORT.md) |
| Bug fixing, five retries and feedback | [`task_bug_issues_report.json`](../run-20260923-repair-train/task_bug_issues_report.json), [`TASK_BUG_ISSUES_REPORT.md`](../run-20260923-repair-train/TASK_BUG_ISSUES_REPORT.md) |
| Bug fixing, model comparison | [`task_bug_issues_comparison_report.json`](../run-20260923-repair-train/task_bug_issues_comparison_report.json), [`TASK_BUG_ISSUES_COMPARISON_REPORT.md`](../run-20260923-repair-train/TASK_BUG_ISSUES_COMPARISON_REPORT.md) |

The test report records **150 passed, 1 deselected** after adding the client-pacing checks. The deselected test is the unrelated live-chat endpoint test described above.

## Follow-up: Python-only failed-task rerun

On 2026-09-24, the Python tasks that had failed in the original run were rerun across all three model targets with up to five retries and per-key request pacing. No task passed or recovered. The code-generation subset failed mainly because no code block was returned; bug-fixing failures also included wrong-language output and output mismatches. Verified corrections were fed back for the failed bug-fixing tasks. See the [Python-only rerun report](../run-20260924-python-recheck/RERUN_ANALYSIS.md) and its linked task-level JSON evidence for details.
