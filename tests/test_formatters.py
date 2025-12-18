"""Tests for formatters module."""

import json

import pytest

from speech_cli.formatters import (
    JSONFormatter,
    SRTFormatter,
    TextFormatter,
    VTTFormatter,
    get_formatter,
)


def test_text_formatter():
    """Test TextFormatter extracts text correctly."""
    formatter = TextFormatter()

    # Test with dict containing 'text' field
    data = {"text": "Hello world", "other": "data"}
    assert formatter.format(data) == "Hello world"

    # Test with dict containing 'transcription' field
    data = {"transcription": "Test transcription"}
    assert formatter.format(data) == "Test transcription"


def test_json_formatter():
    """Test JSONFormatter produces valid JSON."""
    formatter = JSONFormatter()

    data = {"text": "Hello world", "language": "en"}
    result = formatter.format(data)

    # Should be valid JSON
    parsed = json.loads(result)
    assert parsed["text"] == "Hello world"
    assert parsed["language"] == "en"


def test_srt_formatter_with_segments():
    """Test SRTFormatter with segment data."""
    formatter = SRTFormatter()

    data = {
        "segments": [
            {"start": 0.0, "end": 5.0, "text": "First segment"},
            {"start": 5.0, "end": 10.0, "text": "Second segment"},
        ]
    }

    result = formatter.format(data)

    # Check SRT format structure
    assert "1\n" in result
    assert "00:00:00,000 --> 00:00:05,000" in result
    assert "First segment" in result
    assert "2\n" in result
    assert "00:00:05,000 --> 00:00:10,000" in result
    assert "Second segment" in result


def test_srt_formatter_without_segments():
    """Test SRTFormatter without segment data."""
    formatter = SRTFormatter()

    data = {"text": "Simple text"}
    result = formatter.format(data)

    # Should create a single segment
    assert "1\n" in result
    assert "Simple text" in result


def test_vtt_formatter_with_segments():
    """Test VTTFormatter with segment data."""
    formatter = VTTFormatter()

    data = {
        "segments": [
            {"start": 0.0, "end": 5.0, "text": "First segment"},
        ]
    }

    result = formatter.format(data)

    # Check WebVTT format
    assert result.startswith("WEBVTT\n")
    assert "00:00:00.000 --> 00:00:05.000" in result
    assert "First segment" in result


def test_get_formatter():
    """Test get_formatter returns correct formatter instances."""
    assert isinstance(get_formatter("text"), TextFormatter)
    assert isinstance(get_formatter("json"), JSONFormatter)
    assert isinstance(get_formatter("srt"), SRTFormatter)
    assert isinstance(get_formatter("vtt"), VTTFormatter)

    # Test case insensitivity
    assert isinstance(get_formatter("JSON"), JSONFormatter)


def test_get_formatter_invalid():
    """Test get_formatter raises error for invalid format."""
    with pytest.raises(ValueError, match="Unsupported format"):
        get_formatter("invalid")
