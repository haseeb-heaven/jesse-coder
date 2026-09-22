"""
Terminal User Interface (TUI) Launcher for JesseCoder.
Launches the full-screen Textual TUI workbench.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure source and project root are in sys.path
_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_SOURCE_DIR = _ROOT_DIR / "source"
_INTERFACES_DIR = _ROOT_DIR / "interfaces"
for _p in (str(_SOURCE_DIR), str(_INTERFACES_DIR), str(_ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from interfaces.tui.app import JesseTUIApp, run_tui


def main() -> None:
    run_tui()


if __name__ == "__main__":
    main()
