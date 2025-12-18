"""Custom exceptions for speech-cli."""

from typing import Optional

from speech_cli.constants import ExitCode


class SpeechCLIError(Exception):
    """Base exception for all speech-cli errors."""

    exit_code: ExitCode = ExitCode.GENERAL_ERROR

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        """Initialise the exception.

        Args:
            message: The error message
            details: Optional additional details about the error
        """
        self.message = message
        self.details = details
        super().__init__(message)

    def format_message(self) -> str:
        """Format the complete error message with details."""
        if self.details:
            return f"{self.message}\n{self.details}"
        return self.message


class ConfigurationError(SpeechCLIError):
    """Raised when there's a configuration problem."""

    exit_code = ExitCode.CONFIG_ERROR


class ValidationError(SpeechCLIError):
    """Raised when input validation fails."""

    exit_code = ExitCode.VALIDATION_ERROR


class APIError(SpeechCLIError):
    """Raised when the API returns an error."""

    exit_code = ExitCode.API_ERROR


class NetworkError(SpeechCLIError):
    """Raised when there's a network connectivity issue."""

    exit_code = ExitCode.NETWORK_ERROR


class FileError(SpeechCLIError):
    """Raised when there's a file operation error."""

    exit_code = ExitCode.FILE_ERROR


class AuthenticationError(APIError):
    """Raised when API authentication fails."""

    def __init__(
        self, message: str = "Authentication failed", details: Optional[str] = None
    ) -> None:
        """Initialise authentication error with default message."""
        super().__init__(message, details)


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self, message: str = "API rate limit exceeded", details: Optional[str] = None
    ) -> None:
        """Initialise rate limit error with default message."""
        super().__init__(message, details)
