"""ACP Python SDK introspection - enumerate public API surface.

No API calls. Inspects the installed `agent-client-protocol` package
and outputs structured data about available modules, classes, and methods.
"""
import importlib
import inspect
import json
import pkgutil
import sys
from pathlib import Path

PACKAGE = "acp"

def get_submodules(package_name: str) -> list[str]:
    """Return all importable submodule names under *package_name*."""
    try:
        pkg = importlib.import_module(package_name)
    except ImportError:
        return []
    if not hasattr(pkg, "__path__"):
        return [package_name]
    names = [package_name]
    for info in pkgutil.walk_packages(pkg.__path__, prefix=package_name + "."):
        names.append(info.name)
    return names

def inspect_module(module_name: str) -> dict:
    """Return public classes and functions from *module_name*."""
    try:
        mod = importlib.import_module(module_name)
    except Exception as exc:
        return {"module": module_name, "error": str(exc)}
    result = {"module": module_name, "classes": [], "functions": []}
    for name, obj in inspect.getmembers(mod):
        if name.startswith("_"):
            continue
        if inspect.isclass(obj) and obj.__module__.startswith(PACKAGE):
            cls_info = {
                "name": name,
                "bases": [b.__name__ for b in obj.__bases__],
                "methods": [],
            }
            for mname, mobj in inspect.getmembers(obj):
                if mname.startswith("_") and mname != "__init__":
                    continue
                if inspect.isfunction(mobj) or inspect.ismethod(mobj):
                    try:
                        sig = str(inspect.signature(mobj))
                    except (ValueError, TypeError):
                        sig = "(...)"
                    cls_info["methods"].append({"name": mname, "signature": sig})
            result["classes"].append(cls_info)
        elif inspect.isfunction(obj) and obj.__module__.startswith(PACKAGE):
            try:
                sig = str(inspect.signature(obj))
            except (ValueError, TypeError):
                sig = "(...)"
            result["functions"].append({"name": name, "signature": sig})
    return result

def main():
    print(f"Inspecting {PACKAGE} package...")
    version = "unknown"
    try:
        import acp
        version = getattr(acp, "__version__", "unknown")
    except Exception:
        pass
    try:
        from importlib.metadata import version as pkg_version
        version = pkg_version("agent-client-protocol")
    except Exception:
        pass

    submodules = get_submodules(PACKAGE)
    print(f"Found {len(submodules)} submodules")

    results = {
        "package": "agent-client-protocol",
        "version": version,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "submodule_count": len(submodules),
        "submodules": [],
    }

    for mod_name in sorted(submodules):
        info = inspect_module(mod_name)
        if info.get("classes") or info.get("functions") or info.get("error"):
            results["submodules"].append(info)

    out_path = Path(__file__).parent / "sdk_methods.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_path}")

    # Summary
    total_classes = sum(len(s.get("classes", [])) for s in results["submodules"])
    total_functions = sum(len(s.get("functions", [])) for s in results["submodules"])
    errors = [s for s in results["submodules"] if "error" in s]
    print(f"\nSummary:")
    print(f"  Version: {version}")
    print(f"  Submodules: {len(submodules)}")
    print(f"  Public classes: {total_classes}")
    print(f"  Public functions: {total_functions}")
    print(f"  Import errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"    - {e['module']}: {e['error']}")

if __name__ == "__main__":
    main()
