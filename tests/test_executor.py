"""Tests for CodeExecutor and code_extractor ported from open-agent."""

import pytest
from jesse_coder.code_extractor import (
    extract_code_blocks,
    get_primary_code_block,
    ExtractedCodeBlock,
)
from jesse_coder.executor import (
    CodeExecutor,
    ExecutionResult,
    append_and_truncate,
    strip_ansi,
)
from jesse_coder import JesseCodingBot, JesseConfig


def test_code_block_extraction():
    sample_text = (
        "Here is the solution in Python:\n"
        "```python\n"
        "def add(a, b):\n"
        "    return a + b\n"
        "print(add(2, 3))\n"
        "```\n"
        "And here is how to run it in bash:\n"
        "```bash\n"
        "python3 script.py\n"
        "```"
    )
    blocks = extract_code_blocks(sample_text)
    assert len(blocks) == 2
    assert blocks[0].language == "python"
    assert "print(add(2, 3))" in blocks[0].code
    assert blocks[1].language == "bash"
    assert "python3 script.py" in blocks[1].code


def test_primary_code_block_selection():
    text = (
        "Explanation...\n"
        "```bash\n"
        "echo setup\n"
        "```\n"
        "```python\n"
        "print('main code')\n"
        "```"
    )
    # Defaults to preferring Python
    primary = get_primary_code_block(text)
    assert primary is not None
    assert primary.language == "python"
    assert "main code" in primary.code

    # Can request specific language
    bash_primary = get_primary_code_block(text, preferred_lang="bash")
    assert bash_primary is not None
    assert bash_primary.language == "bash"


def test_raw_code_fallback():
    raw_python = "import math\nprint(math.sqrt(16))"
    block = get_primary_code_block(raw_python)
    assert block is not None
    assert block.language == "python"
    assert block.code == raw_python


def test_strip_ansi():
    colored = "\x1b[31mError:\x1b[0m Failed with \x1b[1mcode 1\x1b[0m"
    clean = strip_ansi(colored)
    assert clean == "Error: Failed with code 1"


def test_append_and_truncate():
    buf, truncated = append_and_truncate("hello ", "world", max_size=20)
    assert buf == "hello world"
    assert not truncated

    buf2, truncated2 = append_and_truncate("12345", "67890", max_size=6)
    assert buf2 == "567890"
    assert truncated2


def test_python_code_execution():
    executor = CodeExecutor()
    code = "import sys\nprint('Output test:', 10 * 5)"
    res = executor.execute_code(code, language="python")

    assert res.is_success
    assert res.exit_code == 0
    assert "Output test: 50" in res.stdout
    assert res.timed_out is False
    assert res.duration_ms > 0


def test_python_runtime_error():
    executor = CodeExecutor()
    code = "print('before')\nx = 1 / 0\nprint('after')"
    res = executor.execute_code(code, language="python")

    assert not res.is_success
    assert res.exit_code != 0
    assert "ZeroDivisionError" in res.stderr
    assert "before" in res.stdout


def test_shell_execution():
    executor = CodeExecutor()
    res = executor.execute_shell("echo 'shell execution works'")
    assert res.is_success
    assert "shell execution works" in res.stdout


def test_timeout_process_kill():
    executor = CodeExecutor()
    # Code that sleeps longer than timeout
    code = "import time\ntime.sleep(5)\nprint('Done')"
    res = executor.execute_code(code, language="python", timeout=0.5)

    assert res.timed_out is True
    assert not res.is_success
    assert "timed out" in (res.error or "").lower()


def test_bot_execute_response_integration():
    bot = JesseCodingBot()
    fake_response = (
        "Here is the Python solution:\n"
        "```python\n"
        "result = sum([1, 2, 3, 4, 5])\n"
        "print(f'Sum: {result}')\n"
        "```\n"
    )
    res = bot.execute_response(response_text=fake_response)
    assert res is not None
    assert res.is_success
    assert "Sum: 15" in res.stdout


def test_action_json_extraction_and_execution():
    bot = JesseCodingBot()
    action_text = '<actions> [ { "name": "Bash", "args": { "command": "echo \\"Action executed\\"" } } ]'
    res = bot.execute_response(response_text=action_text)
    assert res is not None
    assert res.is_success
    assert res.language in ("bash", "shell")
    assert "Action executed" in res.stdout
