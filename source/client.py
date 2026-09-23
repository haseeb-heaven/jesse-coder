"""
Jesse API Client Module.
Provides low-level interaction with Jesse's OpenAI-compatible API,
including robust try/catch error handling, token streaming, and session management.
Also exposes non-chat Jesse REST endpoints: feedback, memory, and documents.
"""

from __future__ import annotations

import logging
import hashlib
import threading
import time
from typing import Any, Dict, Iterator, List, Optional
import httpx
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


class PerKeyRequestPacer:
    """Keep requests for one API key at least ``interval_seconds`` apart."""

    def __init__(
        self,
        key_fingerprint: str,
        interval_seconds: float = 0.2,
        monotonic=time.monotonic,
        sleep=time.sleep,
    ) -> None:
        self.key_fingerprint = key_fingerprint
        self.interval_seconds = interval_seconds
        self._monotonic = monotonic
        self._sleep = sleep
        self._lock = threading.Lock()
        self._next_request_at = 0.0

    def wait(self) -> None:
        """Reserve a request slot, serializing callers that use the same key."""
        with self._lock:
            delay = self._next_request_at - self._monotonic()
            if delay > 0:
                self._sleep(delay)
            self._next_request_at = self._monotonic() + self.interval_seconds


_PACERS_BY_KEY: Dict[str, PerKeyRequestPacer] = {}
_PACERS_LOCK = threading.Lock()


def _pacer_for_api_key(api_key: str) -> PerKeyRequestPacer:
    # Keep only a one-way fingerprint in process memory rather than retaining
    # credentials in the global registry.
    fingerprint = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    with _PACERS_LOCK:
        pacer = _PACERS_BY_KEY.get(fingerprint)
        if pacer is None:
            pacer = PerKeyRequestPacer(fingerprint)
            _PACERS_BY_KEY[fingerprint] = pacer
        return pacer


class JesseClient:
    """
    Client wrapper for Jesse's OpenAI-compatible API endpoint.
    Translates underlying networking and API errors into domain-specific exceptions.
    """

    def __init__(self, config: Optional[JesseConfig] = None) -> None:
        self.config = config or JesseConfig()
        self.config.validate()

        # Root URL without trailing slash, used by REST helpers
        self._base_url = self.config.base_url.strip().rstrip('/')
        self._api_key = self.config.api_key.strip()
        self._request_pacer = _pacer_for_api_key(self._api_key)
        request_hooks = {"request": [lambda _request: self._request_pacer.wait()]}

        # Install the same per-key pacer in both HTTP transports. The OpenAI
        # transport hook runs for every wire attempt, including SDK retries.
        openai_http = httpx.Client(
            timeout=self.config.timeout,
            event_hooks=request_hooks,
        )

        self._client = OpenAI(
            base_url=self._base_url,
            api_key=self._api_key,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
            http_client=openai_http,
        )

        # Shared httpx client for non-chat REST endpoints
        self._http = httpx.Client(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=30.0,
            event_hooks=request_hooks,
        )
        self.last_message_id: Optional[str] = None

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
            self.last_message_id = getattr(response, "id", None)
            if not response.choices:
                return ""
            return response.choices[0].message.content or ""
        except Exception as e:
            raise self._map_openai_error(e) from e

    # ------------------------------------------------------------------
    # Jesse REST API helpers (non-chat endpoints)
    # ------------------------------------------------------------------

    def get_models(self) -> List[str]:
        """GET /models — List available models for this API key."""
        try:
            resp = self._http.get("/models")
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return [m.get("id", str(m)) if isinstance(m, dict) else str(m) for m in data]
                elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                    return [m.get("id", str(m)) if isinstance(m, dict) else str(m) for m in data["data"]]
                elif isinstance(data, dict) and "models" in data and isinstance(data["models"], list):
                    return [m.get("id", str(m)) if isinstance(m, dict) else str(m) for m in data["models"]]
                return [self.config.model]
        except Exception:
            pass

        try:
            models_page = self._client.models.list()
            return [m.id for m in models_page.data]
        except Exception as err:
            raise self._map_openai_error(err)

    def submit_feedback(
        self,
        message_id: str,
        rating: str,
        correction: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """POST /feedback — Mark an answer right (👍) or wrong (👎), with an optional correction.

        Args:
            message_id: Identifier for the assistant message being rated.
            rating:     'thumbs_up' or 'thumbs_down'.
            correction: Optional corrected answer text for learning.
            model:      Model that produced the answer (defaults to config.model).
        """
        payload: Dict[str, Any] = {
            "message_id": message_id,
            "rating": rating,
            "model": model or self.config.model,
        }
        if correction and correction.strip():
            payload["correction"] = correction.strip()
        try:
            resp = self._http.post("/feedback", json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise JesseBotError(f"Feedback submission failed ({e.response.status_code}): {e.response.text}") from e
        except Exception as e:
            raise JesseBotError(f"Feedback request error: {e}") from e

    def get_memory(self) -> Dict[str, Any]:
        """GET /memory — Retrieve facts Jesse remembers for this API key."""
        try:
            resp = self._http.get("/memory")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise JesseBotError(f"Memory fetch failed ({e.response.status_code}): {e.response.text}") from e
        except Exception as e:
            raise JesseBotError(f"Memory request error: {e}") from e

    def delete_memory(self) -> Dict[str, Any]:
        """DELETE /memory — Erase everything Jesse remembers for this API key."""
        try:
            resp = self._http.delete("/memory")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise JesseBotError(f"Memory delete failed ({e.response.status_code}): {e.response.text}") from e
        except Exception as e:
            raise JesseBotError(f"Memory delete error: {e}") from e

    def store_document(
        self,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """POST /documents — Store a document for retrieval in later requests."""
        payload: Dict[str, Any] = {"title": title, "content": content}
        if metadata:
            payload["metadata"] = metadata
        try:
            resp = self._http.post("/documents", json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise JesseBotError(f"Document store failed ({e.response.status_code}): {e.response.text}") from e
        except Exception as e:
            raise JesseBotError(f"Document store error: {e}") from e

    def list_documents(self) -> Dict[str, Any]:
        """GET /documents — List stored documents for this API key."""
        try:
            resp = self._http.get("/documents")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise JesseBotError(f"Document list failed ({e.response.status_code}): {e.response.text}") from e
        except Exception as e:
            raise JesseBotError(f"Document list error: {e}") from e

    def query_documents(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """POST /documents/query — Semantic search over stored documents."""
        try:
            resp = self._http.post("/documents/query", json={"query": query, "top_k": top_k})
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise JesseBotError(f"Document query failed ({e.response.status_code}): {e.response.text}") from e
        except Exception as e:
            raise JesseBotError(f"Document query error: {e}") from e

    def close(self) -> None:
        """Close underlying HTTP client connections."""
        try:
            self._client.close()
        except Exception as e:
            logger.warning(f"Error while closing JesseClient OpenAI client: {e}")
        try:
            self._http.close()
        except Exception as e:
            logger.warning(f"Error while closing JesseClient httpx client: {e}")

    def __enter__(self) -> JesseClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
