"""Tests for the benchmark output equivalence rules used by the testing harness.

Tolerant matching (default) ignores value label prefixes and line breaks while
still requiring every value and its order to match. Strict matching requires an
exact one-to-one stdout match.
"""

from testing.automated_testing import (
    normalize_output,
    outputs_equivalent,
    value_tokens,
)

# The real task_04 (Shortest Path) grading case, recorded by the harness.
SHORTEST_PATH_EXPECTED = "0 3 1 4 7\n"
SHORTEST_PATH_LABELLED = "Node 0: 0\nNode 1: 3\nNode 2: 1\nNode 3: 4\nNode 4: 7\n"


def test_identical_output_matches():
    assert outputs_equivalent("0 3 1 4 7\n", "0 3 1 4 7\n")
    assert outputs_equivalent("0 3 1 4 7\n", "0 3 1 4 7\n", strict=True)


def test_label_prefixes_are_ignored():
    assert outputs_equivalent(SHORTEST_PATH_EXPECTED, SHORTEST_PATH_LABELLED)


def test_strict_mode_rejects_labelled_output():
    assert not outputs_equivalent(SHORTEST_PATH_EXPECTED, SHORTEST_PATH_LABELLED, strict=True)


def test_line_breaks_are_ignored():
    assert outputs_equivalent("0 3 1 4 7\n", "0\n3\n1\n4\n7\n")


def test_assignment_style_labels_are_ignored():
    assert outputs_equivalent("3 1 4 7\n", "dist[1] = 3\ndist[2] = 1\ndist[3] = 4\ndist[4] = 7\n")


def test_wrong_value_is_rejected():
    wrong = "Node 0: 0\nNode 1: 9\nNode 2: 1\nNode 3: 4\nNode 4: 7\n"
    assert not outputs_equivalent(SHORTEST_PATH_EXPECTED, wrong)


def test_extra_values_are_rejected():
    extra = SHORTEST_PATH_LABELLED + "Node 5: 99\n"
    assert not outputs_equivalent(SHORTEST_PATH_EXPECTED, extra)


def test_wrong_order_is_rejected():
    assert not outputs_equivalent(SHORTEST_PATH_EXPECTED, "7 4 1 3 0\n")


def test_empty_output_is_rejected():
    assert not outputs_equivalent(SHORTEST_PATH_EXPECTED, "")
    assert not outputs_equivalent("", SHORTEST_PATH_LABELLED)


def test_value_tokens_strip_labels_only():
    assert value_tokens("Node 0: 0") == ["0"]
    assert value_tokens("0 3 1 4 7") == ["0", "3", "1", "4", "7"]
    assert value_tokens("Result -> 12\nOK") == ["12", "OK"]


def test_normalize_output_trims_whitespace():
    assert normalize_output("  1 2  \n\n  3  \n") == "1 2\n\n  3"
