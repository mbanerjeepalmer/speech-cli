"""Audio format conversion utilities."""

import subprocess
from pathlib import Path


def convert_to_wav_16k(input_path: str, output_path: str | None = None) -> str:
    """Convert audio file to 16kHz mono WAV using ffmpeg.

    This is the format expected by whisper.cpp and most STT providers.

    Args:
        input_path: Path to the input audio file.
        output_path: Path for the output WAV. Defaults to input with .wav extension.

    Returns:
        Path to the converted WAV file.
    """
    inp = Path(input_path)
    if output_path:
        out = Path(output_path)
    else:
        out = inp.with_suffix(".16k.wav")

    if out.exists() and out.stat().st_mtime >= inp.stat().st_mtime:
        return str(out)

    cmd = [
        "ffmpeg",
        "-i", str(inp),
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        "-y",
        str(out),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg conversion failed (exit {result.returncode}): {result.stderr[:500]}"
        )

    return str(out)


def is_wav_16k(path: str) -> bool:
    """Check if a file is already a 16kHz mono WAV.

    Uses ffprobe to inspect the file.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate,channels,codec_name",
        "-of", "csv=p=0",
        str(path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False
        parts = result.stdout.strip().split(",")
        if len(parts) >= 3:
            codec, sample_rate, channels = parts[0], parts[1], parts[2]
            return codec == "pcm_s16le" and sample_rate == "16000" and channels == "1"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return False
