"""Tests for the online execution backend (hosted Code Runner / JDoodle service).

All HTTP traffic is mocked, so these tests never touch the network.
"""

import pytest

import executor as executor_module
from executor import (
    DEFAULT_ONLINE_COMPILER_URL,
    CodeExecutor,
)


def install_fake_post(monkeypatch, responses):
    """Installs a fake _post_online_compiler and records every request it receives."""
    calls = []

    def fake_post(url, payload, timeout):
        calls.append({"url": url, "payload": payload, "timeout": timeout})
        return responses.pop(0)

    monkeypatch.setattr(executor_module, "_post_online_compiler", fake_post)
    return calls


def test_online_success(monkeypatch):
    calls = install_fake_post(monkeypatch, [(200, {"output": "42\n", "statusCode": "0"})])
    ex = CodeExecutor(execution_backend="online")
    result = ex.execute_code("print(6*7)", language="cpp", backend="online")

    assert result.is_success
    assert result.stdout == "42\n"
    assert result.exit_code == 0
    assert calls[0]["url"] == f"{DEFAULT_ONLINE_COMPILER_URL}/run_code"
    assert calls[0]["payload"]["code"] == "print(6*7)"
    assert calls[0]["payload"]["language"] == "cpp"


def test_online_compile_error_is_not_success(monkeypatch):
    install_fake_post(
        monkeypatch,
        [(200, {"output": "main.cpp:3:1: error: expected ';' before '}'", "statusCode": "1"})],
    )
    ex = CodeExecutor(execution_backend="online")
    result = ex.execute_code("int main() { return 0 }", language="cpp", backend="online")

    assert not result.is_success
    assert result.exit_code == 1
    assert "error" in result.stdout


def test_online_wrapped_result_shape_is_parsed(monkeypatch):
    install_fake_post(monkeypatch, [(200, {"result": {"output": "hello\n"}})])
    ex = CodeExecutor(execution_backend="online")
    result = ex.execute_code("print('hello')", language="python", backend="online")

    assert result.stdout == "hello\n"
    assert result.exit_code == 0


def test_stdin_is_forwarded_to_the_service(monkeypatch):
    calls = install_fake_post(monkeypatch, [(200, {"output": "120\n", "statusCode": "0"})])
    ex = CodeExecutor(execution_backend="online")
    ex.execute_code("print(int(input())**2)", language="cpp", stdin_data="12\n", backend="online")

    assert calls[0]["payload"]["input"] == "12\n"


def test_compile_only_flag_is_forwarded(monkeypatch):
    calls = install_fake_post(monkeypatch, [(200, {"output": "", "statusCode": "0"})])
    ex = CodeExecutor(execution_backend="online")
    ex.execute_code("int main(){}", language="cpp", backend="online", compile_only=True)

    assert calls[0]["payload"]["compileOnly"] is True


def test_python_stays_local_even_in_online_backend(monkeypatch):
    def explode(url, payload, timeout):
        raise AssertionError("python must not be routed to the online compiler")

    monkeypatch.setattr(executor_module, "_post_online_compiler", explode)
    ex = CodeExecutor(execution_backend="online")
    result = ex.execute_code("print('local')", language="python", backend="online")

    assert result.is_success
    assert result.stdout.strip() == "local"


def test_default_backend_is_local_and_makes_no_requests(monkeypatch):
    def explode(url, payload, timeout):
        raise AssertionError("local backend must not call the online compiler")

    monkeypatch.setattr(executor_module, "_post_online_compiler", explode)
    ex = CodeExecutor()
    result = ex.execute_code("print('local')", language="python")

    assert result.is_success


def test_backend_falls_back_to_environment(monkeypatch):
    monkeypatch.setenv("JESSE_EXECUTION_BACKEND", "online")
    ex = CodeExecutor()
    assert ex.execution_backend == "online"


def test_invalid_backend_falls_back_to_local(monkeypatch):
    monkeypatch.delenv("JESSE_EXECUTION_BACKEND", raising=False)
    ex = CodeExecutor(execution_backend="carrier-pigeon")
    assert ex.execution_backend == "local"


def test_language_aliases_are_routed_online(monkeypatch):
    calls = install_fake_post(monkeypatch, [(200, {"output": "ok\n", "statusCode": "0"})])
    ex = CodeExecutor(execution_backend="online")
    ex.execute_code("int main(){}", language="C++", backend="online")

    assert calls[0]["payload"]["language"] == "c++"


def test_http_error_is_reported_as_failure(monkeypatch):
    install_fake_post(monkeypatch, [(500, {"error": "internal compiler error"})])
    ex = CodeExecutor(execution_backend="online")
    result = ex.execute_code("int main(){}", language="cpp", backend="online")

    assert not result.is_success
    assert result.error is not None and "HTTP 500" in result.error
