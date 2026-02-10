"""Output formatting for CLI responses."""

import json
import sys
from pathlib import Path
from typing import Any, Iterator, Optional, Union

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class OutputFormatter:
    """Handles formatting and output of SDK responses."""

    @staticmethod
    def format_output(
        result: Any,
        output_format: str = "json",
        output_file: Optional[Path] = None,
    ) -> None:
        """Format and output result.

        Args:
            result: Result from SDK method
            output_format: Output format (json, yaml, text, auto)
            output_file: Optional output file path
        """
        # Handle bytes output (audio files)
        if isinstance(result, bytes):
            OutputFormatter.write_bytes(result, output_file)
            return

        # Handle Iterator (streaming)
        if isinstance(result, Iterator):
            OutputFormatter.handle_iterator(result, output_file)
            return

        # Handle text output
        if isinstance(result, str):
            OutputFormatter.write_text(result, output_file)
            return

        # Handle structured data (dict, list, objects)
        formatted = OutputFormatter.format_structured_data(result, output_format)
        OutputFormatter.write_text(formatted, output_file)

    @staticmethod
    def write_bytes(data: bytes, output_file: Optional[Path] = None) -> None:
        """Write binary data to file or stdout.

        Args:
            data: Binary data
            output_file: Output file path
        """
        if output_file:
            output_file.write_bytes(data)
            print(f"Wrote {len(data)} bytes to {output_file}", file=sys.stderr)
        else:
            sys.stdout.buffer.write(data)

    @staticmethod
    def write_text(text: str, output_file: Optional[Path] = None) -> None:
        """Write text to file or stdout.

        Args:
            text: Text to write
            output_file: Output file path
        """
        if output_file:
            output_file.write_text(text, encoding="utf-8")
            print(f"Wrote output to {output_file}", file=sys.stderr)
        else:
            print(text)

    @staticmethod
    def handle_iterator(
        iterator: Iterator, output_file: Optional[Path] = None
    ) -> None:
        """Handle iterator output (streaming).

        Args:
            iterator: Iterator to consume
            output_file: Output file path
        """
        if output_file:
            # Write all chunks to file
            with open(output_file, "wb") as f:
                total_bytes = 0
                for chunk in iterator:
                    if isinstance(chunk, bytes):
                        f.write(chunk)
                        total_bytes += len(chunk)
                    else:
                        # Handle structured streaming responses
                        chunk_bytes = json.dumps(chunk).encode() + b"\n"
                        f.write(chunk_bytes)
                        total_bytes += len(chunk_bytes)
                print(f"Wrote {total_bytes} bytes to {output_file}", file=sys.stderr)
        else:
            # Stream to stdout
            for chunk in iterator:
                if isinstance(chunk, bytes):
                    sys.stdout.buffer.write(chunk)
                else:
                    # Handle structured streaming responses (JSONL)
                    sys.stdout.write(json.dumps(chunk) + "\n")

    @staticmethod
    def format_structured_data(data: Any, output_format: str) -> str:
        """Format structured data (dict, list, objects).

        Args:
            data: Data to format
            output_format: Format type (json, yaml, text)

        Returns:
            Formatted string
        """
        # Convert to dict if it's a Pydantic model or has model_dump
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        elif hasattr(data, "dict"):
            data = data.dict()
        elif hasattr(data, "__dict__") and not isinstance(data, (dict, list, str)):
            data = data.__dict__

        if output_format == "yaml":
            if not YAML_AVAILABLE:
                print(
                    "Warning: PyYAML not installed, falling back to JSON",
                    file=sys.stderr,
                )
                return json.dumps(data, indent=2, default=str)
            return yaml.dump(data, default_flow_style=False, sort_keys=False)

        elif output_format == "text":
            # Simple text representation
            if isinstance(data, dict):
                return "\n".join(f"{k}: {v}" for k, v in data.items())
            elif isinstance(data, list):
                return "\n".join(str(item) for item in data)
            else:
                return str(data)

        else:  # json (default)
            return json.dumps(data, indent=2, default=str)

    @staticmethod
    def format_table(data: list[dict], columns: Optional[list[str]] = None) -> str:
        """Format list of dicts as a table.

        Args:
            data: List of dictionaries
            columns: Columns to include (None = all)

        Returns:
            Formatted table string
        """
        if not data:
            return "No data"

        # Determine columns
        if columns is None:
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())
            columns = sorted(all_keys)

        # Calculate column widths
        widths = {col: len(col) for col in columns}
        for item in data:
            for col in columns:
                value_str = str(item.get(col, ""))
                widths[col] = max(widths[col], len(value_str))

        # Build table
        lines = []

        # Header
        header = " | ".join(col.ljust(widths[col]) for col in columns)
        lines.append(header)
        lines.append("-" * len(header))

        # Rows
        for item in data:
            row = " | ".join(
                str(item.get(col, "")).ljust(widths[col]) for col in columns
            )
            lines.append(row)

        return "\n".join(lines)


class SRTFormatter:
    """Format transcription output as SRT subtitles."""

    @staticmethod
    def format_srt(transcription: dict) -> str:
        """Format transcription as SRT.

        Args:
            transcription: Transcription dict with segments

        Returns:
            SRT formatted string
        """
        segments = transcription.get("segments", [])
        if not segments:
            return ""

        srt_lines = []
        for i, segment in enumerate(segments, 1):
            start = SRTFormatter.format_timestamp(segment.get("start", 0))
            end = SRTFormatter.format_timestamp(segment.get("end", 0))
            text = segment.get("text", "").strip()

            srt_lines.append(str(i))
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(text)
            srt_lines.append("")  # Blank line

        return "\n".join(srt_lines)

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Format seconds as SRT timestamp (HH:MM:SS,mmm).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class VTTFormatter:
    """Format transcription output as WebVTT subtitles."""

    @staticmethod
    def format_vtt(transcription: dict) -> str:
        """Format transcription as WebVTT.

        Args:
            transcription: Transcription dict with segments

        Returns:
            WebVTT formatted string
        """
        segments = transcription.get("segments", [])
        if not segments:
            return "WEBVTT\n"

        vtt_lines = ["WEBVTT", ""]
        for segment in segments:
            start = VTTFormatter.format_timestamp(segment.get("start", 0))
            end = VTTFormatter.format_timestamp(segment.get("end", 0))
            text = segment.get("text", "").strip()

            vtt_lines.append(f"{start} --> {end}")
            vtt_lines.append(text)
            vtt_lines.append("")  # Blank line

        return "\n".join(vtt_lines)

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Format seconds as VTT timestamp (HH:MM:SS.mmm).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
