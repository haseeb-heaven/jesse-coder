"""Tests for the bug-fixing (debug mode) benchmark tasks.

Every task in testing/tasks_bugs.json ships a small buggy program. These tests
pin the invariant that makes the set meaningful: the buggy program must NOT
already produce the task's expected output, otherwise returning the original
code unchanged would score as a pass.
"""

import json
from pathlib import Path

import pytest

from code_extractor import extract_code_blocks
from executor import CodeExecutor
from testing.automated_testing import outputs_equivalent

TASKS_FILE = Path(__file__).resolve().parent.parent / "testing" / "tasks_bugs.json"
TASKS = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
EXECUTOR = CodeExecutor()


def test_bug_task_set_metadata():
    assert len(TASKS) >= 5
    ids = [task["id"] for task in TASKS]
    assert len(ids) == len(set(ids)), "task ids must be unique"
    for task in TASKS:
        assert task["mode"] == "debug"
        assert task["language"] == "python"
        assert task["difficulty"] in ("simple", "medium")
        assert task["expected_output"].strip(), f"{task['id']}: missing expected output"
        assert task["input"].strip(), f"{task['id']}: missing stdin input"
        assert "```python" in task["task"], f"{task['id']}: buggy program not embedded"


@pytest.mark.parametrize("task", TASKS, ids=[task["id"] for task in TASKS])
def test_buggy_program_does_not_match_expected_output(task):
    blocks = extract_code_blocks(task["task"])
    assert len(blocks) == 1, f"{task['id']}: expected exactly one fenced buggy program"

    result = EXECUTOR.execute_code(
        code=blocks[0].code,
        language="python",
        stdin_data=task["input"],
        timeout=10.0,
    )
    already_correct = result.is_success and outputs_equivalent(
        task["expected_output"], result.stdout
    )
    assert not already_correct, (
        f"{task['id']}: the buggy program already produces the expected output "
        f"({result.stdout!r}) - the task is not actually broken"
    )


@pytest.mark.parametrize("task", TASKS, ids=[task["id"] for task in TASKS])
def test_buggy_program_is_small(task):
    """The tasks must stay small: one or two helper methods plus main()."""
    blocks = extract_code_blocks(task["task"])
    definitions = [line for line in blocks[0].code.splitlines() if line.startswith("def ")]
    assert 1 <= len(definitions) <= 3, f"{task['id']}: {len(definitions)} functions defined"
