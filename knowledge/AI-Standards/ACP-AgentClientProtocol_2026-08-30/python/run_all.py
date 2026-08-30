"""Run all ACP Python SDK verification tests and aggregate results."""
import json
import subprocess
import sys
import time
from pathlib import Path

PYTHON = sys.executable
HERE = Path(__file__).parent
TEST_FILES = sorted(HERE.glob("[0-9][0-9]_*_test.py"))

def main():
    print(f"ACP Python SDK Verification")
    print(f"Python: {sys.version}")
    print(f"Test files: {len(TEST_FILES)}")
    print(f"{'='*60}\n")

    all_results = []
    total_pass = 0
    total_fail = 0
    total_skip = 0
    t0 = time.perf_counter()

    for tf in TEST_FILES:
        print(f"--- {tf.name} ---")
        result = subprocess.run(
            [PYTHON, str(tf)],
            capture_output=True, text=True, timeout=30,
        )
        print(result.stdout)
        if result.stderr:
            print(f"  stderr: {result.stderr[:200]}")

        # Read results JSON
        results_file = tf.with_name(tf.stem.replace("_test", "_results") + ".json")
        if results_file.exists():
            with open(results_file, encoding="utf-8") as f:
                data = json.load(f)
            total_pass += data.get("passed", 0)
            total_fail += data.get("failed", 0)
            total_skip += data.get("skipped", 0)
            all_results.append(data)
        print()

    elapsed = time.perf_counter() - t0
    total = total_pass + total_fail + total_skip

    summary = {
        "sdk": "agent-client-protocol",
        "total_tests": total,
        "passed": total_pass,
        "failed": total_fail,
        "skipped": total_skip,
        "duration_seconds": round(elapsed, 1),
        "test_files": len(TEST_FILES),
        "suites": all_results,
    }

    out = HERE / "run_all_summary.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"{'='*60}")
    print(f"TOTAL: {total_pass} passed, {total_fail} failed, {total_skip} skipped ({total} total, {elapsed:.1f}s)")
    print(f"Results: {out}")
    print(f"{'='*60}")

    sys.exit(1 if total_fail else 0)

if __name__ == "__main__":
    main()
