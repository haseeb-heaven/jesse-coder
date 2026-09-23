"""
Unit tests for automated testing retry mechanism in testing/automated_testing.py.
"""

from unittest.mock import MagicMock, patch
import pytest

from source.executor import CodeExecutor, ExecutionResult
from testing.automated_testing import (
    build_task_retry_prompt,
    evaluate_model_on_tasks,
)


def test_build_task_retry_prompt():
    task = {
        "id": "task_99",
        "title": "Prime Checker",
        "language": "python",
        "task": "Check if integer n is prime",
        "input": "7",
        "expected_output": "True",
    }
    prompt = build_task_retry_prompt(
        task=task,
        previous_code="print(False)",
        previous_error="Output mismatch.\nExpected:\nTrue\nGot:\nFalse",
        actual_output="False",
        attempt=1,
        max_retries=3,
    )

    assert "AUTOMATED RETRY 1 OF 3" in prompt
    assert "Prime Checker" in prompt
    assert "Expected Output (stdout):\nTrue" in prompt
    assert "Actual Output Produced:\nFalse" in prompt
    assert "print(False)" in prompt
    assert "Output ONLY the complete runnable corrected program" in prompt


def test_evaluate_model_on_tasks_recovers_on_retry():
    task = {
        "id": "test_t1",
        "title": "Add Two",
        "language": "python",
        "task": "Print sum of two numbers",
        "input": "2 3",
        "expected_output": "5",
    }
    tasks = [task]

    # Mock bot to return wrong answer first, then right answer on retry
    mock_bot = MagicMock()
    mock_bot.ask.side_effect = [
        "```python\nprint(0)\n```",  # first try -> fails
        "```python\nprint(5)\n```",  # retry 1 -> succeeds
    ]

    mock_executor = MagicMock(spec=CodeExecutor)
    mock_executor.execute_code.side_effect = [
        ExecutionResult(stdout="0\n", stderr="", output="0\n", exit_code=0, duration_ms=5.0),
        ExecutionResult(stdout="5\n", stderr="", output="5\n", exit_code=0, duration_ms=6.0),
    ]

    with patch("testing.automated_testing.JesseCodingBot", return_value=mock_bot):
        report = evaluate_model_on_tasks(
            tasks=tasks,
            model_name="jesse-prod",
            executor=mock_executor,
            strict_output=False,
            retries=3,
        )

    assert report["passed"] == 1
    assert report["passed_initial"] == 0
    assert report["passed_on_retry"] == 1
    assert report["retries_configured"] == 3
    task_res = report["tasks"][0]
    assert task_res["passed"] is True
    assert task_res["passed_on_retry"] is True
    assert task_res["retries_used"] == 1
    assert mock_bot.ask.call_count == 2


def test_training_uses_sample_verified_retry_code_after_initial_failure():
    task = {
        "id": "task_recovery",
        "title": "Add Two",
        "language": "python",
        "task": "Print the sum of two numbers",
        "input": "2 3",
        "expected_output": "5\n",
    }
    mock_bot = MagicMock()
    mock_bot.ask.side_effect = [
        "```python\nprint(0)\n```",
        "```python\nprint(5)\n```",
    ]
    mock_bot.submit_correction.return_value = {
        "ok": True, "recorded": True, "learning_active": True
    }
    mock_executor = MagicMock(spec=CodeExecutor)
    mock_executor.execute_code.side_effect = [
        ExecutionResult(stdout="0\n", stderr="", output="0\n", exit_code=0, duration_ms=1),
        ExecutionResult(stdout="5\n", stderr="", output="5\n", exit_code=0, duration_ms=1),
    ]

    with patch("testing.automated_testing.JesseCodingBot", return_value=mock_bot):
        report = evaluate_model_on_tasks(
            tasks=[task],
            model_name="jesse-prod",
            executor=mock_executor,
            retries=5,
            train_model=True,
        )

    assert report["passed"] == 1
    assert report["passed_initial"] == 0
    assert report["trained_count"] == 1
    result = report["tasks"][0]
    assert result["training_source"] == "sample_verified_retry"
    assert result["trained"] is True
    assert result["feedback_recorded"] is True
    assert "print(5)" in mock_bot.submit_correction.call_args.kwargs["correction"]


def test_feedback_recorded_is_not_counted_as_active_training():
    task = {
        "id": "bug_feedback_only",
        "title": "One",
        "language": "python",
        "task": "Print one",
        "input": "",
        "expected_output": "1\n",
        "exact_code": "print(1)",
    }
    mock_bot = MagicMock()
    mock_bot.ask.return_value = "```python\nprint(0)\n```"
    mock_bot.submit_correction.return_value = {
        "ok": True, "recorded": True, "learning_active": False
    }
    mock_executor = MagicMock(spec=CodeExecutor)
    mock_executor.execute_code.return_value = ExecutionResult(
        stdout="0\n", stderr="", output="0\n", exit_code=0, duration_ms=1
    )

    with patch("testing.automated_testing.JesseCodingBot", return_value=mock_bot):
        report = evaluate_model_on_tasks(
            tasks=[task], model_name="jesse-pristine", executor=mock_executor,
            retries=0, train_model=True,
        )

    result = report["tasks"][0]
    assert result["feedback_submitted"] is True
    assert result["feedback_recorded"] is True
    assert result["trained"] is False
    assert report["feedback_recorded_count"] == 1
    assert report["trained_count"] == 0


