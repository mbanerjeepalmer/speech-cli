"""Mistral transcription provider (Voxtral)."""

import os
import time
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
        model: str = "mistral-small-latest",
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
        import base64

        from mistralai import Mistral

        client = Mistral(api_key=self.api_key)

        # Mistral uses multimodal chat with audio encoded as base64 data URL
        with open(path, "rb") as f:
            audio_data = f.read()

        b64 = base64.b64encode(audio_data).decode("utf-8")
        # Determine mime type from extension
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else "wav"
        mime_map = {"wav": "audio/wav", "mp3": "audio/mpeg", "m4a": "audio/mp4", "webm": "audio/webm"}
        mime = mime_map.get(ext, "audio/wav")

        prompt = "Transcribe this audio."
        if self.language:
            prompt += f" The audio is in {self.language}."

        start = time.monotonic()
        response = client.chat.complete(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "audio_url",
                            "audio_url": f"data:{mime};base64,{b64}",
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        )
        elapsed = time.monotonic() - start

        # Extract text from chat response
        text = ""
        raw = {}
        if hasattr(response, "model_dump"):
            raw = response.model_dump()
        elif isinstance(response, dict):
            raw = response

        choices = raw.get("choices", [])
        if choices:
            text = choices[0].get("message", {}).get("content", "")

        return TranscriptionResult(
            provider_name=self.name,
            model_name=self.model_name,
            text=text,
            segments=[],
            language=self.language,
            processing_time_seconds=round(elapsed, 3),
            raw_response=raw,
        )
