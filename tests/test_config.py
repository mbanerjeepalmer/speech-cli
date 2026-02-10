"""Tests for config module."""

import os
import tempfile
from pathlib import Path

import pytest

from speech_cli.config import get_api_key, validate_api_key
from speech_cli.errors import ConfigurationError


def test_get_api_key_from_cli_arg():
    """Test that CLI argument takes priority."""
    api_key = get_api_key(cli_key="cli_key")
    assert api_key == "cli_key"


def test_get_api_key_from_env_var(monkeypatch):
    """Test that environment variable works."""
    monkeypatch.setenv("ELEVENLABS_API_KEY", "env_key")
    api_key = get_api_key()
    assert api_key == "env_key"


def test_get_api_key_not_found(monkeypatch, tmp_path):
    """Test that missing API key raises ConfigurationError."""
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ConfigurationError, match="API key not found"):
        get_api_key()


def test_validate_api_key_valid():
    """Test that valid API keys pass validation."""
    validate_api_key("valid_api_key_123")  # Should not raise


def test_validate_api_key_empty():
    """Test that empty API keys raise ConfigurationError."""
    with pytest.raises(ConfigurationError, match="cannot be empty"):
        validate_api_key("")

    with pytest.raises(ConfigurationError, match="cannot be empty"):
        validate_api_key("   ")


def test_validate_api_key_too_short():
    """Test that short API keys raise ConfigurationError."""
    with pytest.raises(ConfigurationError, match="too short"):
        validate_api_key("short")
