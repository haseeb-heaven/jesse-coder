"""
Entry point for Jesse Coding Bot.
Supports interactive chatbot mode or one-shot command-line prompt streaming.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure root is in path if executed directly as a script
package_root = str(Path(__file__).resolve().parent.parent)
if package_root not in sys.path:
    sys.path.insert(0, package_root)

try:
    from .bot import JesseCodingBot
    from .cli import run_interactive_cli
    from .config import DEFAULT_API_KEY, DEFAULT_BASE_URL, DEFAULT_MODEL, JesseConfig
    from .exceptions import JesseBotError, JesseConfigError
except ImportError:
    from jesse_coder.bot import JesseCodingBot
    from jesse_coder.cli import run_interactive_cli
    from jesse_coder.config import (
        DEFAULT_API_KEY,
        DEFAULT_BASE_URL,
        DEFAULT_MODEL,
        JesseConfig,
    )
    from jesse_coder.exceptions import JesseBotError, JesseConfigError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Jesse Coding Chatbot - Autonomous Engineering Assistant"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help=f"Jesse API Key (defaults to env JESSE_API_KEY or '{DEFAULT_API_KEY}')",
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
        "--web",
        action="store_true",
        default=False,
        help="Launch the modern WebApp interface (Python backend + TypeScript frontend).",
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

    if args.web:
        try:
            from web_app import main as run_web_app
        except ImportError:
            from .web_app import main as run_web_app
        run_web_app()
        sys.exit(0)

    if args.tui:
        try:
            from .tui import run_tui
        except ImportError:
            from tui import run_tui
        run_tui(bot)
        sys.exit(0)

    if args.prompt:
        # One-shot streaming mode
        try:
            for token in bot.ask_stream(args.prompt):
                sys.stdout.write(token)
                sys.stdout.flush()
            print()

            if args.exec:
                from cli import print_execution_result
                if bot.last_extracted_code:
                    block = bot.last_extracted_code
                    print(f"\n[Auto-executing generated {block.language} code...]")
                    res = bot.execute_code(block.code, language=block.language)
                    print_execution_result(res)
                else:
                    print("\n[No executable code block found in response.]")

            sys.exit(0)
        except JesseBotError as e:
            print(f"\n[Jesse Error]: {e}", file=sys.stderr)
            sys.exit(2)
        except KeyboardInterrupt:
            print("\n[Interrupted]", file=sys.stderr)
            sys.exit(130)
    else:
        # Interactive mode
        run_interactive_cli(bot, auto_exec=args.exec)


if __name__ == "__main__":
    main()
