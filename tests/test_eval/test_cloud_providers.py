"""Tests for cloud providers (all mocked - no real API calls)."""

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from speech_cli.eval.providers.base import TranscriptionResult


class TestElevenLabsProvider:
    def test_validate_config_no_key(self):
        from speech_cli.eval.providers.elevenlabs_provider import ElevenLabsProvider

        p = ElevenLabsProvider(api_key=None)
        with patch.dict("os.environ", {}, clear=True):
            p.api_key = None
            with pytest.raises(RuntimeError, match="API key not set"):
                p.validate_config()

    def test_validate_config_with_key(self):
        from speech_cli.eval.providers.elevenlabs_provider import ElevenLabsProvider

        p = ElevenLabsProvider(api_key="test-key")
        p.validate_config()  # should not raise

    def test_supports_diarization(self):
        from speech_cli.eval.providers.elevenlabs_provider import ElevenLabsProvider

        p = ElevenLabsProvider(api_key="k")
        assert p.supports_diarization() is True

    def test_transcribe_file(self, tmp_path):
        from speech_cli.eval.providers.elevenlabs_provider import ElevenLabsProvider

        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "text": "hello world",
            "words": [
                {"text": "hello", "start": 0.0, "end": 0.5},
                {"text": "world", "start": 0.5, "end": 1.0},
            ],
            "language_code": "en",
        }
        mock_client = MagicMock()
        mock_client.speech_to_text.convert.return_value = mock_response

        with patch("elevenlabs.ElevenLabs", return_value=mock_client):
            p = ElevenLabsProvider(api_key="test-key")
            result = p.transcribe_file(str(audio))

        assert isinstance(result, TranscriptionResult)
        assert result.text == "hello world"
        assert len(result.segments) == 2


class TestGroqProvider:
    def test_validate_config_no_key(self):
        from speech_cli.eval.providers.groq_provider import GroqProvider

        p = GroqProvider(api_key=None)
        with patch.dict("os.environ", {}, clear=True):
            p.api_key = None
            with pytest.raises(RuntimeError, match="API key not set"):
                p.validate_config()

    @patch.dict("os.environ", {"GROQ_API_KEY": "test"})
    def test_validate_config_missing_package(self):
        from speech_cli.eval.providers.groq_provider import GroqProvider

        p = GroqProvider(api_key="test")
        assert p.name == "groq"

    def test_transcribe_file(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "text": "hello from groq",
            "segments": [
                {"text": "hello from groq", "start": 0.0, "end": 2.0},
            ],
            "language": "en",
        }
        mock_client_instance = MagicMock()
        mock_client_instance.audio.transcriptions.create.return_value = mock_response

        # Create a fake groq module
        fake_groq = ModuleType("groq")
        fake_groq.Groq = MagicMock(return_value=mock_client_instance)

        with patch.dict(sys.modules, {"groq": fake_groq}):
            from speech_cli.eval.providers.groq_provider import GroqProvider

            p = GroqProvider(api_key="test")
            result = p.transcribe_file(str(audio))

        assert result.text == "hello from groq"
        assert len(result.segments) == 1


class TestMistralProvider:
    def test_validate_config_no_key(self):
        from speech_cli.eval.providers.mistral_provider import MistralProvider

        p = MistralProvider(api_key=None)
        with patch.dict("os.environ", {}, clear=True):
            p.api_key = None
            with pytest.raises(RuntimeError, match="API key not set"):
                p.validate_config()

    def test_transcribe_file(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "choices": [
                {"message": {"content": "hello from mistral"}}
            ],
        }
        mock_client_instance = MagicMock()
        mock_client_instance.chat.complete.return_value = mock_response

        fake_mistralai = ModuleType("mistralai")
        fake_mistralai.Mistral = MagicMock(return_value=mock_client_instance)

        with patch.dict(sys.modules, {"mistralai": fake_mistralai}):
            from speech_cli.eval.providers.mistral_provider import MistralProvider

            p = MistralProvider(api_key="test")
            result = p.transcribe_file(str(audio))

        assert result.text == "hello from mistral"


class TestHuggingFaceProvider:
    def test_validate_config_no_key(self):
        from speech_cli.eval.providers.huggingface_provider import HuggingFaceProvider

        p = HuggingFaceProvider(api_key=None)
        with patch.dict("os.environ", {}, clear=True):
            p.api_key = None
            with pytest.raises(RuntimeError, match="API key not set"):
                p.validate_config()

    def test_transcribe_file(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        mock_output = MagicMock()
        mock_output.text = "hello from huggingface"
        mock_output.chunks = [
            {"text": "hello", "timestamp": [0.0, 0.5]},
            {"text": "from huggingface", "timestamp": [0.5, 1.5]},
        ]
        mock_client_instance = MagicMock()
        mock_client_instance.automatic_speech_recognition.return_value = mock_output

        fake_hf = ModuleType("huggingface_hub")
        fake_hf.InferenceClient = MagicMock(return_value=mock_client_instance)

        with patch.dict(sys.modules, {"huggingface_hub": fake_hf}):
            from speech_cli.eval.providers.huggingface_provider import HuggingFaceProvider

            p = HuggingFaceProvider(api_key="test")
            result = p.transcribe_file(str(audio))

        assert result.text == "hello from huggingface"
        assert len(result.segments) == 2
