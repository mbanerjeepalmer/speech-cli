# CLI Architecture Design - Dynamic SDK Passthrough

## Overview

This document outlines the architecture for a dynamic CLI that automatically generates commands from the ElevenLabs SDK introspection data.

## Design Goals

1. **Zero Maintenance**: CLI commands automatically reflect SDK changes
2. **Complete Coverage**: All 905 SDK methods accessible via CLI
3. **Type Safety**: Proper validation using SDK type hints
4. **User Friendly**: Clear command structure and help text
5. **Extensible**: Easy to add custom formatting and processing

## Architecture

### 1. Data Layer

**Input**: `docs/sdk-methods.json` (2.1MB)
- 453 sync methods with full signatures
- 25 namespaces (conversational_ai, voices, studio, etc.)
- Complete parameter metadata
- Type hints and docstrings

### 2. Command Generation Layer

**Dynamic Command Factory**:
```python
def create_command_from_method(method_data):
    """Generate a Typer command from SDK method metadata"""
    # Parse parameters
    # Create CLI options
    # Generate help text
    # Return executable command
```

**Command Structure**:
```
speech-cli <namespace> <method> [OPTIONS]
```

Examples:
```bash
speech-cli text-to-speech convert --voice-id <id> --text "Hello"
speech-cli voices list
speech-cli history get --history-item-id <id>
```

### 3. CLI Framework: Typer

Why Typer:
- Already used in current CLI
- Excellent type hint support
- Automatic help generation
- Subcommand support
- Compatible with our architecture

### 4. Parameter Handling

**Type Conversions**:
- `str` → `typer.Option(type=str)`
- `int` → `typer.Option(type=int)`
- `bool` → `typer.Option(type=bool, is_flag=True)`
- `Optional[T]` → `typer.Option(default=None)`
- `Sequence[T]` → `typer.Option(..., multiple=True)`
- `File` → `typer.Option(type=typer.FileText)`
- Complex types (VoiceSettings) → JSON string or file input

**Special Handling**:
- `OMIT` sentinel → Skip if not provided
- `Iterator` returns → Stream to stdout or file
- `bytes` returns → Write to file
- Complex objects → JSON output

### 5. Implementation Approach

#### Option 1: Runtime Generation (RECOMMENDED)

**Pros**:
- No build step required
- Instant updates when SDK changes
- Simpler codebase
- Easier debugging

**Cons**:
- Slightly slower startup (negligible)
- JSON file must be distributed

**Implementation**:
```python
# src/speech_cli/cli_generator.py
import json
import typer
from pathlib import Path

def load_sdk_methods():
    """Load SDK introspection data"""
    json_path = Path(__file__).parent.parent / "docs" / "sdk-methods.json"
    with open(json_path) as f:
        return json.load(f)

def create_cli_app():
    """Generate complete CLI from SDK data"""
    app = typer.Typer()
    methods = load_sdk_methods()

    # Group methods by namespace
    namespaces = group_by_namespace(methods)

    # Create subcommand for each namespace
    for namespace, ns_methods in namespaces.items():
        ns_app = create_namespace_app(namespace, ns_methods)
        app.add_typer(ns_app, name=namespace.replace('_', '-'))

    return app

# src/speech_cli/__main__.py
from speech_cli.cli_generator import create_cli_app

app = create_cli_app()

if __name__ == "__main__":
    app()
```

#### Option 2: Build-Time Generation

**Pros**:
- Faster startup
- No JSON file needed at runtime
- Can be type-checked

**Cons**:
- Requires build step
- More complex deployment
- Harder to maintain

**Implementation**: Generate Python files with all commands

### 6. File Structure

```
speech-cli/
├── src/speech_cli/
│   ├── __init__.py
│   ├── __main__.py              # Entry point
│   ├── cli_generator.py         # Dynamic command generation
│   ├── parameter_handlers.py   # Type conversion logic
│   ├── output_formatters.py    # Response formatting
│   ├── client_wrapper.py       # ElevenLabs client wrapper
│   └── legacy/
│       ├── cli.py              # Old manual CLI (deprecated)
│       └── transcribe.py       # Old transcribe logic
├── docs/
│   ├── sdk-methods.json        # SDK introspection data
│   └── elevenlabs-sdk-features.md
├── scripts/
│   ├── inspect_sdk.py          # Regenerate SDK data
│   └── verify_sdk_data.py
└── pyproject.toml
```

