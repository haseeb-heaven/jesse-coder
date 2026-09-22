"""
TUI module wrapper — delegates to interfaces.tui.app.
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_INTERFACES = _ROOT / "interfaces"
if str(_INTERFACES) not in sys.path:
    sys.path.insert(0, str(_INTERFACES))

from interfaces.tui.app import *
