"""Tests for transcription run storage and formats."""

import json

import pytest

from speech_cli.eval.providers.base import TranscriptionResult, TranscriptionSegment
from speech_cli.eval.storage.eval_run import TranscriptionRun
from speech_cli.eval.storage.formats import result_to_dict, result_to_verbose_json


class TestTranscriptionRun:
    def test_setup_creates_directories(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake audio")

        run = TranscriptionRun(
            audio_file=str(audio),
            providers=["whisper-cpp"],
            base_dir=tmp_path / "runs",
        ).setup()

        assert run.run_dir.exists()
        assert run.input_dir.exists()
        assert run.output_dir.exists()
        assert run.assessment_dir.exists()
        assert (run.input_dir / "test.wav").exists()
        assert (run.run_dir / "metadata.json").exists()

    def test_metadata_content(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        run = TranscriptionRun(
            audio_file=str(audio),
            providers=["whisper-cpp", "groq"],
            base_dir=tmp_path / "runs",
        ).setup()

        meta = json.loads((run.run_dir / "metadata.json").read_text())
        assert meta["providers"] == ["whisper-cpp", "groq"]
        assert "created" in meta

    def test_save_result(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        run = TranscriptionRun(
            audio_file=str(audio),
            providers=["test"],
            base_dir=tmp_path / "runs",
        ).setup()

        data = {"text": "hello", "segments": []}
        path = run.save_result("whisper-cpp", "ggml-tiny-en", data)

        assert path.exists()
        saved = json.loads(path.read_text())
        assert saved["text"] == "hello"

    def test_save_result_filename_sanitization(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        run = TranscriptionRun(
            audio_file=str(audio),
            providers=["test"],
            base_dir=tmp_path / "runs",
        ).setup()

        path = run.save_result("groq", "whisper/large.v3", {"text": "hi"})
        assert "/" not in path.name

    def test_load_run(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        run = TranscriptionRun(
            audio_file=str(audio),
            providers=["test"],
            base_dir=tmp_path / "runs",
        ).setup()

        run.save_result("test", "model", {"text": "hi", "segments": []})

        loaded = TranscriptionRun.load_run(run.run_dir)
        assert "metadata" in loaded
        assert "results" in loaded
        assert len(loaded["results"]) == 1

    def test_load_run_missing_dir(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            TranscriptionRun.load_run(tmp_path / "nonexistent")

    def test_run_dir_naming(self, tmp_path):
        audio = tmp_path / "jfk.wav"
        audio.write_bytes(b"fake")

        run = TranscriptionRun(
            audio_file=str(audio),
            providers=["test"],
            base_dir=tmp_path / "runs",
        )
        # Run dir should contain the audio file stem
        assert "jfk" in run.run_dir.name

    def test_explicit_run_dir(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        custom_dir = tmp_path / "my_run"
        run = TranscriptionRun(
            audio_file=str(audio),
            providers=["test"],
            run_dir=custom_dir,
        ).setup()

        assert run.run_dir == custom_dir
        assert custom_dir.exists()


class TestFormats:
    def _make_result(self):
        return TranscriptionResult(
            provider_name="test",
            model_name="test-model",
            text="hello world",
            segments=[
                TranscriptionSegment(text="hello", start=0.0, end=0.5),
                TranscriptionSegment(text="world", start=0.5, end=1.0, speaker="A"),
            ],
            language="en",
            processing_time_seconds=1.5,
        )

    def test_result_to_verbose_json(self):
        result = self._make_result()
        vj = result_to_verbose_json(result)

        assert vj["task"] == "transcribe"
        assert vj["language"] == "en"
        assert vj["text"] == "hello world"
        assert len(vj["segments"]) == 2
        assert vj["segments"][0]["id"] == 0
        assert vj["segments"][0]["start"] == 0.0
        assert vj["segments"][1]["speaker"] == "A"
        assert vj["provider"] == "test"
        assert vj["model"] == "test-model"
        assert vj["processing_time_seconds"] == 1.5

    def test_result_to_dict(self):
        result = self._make_result()
        d = result_to_dict(result)

        assert d["provider_name"] == "test"
        assert d["text"] == "hello world"
        assert len(d["segments"]) == 2

    def test_verbose_json_is_serializable(self):
        result = self._make_result()
        vj = result_to_verbose_json(result)
        # Should not raise
        json.dumps(vj)
