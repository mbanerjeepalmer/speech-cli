# SDK Introspection Quick Reference

## Quick Start

### Run Introspection
```bash
uv run python scripts/inspect_sdk.py
```
Output: `docs/sdk-methods.json` (2.1MB, 905 methods)

### Explore the Data
```bash
uv run python scripts/verify_sdk_data.py
```

### See CLI Generation Examples
```bash
uv run python scripts/example_cli_generator.py
```

## JSON Structure

```json
{
  "sdk_name": "elevenlabs",
  "introspection_version": "1.0",
  "sync_client": {
    "name": "ElevenLabs",
    "methods_count": 453,
    "methods": [...]
  },
  "async_client": {
    "name": "AsyncElevenLabs",
    "methods_count": 452,
    "methods": [...]
  }
}
```

## Method Object Schema

Each method in the `methods` array has:

```json
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
    }
  ],
  "return_type": "Iterator",
  "docstring": "Full method documentation...",
  "is_async": false,
  "source_file": "/path/to/source.py",
  "source_line": 48
}
```

## Common Queries with Python

### Load the Data
```python
import json
with open('docs/sdk-methods.json') as f:
    data = json.load(f)
methods = data['sync_client']['methods']
```

### Find Methods by Name
```python
convert_methods = [m for m in methods if m['name'] == 'convert']
```

### Find Methods by Path Prefix
```python
tts_methods = [m for m in methods if m['path'].startswith('client.text_to_speech')]
```

### Find Methods with Required Params
```python
required_params = [m for m in methods if any(p['required'] for p in m['parameters'])]
```

### Find Methods by Return Type
```python
iterators = [m for m in methods if 'Iterator' in m['return_type']]
```

### Get All Namespaces
```python
namespaces = {m['path'].split('.')[1] for m in methods if len(m['path'].split('.')) > 1}
```

## Common Queries with jq

### Count total methods
```bash
jq '.sync_client.methods_count + .async_client.methods_count' docs/sdk-methods.json
```

### List all method paths
```bash
jq '.sync_client.methods[].path' docs/sdk-methods.json
```

### Get text_to_speech methods
```bash
jq '.sync_client.methods[] | select(.path | startswith("client.text_to_speech"))' docs/sdk-methods.json
```

### Find methods with "convert" in name
```bash
jq '.sync_client.methods[] | select(.name == "convert")' docs/sdk-methods.json
```

### Get method with most parameters
```bash
jq '.sync_client.methods | max_by(.parameters | length)' docs/sdk-methods.json
```

### Count methods per namespace
```bash
jq '.sync_client.methods | group_by(.path | split(".")[1]) | map({key: .[0].path | split(".")[1], count: length})' docs/sdk-methods.json
```

### List all return types
```bash
jq '[.sync_client.methods[].return_type] | unique | sort' docs/sdk-methods.json
```

## CLI Generation Patterns

### Method to CLI Command
```
SDK:  client.text_to_speech.convert
CLI:  elevenlabs text-to-speech convert

SDK:  client.voices.get_all
CLI:  elevenlabs voices get-all
```

### Parameter to CLI Option
```
SDK:  voice_id: str (required)
CLI:  --voice-id <value>

SDK:  model_id: Optional[str] = None
CLI:  --model-id <value> (optional)

SDK:  enable_logging: Optional[bool]
CLI:  --enable-logging / --no-enable-logging
```

### Type Mapping (Click)
```python
str         -> click.STRING
int         -> click.INT
bool        -> click.BOOL
float       -> click.FLOAT
List[str]   -> click.STRING (multiple=True)
```

### Type Mapping (Typer)
```python
str         -> str
int         -> int
bool        -> bool
float       -> float
Optional[T] -> T = None
```

## Key Statistics

- **Total Methods**: 905 (453 sync + 452 async)
- **Namespaces**: 25
- **Total Parameters**: 2,154
- **Avg Params/Method**: 4.8
- **File Size**: 2.1 MB JSON

## Top Namespaces

1. conversational_ai (178 methods)
2. voices (54 methods)
3. studio (44 methods)
4. dubbing (38 methods)
5. workspace (20 methods)

## Use Cases

1. **CLI Generation** - Map methods to commands automatically
2. **Documentation** - Generate API reference docs
3. **Testing** - Ensure SDK coverage
4. **Discovery** - Explore available methods
5. **Validation** - Check parameter requirements
6. **Code Gen** - Create wrappers/bindings

## Files

- `/scripts/inspect_sdk.py` - Run introspection
- `/scripts/verify_sdk_data.py` - Verify and explore
- `/scripts/example_cli_generator.py` - See examples
- `/scripts/README.md` - Full documentation
- `/docs/sdk-methods.json` - Introspection data

## Next Steps

1. Use the JSON data to generate CLI commands
2. Create command routing based on method paths
3. Map parameters to CLI options automatically
4. Extract help text from docstrings
5. Handle special types (files, enums, etc.)
6. Implement streaming for Iterator return types
