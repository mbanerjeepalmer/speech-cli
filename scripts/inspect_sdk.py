#!/usr/bin/env python3
"""
ElevenLabs SDK Introspection Script

This script introspects the ElevenLabs SDK and extracts all method signatures,
parameters, type hints, docstrings, and more. The output is structured JSON
that can be used for automatic CLI command generation.
"""

import inspect
import json
import sys
import typing
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, get_args, get_origin


def get_type_string(type_hint: Any) -> str:
    """Convert a type hint to a readable string representation."""
    if type_hint is inspect.Parameter.empty or type_hint is None:
        return "Any"

    # Handle typing module types
    origin = get_origin(type_hint)
    args = get_args(type_hint)

    if origin is typing.Union:
        # Handle Optional and Union types
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(args) == 2 and type(None) in args:
            # This is Optional[T]
            return f"Optional[{get_type_string(non_none_args[0])}]"
        else:
            # This is Union[T1, T2, ...]
            type_strs = [get_type_string(arg) for arg in args]
            return f"Union[{', '.join(type_strs)}]"

    if origin is list or origin is typing.List:
        if args:
            return f"List[{get_type_string(args[0])}]"
        return "List"

    if origin is dict or origin is typing.Dict:
        if args:
            return f"Dict[{get_type_string(args[0])}, {get_type_string(args[1])}]"
        return "Dict"

    if origin is tuple or origin is typing.Tuple:
        if args:
            arg_strs = [get_type_string(arg) for arg in args]
            return f"Tuple[{', '.join(arg_strs)}]"
        return "Tuple"

    if origin is typing.Sequence or origin is typing.Iterable:
        if args:
            return f"{origin.__name__}[{get_type_string(args[0])}]"
        return origin.__name__

    if origin is typing.Iterator or origin is typing.AsyncIterator:
        if args:
            return f"{origin.__name__}[{get_type_string(args[0])}]"
        return origin.__name__

    # Handle regular types
    if hasattr(type_hint, "__name__"):
        return type_hint.__name__

    if hasattr(type_hint, "__module__") and hasattr(type_hint, "__qualname__"):
        # For custom classes, return the full path
        module = type_hint.__module__
        if module and module.startswith("elevenlabs"):
            return f"{module}.{type_hint.__qualname__}"
        return type_hint.__qualname__

    # Fallback to string representation
    return str(type_hint).replace("typing.", "")


def get_default_value(param: inspect.Parameter) -> Optional[Any]:
    """Extract the default value of a parameter in a JSON-serializable format."""
    if param.default is inspect.Parameter.empty:
        return None

    default = param.default

    # Handle special sentinel values
    if hasattr(default, "__module__") and hasattr(default, "__name__"):
        if default.__module__ == "elevenlabs.client" and default.__name__ == "OMIT":
            return "OMIT"

    # Handle basic types
    if default is None or isinstance(default, (bool, int, float, str)):
        return default

    # Handle enum values
    if hasattr(default, "value"):
        return default.value

    # For complex objects, return their string representation
    return str(default)


def extract_method_info(method: Any, method_path: str) -> Optional[Dict[str, Any]]:
    """Extract comprehensive information about a method."""
    try:
        # Skip special methods, properties, and private methods
        method_name = method_path.split(".")[-1]
        if method_name.startswith("_") or method_name == "with_raw_response":
            return None

        # Check if it's a callable method
        if not callable(method):
            return None

        # Get the signature
        try:
            sig = inspect.signature(method)
        except (ValueError, TypeError):
            return None

        # Extract parameters
        parameters = []
        for param_name, param in sig.parameters.items():
            # Skip 'self' and 'cls'
            if param_name in ("self", "cls"):
                continue

            param_info = {
                "name": param_name,
                "type": get_type_string(param.annotation),
                "default": get_default_value(param),
                "required": param.default is inspect.Parameter.empty,
                "kind": param.kind.name,  # POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, VAR_POSITIONAL, KEYWORD_ONLY, VAR_KEYWORD
            }
            parameters.append(param_info)

        # Extract return type
        return_type = get_type_string(sig.return_annotation)

        # Extract docstring
        docstring = inspect.getdoc(method) or ""

        # Determine if method is async
        is_async = inspect.iscoroutinefunction(method)

        # Extract source file location (for reference)
        try:
            source_file = inspect.getfile(method)
            source_line = inspect.getsourcelines(method)[1]
        except (TypeError, OSError):
            source_file = None
            source_line = None

        return {
            "path": method_path,
            "name": method_name,
            "parameters": parameters,
            "return_type": return_type,
            "docstring": docstring,
            "is_async": is_async,
            "source_file": source_file,
            "source_line": source_line,
        }

    except Exception as e:
        print(f"Error extracting method info for {method_path}: {e}", file=sys.stderr)
        return None


