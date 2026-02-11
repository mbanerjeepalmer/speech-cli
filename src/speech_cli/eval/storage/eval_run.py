"""Transcription run directory management."""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


DEFAULT_RUNS_DIR = Path("runs")


def _slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text.strip("_")


class TranscriptionRun:
    """Manages the directory structure for a single transcription run."""

    def __init__(
        self,
        audio_file: Optional[str] = None,
        providers: Optional[list[str]] = None,
        base_dir: Optional[Path] = None,
        run_dir: Optional[Path] = None,
        name: Optional[str] = None,
    ) -> None:
        self.audio_file = Path(audio_file) if audio_file else None
        self.providers = providers or []

        if run_dir:
            self.run_dir = run_dir
        else:
            base = base_dir or DEFAULT_RUNS_DIR
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            if name:
                stem = _slugify(name)
            elif self.audio_file:
                stem = self.audio_file.stem
            else:
                stem = "mic"
            self.run_dir = base / f"{timestamp}_{stem}"

        self.input_dir = self.run_dir / "input"
        self.output_dir = self.run_dir / "output"
        self.assessment_dir = self.run_dir / "assessment"

    def setup(self) -> "TranscriptionRun":
        """Create directory structure and copy audio input."""
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.assessment_dir.mkdir(exist_ok=True)

        # Copy audio to input dir (if audio file was provided)
        if self.audio_file:
            dest = self.input_dir / self.audio_file.name
            if self.audio_file.is_file() and not dest.exists():
                shutil.copy2(str(self.audio_file), str(dest))

        # Write metadata
        metadata = {
            "created": datetime.now().isoformat(),
            "audio_file": str(self.audio_file) if self.audio_file else None,
            "providers": self.providers,
        }
        (self.run_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n"
        )

        return self

    def set_audio_file(self, path: Path) -> None:
        """Retroactively copy an audio file into the run's input directory."""
        self.audio_file = path
        dest = self.input_dir / path.name
        if path.is_file() and not dest.exists():
            shutil.copy2(str(path), str(dest))

    def save_result(self, provider_name: str, model_name: str, result: dict) -> Path:
        """Save a provider result as JSON in the output directory.

        Args:
            provider_name: e.g. "whisper-cpp"
            model_name: e.g. "ggml-tiny-en"
            result: Serializable result dictionary.

        Returns:
            Path to the written file.
        """
        safe_model = model_name.replace("/", "_").replace(".", "-")
        filename = f"{provider_name}_{safe_model}.json"
        path = self.output_dir / filename
        path.write_text(json.dumps(result, indent=2, default=str) + "\n")
        return path

    @staticmethod
    def load_run(run_dir: Path) -> dict:
        """Load metadata and results from an existing run directory."""
        metadata_path = run_dir / "metadata.json"
        if not metadata_path.is_file():
            raise FileNotFoundError(f"No metadata.json in {run_dir}")

        metadata = json.loads(metadata_path.read_text())

        results = {}
        output_dir = run_dir / "output"
        if output_dir.is_dir():
            for f in sorted(output_dir.glob("*.json")):
                results[f.stem] = json.loads(f.read_text())

        return {"metadata": metadata, "results": results}
