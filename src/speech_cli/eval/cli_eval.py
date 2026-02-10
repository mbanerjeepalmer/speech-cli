"""CLI commands for multi-provider transcription."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from speech_cli.eval.providers.registry import list_providers, get_provider, parse_provider_spec
from speech_cli.eval.runner import run_single, run_parallel, run_streaming
from speech_cli.eval.storage.eval_run import TranscriptionRun

console = Console()


def register_commands(app: typer.Typer) -> None:
    """Register all transcription commands onto a Typer app."""

    @app.command("transcribe")
    def transcribe(
        audio_file: Optional[str] = typer.Argument(
            None,
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
        mic: bool = typer.Option(
            False,
            "--mic",
            help="Record from microphone instead of a file.",
        ),
        max_duration: float = typer.Option(
            300.0,
            "--max-duration",
            help="Maximum recording duration in seconds (mic mode).",
        ),
        sync: bool = typer.Option(
            False,
            "--sync",
            help="Synchronised provider updates (not yet implemented).",
        ),
    ) -> None:
        """Transcribe an audio file or live microphone input."""
        if sync:
            raise NotImplementedError("Synchronised mode not yet implemented")

        if mic and audio_file:
            console.print("[red]Error:[/red] Cannot use both --mic and an audio file.")
            raise typer.Exit(code=1)

        if not mic and not audio_file:
            console.print("[red]Error:[/red] Provide an audio file or use --mic.")
            raise typer.Exit(code=1)

        base_dir = Path(output_dir) if output_dir else None

        if mic:
            _run_mic_mode(provider, display, base_dir, max_duration)
        elif len(provider) == 1:
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


def _run_mic_mode(
    provider_specs: list[str],
    display_mode: str,
    base_dir: Optional[Path],
    max_duration: float,
) -> None:
    """Run live mic recording with streaming transcription."""
    from speech_cli.eval.audio.recorder import MicRecorder
    from speech_cli.eval.display.live_display import TranscriptionDisplay

    provider_names = []
    for spec in provider_specs:
        name, _ = parse_provider_spec(spec)
        provider_names.append(name)

    tr_display = TranscriptionDisplay(mode=display_mode)
    tr_display.set_providers(provider_names)

    adapters, on_audio, stop_fn = run_streaming(
        provider_specs,
        base_dir=base_dir,
        partial_callback=lambda name, text: tr_display.update_partial(name, text),
    )

    recorder = MicRecorder(
        on_audio=on_audio,
        level_callback=lambda level: tr_display.update_recording_status(
            elapsed=recorder.elapsed, level=level, is_recording=True
        ),
        max_duration=max_duration,
    )

    console.print("[bold]Recording from microphone.[/bold] Press Enter to stop.\n")

    with tr_display:
        recorder.start()
        try:
            input()  # Block until Enter
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            recorder.stop()
            tr_display.update_recording_status(0, 0, False)

    results = stop_fn()

    # Save recording
    if base_dir:
        wav_path = str(base_dir / "mic_recording.wav")
    else:
        wav_path = "runs/mic_recording.wav"
    recorder.save_wav(wav_path)
    console.print(f"\n[dim]Recording saved: {wav_path}[/dim]")

    for r in results:
        console.print(
            f"  [green]{r.provider_name}[/green] ({r.model_name}): "
            f"{r.text[:100]}{'...' if len(r.text) > 100 else ''}"
        )


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
