"""Constants and configuration values for speech-cli."""

from enum import Enum, IntEnum
from typing import Final


class ExitCode(IntEnum):
    """Exit codes for the CLI application."""

    SUCCESS = 0
    GENERAL_ERROR = 1
    CONFIG_ERROR = 2
    VALIDATION_ERROR = 3
    API_ERROR = 4
    NETWORK_ERROR = 5
    FILE_ERROR = 6


class Provider(str, Enum):
    """Supported transcription providers."""

    WHISPER_CPP = "whisper-cpp"
    ELEVENLABS = "elevenlabs"
    GROQ = "groq"
    MISTRAL = "mistral"
    HUGGINGFACE = "huggingface"


PROVIDER_MODELS: Final[dict[Provider, list[str]]] = {
    Provider.WHISPER_CPP: [
        "ggml-tiny.en",
        "ggml-base.en",
        "ggml-small.en",
        "ggml-medium.en",
        "ggml-large",
    ],
    Provider.ELEVENLABS: ["scribe_v1", "scribe_v2", "scribe_v2_realtime"],
    Provider.GROQ: ["whisper-large-v3", "whisper-large-v3-turbo"],
    Provider.MISTRAL: [
        "voxtral-mini-latest",
        "voxtral-mini-transcribe-realtime-2602",
    ],
    Provider.HUGGINGFACE: [
        "openai/whisper-large-v3-turbo",
        "openai/whisper-large-v3",
    ],
}

DEFAULT_MODELS: Final[dict[Provider, str]] = {
    Provider.WHISPER_CPP: "ggml-tiny.en",
    Provider.ELEVENLABS: "scribe_v1",
    Provider.GROQ: "whisper-large-v3-turbo",
    Provider.MISTRAL: "voxtral-mini-latest",
    Provider.HUGGINGFACE: "openai/whisper-large-v3-turbo",
}


class OutputFormat(str, Enum):
    """Supported output formats."""

    TEXT = "text"
    JSON = "json"
    SRT = "srt"
    VTT = "vtt"


# Supported output formats
SUPPORTED_FORMATS: Final[tuple[str, ...]] = ("text", "json", "srt", "vtt")

# Default output format
DEFAULT_FORMAT: Final[str] = "text"

# Environment variable names
ENV_API_KEY: Final[str] = "ELEVENLABS_API_KEY"

# Configuration file names
ENV_FILE_NAME: Final[str] = ".env"

# File validation
MAX_FILE_SIZE_MB: Final[int] = 500  # 500 MB
SUPPORTED_AUDIO_EXTENSIONS: Final[tuple[str, ...]] = (
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".m4a",
    ".wav",
    ".webm",
)

# API retry configuration
MAX_RETRIES: Final[int] = 3
RETRY_DELAY: Final[float] = 1.0  # seconds
RETRY_BACKOFF: Final[float] = 2.0  # exponential backoff multiplier

# Timeout configuration
REQUEST_TIMEOUT: Final[int] = 300  # 5 minutes in seconds
