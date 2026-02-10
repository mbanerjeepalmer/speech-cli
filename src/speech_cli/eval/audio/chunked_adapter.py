"""Chunked streaming adapter for batch-only transcription providers."""

import tempfile
import threading
import time
import wave
from typing import Callable, Optional

from speech_cli.eval.providers.base import (
    TranscriptionProvider,
    TranscriptionResult,
)


class ChunkedStreamingAdapter:
    """Wraps a batch TranscriptionProvider to provide near-live streaming.

    Accumulates audio chunks. Every `chunk_interval` seconds, writes
    accumulated audio to a temp WAV, calls provider.transcribe_file(),
    and fires the partial callback with the result text.
    """

    SAMPLE_RATE = 16000
    CHANNELS = 1

    def __init__(
        self,
        provider: TranscriptionProvider,
        chunk_interval: float = 5.0,
    ) -> None:
        self._provider = provider
        self._chunk_interval = chunk_interval

        self._buffer = bytearray()
        self._lock = threading.Lock()
        self._partial_callback: Optional[Callable[[str], None]] = None
        self._start_time: Optional[float] = None
        self._last_flush_time: Optional[float] = None
        self._accumulated_text = ""
        self._stop_event = threading.Event()

    @property
    def name(self) -> str:
        return self._provider.name

    @property
    def model_name(self) -> str:
        return self._provider.model_name

    def on_partial(self, callback: Callable[[str], None]) -> None:
        self._partial_callback = callback

    def start_streaming(self) -> None:
        self._buffer = bytearray()
        self._accumulated_text = ""
        self._start_time = time.monotonic()
        self._last_flush_time = self._start_time
        self._stop_event.clear()

    def send_audio(self, chunk: bytes) -> None:
        with self._lock:
            self._buffer.extend(chunk)

        now = time.monotonic()
        if self._last_flush_time and (now - self._last_flush_time) >= self._chunk_interval:
            self._flush()

    def stop_streaming(self) -> TranscriptionResult:
        self._stop_event.set()
        self._flush()
        return TranscriptionResult(
            provider_name=self._provider.name,
            model_name=self._provider.model_name,
            text=self._accumulated_text,
            processing_time_seconds=(
                time.monotonic() - self._start_time if self._start_time else None
            ),
        )

    def _flush(self) -> None:
        """Write buffered audio to temp WAV and transcribe."""
        with self._lock:
            if not self._buffer:
                return
            audio_data = bytes(self._buffer)

        self._last_flush_time = time.monotonic()

        wav_path = self._write_temp_wav(audio_data)
        try:
            result = self._provider.transcribe_file(wav_path)
            self._accumulated_text = result.text
            if self._partial_callback:
                self._partial_callback(result.text)
        except Exception:
            pass  # Don't crash streaming on transcription errors

    @staticmethod
    def _write_temp_wav(audio_data: bytes) -> str:
        """Write PCM data to a temporary WAV file."""
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with wave.open(tmp.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data)
        return tmp.name
