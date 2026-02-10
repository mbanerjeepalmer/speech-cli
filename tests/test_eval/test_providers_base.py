"""Tests for provider base classes."""

from speech_cli.eval.providers.base import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionSegment,
)


def test_transcription_segment_defaults():
    seg = TranscriptionSegment(text="hello", start=0.0, end=1.0)
    assert seg.text == "hello"
    assert seg.start == 0.0
    assert seg.end == 1.0
    assert seg.speaker is None
    assert seg.confidence is None


def test_transcription_segment_with_all_fields():
    seg = TranscriptionSegment(
        text="hello", start=0.0, end=1.0, speaker="SPEAKER_0", confidence=0.95
    )
    assert seg.speaker == "SPEAKER_0"
    assert seg.confidence == 0.95


def test_transcription_result_defaults():
    result = TranscriptionResult(
        provider_name="test", model_name="test-model", text="hello world"
    )
    assert result.provider_name == "test"
    assert result.model_name == "test-model"
    assert result.text == "hello world"
    assert result.segments == []
    assert result.language is None
    assert result.processing_time_seconds is None
    assert result.raw_response is None


def test_transcription_result_with_segments():
    segs = [TranscriptionSegment(text="hi", start=0.0, end=0.5)]
    result = TranscriptionResult(
        provider_name="test",
        model_name="m",
        text="hi",
        segments=segs,
        language="en",
        processing_time_seconds=1.23,
    )
    assert len(result.segments) == 1
    assert result.language == "en"
    assert result.processing_time_seconds == 1.23


def test_provider_is_abstract():
    """TranscriptionProvider cannot be instantiated directly."""
    try:
        TranscriptionProvider()
        assert False, "Should have raised TypeError"
    except TypeError:
        pass


def test_provider_default_diarization():
    """Default supports_diarization returns False."""

    class DummyProvider(TranscriptionProvider):
        name = "dummy"
        model_name = "dummy"

        def transcribe_file(self, path):
            return TranscriptionResult(
                provider_name=self.name, model_name=self.model_name, text=""
            )

        def validate_config(self):
            pass

    p = DummyProvider()
    assert p.supports_diarization() is False
