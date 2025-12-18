"""Main transcription orchestration logic."""

import sys
from pathlib import Path
from typing import Optional

from speech_cli.client import TranscriptionClient
from speech_cli.config import get_api_key, validate_api_key
from speech_cli.constants import DEFAULT_FORMAT
from speech_cli.formatters import get_formatter
from speech_cli.validators import (
    validate_audio_file,
    validate_language_code,
    validate_output_format,
    validate_output_path,
)


def transcribe_audio(
    audio_file: str,
    output_format: str = DEFAULT_FORMAT,
    output_file: Optional[str] = None,
    api_key: Optional[str] = None,
    language: Optional[str] = None,
    model_id: str = "scribe_v1",
) -> str:
    """Main orchestration function for transcribing audio.

    Args:
        audio_file: Path to the audio file to transcribe
        output_format: Desired output format (text, json, srt, vtt)
        output_file: Optional path to write output to
        api_key: Optional API key (if not provided, will be read from config)
        language: Optional ISO 639-1 language code
        model_id: Model to use for transcription

    Returns:
        The formatted transcription output

    Raises:
        ConfigurationError: If API key is missing or invalid
        ValidationError: If inputs are invalid
        APIError: If API call fails
        FileError: If file operations fail
    """
    # Print status messages to stderr
    print("Validating inputs...", file=sys.stderr)

    # Validate inputs
    audio_path = validate_audio_file(audio_file)
    output_format_validated = validate_output_format(output_format)
    output_path = validate_output_path(output_file)
    language_validated = validate_language_code(language)

    # Get and validate API key
    print("Loading API key...", file=sys.stderr)
    api_key_resolved = get_api_key(api_key)
    validate_api_key(api_key_resolved)

    # Initialise client
    print("Initialising client...", file=sys.stderr)
    client = TranscriptionClient(api_key_resolved)

    # Transcribe
    # Get filename for display
    if isinstance(audio_path, Path):
        display_name = audio_path.name
    else:
        # URL - extract filename from path
        from urllib.parse import urlparse
        parsed = urlparse(audio_path)
        display_name = parsed.path.split('/')[-1] or audio_path

    print(f"Transcribing {display_name}...", file=sys.stderr)
    result = client.transcribe(
        audio_file=audio_path,
        language=language_validated,
        model_id=model_id,
    )

    # Format output
    print("Formatting output...", file=sys.stderr)
    formatter = get_formatter(output_format_validated)
    formatted_output = formatter.format(result)

    # Write to file if specified
    if output_path:
        print(f"Writing output to {output_path}...", file=sys.stderr)
        try:
            output_path.write_text(formatted_output, encoding="utf-8")
            print(f"Successfully wrote output to {output_path}", file=sys.stderr)
        except Exception as e:
            from speech_cli.errors import FileError

            raise FileError(
                f"Failed to write output file: {output_path}",
                details=str(e),
            ) from e

    print("Transcription complete!", file=sys.stderr)
    return formatted_output
