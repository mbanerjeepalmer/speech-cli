"""Main entry point for speech-cli."""

import sys

from rich.console import Console

console = Console(stderr=True)


def main() -> None:
    """Main entry point."""
    try:
        from speech_cli.cli import app

        app()

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
