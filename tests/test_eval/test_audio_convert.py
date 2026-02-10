"""Tests for audio conversion utilities."""

from unittest.mock import MagicMock, patch

import pytest

from speech_cli.eval.audio.convert import convert_to_wav_16k, is_wav_16k


@patch("speech_cli.eval.audio.convert.subprocess.run")
def test_convert_to_wav_16k_success(mock_run, tmp_path):
    input_file = tmp_path / "test.mp3"
    input_file.write_bytes(b"fake mp3")

    mock_run.return_value = MagicMock(returncode=0, stderr="")

    output = convert_to_wav_16k(str(input_file))
    assert output.endswith(".16k.wav")
    mock_run.assert_called_once()

    # Check ffmpeg args
    cmd = mock_run.call_args[0][0]
    assert "ffmpeg" in cmd[0]
    assert "-ar" in cmd
    assert "16000" in cmd


@patch("speech_cli.eval.audio.convert.subprocess.run")
def test_convert_to_wav_16k_failure(mock_run, tmp_path):
    input_file = tmp_path / "test.mp3"
    input_file.write_bytes(b"fake mp3")

    mock_run.return_value = MagicMock(returncode=1, stderr="error")

    with pytest.raises(RuntimeError, match="ffmpeg conversion failed"):
        convert_to_wav_16k(str(input_file))


@patch("speech_cli.eval.audio.convert.subprocess.run")
def test_convert_to_wav_16k_custom_output(mock_run, tmp_path):
    input_file = tmp_path / "test.mp3"
    input_file.write_bytes(b"fake")
    output_file = str(tmp_path / "custom.wav")

    mock_run.return_value = MagicMock(returncode=0, stderr="")

    result = convert_to_wav_16k(str(input_file), output_file)
    assert result == output_file


def test_convert_skips_if_output_newer(tmp_path):
    """If output exists and is newer than input, skip conversion."""
    input_file = tmp_path / "test.mp3"
    input_file.write_bytes(b"fake")

    output_file = tmp_path / "test.16k.wav"
    output_file.write_bytes(b"already converted")

    # Output is newer (same time or later), should skip
    result = convert_to_wav_16k(str(input_file))
    assert result == str(output_file)


@patch("speech_cli.eval.audio.convert.subprocess.run")
def test_is_wav_16k_true(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0, stdout="pcm_s16le,16000,1\n"
    )
    assert is_wav_16k("/tmp/test.wav") is True


@patch("speech_cli.eval.audio.convert.subprocess.run")
def test_is_wav_16k_false(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0, stdout="pcm_s16le,44100,2\n"
    )
    assert is_wav_16k("/tmp/test.wav") is False


@patch("speech_cli.eval.audio.convert.subprocess.run")
def test_is_wav_16k_ffprobe_fails(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="")
    assert is_wav_16k("/tmp/test.wav") is False
