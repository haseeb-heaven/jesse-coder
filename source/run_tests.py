#!/usr/bin/env python3
"""
Self-contained test runner for Jesse Coding Bot.
Executes all unit, boundary, exception-handling, and live integration tests.
Run directly with: python3 run_tests.py
"""

import sys
from pathlib import Path
import pytest

if __name__ == "__main__":
    bot_dir = Path(__file__).resolve().parent
    parent_dir = bot_dir.parent

    for p in (str(bot_dir), str(parent_dir)):
        if p not in sys.path:
            sys.path.insert(0, p)

    config_file = bot_dir / "pytest.ini"
    tests_dir = bot_dir / "tests"

    args = [
        str(tests_dir),
        "-c",
        str(config_file),
        "-v",
        "--tb=short",
    ]

    print(f"Running test suite in {tests_dir}...")
    sys.exit(pytest.main(args))
