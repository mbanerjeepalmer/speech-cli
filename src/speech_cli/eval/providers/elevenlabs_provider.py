"""ElevenLabs transcription provider wrapping the existing client."""

import asyncio
import base64
import os
import threading
import time
from typing import Callable, Optional

from speech_cli.eval.providers.base import (
    StreamingTranscriptionProvider,
    TranscriptionResult,
    TranscriptionSegment,
)


class ElevenLabsProvider(StreamingTranscriptionProvider):
    """Transcription via ElevenLabs Speech-to-Text API.

    Supports both batch file transcription and real-time streaming
    via WebSocket connection.
    """

    STREAMING_MODEL = "scribe_v2_realtime"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "scribe_v1",
        language: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        self.model = model
        self.language = language
        self.name = "elevenlabs"
        self.model_name = model

        self._partial_callback: Optional[Callable[[str], None]] = None
        self._connection = None
        self._committed_text = ""
        self._partial_text = ""
        self._start_time: Optional[float] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

    def validate_config(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "ElevenLabs API key not set. "
                "Set ELEVENLABS_API_KEY env var or pass api_key."
            )

    def supports_diarization(self) -> bool:
        return True

    # -- Batch transcription (unchanged) --

    def transcribe_file(self, path: str) -> TranscriptionResult:
        from elevenlabs import ElevenLabs

        client = ElevenLabs(api_key=self.api_key)

        start = time.monotonic()
        with open(path, "rb") as f:
            response = client.speech_to_text.convert(
                model_id=self.model,
                file=f,
                language_code=self.language,
            )
        elapsed = time.monotonic() - start

        # Convert response
        if hasattr(response, "model_dump"):
            raw = response.model_dump()
        elif hasattr(response, "dict"):
            raw = response.dict()
        else:
            raw = {"text": str(response)}

        segments = []
        text = raw.get("text", "")

        for word in raw.get("words", []):
            segments.append(
                TranscriptionSegment(
                    text=word.get("text", ""),
                    start=word.get("start", 0.0),
                    end=word.get("end", 0.0),
                    speaker=word.get("speaker_id"),
                    confidence=word.get("confidence"),
                )
            )

        return TranscriptionResult(
            provider_name=self.name,
            model_name=self.model_name,
            text=text,
            segments=segments,
            language=raw.get("language_code"),
            processing_time_seconds=round(elapsed, 3),
            raw_response=raw,
        )

    # -- Streaming transcription --

    def on_partial(self, callback: Callable[[str], None]) -> None:
        self._partial_callback = callback

    def start_streaming(self) -> None:
        self._committed_text = ""
        self._partial_text = ""
        self._start_time = time.monotonic()

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_event_loop, daemon=True
        )
        self._thread.start()

        # Wait for connection to be established
        future = asyncio.run_coroutine_threadsafe(
            self._connect(), self._loop
        )
        future.result(timeout=10)

    def _run_event_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _connect(self) -> None:
        from elevenlabs import ElevenLabs
        from elevenlabs.realtime.scribe import AudioFormat, CommitStrategy

        client = ElevenLabs(api_key=self.api_key)

        options = {
            "model_id": self.STREAMING_MODEL,
            "audio_format": AudioFormat.PCM_16000,
            "sample_rate": 16000,
            "commit_strategy": CommitStrategy.VAD,
        }
        if self.language:
            options["language_code"] = self.language

        self._connection = await client.speech_to_text.realtime.connect(options)

        self._connection.on("partial_transcript", self._on_partial_transcript)
        self._connection.on("committed_transcript", self._on_committed_transcript)

    def _on_partial_transcript(self, data) -> None:
        transcript = data.get("transcript", "") if isinstance(data, dict) else ""
        self._partial_text = transcript
        full_text = (self._committed_text + " " + transcript).strip()
        if self._partial_callback:
            self._partial_callback(full_text)

    def _on_committed_transcript(self, data) -> None:
        transcript = data.get("transcript", "") if isinstance(data, dict) else ""
        if self._committed_text:
            self._committed_text += " " + transcript
        else:
            self._committed_text = transcript
        self._partial_text = ""
        if self._partial_callback:
            self._partial_callback(self._committed_text)

    def send_audio(self, chunk: bytes) -> None:
        if self._connection and self._loop:
            b64 = base64.b64encode(chunk).decode("utf-8")
            asyncio.run_coroutine_threadsafe(
                self._connection.send({"audio_base_64": b64}),
                self._loop,
            )

    def stop_streaming(self) -> TranscriptionResult:
        elapsed = time.monotonic() - self._start_time if self._start_time else None

        if self._connection and self._loop:
            try:
                future = asyncio.run_coroutine_threadsafe(
                    self._connection.commit(), self._loop
                )
                future.result(timeout=5)
            except Exception:
                pass

            # Give a moment for final events
            time.sleep(0.5)

        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)

        self._connection = None
        self._loop = None
        self._thread = None

        final_text = self._committed_text
        if self._partial_text:
            final_text = (final_text + " " + self._partial_text).strip()

        return TranscriptionResult(
            provider_name=self.name,
            model_name=self.STREAMING_MODEL,
            text=final_text,
            processing_time_seconds=round(elapsed, 3) if elapsed else None,
        )
