"""CLI commands for multi-provider transcription."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from speech_cli.eval.providers.registry import list_providers, get_provider, parse_provider_spec
from speech_cli.eval.runner import run_single, run_parallel
from speech_cli.eval.storage.eval_run import TranscriptionRun

console = Console()


def register_commands(app: typer.Typer) -> None:
    """Register all transcription commands onto a Typer app."""

    @app.command("transcribe")
    def transcribe(
        audio_file: str = typer.Argument(
            ...,
            help="Path to the audio file to transcribe.",
        ),
        provider: list[str] = typer.Option(
            ["whisper-cpp"],
            "-p",
            "--provider",
            help="Provider spec (repeatable). E.g. 'whisper-cpp', 'groq', 'whisper-cpp:model=/path'.",
        ),
        display: str = typer.Option(
            "single-line",
            "--display",
            "-d",
            help="Display mode: 'single-line' or 'multi-line'.",
        ),
        output_dir: Optional[str] = typer.Option(
            None,
            "--output-dir",
            "-o",
            help="Base directory for runs (default: runs/).",
        ),
    ) -> None:
        """Transcribe an audio file with one or more providers."""
        base_dir = Path(output_dir) if output_dir else None

        if len(provider) == 1:
            tr_run, result = run_single(audio_file, provider[0], base_dir=base_dir)
            _print_result(result)
            console.print(f"\n[dim]Run: {tr_run.run_dir}[/dim]")
        else:
            from speech_cli.eval.display.live_display import TranscriptionDisplay

            tr_display = TranscriptionDisplay(mode=display)
            provider_names = []
            for spec in provider:
                name, _ = parse_provider_spec(spec)
                provider_names.append(name)
            tr_display.set_providers(provider_names)

            def on_result(provider_name, result):
                tr_display.update_result(provider_name, result)

            with tr_display:
                tr_run, results = run_parallel(
                    audio_file,
                    provider,
                    base_dir=base_dir,
                    display_callback=on_result,
                )

            console.print(f"\n[dim]Run: {tr_run.run_dir}[/dim]")
            for r in results:
                console.print(
                    f"  [green]{r.provider_name}[/green] ({r.model_name}): "
                    f"{r.processing_time_seconds:.1f}s"
                )

    @app.command("list-providers")
    def cmd_list_providers() -> None:
        """List available transcription providers."""
        table = Table(title="Available Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")

        for name in list_providers():
            try:
                p = get_provider(name)
                p.validate_config()
                status = "ready"
            except ImportError:
                status = "[yellow]missing deps[/yellow]"
            except RuntimeError as e:
                status = f"[red]{e}[/red]"
            except Exception:
                status = "[red]error[/red]"

            table.add_row(name, status)

        console.print(table)

    @app.command("show")
    def cmd_show(
        run_dir: str = typer.Argument(
            ...,
            help="Path to a run directory.",
        ),
    ) -> None:
        """Show results from a previous transcription run."""
        data = TranscriptionRun.load_run(Path(run_dir))

        console.print(Panel(
            json.dumps(data["metadata"], indent=2),
            title="Metadata",
        ))

        for name, result in data["results"].items():
            text = result.get("text", "")
            time_s = result.get("processing_time_seconds")
            header = name
            if time_s is not None:
                header += f" ({time_s:.1f}s)"

            console.print(Panel(text, title=header))


def _print_result(result) -> None:
    """Pretty-print a single TranscriptionResult."""
    console.print(Panel(
        result.text,
        title=f"{result.provider_name} ({result.model_name})",
        subtitle=f"{result.processing_time_seconds:.1f}s" if result.processing_time_seconds else None,
    ))
    if result.segments:
        table = Table(title="Segments")
        table.add_column("Start", style="cyan")
        table.add_column("End", style="cyan")
        table.add_column("Text")
        table.add_column("Speaker", style="green")
        for seg in result.segments:
            table.add_row(
                f"{seg.start:.1f}",
                f"{seg.end:.1f}",
                seg.text,
                seg.speaker or "",
            )
        console.print(table)
