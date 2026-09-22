"""
JesseCoder Python Package.
A modular, production-ready coding assistant and execution engine for Jesse API.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure package directory is in sys.path
_PKG_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _PKG_DIR.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

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
]
