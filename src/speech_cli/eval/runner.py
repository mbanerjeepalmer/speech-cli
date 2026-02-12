"""Transcription runner: orchestrates providers, display, and storage."""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from rich.console import Console

logger = logging.getLogger(__name__)

from speech_cli.eval.audio.chunked_adapter import ChunkedStreamingAdapter
from speech_cli.eval.audio.convert import convert_to_wav_16k, is_wav_16k
from speech_cli.eval.providers.base import (
    StreamingTranscriptionProvider,
    TranscriptionProvider,
    TranscriptionResult,
)
from speech_cli.eval.providers.registry import get_provider, parse_provider_spec
from speech_cli.eval.storage.eval_run import TranscriptionRun
from speech_cli.eval.storage.formats import result_to_verbose_json

console = Console(stderr=True)


def _ensure_wav_16k(audio_file: str) -> str:
    """Convert audio to WAV 16kHz mono if needed."""
    if is_wav_16k(audio_file):
        return audio_file
    console.print("[dim]Converting audio to WAV 16kHz mono...[/dim]")
    return convert_to_wav_16k(audio_file)


def run_single(
    audio_file: str,
    provider_spec: str,
    base_dir: Optional[Path] = None,
    run_name: Optional[str] = None,
    extra_config: Optional[dict] = None,
) -> tuple[TranscriptionRun, TranscriptionResult]:
    """Run a single provider on an audio file.

    Args:
        audio_file: Path to the audio file.
        provider_spec: Provider spec string (e.g. "whisper-cpp" or "whisper-cpp:model=/path").
        base_dir: Base directory for runs.
        run_name: Optional name for the run directory.
        extra_config: Extra config (language, diarize) merged into provider config.

    Returns:
        Tuple of (TranscriptionRun, TranscriptionResult).
    """
    name, config = parse_provider_spec(provider_spec)
    if extra_config:
        config = {**config, **extra_config}
    provider = get_provider(name, config)
    provider.validate_config()

    wav_file = _ensure_wav_16k(audio_file)

    tr_run = TranscriptionRun(
        audio_file=audio_file,
        providers=[provider_spec],
        base_dir=base_dir,
        name=run_name,
    ).setup()

    console.print(f"[blue]Running {provider.name} ({provider.model_name})...[/blue]")
    result = provider.transcribe_file(wav_file)

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
    run_name: Optional[str] = None,
    extra_config: Optional[dict] = None,
) -> tuple[TranscriptionRun, list[TranscriptionResult]]:
    """Run multiple providers in parallel on an audio file.

    Args:
        audio_file: Path to the audio file.
        provider_specs: List of provider spec strings.
        base_dir: Base directory for runs.
        display_callback: Optional callback(provider_name, result) for live display.
        run_name: Optional name for the run directory.
        extra_config: Extra config (language, diarize) merged into provider config.

    Returns:
        Tuple of (TranscriptionRun, list of TranscriptionResults).
    """
    # Instantiate and validate all providers first
    providers = []
    for spec in provider_specs:
        pname, config = parse_provider_spec(spec)
        if extra_config:
            config = {**config, **extra_config}
        provider = get_provider(pname, config)
        provider.validate_config()
        providers.append((spec, provider))

    wav_file = _ensure_wav_16k(audio_file)

    tr_run = TranscriptionRun(
        audio_file=audio_file,
        providers=provider_specs,
        base_dir=base_dir,
        name=run_name,
    ).setup()

    results = []
    with ThreadPoolExecutor(max_workers=len(providers)) as executor:
        future_to_spec = {}
        for spec, provider in providers:
            future = executor.submit(_run_provider, provider, wav_file)
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


def run_streaming(
    provider_specs: list[str],
    base_dir: Optional[Path] = None,
    partial_callback=None,
    extra_config: Optional[dict] = None,
) -> tuple[list, "Callable[[bytes], None]", "Callable[[], list[TranscriptionResult]]"]:
    """Set up streaming providers and return audio sink + stop function.

    Args:
        provider_specs: List of provider spec strings.
        base_dir: Base directory for runs.
        partial_callback: Optional callback(provider_name, text) for partial updates.
        extra_config: Extra config (language, diarize) merged into provider config.

    Returns:
        Tuple of (streaming_adapters, on_audio_fn, stop_fn).
        - streaming_adapters: list of adapters (for reference)
        - on_audio_fn: call with audio bytes to fan out to all providers
        - stop_fn: call to stop all providers and get final results
    """
    adapters = []
    for spec in provider_specs:
        name, config = parse_provider_spec(spec)
        if extra_config:
            config = {**config, **extra_config}
        provider = get_provider(name, config)
        provider.validate_config()

        if isinstance(provider, StreamingTranscriptionProvider):
            adapter = provider
            logger.info("[%s] native streaming provider", name)
        else:
            adapter = ChunkedStreamingAdapter(provider)
            logger.info("[%s] batch provider via ChunkedStreamingAdapter", name)

        if partial_callback:
            adapter.on_partial(lambda text, n=name: partial_callback(n, text))

        logger.info("[%s] starting streaming", name)
        adapter.start_streaming()
        logger.info("[%s] streaming started", name)
        adapters.append((spec, adapter))

    def on_audio(chunk: bytes) -> None:
        for _, adapter in adapters:
            adapter.send_audio(chunk)

    def stop() -> list[TranscriptionResult]:
        results = []
        for spec, adapter in adapters:
            name = spec.split(":")[0]
            logger.info("[%s] stopping streaming", name)
            try:
                result = adapter.stop_streaming()
                logger.info("[%s] stopped, text=%d chars", name, len(result.text))
                results.append(result)
            except Exception as e:
                logger.error("[%s] stop failed: %s", name, e, exc_info=True)
                console.print(f"[red]{spec} stop failed:[/red] {e}")
        return results

    return adapters, on_audio, stop
