"""Parameter type conversion and handling for CLI commands."""

import json
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse
from urllib.request import urlopen


class ParameterHandler:
    """Handles conversion of CLI parameters to SDK types."""

    @staticmethod
    def handle_file_input(file_input: str) -> Union[BytesIO, Any]:
        """Handle file input from various sources.

        Args:
            file_input: File path, URL, or '-' for stdin

        Returns:
            File-like object or bytes
        """
        if file_input == "-":
            # Read from stdin
            import sys
            return BytesIO(sys.stdin.buffer.read())

        # Check if it's a URL
        parsed = urlparse(file_input)
        if parsed.scheme in ("http", "https"):
            # Download from URL
            with urlopen(file_input) as response:
                return BytesIO(response.read())

        # Local file path
        path = Path(file_input)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_input}")

        return open(path, "rb")

    @staticmethod
    def parse_json_parameter(value: Optional[str]) -> Optional[Dict[str, Any]]:
        """Parse JSON parameter from string or file.

        Args:
            value: JSON string or @file.json reference

        Returns:
            Parsed JSON dict or None
        """
        if not value:
            return None

        # Check if it's a file reference (@file.json)
        if value.startswith("@"):
            file_path = Path(value[1:])
            if not file_path.exists():
                raise FileNotFoundError(f"JSON file not found: {file_path}")
            return json.loads(file_path.read_text())

        # Parse as JSON string
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    @staticmethod
    def parse_sequence_parameter(values: Optional[list]) -> Optional[list]:
        """Parse sequence parameter (multiple values).

        Args:
            values: List of string values

        Returns:
            Parsed list or None
        """
        if not values:
            return None
        return values

    @staticmethod
    def convert_to_type(value: Any, type_hint: str) -> Any:
        """Convert value to the appropriate Python type.

        Args:
            value: Input value
            type_hint: Type hint string from SDK introspection

        Returns:
            Converted value
        """
        if value is None:
            return None

        # Handle basic types
        if "str" in type_hint:
            return str(value)
        elif "int" in type_hint:
            return int(value)
        elif "float" in type_hint:
            return float(value)
        elif "bool" in type_hint:
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)

        # Handle complex types (already parsed)
        return value

    @staticmethod
    def should_omit_parameter(value: Any, default: Any) -> bool:
        """Check if parameter should be omitted (OMIT sentinel).

        Args:
            value: Parameter value
            default: Default value from signature

        Returns:
            True if parameter should be omitted
        """
        # If value is None and default is Ellipsis (OMIT), omit it
        if value is None and default is ...:
            return True
        return False

    @staticmethod
    def prepare_parameters(
        cli_params: Dict[str, Any],
        method_params: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Prepare CLI parameters for SDK method call.

        Args:
            cli_params: Parameters from CLI
            method_params: Parameter metadata from SDK introspection

        Returns:
            Prepared parameters for SDK call
        """
        prepared = {}

        for param_name, param_value in cli_params.items():
            # Skip if None and should be omitted
            param_metadata = method_params.get(param_name, {})
            default = param_metadata.get("default")

            if ParameterHandler.should_omit_parameter(param_value, default):
                continue

            # Handle special parameter types
            type_hint = param_metadata.get("annotation", "")

            # File parameters
            if "File" in type_hint or param_name in ("file", "audio", "audio_file"):
                if param_value:
                    prepared[param_name] = ParameterHandler.handle_file_input(param_value)
                continue

            # JSON parameters (complex objects)
            if any(
                keyword in type_hint
                for keyword in ("VoiceSettings", "Settings", "Config")
            ):
                if param_value:
                    prepared[param_name] = ParameterHandler.parse_json_parameter(
                        param_value
                    )
                continue

            # Sequence parameters
            if "Sequence" in type_hint or "List" in type_hint:
                if param_value:
                    prepared[param_name] = ParameterHandler.parse_sequence_parameter(
                        param_value
                    )
                continue

            # Regular parameters
            if param_value is not None:
                prepared[param_name] = ParameterHandler.convert_to_type(
                    param_value, type_hint
                )

        return prepared


class VoiceSettingsHandler:
    """Handle voice settings parsing and creation."""

    @staticmethod
    def parse_voice_settings(settings_input: Optional[str]) -> Optional[Any]:
        """Parse voice settings from JSON.

        Args:
            settings_input: JSON string or file reference

        Returns:
            VoiceSettings object or None
        """
        if not settings_input:
            return None

        from elevenlabs import VoiceSettings

        settings_dict = ParameterHandler.parse_json_parameter(settings_input)
        if not settings_dict:
            return None

        return VoiceSettings(**settings_dict)

    @staticmethod
    def create_voice_settings(
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None,
        style: Optional[float] = None,
        use_speaker_boost: Optional[bool] = None,
    ) -> Optional[Any]:
        """Create VoiceSettings object from individual parameters.

        Args:
            stability: Stability value (0.0-1.0)
            similarity_boost: Similarity boost (0.0-1.0)
            style: Style exaggeration (0.0-1.0)
            use_speaker_boost: Enable speaker boost

        Returns:
            VoiceSettings object or None
        """
        # Only create if at least one parameter is provided
        if all(
            v is None
            for v in [stability, similarity_boost, style, use_speaker_boost]
        ):
            return None

        from elevenlabs import VoiceSettings

        kwargs = {}
        if stability is not None:
            kwargs["stability"] = stability
        if similarity_boost is not None:
            kwargs["similarity_boost"] = similarity_boost
        if style is not None:
            kwargs["style"] = style
        if use_speaker_boost is not None:
            kwargs["use_speaker_boost"] = use_speaker_boost

        return VoiceSettings(**kwargs)
