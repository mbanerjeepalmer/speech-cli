"""Tests for validators module."""

import os
import tempfile
from pathlib import Path

import pytest

from speech_cli.errors import ValidationError
from speech_cli.validators import (
    validate_audio_file,
    validate_language_code,
    validate_output_format,
    validate_output_path,
)


def test_validate_audio_file_success():
    """Test that valid audio files pass validation."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(b"fake audio data")
        temp_path = f.name

    try:
        result = validate_audio_file(temp_path)
        assert isinstance(result, Path)
        assert result.exists()
    finally:
        os.unlink(temp_path)


def test_validate_audio_file_not_found():
    """Test that missing files raise ValidationError."""
    with pytest.raises(ValidationError, match="File not found"):
        validate_audio_file("nonexistent.mp3")


def test_validate_audio_file_unsupported_format():
    """Test that unsupported formats raise ValidationError."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"text file")
        temp_path = f.name

    try:
        with pytest.raises(ValidationError, match="Unsupported file format"):
            validate_audio_file(temp_path)
    finally:
        os.unlink(temp_path)


def test_validate_output_format_valid():
    """Test that valid formats pass validation."""
    assert validate_output_format("text") == "text"
    assert validate_output_format("JSON") == "json"
    assert validate_output_format("SRT") == "srt"
    assert validate_output_format("vtt") == "vtt"


def test_validate_output_format_invalid():
    """Test that invalid formats raise ValidationError."""
    with pytest.raises(ValidationError, match="Unsupported output format"):
        validate_output_format("invalid")


def test_validate_language_code_valid():
    """Test that valid language codes pass validation."""
    assert validate_language_code("en") == "en"
    assert validate_language_code("ES") == "es"
    assert validate_language_code(None) is None


def test_validate_language_code_invalid():
    """Test that invalid language codes raise ValidationError."""
    with pytest.raises(ValidationError, match="Invalid language code"):
        validate_language_code("invalid")

    with pytest.raises(ValidationError, match="Invalid language code"):
        validate_language_code("e")


def test_validate_output_path_none():
    """Test that None output path returns None."""
    assert validate_output_path(None) is None


def test_validate_output_path_valid():
    """Test that valid output paths pass validation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "output.txt")
        result = validate_output_path(output_path)
        assert isinstance(result, Path)
