"""Tests for CLI module."""

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
    assert "transcribe" in result.stdout.lower()
    assert "list-providers" in result.stdout.lower()
    assert "show" in result.stdout.lower()


def test_list_providers():
    """Test list-providers from top level."""
    result = runner.invoke(app, ["list-providers"])
    assert result.exit_code == 0
    assert "whisper-cpp" in result.stdout
