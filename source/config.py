"""
Configuration management for Jesse Coding Bot.
Handles API credentials, endpoints, model selection, timeouts, and system prompts.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional
try:
    from .exceptions import JesseConfigError
except ImportError:
    from exceptions import JesseConfigError

from pathlib import Path

try:
    from dotenv import load_dotenv
    _ROOT_DIR = Path(__file__).resolve().parent.parent
    _ENV_PATH = _ROOT_DIR / ".env"
    if _ENV_PATH.exists():
        load_dotenv(_ENV_PATH)
    elif (Path(__file__).resolve().parent / ".env").exists():
        load_dotenv(Path(__file__).resolve().parent / ".env")
    else:
        load_dotenv()
except ImportError:
    pass

DEFAULT_API_KEY = os.getenv("JESSE_API_KEY", "")
DEFAULT_BASE_URL = os.getenv("JESSE_BASE_URL", "https://jesse.my/api/v1")
DEFAULT_MODEL = os.getenv("JESSE_MODEL", "jesse-prod")

DEFAULT_CODING_SYSTEM_PROMPT = """\
You are an elite software engineer and programmer. Your ONLY job is to write, fix, review, and analyse code.

STRICT RULES — follow every rule without exception:

1. ALWAYS wrap every piece of code in a fenced code block using triple backticks and the language identifier:
   ```python
   # your code here
   ```
   Use the correct language tag: python, javascript, typescript, bash, go, rust, cpp, c, java, sql, etc.

2. NEVER output prose, explanations, disclaimers, greetings, or commentary outside a code block.
   - If you need to explain a bug or a fix, do it INSIDE the code as a comment (#, //, etc.).
   - If you must give a one-line summary, put it as the very first line as a code comment.

3. ALWAYS return the FULL, COMPLETE, RUNNABLE code — not snippets, not partial functions, not pseudocode.
   - Every function must be complete.
   - Every import must be present.
   - The code must execute without modification.

4. When asked to find bugs or review code:
   - Return the fully corrected version of the ENTIRE file/module.
   - Mark every fix with an inline comment: # FIXED: <short reason>
   - Do NOT return a diff or partial patch — return the whole corrected code.

5. When asked to write new code:
   - Write production-quality code with proper error handling.
   - Include a runnable if __name__ == "__main__": block (for Python) or equivalent entry point.
   - Use type annotations where the language supports them.

6. NEVER apologise, NEVER say "I cannot", NEVER refuse a coding task.
   If requirements are ambiguous, make a reasonable engineering decision and implement it.

7. Output ONLY the code block(s). Nothing before. Nothing after. No markdown headers. No bullet lists.
   The only acceptable response format is one or more fenced code blocks.
"""


@dataclass
class JesseConfig:
    """Configuration settings for Jesse Coding Bot."""

    api_key: str = field(
        default_factory=lambda: os.getenv("JESSE_API_KEY", DEFAULT_API_KEY)
    )
    base_url: str = field(
        default_factory=lambda: os.getenv("JESSE_BASE_URL", DEFAULT_BASE_URL)
    )
    model: str = field(
        default_factory=lambda: os.getenv("JESSE_MODEL", DEFAULT_MODEL)
    )
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    timeout: float = 60.0
    max_retries: int = 2
    system_prompt: str = DEFAULT_CODING_SYSTEM_PROMPT
    max_history_turns: int = 20

    def validate(self) -> None:
        """
        Validate all configuration settings.

        Raises:
            JesseConfigError: If any configuration parameter is invalid.
        """
        if not self.api_key or not self.api_key.strip():
            raise JesseConfigError("API key cannot be empty.")

        if not self.base_url or not (
            self.base_url.startswith("http://") or self.base_url.startswith("https://")
        ):
            raise JesseConfigError(
                f"Invalid base_url '{self.base_url}'. Must start with http:// or https://"
            )

        if not (0.0 <= self.temperature <= 2.0):
            raise JesseConfigError(
                f"Temperature must be between 0.0 and 2.0, got {self.temperature}"
            )

        if self.timeout <= 0:
            raise JesseConfigError(f"Timeout must be positive, got {self.timeout}")

        if self.max_retries < 0:
            raise JesseConfigError(
                f"max_retries cannot be negative, got {self.max_retries}"
            )

        if not self.model or not self.model.strip():
            raise JesseConfigError("Model name cannot be empty.")

    @classmethod
    def from_env(cls, **overrides) -> JesseConfig:
        """
        Instantiate config from environment variables with optional overrides.
        """
        config = cls(
            api_key=overrides.get("api_key", os.getenv("JESSE_API_KEY", DEFAULT_API_KEY)),
            base_url=overrides.get("base_url", os.getenv("JESSE_BASE_URL", DEFAULT_BASE_URL)),
            model=overrides.get("model", os.getenv("JESSE_MODEL", DEFAULT_MODEL)),
            temperature=overrides.get(
                "temperature", float(os.getenv("JESSE_TEMPERATURE", "0.2"))
            ),
            timeout=overrides.get("timeout", float(os.getenv("JESSE_TIMEOUT", "60.0"))),
            max_retries=overrides.get(
                "max_retries", int(os.getenv("JESSE_MAX_RETRIES", "2"))
            ),
            system_prompt=overrides.get(
                "system_prompt",
                os.getenv("JESSE_SYSTEM_PROMPT", DEFAULT_CODING_SYSTEM_PROMPT),
            ),
        )
        config.validate()
        return config