def test_resolve_selected_models_defaults_to_single_model():
    from testing.automated_testing import build_argument_parser, resolve_selected_models

    parser = build_argument_parser()

    # When no model flags are provided, defaults to single model ('jesse-prod')
    args = parser.parse_args(["--tasks-file", "testing/tasks/task_bug_issues.json", "--task", "bug_01", "--retries", "4"])
    models = resolve_selected_models(args)
    assert models == ["jesse-prod"]

    # When --all-models is provided, returns all 3 models
    args_all = parser.parse_args(["--all-models"])
    models_all = resolve_selected_models(args_all)
    assert models_all == ["jesse-prod", "jesse-pristine", "jesse"]

    # When --model is provided, returns that specific model
    args_one = parser.parse_args(["--model", "jesse"])
    models_one = resolve_selected_models(args_one)
    assert models_one == ["jesse"]

    # When --models is provided, returns the list
    args_multi = parser.parse_args(["--models", "jesse-prod,jesse"])
    models_multi = resolve_selected_models(args_multi)
    assert models_multi == ["jesse-prod", "jesse"]


def test_cli_accepts_multiple_specific_task_ids():
    from testing.automated_testing import build_argument_parser

    args = build_argument_parser().parse_args([
        "--dataset", "generate", "--task-ids", "task_17,task_20,task_21",
        "--lang", "python",
    ])

    assert args.task_ids == "task_17,task_20,task_21"
    assert args.lang == "python"


def test_build_task_prompt_without_stdin():
    from testing.automated_testing import build_task_prompt

    task = {
        "id": "bug_01",
        "language": "python",
        "mode": "fix_bugs",
        "title": "Bank Transfer",
        "task": "Fix transfer bug",
        "input": "",
        "expected_output": "OK 800 700\nREJECTED 800 700\n",
    }
    prompt = build_task_prompt(task)

    assert "Bank Transfer" in prompt
    assert "Expected Output:\nOK 800 700" in prompt
    assert "sys.stdin" not in prompt
    assert "Sample Input:" not in prompt


def test_cli_train_argument():
    from testing.automated_testing import build_argument_parser

    parser = build_argument_parser()
    # Default is False
    args_default = parser.parse_args([])
    assert args_default.train_model is False

    # --train
    args_train = parser.parse_args(["--train"])
    assert args_train.train_model is True

    # --train-model
    args_train_model = parser.parse_args(["--train-model"])
    assert args_train_model.train_model is True

    # --correct
    args_correct = parser.parse_args(["--correct"])
    assert args_correct.train_model is True


def test_evaluate_model_on_tasks_trains_on_failure_with_exact_code():
    task = {
        "id": "bug_01",
        "title": "Bank Transfer",
        "language": "python",
        "task": "Fix transfer bug",
        "input": "",
        "expected_output": "OK 800 700\nREJECTED 800 700\n",
        "exact_code": "class Account:\n    pass\n",
    }

    mock_bot = MagicMock()
    # Model returns wrong output
    mock_bot.ask.return_value = "```python\nprint('WRONG')\n```"
    mock_bot.submit_correction.return_value = {"ok": True, "learning_active": True}

    mock_executor = MagicMock(spec=CodeExecutor)
    mock_executor.execute_code.return_value = ExecutionResult(
        stdout="WRONG\n", stderr="", output="WRONG\n", exit_code=0, duration_ms=5.0
    )

    with patch("testing.automated_testing.JesseCodingBot", return_value=mock_bot):
        report = evaluate_model_on_tasks(
            tasks=[task],
            model_name="jesse-prod",
            executor=mock_executor,
            strict_output=False,
            retries=0,
            train_model=True,
        )

    assert report["passed"] == 0
    assert report["trained_count"] == 1
    assert report["train_model_enabled"] is True
    task_res = report["tasks"][0]
    assert task_res["passed"] is False
    assert task_res["trained"] is True
    assert mock_bot.submit_correction.call_count == 1
    corr_arg = mock_bot.submit_correction.call_args[1]["correction"]
    assert "class Account:" in corr_arg


def test_run_automated_testing_keeps_retry_toggle_separate_from_dataset_mode(tmp_path):
    from testing.automated_testing import run_automated_testing

    model_result = {
        "model": "jesse-prod",
        "total": 1,
        "passed": 0,
        "failed": 1,
        "pass_rate_pct": 0.0,
        "tasks": [],
        "output_matching": "tolerant",
    }
    with patch(
        "testing.automated_testing.evaluate_model_on_tasks",
        return_value=model_result,
    ) as evaluate:
        result = run_automated_testing(
            dataset="tasks_code_generation.json",
            models=["jesse-prod"],
            retries=5,
            auto_repair=False,
            output_dir=tmp_path,
        )

    assert result["dataset"] == "tasks_code_generation.json"
    assert evaluate.call_args.kwargs["retries"] == 0
    assert evaluate.call_args.kwargs["train_model"] is False


