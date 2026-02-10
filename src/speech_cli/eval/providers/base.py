"""Base classes for transcription providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TranscriptionSegment:
    """A single segment of transcribed text with timestamps."""

    text: str
    start: float  # seconds
    end: float  # seconds
    speaker: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class TranscriptionResult:
    """Result from a transcription provider."""

    provider_name: str
    model_name: str
    text: str
    segments: list = field(default_factory=list)
    language: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    raw_response: Optional[dict] = None


class TranscriptionProvider(ABC):
    """Abstract base class for transcription providers."""

    name: str
    model_name: str

    @abstractmethod
    def transcribe_file(self, path: str) -> TranscriptionResult:
        """Transcribe an audio file.

        Args:
            path: Path to the audio file.

        Returns:
            TranscriptionResult with the transcription.
        """

    @abstractmethod
    def validate_config(self) -> None:
        """Validate that the provider is properly configured.

        Raises:
            RuntimeError: If configuration is invalid (e.g. missing binary or API key).
        """

    def supports_diarization(self) -> bool:
        """Whether this provider supports speaker diarization."""
        return False
