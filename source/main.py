"""
CLI entrypoint wrapper — delegates to interfaces.cli.main.
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_INTERFACES = _ROOT / "interfaces"
if str(_INTERFACES) not in sys.path:
    sys.path.insert(0, str(_INTERFACES))

from interfaces.cli.main import *

if __name__ == "__main__":
    main()
