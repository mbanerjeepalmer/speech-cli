"""Tests for MicRecorder."""

import struct
import time
import wave
from unittest.mock import MagicMock, patch

import pytest

from speech_cli.eval.audio.recorder import MicRecorder


def _make_pcm_chunk(n_samples=1600, amplitude=1000):
    """Create a PCM int16 chunk with a constant amplitude."""
    return struct.pack(f"<{n_samples}h", *([amplitude] * n_samples))


def test_compute_rms_silence():
    silence = b"\x00" * 3200  # 1600 samples of silence
    rms = MicRecorder._compute_rms(silence)
    assert rms == 0.0


def test_compute_rms_nonzero():
    chunk = _make_pcm_chunk(amplitude=16384)  # half max
    rms = MicRecorder._compute_rms(chunk)
    assert 0.49 < rms < 0.51


def test_compute_rms_empty():
    assert MicRecorder._compute_rms(b"") == 0.0
    assert MicRecorder._compute_rms(b"\x00") == 0.0


def test_audio_callback_accumulates_buffer():
    recorder = MicRecorder()
    recorder._start_time = time.monotonic()

    chunk = _make_pcm_chunk()
    recorder._audio_callback(chunk, 1600, None, None)
    recorder._audio_callback(chunk, 1600, None, None)

    assert len(recorder._buffer) == len(chunk) * 2


def test_audio_callback_calls_on_audio():
    received = []
    recorder = MicRecorder(on_audio=lambda c: received.append(c))
    recorder._start_time = time.monotonic()

    chunk = _make_pcm_chunk()
    recorder._audio_callback(chunk, 1600, None, None)

    assert len(received) == 1
    assert received[0] == chunk


def test_audio_callback_calls_level_callback():
    levels = []
    recorder = MicRecorder(level_callback=lambda rms: levels.append(rms))
    recorder._start_time = time.monotonic()

    chunk = _make_pcm_chunk(amplitude=16384)
    recorder._audio_callback(chunk, 1600, None, None)

    assert len(levels) == 1
    assert 0.49 < levels[0] < 0.51


def test_save_wav(tmp_path):
    recorder = MicRecorder()
    recorder._start_time = time.monotonic()

    chunk = _make_pcm_chunk(n_samples=16000)  # 1 second
    recorder._audio_callback(chunk, 16000, None, None)

    wav_path = str(tmp_path / "test.wav")
    result = recorder.save_wav(wav_path)

    assert result == wav_path
    with wave.open(wav_path, "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 16000
        assert wf.getsampwidth() == 2
        assert wf.getnframes() == 16000


def test_save_wav_creates_parent_dirs(tmp_path):
    recorder = MicRecorder()
    wav_path = str(tmp_path / "subdir" / "deep" / "test.wav")
    recorder.save_wav(wav_path)
    assert (tmp_path / "subdir" / "deep" / "test.wav").exists()


@patch("speech_cli.eval.audio.recorder.sd", create=True)
def test_start_creates_stream(mock_sd):
    """Test that start() creates and starts a RawInputStream."""
    mock_stream = MagicMock()

    with patch("sounddevice.RawInputStream", return_value=mock_stream):
        recorder = MicRecorder()
        recorder.start()

        assert recorder._stream is mock_stream
        mock_stream.start.assert_called_once()
        assert recorder.is_recording

        recorder.stop()
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()
        assert not recorder.is_recording


def test_max_duration_auto_stop():
    """Audio callback sets stop event when max duration exceeded."""
    recorder = MicRecorder(max_duration=0.0)
    recorder._start_time = 0.0  # far in the past

    chunk = _make_pcm_chunk()
    recorder._audio_callback(chunk, 1600, None, None)

    assert recorder._stop_event.is_set()


def test_stopped_callback_ignored():
    """Audio callback does nothing after stop event is set."""
    received = []
    recorder = MicRecorder(on_audio=lambda c: received.append(c))
    recorder._start_time = time.monotonic()
    recorder._stop_event.set()

    chunk = _make_pcm_chunk()
    recorder._audio_callback(chunk, 1600, None, None)

    assert len(received) == 0
