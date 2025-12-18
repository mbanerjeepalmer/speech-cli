"""Command-line interface for speech-cli."""

import sys
from typing import Optional

import typer
from rich.console import Console

from speech_cli import __version__
from speech_cli.constants import DEFAULT_FORMAT, SUPPORTED_FORMATS
from speech_cli.errors import SpeechCLIError
from speech_cli.transcribe import transcribe_audio

# Create Typer app
app = typer.Typer(
    name="speech-cli",
    help="Transcribe audio files using the ElevenLabs API",
    add_completion=False,
)

# Rich console for pretty output
console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"speech-cli version {__version__}")
        raise typer.Exit()


@app.command()
def transcribe(
    audio_file: str = typer.Argument(
        ...,
        help="Path to the audio file to transcribe",
        metavar="AUDIO_FILE",
    ),
    output_format: str = typer.Option(
        DEFAULT_FORMAT,
        "--format",
        "-f",
        help=f"Output format ({', '.join(SUPPORTED_FORMATS)})",
    ),
    output_file: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to write output to (default: stdout)",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        envvar="ELEVENLABS_API_KEY",
        help="ElevenLabs API key (can also be set via ELEVENLABS_API_KEY env var or .env file)",
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="ISO 639-1 language code (e.g., 'en', 'es', 'fr')",
    ),
    model_id: str = typer.Option(
        "scribe_v1",
        "--model",
        "-m",
        help="Model to use for transcription",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable coloured output",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Transcribe an audio file using the ElevenLabs API.

    Example usage:

        # Transcribe to text (default)
        speech-cli audio.mp3

        # Transcribe to JSON format
        speech-cli audio.mp3 --format json

        # Save to file
        speech-cli audio.mp3 --output transcript.txt

        # Specify language
        speech-cli audio.mp3 --language es

        # Use API key from command line
        speech-cli audio.mp3 --api-key YOUR_KEY
    """
    # Disable color if requested
    if no_color:
        console.no_color = True

    try:
        # Run transcription
        result = transcribe_audio(
            audio_file=audio_file,
            output_format=output_format,
            output_file=output_file,
            api_key=api_key,
            language=language,
            model_id=model_id,
        )

        # Print to stdout if not writing to file
        if not output_file:
            print(result)

        sys.exit(0)

    except SpeechCLIError as e:
        # Handle our custom errors
        console.print(f"[red]Error:[/red] {e.message}", stderr=True)
        if e.details:
            console.print(e.details, stderr=True)
        sys.exit(e.exit_code.value)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]", stderr=True)
        sys.exit(130)

    except Exception as e:
        # Unexpected errors
        console.print(f"[red]Unexpected error:[/red] {str(e)}", stderr=True)
        sys.exit(1)


if __name__ == "__main__":
    app()
