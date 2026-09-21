"""Tests for JesseConfig validation and default parameters."""

import pytest
from jesse_coder.config import JesseConfig, DEFAULT_API_KEY, DEFAULT_BASE_URL, DEFAULT_MODEL
from jesse_coder.exceptions import JesseConfigError


def test_default_config():
    cfg = JesseConfig()
    cfg.validate()
    assert cfg.api_key == DEFAULT_API_KEY
    assert cfg.base_url == DEFAULT_BASE_URL
    assert cfg.model == DEFAULT_MODEL
    assert cfg.temperature == 0.2
    assert cfg.max_retries == 2
    assert "software engineer" in cfg.system_prompt.lower()


def test_invalid_api_key():
    cfg = JesseConfig(api_key="")
    with pytest.raises(JesseConfigError, match="API key cannot be empty"):
        cfg.validate()


def test_invalid_base_url():
    cfg = JesseConfig(base_url="ftp://invalid-host")
    with pytest.raises(JesseConfigError, match="Invalid base_url"):
        cfg.validate()


def test_invalid_temperature():
    cfg = JesseConfig(temperature=2.5)
    with pytest.raises(JesseConfigError, match="Temperature must be between 0.0 and 2.0"):
        cfg.validate()

    cfg2 = JesseConfig(temperature=-0.1)
    with pytest.raises(JesseConfigError, match="Temperature must be between 0.0 and 2.0"):
        cfg2.validate()


def test_invalid_timeout():
    cfg = JesseConfig(timeout=0)
    with pytest.raises(JesseConfigError, match="Timeout must be positive"):
        cfg.validate()


def test_invalid_max_retries():
    cfg = JesseConfig(max_retries=-1)
    with pytest.raises(JesseConfigError, match="max_retries cannot be negative"):
        cfg.validate()


def test_from_env_override(monkeypatch):
    monkeypatch.setenv("JESSE_API_KEY", "custom_key_123")
    monkeypatch.setenv("JESSE_MODEL", "jesse-pristine")
    monkeypatch.setenv("JESSE_TEMPERATURE", "0.5")

    cfg = JesseConfig.from_env()
    assert cfg.api_key == "custom_key_123"
    assert cfg.model == "jesse-pristine"
    assert cfg.temperature == 0.5
