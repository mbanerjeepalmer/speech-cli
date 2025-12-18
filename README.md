# speech-cli

A command-line tool for transcribing audio files using the ElevenLabs API.

## Features

- 🎙️ Transcribe audio files using ElevenLabs' powerful speech-to-text API
- 📄 Multiple output formats: text, JSON, SRT subtitles, WebVTT
- 🔑 Flexible API key management (CLI, environment variable, or .env file)
- 🌍 Language specification support
- 💾 Save output to files or stdout
- 🎨 Coloured terminal output (optional)
- 🔄 Automatic retry logic for network errors
- ✅ Comprehensive input validation

## Installation

### Using uvx (recommended)

Run without installation:

```bash
uvx --from git+https://github.com/yourusername/speech-cli speech-cli audio.mp3
```

### Using pip

```bash
pip install speech-cli
```

### From source

```bash
git clone https://github.com/yourusername/speech-cli
cd speech-cli
uv sync
uv run speech-cli audio.mp3
```

## Configuration

Get your API key from [ElevenLabs](https://elevenlabs.io/app/settings/api-keys).

### Option 1: Environment Variable

```bash
export ELEVENLABS_API_KEY=your_api_key_here
```

### Option 2: .env File

Create a `.env` file in your current directory or home directory:

```env
ELEVENLABS_API_KEY=your_api_key_here
```

### Option 3: Command-line Argument

```bash
speech-cli audio.mp3 --api-key your_api_key_here
```

Priority order: CLI argument > environment variable > .env file (current directory) > .env file (home directory)

## Usage

### Basic Examples

Transcribe an audio file to text (default):

```bash
speech-cli audio.mp3
```

Transcribe to JSON format:

```bash
speech-cli audio.mp3 --format json
```

Save output to a file:

```bash
speech-cli audio.mp3 --output transcript.txt
```

Specify the source language:

```bash
speech-cli audio.mp3 --language es
```

### Advanced Examples

Transcribe to SRT subtitles:

```bash
speech-cli audio.mp3 --format srt --output subtitles.srt
```

Use a specific model:

```bash
speech-cli audio.mp3 --model scribe_v1_experimental
```

Disable coloured output:

```bash
speech-cli audio.mp3 --no-color
```

### All Options

```
Usage: speech-cli [OPTIONS] AUDIO_FILE

Arguments:
  AUDIO_FILE  Path to the audio file to transcribe [required]

Options:
  -f, --format TEXT       Output format (text, json, srt, vtt) [default: text]
  -o, --output TEXT       Path to write output to (default: stdout)
  -k, --api-key TEXT      ElevenLabs API key
  -l, --language TEXT     ISO 639-1 language code (e.g., 'en', 'es', 'fr')
  -m, --model TEXT        Model to use for transcription [default: scribe_v1]
  --no-color              Disable coloured output
  -v, --version           Show version and exit
  --help                  Show this message and exit
```

## Supported Audio Formats

- MP3 (.mp3)
- MP4 (.mp4)
- MPEG (.mpeg, .mpga)
- M4A (.m4a)
- WAV (.wav)
- WebM (.webm)

Maximum file size: 500 MB

## Output Formats

### text (default)

Plain text transcription:

```
This is the transcribed text from your audio file.
```

### json

Structured JSON with metadata:

```json
{
  "text": "This is the transcribed text from your audio file.",
  "language": "en",
  "segments": [...]
}
```

### srt

SRT subtitle format:

```
1
00:00:00,000 --> 00:00:05,000
This is the transcribed text from your audio file.
```

### vtt

WebVTT subtitle format:

```
WEBVTT

00:00:00.000 --> 00:00:05.000
This is the transcribed text from your audio file.
```

## Error Handling

The tool provides clear error messages with specific exit codes:

- 0: Success
- 1: General error
- 2: Configuration error (missing or invalid API key)
- 3: Validation error (invalid input)
- 4: API error
- 5: Network error
- 6: File error

## Development

### Setup

```bash
git clone https://github.com/yourusername/speech-cli
cd speech-cli
uv sync --extra dev
```

### Run Tests

```bash
uv run pytest
```

### Run with Coverage

```bash
uv run pytest --cov=speech_cli --cov-report=html
```

## Requirements

- Python 3.8+
- ElevenLabs API key

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
- [Get API Key](https://elevenlabs.io/app/settings/api-keys)
