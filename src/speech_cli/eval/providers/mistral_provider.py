"""Mistral transcription provider (Voxtral)."""

import os
import time
from pathlib import Path
from typing import Optional

from speech_cli.eval.providers.base import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionSegment,
)


class MistralProvider(TranscriptionProvider):
    """Transcription via Mistral API (Voxtral models)."""

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
