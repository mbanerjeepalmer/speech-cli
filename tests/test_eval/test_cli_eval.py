"""Tests for transcribe CLI commands."""

from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from speech_cli.eval.cli_eval import register_commands
from speech_cli.eval.providers.base import TranscriptionResult

# Build a test app with commands registered
_test_app = typer.Typer()
register_commands(_test_app)

runner = CliRunner()


def test_list_providers():
    result = runner.invoke(_test_app, ["list-providers"])
    assert result.exit_code == 0
    assert "whisper-cpp" in result.stdout


@patch("speech_cli.eval.cli_eval.run_single")
def test_transcribe_single_provider(mock_run, tmp_path):
    audio = tmp_path / "test.wav"
    audio.write_bytes(b"fake audio")

    mock_tr_run = MagicMock()
    mock_tr_run.run_dir = tmp_path / "runs" / "test_run"
    mock_result = TranscriptionResult(
        provider_name="whisper-cpp",
        model_name="tiny",
        text="hello world",
        processing_time_seconds=1.0,
    )
    mock_run.return_value = (mock_tr_run, mock_result)

    result = runner.invoke(_test_app, ["transcribe", str(audio), "-p", "whisper-cpp"])
    assert result.exit_code == 0


def test_show_missing_dir():
    result = runner.invoke(_test_app, ["show", "/nonexistent/path"])
    assert result.exit_code != 0


@patch("speech_cli.eval.cli_eval.TranscriptionRun")
def test_show_valid_run(mock_run_cls, tmp_path):
    mock_run_cls.load_run.return_value = {
        "metadata": {"created": "2026-01-01", "providers": ["test"]},
        "results": {
            "test_model": {
                "text": "hello",
                "processing_time_seconds": 1.0,
            }
        },
    }

    result = runner.invoke(_test_app, ["show", str(tmp_path)])
    assert result.exit_code == 0


def test_help():
    result = runner.invoke(_test_app, ["--help"])
    assert result.exit_code == 0
    assert "transcribe" in result.stdout.lower()


def test_transcribe_help():
    result = runner.invoke(_test_app, ["transcribe", "--help"])
    assert result.exit_code == 0
    assert "audio" in result.stdout.lower()


@patch("speech_cli.eval.cli_eval._run_mic_mode")
def test_transcribe_no_file_defaults_to_mic(mock_mic_mode):
    """No audio file defaults to mic mode."""
    result = runner.invoke(_test_app, ["transcribe"])
    assert result.exit_code == 0
    mock_mic_mode.assert_called_once()


def test_transcribe_mic_and_file():
    """Cannot use both --mic and an audio file."""
    result = runner.invoke(_test_app, ["transcribe", "test.wav", "--mic"])
    assert result.exit_code != 0


def test_transcribe_sync_not_implemented():
    """--sync flag raises NotImplementedError."""
    result = runner.invoke(_test_app, ["transcribe", "test.wav", "--sync"])
    assert result.exit_code != 0


def test_transcribe_help_shows_mic():
    result = runner.invoke(_test_app, ["transcribe", "--help"])
    assert "--mic" in result.stdout
