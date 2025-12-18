╔══════════════════════════════════════════════╗
║  📋 ELEVENLABS TRANSCRIPTION CLI - SPEC     ║
║  Created: 2025-12-18                        ║
╚══════════════════════════════════════════════╝

┌──────────────────────────────────────────────┐
│ 📍 SPECIFICATION PROGRESS                    │
├──────────────────────────────────────────────┤
│ ✅ Requirements  [████████████] APPROVED    │
│ ✅ Design        [████████████] APPROVED    │
│ ✅ Tasks         [████████████] COMPLETE    │
└──────────────────────────────────────────────┘

═══════════════════════════════════════════════
📋 PHASE 1: REQUIREMENTS
═══════════════════════════════════════════════

## 1. Overview

**Feature Name:** ElevenLabs Audio Transcription CLI

**Purpose:** A production-ready command-line tool that enables developers and content creators to transcribe audio files quickly using the ElevenLabs API, with a focus on simplicity, reliability, and seamless integration into workflows.

**Business Value:**
- Reduces friction for audio transcription tasks by providing a simple CLI interface
- Enables automation and scripting of transcription workflows
- Provides immediate utility without installation via `uvx` execution
- Serves as a foundation for future audio processing features

**Target Users:**
- Developers integrating transcription into automated workflows
- Content creators needing quick audio-to-text conversion
- DevOps engineers building audio processing pipelines
- Researchers processing interview or lecture recordings

**Success Metrics:**
  • First transcription completed in < 2 minutes from discovery (via uvx)
  • API key configuration successful on first attempt > 95% of users
  • Zero runtime errors for valid audio files and API keys
  • Clear error messages resolve 90% of issues without documentation

## 2. User Stories

### 2.1 Quick Start with uvx (Must Have) 🔥
As a developer who just discovered the tool, I want to transcribe an audio file immediately using uvx without any installation, So that I can evaluate the tool's usefulness before committing to it.

**Acceptance Criteria:**
  ✓ Given I have Python 3.8+ and uv installed
  ✓ When I run `uvx --from git+https://github.com/[user]/speech-cli speech-cli transcribe audio.mp3 --api-key sk-xxx`
  ✓ Then the tool downloads, installs dependencies, and transcribes the file
  ✓ And displays the transcription text to stdout
  ✓ And completes in reasonable time (< 30s for setup + transcription time)

**Edge Cases:**
  • No internet connection during download
  • Invalid GitHub URL or repository not found
  • Python version incompatible (< 3.8)
  • uv not installed or outdated version

**Priority:** Must Have
**Effort Estimate:** M (3-4h)

### 2.2 Flexible API Key Configuration (Must Have) 🔥
As a regular user, I want multiple ways to provide my API key with clear priority order, So that I can choose the method that best fits my security and workflow requirements.

**Acceptance Criteria:**
  ✓ Given I need to authenticate with ElevenLabs
  ✓ When I provide an API key via --api-key flag, it takes highest priority
  ✓ When no flag is provided, it checks ELEVENLABS_API_KEY environment variable
  ✓ When no env var exists, it checks .env file in current directory
  ✓ When no .env file exists, it checks .env in home directory (~/.speech-cli/.env)
  ✓ Then it uses the first valid API key found
  ✓ And displays a clear error if no API key is found

**Edge Cases:**
  • Multiple .env files exist (priority order matters)
  • .env file exists but is malformed
  • API key is empty string or whitespace only
  • .env file lacks read permissions
  • API key is provided but invalid format

**Priority:** Must Have
**Effort Estimate:** M (3-4h)

### 2.3 Single Audio File Transcription (Must Have) 🔥
As a user with an audio file, I want to transcribe it with a simple command, So that I can get text output quickly without complex configuration.

**Acceptance Criteria:**
  ✓ Given I have a valid audio file (mp3, wav, m4a, flac, ogg)
  ✓ When I run `speech-cli transcribe path/to/audio.mp3`
  ✓ Then the tool uploads the file to ElevenLabs API
  ✓ And displays "Processing audio file..." status message
  ✓ And displays "Transcription complete" when finished
  ✓ And outputs the transcribed text to stdout
  ✓ And returns exit code 0 on success

**Edge Cases:**
  • File path doesn't exist
  • File path is a directory, not a file
  • File is empty (0 bytes)
  • File exceeds ElevenLabs size limits
  • File format is unsupported
  • File is corrupted or unreadable
  • Relative vs absolute paths
  • Paths with spaces or special characters
  • Network interruption during upload

**Priority:** Must Have
**Effort Estimate:** L (5-8h)

### 2.4 Output Format Options (Must Have) 🔥
As a user integrating transcription into my workflow, I want to choose the output format (text, JSON, SRT, etc.), So that I can use the output directly in my downstream processes.

**Acceptance Criteria:**
  ✓ Given I want formatted output
  ✓ When I run `speech-cli transcribe audio.mp3 --format json`
  ✓ Then the output is valid JSON matching ElevenLabs SDK response structure
  ✓ When I run with `--format text` (default), output is plain text only
  ✓ When I run with `--format srt`, output is SRT subtitle format (if SDK supports)
  ✓ When I run with invalid format, display error with available formats
  ✓ And all formats output to stdout for easy piping

**Edge Cases:**
  • Unsupported format requested
  • Format option case sensitivity (json vs JSON)
  • JSON output with special characters requiring escaping
  • Empty transcription result

**Priority:** Must Have
**Effort Estimate:** M (3-4h)

### 2.5 Output to File (Should Have)
As a user transcribing multiple files, I want to save output directly to a file instead of redirecting stdout, So that I can avoid shell redirection syntax and have clearer commands.

**Acceptance Criteria:**
  ✓ Given I want to save output to a file
  ✓ When I run `speech-cli transcribe audio.mp3 --output result.txt`
  ✓ Then the transcription is written to result.txt
  ✓ And stdout shows only status messages
  ✓ And the file is created if it doesn't exist
  ✓ When the file exists, it prompts for confirmation to overwrite
  ✓ When I use `--output result.txt --force`, it overwrites without prompting

**Edge Cases:**
  • Output directory doesn't exist
  • No write permissions for output path
  • Output path is a directory
  • Disk full during write
  • Output file is open by another process

**Priority:** Should Have
**Effort Estimate:** S (1-2h)

### 2.6 Language Specification (Should Have)
As a user transcribing non-English audio, I want to specify the source language, So that transcription accuracy improves for my content.

**Acceptance Criteria:**
  ✓ Given I have audio in a specific language
  ✓ When I run `speech-cli transcribe audio.mp3 --language es`
  ✓ Then the language hint is passed to ElevenLabs API
  ✓ When no language is specified, API auto-detects (default behavior)
  ✓ When invalid language code is provided, display error with supported languages
  ✓ And language codes follow ISO 639-1 standard (en, es, fr, de, etc.)

**Edge Cases:**
  • Unsupported language code
  • Case sensitivity of language codes
  • Language code vs full language name
  • Language hint conflicts with actual audio language

**Priority:** Should Have
**Effort Estimate:** S (1-2h)

### 2.7 Comprehensive Error Handling (Must Have) 🔥
As a user encountering problems, I want clear, actionable error messages, So that I can quickly resolve issues without hunting through documentation.

**Acceptance Criteria:**
  ✓ Given an error occurs during transcription
  ✓ When the API key is invalid, display "Invalid API key. Check your key at https://elevenlabs.io/app/settings"
  ✓ When the file format is unsupported, display "Unsupported format '.xyz'. Supported: mp3, wav, m4a, flac, ogg"
  ✓ When the API rate limit is hit, display "Rate limit exceeded. Try again in X seconds"
  ✓ When network fails, display "Network error: Unable to connect to ElevenLabs API"
  ✓ When file is too large, display "File exceeds maximum size of X MB"
  ✓ And all errors include specific details about the problem
  ✓ And all errors return non-zero exit codes
  ✓ And all errors go to stderr, not stdout

**Edge Cases:**
  • API returns unexpected error codes
  • Timeout during long transcriptions
  • Partial upload failures
  • API service downtime
  • Malformed API responses

**Priority:** Must Have
**Effort Estimate:** M (3-4h)

### 2.8 Version and Help Information (Must Have) 🔥
As a user learning the tool, I want accessible help and version information, So that I can discover features and troubleshoot compatibility issues.

**Acceptance Criteria:**
  ✓ Given I need help or version info
  ✓ When I run `speech-cli --help`, display comprehensive usage information
  ✓ When I run `speech-cli transcribe --help`, display transcribe command options
  ✓ When I run `speech-cli --version`, display version number
  ✓ And help text includes all commands, options, and examples
  ✓ And help text is formatted clearly with sections
  ✓ And examples show common use cases

**Edge Cases:**
  • Help text too long for terminal (should page appropriately)
  • Version number format consistency

**Priority:** Must Have
**Effort Estimate:** S (1-2h)

### 2.9 SDK Feature Parity (Nice to Have) 💡
As an advanced user, I want access to any additional transcription options the ElevenLabs Python SDK provides, So that I can leverage the full API capabilities.

**Acceptance Criteria:**
  ✓ Given the ElevenLabs SDK supports additional parameters
  ✓ When I run `speech-cli transcribe --help`
  ✓ Then all SDK-supported options are documented
  ✓ And options map cleanly to CLI flags
  ✓ And advanced options are clearly marked

**Edge Cases:**
  • SDK options that don't map well to CLI flags
  • SDK breaking changes in future versions

**Priority:** Nice to Have
**Effort Estimate:** M (3-4h)

## 3. Non-Functional Requirements

### 3.1 Performance
  • Cold start (via uvx from GitHub): < 30 seconds for dependency installation
  • Transcription initiation: < 3 seconds after file validation
  • Memory usage: < 100MB for CLI process (excluding audio file size)
  • File upload: Stream large files rather than loading entirely into memory
  • Startup time (installed): < 1 second to show help or begin processing

### 3.2 Security
  • **API Key Handling:**
    - Never log or print API keys in output
    - Clear API keys from memory after use
    - .env files should be added to .gitignore by default
    - Warn if .env file has overly permissive permissions (world-readable)
  • **File Access:**
    - Validate file paths to prevent directory traversal
    - Only read files, never execute or modify input files
  • **Network:**
    - Use HTTPS only for API communication
    - Validate SSL certificates
    - Timeout on long-running requests (configurable, default 5 minutes)

