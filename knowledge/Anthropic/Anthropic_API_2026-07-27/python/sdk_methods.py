"""Introspect all Python SDK client methods and their parameters.
Outputs sdk_methods.json with every method + accepted params.
Python SDK equivalent of javascript/sdk_methods.json generation.
"""
import inspect
import json
from pathlib import Path

import anthropic

def get_method_params(method):
  """Extract parameter names from a method signature."""
  try:
    sig = inspect.signature(method)
    return [
      name for name, param in sig.parameters.items()
      if name not in ("self", "cls") and param.kind not in (
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.VAR_KEYWORD,
      )
    ]
  except (ValueError, TypeError):
    return []

def walk_resources(obj, prefix="client", depth=0, visited=None):
  """Recursively walk SDK resource tree and collect methods."""
  if visited is None:
    visited = set()
  if depth > 5 or id(obj) in visited:
    return {}
  visited.add(id(obj))

  methods = {}
  for name in sorted(dir(obj)):
    if name.startswith("_"):
      continue
    try:
      attr = getattr(obj, name)
    except Exception:
      continue

    full_name = f"{prefix}.{name}"

    if callable(attr) and not isinstance(attr, type):
      params = get_method_params(attr)
      source_file = ""
      try:
        source_file = inspect.getfile(type(obj))
        source_file = str(Path(source_file).relative_to(Path(anthropic.__file__).parent))
      except Exception:
        pass
      methods[full_name] = {
        "params": params,
        "source": source_file,
        "class": type(obj).__name__,
      }
    elif hasattr(attr, "__class__") and not isinstance(attr, (str, int, float, bool, list, dict, type)):
      if "anthropic" in type(attr).__module__:
        sub_methods = walk_resources(attr, full_name, depth + 1, visited)
        methods.update(sub_methods)

  return methods

def main():
  client = anthropic.Anthropic(api_key="sk-ant-placeholder")
  print(f"SDK version: {anthropic.__version__}")
  print("Introspecting client methods...")

  methods = walk_resources(client)
  print(f"Found {len(methods)} methods/resources")

  out_path = Path(__file__).parent / "sdk_methods.json"
  out_path.write_text(json.dumps(methods, indent=2), encoding="utf-8")
  print(f"Results written to {out_path}")

if __name__ == "__main__":
  main()
