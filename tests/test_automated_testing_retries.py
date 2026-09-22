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


def test_resolve_selected_models_defaults_to_single_model():
    from testing.automated_testing import build_argument_parser, resolve_selected_models

    parser = build_argument_parser()

    # When no model flags are provided, defaults to single model ('jesse-prod')
    args = parser.parse_args(["--tasks-file", "testing/tasks_bug_fixing.json", "--task", "bug_01", "--retries", "4"])
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
