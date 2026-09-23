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
    """Test /api/testing/tasks returns tasks from task_bug_issues.json with difficulty filtering."""
    res = client.get("/api/testing/tasks?dataset=task_bug_issues.json")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["count"] >= 10
    assert len(data["tasks"]) == data["count"]
    task_0 = data["tasks"][0]
    assert "id" in task_0
    assert "buggy_code" in task_0
    assert "expected_output" in task_0
    assert "difficulty" in task_0

    # Test filtering by complexity
    res_easy = client.get("/api/testing/tasks?dataset=task_bug_issues.json&difficulty=easy")
    assert res_easy.status_code == 200
    data_easy = res_easy.json()
    assert data_easy["count"] > 0
    assert all(t["difficulty"] == "easy" for t in data_easy["tasks"])

    res_complex = client.get("/api/testing/tasks?dataset=task_bug_issues.json&difficulty=complex")
    assert res_complex.status_code == 200
    data_complex = res_complex.json()
    assert data_complex["count"] > 0
    assert all(t["difficulty"] == "complex" for t in data_complex["tasks"])


def test_testing_reports_endpoints(client):
    """Test /api/testing/reports lists reports from testing/reports/."""
    res = client.get("/api/testing/reports")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert isinstance(data["reports"], list)


def test_testing_datasets_endpoint_reports_current_counts(client):
    response = client.get("/api/testing/datasets")
    assert response.status_code == 200
    datasets = {item["id"]: item for item in response.json()["datasets"]}
    assert datasets["tasks_code_generation.json"]["task_count"] == 45
    assert datasets["tasks_code_generation.json"]["difficulty_counts"] == {
        "easy": 15, "medium": 15, "complex": 15
    }
    assert datasets["task_bug_issues.json"]["task_count"] == 33
    assert datasets["task_bug_issues.json"]["difficulty_counts"] == {
        "easy": 11, "medium": 11, "complex": 11
    }


def test_benchmarks_button_and_modal_in_index(client):
    """Test index HTML includes benchmarks button and modal."""
    res = client.get("/")
    assert res.status_code == 200
    assert "btn-benchmarks" in res.text
    assert "benchmarks-modal" in res.text
    assert "bench-dataset-select" in res.text


def test_byok_vercel_mode_health(client, monkeypatch):
    """Test that Vercel runtime operates in pure BYOK mode with zero default keys."""
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("JESSE_API_KEY", raising=False)

    # 1. Without header: no key
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["has_api_key"] is False
    assert data["api_key_masked"] == ""
    assert data["is_vercel"] is True
    assert data["byok_mode"] is True

    # 2. With client header: isolated to that request
    res_keyed = client.get("/api/health", headers={"X-Jesse-Api-Key": "jesse_user_custom_key_1234"})
    assert res_keyed.status_code == 200
    data_keyed = res_keyed.json()
    assert data_keyed["has_api_key"] is True
    assert data_keyed["api_key_masked"].startswith("jesse_us")
    assert data_keyed["api_key_masked"].endswith("1234")

    # 3. Subsequent request without header still has no key (zero state bleed)
    res_again = client.get("/api/health")
    assert res_again.json()["has_api_key"] is False


def test_byok_banner_in_index(client):
    """Test that index HTML contains the BYOK notification banner."""
    res = client.get("/")
    assert res.status_code == 200
    assert "byok-banner" in res.text
    assert "Bring Your Own Key" in res.text


