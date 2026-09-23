"""Tests for JesseClient error mapping and response handling."""

from unittest.mock import MagicMock, patch
import pytest
import openai
import httpx

from jesse_coder.client import JesseClient
from jesse_coder.client import PerKeyRequestPacer
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


def test_request_pacer_spaces_six_requests_for_one_key_by_200ms():
    now = [0.0]
    starts = []

    def fake_sleep(delay):
        now[0] += delay

    pacer = PerKeyRequestPacer(
        key_fingerprint="same-key",
        interval_seconds=0.2,
        monotonic=lambda: now[0],
        sleep=fake_sleep,
    )

    for _ in range(6):
        pacer.wait()
        starts.append(now[0])

    assert starts == pytest.approx([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    assert all(right - left >= 0.2 - 1e-9 for left, right in zip(starts, starts[1:]))


def test_request_pacer_does_not_share_slots_between_different_keys():
    now = [0.0]

    def fake_sleep(delay):
        now[0] += delay

    first_key = PerKeyRequestPacer("key-a", 0.2, lambda: now[0], fake_sleep)
    second_key = PerKeyRequestPacer("key-b", 0.2, lambda: now[0], fake_sleep)

    first_key.wait()
    first_key.wait()
    second_key.wait()

    assert now[0] == pytest.approx(0.2)


def test_chat_requests_from_separate_clients_share_per_key_pacing(monkeypatch):
    now = [0.0]
    starts = []

    def fake_sleep(delay):
        now[0] += delay

    def handler(request):
        starts.append(now[0])
        if request.url.path.endswith("/feedback"):
            return httpx.Response(200, json={"recorded": True})
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 1,
                "model": "jesse-prod",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "ok"},
                    "finish_reason": "stop",
                }],
            },
        )

    transport = httpx.MockTransport(handler)

    config = JesseConfig(
        api_key="pacing-integration-test-key",
        base_url="https://jesse.test/api/v1",
        max_retries=0,
    )
    first_client = JesseClient(config=config)
    second_client = JesseClient(config=config)
    first_client._client._client._transport = transport
    second_client._client._client._transport = transport
    first_client._http._transport = transport
    second_client._http._transport = transport
    pacer = first_client._request_pacer
    pacer._monotonic = lambda: now[0]
    pacer._sleep = fake_sleep

    try:
        first_client.chat([{"role": "user", "content": "first"}])
        second_client.submit_feedback(message_id="msg-test", rating="thumbs_down")
        second_client.chat([{"role": "user", "content": "third"}])
    finally:
        first_client.close()
        second_client.close()

    assert starts == pytest.approx([0.0, 0.2, 0.4])


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
