#!/usr/bin/env python3
"""
Quickstart example demonstrating real-time token streaming with JesseCodingBot.
"""

import sys
from pathlib import Path

# Ensure package root is in sys.path
package_root = str(Path(__file__).resolve().parent.parent)
if package_root not in sys.path:
    sys.path.insert(0, package_root)

from jesse_coder import JesseCodingBot, JesseConfig, JesseBotError


def main():
    print("=" * 60)
    print(" Jesse Coding Bot - Real-time Streaming Demonstration ")
    print("=" * 60)

    # 1. Initialize configuration with Jesse API details
    config = JesseConfig(
        api_key="jesse_test_demo00000000000000000000000001",
        base_url="https://jesse.solidsf.com/api/v1",
        model="jesse-prod",
        temperature=0.1,
    )

    # 2. Instantiate bot
    try:
        bot = JesseCodingBot(config=config)
    except JesseBotError as e:
        print(f"Error initializing bot: {e}", file=sys.stderr)
        return

    # 3. Stream a coding question
    question = (
        "Write a Python function to perform concurrent HTTP requests with asyncio and aiohttp, "
        "including rate-limiting via an asyncio.Semaphore and comprehensive exception handling."
    )

    print(f"\nUser Query:\n{question}\n")
    print("Streaming Response from Jesse:\n" + "-" * 40)

    try:
        for chunk in bot.ask_stream(question):
            sys.stdout.write(chunk)
            sys.stdout.flush()
        print("\n" + "-" * 40)
        print("\nStreaming finished successfully!")
        print(f"Total messages in conversation context: {len(bot.get_history())}")

    except JesseBotError as e:
        print(f"\n[Error caught]: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nStream aborted by user.")


if __name__ == "__main__":
    main()