### 3.3 Reliability
  • **Error Recovery:**
    - Retry failed uploads up to 3 times with exponential backoff
    - Gracefully handle network interruptions
    - Clean up temporary files on exit or error
  • **Validation:**
    - Validate file existence before API calls
    - Validate file format before upload
    - Validate API key format before API calls
  • **Exit Codes:**
    - 0: Success
    - 1: General error
    - 2: Invalid arguments
    - 3: API authentication error
    - 4: API rate limit error
    - 5: Network error
    - 6: File error

### 3.4 Usability
  • **CLI Design:**
    - Follow POSIX conventions for flags
    - Provide both short (-f) and long (--format) options
    - Show progress for long operations
    - Color output support (with --no-color option)
  • **Documentation:**
    - README with quick start examples
    - Inline help text for all commands
    - Error messages include remediation steps
  • **Output:**
    - Status messages to stderr
    - Actual output (transcription) to stdout
    - Enable clean piping: `speech-cli transcribe audio.mp3 | grep keyword`

### 3.5 Compatibility
  • **Python Versions:** 3.8, 3.9, 3.10, 3.11, 3.12
  • **Operating Systems:** Linux, macOS, Windows
  • **Package Management:**
    - Must work with `uvx` (no installation)
    - Must work with `uv pip install` (local installation)
    - Must be publishable to PyPI
  • **Audio Formats:** All formats supported by ElevenLabs API
  • **Terminal Support:** UTF-8 output, ANSI color codes (optional)

### 3.6 Maintainability
  • **Code Quality:**
    - Type hints for all functions
    - Docstrings for public APIs
    - Unit test coverage > 80%
    - Integration tests for main workflows
  • **Dependencies:**
    - Minimal dependency tree
    - Pin major versions, allow minor updates
    - Regular dependency security updates
  • **Project Structure:**
    - Follow Python best practices (src layout)
    - Clear separation: CLI layer, API client layer, business logic
    - Configuration management in dedicated module

## 4. Out of Scope

**Explicitly excluded from v1:**
  • Batch processing of multiple files in a single command
  • Real-time audio transcription (streaming)
  • Audio file format conversion or preprocessing
  • Translation (transcription + translation in one step)
  • Speaker diarization (identifying different speakers)
  • Custom model training or fine-tuning
  • GUI or web interface
  • Audio playback or visualization
  • Cloud storage integration (S3, GCS, etc.)
  • Webhook or callback mechanisms
  • Job queuing for asynchronous processing

**Future Considerations:**
  • Batch processing with progress tracking
  • Configuration profiles for different use cases
  • Plugin system for custom output formatters
  • Audio preprocessing (noise reduction, normalization)
  • Cost estimation before transcription

## 5. Dependencies & Constraints

**Technical Dependencies:**
  • **ElevenLabs Python SDK:** Core transcription functionality
    - Status: Official SDK available on PyPI
    - Version: Use latest stable (>=1.0.0)
    - Risk: API changes may require updates
  • **Typer:** CLI framework
    - Status: Mature and stable
    - Version: >=0.9.0
    - Risk: Minimal, stable API
  • **python-dotenv:** .env file parsing
    - Status: Widely used, stable
    - Version: >=1.0.0
    - Risk: Minimal
  • **uv:** Package management and uvx execution
    - Status: Required by user, rapidly evolving
    - Version: Latest recommended
    - Risk: Changes in uvx behavior in future versions

**Business Constraints:**
  • Timeline: No specific deadline, focus on quality
  • Resources: Single developer
  • Budget: No cost constraints for dependencies

**External Dependencies:**
  • **ElevenLabs API:**
    - Requires valid API key
    - Subject to rate limits (varies by plan)
    - Network connectivity required
    - API uptime SLA applies
  • **Internet Access:**
    - Required for uvx initial download
    - Required for API calls
    - Firewall/proxy considerations for corporate users

**Platform Constraints:**
  • Must support uvx execution model
  • Must work without local installation
  • Must be pip-installable for users who prefer it
  • Project structure must follow uv conventions (pyproject.toml)

═══════════════════════════════════════════════
🏗️ PHASE 2: DESIGN
═══════════════════════════════════════════════

## 1. Architecture Overview

**Pattern:** Layered Architecture with Separation of Concerns

**Layers:**
```
┌─────────────────────────────────────────────┐
│          CLI Layer (Typer)                  │
│  - Command parsing & argument validation    │
│  - User interaction & output formatting     │
│  - Error display & exit code management     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│       Business Logic Layer                  │
│  - Configuration resolution                 │
│  - File validation & path handling          │
│  - Output formatting logic                  │
│  - Retry & error recovery orchestration     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│       API Client Layer                      │
│  - ElevenLabs SDK wrapper                   │
│  - Request/response handling                │
│  - Error translation (API → Domain)         │
│  - Retry logic with exponential backoff     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│       ElevenLabs Python SDK                 │
│  - HTTP communication                       │
│  - API authentication                       │
│  - Response parsing                         │
└─────────────────────────────────────────────┘
```

**Data Flow:**
```
User Command
    │
    ├─→ Typer parses arguments
    │
    ├─→ Configuration resolver finds API key
    │
    ├─→ File validator checks audio file
    │
    ├─→ API client calls ElevenLabs SDK
    │
    ├─→ Response formatter processes result
    │
    └─→ Output writer sends to stdout/file
```

**Key Architectural Decisions:**

### Decision 1: Layered Architecture
  - **What:** Separate CLI, business logic, and API client concerns
  - **Rationale:**
    - Enables testing each layer independently
    - CLI can be swapped (Typer → Click) without touching business logic
    - API client can mock ElevenLabs SDK for tests
    - Business logic remains pure and reusable
  - **Alternatives Considered:**
    - Monolithic: All logic in CLI commands (rejected: hard to test)
    - Plugin architecture: Over-engineered for v1 scope
  - **Trade-offs:**
    - Gains: Testability, maintainability, clear responsibilities
    - Losses: Slightly more files, indirection for simple operations

### Decision 2: Configuration Priority Chain
  - **What:** CLI flag → ENV var → .env (cwd) → .env (home)
  - **Rationale:**
    - CLI flags offer highest security (no file storage)
    - ENV vars standard for CI/CD and containers
    - .env (cwd) for project-specific keys
    - .env (home) for personal default
  - **Alternatives Considered:**
    - Config file (~/.speech-cli/config.yaml): More complex, yaml dependency
    - Keyring integration: Security overkill for v1
  - **Trade-offs:**
    - Gains: Flexibility, security options, predictable precedence
    - Losses: Need to check multiple locations, more error cases

### Decision 3: Synchronous I/O (No async)
  - **What:** Use synchronous file I/O and API calls
  - **Rationale:**
    - v1 handles single files only (no concurrency benefit)
    - Simpler error handling and debugging
    - ElevenLabs SDK likely synchronous
    - Easier for contributors to understand
  - **Alternatives Considered:**
    - Async I/O with asyncio: Unnecessary complexity for single-file
  - **Trade-offs:**
    - Gains: Simplicity, easier testing, lower cognitive load
    - Losses: Future batch processing requires refactor

### Decision 4: Exit Codes as Error Categories
  - **What:** Specific exit codes for error types (0-6)
  - **Rationale:**
    - Enables script-based error handling
    - Users can react differently to auth vs network errors
    - Standard practice for CLI tools
  - **Alternatives Considered:**
    - Generic exit 1 for all errors: Less useful for automation
    - JSON error output: Breaks stdout cleanliness
  - **Trade-offs:**
    - Gains: Automation-friendly, clear error categorization
    - Losses: Must maintain exit code contract

### Decision 5: stdout/stderr Separation
  - **What:** Transcription → stdout, status/errors → stderr
  - **Rationale:**
    - Enables clean piping: `speech-cli transcribe file.mp3 | wc -w`
    - Standard Unix philosophy
    - Status messages don't pollute output
  - **Alternatives Considered:**
    - All to stdout with --quiet flag: Requires extra flag
    - Structured output only: Not human-friendly by default
  - **Trade-offs:**
    - Gains: Pipeable output, Unix convention compliance
    - Losses: Users must redirect stderr if logging needed

### Decision 6: Src Layout for Package
  - **What:** Use src/speech_cli/ directory structure
  - **Rationale:**
    - Prevents accidental imports of uninstalled package
    - Forces testing against installed version
    - Python packaging best practice (PEP 517)
    - Clear namespace separation
  - **Alternatives Considered:**
    - Flat layout (speech_cli/ at root): Can import before install
  - **Trade-offs:**
    - Gains: Testing correctness, packaging clarity
    - Losses: One extra directory level

## 2. Project Structure

```
speech-cli/
├── .gitignore                    # Ignore .env, __pycache__, etc.
├── .env.example                  # Example environment variables
├── pyproject.toml                # uv project config + dependencies
├── README.md                     # Quick start, examples, installation
├── LICENSE                       # MIT or Apache 2.0
│
├── docs/
│   └── specs/
│       └── elevenlabs-transcription-cli-spec.md
│
├── src/
│   └── speech_cli/
│       ├── __init__.py           # Package version
│       ├── __main__.py           # Entry point: python -m speech_cli
│       │
│       ├── cli.py                # Typer app & command definitions
│       ├── config.py             # Configuration resolution logic
│       ├── transcribe.py         # Core transcription business logic
│       ├── client.py             # ElevenLabs API client wrapper
│       ├── validators.py         # File & input validation
│       ├── formatters.py         # Output formatting (text/json/srt)
│       ├── errors.py             # Custom exceptions & error handling
│       └── constants.py          # Exit codes, formats, defaults
│
└── tests/
    ├── __init__.py
    ├── conftest.py               # Pytest fixtures
    │
    ├── unit/
    │   ├── test_config.py        # Config resolution unit tests
    │   ├── test_validators.py    # Validation unit tests
    │   ├── test_formatters.py    # Formatter unit tests
    │   └── test_client.py        # API client unit tests (mocked)
    │
    ├── integration/
    │   ├── test_transcribe_flow.py  # End-to-end transcription
    │   └── test_cli_commands.py     # CLI integration tests
    │
    └── fixtures/
        ├── sample_audio.mp3      # Small test audio file
        └── sample_response.json  # Mock API response
```

**File Responsibilities:**

### src/speech_cli/cli.py
- Typer app instance
- `transcribe` command definition
- Argument parsing with Typer annotations
- Calls business logic layer
- Handles output display and exit codes

### src/speech_cli/config.py
- `resolve_api_key()`: Implements priority chain
- `load_dotenv_files()`: Loads .env from multiple locations
- `check_env_permissions()`: Warns on world-readable .env
- API key validation and sanitization

### src/speech_cli/transcribe.py
- `transcribe_audio()`: Main orchestration function
- Coordinates validation → API call → formatting → output
- Error recovery logic
- Status message generation

