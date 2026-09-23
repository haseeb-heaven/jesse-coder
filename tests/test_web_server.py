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


def test_settings_endpoints(client):
    """Test /api/settings GET and POST and mask behavior."""
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert "has_api_key" in data
    assert "api_key_masked" in data
    assert "base_url" in data
    assert "model" in data

    # Update model via settings
    update_res = client.post("/api/settings", json={"model": "jesse-prod"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "ok"


def test_settings_verify_endpoint(client):
    """Test /api/settings/verify rejects invalid keys."""
    res = client.post("/api/settings/verify", json={"api_key": "jesse_live_badkey999"})
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert "error" in data


def test_testing_datasets_endpoint(client):
    """Test /api/testing/datasets returns both datasets."""
    res = client.get("/api/testing/datasets")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    datasets = data["datasets"]
    assert len(datasets) == 2
    filenames = [d["filename"] for d in datasets]
    assert "task_bug_issues.json" in filenames
    assert "tasks_code_generation.json" in filenames


def test_testing_tasks_endpoint(client):
    """Test /api/testing/tasks returns tasks from task_bug_issues.json."""
    res = client.get("/api/testing/tasks?dataset=task_bug_issues.json")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["count"] == 10
    assert len(data["tasks"]) == 10
    task_0 = data["tasks"][0]
    assert "id" in task_0
    assert "buggy_code" in task_0
    assert "expected_output" in task_0


def test_testing_reports_endpoints(client):
    """Test /api/testing/reports lists reports from testing/reports/."""
    res = client.get("/api/testing/reports")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert isinstance(data["reports"], list)


def test_benchmarks_button_and_modal_in_index(client):
    """Test index HTML includes benchmarks button and modal."""
    res = client.get("/")
    assert res.status_code == 200
    assert "btn-benchmarks" in res.text
    assert "benchmarks-modal" in res.text
    assert "bench-dataset-select" in res.text


