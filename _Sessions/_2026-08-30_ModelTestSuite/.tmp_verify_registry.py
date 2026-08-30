"""Temp verification: all available models resolve, JSON files valid (SOP 4)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from lana.config import RoleSpec, read_json, resolve_role

cfg = Path(__file__).resolve().parents[2] / "config"
registry = read_json(cfg / "model-registry.json")
mapping = read_json(cfg / "model-parameter-mapping.json")
json.loads((cfg / "model-pricing.json").read_text(encoding="utf-8"))
print("All 3 JSON files valid.")

models = [m for m in registry["models"] if m.get("enabled") and m.get("status") == "available"]
print(f"{len(models)} available models:")
failures = 0
for m in models:
  try:
    r = resolve_role("test", RoleSpec(model_id=m["model_id"], effort="medium"), registry, mapping)
    print(f"  {m['model_id']}: {r.method} params={r.params} max_out={r.max_output}" + (f" beta={r.beta}" if r.beta else ""))
  except Exception as error:
    failures += 1
    print(f"  {m['model_id']}: FAIL {error}")
print(f"RESULT: {'OK' if failures == 0 else f'{failures} FAILED'}")
sys.exit(1 if failures else 0)