### src/speech_cli/client.py
- `ElevenLabsClient` class: Wraps SDK
- `transcribe()`: Calls SDK transcription endpoint
- Retry logic with exponential backoff
- API error translation to domain errors

### src/speech_cli/validators.py
- `validate_audio_file()`: Checks existence, format, size
- `validate_output_path()`: Checks write permissions
- `validate_format()`: Checks supported output formats
- Path normalization and sanitization

### src/speech_cli/formatters.py
- `format_transcription()`: Routes to specific formatter
- `format_text()`: Plain text output
- `format_json()`: JSON output with proper escaping
- `format_srt()`: SRT subtitle format (if supported)

### src/speech_cli/errors.py
- Custom exception hierarchy
- `SpeechCLIError` (base)
- `APIError`, `FileError`, `ConfigError` subclasses
- `handle_error()`: Translates exceptions to exit codes

### src/speech_cli/constants.py
- Exit code constants (EXIT_SUCCESS, EXIT_API_AUTH_ERROR, etc.)
- Supported formats enum
- Default values (timeout, retry attempts, etc.)
- File size limits

## 3. Component Design

### 3.1 CLI Layer (cli.py)

**Addresses:** Requirements 2.1, 2.8

**Purpose:** Entry point for user interaction, command parsing, output display

**Main Function:**
```python
import typer
from typing import Optional
from pathlib import Path
from .transcribe import transcribe_audio
from .constants import OutputFormat, EXIT_SUCCESS
from .errors import handle_error

app = typer.Typer(
    name="speech-cli",
    help="Transcribe audio files using ElevenLabs API",
    add_completion=False
)

@app.command()
def transcribe(
    audio_file: Path = typer.Argument(
        ...,
        help="Path to audio file (mp3, wav, m4a, flac, ogg)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="ElevenLabs API key (overrides env vars and .env files)",
        envvar="ELEVENLABS_API_KEY"
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--format",
        "-f",
        help="Output format: text, json, srt"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Write output to file instead of stdout"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite output file without confirmation"
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Source language code (ISO 639-1, e.g., 'en', 'es')"
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable colored output"
    )
) -> None:
    """Transcribe an audio file to text."""
    try:
        result = transcribe_audio(
            audio_file=audio_file,
            api_key=api_key,
            output_format=format,
            output_file=output,
            force_overwrite=force,
            language=language,
            use_color=not no_color
        )

        if output:
            typer.secho(f"✓ Transcription saved to {output}", fg="green", err=True)

        raise typer.Exit(EXIT_SUCCESS)

    except Exception as e:
        exit_code = handle_error(e, use_color=not no_color)
        raise typer.Exit(exit_code)


def version_callback(value: bool) -> None:
    """Display version information."""
    if value:
        from . import __version__
        typer.echo(f"speech-cli version {__version__}")
        raise typer.Exit(0)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    )
) -> None:
    """ElevenLabs Audio Transcription CLI"""
    pass


if __name__ == "__main__":
    app()
```

**Key Design Elements:**
- Typer annotations for automatic validation
- Type hints for all parameters
- Both short and long flag options
- Help text for discoverability
- Color support with --no-color escape hatch

---

### 3.2 Configuration Management (config.py)

**Addresses:** Requirement 2.2

**Purpose:** Resolve API key from multiple sources with priority

```python
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from .errors import ConfigError

def resolve_api_key(cli_key: Optional[str] = None) -> str:
    """
    Resolve API key from multiple sources in priority order:
    1. CLI argument (highest priority)
    2. ELEVENLABS_API_KEY environment variable
    3. .env file in current directory
    4. .env file in ~/.speech-cli/

    Returns:
        Validated API key

    Raises:
        ConfigError: If no valid API key found
    """
    # Priority 1: CLI argument
    if cli_key:
        key = cli_key.strip()
        if key:
            return validate_api_key(key)

    # Priority 2: Environment variable (already loaded by Typer)
    env_key = os.getenv("ELEVENLABS_API_KEY")
    if env_key:
        key = env_key.strip()
        if key:
            return validate_api_key(key)

    # Priority 3: .env in current directory
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        check_env_permissions(cwd_env)
        load_dotenv(cwd_env, override=False)
        env_key = os.getenv("ELEVENLABS_API_KEY")
        if env_key:
            key = env_key.strip()
            if key:
                return validate_api_key(key)

    # Priority 4: .env in home directory
    home_env = Path.home() / ".speech-cli" / ".env"
    if home_env.exists():
        check_env_permissions(home_env)
        load_dotenv(home_env, override=False)
        env_key = os.getenv("ELEVENLABS_API_KEY")
        if env_key:
            key = env_key.strip()
            if key:
                return validate_api_key(key)

    # No API key found
    raise ConfigError(
        "No API key found. Provide via:\n"
        "  1. --api-key flag\n"
        "  2. ELEVENLABS_API_KEY environment variable\n"
        "  3. .env file (current directory or ~/.speech-cli/)\n"
        "\n"
        "Get your API key at: https://elevenlabs.io/app/settings"
    )


def validate_api_key(key: str) -> str:
    """
    Validate API key format.

    Args:
        key: API key to validate

    Returns:
        Validated API key

    Raises:
        ConfigError: If key format is invalid
    """
    if not key or len(key) < 10:  # Basic sanity check
        raise ConfigError("Invalid API key format")

    # ElevenLabs keys might have specific prefix (e.g., 'sk_')
    # Add more validation if format is known

    return key


def check_env_permissions(env_path: Path) -> None:
    """
    Check .env file permissions and warn if world-readable.

    Args:
        env_path: Path to .env file
    """
    import stat

    try:
        mode = env_path.stat().st_mode
        if mode & stat.S_IROTH:  # World-readable
            import sys
            print(
                f"Warning: {env_path} is world-readable. "
                f"Consider: chmod 600 {env_path}",
                file=sys.stderr
            )
    except OSError:
        pass  # Can't check permissions, skip warning
```

**Key Design Elements:**
- Clear priority order documented in docstring
- Validation at each step
- Helpful error message with remediation
- Security warning for world-readable .env
- Strip whitespace to handle copy-paste errors

---

### 3.3 File Validation (validators.py)

**Addresses:** Requirements 2.3, 2.5

**Purpose:** Validate inputs before making API calls

```python
from pathlib import Path
from typing import List
from .errors import FileError
from .constants import SUPPORTED_FORMATS, MAX_FILE_SIZE_MB

def validate_audio_file(file_path: Path) -> Path:
    """
    Validate audio file exists, is readable, and has supported format.

    Args:
        file_path: Path to audio file

    Returns:
        Resolved absolute path

    Raises:
        FileError: If file is invalid
    """
    # Resolve to absolute path
    abs_path = file_path.resolve()

    # Check existence
    if not abs_path.exists():
        raise FileError(f"File not found: {file_path}")

    # Check it's a file, not directory
    if not abs_path.is_file():
        raise FileError(f"Path is not a file: {file_path}")

    # Check file size
    size_mb = abs_path.stat().st_size / (1024 * 1024)
    if size_mb == 0:
        raise FileError(f"File is empty: {file_path}")
    if size_mb > MAX_FILE_SIZE_MB:
        raise FileError(
            f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB: "
            f"{size_mb:.1f}MB"
        )

    # Check format
    extension = abs_path.suffix.lower()
    if extension not in SUPPORTED_FORMATS:
        formats_str = ", ".join(sorted(SUPPORTED_FORMATS))
        raise FileError(
            f"Unsupported format '{extension}'. "
            f"Supported: {formats_str}"
        )

    # Check readability
    if not os.access(abs_path, os.R_OK):
        raise FileError(f"File is not readable: {file_path}")

    return abs_path


def validate_output_path(output_path: Path, force: bool = False) -> Path:
    """
    Validate output path is writable and handle overwrite confirmation.

    Args:
        output_path: Desired output file path
        force: Skip confirmation if file exists

    Returns:
        Resolved absolute path

    Raises:
        FileError: If output path is invalid
    """
    abs_path = output_path.resolve()

    # Check if path is directory
    if abs_path.exists() and abs_path.is_dir():
        raise FileError(f"Output path is a directory: {output_path}")

    # Check parent directory exists
    parent = abs_path.parent
    if not parent.exists():
        raise FileError(
            f"Output directory does not exist: {parent}\n"
            f"Create it first: mkdir -p {parent}"
        )

    # Check write permission on parent directory
    if not os.access(parent, os.W_OK):
        raise FileError(f"No write permission for directory: {parent}")

    # Check if file exists and handle overwrite
    if abs_path.exists() and not force:
        import typer
        overwrite = typer.confirm(
            f"File {abs_path.name} already exists. Overwrite?",
            default=False,
            err=True
        )
        if not overwrite:
            raise FileError("Output cancelled by user")

    return abs_path


def validate_format(format_str: str) -> str:
    """
    Validate output format is supported.

    Args:
        format_str: Format string (case-insensitive)

    Returns:
        Lowercase format string

    Raises:
        FileError: If format is unsupported
    """
    from .constants import OutputFormat

    fmt = format_str.lower()
    valid_formats = [f.value for f in OutputFormat]

    if fmt not in valid_formats:
        formats_str = ", ".join(valid_formats)
        raise FileError(
            f"Unsupported format '{format_str}'. "
            f"Supported: {formats_str}"
        )

    return fmt
```

**Key Design Elements:**
- Fail fast with clear error messages
- Absolute path resolution (handles relative paths)
- Size checks before upload (save API calls)
- Format validation before API call
- Interactive confirmation for overwrites
- Remediation hints in error messages

---

### 3.4 API Client (client.py)

**Addresses:** Requirements 2.3, 2.4, 2.6, 2.7

**Purpose:** Wrap ElevenLabs SDK with retry logic and error handling