def test_benchmark_datasets_have_expected_difficulty_levels():
    import json
    from collections import Counter
    from pathlib import Path

    tasks_dir = Path(__file__).resolve().parents[1] / "testing" / "tasks"
    expected_counts = {
        "tasks_code_generation.json": {"easy": 15, "medium": 15, "complex": 18},
        "task_bug_issues.json": {"easy": 11, "medium": 11, "complex": 13},
    }
    for filename, counts in expected_counts.items():
        tasks = json.loads((tasks_dir / filename).read_text(encoding="utf-8"))
        assert len(tasks) == sum(counts.values())
        assert len({task["id"] for task in tasks}) == len(tasks)
        assert Counter(task["difficulty"] for task in tasks) == counts
        for task in tasks:
            assert task["language"] in {"python", "cpp", "javascript"}
            assert task["expected_output"]
            if task["mode"] == "fix_bugs":
                assert task.get("buggy_code")
                assert task.get("exact_code")
def test_evaluate_model_on_tasks_skips_train_when_passed():
    task = {
        "id": "bug_01",
        "title": "Bank Transfer",
        "language": "python",
        "task": "Fix transfer bug",
        "input": "",
        "expected_output": "OK 800 700\nREJECTED 800 700\n",
        "exact_code": "class Account:\n    pass\n",
    }

    mock_bot = MagicMock()
    mock_bot.ask.return_value = "```python\nprint('OK 800 700\\nREJECTED 800 700')\n```"

    mock_executor = MagicMock(spec=CodeExecutor)
    mock_executor.execute_code.return_value = ExecutionResult(
        stdout="OK 800 700\nREJECTED 800 700\n", stderr="", output="OK 800 700\nREJECTED 800 700\n", exit_code=0, duration_ms=5.0
    )

    with patch("testing.automated_testing.JesseCodingBot", return_value=mock_bot):
        report = evaluate_model_on_tasks(
            tasks=[task],
            model_name="jesse-prod",
            executor=mock_executor,
            strict_output=False,
            retries=0,
            train_model=True,
        )

    assert report["passed"] == 1
    assert report["trained_count"] == 0
    assert mock_bot.submit_correction.call_count == 0


def test_bot_submit_correction_calls_client():
    from source.bot import JesseCodingBot

    mock_client = MagicMock()
    mock_client.submit_feedback.return_value = {"ok": True}
    mock_client.last_message_id = "msg_123"

    bot = JesseCodingBot(client=mock_client)
    res = bot.submit_correction("```python\ncode\n```")
    assert res == {"ok": True}
    mock_client.submit_feedback.assert_called_once_with(
        message_id="msg_123",
        rating="thumbs_down",
        correction="```python\ncode\n```",
        model=bot.config.model,
    )


def test_resolve_tasks_path_shortcuts():
    from testing.automated_testing import (
        DATASET_BUG_ISSUES,
        DATASET_CODE_GENERATION,
        resolve_tasks_path,
    )

    # Defaults to code generation
    assert resolve_tasks_path() == DATASET_CODE_GENERATION

    # Dataset shortcut: generate
    assert resolve_tasks_path(dataset="generate") == DATASET_CODE_GENERATION
    assert resolve_tasks_path(tasks_file="generate") == DATASET_CODE_GENERATION

    # Dataset shortcut: bugs / bug_issues / fix_bugs
    assert resolve_tasks_path(dataset="bugs") == DATASET_BUG_ISSUES
    assert resolve_tasks_path(dataset="bug_issues") == DATASET_BUG_ISSUES
    assert resolve_tasks_path(tasks_file="task_bug_issues.json") == DATASET_BUG_ISSUES
    assert resolve_tasks_path(tasks_file="task_bug_issues") == DATASET_BUG_ISSUES

    # Repair mode flags
    assert resolve_tasks_path(repair=True) == DATASET_BUG_ISSUES
    assert resolve_tasks_path(mode="repair") == DATASET_BUG_ISSUES
    assert resolve_tasks_path(mode="fix_bugs") == DATASET_BUG_ISSUES


def test_build_task_prompt_with_buggy_code():
    from testing.automated_testing import build_task_prompt

    task = {
        "id": "bug_01",
        "title": "Sample Buggy Task",
        "language": "python",
        "mode": "repair",
        "task": "Fix the logic bug in this program.",
        "buggy_code": "def solve():\n    return False\n",
        "buggy_output": "False",
        "input": "",
        "expected_output": "True\n",
    }
    prompt = build_task_prompt(task)
    assert "Find and fix every bug" in prompt
    assert "Buggy Program:" in prompt
    assert "def solve():" in prompt
    assert "Current (Buggy) Output:" in prompt
    assert "False" in prompt
    assert "Output ONLY the complete runnable program" in prompt
