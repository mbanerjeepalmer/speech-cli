"""Output formatters for transcription results."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict


class OutputFormatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def format(self, transcription_data: Dict[str, Any]) -> str:
        """Format the transcription data.

        Args:
            transcription_data: The raw transcription data from the API

        Returns:
            Formatted string output
        """
        pass


class TextFormatter(OutputFormatter):
    """Format transcription as plain text."""

    def format(self, transcription_data: Dict[str, Any]) -> str:
        """Extract and return just the text content.

        Args:
            transcription_data: The raw transcription data from the API

        Returns:
            Plain text transcription
        """
        # Handle different possible response structures
        if isinstance(transcription_data, dict):
            # Try common field names
            for field in ["text", "transcription", "transcript"]:
                if field in transcription_data:
                    return str(transcription_data[field])

            # If no standard field found, return the whole dict as string
            return str(transcription_data)

        # If it's already a string, return it
        return str(transcription_data)


class JSONFormatter(OutputFormatter):
    """Format transcription as JSON."""

    def format(self, transcription_data: Dict[str, Any]) -> str:
        """Return the transcription data as formatted JSON.

        Args:
            transcription_data: The raw transcription data from the API

        Returns:
            JSON formatted string
        """
        return json.dumps(transcription_data, indent=2, ensure_ascii=False)


class SRTFormatter(OutputFormatter):
    """Format transcription as SRT subtitles."""

    def format(self, transcription_data: Dict[str, Any]) -> str:
        """Convert transcription to SRT subtitle format.

        Args:
            transcription_data: The raw transcription data from the API
                Expected to contain 'segments' with timing information

        Returns:
            SRT formatted string
        """
        # Check if the data has segments with timing information
        if isinstance(transcription_data, dict) and "segments" in transcription_data:
            segments = transcription_data["segments"]
            srt_output = []

            for i, segment in enumerate(segments, start=1):
                start_time = self._format_timestamp(segment.get("start", 0))
                end_time = self._format_timestamp(segment.get("end", 0))
                text = segment.get("text", "").strip()

                srt_output.append(f"{i}")
                srt_output.append(f"{start_time} --> {end_time}")
                srt_output.append(text)
                srt_output.append("")  # Empty line between segments

            return "\n".join(srt_output)

        # If no segments, create a simple single-segment SRT
        text = self._extract_text(transcription_data)
        return "1\n00:00:00,000 --> 99:59:59,999\n" + text + "\n"

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as SRT timestamp (HH:MM:SS,mmm).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _extract_text(self, data: Any) -> str:
        """Extract text from transcription data."""
        if isinstance(data, dict):
            for field in ["text", "transcription", "transcript"]:
                if field in data:
                    return str(data[field])
        return str(data)


class VTTFormatter(OutputFormatter):
    """Format transcription as WebVTT subtitles."""

    def format(self, transcription_data: Dict[str, Any]) -> str:
        """Convert transcription to WebVTT subtitle format.

        Args:
            transcription_data: The raw transcription data from the API
                Expected to contain 'segments' with timing information

        Returns:
            WebVTT formatted string
        """
        vtt_output = ["WEBVTT", ""]

        # Check if the data has segments with timing information
        if isinstance(transcription_data, dict) and "segments" in transcription_data:
            segments = transcription_data["segments"]

            for segment in segments:
                start_time = self._format_timestamp(segment.get("start", 0))
                end_time = self._format_timestamp(segment.get("end", 0))
                text = segment.get("text", "").strip()

                vtt_output.append(f"{start_time} --> {end_time}")
                vtt_output.append(text)
                vtt_output.append("")  # Empty line between segments

            return "\n".join(vtt_output)

        # If no segments, create a simple single-segment VTT
        text = self._extract_text(transcription_data)
        return "WEBVTT\n\n00:00:00.000 --> 99:59:59.999\n" + text + "\n"

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as WebVTT timestamp (HH:MM:SS.mmm).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def _extract_text(self, data: Any) -> str:
        """Extract text from transcription data."""
        if isinstance(data, dict):
            for field in ["text", "transcription", "transcript"]:
                if field in data:
                    return str(data[field])
        return str(data)


def get_formatter(format_type: str) -> OutputFormatter:
    """Get the appropriate formatter for the given format type.

    Args:
        format_type: The desired output format (text, json, srt, vtt)

    Returns:
        An instance of the appropriate formatter

    Raises:
        ValueError: If the format type is not supported
    """
    formatters = {
        "text": TextFormatter,
        "json": JSONFormatter,
        "srt": SRTFormatter,
        "vtt": VTTFormatter,
    }

    format_type = format_type.lower()
    if format_type not in formatters:
        raise ValueError(
            f"Unsupported format: {format_type}. "
            f"Supported formats: {', '.join(formatters.keys())}"
        )

    return formatters[format_type]()
