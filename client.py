"""
Jesse API Client Module.
Provides low-level interaction with Jesse's OpenAI-compatible API,
including robust try/catch error handling, token streaming, and session management.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List, Optional
import openai
from openai import OpenAI

try:
    from .config import JesseConfig
    from .exceptions import (
        JesseAuthenticationError,
        JesseBadRequestError,
        JesseBotError,
        JesseConnectionError,
        JesseRateLimitError,
        JesseServerError,
        JesseStreamError,
    )
except ImportError:
    from config import JesseConfig
    from exceptions import (
        JesseAuthenticationError,
        JesseBadRequestError,
        JesseBotError,
        JesseConnectionError,
        JesseRateLimitError,
        JesseServerError,
        JesseStreamError,
    )

logger = logging.getLogger("jesse_coder.client")


class JesseClient:
    """
    Client wrapper for Jesse's OpenAI-compatible API endpoint.
    Translates underlying networking and API errors into domain-specific exceptions.
    """

    def __init__(self, config: Optional[JesseConfig] = None) -> None:
        self.config = config or JesseConfig()
        self.config.validate()

        self._client = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
        )

    def _map_openai_error(self, err: Exception) -> JesseBotError:
        """Map raw OpenAI or system exceptions to custom JesseBotError types."""
        if isinstance(err, (openai.AuthenticationError, openai.PermissionDeniedError)):
            masked_key = self.config.api_key[:8] + "..." if len(self.config.api_key) > 8 else "***"
            return JesseAuthenticationError(
                f"Authentication/Permission denied by Jesse API ({getattr(err, 'status_code', 401)}). Please verify your API key: '{masked_key}'",
                original_error=err,
            )
        elif isinstance(err, openai.APIConnectionError):
            return JesseConnectionError(
                f"Failed to connect to Jesse endpoint at '{self.config.base_url}'. Check network or URL availability.",
                original_error=err,
            )
        elif isinstance(err, openai.RateLimitError):
            return JesseRateLimitError(
                "Jesse API rate limit or quota exceeded. Please wait before retrying.",
                original_error=err,
            )
        elif isinstance(err, openai.BadRequestError):
            return JesseBadRequestError(
                f"Bad request to Jesse API: {err}",
                original_error=err,
            )
        elif isinstance(err, (openai.InternalServerError, openai.APIStatusError)):
            return JesseServerError(
                f"Jesse API server returned error status ({getattr(err, 'status_code', 'unknown')}): {err}",
                original_error=err,
            )
        elif isinstance(err, (openai.APIError, openai.OpenAIError)):
            return JesseBotError(
                f"Jesse OpenAI-compatible API error: {err}",
                original_error=err,
            )
        else:
            return JesseBotError(
                f"Unexpected error communicating with Jesse: {err}",
                original_error=err,
            )

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **extra_params: Any,
    ) -> Iterator[str]:
        """
        Stream chat completions token-by-token from Jesse API.

        Args:
            messages: Formatted list of message dicts ({"role": ..., "content": ...}).
            model: Model identifier override (defaults to config.model).
            temperature: Temperature override (defaults to config.temperature).
            max_tokens: Maximum tokens override.
            **extra_params: Additional kwargs passed to OpenAI chat completions.

        Yields:
            str: Text chunk deltas as they arrive from the server.

        Raises:
            JesseAuthenticationError: If API key is rejected.
            JesseConnectionError: If connection fails.
            JesseRateLimitError: If rate limit is hit.
            JesseBadRequestError: If payload is rejected.
            JesseServerError: If remote service returns 5xx.
            JesseStreamError: If stream breaks unexpectedly.
            JesseBotError: For any other client-side or unexpected issue.
        """
        target_model = model or self.config.model
        temp = temperature if temperature is not None else self.config.temperature
        tokens = max_tokens if max_tokens is not None else self.config.max_tokens

        try:
            stream_response = self._client.chat.completions.create(
                model=target_model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temp,
                max_tokens=tokens,
                stream=True,
                **extra_params,
            )
        except Exception as e:
            raise self._map_openai_error(e) from e

        try:
            for chunk in stream_response:
                if not chunk or not chunk.choices:
                    continue

                choice = chunk.choices[0]
                delta = getattr(choice, "delta", None)
                if delta is None:
                    continue

                content = getattr(delta, "content", None)
                if content:
                    yield content

        except (openai.OpenAIError, OSError, IOError) as e:
            raise JesseStreamError(
                f"Error occurred mid-stream while reading tokens: {e}",
                original_error=e,
            ) from e
        except Exception as e:
            raise JesseStreamError(
                f"Unexpected failure during token streaming: {e}",
                original_error=e,
            ) from e

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **extra_params: Any,
    ) -> str:
        """
        Execute non-streaming chat completion.

        Args:
            messages: List of message dictionaries.
            model: Model name override.
            temperature: Sampling temperature override.
            max_tokens: Max tokens override.
            **extra_params: Additional parameters.

        Returns:
            str: Complete response text.
        """
        target_model = model or self.config.model
        temp = temperature if temperature is not None else self.config.temperature
        tokens = max_tokens if max_tokens is not None else self.config.max_tokens

        try:
            response = self._client.chat.completions.create(
                model=target_model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temp,
                max_tokens=tokens,
                stream=False,
                **extra_params,
            )
            if not response.choices:
                return ""
            return response.choices[0].message.content or ""
        except Exception as e:
            raise self._map_openai_error(e) from e

    def close(self) -> None:
        """Close underlying HTTP client connections."""
        try:
            self._client.close()
        except Exception as e:
            logger.warning(f"Error while closing JesseClient: {e}")

    def __enter__(self) -> JesseClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
