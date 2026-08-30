"""SDK method introspection for OpenAI Python SDK.

Builds a method map by inspecting the OpenAI client class hierarchy.
No API calls are made - this is pure AST/reflection inspection.

Output: sdk_methods.json
"""

import ast
import inspect
import json
import sys
from pathlib import Path

# Ensure openai is importable
try:
    import openai
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed")
    sys.exit(1)


def get_public_methods(obj, prefix="client"):
    """Recursively inspect an object for public methods and sub-resources."""
    methods = {}

    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            attr = getattr(obj, name)
        except Exception:
            continue

        full_path = f"{prefix}.{name}"

        if callable(attr) and not isinstance(attr, type):
            # It's a method
            try:
                sig = inspect.signature(attr)
                params = []
                for pname, param in sig.parameters.items():
                    if pname in ("self", "cls"):
                        continue
                    p_info = {"name": pname}
                    if param.default is not inspect.Parameter.empty:
                        p_info["has_default"] = True
                    if param.kind == inspect.Parameter.KEYWORD_ONLY:
                        p_info["keyword_only"] = True
                    if param.annotation is not inspect.Parameter.empty:
                        try:
                            p_info["type"] = str(param.annotation)
                        except Exception:
                            pass
                    params.append(p_info)
                methods[full_path] = {
                    "type": "method",
                    "params": params,
                }
            except (ValueError, TypeError):
                methods[full_path] = {"type": "method", "params": []}

        elif hasattr(attr, "__class__") and not isinstance(attr, (str, int, float, bool, list, dict)):
            # It's a sub-resource (nested object)
            cls_name = type(attr).__name__
            if cls_name.endswith("Resource") or cls_name.endswith("Resources") or "With" in cls_name:
                methods[full_path] = {"type": "resource", "class": cls_name}
                # Recurse one level deeper
                sub_methods = get_public_methods(attr, full_path)
                methods.update(sub_methods)

    return methods


def introspect_client():
    """Build full method map from OpenAI client."""
    client = OpenAI(api_key="sk-fake-key-for-introspection")

    print(f"OpenAI SDK version: {openai.__version__}")
    print(f"Client class: {type(client).__name__}")
    print()

    methods = get_public_methods(client)

    # Categorize
    resources = {k: v for k, v in methods.items() if v["type"] == "resource"}
    callables = {k: v for k, v in methods.items() if v["type"] == "method"}

    print(f"Resources found: {len(resources)}")
    print(f"Methods found: {len(callables)}")
    print()

    # Print top-level resources
    top_resources = sorted(k for k in resources if k.count(".") == 1)
    print("Top-level resources:")
    for r in top_resources:
        print(f"  {r} ({resources[r]['class']})")

    print()
    print("Top-level methods (directly on client):")
    top_methods = sorted(k for k in callables if k.count(".") == 1)
    for m in top_methods:
        params = [p["name"] for p in callables[m]["params"]]
        print(f"  {m}({', '.join(params)})")

    return {
        "sdk_version": openai.__version__,
        "sdk_path": str(Path(openai.__file__).parent),
        "total_resources": len(resources),
        "total_methods": len(callables),
        "resources": resources,
        "methods": callables,
    }


def main():
    data = introspect_client()

    output_path = Path(__file__).parent / "sdk_methods.json"
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"\nSaved to: {output_path}")
    print(f"Total entries: {data['total_resources'] + data['total_methods']}")


if __name__ == "__main__":
    main()
