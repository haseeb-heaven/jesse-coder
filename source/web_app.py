#!/usr/bin/env python3
"""
JesseCoder WebApp Runner.
Starts the FastAPI backend with Uvicorn and opens the browser.
"""

from __future__ import annotations

import argparse
import logging
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Add source directory and project root to path
SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent
for p in (str(SRC_DIR), str(ROOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import uvicorn

logger = logging.getLogger("jesse_coder.webapp")


def open_browser_delayed(url: str, delay: float = 1.0) -> None:
    """Open the browser after a brief delay so the server has bound to the port."""
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            logger.debug("Failed to auto-open browser: %s", e)
    threading.Thread(target=_open, daemon=True).start()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run JesseCoder WebApp.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open web browser")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    print("\n" + "=" * 64)
    print("  ⚡ JesseCoder — Modern WebApp & Isolated Execution Console")
    print("=" * 64)
    print(f"  URL:         {url}")
    print(f"  API Docs:    {url}/docs")
    print(f"  Environment: Python {sys.version.split()[0]} + TypeScript Frontend")
    print("=" * 64 + "\n")

    if not args.no_browser:
        open_browser_delayed(url)

    uvicorn.run(
        "web_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
        app_dir=str(SRC_DIR),
    )


if __name__ == "__main__":
    main()
