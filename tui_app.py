#!/usr/bin/env python3
"""
1-Click Launcher for Jesse Coding Bot TUI.
Run directly with: python3 tui_app.py
"""

from pathlib import Path
import sys

# Ensure current and parent folders are on sys.path
current_dir = str(Path(__file__).resolve().parent)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tui import run_tui

if __name__ == "__main__":
    run_tui()
