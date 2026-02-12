"""Provider discovery and instantiation."""

from typing import Optional

from speech_cli.constants import DEFAULT_MODELS, PROVIDER_MODELS, Provider
from speech_cli.eval.providers.base import TranscriptionProvider

# Lazy provider map: Provider enum -> (module_path, class_name)
_PROVIDER_MAP = {
    Provider.WHISPER_CPP: (
        "speech_cli.eval.providers.whisper_cpp",
        "WhisperCppProvider",
    ),
    Provider.ELEVENLABS: (
        "speech_cli.eval.providers.elevenlabs_provider",
        "ElevenLabsProvider",
    ),
    Provider.GROQ: (
        "speech_cli.eval.providers.groq_provider",
        "GroqProvider",
    ),
    Provider.MISTRAL: (
        "speech_cli.eval.providers.mistral_provider",
        "MistralProvider",
    ),
    Provider.HUGGINGFACE: (
        "speech_cli.eval.providers.huggingface_provider",
        "HuggingFaceProvider",
    ),
}


def list_providers() -> list[str]:
    """Return list of registered provider names."""
    return sorted(p.value for p in _PROVIDER_MAP.keys())


def _resolve_provider(name: str) -> Provider:
    """Resolve a string to a Provider enum, raising a helpful error if invalid."""
    try:
        return Provider(name)
    except ValueError:
        available = ", ".join(sorted(p.value for p in Provider))
        raise ValueError(
            f"Unknown provider '{name}'. Available providers: {available}"
        )


def _validate_model(provider: Provider, model: str) -> None:
    """Validate a model name against the known models for a provider."""
    valid_models = PROVIDER_MODELS.get(provider, [])
    if valid_models and model not in valid_models:
        models_list = ", ".join(valid_models)
        raise ValueError(
            f"Unknown model '{model}' for provider '{provider.value}'. "
            f"Available models: {models_list}"
        )


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
    provider_enum = _resolve_provider(name)

    module_path, class_name = _PROVIDER_MAP[provider_enum]

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
    """Parse a provider spec string.

    Supports two syntaxes:
    - Slash syntax: 'groq/whisper-large-v3-turbo'
    - Legacy colon syntax: 'whisper-cpp:diarize=true,model=large'

    Args:
        spec: Provider spec string.

    Returns:
        Tuple of (provider_name, config_dict).
    """
    # Slash syntax: provider/model
    if "/" in spec and ":" not in spec.split("/", 1)[0]:
        name, model = spec.split("/", 1)
        provider_enum = _resolve_provider(name)
        _validate_model(provider_enum, model)
        return name, {"model": model}

    # Legacy colon syntax: provider:key=val,...
    if ":" in spec:
        name, params_str = spec.split(":", 1)
        _resolve_provider(name)  # validate provider name
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

    # Bare provider name
    _resolve_provider(spec)  # validate
    return spec, {}
