"""
Exceptions module for Jesse Coding Bot.
Provides custom exception classes and error classification for OpenAI-compatible APIs.
"""

from __future__ import annotations
from typing import Optional


class JesseBotError(Exception):
    """Base exception for all Jesse Coding Bot errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error

    def __str__(self) -> str:
        if self.original_error:
            return f"{self.message} (Underlying {type(self.original_error).__name__}: {self.original_error})"
        return self.message


class JesseConfigError(JesseBotError):
    """Raised when configuration values are missing, invalid, or malformed."""
    pass


class JesseAuthenticationError(JesseBotError):
    """Raised when API key is invalid, revoked, or missing appropriate permissions (HTTP 401)."""
    pass


class JesseConnectionError(JesseBotError):
    """Raised when connection to the Jesse endpoint fails, DNS lookup fails, or request times out."""
    pass


class JesseRateLimitError(JesseBotError):
    """Raised when the Jesse API rate limit or quota has been exceeded (HTTP 429)."""
    pass


class JesseBadRequestError(JesseBotError):
    """Raised when the request parameters or payload are invalid (HTTP 400)."""
    pass


class JesseServerError(JesseBotError):
    """Raised when the Jesse upstream server returns a 5xx error."""
    pass


class JesseStreamError(JesseBotError):
    """Raised when an error occurs during streaming token delivery."""
    pass
