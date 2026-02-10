"""Base classes for transcription providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional


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


class StreamingTranscriptionProvider(TranscriptionProvider):
    """Provider that supports real-time audio streaming."""

    @abstractmethod
    def start_streaming(self) -> None:
        """Open the streaming connection."""

    @abstractmethod
    def send_audio(self, chunk: bytes) -> None:
        """Send a chunk of PCM 16kHz mono int16 audio."""

    @abstractmethod
    def stop_streaming(self) -> TranscriptionResult:
        """Close the connection and return the final result."""

    @abstractmethod
    def on_partial(self, callback: Callable[[str], None]) -> None:
        """Register callback for partial transcript text updates."""
