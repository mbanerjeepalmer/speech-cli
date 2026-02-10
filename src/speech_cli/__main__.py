"""Main entry point for speech-cli with dynamic CLI generation."""

import sys
from pathlib import Path

from rich.console import Console

# Console for stderr output
console = Console(stderr=True)


def main() -> None:
    """Main entry point - dynamically generate CLI from SDK."""
    try:
        # Check if SDK methods file exists
        sdk_methods_path = (
            Path(__file__).parent.parent.parent / "docs" / "sdk-methods.json"
        )

        if sdk_methods_path.exists():
            # Use dynamic CLI generator
            from speech_cli.cli_generator import get_cli_app

            app = get_cli_app()
            app()
        else:
            # Fallback to legacy CLI
            console.print("[yellow]Warning:[/yellow] SDK methods data not found")
            console.print("Falling back to legacy CLI (STT only)")
            console.print(
                "To enable full SDK access, run: uv run python scripts/inspect_sdk.py"
            )
            console.print("")

            from speech_cli.cli import app as legacy_app

            legacy_app()

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
