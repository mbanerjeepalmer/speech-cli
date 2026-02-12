"""Command-line interface for speech-cli."""

from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from speech_cli import __version__
from speech_cli.eval.cli_eval import register_commands

app = typer.Typer(
    name="speech-cli",
    help="Speech-to-text CLI with multi-provider support.",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"speech-cli version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Speech-to-text CLI with multi-provider support."""
    load_dotenv()


register_commands(app)


if __name__ == "__main__":
    app()
