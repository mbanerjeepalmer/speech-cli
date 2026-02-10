"""Dynamic CLI generator from SDK introspection data."""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from elevenlabs import ElevenLabs
from rich.console import Console

from speech_cli import __version__
from speech_cli.config import get_api_key, validate_api_key
from speech_cli.errors import SpeechCLIError
from speech_cli.output_formatters import OutputFormatter
from speech_cli.parameter_handlers import ParameterHandler

# Console for stderr output
console = Console(stderr=True)


def load_sdk_methods() -> List[Dict[str, Any]]:
    """Load SDK introspection data.

    Returns:
        List of SDK methods from sync_client
    """
    # Path to the SDK methods JSON file
    json_path = Path(__file__).parent.parent.parent / "docs" / "sdk-methods.json"

    if not json_path.exists():
        console.print(
            f"[red]Error:[/red] SDK methods data not found at {json_path}"
        )
        console.print("Run: uv run python scripts/inspect_sdk.py")
        sys.exit(1)

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            # Extract methods from sync_client
            return data.get("sync_client", {}).get("methods", [])
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load SDK methods: {e}")
        sys.exit(1)


def group_methods_by_namespace(methods: Dict[str, Any]) -> Dict[str, List[Dict]]:
    """Group methods by their top-level namespace.

    Args:
        methods: SDK methods dictionary

    Returns:
        Dictionary mapping namespace to list of methods
    """
    grouped = defaultdict(list)

    for method_path, method_data in methods.items():
        if method_path.startswith("client."):
            # Remove 'client.' prefix
            path_parts = method_path[7:].split(".")
            if path_parts:
                namespace = path_parts[0]
                grouped[namespace].append(
                    {"path": method_path, "data": method_data, "parts": path_parts}
                )

    return dict(grouped)


def get_method_by_path(client: ElevenLabs, method_path: str) -> Any:
    """Get method from client by path.

    Args:
        client: ElevenLabs client instance
        method_path: Method path (e.g., 'client.text_to_speech.convert')

    Returns:
        Method object
    """
    # Remove 'client.' prefix
    if method_path.startswith("client."):
        method_path = method_path[7:]

    parts = method_path.split(".")
    obj = client

    for part in parts:
        obj = getattr(obj, part)

    return obj


def create_method_command(
    method_info: Dict[str, Any], api_key_param: Optional[str] = None
) -> Any:
    """Create a Typer command for a SDK method.

    Args:
        method_info: Method metadata from SDK introspection
        api_key_param: API key parameter (for command closure)

    Returns:
        Typer command function
    """
    method_path = method_info["path"]
    method_data = method_info["data"]
    parameters = method_data.get("parameters", {})
    docstring = method_data.get("docstring", "")
    return_type = method_data.get("return_annotation", "")

    # Extract first line of docstring as help text
    help_text = docstring.split("\n")[0] if docstring else method_path

    def command_function(
        api_key: Optional[str] = typer.Option(
            None,
            "--api-key",
            "-k",
            envvar="ELEVENLABS_API_KEY",
            help="ElevenLabs API key",
        ),
        output_format: str = typer.Option(
            "json",
            "--format",
            "-f",
            help="Output format (json, yaml, text, table)",
        ),
        output_file: Optional[Path] = typer.Option(
            None,
            "--output",
            "-o",
            help="Output file path",
        ),
        **kwargs: Any,
    ) -> None:
        """Execute SDK method."""
        try:
            # Get and validate API key
            resolved_api_key = get_api_key(api_key)
            validate_api_key(resolved_api_key)

            # Initialize client
            client = ElevenLabs(api_key=resolved_api_key)

            # Get method
            method = get_method_by_path(client, method_path)

            # Prepare parameters
            prepared_params = ParameterHandler.prepare_parameters(kwargs, parameters)

            # Call method
            console.print(f"Calling {method_path}...")
            result = method(**prepared_params)

            # Format and output result
            OutputFormatter.format_output(result, output_format, output_file)

        except SpeechCLIError as e:
            console.print(f"[red]Error:[/red] {e.message}")
            if e.details:
                console.print(e.details)
            sys.exit(e.exit_code.value)
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            sys.exit(1)

    # Set function metadata
    command_function.__name__ = method_info["parts"][-1]
    command_function.__doc__ = help_text

    # Add parameters as typer options
    # Note: In actual implementation, we would dynamically add parameters
    # For now, we use **kwargs to accept any parameters

    return command_function


def create_namespace_app(namespace: str, methods: List[Dict]) -> typer.Typer:
    """Create a Typer app for a namespace.

    Args:
        namespace: Namespace name (e.g., 'text_to_speech')
        methods: List of methods in this namespace

    Returns:
        Typer app for namespace
    """
    app = typer.Typer(
        name=namespace.replace("_", "-"),
        help=f"Commands for {namespace.replace('_', ' ')}",
    )

    # Group methods by sub-namespace
    direct_methods = []
    sub_namespaces = defaultdict(list)

    for method_info in methods:
        parts = method_info["parts"]
        if len(parts) == 2:
            # Direct method (e.g., voices.get)
            direct_methods.append(method_info)
        else:
            # Sub-namespace method (e.g., voices.settings.get)
            sub_namespace = parts[1]
            sub_namespaces[sub_namespace].append(method_info)

    # Add direct methods as commands
    for method_info in direct_methods:
        command = create_method_command(method_info)
        method_name = method_info["parts"][-1].replace("_", "-")
        app.command(name=method_name)(command)

    # Add sub-namespaces as nested apps (simplified for now)
    # Full implementation would recursively create nested apps

    return app


def create_dynamic_cli() -> typer.Typer:
    """Create the complete dynamic CLI.

    Returns:
        Main Typer app
    """
    app = typer.Typer(
        name="speech-cli",
        help="Complete CLI for ElevenLabs API - Auto-generated from SDK",
        add_completion=False,
    )

    def version_callback(value: bool) -> None:
        """Show version and exit."""
        if value:
            console.print(f"speech-cli version {__version__}")
            raise typer.Exit()

    @app.callback()
    def main(
        version: Optional[bool] = typer.Option(
            None,
            "--version",
            "-v",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ) -> None:
        """Main callback."""
        pass

    # Load SDK methods
    console.print("Loading SDK methods...")
    methods = load_sdk_methods()
    console.print(f"Loaded {len(methods)} methods from SDK")

    # Group by namespace
    grouped = group_methods_by_namespace(methods)
    console.print(f"Found {len(grouped)} namespaces")

    # Create namespace apps
    for namespace, ns_methods in grouped.items():
        # Skip some internal namespaces
        if namespace in ("with_raw_response", "with_streaming_response"):
            continue

        ns_app = create_namespace_app(namespace, ns_methods)
        app.add_typer(ns_app, name=namespace.replace("_", "-"))

    return app


# Singleton instance
_cli_app = None


def get_cli_app() -> typer.Typer:
    """Get or create the CLI app (singleton).

    Returns:
        Main Typer app
    """
    global _cli_app
    if _cli_app is None:
        _cli_app = create_dynamic_cli()
    return _cli_app
