"""whisper.cpp transcription provider via subprocess."""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

from speech_cli.eval.providers.base import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionSegment,
)

DEFAULT_BINARY = os.path.expanduser(
    "~/Dropbox/Projects/whisper.cpp/build/bin/main"
)
DEFAULT_MODEL = os.path.expanduser(
    "~/Dropbox/Projects/whisper.cpp/models/ggml-tiny.en.bin"
)


class WhisperCppProvider(TranscriptionProvider):
    """Transcription provider using whisper.cpp via subprocess."""

    def __init__(
        self,
        binary: Optional[str] = None,
        model: Optional[str] = None,
        diarize: bool = False,
        language: Optional[str] = None,
    ) -> None:
        self.binary = binary or os.environ.get("WHISPER_CPP_BINARY", DEFAULT_BINARY)
        self.model = model or os.environ.get("WHISPER_CPP_MODEL", DEFAULT_MODEL)
        self.diarize = diarize
        self.language = language
        self.name = "whisper-cpp"
        self.model_name = Path(self.model).stem

    def validate_config(self) -> None:
        """Check that the binary and model file exist."""
        if not Path(self.binary).is_file():
            raise RuntimeError(
                f"whisper.cpp binary not found: {self.binary}. "
                "Set WHISPER_CPP_BINARY env var or pass --binary."
            )
        if not Path(self.model).is_file():
            raise RuntimeError(
                f"whisper.cpp model not found: {self.model}. "
                "Set WHISPER_CPP_MODEL env var or pass --model."
            )

    def supports_diarization(self) -> bool:
        return self.diarize

    def transcribe_file(self, path: str) -> TranscriptionResult:
        """Run whisper.cpp on an audio file and parse JSON output."""
        audio_path = Path(path).resolve()
        if not audio_path.is_file():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_prefix = str(Path(tmpdir) / "result")

            cmd = [
                self.binary,
                "-m", self.model,
                "-f", str(audio_path),
                "-ojf",  # output full JSON
                "-of", output_prefix,  # output file prefix
                "-np",  # no prints (progress)
            ]

            if self.diarize:
                cmd.append("-di")  # enable diarization (tinydiarize)

            if self.language:
                cmd.extend(["-l", self.language])

            start_time = time.monotonic()

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            elapsed = time.monotonic() - start_time

            if result.returncode != 0:
                raise RuntimeError(
                    f"whisper.cpp exited with code {result.returncode}: "
                    f"{result.stderr.strip()}"
                )

            # whisper.cpp writes <prefix>.json with -ojf
            json_path = Path(f"{output_prefix}.json")
            if not json_path.is_file():
                raise RuntimeError(
                    f"whisper.cpp did not produce expected JSON at {json_path}. "
                    f"stdout: {result.stdout[:500]}"
                )

            raw = json.loads(json_path.read_text())

        return self._parse_output(raw, elapsed)

    def _parse_output(self, raw: dict, elapsed: float) -> TranscriptionResult:
        """Parse whisper.cpp full JSON output into TranscriptionResult."""
        segments = []
        full_text_parts = []

        for item in raw.get("transcription", []):
            text = item.get("text", "").strip()
            if not text:
                continue

            timestamps = item.get("timestamps", {})
            start = _ts_to_seconds(timestamps.get("from", "00:00:00.000"))
            end = _ts_to_seconds(timestamps.get("to", "00:00:00.000"))

            # Offsets can also be direct fields
            if "offsets" in item:
                start = item["offsets"].get("from", 0) / 1000.0
                end = item["offsets"].get("to", 0) / 1000.0

            speaker = None
            if "speaker" in item:
                speaker = item["speaker"]

            segments.append(
                TranscriptionSegment(
                    text=text,
                    start=start,
                    end=end,
                    speaker=speaker,
                )
            )
            full_text_parts.append(text)

        return TranscriptionResult(
            provider_name=self.name,
            model_name=self.model_name,
            text=" ".join(full_text_parts),
            segments=segments,
            language=raw.get("result", {}).get("language", None),
            processing_time_seconds=round(elapsed, 3),
            raw_response=raw,
        )


def _ts_to_seconds(ts: str) -> float:
    """Convert timestamp string 'HH:MM:SS.mmm' to seconds."""
    try:
        parts = ts.split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        return float(ts)
    except (ValueError, AttributeError):
        return 0.0
