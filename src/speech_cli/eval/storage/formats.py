"""Result serialization helpers."""

from dataclasses import asdict

from speech_cli.eval.providers.base import TranscriptionResult


def result_to_verbose_json(result: TranscriptionResult) -> dict:
    """Convert a TranscriptionResult to OpenAI Whisper verbose_json format.

    This is the de facto standard for STT output interchange.
    """
    segments = []
    for i, seg in enumerate(result.segments):
        segments.append({
            "id": i,
            "start": seg.start,
            "end": seg.end,
            "text": seg.text,
            "speaker": seg.speaker,
            "confidence": seg.confidence,
        })

    return {
        "task": "transcribe",
        "language": result.language,
        "text": result.text,
        "segments": segments,
        "provider": result.provider_name,
        "model": result.model_name,
        "processing_time_seconds": result.processing_time_seconds,
    }


def result_to_dict(result: TranscriptionResult) -> dict:
    """Convert a TranscriptionResult to a plain dict."""
    return asdict(result)
