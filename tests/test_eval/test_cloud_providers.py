"""Tests for cloud providers (all mocked - no real API calls)."""

import asyncio
import struct
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


def _make_pcm_chunk(n_samples=1600, amplitude=1000):
    """Create a PCM int16 chunk."""
    return struct.pack(f"<{n_samples}h", *([amplitude] * n_samples))


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

        mock_segment = MagicMock()
        mock_segment.text = "hello from mistral"
        mock_segment.start = 0.0
        mock_segment.end = 2.0

        mock_response = MagicMock()
        mock_response.text = "hello from mistral"
        mock_response.segments = [mock_segment]
        mock_response.language = "en"
        mock_response.model_dump.return_value = {
            "text": "hello from mistral",
            "segments": [{"text": "hello from mistral", "start": 0.0, "end": 2.0}],
            "language": "en",
        }
        mock_client_instance = MagicMock()
        mock_client_instance.audio.transcriptions.complete.return_value = mock_response

        fake_mistralai = ModuleType("mistralai")
        fake_mistralai.Mistral = MagicMock(return_value=mock_client_instance)

        with patch.dict(sys.modules, {"mistralai": fake_mistralai}):
            from speech_cli.eval.providers.mistral_provider import MistralProvider

            p = MistralProvider(api_key="test")
            result = p.transcribe_file(str(audio))

        assert result.text == "hello from mistral"
        assert len(result.segments) == 1
        assert result.segments[0].start == 0.0

    def test_is_streaming_provider(self):
        from speech_cli.eval.providers.base import StreamingTranscriptionProvider
        from speech_cli.eval.providers.mistral_provider import MistralProvider

        p = MistralProvider(api_key="test")
        assert isinstance(p, StreamingTranscriptionProvider)

    def test_streaming_lifecycle(self):
        """Test start_streaming, send_audio, stop_streaming with mocked Mistral API."""
        from speech_cli.eval.providers.mistral_provider import MistralProvider

        # Create mock event objects
        mock_delta = MagicMock()
        mock_delta.text = "hello "

        mock_delta2 = MagicMock()
        mock_delta2.text = "world"

        events = [mock_delta, mock_delta2]

        async def fake_transcribe_stream(audio_stream, model, audio_format):
            """Consume audio stream then yield events."""
            async for _ in audio_stream:
                pass
            for event in events:
                yield event

        # Build fake mistralai module with correct types
        fake_models = ModuleType("mistralai.models")
        fake_models.AudioFormat = MagicMock(return_value=MagicMock())
        fake_models.RealtimeTranscriptionError = type("RealtimeTranscriptionError", (), {})
        fake_models.TranscriptionStreamTextDelta = type("TranscriptionStreamTextDelta", (), {})

        # Make our mock events instances of the fake type
        mock_delta.__class__ = fake_models.TranscriptionStreamTextDelta
        mock_delta2.__class__ = fake_models.TranscriptionStreamTextDelta

        mock_client_instance = MagicMock()
        mock_client_instance.audio.realtime.transcribe_stream = fake_transcribe_stream

        fake_mistralai = ModuleType("mistralai")
        fake_mistralai.Mistral = MagicMock(return_value=mock_client_instance)

        # Patch must persist across the background thread's lifetime
        patcher = patch.dict(sys.modules, {
            "mistralai": fake_mistralai,
            "mistralai.models": fake_models,
        })
        patcher.start()
        try:
            p = MistralProvider(api_key="test")
            p.start_streaming()

            chunk = _make_pcm_chunk()
            p.send_audio(chunk)

            result = p.stop_streaming()
        finally:
            patcher.stop()

        assert result.text == "hello world"
        assert result.provider_name == "mistral"
        assert result.processing_time_seconds is not None

    def test_streaming_partial_callback(self):
        """Test that partial callback fires on each text delta."""
        from speech_cli.eval.providers.mistral_provider import MistralProvider

        mock_delta = MagicMock()
        mock_delta.text = "hi"

        async def fake_transcribe_stream(audio_stream, model, audio_format):
            async for _ in audio_stream:
                pass
            yield mock_delta

        fake_models = ModuleType("mistralai.models")
        fake_models.AudioFormat = MagicMock(return_value=MagicMock())
        fake_models.RealtimeTranscriptionError = type("RealtimeTranscriptionError", (), {})
        fake_models.TranscriptionStreamTextDelta = type("TranscriptionStreamTextDelta", (), {})
        mock_delta.__class__ = fake_models.TranscriptionStreamTextDelta

        mock_client_instance = MagicMock()
        mock_client_instance.audio.realtime.transcribe_stream = fake_transcribe_stream

        fake_mistralai = ModuleType("mistralai")
        fake_mistralai.Mistral = MagicMock(return_value=mock_client_instance)

        partials = []

        patcher = patch.dict(sys.modules, {
            "mistralai": fake_mistralai,
            "mistralai.models": fake_models,
        })
        patcher.start()
        try:
            p = MistralProvider(api_key="test")
            p.on_partial(lambda text: partials.append(text))
            p.start_streaming()
            p.send_audio(_make_pcm_chunk())
            result = p.stop_streaming()
        finally:
            patcher.stop()

        assert result.text == "hi"
        assert len(partials) > 0
        assert partials[-1] == "hi"

    def test_streaming_empty_audio(self):
        """Test stop_streaming with no audio sent."""
        from speech_cli.eval.providers.mistral_provider import MistralProvider

        async def fake_transcribe_stream(audio_stream, model, audio_format):
            async for _ in audio_stream:
                pass
            return
            yield  # make it an async generator

        fake_models = ModuleType("mistralai.models")
        fake_models.AudioFormat = MagicMock(return_value=MagicMock())
        fake_models.RealtimeTranscriptionError = type("RealtimeTranscriptionError", (), {})
        fake_models.TranscriptionStreamTextDelta = type("TranscriptionStreamTextDelta", (), {})

        mock_client_instance = MagicMock()
        mock_client_instance.audio.realtime.transcribe_stream = fake_transcribe_stream

        fake_mistralai = ModuleType("mistralai")
        fake_mistralai.Mistral = MagicMock(return_value=mock_client_instance)

        patcher = patch.dict(sys.modules, {
            "mistralai": fake_mistralai,
            "mistralai.models": fake_models,
        })
        patcher.start()
        try:
            p = MistralProvider(api_key="test")
            p.start_streaming()
            result = p.stop_streaming()
        finally:
            patcher.stop()

        assert result.text == ""


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
