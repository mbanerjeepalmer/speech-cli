"""Groq transcription provider (Whisper via Groq API)."""

import os
import time
from typing import Optional

from speech_cli.eval.providers.base import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionSegment,
)


class GroqProvider(TranscriptionProvider):
    """Transcription via Groq API (Whisper models)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "whisper-large-v3-turbo",
        language: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.model = model
        self.language = language
        self.name = "groq"
        self.model_name = model

    def validate_config(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "Groq API key not set. "
                "Set GROQ_API_KEY env var or pass api_key."
            )
        try:
            import groq  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "groq package not installed. Install with: uv pip install 'groq>=0.4.0'"
            )

    def transcribe_file(self, path: str) -> TranscriptionResult:
        from groq import Groq

        client = Groq(api_key=self.api_key)

        start = time.monotonic()
        with open(path, "rb") as f:
            response = client.audio.transcriptions.create(
                model=self.model,
                file=f,
                response_format="verbose_json",
                language=self.language,
            )
        elapsed = time.monotonic() - start

        # Parse response (OpenAI-compatible verbose_json)
        if hasattr(response, "model_dump"):
            raw = response.model_dump()
        elif isinstance(response, dict):
            raw = response
        else:
            raw = {"text": str(response)}

        segments = []
        for seg in raw.get("segments", []):
            segments.append(
                TranscriptionSegment(
                    text=seg.get("text", "").strip(),
                    start=seg.get("start", 0.0),
                    end=seg.get("end", 0.0),
                    confidence=seg.get("avg_logprob"),
                )
            )

        return TranscriptionResult(
            provider_name=self.name,
            model_name=self.model_name,
            text=raw.get("text", ""),
            segments=segments,
            language=raw.get("language"),
            processing_time_seconds=round(elapsed, 3),
            raw_response=raw,
        )