```python
import time
from typing import Optional, Dict, Any
from pathlib import Path
from elevenlabs import ElevenLabs
from .errors import APIError, NetworkError, RateLimitError, AuthenticationError
from .constants import MAX_RETRIES, RETRY_DELAY_BASE

class ElevenLabsClient:
    """Wrapper for ElevenLabs SDK with retry logic and error handling."""

    def __init__(self, api_key: str):
        """
        Initialize ElevenLabs client.

        Args:
            api_key: ElevenLabs API key
        """
        self.api_key = api_key
        self.client = ElevenLabs(api_key=api_key)

    def transcribe(
        self,
        audio_file: Path,
        language: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe audio file with retry logic.

        Args:
            audio_file: Path to audio file
            language: Optional language code
            **kwargs: Additional SDK parameters

        Returns:
            Transcription response from API

        Raises:
            APIError: On API errors
            NetworkError: On network failures
            RateLimitError: On rate limit exceeded
            AuthenticationError: On invalid API key
        """
        for attempt in range(MAX_RETRIES):
            try:
                return self._transcribe_once(audio_file, language, **kwargs)

            except AuthenticationError:
                # Don't retry authentication errors
                raise

            except RateLimitError as e:
                # Don't retry rate limits immediately
                raise

            except (NetworkError, APIError) as e:
                if attempt == MAX_RETRIES - 1:
                    # Last attempt, raise the error
                    raise

                # Exponential backoff
                delay = RETRY_DELAY_BASE * (2 ** attempt)
                import sys
                print(
                    f"Retry {attempt + 1}/{MAX_RETRIES} after {delay}s...",
                    file=sys.stderr
                )
                time.sleep(delay)

        raise APIError("Max retries exceeded")

    def _transcribe_once(
        self,
        audio_file: Path,
        language: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Single transcription attempt.

        Args:
            audio_file: Path to audio file
            language: Optional language code
            **kwargs: Additional SDK parameters

        Returns:
            Transcription response

        Raises:
            Various API errors
        """
        try:
            with open(audio_file, "rb") as f:
                # Call ElevenLabs SDK
                # Actual SDK method may differ - adjust based on SDK docs
                params = {}
                if language:
                    params["language"] = language
                params.update(kwargs)

                response = self.client.transcribe(audio=f, **params)

                return self._parse_response(response)

        except FileNotFoundError:
            raise APIError(f"Audio file disappeared during upload: {audio_file}")

        except PermissionError:
            raise APIError(f"Lost read permission on file: {audio_file}")

        except ConnectionError as e:
            raise NetworkError(
                "Unable to connect to ElevenLabs API. "
                "Check your internet connection."
            )

        except TimeoutError as e:
            raise NetworkError(
                "Request timed out. Try again or check your connection."
            )

        except Exception as e:
            # Translate SDK exceptions to domain exceptions
            error_msg = str(e).lower()

            if "401" in error_msg or "unauthorized" in error_msg:
                raise AuthenticationError(
                    "Invalid API key. Check your key at "
                    "https://elevenlabs.io/app/settings"
                )

            if "429" in error_msg or "rate limit" in error_msg:
                # Try to extract retry time from error
                retry_after = self._extract_retry_after(e)
                raise RateLimitError(
                    f"Rate limit exceeded. Try again in {retry_after} seconds."
                )

            if "400" in error_msg:
                raise APIError(f"Invalid request: {e}")

            if "500" in error_msg or "503" in error_msg:
                raise APIError(
                    "ElevenLabs API is experiencing issues. Try again later."
                )

            # Unknown error
            raise APIError(f"Unexpected API error: {e}")

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """
        Parse and validate API response.

        Args:
            response: Raw SDK response

        Returns:
            Parsed response dictionary

        Raises:
            APIError: If response is malformed
        """
        # Adjust based on actual SDK response structure
        try:
            if hasattr(response, "text"):
                return {"text": response.text}
            elif isinstance(response, dict):
                return response
            else:
                return {"text": str(response)}
        except Exception as e:
            raise APIError(f"Failed to parse API response: {e}")

    def _extract_retry_after(self, error: Exception) -> int:
        """Extract retry-after time from error, default to 60s."""
        # Try to parse retry-after from error message
        # Adjust based on actual SDK error format
        return 60
```

**Key Design Elements:**
- Retry with exponential backoff
- Error translation from SDK to domain
- Specific exceptions for different error types
- No retry on auth errors (fail fast)
- Rate limit handling with retry-after
- File streaming (not loading to memory)

---

### 3.5 Output Formatting (formatters.py)

**Addresses:** Requirement 2.4

**Purpose:** Format transcription results for different outputs

```python
import json
from typing import Dict, Any
from .constants import OutputFormat
from .errors import FormatterError

def format_transcription(
    response: Dict[str, Any],
    format: OutputFormat
) -> str:
    """
    Format transcription response based on desired output format.

    Args:
        response: API response dictionary
        format: Desired output format

    Returns:
        Formatted string ready for output

    Raises:
        FormatterError: If formatting fails
    """
    formatters = {
        OutputFormat.TEXT: format_text,
        OutputFormat.JSON: format_json,
        OutputFormat.SRT: format_srt,
    }

    formatter = formatters.get(format)
    if not formatter:
        raise FormatterError(f"No formatter for format: {format}")

    try:
        return formatter(response)
    except Exception as e:
        raise FormatterError(f"Formatting failed: {e}")


def format_text(response: Dict[str, Any]) -> str:
    """
    Format as plain text (default).

    Args:
        response: API response

    Returns:
        Plain text transcription
    """
    text = response.get("text", "")
    return text.strip()


def format_json(response: Dict[str, Any]) -> str:
    """
    Format as JSON.

    Args:
        response: API response

    Returns:
        Pretty-printed JSON string
    """
    return json.dumps(response, indent=2, ensure_ascii=False)


def format_srt(response: Dict[str, Any]) -> str:
    """
    Format as SRT subtitles (if SDK provides timestamps).

    Args:
        response: API response with segments/timestamps

    Returns:
        SRT formatted string

    Raises:
        FormatterError: If response lacks timestamp data
    """
    # Check if response has segments with timestamps
    segments = response.get("segments")
    if not segments:
        raise FormatterError(
            "SRT format requires timestamps. "
            "API response does not contain segments."
        )

    srt_lines = []
    for i, segment in enumerate(segments, start=1):
        start = segment.get("start", 0)
        end = segment.get("end", 0)
        text = segment.get("text", "").strip()

        # SRT format:
        # 1
        # 00:00:00,000 --> 00:00:05,000
        # Subtitle text
        srt_lines.append(str(i))
        srt_lines.append(f"{_format_timestamp(start)} --> {_format_timestamp(end)}")
        srt_lines.append(text)
        srt_lines.append("")  # Blank line between subtitles

    return "\n".join(srt_lines)


def _format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm).

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
```

**Key Design Elements:**
- Strategy pattern for formatters
- Each formatter isolated and testable
- Graceful degradation (SRT fails if no timestamps)
- Proper JSON escaping with ensure_ascii=False
- Clean text output (stripped whitespace)

---

### 3.6 Error Handling (errors.py)

**Addresses:** Requirement 2.7

**Purpose:** Custom exceptions and error handling logic

```python
import sys
from typing import NoReturn
from .constants import (
    EXIT_SUCCESS,
    EXIT_GENERAL_ERROR,
    EXIT_INVALID_ARGS,
    EXIT_AUTH_ERROR,
    EXIT_RATE_LIMIT_ERROR,
    EXIT_NETWORK_ERROR,
    EXIT_FILE_ERROR,
)


class SpeechCLIError(Exception):
    """Base exception for speech-cli errors."""
    exit_code = EXIT_GENERAL_ERROR


class ConfigError(SpeechCLIError):
    """Configuration errors (API key, settings)."""
    exit_code = EXIT_INVALID_ARGS


class FileError(SpeechCLIError):
    """File-related errors (not found, permissions, format)."""
    exit_code = EXIT_FILE_ERROR


class APIError(SpeechCLIError):
    """General API errors."""
    exit_code = EXIT_GENERAL_ERROR


class AuthenticationError(APIError):
    """API authentication errors."""
    exit_code = EXIT_AUTH_ERROR


class RateLimitError(APIError):
    """API rate limit errors."""
    exit_code = EXIT_RATE_LIMIT_ERROR


class NetworkError(SpeechCLIError):
    """Network connectivity errors."""
    exit_code = EXIT_NETWORK_ERROR


class FormatterError(SpeechCLIError):
    """Output formatting errors."""
    exit_code = EXIT_GENERAL_ERROR


def handle_error(error: Exception, use_color: bool = True) -> int:
    """
    Handle error, display message to stderr, and return exit code.

    Args:
        error: Exception to handle
        use_color: Whether to use colored output

    Returns:
        Appropriate exit code
    """
    if isinstance(error, SpeechCLIError):
        exit_code = error.exit_code
        message = str(error)
    else:
        exit_code = EXIT_GENERAL_ERROR
        message = f"Unexpected error: {error}"

    # Color the error message
    if use_color:
        import typer
        typer.secho(f"Error: {message}", fg="red", err=True, bold=True)
    else:
        print(f"Error: {message}", file=sys.stderr)

    return exit_code
```

**Key Design Elements:**
- Exception hierarchy for different error types
- Exit codes attached to exception classes
- Centralized error handling function
- Errors always go to stderr
- Color support with graceful degradation

---

### 3.7 Constants (constants.py)

**Addresses:** All requirements (cross-cutting)

**Purpose:** Centralized configuration and constants

```python
from enum import Enum

# Exit codes
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_INVALID_ARGS = 2
EXIT_AUTH_ERROR = 3
EXIT_RATE_LIMIT_ERROR = 4
EXIT_NETWORK_ERROR = 5
EXIT_FILE_ERROR = 6

# Supported audio formats
SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}

# File size limits (adjust based on ElevenLabs API limits)
MAX_FILE_SIZE_MB = 100  # Conservative default

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # seconds, exponential backoff

# Request timeout
REQUEST_TIMEOUT_SECONDS = 300  # 5 minutes


class OutputFormat(str, Enum):
    """Supported output formats."""
    TEXT = "text"
    JSON = "json"
    SRT = "srt"
```

**Key Design Elements:**
- All magic numbers in one place
- Enum for output formats (type-safe)
- Easy to adjust limits based on API docs
- Clear naming conventions

---

### 3.8 Business Logic Orchestration (transcribe.py)

**Addresses:** Requirements 2.3, 2.4, 2.5

**Purpose:** Orchestrate the complete transcription workflow

