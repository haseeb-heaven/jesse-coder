"""
Tests for JesseCoder FastAPI Web Server.
Verifies health, execution, reset, history, raw, and SSE chat streaming endpoints.
"""

import json
import pytest
from starlette.testclient import TestClient

from web_server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check returns status online and config."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "model" in data
    assert "base_url" in data


def test_index_page(client):
    """Test index HTML route serves correctly."""
    res = client.get("/")
    assert res.status_code == 200
    assert "JesseCoder" in res.text
    assert "dialogue-stream" in res.text


def test_execute_code_success(client):
    """Test /api/execute successfully executes Python code."""
    code = "numbers = [x * 2 for x in range(5)]\nprint('RESULT:', numbers)"
    res = client.post("/api/execute", json={"code": code, "language": "python"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["exit_code"] == 0
    assert "RESULT: [0, 2, 4, 6, 8]" in data["stdout"]
    assert data["execution_time_ms"] > 0


def test_execute_code_failure(client):
    """Test /api/execute captures execution failure/syntax error."""
    code = "this is not valid python code !!!"
    res = client.post("/api/execute", json={"code": code, "language": "python"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["exit_code"] != 0
    assert len(data["stderr"]) > 0 or len(data["stdout"]) > 0


def test_reset_conversation(client):
    """Test /api/reset resets memory and returns confirmation."""
    res = client.post("/api/reset")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"

    history_res = client.get("/api/history")
    assert history_res.status_code == 200
    # Only system prompt message should remain
    assert len(history_res.json()["messages"]) == 1


def test_chat_stream_endpoint(client):
    """Test SSE streaming returns event chunks and done payload."""
    prompt = "Write a one-line Python print function"
    with client.stream("POST", "/api/chat/stream", json={"prompt": prompt}) as response:
        assert response.status_code == 200
        events = []
        for line in response.iter_lines():
            if line.startswith("data: "):
                payload = json.loads(line[6:])
                events.append(payload)

        # Must have at least token events and a done event
        done_events = [e for e in events if e.get("event") == "done"]
        assert len(done_events) >= 1
        done_payload = done_events[0]
        assert "full_text" in done_payload
        assert len(done_payload["full_text"]) > 0


def test_switch_model_endpoint(client):
    """Test /api/model switches the bot model and reflects in health check."""
    res = client.post("/api/model", json={"model": "jesse-pristine"})
    assert res.status_code == 200
    assert res.json()["model"] == "jesse-pristine"

    health = client.get("/api/health").json()
    assert health["model"] == "jesse-pristine"

    # Switch back to default
    res2 = client.post("/api/model", json={"model": "jesse-prod"})
    assert res2.status_code == 200
    assert res2.json()["model"] == "jesse-prod"