def explore_client(
    obj: Any,
    path: str,
    visited: Set[int],
    methods: List[Dict[str, Any]],
    depth: int = 0,
    max_depth: int = 10
) -> None:
    """Recursively explore a client object and extract all methods."""
    # Prevent infinite recursion
    if depth > max_depth or id(obj) in visited:
        return

    visited.add(id(obj))

    # Get all attributes of the object
    try:
        attrs = dir(obj)
    except Exception:
        return

    for attr_name in attrs:
        # Skip private and special attributes
        if attr_name.startswith("_"):
            continue

        try:
            attr = getattr(obj, attr_name)
        except Exception:
            continue

        current_path = f"{path}.{attr_name}" if path else attr_name

        # Check if it's a method
        if callable(attr):
            method_info = extract_method_info(attr, current_path)
            if method_info:
                methods.append(method_info)

        # Check if it's a nested client (property that returns another client)
        elif hasattr(attr, "__class__"):
            class_name = attr.__class__.__name__
            # Look for client classes
            if "Client" in class_name and not class_name.startswith("_"):
                explore_client(attr, current_path, visited, methods, depth + 1, max_depth)


def main():
    """Main function to introspect the ElevenLabs SDK."""
    print("Starting ElevenLabs SDK introspection...")

    try:
        # Import the ElevenLabs clients
        from elevenlabs import ElevenLabs, AsyncElevenLabs

        # Initialize empty client (no API key needed for introspection)
        sync_client = ElevenLabs(api_key="dummy_key_for_introspection")
        async_client = AsyncElevenLabs(api_key="dummy_key_for_introspection")

        # Collect all methods
        all_methods = []
        visited = set()

        print("Exploring sync client...")
        explore_client(sync_client, "client", visited, all_methods)

        print("Exploring async client...")
        visited_async = set()
        async_methods = []
        explore_client(async_client, "async_client", visited_async, async_methods)

        # Combine results
        result = {
            "sdk_name": "elevenlabs",
            "introspection_version": "1.0",
            "sync_client": {
                "name": "ElevenLabs",
                "methods_count": len(all_methods),
                "methods": all_methods,
            },
            "async_client": {
                "name": "AsyncElevenLabs",
                "methods_count": len(async_methods),
                "methods": async_methods,
            },
        }

        # Create output directory if it doesn't exist
        output_path = Path(__file__).parent.parent / "docs" / "sdk-methods.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to JSON file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Introspection complete!")
        print(f"✓ Found {len(all_methods)} sync methods")
        print(f"✓ Found {len(async_methods)} async methods")
        print(f"✓ Output written to: {output_path}")

        # Print summary of top-level namespaces
        namespaces = set()
        for method in all_methods:
            parts = method["path"].split(".")
            if len(parts) > 1:
                namespaces.add(parts[1])

        print(f"\n✓ Found {len(namespaces)} top-level namespaces:")
        for ns in sorted(namespaces):
            count = sum(1 for m in all_methods if m["path"].split(".")[1] == ns if len(m["path"].split(".")) > 1)
            print(f"  - {ns}: {count} methods")

        return 0

    except Exception as e:
        print(f"Error during introspection: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
