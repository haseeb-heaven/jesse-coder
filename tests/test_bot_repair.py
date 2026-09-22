"""
Tests for self-healing auto-repair prompt construction and retry logic.
"""

from unittest.mock import MagicMock, patch
import pytest

from source.bot import JesseCodingBot, build_repair_prompt
from source.config import JesseConfig
from source.executor import ExecutionResult


def test_build_repair_prompt_structure():
    exec_res = ExecutionResult(
        stdout="Partial output before crash",
        stderr="ZeroDivisionError: division by zero\n  at line 4",
        output="Partial output before crash\nZeroDivisionError: division by zero",
        exit_code=1,
        duration_ms=12.5,
    )
    prompt = build_repair_prompt(
        original_prompt="Calculate division of a by b",
        failed_code="def div(a, b):\n    return a / b\nprint(div(10, 0))",
        language="python",
        execution_result=exec_res,
        attempt=1,
        max_retries=3,
    )

    assert "SELF-HEALING AUTO-REPAIR - Attempt 1 of 3" in prompt
    assert "Calculate division of a by b" in prompt
    assert "ZeroDivisionError: division by zero" in prompt
    assert "Partial output before crash" in prompt
    assert "Exit Code: 1" in prompt
    assert "def div(a, b):" in prompt


def test_ask_and_repair_success_first_try():
    config = JesseConfig(api_key="mock_key", model="jesse-prod")
    bot = JesseCodingBot(config=config)

    passing_result = ExecutionResult(
        stdout="42\n",
        stderr="",
        output="42\n",
        exit_code=0,
        duration_ms=5.0,
    )

    with patch.object(bot, "ask_and_execute", return_value=("Here is the code:\n```python\nprint(42)\n```", passing_result)) as mock_exec:
        resp, res, attempts = bot.ask_and_repair("Print 42", max_retries=3)
        assert attempts == 1
        assert res is not None
        assert res.is_success is True
        assert mock_exec.call_count == 1


def test_ask_and_repair_retries_until_success():
    config = JesseConfig(api_key="mock_key", model="jesse-prod")
    bot = JesseCodingBot(config=config)

    fail_result = ExecutionResult(
        stdout="",
        stderr="SyntaxError",
        output="SyntaxError",
        exit_code=1,
        duration_ms=5.0,
    )
    pass_result = ExecutionResult(
        stdout="Hello World\n",
        stderr="",
        output="Hello World\n",
        exit_code=0,
        duration_ms=4.0,
    )

    # First call fails, second call succeeds
    with patch.object(
        bot,
        "ask_and_execute",
        side_effect=[
            ("Broken code:\n```python\nprint('Hello World\n```", fail_result),
            ("Fixed code:\n```python\nprint('Hello World')\n```", pass_result),
        ],
    ) as mock_exec:
        resp, res, attempts = bot.ask_and_repair("Print Hello World", max_retries=3)
        assert attempts == 2
        assert res is not None
        assert res.is_success is True
        assert mock_exec.call_count == 2
