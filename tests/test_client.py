"""Tests for JesseClient error mapping and response handling."""

from unittest.mock import MagicMock, patch
import pytest
import openai
import httpx

from jesse_coder.client import JesseClient
from jesse_coder.config import JesseConfig
from jesse_coder.exceptions import (
    JesseAuthenticationError,
    JesseBadRequestError,
    JesseConnectionError,
    JesseRateLimitError,
    JesseServerError,
    JesseStreamError,
)


@pytest.fixture
def mock_client():
    cfg = JesseConfig(api_key="test_key", base_url="https://jesse.solidsf.com/api/v1")
    return JesseClient(config=cfg)


def test_authentication_error_mapping(mock_client):
    req = httpx.Request("POST", "https://jesse.solidsf.com/api/v1/chat/completions")
    resp = httpx.Response(401, request=req)
    err = openai.AuthenticationError("Invalid API key", response=resp, body=None)

    with patch.object(mock_client._client.chat.completions, "create", side_effect=err):
        with pytest.raises(JesseAuthenticationError) as exc_info:
            list(mock_client.stream_chat([{"role": "user", "content": "hi"}]))
        assert "Authentication/Permission denied" in str(exc_info.value)


def test_connection_error_mapping(mock_client):
    req = httpx.Request("POST", "https://jesse.solidsf.com/api/v1/chat/completions")
    err = openai.APIConnectionError(request=req)

    with patch.object(mock_client._client.chat.completions, "create", side_effect=err):
        with pytest.raises(JesseConnectionError) as exc_info:
            list(mock_client.stream_chat([{"role": "user", "content": "hi"}]))
        assert "Failed to connect" in str(exc_info.value)


def test_rate_limit_error_mapping(mock_client):
    req = httpx.Request("POST", "https://jesse.solidsf.com/api/v1/chat/completions")
    resp = httpx.Response(429, request=req)
    err = openai.RateLimitError("Rate limit exceeded", response=resp, body=None)

    with patch.object(mock_client._client.chat.completions, "create", side_effect=err):
        with pytest.raises(JesseRateLimitError) as exc_info:
            mock_client.chat([{"role": "user", "content": "hi"}])
        assert "rate limit" in str(exc_info.value).lower()


def test_bad_request_error_mapping(mock_client):
    req = httpx.Request("POST", "https://jesse.solidsf.com/api/v1/chat/completions")
    resp = httpx.Response(400, request=req)
    err = openai.BadRequestError("Invalid parameter", response=resp, body=None)

    with patch.object(mock_client._client.chat.completions, "create", side_effect=err):
        with pytest.raises(JesseBadRequestError) as exc_info:
            mock_client.chat([{"role": "user", "content": "hi"}])
        assert "Bad request" in str(exc_info.value)


def test_server_error_mapping(mock_client):
    req = httpx.Request("POST", "https://jesse.solidsf.com/api/v1/chat/completions")
    resp = httpx.Response(500, request=req)
    err = openai.InternalServerError("Internal server error", response=resp, body=None)

    with patch.object(mock_client._client.chat.completions, "create", side_effect=err):
        with pytest.raises(JesseServerError) as exc_info:
            mock_client.chat([{"role": "user", "content": "hi"}])
        assert "500" in str(exc_info.value) or "error" in str(exc_info.value)


def test_stream_chunk_generator(mock_client):
    chunk1 = MagicMock()
    chunk1.choices = [MagicMock(delta=MagicMock(content="def "))]

    chunk2 = MagicMock()
    chunk2.choices = [MagicMock(delta=MagicMock(content="hello():"))]

    chunk3 = MagicMock()
    chunk3.choices = [MagicMock(delta=MagicMock(content=None))]  # finish chunk

    with patch.object(
        mock_client._client.chat.completions,
        "create",
        return_value=iter([chunk1, chunk2, chunk3]),
    ):
        result = list(mock_client.stream_chat([{"role": "user", "content": "code"}]))
        assert result == ["def ", "hello():"]
