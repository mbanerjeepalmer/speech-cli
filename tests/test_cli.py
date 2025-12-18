"""Tests for CLI module."""

import tempfile

from typer.testing import CliRunner

from speech_cli.cli import app

runner = CliRunner()


def test_cli_version():
    """Test --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "speech-cli version" in result.stdout


def test_cli_help():
    """Test --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Transcribe an audio file" in result.stdout
    assert "AUDIO_FILE" in result.stdout


def test_cli_missing_file():
    """Test with missing audio file."""
    result = runner.invoke(app, ["nonexistent.mp3", "--api-key", "test_key"])
    assert result.exit_code != 0


def test_cli_invalid_format():
    """Test with invalid output format."""
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        result = runner.invoke(
            app, [f.name, "--format", "invalid", "--api-key", "test_key"]
        )
        assert result.exit_code != 0
