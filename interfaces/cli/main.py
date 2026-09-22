"""
Command Line Interface (CLI) Launcher for JesseCoder.
Supports interactive terminal chat, one-shot prompt streaming,
and auto-execution.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure source and project root are in sys.path
_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_SOURCE_DIR = _ROOT_DIR / "source"
_INTERFACES_DIR = _ROOT_DIR / "interfaces"
for _p in (str(_SOURCE_DIR), str(_INTERFACES_DIR), str(_ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from bot import JesseCodingBot
    from config import DEFAULT_API_KEY, DEFAULT_BASE_URL, DEFAULT_MODEL, JesseConfig
    from exceptions import JesseBotError, JesseConfigError
except ImportError:
    from jesse_coder.bot import JesseCodingBot
    from jesse_coder.config import (
        DEFAULT_API_KEY,
        DEFAULT_BASE_URL,
        DEFAULT_MODEL,
        JesseConfig,
    )
    from jesse_coder.exceptions import JesseBotError, JesseConfigError

from interfaces.cli.cli import run_interactive_cli, run_one_shot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="JesseCoder CLI — Autonomous Command Line Engineering Assistant"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Jesse API Key (defaults to env JESSE_API_KEY)",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help=f"Jesse Base URL (defaults to env JESSE_BASE_URL or '{DEFAULT_BASE_URL}')",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"Model identifier: 'jesse-prod' or 'jesse-pristine' (default: '{DEFAULT_MODEL}')",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature (default: 0.2)",
    )
    parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        default=None,
        help="Run a single one-shot coding prompt with streaming and exit.",
    )
    parser.add_argument(
        "--exec",
        "-e",
        action="store_true",
        default=False,
        help="Execute generated code automatically.",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        default=False,
        help="Launch the full Textual TUI interface.",
    )
    parser.add_argument(
        "--gui",
        "--web",
        action="store_true",
        default=False,
        help="Launch the Graphical User Interface (Web Console Workbench).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    overrides = {}
    if args.api_key:
        overrides["api_key"] = args.api_key
    if args.base_url:
        overrides["base_url"] = args.base_url
    if args.model:
        overrides["model"] = args.model
    if args.temperature is not None:
        overrides["temperature"] = args.temperature

    try:
        config = JesseConfig.from_env(**overrides)
        bot = JesseCodingBot(config=config)
    except JesseConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.gui:
        try:
            from interfaces.gui.app import main as run_gui_app
            run_gui_app()
            sys.exit(0)
        except ImportError:
            from gui.app import main as run_gui_app
            run_gui_app()
            sys.exit(0)

    if args.tui:
        try:
            from interfaces.tui.main import run_tui
            run_tui(bot)
            sys.exit(0)
        except ImportError:
            from tui.main import run_tui
            run_tui(bot)
            sys.exit(0)

    if args.prompt:
        run_one_shot(bot, args.prompt, auto_exec=args.exec)
    else:
        run_interactive_cli(bot, auto_exec=args.exec)


if __name__ == "__main__":
    main()