### 7. Command Execution Flow

```
1. User runs: speech-cli text-to-speech convert --voice-id X --text "Hi"
                ↓
2. CLI loads sdk-methods.json
                ↓
3. Finds method: client.text_to_speech.convert
                ↓
4. Validates parameters against method signature
                ↓
5. Converts CLI args to Python types
                ↓
6. Initializes ElevenLabs client
                ↓
7. Navigates to method: client.text_to_speech.convert
                ↓
8. Calls method with converted parameters
                ↓
9. Formats response based on return type
                ↓
10. Outputs to stdout/file
```

### 8. Configuration Management

**API Key Handling** (same as current):
- CLI option: `--api-key`
- Environment: `ELEVENLABS_API_KEY`
- .env file

**Global Options**:
```bash
speech-cli --api-key <key> --format json --output file.json <command>
```

**Config File** (optional future enhancement):
```yaml
# ~/.config/speech-cli/config.yaml
api_key: sk_...
default_voice_id: 21m00Tcm4TlvDq8ikWAM
default_model: eleven_monolingual_v1
```

### 9. Output Formatting

**Based on Return Type**:
- `str` → Print to stdout
- `bytes` → Write to file
- `Iterator[bytes]` → Stream to file
- `dict`/object → JSON (default) or formatted table
- `list` → JSON array or table

**Format Options**:
```bash
--format json          # JSON output
--format yaml          # YAML output
--format table         # Pretty table (for lists)
--format text          # Plain text (where applicable)
--output <file>        # Write to file
```

### 10. Advanced Features

#### File Input Handling
```bash
# Direct file path
speech-cli speech-to-text convert --file audio.mp3

# Stdin
cat audio.mp3 | speech-cli speech-to-text convert --file -

# URL
speech-cli speech-to-text convert --file https://example.com/audio.mp3
```

#### Complex Type Handling
```bash
# JSON string
speech-cli text-to-speech convert \
  --voice-settings '{"stability": 0.5, "similarity_boost": 0.75}'

# JSON file
speech-cli text-to-speech convert \
  --voice-settings @settings.json
```

#### Streaming Output
```bash
# Stream audio to file
speech-cli text-to-speech convert \
  --voice-id <id> --text "Hello" --output audio.mp3

# Stream to player
speech-cli text-to-speech convert \
  --voice-id <id> --text "Hello" --output - | mpv -
```

### 11. Error Handling

**Validation Errors**:
- Missing required parameters
- Invalid types
- Invalid values

**API Errors**:
- Authentication (401)
- Rate limits (429)
- Server errors (5xx)
- Network errors

**Output**:
```bash
Error: Missing required parameter: --voice-id
Usage: speech-cli text-to-speech convert [OPTIONS]

Try 'speech-cli text-to-speech convert --help' for more information.
```

### 12. Help System

**Namespace Help**:
```bash
$ speech-cli text-to-speech --help
Usage: speech-cli text-to-speech [COMMAND]

Commands:
  convert                    Convert text to speech
  convert-with-timestamps    Convert with timing information
  stream                     Stream audio in real-time
  stream-with-timestamps     Stream with timing information
```

**Method Help**:
```bash
$ speech-cli text-to-speech convert --help
Usage: speech-cli text-to-speech convert [OPTIONS]

Convert text to speech.

Required Arguments:
  --voice-id TEXT        Voice ID to use
  --text TEXT           Text to convert

Optional Arguments:
  --model-id TEXT       Model ID [default: eleven_monolingual_v1]
  --language-code TEXT  ISO 639-1 language code
  --output-format TEXT  Audio format [default: mp3_44100_128]
  ...
```

### 13. Backward Compatibility

**Keep Legacy Commands**:
```bash
# Old command (still works)
speech-cli audio.mp3

# New equivalent
speech-cli speech-to-text convert --file audio.mp3
```

**Migration Path**:
1. Phase 1: Add new dynamic CLI alongside old
2. Phase 2: Deprecation warnings on old commands
3. Phase 3: Remove old commands (major version bump)

### 14. Testing Strategy

**Unit Tests**:
- Parameter parsing
- Type conversion
- Command generation
- Output formatting

