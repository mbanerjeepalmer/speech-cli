"""Constants and configuration values for speech-cli."""

from enum import IntEnum
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
