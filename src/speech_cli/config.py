"""Configuration management for speech-cli."""

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from speech_cli.constants import ENV_API_KEY, ENV_FILE_NAME
from speech_cli.errors import ConfigurationError


def get_api_key(cli_key: Optional[str] = None) -> str:
    """Get the ElevenLabs API key from various sources with priority.

    Priority order:
    1. Command-line argument
    2. Environment variable
    3. .env file in current working directory
    4. .env file in user's home directory

    Args:
        cli_key: Optional API key passed via command-line argument

    Returns:
        The API key string

    Raises:
        ConfigurationError: If no API key is found in any source
    """
    # Priority 1: Command-line argument
    if cli_key:
        return cli_key

    # Priority 2: Environment variable (already loaded)
    env_key = os.getenv(ENV_API_KEY)
    if env_key:
        return env_key

    # Priority 3: .env file in current working directory
    cwd_env = Path.cwd() / ENV_FILE_NAME
    if cwd_env.exists():
        load_dotenv(cwd_env)
        _check_env_file_permissions(cwd_env)
        env_key = os.getenv(ENV_API_KEY)
        if env_key:
            return env_key

    # Priority 4: .env file in user's home directory
    home_env = Path.home() / ENV_FILE_NAME
    if home_env.exists():
        load_dotenv(home_env)
        _check_env_file_permissions(home_env)
        env_key = os.getenv(ENV_API_KEY)
        if env_key:
            return env_key

    # No API key found in any source
    raise ConfigurationError(
        "ElevenLabs API key not found",
        details=(
            "Please provide your API key using one of these methods:\n"
            f"  1. Command-line: --api-key YOUR_KEY\n"
            f"  2. Environment variable: {ENV_API_KEY}\n"
            f"  3. .env file in current directory\n"
            f"  4. .env file in home directory\n\n"
            "Get your API key from: https://elevenlabs.io/app/settings/api-keys"
        ),
    )


def _check_env_file_permissions(env_file: Path) -> None:
    """Check if .env file has secure permissions and warn if not.

    Args:
        env_file: Path to the .env file to check
    """
    # Only check permissions on Unix-like systems
    if sys.platform == "win32":
        return

    try:
        stat_info = env_file.stat()
        # Check if file is world-readable (other permissions & read bit)
        if stat_info.st_mode & 0o004:
            print(
                f"Warning: {env_file} is world-readable. "
                "Consider restricting permissions with: chmod 600 {env_file}",
                file=sys.stderr,
            )
    except OSError:
        # If we can't check permissions, just continue
        pass


def validate_api_key(api_key: str) -> None:
    """Validate the format of the API key.

    Args:
        api_key: The API key to validate

    Raises:
        ConfigurationError: If the API key format is invalid
    """
    if not api_key or not api_key.strip():
        raise ConfigurationError("API key cannot be empty")

    # Basic validation - ElevenLabs API keys are typically alphanumeric strings
    # This is a loose check to catch obvious mistakes
    if len(api_key) < 10:
        raise ConfigurationError(
            "API key appears to be too short",
            details="ElevenLabs API keys are typically longer. "
            "Please verify your API key.",
        )
