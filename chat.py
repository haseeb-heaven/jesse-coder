#!/usr/bin/env python3
"""
Quickstart interactive chat launcher.
Run directly with: python3 chat.py
"""

from pathlib import Path
import sys

# Ensure current folder is on sys.path
current_dir = str(Path(__file__).resolve().parent)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from main import main

if __name__ == "__main__":
    main()
