#!/usr/bin/env python3
"""
Example CLI Generator

This script demonstrates how to use the SDK introspection data to automatically
generate CLI command definitions. This is a simplified example showing the concept.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


def load_sdk_data() -> Dict[str, Any]:
    """Load the SDK methods data from JSON."""
    data_path = Path(__file__).parent.parent / "docs" / "sdk-methods.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def method_to_cli_command_name(method_path: str) -> str:
    """
    Convert SDK method path to CLI command name.

    Examples:
        client.text_to_speech.convert -> text-to-speech convert
        client.voices.get_all -> voices get-all
    """
    parts = method_path.split(".")
    # Remove "client." prefix
    if parts[0] == "client":
        parts = parts[1:]

    # Convert to kebab-case and join
    return " ".join(part.replace("_", "-") for part in parts)


def generate_click_command(method: Dict[str, Any]) -> str:
    """
    Generate a Click command definition from a method.
    This is a simplified example.
    """
    cli_name = method_to_cli_command_name(method["path"])
    parts = cli_name.split()
    group = parts[0] if len(parts) > 1 else None
    command_name = parts[-1]

    lines = []
    lines.append(f"# Generated from: {method['path']}")

    if group:
        lines.append(f"@{group}.command(name='{command_name}')")
    else:
        lines.append(f"@cli.command(name='{command_name}')")

    # Add options for parameters
    for param in method["parameters"]:
        if param["name"] == "request_options":
            continue  # Skip internal parameters

        param_name = param["name"].replace("_", "-")
        is_required = param["required"]
        param_type = param["type"]

        # Simplify type representation
        if "Optional[" in param_type:
            param_type = param_type.replace("Optional[", "").replace("]", "")
            is_required = False

        # Map Python types to Click types
        click_type = "str"
        if "int" in param_type.lower():
            click_type = "int"
        elif "bool" in param_type.lower():
            click_type = "bool"
        elif "float" in param_type.lower():
            click_type = "float"

        if is_required:
            lines.append(f"@click.option('--{param_name}', required=True, type={click_type})")
        else:
            default = param.get("default")
            if default == "OMIT" or default == "Ellipsis":
                default = "None"
            lines.append(f"@click.option('--{param_name}', type={click_type}, default={default})")

    # Generate function signature
    func_params = [param["name"] for param in method["parameters"]
                   if param["name"] != "request_options"]
    lines.append(f"def {command_name}({', '.join(func_params)}):")

    # Add docstring
    if method["docstring"]:
        first_line = method["docstring"].split("\n")[0]
        lines.append(f'    """{first_line}"""')

    # Add implementation hint
    lines.append(f"    # Call: client.{'.'.join(method['path'].split('.')[1:])}(...)")
    lines.append(f"    pass  # Implementation here")

    return "\n".join(lines)


def generate_typer_command(method: Dict[str, Any]) -> str:
    """
    Generate a Typer command definition from a method.
    This is a simplified example.
    """
    cli_name = method_to_cli_command_name(method["path"])
    parts = cli_name.split()
    command_name = parts[-1].replace("-", "_")

    lines = []
    lines.append(f"# Generated from: {method['path']}")
    lines.append(f"@app.command(name='{parts[-1]}')")

    # Generate function signature with Typer annotations
    params = []
    for param in method["parameters"]:
        if param["name"] == "request_options":
            continue

        param_name = param["name"]
        param_type = param["type"]
        is_required = param["required"]

        # Simplify type
        if "Optional[" in param_type:
            param_type = param_type.replace("Optional[", "").replace("]", "")
            typer_default = "None"
        elif is_required:
            typer_default = "..."
        else:
            typer_default = "None"

        # Map to basic Python types
        if "str" in param_type:
            param_type = "str"
        elif "int" in param_type:
            param_type = "int"
        elif "bool" in param_type:
            param_type = "bool"
        else:
            param_type = "str"  # Default to str

        cli_param_name = param_name.replace("_", "-")
        params.append(
            f"{param_name}: {param_type} = typer.Option({typer_default}, '--{cli_param_name}')"
        )

    lines.append(f"def {command_name}(")
    for i, param in enumerate(params):
        comma = "," if i < len(params) - 1 else ""
        lines.append(f"    {param}{comma}")
    lines.append("):")

    # Add docstring
    if method["docstring"]:
        first_line = method["docstring"].split("\n")[0]
        lines.append(f'    """{first_line}"""')

    # Add implementation hint
    lines.append(f"    # Call: client.{'.'.join(method['path'].split('.')[1:])}(...)")
    lines.append(f"    pass  # Implementation here")

    return "\n".join(lines)


def main():
    """Main function to demonstrate CLI generation."""
    print("=== Example CLI Command Generation ===\n")

    # Load SDK data
    data = load_sdk_data()

    # Get a few example methods
    methods = data["sync_client"]["methods"]

    # Filter to some interesting methods
    example_methods = [
        m for m in methods
        if m["path"] in [
            "client.text_to_speech.convert",
            "client.voices.get_all",
            "client.models.get",
        ]
    ]

    print("=" * 80)
    print("CLICK FRAMEWORK EXAMPLES")
    print("=" * 80)

    for method in example_methods:
        print(f"\n{generate_click_command(method)}\n")
        print("-" * 80)

    print("\n\n")
    print("=" * 80)
    print("TYPER FRAMEWORK EXAMPLES")
    print("=" * 80)

    for method in example_methods:
        print(f"\n{generate_typer_command(method)}\n")
        print("-" * 80)

    print("\n\n=== Summary ===")
    print(f"Total methods available for CLI generation: {len(methods)}")
    print(f"Namespaces: {len(set(m['path'].split('.')[1] for m in methods if len(m['path'].split('.')) > 1))}")
    print("\nThese examples show how the SDK introspection data can be used")
    print("to automatically generate CLI commands for any framework!")


if __name__ == "__main__":
    main()
