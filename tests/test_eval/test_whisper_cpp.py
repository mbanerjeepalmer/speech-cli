"""Tests for whisper.cpp provider (mocked subprocess)."""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from speech_cli.eval.providers.whisper_cpp import WhisperCppProvider, _ts_to_seconds


@pytest.fixture
def provider():
    return WhisperCppProvider(binary="/tmp/fake_whisper", model="/tmp/fake_model.bin")


def test_name_and_model(provider):
    assert provider.name == "whisper-cpp"
    assert provider.model_name == "fake_model"


def test_validate_config_missing_binary():
    p = WhisperCppProvider(binary="/nonexistent/binary", model="/tmp/fake.bin")
    with pytest.raises(RuntimeError, match="binary not found"):
        p.validate_config()


def test_validate_config_missing_model(tmp_path):
    binary = tmp_path / "main"
    binary.touch()
    p = WhisperCppProvider(binary=str(binary), model="/nonexistent/model.bin")
    with pytest.raises(RuntimeError, match="model not found"):
        p.validate_config()


def test_validate_config_success(tmp_path):
    binary = tmp_path / "main"
    binary.touch()
    model = tmp_path / "model.bin"
    model.touch()
    p = WhisperCppProvider(binary=str(binary), model=str(model))
    p.validate_config()  # should not raise


def test_supports_diarization_default(provider):
    assert provider.supports_diarization() is False


def test_supports_diarization_enabled():
    p = WhisperCppProvider(
        binary="/tmp/b", model="/tmp/m", diarize=True
    )
    assert p.supports_diarization() is True


def test_transcribe_file_not_found(provider):
    with pytest.raises(FileNotFoundError):
        provider.transcribe_file("/nonexistent/audio.wav")


SAMPLE_WHISPER_JSON = {
    "transcription": [
        {
            "timestamps": {"from": "00:00:00.000", "to": "00:00:05.000"},
            "text": "And so my fellow Americans",
        },
        {
            "timestamps": {"from": "00:00:05.000", "to": "00:00:11.000"},
            "text": "ask not what your country can do for you",
        },
    ]
}


@patch("speech_cli.eval.providers.whisper_cpp.subprocess.run")
def test_transcribe_file_success(mock_run, provider, tmp_path):
    # Create a fake audio file
    audio = tmp_path / "test.wav"
    audio.touch()

    # Mock subprocess to succeed
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    # Mock the JSON output file creation
    def side_effect(*args, **kwargs):
        # Find the output prefix from the command args
        cmd = args[0]
        of_idx = cmd.index("-of")
        prefix = cmd[of_idx + 1]
        json_path = Path(f"{prefix}.json")
        json_path.write_text(json.dumps(SAMPLE_WHISPER_JSON))
        return MagicMock(returncode=0, stdout="", stderr="")

    mock_run.side_effect = side_effect

    result = provider.transcribe_file(str(audio))

    assert result.provider_name == "whisper-cpp"
    assert "fellow Americans" in result.text
    assert len(result.segments) == 2
    assert result.segments[0].start == 0.0
    assert result.segments[0].end == 5.0
    assert result.processing_time_seconds is not None


@patch("speech_cli.eval.providers.whisper_cpp.subprocess.run")
def test_transcribe_file_nonzero_exit(mock_run, provider, tmp_path):
    audio = tmp_path / "test.wav"
    audio.touch()

    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error occurred")

    with pytest.raises(RuntimeError, match="exited with code 1"):
        provider.transcribe_file(str(audio))


def test_ts_to_seconds():
    assert _ts_to_seconds("00:00:00.000") == 0.0
    assert _ts_to_seconds("00:01:30.500") == 90.5
    assert _ts_to_seconds("01:00:00.000") == 3600.0
    assert _ts_to_seconds("invalid") == 0.0


def test_env_var_override(monkeypatch):
    monkeypatch.setenv("WHISPER_CPP_BINARY", "/custom/binary")
    monkeypatch.setenv("WHISPER_CPP_MODEL", "/custom/model.bin")
    p = WhisperCppProvider()
    assert p.binary == "/custom/binary"
    assert p.model == "/custom/model.bin"
