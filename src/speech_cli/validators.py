"""Input validation for speech-cli."""

from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

from speech_cli.constants import (
    MAX_FILE_SIZE_MB,
    SUPPORTED_AUDIO_EXTENSIONS,
    SUPPORTED_FORMATS,
)
from speech_cli.errors import ValidationError


def validate_audio_file(file_path: str) -> Union[Path, str]:
    """Validate that the audio file exists and is valid.

    Args:
        file_path: Path to the audio file or URL

    Returns:
        Path object for local files or URL string for remote files

    Raises:
        ValidationError: If the file is invalid
    """
    # Check if it's a URL
    parsed = urlparse(file_path)
    if parsed.scheme in ('http', 'https'):
        # Validate URL has a supported audio extension
        path_lower = parsed.path.lower()
        if not any(path_lower.endswith(ext) for ext in SUPPORTED_AUDIO_EXTENSIONS):
            raise ValidationError(
                f"Unsupported URL file format",
                details=f"URL must point to a file with one of these extensions: {', '.join(SUPPORTED_AUDIO_EXTENSIONS)}",
            )
        # Return the URL as-is for remote handling
        return file_path

    # Handle local file path
    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        raise ValidationError(
            f"File not found: {file_path}",
            details="Please check the file path and try again.",
        )

    # Check if it's a file (not a directory)
    if not path.is_file():
        raise ValidationError(
            f"Not a file: {file_path}",
            details="Please provide a path to a file, not a directory.",
        )

    # Check file extension
    if path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file format: {path.suffix}",
            details=f"Supported formats: {', '.join(SUPPORTED_AUDIO_EXTENSIONS)}",
        )

    # Check file size
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValidationError(
            f"File too large: {file_size_mb:.1f}MB",
            details=f"Maximum file size is {MAX_FILE_SIZE_MB}MB.",
        )

    # Check if file is readable
    if not os.access(path, os.R_OK):
        raise ValidationError(
            f"File is not readable: {file_path}",
            details="Please check file permissions.",
        )

    return path


def validate_output_format(format_type: str) -> str:
    """Validate that the output format is supported.

    Args:
        format_type: The requested output format

    Returns:
        The validated format string (lowercase)

    Raises:
        ValidationError: If the format is not supported
    """
    format_lower = format_type.lower()

    if format_lower not in SUPPORTED_FORMATS:
        raise ValidationError(
            f"Unsupported output format: {format_type}",
            details=f"Supported formats: {', '.join(SUPPORTED_FORMATS)}",
        )

    return format_lower


def validate_output_path(output_path: Optional[str]) -> Optional[Path]:
    """Validate that the output path is writable.

    Args:
        output_path: Optional path where output should be written

    Returns:
        Path object if output_path is provided, None otherwise

    Raises:
        ValidationError: If the output path is invalid
    """
    if not output_path:
        return None

    path = Path(output_path)

    # Check if parent directory exists
    parent_dir = path.parent
    if not parent_dir.exists():
        raise ValidationError(
            f"Output directory does not exist: {parent_dir}",
            details="Please create the directory first or choose a different path.",
        )

    # Check if parent directory is writable
    if not os.access(parent_dir, os.W_OK):
        raise ValidationError(
            f"Output directory is not writable: {parent_dir}",
            details="Please check directory permissions.",
        )

    # Check if file already exists (warn but don't fail)
    if path.exists() and path.is_file():
        # This is just informational - we'll overwrite
        # The CLI can add a --force flag later if needed
        pass

    return path


def validate_language_code(language: Optional[str]) -> Optional[str]:
    """Validate language code format.

    Args:
        language: Optional ISO 639-1 language code

    Returns:
        The validated language code (lowercase) or None

    Raises:
        ValidationError: If the language code format is invalid
    """
    if not language:
        return None

    # Basic validation - ISO 639-1 codes are 2 letters
    language_lower = language.lower()

    if len(language_lower) != 2 or not language_lower.isalpha():
        raise ValidationError(
            f"Invalid language code: {language}",
            details="Please provide a valid ISO 639-1 language code (e.g., 'en', 'es', 'fr').",
        )

    return language_lower


# Import os for file access checks
import os
