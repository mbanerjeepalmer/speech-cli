"""Mistral transcription provider (Voxtral)."""

import asyncio
import os
import threading
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Callable, Optional

from speech_cli.eval.providers.base import (
    StreamingTranscriptionProvider,
    TranscriptionResult,
    TranscriptionSegment,
)

SAMPLE_RATE = 16000
STREAMING_MODEL = "voxtral-mini-transcribe-realtime-2602"


class MistralProvider(StreamingTranscriptionProvider):
    """Transcription via Mistral API (Voxtral models).

    Supports both batch file transcription and real-time streaming
    via the realtime transcribe_stream WebSocket API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "voxtral-mini-latest",
        language: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        self.model = model
        self.language = language
        self.name = "mistral"
        self.model_name = model

        self._partial_callback: Optional[Callable[[str], None]] = None
        self._accumulated_text = ""
        self._start_time: Optional[float] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._audio_queue: Optional[asyncio.Queue] = None
        self._stream_task: Optional[asyncio.Task] = None

    def validate_config(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "Mistral API key not set. "
                "Set MISTRAL_API_KEY env var or pass api_key."
            )
        try:
            import mistralai  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "mistralai package not installed. Install with: uv pip install 'mistralai>=1.0.0'"
            )

    # -- Batch transcription --

    def transcribe_file(self, path: str) -> TranscriptionResult:
        from mistralai import Mistral

        client = Mistral(api_key=self.api_key)

        file_name = Path(path).name

        start = time.monotonic()
        with open(path, "rb") as f:
            response = client.audio.transcriptions.complete(
                model=self.model,
                file={"content": f, "file_name": file_name},
                timestamp_granularities=["segment"],
            )
        elapsed = time.monotonic() - start

        text = response.text or ""
        segments = []
        if response.segments:
            for seg in response.segments:
                segments.append(
                    TranscriptionSegment(
                        text=seg.text,
                        start=seg.start,
                        end=seg.end,
                    )
                )

        raw = {}
        if hasattr(response, "model_dump"):
            raw = response.model_dump()

        return TranscriptionResult(
            provider_name=self.name,
            model_name=self.model_name,
            text=text,
            segments=segments,
            language=self.language or getattr(response, "language", None),
            processing_time_seconds=round(elapsed, 3),
            raw_response=raw,
        )

    # -- Streaming transcription --

    def on_partial(self, callback: Callable[[str], None]) -> None:
        self._partial_callback = callback

    def start_streaming(self) -> None:
        self._accumulated_text = ""
        self._start_time = time.monotonic()

        self._loop = asyncio.new_event_loop()
        self._audio_queue = asyncio.Queue()
        self._thread = threading.Thread(
            target=self._run_event_loop, daemon=True
        )
        self._thread.start()

        # Start the stream consumer task
        future = asyncio.run_coroutine_threadsafe(
            self._start_stream(), self._loop
        )
        future.result(timeout=10)

    def _run_event_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _audio_iter(self) -> AsyncIterator[bytes]:
        """Yield audio chunks from the queue until sentinel."""
        while True:
            chunk = await self._audio_queue.get()
            if chunk is None:
                return
            yield chunk

    async def _start_stream(self) -> None:
        """Start the transcription stream as a background task."""
        self._stream_task = asyncio.ensure_future(self._consume_stream())

    async def _consume_stream(self) -> None:
        from mistralai import Mistral
        from mistralai.models import (
            AudioFormat,
            RealtimeTranscriptionError,
            TranscriptionStreamTextDelta,
        )

        client = Mistral(api_key=self.api_key)
        audio_format = AudioFormat(encoding="pcm_s16le", sample_rate=SAMPLE_RATE)

        try:
            async for event in client.audio.realtime.transcribe_stream(
                audio_stream=self._audio_iter(),
                model=STREAMING_MODEL,
                audio_format=audio_format,
            ):
                if isinstance(event, TranscriptionStreamTextDelta):
                    self._accumulated_text += event.text
                    if self._partial_callback:
                        self._partial_callback(self._accumulated_text)
                elif isinstance(event, RealtimeTranscriptionError):
                    pass  # Don't crash on streaming errors
        except asyncio.CancelledError:
            pass
        except Exception:
            pass  # Don't crash streaming on connection errors

    def send_audio(self, chunk: bytes) -> None:
        if self._audio_queue and self._loop:
            self._loop.call_soon_threadsafe(self._audio_queue.put_nowait, chunk)

    def stop_streaming(self) -> TranscriptionResult:
        elapsed = time.monotonic() - self._start_time if self._start_time else None

        # Signal end of audio
        if self._audio_queue and self._loop:
            self._loop.call_soon_threadsafe(self._audio_queue.put_nowait, None)

        # Wait for stream to finish processing
        if self._stream_task and self._loop:
            try:
                async def _wait():
                    await self._stream_task

                future = asyncio.run_coroutine_threadsafe(_wait(), self._loop)
                future.result(timeout=10)
            except Exception:
                pass

        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)

        self._loop = None
        self._thread = None
        self._audio_queue = None
        self._stream_task = None

        return TranscriptionResult(
            provider_name=self.name,
            model_name=STREAMING_MODEL,
            text=self._accumulated_text,
            processing_time_seconds=round(elapsed, 3) if elapsed else None,
        )
