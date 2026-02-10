"""HuggingFace Inference API transcription provider."""

import os
import time
from typing import Optional

from speech_cli.eval.providers.base import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionSegment,
)


class HuggingFaceProvider(TranscriptionProvider):
    """Transcription via HuggingFace Inference API.

    Setup:
        1. Get a token at https://huggingface.co/settings/tokens
        2. Set HF_API_KEY in your .env file
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "openai/whisper-large-v3-turbo",
        language: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("HF_API_KEY")
        self.model = model
        self.language = language
        self.name = "huggingface"
        self.model_name = model

    def validate_config(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "HuggingFace API key not set. "
                "Get a token at https://huggingface.co/settings/tokens "
                "and set HF_API_KEY env var."
            )
        try:
            import huggingface_hub  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "huggingface-hub package not installed. "
                "Install with: uv pip install 'huggingface-hub>=0.20.0'"
            )

    def transcribe_file(self, path: str) -> TranscriptionResult:
        from huggingface_hub import InferenceClient

        client = InferenceClient(token=self.api_key)

        start = time.monotonic()
        output = client.automatic_speech_recognition(
            audio=path,
            model=self.model,
        )
        elapsed = time.monotonic() - start

        # InferenceClient returns an AutomaticSpeechRecognitionOutput
        if isinstance(output, dict):
            text = output.get("text", "")
            chunks = output.get("chunks", [])
        elif hasattr(output, "text"):
            text = output.text
            chunks = getattr(output, "chunks", []) or []
        else:
            text = str(output)
            chunks = []

        segments = []
        for chunk in chunks:
            if isinstance(chunk, dict):
                ts = chunk.get("timestamp", [0.0, 0.0])
                segments.append(
                    TranscriptionSegment(
                        text=chunk.get("text", ""),
                        start=ts[0] if ts and len(ts) > 0 else 0.0,
                        end=ts[1] if ts and len(ts) > 1 else 0.0,
                    )
                )

        return TranscriptionResult(
            provider_name=self.name,
            model_name=self.model_name,
            text=text,
            segments=segments,
            language=self.language,
            processing_time_seconds=round(elapsed, 3),
            raw_response={"text": text},
        )
