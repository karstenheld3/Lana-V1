"""Run all test files and aggregate results.

Usage:
    python run_all.py          # Run all tests
    python run_all.py --dry    # List test files without running
"""

import json
import subprocess
import sys
import time
from pathlib import Path

PYTHON = sys.executable
TEST_DIR = Path(__file__).parent


def find_test_files():
    """Find all NN_*_test.py files in order."""
    files = sorted(TEST_DIR.glob("[0-9][0-9]_*_test.py"))
    return files


def run_test_file(test_file: Path) -> dict:
    """Run a single test file and return its results."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file.name}")
    print(f"{'='*60}")

    start = time.time()
    result = subprocess.run(
        [PYTHON, str(test_file)],
        capture_output=True,
        text=True,
        cwd=str(TEST_DIR),
    )
    duration = time.time() - start

    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr[:500]}")

    # Try to read the results JSON
    results_file = test_file.with_name(
        test_file.stem.replace("_test", "_results") + ".json"
    )
    if results_file.exists():
        data = json.loads(results_file.read_text(encoding="utf-8"))
        data["duration_s"] = round(duration, 1)
        data["exit_code"] = result.returncode
        return data

    return {
        "topic_id": test_file.stem,
        "error": "No results file produced",
        "exit_code": result.returncode,
        "stdout": result.stdout[-500:] if result.stdout else "",
        "stderr": result.stderr[-500:] if result.stderr else "",
        "duration_s": round(duration, 1),
    }


def main():
    test_files = find_test_files()

    if "--dry" in sys.argv:
        print(f"Found {len(test_files)} test files:")
        for f in test_files:
            print(f"  {f.name}")
        return

    print(f"Running {len(test_files)} test files...")
    print(f"Python: {PYTHON}")
    print(f"Test dir: {TEST_DIR}")

    all_results = []
    total_start = time.time()

    for test_file in test_files:
        result = run_test_file(test_file)
        all_results.append(result)

    total_duration = time.time() - total_start

    # Aggregate summary
    total_passed = sum(r.get("summary", {}).get("passed", 0) for r in all_results)
    total_failed = sum(r.get("summary", {}).get("failed", 0) for r in all_results)
    total_skipped = sum(r.get("summary", {}).get("skipped", 0) for r in all_results)
    total_tests = sum(r.get("summary", {}).get("total", 0) for r in all_results)
    errors = sum(1 for r in all_results if "error" in r and r.get("exit_code", 0) != 0)

    summary = {
        "sdk_version": "openai 2.45.0",
        "run_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_files": len(test_files),
        "total_tests": total_tests,
        "passed": total_passed,
        "failed": total_failed,
        "skipped": total_skipped,
        "file_errors": errors,
        "total_duration_s": round(total_duration, 1),
        "results_per_file": [
            {
                "file": test_files[i].name,
                "topic_id": r.get("topic_id", "unknown"),
                "summary": r.get("summary", {}),
                "duration_s": r.get("duration_s", 0),
            }
            for i, r in enumerate(all_results)
        ],
    }

    # Save aggregated results
    output_path = TEST_DIR / "run_all_summary.json"
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Print final summary
    print(f"\n{'='*60}")
    print(f"FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Test files: {len(test_files)}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Skipped: {total_skipped}")
    print(f"File errors: {errors}")
    print(f"Duration: {total_duration:.1f}s")
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
