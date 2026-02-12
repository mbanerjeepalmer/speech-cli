"""Tests for the eval runner."""

from unittest.mock import MagicMock, patch

import pytest

from speech_cli.eval.providers.base import TranscriptionResult, TranscriptionSegment
from speech_cli.eval.runner import run_single, run_parallel


MOCK_RESULT = TranscriptionResult(
    provider_name="whisper-cpp",
    model_name="ggml-tiny-en",
    text="test transcription",
    segments=[TranscriptionSegment(text="test", start=0.0, end=1.0)],
    processing_time_seconds=0.5,
)


@patch("speech_cli.eval.runner._ensure_wav_16k", side_effect=lambda f: f)
@patch("speech_cli.eval.runner.get_provider")
def test_run_single(mock_get_provider, mock_ensure, tmp_path):
    # Setup
    audio = tmp_path / "test.wav"
    audio.write_bytes(b"fake audio")

    mock_provider = MagicMock()
    mock_provider.name = "whisper-cpp"
    mock_provider.model_name = "ggml-tiny-en"
    mock_provider.transcribe_file.return_value = MOCK_RESULT
    mock_get_provider.return_value = mock_provider

    eval_run, result = run_single(
        str(audio), "whisper-cpp", base_dir=tmp_path / "runs"
    )

    assert result.text == "test transcription"
    assert eval_run.run_dir.exists()
    mock_provider.validate_config.assert_called_once()
    mock_provider.transcribe_file.assert_called_once_with(str(audio))


@patch("speech_cli.eval.runner._ensure_wav_16k", side_effect=lambda f: f)
@patch("speech_cli.eval.runner.get_provider")
def test_run_parallel_multiple(mock_get_provider, mock_ensure, tmp_path):
    audio = tmp_path / "test.wav"
    audio.write_bytes(b"fake audio")

    result1 = TranscriptionResult(
        provider_name="p1", model_name="m1", text="text1", processing_time_seconds=0.5
    )
    result2 = TranscriptionResult(
        provider_name="p2", model_name="m2", text="text2", processing_time_seconds=0.7
    )

    def make_provider(name, config=None):
        p = MagicMock()
        p.name = name
        p.model_name = f"{name}-model"
        if name == "p1":
            p.transcribe_file.return_value = result1
        else:
            p.transcribe_file.return_value = result2
        return p

    # parse_provider_spec returns (name, {}) for simple specs
    with patch("speech_cli.eval.runner.parse_provider_spec") as mock_parse:
        mock_parse.side_effect = lambda s: (s, {})
        mock_get_provider.side_effect = make_provider

        eval_run, results = run_parallel(
            str(audio),
            ["p1", "p2"],
            base_dir=tmp_path / "runs",
        )

    assert len(results) == 2
    texts = {r.text for r in results}
    assert "text1" in texts
    assert "text2" in texts


@patch("speech_cli.eval.runner._ensure_wav_16k", side_effect=lambda f: f)
@patch("speech_cli.eval.runner.get_provider")
def test_run_parallel_with_callback(mock_get_provider, mock_ensure, tmp_path):
    audio = tmp_path / "test.wav"
    audio.write_bytes(b"fake audio")

    mock_provider = MagicMock()
    mock_provider.name = "test"
    mock_provider.model_name = "m"
    mock_provider.transcribe_file.return_value = MOCK_RESULT

    with patch("speech_cli.eval.runner.parse_provider_spec") as mock_parse:
        mock_parse.return_value = ("test", {})
        mock_get_provider.return_value = mock_provider

        callback = MagicMock()
        eval_run, results = run_parallel(
            str(audio),
            ["test"],
            base_dir=tmp_path / "runs",
            display_callback=callback,
        )

    callback.assert_called_once()


@patch("speech_cli.eval.runner._ensure_wav_16k", side_effect=lambda f: f)
@patch("speech_cli.eval.runner.get_provider")
def test_run_parallel_provider_failure(mock_get_provider, mock_ensure, tmp_path):
    audio = tmp_path / "test.wav"
    audio.write_bytes(b"fake audio")

    mock_provider = MagicMock()
    mock_provider.name = "failing"
    mock_provider.model_name = "m"
    mock_provider.transcribe_file.side_effect = RuntimeError("boom")

    with patch("speech_cli.eval.runner.parse_provider_spec") as mock_parse:
        mock_parse.return_value = ("failing", {})
        mock_get_provider.return_value = mock_provider

        eval_run, results = run_parallel(
            str(audio),
            ["failing"],
            base_dir=tmp_path / "runs",
        )

    # Should not raise, but results should be empty
    assert len(results) == 0
