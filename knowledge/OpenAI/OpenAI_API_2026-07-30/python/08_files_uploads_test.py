"""Test: Files and Uploads (IN33, IN34)

Verifies Python SDK examples from:
- _INFO_OAIAPI-IN33_FILES.md
- _INFO_OAIAPI-IN34_UPLOADS.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestRunner, get_client

runner = TestRunner("IN33-IN34", "Files and Uploads")


def test_files_list():
    t = runner.add_test("files_list")
    t.start()
    try:
        client = get_client()
        files = client.files.list()
        # Just verify the API call works
        assert files is not None
        t.passed({"file_count": len(list(files))})
    except Exception as e:
        t.failed(str(e))


def test_file_upload():
    t = runner.add_test("file_upload")
    t.start()
    try:
        # Skip - would create persistent state
        t.skipped("File upload creates persistent state, skipping in automated tests")
    except Exception as e:
        t.failed(str(e))


if __name__ == "__main__":
    print("Running Files and Uploads tests...")
    test_files_list()
    test_file_upload()

    summary = runner.summary()
    print(f"\nResults: {summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['skipped']} skipped ({summary['total']} total)")

    runner.save_results(Path(__file__).parent / "08_files_uploads_results.json")
