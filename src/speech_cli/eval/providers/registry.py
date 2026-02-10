"""Provider discovery and instantiation."""

from typing import Optional

from speech_cli.eval.providers.base import TranscriptionProvider

# Lazy provider map: name -> (module_path, class_name)
_PROVIDER_MAP = {
    "whisper-cpp": (
        "speech_cli.eval.providers.whisper_cpp",
        "WhisperCppProvider",
    ),
    "elevenlabs": (
        "speech_cli.eval.providers.elevenlabs_provider",
        "ElevenLabsProvider",
    ),
    "groq": (
        "speech_cli.eval.providers.groq_provider",
        "GroqProvider",
    ),
    "mistral": (
        "speech_cli.eval.providers.mistral_provider",
        "MistralProvider",
    ),
    "huggingface": (
        "speech_cli.eval.providers.huggingface_provider",
        "HuggingFaceProvider",
    ),
}


def list_providers() -> list[str]:
    """Return list of registered provider names."""
    return sorted(_PROVIDER_MAP.keys())


def get_provider(
    name: str,
    config: Optional[dict] = None,
) -> TranscriptionProvider:
    """Instantiate a provider by name.

    Args:
        name: Provider name (e.g. "whisper-cpp", "groq").
        config: Optional config overrides passed to provider constructor.

    Returns:
        Instantiated TranscriptionProvider.

    Raises:
        ValueError: If provider name is unknown.
        ImportError: If provider dependencies are not installed.
    """
    if name not in _PROVIDER_MAP:
        available = ", ".join(list_providers())
        raise ValueError(f"Unknown provider '{name}'. Available: {available}")

    module_path, class_name = _PROVIDER_MAP[name]

    import importlib

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(
            f"Provider '{name}' requires additional dependencies: {e}. "
            f"Install with: uv pip install speech-cli[{name}]"
        ) from e

    cls = getattr(module, class_name)
    return cls(**(config or {}))


def parse_provider_spec(spec: str) -> tuple[str, dict]:
    """Parse a provider spec string like 'whisper-cpp:diarize=true,model=large'.

    Args:
        spec: Provider spec string.

    Returns:
        Tuple of (provider_name, config_dict).
    """
    if ":" not in spec:
        return spec, {}

    name, params_str = spec.split(":", 1)
    config = {}
    for param in params_str.split(","):
        param = param.strip()
        if "=" in param:
            key, value = param.split("=", 1)
            # Coerce booleans
            if value.lower() in ("true", "1", "yes"):
                config[key.strip()] = True
            elif value.lower() in ("false", "0", "no"):
                config[key.strip()] = False
            else:
                config[key.strip()] = value.strip()
        elif param:
            config[param] = True

    return name, config
