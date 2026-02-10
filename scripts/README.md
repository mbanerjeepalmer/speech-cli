# SDK Introspection Scripts

This directory contains scripts for introspecting the ElevenLabs SDK and extracting method signatures for automatic CLI command generation.

## Scripts

### `inspect_sdk.py`

The main introspection script that extracts ALL method signatures from the ElevenLabs SDK.

**What it does:**
- Imports both sync (`ElevenLabs`) and async (`AsyncElevenLabs`) clients
- Recursively explores all nested client attributes
- Extracts comprehensive information for each method:
  - Full method path (e.g., `client.text_to_speech.convert`)
  - All parameters with names, types, and default values
  - Return type hints
  - Complete docstrings
  - Source file location and line number
  - Async/sync indicator

**Usage:**
```bash
uv run python scripts/inspect_sdk.py
```

**Output:**
- Creates/updates `docs/sdk-methods.json` with structured data
- Contains 905 total methods (453 sync + 452 async)
- 2.1MB JSON file with complete SDK introspection data

### `verify_sdk_data.py`

A verification and demonstration script that shows how to use the introspected SDK data.

**What it does:**
- Loads and validates the SDK methods JSON
- Prints statistics about the SDK structure
- Demonstrates various queries on the data
- Shows example CLI command generation

**Usage:**
```bash
uv run python scripts/verify_sdk_data.py
```

**Example queries demonstrated:**
1. Find all methods by name (e.g., all "convert" methods)
2. Find all methods in a namespace (e.g., text_to_speech)
3. Show detailed method signatures
4. Find methods by return type
5. Find methods with no required parameters

## Output Data Structure

The generated `docs/sdk-methods.json` has the following structure:

```json
{
  "sdk_name": "elevenlabs",
  "introspection_version": "1.0",
  "sync_client": {
    "name": "ElevenLabs",
    "methods_count": 453,
    "methods": [
      {
        "path": "client.text_to_speech.convert",
        "name": "convert",
        "parameters": [
          {
            "name": "voice_id",
            "type": "str",
            "default": null,
            "required": true,
            "kind": "POSITIONAL_OR_KEYWORD"
          },
          {
            "name": "text",
            "type": "str",
            "default": null,
            "required": true,
            "kind": "KEYWORD_ONLY"
          }
          // ... more parameters
        ],
        "return_type": "Iterator",
        "docstring": "Converts text into speech...",
        "is_async": false,
        "source_file": "/path/to/elevenlabs/text_to_speech/client.py",
        "source_line": 48
      }
      // ... more methods
    ]
  },
  "async_client": {
    // Same structure for async methods
  }
}
```

## SDK Coverage

The scripts successfully capture:

### Top-level Namespaces (25 total)
- `audio_isolation` - 4 methods
- `audio_native` - 6 methods
- `conversational_ai` - 178 methods (largest namespace)
- `dubbing` - 38 methods
- `forced_alignment` - 2 methods
- `history` - 10 methods
- `models` - 2 methods
- `music` - 10 methods
- `pronunciation_dictionaries` - 16 methods
- `samples` - 2 methods
- `service_accounts` - 10 methods
- `speech_to_speech` - 4 methods
- `speech_to_text` - 6 methods
- `studio` - 44 methods
- `text_to_dialogue` - 8 methods
- `text_to_sound_effects` - 2 methods
- `text_to_speech` - 9 methods
- `text_to_voice` - 10 methods
- `tokens` - 2 methods
- `usage` - 2 methods
- `user` - 4 methods
- `voices` - 54 methods
- `webhooks` - 9 methods
- `workspace` - 20 methods

### Nested Methods
The script correctly handles deep nesting, such as:
- `client.voices.pvc.samples.speakers.audio.get`
- `client.voices.settings.update`
- `client.conversational_ai.agents.create`

## Use Cases

This introspection data can be used for:

1. **Automatic CLI Generation**: Map SDK methods directly to CLI commands
2. **Documentation Generation**: Auto-generate API reference docs
3. **Type Safety**: Extract type hints for better tooling
4. **API Discovery**: Understand the full SDK surface area
5. **Testing**: Ensure all SDK methods are covered
6. **Code Generation**: Generate wrapper code, bindings, etc.

## Example CLI Generation

The data makes it straightforward to generate CLI commands:

```
SDK Method: client.text_to_speech.convert(voice_id, text, ...)
CLI Command: elevenlabs text-to-speech convert --voice-id <id> --text <text> [OPTIONS]
```

## Implementation Details

### Type Extraction
The script handles:
- Basic types (`str`, `int`, `bool`, `float`)
- Optional types (`Optional[T]`)
- Union types (`Union[T1, T2]`)
- Generic types (`List[T]`, `Dict[K, V]`, `Sequence[T]`)
- Iterator types (`Iterator[T]`, `AsyncIterator[T]`)
- Custom SDK types (Pydantic models, enums)

### Special Values
- `OMIT`: ElevenLabs SDK sentinel value for optional parameters
- `Ellipsis`: Python's `...` used for some defaults
- `None`: Standard Python None

### Excluded Methods
The script filters out:
- Private methods (starting with `_`)
- Special methods (`__init__`, `__repr__`, etc.)
- Internal properties (`with_raw_response`)

## Future Enhancements

Potential improvements:
1. Extract enum/literal possible values
2. Parse docstrings to extract parameter descriptions
3. Identify deprecated methods
4. Extract HTTP method and endpoint information
5. Generate OpenAPI/Swagger specs
6. Add validation rules extraction
7. Track SDK version changes over time
