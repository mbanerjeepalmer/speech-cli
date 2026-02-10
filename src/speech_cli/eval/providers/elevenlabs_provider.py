"""ElevenLabs transcription provider wrapping the existing client."""

import os
import time
from typing import Optional

from speech_cli.eval.providers.base import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionSegment,
)


class ElevenLabsProvider(TranscriptionProvider):
    """Transcription via ElevenLabs Speech-to-Text API."""

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

    def validate_config(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "ElevenLabs API key not set. "
                "Set ELEVENLABS_API_KEY env var or pass api_key."
            )

    def supports_diarization(self) -> bool:
        return True

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
