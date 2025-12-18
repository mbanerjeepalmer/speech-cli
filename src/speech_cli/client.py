"""ElevenLabs API client wrapper with retry logic."""

import time
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse
from urllib.request import urlopen

from elevenlabs import ElevenLabs
from elevenlabs.core import ApiError

from speech_cli.constants import (
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    RETRY_BACKOFF,
    RETRY_DELAY,
)
from speech_cli.errors import (
    APIError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
)


class TranscriptionClient:
    """Wrapper around ElevenLabs client with retry logic and error handling."""

    def __init__(self, api_key: str, timeout: int = REQUEST_TIMEOUT) -> None:
        """Initialise the transcription client.

        Args:
            api_key: ElevenLabs API key
            timeout: Request timeout in seconds
        """
        self.client = ElevenLabs(api_key=api_key, timeout=float(timeout))

    def transcribe(
        self,
        audio_file: Union[Path, str],
        language: Optional[str] = None,
        model_id: str = "scribe_v1",
    ) -> Dict[str, Any]:
        """Transcribe an audio file.

        Args:
            audio_file: Path to the audio file or URL
            language: Optional ISO 639-1 language code
            model_id: The model to use for transcription

        Returns:
            Dictionary containing the transcription result

        Raises:
            AuthenticationError: If API authentication fails
            RateLimitError: If API rate limit is exceeded
            APIError: For other API errors
            NetworkError: For network connectivity issues
        """
        attempt = 0
        last_error = None

        while attempt < MAX_RETRIES:
            try:
                # Check if audio_file is a URL or local path
                is_url = isinstance(audio_file, str) and urlparse(audio_file).scheme in ('http', 'https')

                if is_url:
                    # Download from URL
                    with urlopen(audio_file) as response:
                        audio_data = response.read()
                        # Call the speech-to-text API with binary data
                        from io import BytesIO
                        result = self.client.speech_to_text.convert(
                            model_id=model_id,
                            file=BytesIO(audio_data),
                            language_code=language if language else None,
                        )
                else:
                    # Open local file in binary mode
                    with open(audio_file, "rb") as f:
                        # Call the speech-to-text API
                        result = self.client.speech_to_text.convert(
                            model_id=model_id,
                            file=f,
                            language_code=language if language else None,
                        )

                # Convert the response to a dictionary
                return self._process_response(result)

            except ApiError as e:
                # Handle specific API errors
                status_code = getattr(e, "status_code", None)

                if status_code == 401:
                    raise AuthenticationError(
                        "Invalid API key",
                        details="Please check your ElevenLabs API key and try again.",
                    ) from e

                if status_code == 429:
                    raise RateLimitError(
                        "API rate limit exceeded",
                        details="Please wait a moment and try again.",
                    ) from e

                if status_code in (500, 502, 503, 504):
                    # Server errors - retry
                    last_error = e
                    attempt += 1
                    if attempt < MAX_RETRIES:
                        delay = RETRY_DELAY * (RETRY_BACKOFF**attempt)
                        time.sleep(delay)
                        continue

                # Other API errors - don't retry
                raise APIError(
                    f"API error: {str(e)}",
                    details=f"Status code: {status_code}" if status_code else None,
                ) from e

            except (ConnectionError, TimeoutError, OSError) as e:
                # Network errors - retry (includes URLError from urlopen)
                last_error = e
                attempt += 1
                if attempt < MAX_RETRIES:
                    delay = RETRY_DELAY * (RETRY_BACKOFF**attempt)
                    time.sleep(delay)
                    continue

                raise NetworkError(
                    "Network error occurred",
                    details="Please check your internet connection and try again.",
                ) from e

            except Exception as e:
                # Unexpected errors - don't retry
                raise APIError(f"Unexpected error: {str(e)}") from e

        # If we exhausted all retries
        if last_error:
            raise NetworkError(
                f"Failed after {MAX_RETRIES} attempts",
                details=str(last_error),
            ) from last_error

        raise APIError("Transcription failed for unknown reason")

    def _process_response(self, response: Any) -> Dict[str, Any]:
        """Process the API response into a standard dictionary format.

        Args:
            response: The API response object

        Returns:
            Dictionary containing the transcription data
        """
        # Convert the response object to a dictionary
        # The ElevenLabs SDK returns a response object with attributes
        if hasattr(response, "model_dump"):
            return response.model_dump()
        elif hasattr(response, "dict"):
            return response.dict()
        elif isinstance(response, dict):
            return response
        else:
            # Fallback: try to extract common fields
            result = {}
            if hasattr(response, "text"):
                result["text"] = response.text
            if hasattr(response, "segments"):
                result["segments"] = response.segments
            if hasattr(response, "language"):
                result["language"] = response.language

            return result if result else {"text": str(response)}