**Integration Tests**:
- End-to-end command execution
- API mocking
- File I/O

**Snapshot Tests**:
- Help text generation
- Command structure

### 15. Performance Considerations

**Lazy Loading**:
- Load sdk-methods.json only once
- Cache parsed command structure
- Lazy import of ElevenLabs SDK

**Startup Time Target**: < 200ms

**Optimization**:
```python
# Use orjson for faster JSON parsing
import orjson

def load_sdk_methods():
    with open("sdk-methods.json", "rb") as f:
        return orjson.loads(f.read())
```

### 16. Documentation

**Auto-Generated Docs**:
- README with all commands
- Man pages
- Web documentation
- Shell completion scripts

**Maintenance**:
- Update SDK introspection: `uv run python scripts/inspect_sdk.py`
- Docs regenerate automatically from sdk-methods.json

### 17. Distribution

**Package Contents**:
```
speech-cli/
├── speech_cli/
│   └── data/
│       └── sdk-methods.json    # Bundled in package
```

**pyproject.toml**:
```toml
[tool.hatch.build.targets.wheel]
include = [
    "src/speech_cli",
    "docs/sdk-methods.json"
]
```

## Implementation Phases

### Phase 1: Core Framework (Current Focus)
- [x] SDK introspection
- [ ] CLI generator core
- [ ] Basic parameter handling
- [ ] Simple output formatting

### Phase 2: Complete Coverage
- [ ] All parameter types
- [ ] All output types
- [ ] File handling
- [ ] Streaming support

### Phase 3: Polish
- [ ] Advanced formatting
- [ ] Shell completion
- [ ] Config file
- [ ] Better error messages

### Phase 4: Migration
- [ ] Deprecate old CLI
- [ ] Update documentation
- [ ] Migration guide

## Decision: Runtime Generation

We will implement **Runtime Generation (Option 1)** because:
1. No build complexity
2. Instant SDK updates
3. Easier maintenance
4. Simpler codebase
5. Startup time is acceptable (<200ms)

## Next Steps

1. Implement `cli_generator.py` with dynamic command generation
2. Implement `parameter_handlers.py` for type conversion
3. Implement `output_formatters.py` for response formatting
4. Test with a subset of commands
5. Expand to full coverage
6. Add documentation
7. Migration path from old CLI

---

## Example: Generated Command

**SDK Method**:
```python
client.text_to_speech.convert(
    voice_id: str,
    text: str,
    model_id: Optional[str] = None,
    language_code: Optional[str] = None,
    voice_settings: Optional[VoiceSettings] = None,
    output_format: Optional[str] = None,
) -> Iterator[bytes]
```

**Generated CLI Command**:
```bash
speech-cli text-to-speech convert \
  --voice-id "21m00Tcm4TlvDq8ikWAM" \
  --text "Hello, world!" \
  --model-id "eleven_monolingual_v1" \
  --language-code "en" \
  --voice-settings '{"stability": 0.5, "similarity_boost": 0.75}' \
  --output-format "mp3_44100_128" \
  --output audio.mp3
```

**Implementation**:
```python
@app.command()
def convert(
    voice_id: str = typer.Option(..., help="Voice ID to use"),
    text: str = typer.Option(..., help="Text to convert"),
    model_id: Optional[str] = typer.Option(None, help="Model ID"),
    language_code: Optional[str] = typer.Option(None, help="Language code"),
    voice_settings: Optional[str] = typer.Option(None, help="Voice settings JSON"),
    output_format: Optional[str] = typer.Option("mp3_44100_128", help="Audio format"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
    api_key: Optional[str] = typer.Option(None, envvar="ELEVENLABS_API_KEY"),
):
    """Convert text to speech."""
    client = ElevenLabs(api_key=api_key)

    # Parse complex types
    settings = json.loads(voice_settings) if voice_settings else None

    # Call SDK method
    audio_iterator = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
        language_code=language_code,
        voice_settings=VoiceSettings(**settings) if settings else None,
        output_format=output_format,
    )

    # Handle output
    audio_bytes = b"".join(audio_iterator)
    if output:
        output.write_bytes(audio_bytes)
    else:
        sys.stdout.buffer.write(audio_bytes)
```

This architecture provides a scalable, maintainable solution that automatically reflects SDK changes and provides complete API coverage.
