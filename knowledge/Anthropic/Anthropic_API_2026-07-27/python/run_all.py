"""Run all numbered test files (01-14) and produce aggregate summary."""
import json, subprocess, sys, time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PYTHON = sys.executable

# Discover all numbered test files
test_files = sorted(SCRIPT_DIR.glob("[0-9][0-9]_*_test.py"))

print(f"Python: {PYTHON}")
print(f"Found {len(test_files)} test files")
print("=" * 70)

summary = []
total_passed = total_failed = total_skipped = 0
t_start = time.time()

for tf in test_files:
  print(f"\n{'─' * 70}")
  print(f"Running: {tf.name}")
  print(f"{'─' * 70}")
  t0 = time.time()
  result = subprocess.run([PYTHON, str(tf)], capture_output=False, text=True)
  elapsed = time.time() - t0

  # Read the results file
  results_name = tf.stem.replace("_test", "_results") + ".json"
  results_path = SCRIPT_DIR / results_name
  if results_path.exists():
    results = json.loads(results_path.read_text(encoding="utf-8"))
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
  else:
    passed = failed = skipped = 0
    results = []

  total_passed += passed
  total_failed += failed
  total_skipped += skipped

  summary.append({
    "file": tf.name,
    "passed": passed,
    "failed": failed,
    "skipped": skipped,
    "total": len(results),
    "elapsed_s": round(elapsed, 1),
    "exit_code": result.returncode,
  })

total_elapsed = time.time() - t_start
print(f"\n{'=' * 70}")
print(f"AGGREGATE: {total_passed} passed, {total_failed} failed, {total_skipped} skipped")
print(f"           {total_passed + total_failed + total_skipped} total tests across {len(test_files)} files")
print(f"           {total_elapsed:.1f}s elapsed")
print(f"{'=' * 70}")

if total_failed:
  print("\nFILES WITH FAILURES:")
  for s in summary:
    if s["failed"] > 0:
      print(f"  {s['file']}: {s['failed']} failed")

# Write summary
summary_path = SCRIPT_DIR / "run_all_summary.json"
summary_path.write_text(json.dumps({
  "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
  "python": PYTHON,
  "elapsed_s": round(total_elapsed, 1),
  "totals": {"passed": total_passed, "failed": total_failed, "skipped": total_skipped},
  "files": summary,
}, indent=2), encoding="utf-8")
print(f"\nSummary: {summary_path.name}")

sys.exit(1 if total_failed else 0)
