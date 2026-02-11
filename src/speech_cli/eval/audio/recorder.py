"""Microphone recording with live audio streaming."""

import math
import struct
import threading
import time
import wave
from pathlib import Path
from typing import Callable, Optional


class MicRecorder:
    """Records from the microphone and streams PCM chunks to callbacks.

    Uses sounddevice.RawInputStream at 16kHz mono int16.
    Audio is streamed via on_audio callbacks and also accumulated
    for writing a complete WAV file on stop().
    """

    SAMPLE_RATE = 16000
    CHANNELS = 1
    DTYPE = "int16"
    BLOCK_SIZE = 1600  # 100ms at 16kHz

    def __init__(
        self,
        on_audio: Optional[Callable[[bytes], None]] = None,
        level_callback: Optional[Callable[[float], None]] = None,
        max_duration: float = 300.0,
        gain: float = 1.0,
    ) -> None:
        self._on_audio = on_audio
        self._level_callback = level_callback
        self._max_duration = max_duration
        self._gain = gain

        self._buffer = bytearray()
        self._lock = threading.Lock()
        self._stream = None
        self._start_time: Optional[float] = None
        self._stop_event = threading.Event()
        self._stopped = False

    def _audio_callback(self, indata: bytes, frames: int, time_info, status) -> None:
        """Called by sounddevice on each audio block."""
        if self._stop_event.is_set():
            return

        if self._gain != 1.0:
            indata = self._apply_gain(indata)

        with self._lock:
            self._buffer.extend(indata)

        if self._on_audio:
            self._on_audio(bytes(indata))

        if self._level_callback:
            rms = self._compute_rms(indata)
            self._level_callback(rms)

        # Auto-stop on max duration
        if self._start_time is not None and (time.monotonic() - self._start_time) >= self._max_duration:
            self._stop_event.set()

    def _apply_gain(self, data: bytes) -> bytes:
        """Apply gain multiplier to PCM int16 data with clamping."""
        n_samples = len(data) // 2
        samples = struct.unpack(f"<{n_samples}h", data[:n_samples * 2])
        gained = []
        for s in samples:
            v = int(s * self._gain)
            v = max(-32768, min(32767, v))
            gained.append(v)
        return struct.pack(f"<{n_samples}h", *gained)

    @staticmethod
    def _compute_rms(data: bytes) -> float:
        """Compute RMS level from PCM int16 data."""
        if len(data) < 2:
            return 0.0
        n_samples = len(data) // 2
        samples = struct.unpack(f"<{n_samples}h", data[:n_samples * 2])
        if not samples:
            return 0.0
        sum_sq = sum(s * s for s in samples)
        return math.sqrt(sum_sq / n_samples) / 32768.0

    def start(self) -> None:
        """Start recording from the microphone."""
        import sounddevice as sd

        self._stop_event.clear()
        self._stopped = False
        self._buffer = bytearray()
        self._start_time = time.monotonic()

        self._stream = sd.RawInputStream(
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype=self.DTYPE,
            blocksize=self.BLOCK_SIZE,
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self) -> None:
        """Stop recording."""
        self._stop_event.set()
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._stopped = True

    @property
    def elapsed(self) -> float:
        """Elapsed recording time in seconds."""
        if self._start_time is None:
            return 0.0
        if self._stopped:
            return self._stop_event is not None and time.monotonic() - self._start_time or 0.0
        return time.monotonic() - self._start_time

    @property
    def is_recording(self) -> bool:
        return self._stream is not None and not self._stop_event.is_set()

    def save_wav(self, path: str) -> str:
        """Write the accumulated audio buffer to a WAV file.

        Args:
            path: Output WAV file path.

        Returns:
            The path written to.
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            audio_data = bytes(self._buffer)

        with wave.open(path, "wb") as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(2)  # int16 = 2 bytes
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(audio_data)

        return path
