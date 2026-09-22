"""
CLI module wrapper — delegates to interfaces.cli.cli.
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_INTERFACES = _ROOT / "interfaces"
if str(_INTERFACES) not in sys.path:
    sys.path.insert(0, str(_INTERFACES))

from interfaces.cli.cli import *
