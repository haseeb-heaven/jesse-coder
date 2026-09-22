"""Vercel serverless entrypoint for the JesseCoder web console.

Exposes the FastAPI/ASGI application (interfaces/gui/server.py) to Vercel's
Python runtime. The runtime looks for an `app` object in this module.
"""

from __future__ import annotations

import sys
from pathlib import Path

# In the Lambda bundle the layout is preserved relative to the project root,
# so the sources live next to api/.
_ROOT = Path(__file__).resolve().parent.parent

for _p in (str(_ROOT / "source"), str(_ROOT / "interfaces"), str(_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from interfaces.gui.server import app  # noqa: E402  (FastAPI/ASGI application)

application = app  # some runtime versions resolve the WSGI/ASGI name differently
