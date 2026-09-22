"""
Jesse-Coder Package
===================
A modular, production-ready coding chatbot and execution workbench built on the Jesse API
(OpenAI-compatible) with real-time streaming, comprehensive error handling,
open-agent code execution, and a Textual TUI.
"""

from __future__ import annotations

try:
    from .config import JesseConfig
    from .exceptions import (
        JesseBotError,
        JesseAuthenticationError,
        JesseConnectionError,
        JesseRateLimitError,
        JesseBadRequestError,
        JesseServerError,
        JesseStreamError,
        JesseConfigError,
    )
    from .conversation import ConversationManager, ChatMessage
    from .client import JesseClient
    from .bot import JesseCodingBot
    from .executor import CodeExecutor, ExecutionResult
    from .code_extractor import (
        extract_code_blocks,
        get_primary_code_block,
        ExtractedCodeBlock,
    )
    from .tui import JesseTUIApp, run_tui
except (ImportError, ValueError):
    from config import JesseConfig
    from exceptions import (
        JesseBotError,
        JesseAuthenticationError,
        JesseConnectionError,
        JesseRateLimitError,
        JesseBadRequestError,
        JesseServerError,
        JesseStreamError,
        JesseConfigError,
    )
    from conversation import ConversationManager, ChatMessage
    from client import JesseClient
    from bot import JesseCodingBot
    from executor import CodeExecutor, ExecutionResult
    from code_extractor import (
        extract_code_blocks,
        get_primary_code_block,
        ExtractedCodeBlock,
    )
    from tui import JesseTUIApp, run_tui

__all__ = [
    "JesseConfig",
    "JesseBotError",
    "JesseAuthenticationError",
    "JesseConnectionError",
    "JesseRateLimitError",
    "JesseBadRequestError",
    "JesseServerError",
    "JesseStreamError",
    "JesseConfigError",
    "ConversationManager",
    "ChatMessage",
    "JesseClient",
    "JesseCodingBot",
    "CodeExecutor",
    "ExecutionResult",
    "extract_code_blocks",
    "get_primary_code_block",
    "ExtractedCodeBlock",
    "JesseTUIApp",
    "run_tui",
]
