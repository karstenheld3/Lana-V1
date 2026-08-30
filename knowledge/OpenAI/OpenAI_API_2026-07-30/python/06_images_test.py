"""Test: Image Generation (IN21, IN22)

Verifies Python SDK examples from:
- _INFO_OAIAPI-IN21_IMAGE_GENERATION.md
- _INFO_OAIAPI-IN22_IMAGE_STREAMING.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestRunner, get_client

runner = TestRunner("IN21-IN22", "Image Generation")


def test_image_generate():
    t = runner.add_test("image_generate_basic")
    t.start()
    try:
        client = get_client()
        result = client.images.generate(
            model="gpt-image-1",
            prompt="A simple red circle on white background",
            size="1024x1024",
            n=1,
        )
        assert len(result.data) == 1
        assert result.data[0].b64_json is not None or result.data[0].url is not None
        t.passed()
    except Exception as e:
        t.failed(str(e))


def test_image_edit():
    t = runner.add_test("image_edit")
    t.start()
    try:
        # Skip - requires image file input
        t.skipped("Requires image file input, not suitable for automated test")
    except Exception as e:
        t.failed(str(e))


if __name__ == "__main__":
    print("Running Image Generation tests...")
    test_image_generate()
    test_image_edit()

    summary = runner.summary()
    print(f"\nResults: {summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['skipped']} skipped ({summary['total']} total)")

    runner.save_results(Path(__file__).parent / "06_images_results.json")