```python
import sys
from pathlib import Path
from typing import Optional
from .config import resolve_api_key
from .validators import validate_audio_file, validate_output_path
from .client import ElevenLabsClient
from .formatters import format_transcription
from .constants import OutputFormat


def transcribe_audio(
    audio_file: Path,
    api_key: Optional[str] = None,
    output_format: OutputFormat = OutputFormat.TEXT,
    output_file: Optional[Path] = None,
    force_overwrite: bool = False,
    language: Optional[str] = None,
    use_color: bool = True
) -> str:
    """
    Main transcription workflow orchestration.

    Args:
        audio_file: Path to audio file
        api_key: Optional API key (or None to auto-resolve)
        output_format: Desired output format
        output_file: Optional output file path
        force_overwrite: Skip confirmation if output exists
        language: Optional language code
        use_color: Use colored status messages

    Returns:
        Formatted transcription string

    Raises:
        Various errors from validation, API, formatting
    """
    # Step 1: Resolve API key
    resolved_key = resolve_api_key(api_key)

    # Step 2: Validate audio file
    print_status("Validating audio file...", use_color)
    validated_file = validate_audio_file(audio_file)

    # Step 3: Validate output path if specified
    validated_output = None
    if output_file:
        validated_output = validate_output_path(output_file, force_overwrite)

    # Step 4: Initialize API client
    client = ElevenLabsClient(api_key=resolved_key)

    # Step 5: Call API
    print_status("Processing audio file...", use_color)
    response = client.transcribe(
        audio_file=validated_file,
        language=language
    )

    # Step 6: Format output
    formatted = format_transcription(response, output_format)

    # Step 7: Write output
    if validated_output:
        validated_output.write_text(formatted, encoding="utf-8")
    else:
        # Write to stdout (actual output, not status)
        print(formatted)

    print_status("Transcription complete", use_color)

    return formatted


def print_status(message: str, use_color: bool) -> None:
    """
    Print status message to stderr.

    Args:
        message: Status message
        use_color: Whether to use color
    """
    if use_color:
        import typer
        typer.secho(message, fg="blue", err=True)
    else:
        print(message, file=sys.stderr)
```

**Key Design Elements:**
- Clear step-by-step workflow
- Status messages to stderr
- Transcription to stdout (unless --output)
- Delegates to specialized modules
- Testable (can mock each dependency)

## 4. API Integration Strategy

**ElevenLabs SDK Usage:**
```
1. Install: pip install elevenlabs
2. Initialize: client = ElevenLabs(api_key=key)
3. Transcribe: response = client.transcribe(audio=file_handle, ...)
4. Parse response based on SDK return type
```

**Error Handling:**
- Wrap all SDK calls in try-except
- Translate SDK exceptions to domain exceptions
- Retry on transient network errors
- Fail fast on auth errors

**Request Flow:**
```
User Command
    ↓
Validate inputs locally (fast fail)
    ↓
Open audio file as binary stream
    ↓
Call SDK with file handle (not bytes)
    ↓
SDK handles HTTP upload
    ↓
SDK returns transcription object
    ↓
Parse response to dict
    ↓
Format and output
```

## 5. Configuration Management Strategy

**Configuration Sources (Priority Order):**

1. **CLI Arguments** (Highest Priority)
   - Passed directly to Typer command
   - Overrides all other sources
   - Use case: One-off commands, CI/CD

2. **Environment Variables**
   - ELEVENLABS_API_KEY
   - Loaded automatically by Typer's envvar parameter
   - Use case: CI/CD, containers, shell profiles

3. **.env in Current Directory**
   - Project-specific configuration
   - Loaded via python-dotenv
   - Use case: Per-project API keys

