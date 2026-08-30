"""Shared test harness for Anthropic SDK documentation tests.
Provides client initialization, test runner, and result writing.
"""
import json, time
from pathlib import Path

import anthropic

# ── API Keys ─────────────────────────────────────────────────────────────────
_KEY_FILES = [
  Path(__file__).resolve().parents[4] / ".api-keys.txt",       # project-local
  Path(__file__).resolve().parents[4].parent / ".tools" / ".api-keys.txt",  # shared tools
]
KEYS = {}
for _kf in _KEY_FILES:
  if not _kf.exists():
    continue
  for _line in _kf.read_text(encoding="utf-8").splitlines():
    _line = _line.strip()
    if not _line or _line.startswith("#"):
      continue
    if "=" not in _line:
      continue
    _idx = _line.index("=")
    _key = _line[:_idx].strip()
    if _key not in KEYS:  # first file wins for duplicates
      KEYS[_key] = _line[_idx + 1:].strip()

# ── Clients ──────────────────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=KEYS["ANTHROPIC_API_KEY"])
ADMIN_KEY = KEYS.get("ANTHROPIC_ADMIN_KEY")

# ── Model Constants ──────────────────────────────────────────────────────────
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
OPUS_MODEL = "claude-opus-4-5-20251101"
ADAPTIVE_MODEL = "claude-opus-4-8"

# ── Test Harness ─────────────────────────────────────────────────────────────
_results = []
_test_num = 0

def reset():
  global _results, _test_num
  _results = []
  _test_num = 0

def test(label, fn, *, skip=None):
  global _test_num
  _test_num += 1
  if skip:
    _results.append({"n": _test_num, "label": label, "status": "SKIP", "reason": skip, "ms": 0})
    print(f"SKIP  [{_test_num}] {label} -- {skip}")
    return
  t0 = time.time()
  try:
    info = fn()
    ms = int((time.time() - t0) * 1000)
    _results.append({"n": _test_num, "label": label, "status": "PASS", "ms": ms, **(info or {})})
    print(f"PASS  [{_test_num}] {label} ({ms}ms)")
  except Exception as err:
    ms = int((time.time() - t0) * 1000)
    _results.append({
      "n": _test_num, "label": label, "status": "FAIL", "ms": ms,
      "error_type": type(err).__name__, "error": str(err)[:300],
    })
    print(f"FAIL  [{_test_num}] {label} ({ms}ms) -> {str(err)[:120]}")

# Print summary and write results JSON
def finish(script_path: str):
  passed = sum(1 for r in _results if r["status"] == "PASS")
  failed = sum(1 for r in _results if r["status"] == "FAIL")
  skipped = sum(1 for r in _results if r["status"] == "SKIP")
  print(f"\n{'=' * 70}")
  print(f"SUMMARY: {passed} passed, {failed} failed, {skipped} skipped ({len(_results)} total)")

  if failed:
    print("\nFAILED:")
    for r in _results:
      if r["status"] == "FAIL":
        print(f"  [{r['n']}] {r['label']} -> {r.get('error', '')[:100]}")

  out_path = Path(script_path).with_name(Path(script_path).stem.replace("_test", "_results") + ".json")
  out_path.write_text(json.dumps(_results, indent=2), encoding="utf-8")
  print(f"Results: {out_path.name}")
  return {"passed": passed, "failed": failed, "skipped": skipped, "total": len(_results)}
