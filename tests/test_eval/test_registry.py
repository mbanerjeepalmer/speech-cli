"""Tests for provider registry."""

import pytest

from speech_cli.eval.providers.registry import (
    get_provider,
    list_providers,
    parse_provider_spec,
)


def test_list_providers_returns_known_names():
    names = list_providers()
    assert "whisper-cpp" in names
    assert "elevenlabs" in names
    assert "groq" in names
    assert "mistral" in names
    assert "huggingface" in names


def test_list_providers_is_sorted():
    names = list_providers()
    assert names == sorted(names)


def test_get_provider_unknown_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("nonexistent")


def test_get_provider_whisper_cpp():
    p = get_provider("whisper-cpp")
    assert p.name == "whisper-cpp"


def test_get_provider_with_config():
    p = get_provider("whisper-cpp", {"binary": "/tmp/fake", "model": "/tmp/fake.bin"})
    assert p.binary == "/tmp/fake"
    assert p.model == "/tmp/fake.bin"


def test_parse_provider_spec_simple():
    name, config = parse_provider_spec("whisper-cpp")
    assert name == "whisper-cpp"
    assert config == {}


def test_parse_provider_spec_with_params():
    name, config = parse_provider_spec("whisper-cpp:diarize=true,model=/path/to/m")
    assert name == "whisper-cpp"
    assert config["diarize"] is True
    assert config["model"] == "/path/to/m"


def test_parse_provider_spec_boolean_false():
    _, config = parse_provider_spec("groq:flag=false")
    assert config["flag"] is False


def test_parse_provider_spec_bare_flag():
    _, config = parse_provider_spec("groq:verbose")
    assert config["verbose"] is True
