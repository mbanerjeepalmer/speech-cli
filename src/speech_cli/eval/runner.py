"""Transcription runner: orchestrates providers, display, and storage."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from rich.console import Console

from speech_cli.eval.providers.base import TranscriptionProvider, TranscriptionResult
from speech_cli.eval.providers.registry import get_provider, parse_provider_spec
from speech_cli.eval.storage.eval_run import TranscriptionRun
from speech_cli.eval.storage.formats import result_to_verbose_json

console = Console(stderr=True)


def run_single(
    audio_file: str,
    provider_spec: str,
    base_dir: Optional[Path] = None,
) -> tuple[TranscriptionRun, TranscriptionResult]:
    """Run a single provider on an audio file.

    Args:
        audio_file: Path to the audio file.
        provider_spec: Provider spec string (e.g. "whisper-cpp" or "whisper-cpp:model=/path").
        base_dir: Base directory for runs.

    Returns:
        Tuple of (TranscriptionRun, TranscriptionResult).
    """
    name, config = parse_provider_spec(provider_spec)
    provider = get_provider(name, config)
    provider.validate_config()

    tr_run = TranscriptionRun(
        audio_file=audio_file,
        providers=[provider_spec],
        base_dir=base_dir,
    ).setup()

    console.print(f"[blue]Running {provider.name} ({provider.model_name})...[/blue]")
    result = provider.transcribe_file(audio_file)

    # Save result
    output = result_to_verbose_json(result)
    saved_path = tr_run.save_result(result.provider_name, result.model_name, output)
    console.print(f"[green]Saved:[/green] {saved_path}")

    return tr_run, result


def _run_provider(
    provider: TranscriptionProvider,
    audio_file: str,
) -> TranscriptionResult:
    """Run a single provider (used by thread pool)."""
    return provider.transcribe_file(audio_file)


def run_parallel(
    audio_file: str,
    provider_specs: list[str],
    base_dir: Optional[Path] = None,
    display_callback=None,
) -> tuple[TranscriptionRun, list[TranscriptionResult]]:
    """Run multiple providers in parallel on an audio file.

    Args:
        audio_file: Path to the audio file.
        provider_specs: List of provider spec strings.
        base_dir: Base directory for runs.
        display_callback: Optional callback(provider_name, result) for live display.

    Returns:
        Tuple of (TranscriptionRun, list of TranscriptionResults).
    """
    # Instantiate and validate all providers first
    providers = []
    for spec in provider_specs:
        name, config = parse_provider_spec(spec)
        provider = get_provider(name, config)
        provider.validate_config()
        providers.append((spec, provider))

    tr_run = TranscriptionRun(
        audio_file=audio_file,
        providers=provider_specs,
        base_dir=base_dir,
    ).setup()

    results = []
    with ThreadPoolExecutor(max_workers=len(providers)) as executor:
        future_to_spec = {}
        for spec, provider in providers:
            future = executor.submit(_run_provider, provider, audio_file)
            future_to_spec[future] = (spec, provider)

        for future in as_completed(future_to_spec):
            spec, provider = future_to_spec[future]
            try:
                result = future.result()
                results.append(result)

                # Save result
                output = result_to_verbose_json(result)
                tr_run.save_result(result.provider_name, result.model_name, output)

                if display_callback:
                    display_callback(result.provider_name, result)
                else:
                    console.print(
                        f"[green]{result.provider_name}[/green] "
                        f"({result.processing_time_seconds:.1f}s): "
                        f"{result.text[:100]}..."
                        if len(result.text) > 100
                        else f"[green]{result.provider_name}[/green] "
                        f"({result.processing_time_seconds:.1f}s): "
                        f"{result.text}"
                    )
            except Exception as e:
                console.print(f"[red]{spec} failed:[/red] {e}")

    return tr_run, results
