"""Tests for ChunkedStreamingAdapter."""

import struct
import time
from unittest.mock import MagicMock

from speech_cli.eval.audio.chunked_adapter import ChunkedStreamingAdapter
from speech_cli.eval.providers.base import TranscriptionResult


def _make_pcm_chunk(n_samples=1600, amplitude=1000):
    return struct.pack(f"<{n_samples}h", *([amplitude] * n_samples))


def _mock_provider(name="test", model="test-model", text="hello world"):
    provider = MagicMock()
    provider.name = name
    provider.model_name = model
    provider.transcribe_file.return_value = TranscriptionResult(
        provider_name=name,
        model_name=model,
        text=text,
    )
    return provider


def test_start_streaming_resets_state():
    provider = _mock_provider()
    adapter = ChunkedStreamingAdapter(provider, chunk_interval=5.0)

    adapter.start_streaming()
    assert adapter._accumulated_text == ""
    assert len(adapter._buffer) == 0


def test_send_audio_accumulates():
    provider = _mock_provider()
    adapter = ChunkedStreamingAdapter(provider, chunk_interval=999.0)
    adapter.start_streaming()

    chunk = _make_pcm_chunk()
    adapter.send_audio(chunk)
    adapter.send_audio(chunk)

    assert len(adapter._buffer) == len(chunk) * 2
    # Should not have called transcribe yet (interval not reached)
    provider.transcribe_file.assert_not_called()


def test_flush_on_interval():
    provider = _mock_provider(text="partial result")
    adapter = ChunkedStreamingAdapter(provider, chunk_interval=0.0)
    adapter.start_streaming()

    partials = []
    adapter.on_partial(lambda text: partials.append(text))

    chunk = _make_pcm_chunk()
    adapter.send_audio(chunk)

    # With interval=0, should flush immediately
    provider.transcribe_file.assert_called_once()
    assert partials == ["partial result"]


def test_stop_streaming_returns_result():
    provider = _mock_provider(text="final text")
    adapter = ChunkedStreamingAdapter(provider, chunk_interval=999.0)
    adapter.start_streaming()

    chunk = _make_pcm_chunk()
    adapter.send_audio(chunk)

    result = adapter.stop_streaming()
    assert result.text == "final text"
    assert result.provider_name == "test"
    assert result.model_name == "test-model"
    provider.transcribe_file.assert_called_once()


def test_stop_streaming_empty_buffer():
    provider = _mock_provider()
    adapter = ChunkedStreamingAdapter(provider, chunk_interval=999.0)
    adapter.start_streaming()

    result = adapter.stop_streaming()
    assert result.text == ""
    provider.transcribe_file.assert_not_called()


def test_name_and_model_delegated():
    provider = _mock_provider(name="groq", model="whisper-large")
    adapter = ChunkedStreamingAdapter(provider)
    assert adapter.name == "groq"
    assert adapter.model_name == "whisper-large"


def test_transcription_error_does_not_crash():
    provider = _mock_provider()
    provider.transcribe_file.side_effect = RuntimeError("API error")

    adapter = ChunkedStreamingAdapter(provider, chunk_interval=0.0)
    adapter.start_streaming()

    chunk = _make_pcm_chunk()
    adapter.send_audio(chunk)  # Should not raise

    result = adapter.stop_streaming()
    assert result.text == ""  # No successful transcription


def test_accumulated_text_updates():
    """Subsequent flushes update the accumulated text."""
    provider = _mock_provider()
    adapter = ChunkedStreamingAdapter(provider, chunk_interval=0.0)
    adapter.start_streaming()

    provider.transcribe_file.return_value = TranscriptionResult(
        provider_name="test", model_name="m", text="hello"
    )
    adapter.send_audio(_make_pcm_chunk())

    provider.transcribe_file.return_value = TranscriptionResult(
        provider_name="test", model_name="m", text="hello world"
    )
    adapter.send_audio(_make_pcm_chunk())

    result = adapter.stop_streaming()
    # Final flush re-transcribes everything
    assert "hello" in result.text
