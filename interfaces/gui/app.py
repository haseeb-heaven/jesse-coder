"""
Graphical User Interface (GUI) / WebApp runner for JesseCoder.
Starts the FastAPI server with live SSE token streaming and executes code
in process-isolated sandboxes.
"""

from __future__ import annotations

import argparse
import sys
import time
import webbrowser
from pathlib import Path

# Add GUI directory, source directory, and project root to path
GUI_DIR = Path(__file__).resolve().parent
ROOT_DIR = GUI_DIR.parent.parent
SRC_DIR = ROOT_DIR / "source"
for p in (str(GUI_DIR), str(SRC_DIR), str(ROOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import uvicorn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="JesseCoder GUI / Web Console — Interactive Autonomous Engineering Workbench"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind the server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run the web server on (default: 8080)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=False,
        help="Enable auto-reload for development",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        default=False,
        help="Do not open the browser automatically upon launch",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    url = f"http://{args.host}:{args.port}"
    print(f"\n================================================================")
    print(f"  ⚡ JesseCoder GUI — Modern WebApp & Isolated Execution Console")
    print(f"================================================================")
    print(f"  URL:         {url}")
    print(f"  API Docs:    {url}/docs")
    print(f"  Environment: Python + TypeScript Frontend")
    print(f"================================================================\n")

    if not args.no_browser:
        def _open_browser():
            time.sleep(1.2)
            webbrowser.open(url)

        import threading
        threading.Thread(target=_open_browser, daemon=True).start()

    from interfaces.gui.server import app
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
