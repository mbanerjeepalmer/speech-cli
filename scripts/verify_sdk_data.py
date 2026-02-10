#!/usr/bin/env python3
"""
Verification script to demonstrate how to use the SDK methods JSON data.
This shows examples of how to query and use the introspected data.
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_sdk_data() -> Dict[str, Any]:
    """Load the SDK methods data from JSON."""
    data_path = Path(__file__).parent.parent / "docs" / "sdk-methods.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_statistics(data: Dict[str, Any]) -> None:
    """Print statistics about the SDK."""
    print("=== ElevenLabs SDK Statistics ===\n")

    sync_client = data["sync_client"]
    async_client = data["async_client"]

    print(f"Total sync methods: {sync_client['methods_count']}")
    print(f"Total async methods: {async_client['methods_count']}")

    # Count namespaces
    namespaces = {}
    for method in sync_client["methods"]:
        parts = method["path"].split(".")
        if len(parts) > 1:
            namespace = parts[1]
            namespaces[namespace] = namespaces.get(namespace, 0) + 1

    print(f"\nNamespaces: {len(namespaces)}")
    print("\nTop 10 namespaces by method count:")
    sorted_namespaces = sorted(namespaces.items(), key=lambda x: x[1], reverse=True)[:10]
    for ns, count in sorted_namespaces:
        print(f"  {ns:30} {count:3} methods")


def find_methods_by_name(data: Dict[str, Any], name: str) -> List[Dict[str, Any]]:
    """Find all methods with a specific name."""
    methods = []
    for method in data["sync_client"]["methods"]:
        if method["name"] == name:
            methods.append(method)
    return methods


def find_methods_by_path_prefix(data: Dict[str, Any], prefix: str) -> List[Dict[str, Any]]:
    """Find all methods that start with a specific path prefix."""
    methods = []
    for method in data["sync_client"]["methods"]:
        if method["path"].startswith(prefix):
            methods.append(method)
    return methods


def print_method_signature(method: Dict[str, Any]) -> None:
    """Print a readable method signature."""
    path = method["path"]
    name = method["name"]
    params = method["parameters"]
    return_type = method["return_type"]

    # Build parameter string
    param_strs = []
    for param in params:
        param_str = f"{param['name']}: {param['type']}"
        if not param["required"] and param["default"] is not None:
            param_str += f" = {param['default']}"
        elif not param["required"]:
            param_str += " = None"
        param_strs.append(param_str)

    # Print signature
    if method["is_async"]:
        print(f"async def {name}({', '.join(param_strs)}) -> {return_type}")
    else:
        print(f"def {name}({', '.join(param_strs)}) -> {return_type}")

    print(f"Path: {path}")


def example_queries(data: Dict[str, Any]) -> None:
    """Show example queries on the SDK data."""
    print("\n\n=== Example Queries ===\n")

    # Example 1: Find all "convert" methods
    print("1. All 'convert' methods:")
    convert_methods = find_methods_by_name(data, "convert")
    for method in convert_methods[:5]:  # Show first 5
        print(f"   - {method['path']}")
    print(f"   ... ({len(convert_methods)} total)")

    # Example 2: Find all text_to_speech methods
    print("\n2. All text_to_speech methods:")
    tts_methods = find_methods_by_path_prefix(data, "client.text_to_speech.")
    for method in tts_methods:
        if not "with_raw_response" in method["path"]:
            print(f"   - {method['path']}")

    # Example 3: Show detailed info for a specific method
    print("\n3. Detailed info for client.text_to_speech.convert:")
    tts_convert = [m for m in data["sync_client"]["methods"]
                   if m["path"] == "client.text_to_speech.convert"][0]
    print_method_signature(tts_convert)
    print(f"\nRequired parameters:")
    for param in tts_convert["parameters"]:
        if param["required"]:
            print(f"   - {param['name']}: {param['type']}")

    print(f"\nOptional parameters: {sum(1 for p in tts_convert['parameters'] if not p['required'])}")

    # Example 4: Find methods with specific return types
    print("\n4. Methods that return Iterator:")
    iterator_methods = [m for m in data["sync_client"]["methods"]
                       if "Iterator" in m["return_type"] and not "with_raw_response" in m["path"]]
    for method in iterator_methods[:10]:
        print(f"   - {method['path']}")
    print(f"   ... ({len(iterator_methods)} total)")

    # Example 5: Methods with no required parameters (besides self)
    print("\n5. Methods with no required parameters:")
    no_req_params = [m for m in data["sync_client"]["methods"]
                     if all(not p["required"] for p in m["parameters"])
                     and not "with_raw_response" in m["path"]]
    for method in no_req_params[:10]:
        print(f"   - {method['path']}")
    print(f"   ... ({len(no_req_params)} total)")


def example_cli_generation(data: Dict[str, Any]) -> None:
    """Show how this data could be used for CLI generation."""
    print("\n\n=== Example: CLI Command Generation ===\n")

    # Get a method
    method = [m for m in data["sync_client"]["methods"]
              if m["path"] == "client.text_to_speech.convert"][0]

    print("For method: client.text_to_speech.convert")
    print("\nGenerated CLI command structure:")
    print("  elevenlabs text-to-speech convert [OPTIONS]")

    print("\nRequired arguments:")
    for param in method["parameters"]:
        if param["required"]:
            print(f"  --{param['name'].replace('_', '-')} <{param['type']}>")

    print("\nOptional arguments:")
    for param in method["parameters"]:
        if not param["required"] and param["name"] != "request_options":
            default = param["default"] if param["default"] != "OMIT" else "None"
            print(f"  --{param['name'].replace('_', '-')} <{param['type']}> (default: {default})")

    print("\nDocstring (first paragraph):")
    docstring = method["docstring"].split("\n\n")[0]
    print(f"  {docstring}")


def main():
    """Main function."""
    # Load the data
    data = load_sdk_data()

    # Print statistics
    print_statistics(data)

    # Show example queries
    example_queries(data)

    # Show CLI generation example
    example_cli_generation(data)

    print("\n\n=== Verification Complete ===")
    print(f"The SDK introspection data is ready for use!")
    print(f"Location: docs/sdk-methods.json")
    print(f"Total methods captured: {data['sync_client']['methods_count'] + data['async_client']['methods_count']}")


if __name__ == "__main__":
    main()