4. **.env in ~/.speech-cli/**
   - User-global configuration
   - Fallback for personal use
   - Use case: Personal default API key

**Configuration File Format (.env):**
```bash
# ElevenLabs API Key
ELEVENLABS_API_KEY=sk_your_key_here

# Optional: Future configuration
# SPEECH_CLI_DEFAULT_FORMAT=json
# SPEECH_CLI_DEFAULT_LANGUAGE=en
```

**Security Considerations:**
- Never log API keys
- Warn if .env is world-readable
- Add .env to .gitignore template
- Clear keys from memory after use

## 6. Error Handling Strategy

**Error Categories:**

| Category | Exit Code | Retry? | Example |
|----------|-----------|--------|---------|
| Success | 0 | N/A | Transcription completed |
| General | 1 | No | Unexpected errors |
| Invalid Args | 2 | No | Invalid format specified |
| Auth Error | 3 | No | Invalid API key |
| Rate Limit | 4 | Manual | Too many requests |
| Network | 5 | Yes | Connection timeout |
| File Error | 6 | No | File not found |

**Error Message Format:**
```
Error: [Clear description of what went wrong]

[Optional: Specific details]

[Optional: Remediation steps]
```

**Examples:**
```
Error: Invalid API key. Check your key at https://elevenlabs.io/app/settings

Error: File not found: /path/to/audio.mp3

Error: Unsupported format '.xyz'. Supported: mp3, wav, m4a, flac, ogg

Error: Rate limit exceeded. Try again in 60 seconds.

Error: Network error: Unable to connect to ElevenLabs API
Check your internet connection.
```

**Retry Strategy:**
- Automatic retry for network errors (3 attempts)
- Exponential backoff: 2s, 4s, 8s
- No retry for auth, validation, or rate limit errors
- Status messages to stderr during retries

## 7. Testing Strategy

### 7.1 Unit Tests (tests/unit/)

**test_config.py:**
- Test API key resolution priority order
- Test missing API key error
- Test .env file parsing
- Test permission warnings
- Mock file system for .env locations

**test_validators.py:**
- Test file existence validation
- Test format validation
- Test file size limits
- Test output path validation
- Test overwrite confirmation logic
- Mock file system operations

**test_formatters.py:**
- Test text formatting
- Test JSON formatting
- Test SRT formatting (with timestamp data)
- Test SRT error when no timestamps
- Test empty transcriptions

**test_client.py:**
- Test retry logic with mocked failures
- Test exponential backoff timing
- Test error translation (401 → AuthenticationError)
- Test rate limit handling
- Mock ElevenLabs SDK

### 7.2 Integration Tests (tests/integration/)

**test_transcribe_flow.py:**
- End-to-end transcription with real file
- Mock API responses (don't call real API)
- Test complete workflow: validate → API → format → output
- Test error paths: file not found, invalid API key

**test_cli_commands.py:**
- Test CLI argument parsing
- Test help text generation
- Test version display
- Test exit codes for various errors
- Use Typer's CliRunner for testing

### 7.3 Test Fixtures (tests/fixtures/)

**sample_audio.mp3:**
- Small (~100KB) valid MP3 file
- Silent audio or simple tone
- For validation and upload testing

**sample_response.json:**
- Example API response structure
- For formatter testing
- Multiple variants (with/without timestamps)

### 7.4 Test Configuration

**conftest.py:**
```python
import pytest
from pathlib import Path
from unittest.mock import Mock

@pytest.fixture
def sample_audio_file(tmp_path):
    """Create a temporary audio file for testing."""
    audio_file = tmp_path / "test.mp3"
    audio_file.write_bytes(b"fake mp3 data")
    return audio_file

@pytest.fixture
def mock_api_response():
    """Mock successful API response."""
    return {
        "text": "This is a test transcription.",
        "language": "en"
    }

@pytest.fixture
def mock_elevenlabs_client():
    """Mock ElevenLabs client."""
    client = Mock()
    client.transcribe.return_value = Mock(text="Test transcription")
    return client
```

**Coverage Target:**
- Minimum 80% code coverage
- Focus on error paths and edge cases
- Mock external dependencies (SDK, file system)

## 8. Correctness Properties

**Requirement → Design Mapping:**

| Requirement | Design Element | Correctness Property | How to Verify |
|-------------|----------------|---------------------|---------------|
| 2.1: uvx execution | pyproject.toml with entry points | CLI callable via uvx | Integration test with uvx |
| 2.2: API key config | config.py priority chain | First valid key found in order | Unit tests with mocked env/files |
| 2.3: File transcription | transcribe.py orchestration | File validated before upload | Integration test with invalid files |
| 2.4: Format options | formatters.py strategy pattern | Each format produces valid output | Unit tests for each formatter |
| 2.5: Output to file | validate_output_path + write | File written with correct content | Integration test checking file contents |
| 2.6: Language support | client.py passes language param | Language sent to API | Mock API call verification |
| 2.7: Error handling | errors.py exception hierarchy | Correct exit code for error type | Tests for each error scenario |
| 2.8: Help & version | Typer annotations + callback | Help text complete and accurate | CLI runner tests |
| 3.3: Retry logic | client.py exponential backoff | 3 retries with correct delays | Time-mocked unit tests |
| 3.3: Exit codes | errors.py handle_error | Correct exit code per error type | Tests for each error |

**Invariants:**
1. **API Key Security:** API key never appears in stdout
2. **Output Separation:** Transcription to stdout, status to stderr (unless --output)
3. **Exit Code Contract:** Exit 0 only on success, non-zero on any error
4. **Validation First:** All validation completes before API calls
5. **Idempotency:** Same inputs always produce same outputs (given same API)
6. **No Side Effects:** Never modifies input files

## 9. Security Considerations

### 9.1 API Key Security
- Never log or print API keys
- Redact keys in error messages if accidentally included
- Warn on world-readable .env files
- Add .env to .gitignore template
- Environment variables safer than files for CI/CD

### 9.2 Input Validation
- Validate file paths (prevent directory traversal)
- Reject files above size limit (prevent resource exhaustion)
- Validate output paths (prevent writing to system directories)
- Sanitize all user inputs before passing to SDK

### 9.3 Network Security
- Use HTTPS only (SDK handles this)
- Validate SSL certificates (SDK default)
- Set reasonable timeouts (prevent hanging)
- No certificate verification bypass

### 9.4 File System Security
- Only read audio files, never execute
- Only write to user-specified output locations
- Check permissions before operations
- Clean up temporary files (if SDK creates any)

### 9.5 Dependency Security
- Pin major versions in pyproject.toml
- Use ^version for minor updates
- Regular dependency audits (pip-audit)
- Keep ElevenLabs SDK updated for security patches

## 10. Performance Considerations

### 10.1 Startup Performance
- Lazy imports for faster help/version display
- Minimal initialization before argument validation
- Fast-fail on validation errors (don't load SDK)

### 10.2 Memory Efficiency
- Stream file uploads (don't load to memory)
- Process response incrementally if possible
- Clear API client after use
- Target: <100MB process memory

### 10.3 Network Efficiency
- Use SDK's built-in compression
- Single request per transcription
- Retry only on transient failures
- Respect rate limits

### 10.4 User Experience
- Show status messages for long operations
- Don't block terminal unnecessarily
- Fast exit on errors
- Target: <1s startup for help, <3s for validation

## 11. Documentation Strategy

### 11.1 README.md
- Quick start with uvx example
- Installation instructions (uvx and pip)
- Common usage examples
- API key setup guide
- Troubleshooting section

### 11.2 Inline Help (--help)
- Clear command descriptions
- All options documented
- Usage examples
- Short and long flag variants

### 11.3 Error Messages
- Describe what went wrong
- Provide specific details
- Include remediation steps
- Link to relevant resources

### 11.4 Code Documentation
- Docstrings for all public functions
- Type hints for all parameters
- Module-level docstrings
- Inline comments for complex logic

## 12. Deployment Strategy

### 12.1 Package Distribution
- Publish to PyPI as "speech-cli"
- Support installation via: `pip install speech-cli`
- Support execution via: `uvx speech-cli`
- Support GitHub source: `uvx --from git+https://github.com/user/speech-cli`

### 12.2 Versioning
- Semantic versioning (MAJOR.MINOR.PATCH)
- Version in src/speech_cli/__init__.py
- Version in pyproject.toml (single source)
- Git tags for releases

### 12.3 Release Process
1. Update version in __init__.py and pyproject.toml
2. Update CHANGELOG.md
3. Run full test suite
4. Create git tag (e.g., v0.1.0)
5. Build package: `uv build`
6. Publish to PyPI: `uv publish`
7. Create GitHub release with notes

### 12.4 CI/CD
- GitHub Actions for testing
- Run tests on Python 3.8, 3.9, 3.10, 3.11, 3.12
- Run on Linux, macOS, Windows
- Lint with ruff
- Type check with mypy
- Test coverage report

## 13. Future Extensibility

**Design decisions that enable future features:**

1. **Layered Architecture:**
   - Easy to add new commands without touching business logic
   - API client can be reused for future features (TTS, etc.)

2. **Formatter Strategy Pattern:**
   - New formats add new formatter function
   - No changes to core transcription logic

3. **Configuration System:**
   - Easy to add new config options to .env
   - Priority chain supports new sources

4. **Error Hierarchy:**
   - New error types extend base exception
   - Error handling remains centralized

5. **Modular Structure:**
   - Each module has single responsibility
   - New features add new modules, minimal changes to existing

**Future features enabled:**
- Batch processing: Add new command, reuse transcribe.py logic
- Configuration profiles: Extend config.py
- Plugin system: Add plugin loader in formatters.py
- Multiple API providers: Abstract client interface

═══════════════════════════════════════════════
📝 PHASE 3: TASKS BREAKDOWN
═══════════════════════════════════════════════

## Implementation Plan

📊 **Total Tasks:** 24
⏱️ **Estimated Time:** 29-42 hours
📦 **Phases:** 4 (Foundation → Core Features → Polish & UX → Testing)

## Task Dependency Graph

### Rules for Dependencies
Task depends on another if it requires:
1. **Types/Interfaces** from other task
2. **Components/Services** from other task
3. **Data/Infrastructure** from other task
4. **Features/Functionality** from other task

No dependency if: Different parts, don't share types/components, can test independently.

### Visualization
```
Task #1 (Project Setup) ──┬──> Task #4 (Constants)
                          │
                          ├──> Task #5 (Errors) ──┬──> Task #7 (Config) ──┬──> Task #10 (Validators)
                          │                        │                        │
                          │                        ├──> Task #8 (Client) ───┤
                          │                        │                        │
                          ├──> Task #6 (Formatters)┴────────────────────────┤
                          │                                                  │
                          └────────────────────────────────────────────────>│
                                                                             │
Task #2 (Git Setup) ──────────────────────────────────────────────────────>│
Task #3 (Deps Install) ───────────────────────────────────────────────────>│
                                                                             │
                                                    ┌────────────────────────┘
                                                    │
                                                    ├──> Task #11 (Orchestration) ──> Task #12 (CLI) ──┬──> Task #13 (Entry Points)
                                                    │                                                   │
                                                    └───────────────────────────────────────────────────┤
                                                                                                        │
                                                                                                        ├──> Task #14 (Smoke Test)
                                                                                                        │
                                                                                                        ├──> Task #15 (README)
                                                                                                        │
                                                                                                        ├──> Task #16 (Output --output)
                                                                                                        │
                                                                                                        ├──> Task #17 (Language)
                                                                                                        │
                                                                                                        ├──> Task #18 (Color)
                                                                                                        │
Task #19-23 (Unit Tests) ────────────────────────────────────────────────────────────────────────────>│
                                                                                                        │
                                                                                                        └──> Task #24 (Integration Tests)
```

**Critical Path:** #1 → #5 → #7 → #10 → #11 → #12 → #13 → #14 (Est: 21-29h)
**Parallel Opportunities:**
- Tasks #2, #3 can run with #1
- Tasks #4, #5, #6 can run in parallel after #1
- Tasks #19-23 (unit tests) can run in parallel at end

## Progress Overview

📊 **Overall:** ░░░░░░░░░░░░ 0% (0/24 completed)
⏱️ **Last Updated:** 2025-12-18

### Phase Breakdown
┌──────────────────────────────────────────────┐
│ Foundation    [░░░░░░░░░░] 0% (0/10) 15-21h│
│ Core Features [░░░░░░░░░░] 0% (0/5)  8-12h │
│ Polish & UX   [░░░░░░░░░░] 0% (0/3)  2-4h  │
│ Testing       [░░░░░░░░░░] 0% (0/6)  4-5h  │
└──────────────────────────────────────────────┘

═══════════════════════════════════════════════
🏗️ PHASE 1: FOUNDATION
═══════════════════════════════════════════════

Tasks establishing foundational project structure, types, and core modules.

┌──────────────────────────────────────────────┐
│ Task #1: Project Setup and Structure         │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 2 hours                         │
│ 🎯 Addresses: Req 2.1, Design Sec 2         │
│ 🔗 Dependencies: None                        │
│ 📂 Files: pyproject.toml, src/speech_cli/   │
│          __init__.py, __main__.py            │
│                                              │
│ **Description:**                             │
│ Initialize uv project with src layout,      │
│ configure pyproject.toml with metadata,     │
│ dependencies, and entry points.             │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] pyproject.toml exists with:           │
│   - name = "speech-cli"                     │
│   - requires-python = ">=3.8"               │
│   - dependencies: typer, elevenlabs,        │
│     python-dotenv                           │
│   - [project.scripts] entry point           │
│ • [ ] src/speech_cli/__init__.py with       │
│     __version__ = "0.1.0"                   │
│ • [ ] src/speech_cli/__main__.py imports    │
│     cli.main() and calls it                 │
│ • [ ] Directory structure matches design    │
│ • [ ] uv.lock file generated                │
│                                              │
│ **Implementation Notes:**                    │
│ • Use: uv init --lib --package speech-cli   │
│ • Add build-system section for PEP 517      │
│ • Configure [tool.uv] section if needed     │
│ • Entry point: speech-cli = "speech_cli.cli:app" │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #2: Git Configuration                   │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 0.5 hours                       │
│ 🎯 Addresses: Design Sec 2, Security 3.2    │
│ 🔗 Dependencies: None                        │
│ 📂 Files: .gitignore, .env.example, LICENSE │
│                                              │
│ **Description:**                             │
│ Create Git configuration files to ensure    │
│ proper version control and security.        │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] .gitignore includes:                  │
│   - .env (never commit API keys)            │
│   - __pycache__/, *.pyc                     │
│   - .pytest_cache/, .coverage               │
│   - dist/, build/, *.egg-info/              │
│   - .venv/, venv/, uv.lock (optional)       │
│ • [ ] .env.example created with template    │
│ • [ ] LICENSE file added (MIT or Apache 2.0)│
│ • [ ] Git initialized: git init             │
│                                              │
│ **Implementation Notes:**                    │
│ • Use Python .gitignore template            │
│ • .env.example should show:                 │
│   ELEVENLABS_API_KEY=your_key_here          │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #3: Install and Verify Dependencies     │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 0.5 hours                       │
│ 🎯 Addresses: Req 5 (Dependencies)          │
│ 🔗 Dependencies: Task #1                     │
│ 📂 Files: pyproject.toml                     │
│                                              │
│ **Description:**                             │
│ Install all required dependencies and       │
│ verify they work correctly.                 │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] uv sync completes successfully        │
│ • [ ] typer version >=0.9.0 installed       │
│ • [ ] elevenlabs SDK installed              │
│ • [ ] python-dotenv >=1.0.0 installed       │
│ • [ ] pytest installed (dev dependency)     │
│ • [ ] Can import: import typer, elevenlabs  │
│                                              │
│ **Implementation Notes:**                    │
│ • Use: uv add typer elevenlabs python-dotenv│
│ • Dev deps: uv add --dev pytest pytest-mock │
│ • Check SDK docs for latest version         │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #4: Implement Constants Module          │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Design Sec 3.7                │
│ 🔗 Dependencies: Task #1                     │
│ 📂 Files: src/speech_cli/constants.py       │
│                                              │
│ **Description:**                             │
│ Create constants module with exit codes,    │
│ formats, and configuration values.          │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Exit codes defined (0-6)              │
│ • [ ] SUPPORTED_FORMATS set created         │
│ • [ ] MAX_FILE_SIZE_MB constant             │
│ • [ ] MAX_RETRIES = 3                       │
│ • [ ] RETRY_DELAY_BASE = 2                  │
│ • [ ] REQUEST_TIMEOUT_SECONDS = 300         │
│ • [ ] OutputFormat enum (TEXT, JSON, SRT)   │
│ • [ ] All constants have docstrings         │
│ • [ ] Module imports without errors         │
│                                              │
│ **Implementation Notes:**                    │
│ • Use enum.Enum for OutputFormat            │
│ • Make OutputFormat inherit from str        │
│ • Add module docstring explaining purpose   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #5: Implement Error Handling Module     │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 2 hours                         │
│ 🎯 Addresses: Req 2.7, Design Sec 3.6       │
│ 🔗 Dependencies: Task #4                     │
│ 📂 Files: src/speech_cli/errors.py          │
│                                              │
│ **Description:**                             │
│ Create custom exception hierarchy and       │
│ error handling function.                    │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] SpeechCLIError base exception         │
│ • [ ] ConfigError with exit code 2          │
│ • [ ] FileError with exit code 6            │
│ • [ ] APIError with exit code 1             │
│ • [ ] AuthenticationError with exit code 3  │
│ • [ ] RateLimitError with exit code 4       │
│ • [ ] NetworkError with exit code 5         │
│ • [ ] FormatterError with exit code 1       │
│ • [ ] handle_error() function implemented   │
│ • [ ] Errors output to stderr               │
│ • [ ] Color support with fallback           │
│                                              │
│ **Implementation Notes:**                    │
│ • Each exception has exit_code attribute    │
│ • handle_error() returns int (exit code)    │
│ • Use typer.secho() for colored errors      │
│ • Test by raising each exception type       │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #6: Implement Output Formatters         │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 2 hours                         │
│ 🎯 Addresses: Req 2.4, Design Sec 3.5       │
│ 🔗 Dependencies: Task #4, #5                 │
│ 📂 Files: src/speech_cli/formatters.py      │
│                                              │
│ **Description:**                             │
│ Implement formatting functions for text,    │
│ JSON, and SRT output formats.               │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] format_transcription() dispatcher     │
│ • [ ] format_text() returns stripped text   │
│ • [ ] format_json() returns pretty JSON     │
│ • [ ] format_srt() handles timestamps       │
│ • [ ] _format_timestamp() helper for SRT    │
│ • [ ] SRT raises FormatterError if no       │
│     timestamp data                          │
│ • [ ] JSON uses ensure_ascii=False          │
│ • [ ] All functions have type hints         │
│                                              │
│ **Subtasks:**                                │
│   6.1 [ ] Implement text formatter          │
│   6.2 [ ] Implement JSON formatter          │
│   6.3 [ ] Implement SRT formatter           │
│   6.4 [ ] Add error handling                │
│                                              │
│ **Implementation Notes:**                    │
│ • Use strategy pattern (dict of formatters) │
│ • SRT format: HH:MM:SS,mmm --> HH:MM:SS,mmm │
│ • Test with mock API responses              │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #7: Implement Configuration Module      │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 3 hours                         │
│ 🎯 Addresses: Req 2.2, Design Sec 3.2       │
│ 🔗 Dependencies: Task #5                     │
│ 📂 Files: src/speech_cli/config.py          │
│                                              │
│ **Description:**                             │
│ Implement API key resolution with priority  │
│ chain and security checks.                  │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] resolve_api_key() with 4-step chain   │
│ • [ ] Checks CLI arg → ENV → .env(cwd) →    │
│     .env(~/.speech-cli/)                    │
│ • [ ] validate_api_key() basic checks       │
│ • [ ] check_env_permissions() warns on      │
│     world-readable                          │
│ • [ ] ConfigError raised if no key found    │
│ • [ ] Error message includes remediation    │
│ • [ ] Strips whitespace from keys           │
│                                              │
│ **Subtasks:**                                │
│   7.1 [ ] Implement CLI arg priority        │
│   7.2 [ ] Add ENV variable check            │
│   7.3 [ ] Add .env file loading (cwd)       │
│   7.4 [ ] Add .env file loading (home)      │
│   7.5 [ ] Add permission checks             │
│                                              │
│ **Implementation Notes:**                    │
│ • Use load_dotenv() with override=False     │
│ • Check stat.S_IROTH for world-readable     │
│ • Test with mocked file system              │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #8: Implement API Client Wrapper        │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 4 hours                         │
│ 🎯 Addresses: Req 2.3, 2.6, 2.7, Design 3.4 │
│ 🔗 Dependencies: Task #4, #5                 │
│ 📂 Files: src/speech_cli/client.py          │
│                                              │
│ **Description:**                             │
│ Create ElevenLabsClient wrapper with retry  │
│ logic and error translation.                │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] ElevenLabsClient class created        │
│ • [ ] __init__ takes api_key parameter      │
│ • [ ] transcribe() method with retry logic  │
│ • [ ] _transcribe_once() single attempt     │
│ • [ ] Exponential backoff (2s, 4s, 8s)      │
│ • [ ] Error translation for 401, 429, 500   │
│ • [ ] No retry on AuthenticationError       │
│ • [ ] No retry on RateLimitError            │
│ • [ ] _parse_response() handles SDK output  │
│ • [ ] File opened as binary stream          │
│                                              │
│ **Subtasks:**                                │
│   8.1 [ ] Create client class skeleton      │
│   8.2 [ ] Implement transcribe with retry   │
│   8.3 [ ] Add exponential backoff           │
│   8.4 [ ] Add error translation             │
│   8.5 [ ] Test with mocked SDK              │
│                                              │
│ **Implementation Notes:**                    │
│ • Check ElevenLabs SDK docs for method name │
│ • May need: client.speech_to_text() or      │
│   client.transcribe()                       │
│ • Print retry messages to stderr            │
│ • Use time.sleep() for backoff              │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #9: Research ElevenLabs SDK API         │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Req 2.4, 2.6, Design Sec 4    │
│ 🔗 Dependencies: Task #3                     │
│ 📂 Files: None (research/documentation)     │
│                                              │
│ **Description:**                             │
│ Research ElevenLabs Python SDK to understand│
│ actual transcription API, response format,  │
│ and supported parameters.                   │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Identified correct SDK method name    │
│ • [ ] Documented response structure         │
│ • [ ] Confirmed language parameter support  │
│ • [ ] Identified supported audio formats    │
│ • [ ] Documented error types from SDK       │
│ • [ ] Confirmed if SRT/timestamps available │
│ • [ ] Noted any SDK-specific parameters     │
│                                              │
│ **Implementation Notes:**                    │
│ • Check official ElevenLabs docs            │
│ • Test with dummy API key if needed         │
│ • Document findings in code comments        │
│ • May need to adjust client.py based on API │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #10: Implement Validators Module        │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 3 hours                         │
│ 🎯 Addresses: Req 2.3, 2.5, Design Sec 3.3  │
│ 🔗 Dependencies: Task #4, #5                 │
│ 📂 Files: src/speech_cli/validators.py      │
│                                              │
│ **Description:**                             │
│ Implement input validation for audio files, │
│ output paths, and formats.                  │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] validate_audio_file() checks:         │
│   - File exists                             │
│   - Is a file (not directory)               │
│   - Size > 0 and < MAX_FILE_SIZE_MB         │
│   - Extension in SUPPORTED_FORMATS          │
│   - File is readable                        │
│ • [ ] validate_output_path() checks:        │
│   - Parent directory exists                 │
│   - Parent is writable                      │
│   - Not a directory                         │
│   - Handles overwrite confirmation          │
│ • [ ] validate_format() checks format       │
│ • [ ] Returns resolved absolute paths       │
│ • [ ] Clear FileError messages              │
│                                              │
│ **Subtasks:**                                │
│   10.1 [ ] Implement audio file validator   │
│   10.2 [ ] Implement output path validator  │
│   10.3 [ ] Implement format validator       │
│   10.4 [ ] Add overwrite confirmation       │
│                                              │
│ **Implementation Notes:**                    │
│ • Use Path.resolve() for absolute paths     │
│ • Use os.access(path, os.R_OK/W_OK)         │
│ • Use typer.confirm() for overwrite         │
│ • Test with temporary directories           │
└──────────────────────────────────────────────┘

═══════════════════════════════════════════════
⚙️ PHASE 2: CORE FEATURES
═══════════════════════════════════════════════

Tasks implementing main transcription workflow and CLI interface.

┌──────────────────────────────────────────────┐
│ Task #11: Implement Orchestration Module     │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 2 hours                         │
│ 🎯 Addresses: Req 2.3, Design Sec 3.8       │
│ 🔗 Dependencies: Tasks #7, #8, #10, #6       │
│ 📂 Files: src/speech_cli/transcribe.py      │
│                                              │
│ **Description:**                             │
│ Implement main transcribe_audio() function  │
│ that orchestrates the complete workflow.    │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] transcribe_audio() function with all  │
│     parameters                              │
│ • [ ] Step 1: Resolve API key               │
│ • [ ] Step 2: Validate audio file           │
│ • [ ] Step 3: Validate output path if given │
│ • [ ] Step 4: Initialize API client         │
│ • [ ] Step 5: Call API                      │
│ • [ ] Step 6: Format response               │
│ • [ ] Step 7: Output to stdout or file      │
│ • [ ] print_status() helper to stderr       │
│ • [ ] Status messages at each step          │
│                                              │
│ **Implementation Notes:**                    │
│ • Follow design section 3.8 exactly         │
│ • Keep function pure (delegates to modules) │
│ • Return formatted string                   │
│ • Test with mocked dependencies             │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #12: Implement CLI Layer                │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 3 hours                         │
│ 🎯 Addresses: Req 2.1, 2.8, Design Sec 3.1  │
│ 🔗 Dependencies: Task #11                    │
│ 📂 Files: src/speech_cli/cli.py             │
│                                              │
│ **Description:**                             │
│ Create Typer CLI application with transcribe│
│ command and all options.                    │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Typer app instance created            │
│ • [ ] transcribe() command with:            │
│   - audio_file Argument (required)          │
│   - --api-key / -k Option                   │
│   - --format / -f Option (default: text)    │
│   - --output / -o Option                    │
│   - --force flag                            │
│   - --language / -l Option                  │
│   - --no-color flag                         │
│ • [ ] --version callback                    │
│ • [ ] --help automatically generated        │
│ • [ ] Calls transcribe_audio()              │
│ • [ ] Uses handle_error() for exceptions    │
│ • [ ] Exits with correct exit codes         │
│                                              │
│ **Subtasks:**                                │
│   12.1 [ ] Create Typer app                 │
│   12.2 [ ] Implement transcribe command     │
│   12.3 [ ] Add version callback             │
│   12.4 [ ] Add error handling               │
│   12.5 [ ] Test with CliRunner              │
│                                              │
│ **Implementation Notes:**                    │
│ • Follow design section 3.1 exactly         │
│ • Typer handles --help automatically        │
│ • Use typer.Exit() with exit codes          │
│ • Test each option independently            │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #13: Configure Entry Points             │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Req 2.1, Design Sec 12        │
│ 🔗 Dependencies: Task #12                    │
│ 📂 Files: pyproject.toml, __main__.py       │
│                                              │
│ **Description:**                             │
│ Configure package entry points for both     │
│ uvx and pip installation methods.           │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] [project.scripts] in pyproject.toml:  │
│     speech-cli = "speech_cli.cli:app"       │
│ • [ ] __main__.py calls cli.app()           │
│ • [ ] Can run: python -m speech_cli         │
│ • [ ] Can run: uv run speech-cli (local)    │
│ • [ ] Can run: uvx --from . speech-cli      │
│ • [ ] --help and --version work             │
│                                              │
│ **Implementation Notes:**                    │
│ • Test locally before pushing               │
│ • __main__.py should be minimal:            │
│   from .cli import app                      │
│   if __name__ == "__main__": app()          │
│ • Verify entry point name matches docs      │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #14: Manual Smoke Test                  │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Req 2.1, 2.3                  │
│ 🔗 Dependencies: Task #13                    │
│ 📂 Files: tests/fixtures/sample_audio.mp3   │
│                                              │
│ **Description:**                             │
│ Manually test the complete workflow with a  │
│ real or mocked audio file and API key.      │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Created small test audio file         │
│ • [ ] Tested: speech-cli transcribe file.mp3│
│ • [ ] Verified API key resolution works     │
│ • [ ] Verified file validation catches bad  │
│     inputs                                  │
│ • [ ] Verified output to stdout             │
│ • [ ] Verified --format json works          │
│ • [ ] Verified error messages are clear     │
│ • [ ] Verified exit codes are correct       │
│                                              │
│ **Implementation Notes:**                    │
│ • Use ElevenLabs API key if available       │
│ • Or mock the SDK client for testing        │
│ • Test with invalid file to see errors      │
│ • Verify status messages go to stderr       │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #15: Write README Documentation         │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Design Sec 11.1               │
│ 🔗 Dependencies: Task #14                    │
│ 📂 Files: README.md                          │
│                                              │
│ **Description:**                             │
│ Create comprehensive README with quick      │
│ start, installation, and usage examples.    │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Title and description                 │
│ • [ ] Quick start with uvx example          │
│ • [ ] Installation section (uvx + pip)      │
│ • [ ] API key setup instructions            │
│ • [ ] Usage examples:                       │
│   - Basic transcription                     │
│   - Output formats                          │
│   - Output to file                          │
│   - Language specification                  │
│ • [ ] Configuration section (.env files)    │
│ • [ ] Troubleshooting section               │
│ • [ ] License and contributing info         │
│                                              │
│ **Implementation Notes:**                    │
│ • Include actual command examples           │
│ • Use code blocks with proper syntax        │
│ • Link to ElevenLabs API key page           │
│ • Keep examples concise and clear           │
└──────────────────────────────────────────────┘

═══════════════════════════════════════════════
✨ PHASE 3: POLISH & UX
═══════════════════════════════════════════════

Tasks enhancing user experience and adding optional features.

┌──────────────────────────────────────────────┐
│ Task #16: Implement --output Flag            │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Req 2.5                       │
│ 🔗 Dependencies: Task #12                    │
│ 📂 Files: src/speech_cli/transcribe.py      │
│                                              │
│ **Description:**                             │
│ Already implemented in Task #11, verify and │
│ test thoroughly.                            │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] --output flag accepts file path       │
│ • [ ] File is created if doesn't exist      │
│ • [ ] Prompts for overwrite if exists       │
│ • [ ] --force skips confirmation            │
│ • [ ] Output written with UTF-8 encoding    │
│ • [ ] Success message to stderr             │
│ • [ ] Stdout shows only status (no output)  │
│                                              │
│ **Implementation Notes:**                    │
│ • Should already be in transcribe.py        │
│ • Test with various paths                   │
│ • Test overwrite scenarios                  │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #17: Implement --language Flag          │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Req 2.6                       │
│ 🔗 Dependencies: Task #8, #9                 │
│ 📂 Files: src/speech_cli/client.py          │
│                                              │
│ **Description:**                             │
│ Verify language parameter is passed to SDK  │
│ and test with different language codes.     │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] --language flag in CLI                │
│ • [ ] Language passed to client.transcribe()│
│ • [ ] Optional parameter (auto-detect)      │
│ • [ ] Error if SDK rejects language code    │
│ • [ ] Documented supported languages        │
│                                              │
│ **Implementation Notes:**                    │
│ • Already in cli.py from Task #12           │
│ • Verify SDK accepts language parameter     │
│ • Test with 'en', 'es', 'fr', etc.          │
│ • Document in --help text                   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #18: Implement Color Output Control     │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 0.5 hours                       │
│ 🎯 Addresses: Design Sec 3.4 Usability      │
│ 🔗 Dependencies: Task #11                    │
│ 📂 Files: src/speech_cli/transcribe.py,     │
│          errors.py                           │
│                                              │
│ **Description:**                             │
│ Verify --no-color flag disables all colored │
│ output throughout the application.          │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] --no-color flag exists in CLI         │
│ • [ ] Flag propagates to all status messages│
│ • [ ] Flag propagates to error handler      │
│ • [ ] With --no-color, no ANSI codes output │
│ • [ ] Works in pipes/redirects              │
│                                              │
│ **Implementation Notes:**                    │
│ • Already in cli.py and transcribe.py       │
│ • Test by piping output                     │
│ • Verify with: cmd --no-color | cat         │
└──────────────────────────────────────────────┘

═══════════════════════════════════════════════
🧪 PHASE 4: TESTING
═══════════════════════════════════════════════

Comprehensive test coverage for all modules and workflows.

┌──────────────────────────────────────────────┐
│ Task #19: Unit Tests - Config Module         │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Design Sec 7.1                │
│ 🔗 Dependencies: Task #7                     │
│ 📂 Files: tests/unit/test_config.py         │
│                                              │
│ **Description:**                             │
│ Write comprehensive unit tests for API key  │
│ resolution logic.                           │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Test CLI arg takes priority           │
│ • [ ] Test ENV var fallback                 │
│ • [ ] Test .env (cwd) fallback              │
│ • [ ] Test .env (home) fallback             │
│ • [ ] Test ConfigError when no key found    │
│ • [ ] Test whitespace stripping             │
│ • [ ] Test permission warning               │
│ • [ ] Test malformed .env files             │
│ • [ ] Mock file system and environment      │
│                                              │
│ **Implementation Notes:**                    │
│ • Use pytest fixtures for mock files        │
│ • Use monkeypatch for environment vars      │
│ • Test priority order explicitly            │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #20: Unit Tests - Validators            │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Design Sec 7.1                │
│ 🔗 Dependencies: Task #10                    │
│ 📂 Files: tests/unit/test_validators.py     │
│                                              │
│ **Description:**                             │
│ Write unit tests for file and input         │
│ validation logic.                           │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Test file exists check                │
│ • [ ] Test file vs directory                │
│ • [ ] Test file size limits                 │
│ • [ ] Test format validation                │
│ • [ ] Test output path validation           │
│ • [ ] Test overwrite confirmation           │
│ • [ ] Test FileError messages               │
│ • [ ] Use tmp_path fixture                  │
│                                              │
│ **Implementation Notes:**                    │
│ • Create test files with tmp_path           │
│ • Test all edge cases from requirements     │
│ • Mock typer.confirm() for overwrite tests  │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #21: Unit Tests - Formatters            │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Design Sec 7.1                │
│ 🔗 Dependencies: Task #6                     │
│ 📂 Files: tests/unit/test_formatters.py     │
│                                              │
│ **Description:**                             │
│ Write unit tests for output formatting      │
│ functions.                                  │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Test format_text() basic case         │
│ • [ ] Test format_json() valid JSON output  │
│ • [ ] Test format_srt() with timestamps     │
│ • [ ] Test format_srt() error without       │
│     timestamps                              │
│ • [ ] Test special characters in JSON       │
│ • [ ] Test empty transcription              │
│ • [ ] Test timestamp formatting helper      │
│                                              │
│ **Implementation Notes:**                    │
│ • Use fixtures for mock API responses       │
│ • Validate JSON with json.loads()           │
│ • Verify SRT format structure               │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #22: Unit Tests - API Client            │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1 hour                          │
│ 🎯 Addresses: Design Sec 7.1                │
│ 🔗 Dependencies: Task #8                     │
│ 📂 Files: tests/unit/test_client.py         │
│                                              │
│ **Description:**                             │
│ Write unit tests for API client with mocked │
│ SDK calls.                                  │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Test successful transcription         │
│ • [ ] Test retry logic (3 attempts)         │
│ • [ ] Test exponential backoff timing       │
│ • [ ] Test AuthenticationError (no retry)   │
│ • [ ] Test RateLimitError (no retry)        │
│ • [ ] Test NetworkError (with retry)        │
│ • [ ] Test error code translation           │
│ • [ ] Mock ElevenLabs SDK                   │
│                                              │
│ **Implementation Notes:**                    │
│ • Use unittest.mock.Mock for SDK            │
│ • Use time.time() to verify backoff delays  │
│ • Test stderr output for retry messages     │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #23: Unit Tests - Error Handling        │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 0.5 hours                       │
│ 🎯 Addresses: Design Sec 7.1                │
│ 🔗 Dependencies: Task #5                     │
│ 📂 Files: tests/unit/test_errors.py         │
│                                              │
│ **Description:**                             │
│ Write unit tests for exception hierarchy    │
│ and error handling.                         │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Test each exception type              │
│ • [ ] Test exit_code attribute              │
│ • [ ] Test handle_error() returns correct   │
│     exit code                               │
│ • [ ] Test error output to stderr           │
│ • [ ] Test color vs no-color output         │
│                                              │
│ **Implementation Notes:**                    │
│ • Raise each exception and verify code      │
│ • Capture stderr to verify error messages   │
│ • Test both colored and plain output        │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Task #24: Integration Tests                  │
├──────────────────────────────────────────────┤
│ ⏳ Status: PENDING                           │
│ ⏱️ Estimate: 1.5 hours                       │
│ 🎯 Addresses: Design Sec 7.2                │
│ 🔗 Dependencies: Tasks #12, #19-23           │
│ 📂 Files: tests/integration/                │
│          test_transcribe_flow.py,           │
│          test_cli_commands.py               │
│                                              │
│ **Description:**                             │
│ Write end-to-end integration tests for      │
│ complete workflows.                         │
│                                              │
│ **Completion Criteria:**                     │
│ • [ ] Test complete transcription flow      │
│ • [ ] Test CLI with CliRunner               │
│ • [ ] Test --help output                    │
│ • [ ] Test --version output                 │
│ • [ ] Test file not found error path        │
│ • [ ] Test invalid API key error path       │
│ • [ ] Test output to file                   │
│ • [ ] Test different formats                │
│ • [ ] Mock API client (no real API calls)   │
│ • [ ] Verify exit codes                     │
│                                              │
│ **Subtasks:**                                │
│   24.1 [ ] Write workflow integration tests │
│   24.2 [ ] Write CLI command tests          │
│   24.3 [ ] Create test fixtures             │
│   24.4 [ ] Set up conftest.py               │
│                                              │
│ **Implementation Notes:**                    │
│ • Use typer.testing.CliRunner               │
│ • Mock ElevenLabsClient at integration level│
│ • Use fixtures from conftest.py             │
│ • Test both success and error paths         │
└──────────────────────────────────────────────┘

## Change Log

### 2025-12-18
- Initial task breakdown created
- 24 tasks across 4 phases
- Foundation: 10 tasks (15-21h)
- Core Features: 5 tasks (8-12h)
- Polish & UX: 3 tasks (2-4h)
- Testing: 6 tasks (4-5h)
- Total: 29-42 hours estimated

## Implementation Notes & Discoveries

<!-- This section will be populated during implementation:
     - Actual ElevenLabs SDK API methods discovered
     - Decisions made during coding
     - Deviations from plan with rationale
     - New tasks discovered
     - Blockers and resolutions
     - Actual time vs estimates
-->
