"""CLI commands for multi-provider transcription."""

import json
import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from speech_cli.constants import DEFAULT_MODELS, PROVIDER_MODELS, OutputFormat, Provider
from speech_cli.eval.providers.registry import (
    get_provider,
    list_providers,
    parse_provider_spec,
)
from speech_cli.eval.runner import run_single, run_parallel, run_streaming
from speech_cli.eval.storage.eval_run import TranscriptionRun
from speech_cli.eval.storage.formats import result_to_verbose_json
from speech_cli.formatters import get_formatter

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
            help="Provider spec (repeatable). E.g. 'groq', 'groq/whisper-large-v3-turbo'.",
        ),
        format: OutputFormat = typer.Option(
            OutputFormat.TEXT,
            "-f",
            "--format",
            help="Output format.",
        ),
        diarize: bool = typer.Option(
            False,
            "--diarize",
            help="Enable speaker diarization (if supported by provider).",
        ),
        language: Optional[str] = typer.Option(
            None,
            "-l",
            "--language",
            help="Language code (e.g. 'en', 'fr').",
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
        name: Optional[str] = typer.Option(
            None,
            "--name",
            "-n",
            help="Optional name for this run.",
        ),
        gain: float = typer.Option(
            1.0,
            "--gain",
            "-g",
            help="Mic input gain multiplier (e.g. 2.0 for 2x louder).",
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

        # Default to mic mode when no audio file provided
        use_mic = mic or not audio_file

        base_dir = Path(output_dir) if output_dir else None

        # Inject language/diarize into each provider spec's config
        extra_config = {}
        if language:
            extra_config["language"] = language
        if diarize:
            extra_config["diarize"] = True

        if use_mic:
            results = _run_mic_mode(
                provider, display, base_dir, max_duration,
                name=name, gain=gain, extra_config=extra_config,
            )
            if format != OutputFormat.TEXT and results:
                _print_formatted(results, format)
        elif len(provider) == 1:
            tr_run, result = run_single(
                audio_file, provider[0], base_dir=base_dir,
                run_name=name, extra_config=extra_config,
            )
            if format != OutputFormat.TEXT:
                _print_formatted([result], format)
            else:
                _print_result(result)
            console.print(f"\n[dim]Run: {tr_run.run_dir}[/dim]")
        else:
            from speech_cli.eval.display.live_display import TranscriptionDisplay

            tr_display = TranscriptionDisplay(mode=display)
            provider_names = []
            for spec in provider:
                pname, _ = parse_provider_spec(spec)
                provider_names.append(pname)
            tr_display.set_providers(provider_names)

            def on_result(provider_name, result):
                tr_display.update_result(provider_name, result)

            with tr_display:
                tr_run, results = run_parallel(
                    audio_file,
                    provider,
                    base_dir=base_dir,
                    display_callback=on_result,
                    run_name=name,
                    extra_config=extra_config,
                )

            if format != OutputFormat.TEXT:
                _print_formatted(results, format)
            else:
                console.print(f"\n[dim]Run: {tr_run.run_dir}[/dim]")
                for r in results:
                    console.print(
                        f"  [green]{r.provider_name}[/green] ({r.model_name}): "
                        f"{r.processing_time_seconds:.1f}s"
                    )

    @app.command("providers")
    def cmd_providers(
        json_output: bool = typer.Option(
            False,
            "--json",
            help="Output as JSON.",
        ),
    ) -> None:
        """List available transcription providers."""
        rows = []
        for name in list_providers():
            provider_enum = Provider(name)
            models = PROVIDER_MODELS.get(provider_enum, [])
            default_model = DEFAULT_MODELS.get(provider_enum, "")

            try:
                p = get_provider(name)
                p.validate_config()
                status = "ready"
            except ImportError:
                status = "missing deps"
            except RuntimeError as e:
                status = str(e)
            except Exception:
                status = "error"

            rows.append({
                "provider": name,
                "status": status,
                "models": len(models),
                "default_model": default_model,
            })

        if json_output:
            console.print(json.dumps(rows, indent=2))
            return

        table = Table(title="Providers")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Models", justify="right")
        table.add_column("Default Model", style="dim")

        for row in rows:
            status_style = row["status"]
            if "missing" in status_style or "error" in status_style:
                status_style = f"[yellow]{row['status']}[/yellow]"
            elif status_style != "ready":
                status_style = f"[red]{row['status']}[/red]"
            table.add_row(
                row["provider"],
                status_style,
                str(row["models"]),
                row["default_model"],
            )

        console.print(table)

    @app.command("models")
    def cmd_models(
        provider_filter: Optional[str] = typer.Option(
            None,
            "-p",
            "--provider",
            help="Filter by provider name.",
        ),
        json_output: bool = typer.Option(
            False,
            "--json",
            help="Output as JSON.",
        ),
    ) -> None:
        """List all available models."""
        rows = []
        for provider_enum in Provider:
            if provider_filter and provider_enum.value != provider_filter:
                continue
            models = PROVIDER_MODELS.get(provider_enum, [])
            default = DEFAULT_MODELS.get(provider_enum, "")
            for model in models:
                rows.append({
                    "provider": provider_enum.value,
                    "model": model,
                    "default": model == default,
                })

        if provider_filter and not rows:
            # Validate the provider name to give a helpful error
            try:
                Provider(provider_filter)
            except ValueError:
                available = ", ".join(p.value for p in Provider)
                console.print(
                    f"[red]Unknown provider '{provider_filter}'. "
                    f"Available: {available}[/red]"
                )
                raise typer.Exit(code=1)

        if json_output:
            console.print(json.dumps(rows, indent=2))
            return

        table = Table(title="Models")
        table.add_column("Provider", style="cyan")
        table.add_column("Model")
        table.add_column("Default", justify="center")

        for row in rows:
            table.add_row(
                row["provider"],
                row["model"],
                "*" if row["default"] else "",
            )

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


def _print_formatted(results, format: OutputFormat) -> None:
    """Print results in the requested output format."""
    formatter = get_formatter(format.value)
    for result in results:
        data = result_to_verbose_json(result)
        console.print(formatter.format(data))


def _run_mic_mode(
    provider_specs: list[str],
    display_mode: str,
    base_dir: Optional[Path],
    max_duration: float,
    name: Optional[str] = None,
    gain: float = 1.0,
    extra_config: Optional[dict] = None,
) -> list:
    """Run live mic recording with streaming transcription.

    Returns list of TranscriptionResults.
    """
    from speech_cli.eval.audio.recorder import MicRecorder
    from speech_cli.eval.display.live_display import TranscriptionDisplay

    provider_names = []
    for spec in provider_specs:
        pname, _ = parse_provider_spec(spec)
        provider_names.append(pname)

    tr_display = TranscriptionDisplay(mode=display_mode)
    tr_display.set_providers(provider_names)

    # Create run directory before recording (no audio file yet)
    tr_run = TranscriptionRun(
        providers=provider_specs,
        base_dir=base_dir,
        name=name,
    ).setup()

    # Set up file logging for streaming diagnostics
    log_path = tr_run.run_dir / "streaming.log"
    _stream_log_handler = logging.FileHandler(log_path)
    _stream_log_handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s  %(message)s", datefmt="%H:%M:%S")
    )
    stream_logger = logging.getLogger("speech_cli.eval")
    stream_logger.addHandler(_stream_log_handler)
    stream_logger.setLevel(logging.DEBUG)

    adapters, on_audio, stop_fn = run_streaming(
        provider_specs,
        base_dir=base_dir,
        partial_callback=lambda pname, text: tr_display.update_partial(pname, text),
        extra_config=extra_config,
    )

    recorder = MicRecorder(
        on_audio=on_audio,
        level_callback=lambda level: tr_display.update_recording_status(
            elapsed=recorder.elapsed, level=level, is_recording=True
        ),
        max_duration=max_duration,
        gain=gain,
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
            # Save wav immediately so it's preserved even on Ctrl+C
            wav_path = str(tr_run.input_dir / "mic_recording.wav")
            recorder.save_wav(wav_path)
            tr_display.update_recording_status(0, 0, False)

    results = stop_fn()

    # Save provider results into the run's output directory
    for r in results:
        output = result_to_verbose_json(r)
        tr_run.save_result(r.provider_name, r.model_name, output)

    # Tear down file logging
    stream_logger.removeHandler(_stream_log_handler)
    _stream_log_handler.close()

    console.print(f"\n[dim]Run: {tr_run.run_dir}[/dim]")
    for r in results:
        console.print(
            f"  [green]{r.provider_name}[/green] ({r.model_name}): "
            f"{r.text[:100]}{'...' if len(r.text) > 100 else ''}"
        )

    return results


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
