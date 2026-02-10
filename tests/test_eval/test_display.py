"""Tests for display components."""

from speech_cli.eval.display.layouts import tail_text, truncate_text
from speech_cli.eval.display.live_display import TranscriptionDisplay
from speech_cli.eval.providers.base import TranscriptionResult


def test_tail_text_short():
    assert tail_text("hello", 10) == "hello"


def test_tail_text_exact():
    assert tail_text("hello", 5) == "hello"


def test_tail_text_truncated():
    assert tail_text("hello world", 5) == "world"


def test_truncate_text_short():
    assert truncate_text("hi", 10) == "hi"


def test_truncate_text_exact():
    assert truncate_text("hello", 5) == "hello"


def test_truncate_text_long():
    result = truncate_text("hello world", 6)
    assert len(result) == 6
    assert result.endswith("\u2026")


def test_eval_display_set_providers():
    display = TranscriptionDisplay(mode="single-line")
    display.set_providers(["whisper-cpp", "groq"])
    assert display._providers == ["whisper-cpp", "groq"]


def test_eval_display_update_result():
    display = TranscriptionDisplay(mode="single-line")
    display.set_providers(["test"])

    result = TranscriptionResult(
        provider_name="test", model_name="m", text="hello"
    )
    display.update_result("test", result)
    assert "test" in display._results


def test_eval_display_render_single_line():
    display = TranscriptionDisplay(mode="single-line")
    display.set_providers(["test"])

    result = TranscriptionResult(
        provider_name="test",
        model_name="m",
        text="hello",
        processing_time_seconds=1.0,
    )
    display.update_result("test", result)

    # Should not raise
    rendered = display._render()
    assert rendered is not None


def test_eval_display_render_multi_line():
    display = TranscriptionDisplay(mode="multi-line")
    display.set_providers(["a", "b"])

    result = TranscriptionResult(
        provider_name="a", model_name="m", text="text a", processing_time_seconds=0.5
    )
    display.update_result("a", result)

    rendered = display._render()
    assert rendered is not None


def test_eval_display_render_waiting():
    """Providers without results show 'waiting...'."""
    display = TranscriptionDisplay(mode="single-line")
    display.set_providers(["pending-provider"])

    rendered = display._render_single_line()
    assert rendered is not None
