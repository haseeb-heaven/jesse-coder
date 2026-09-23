"""Tests for the bug-fixing task set (mode: fix_bugs).

Every task in testing/tasks_bug_fixing.json ships a small buggy program. These
tests pin the invariant that makes the set meaningful: the buggy program must NOT
already produce the task's expected output, otherwise returning the original
code unchanged would score as a pass.
"""

import json
from pathlib import Path

import pytest

from code_extractor import extract_code_blocks
from executor import CodeExecutor
from testing.automated_testing import (
    TASK_MODE_FIX_BUGS,
    TASK_MODE_GENERATE,
    outputs_equivalent,
)

TESTING_DIR = Path(__file__).resolve().parent.parent / "testing"
TASKS_FILE = TESTING_DIR / "tasks" / "task_bug_issues.json"
GENERATION_FILE = TESTING_DIR / "tasks" / "tasks_code_generation.json"
TASKS = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
EXECUTOR = CodeExecutor()


def buggy_program(task):
    """Read buggy source from the structured field or legacy task Markdown."""
    if task.get("buggy_code"):
        return task["buggy_code"]
    blocks = extract_code_blocks(task["task"])
    assert len(blocks) == 1, f"{task['id']}: expected one buggy program"
    return blocks[0].code


def test_task_type_files_use_expected_modes():
    """The two task types are distinguished by the 'mode' field."""
    generation = json.loads(GENERATION_FILE.read_text(encoding="utf-8"))
    assert generation, "code generation task set is empty"
    assert {task["mode"] for task in generation} == {TASK_MODE_GENERATE}
    assert {task["mode"] for task in TASKS} == {TASK_MODE_FIX_BUGS}


def test_bug_task_set_metadata():
    assert len(TASKS) >= 5
    ids = [task["id"] for task in TASKS]
    assert len(ids) == len(set(ids)), "task ids must be unique"
    for task in TASKS:
        assert task["mode"] == TASK_MODE_FIX_BUGS
        assert task["language"] in ("python", "cpp", "javascript")
        assert task["difficulty"] in ("simple", "easy", "medium", "complex", "very complex", "hard")
        assert task["expected_output"].strip(), f"{task['id']}: missing expected output"
        assert task.get("buggy_code") or f"```{task['language']}" in task["task"], (
            f"{task['id']}: buggy program is missing"
        )


@pytest.mark.parametrize("task", TASKS, ids=[task["id"] for task in TASKS])
def test_buggy_program_does_not_match_expected_output(task):
    result = EXECUTOR.execute_code(
        code=buggy_program(task),
        language=task["language"],
        stdin_data=task.get("input", ""),
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
    """The tasks must stay small: concise functions/classes."""
    assert len(buggy_program(task).splitlines()) <= 100, f"{task['id']}: program too large"


@pytest.mark.parametrize("task", TASKS, ids=[task["id"] for task in TASKS])
def test_exact_code_produces_expected_output(task):
    """Verifies that exact_code (if provided) compiles/runs and produces expected output."""
    exact = task.get("exact_code")
    if not exact:
        pytest.skip(f"{task['id']}: no exact_code specified")
    result = EXECUTOR.execute_code(
        code=exact,
        language=task["language"],
        stdin_data=task.get("input", ""),
        timeout=10.0,
    )
    assert result.is_success, f"{task['id']}: exact_code failed execution: {result.error or result.stderr}"
    assert outputs_equivalent(task["expected_output"], result.stdout), (
        f"{task['id']}: exact_code stdout did not match expected output.\n"
        f"Expected:\n{task['expected_output']}\nGot:\n{result.stdout}"
    )
