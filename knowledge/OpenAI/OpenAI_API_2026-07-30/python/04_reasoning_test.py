"""Test: Reasoning (IN16)

Verifies Python SDK examples from:
- _INFO_OAIAPI-IN16_REASONING.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestRunner, get_client, REASONING_MODEL

runner = TestRunner("IN16", "Reasoning")


def test_reasoning_basic():
    t = runner.add_test("reasoning_basic")
    t.start()
    try:
        client = get_client()
        response = client.responses.create(
            model=REASONING_MODEL,
            input="What is the square root of 144?",
            reasoning={"effort": "low"},
        )
        assert response.output is not None
        t.passed()
    except Exception as e:
        t.failed(str(e))


def test_reasoning_medium_effort():
    t = runner.add_test("reasoning_medium_effort")
    t.start()
    try:
        client = get_client()
        response = client.responses.create(
            model=REASONING_MODEL,
            input="Solve: If a train travels at 60 mph for 2.5 hours, how far does it go?",
            reasoning={"effort": "medium"},
        )
        assert response.output is not None
        t.passed()
    except Exception as e:
        t.failed(str(e))


def test_reasoning_with_summary():
    t = runner.add_test("reasoning_with_summary")
    t.start()
    try:
        client = get_client()
        response = client.responses.create(
            model=REASONING_MODEL,
            input="Explain why the sky is blue in one sentence.",
            reasoning={"effort": "low", "summary": "auto"},
        )
        assert response.output is not None
        t.passed()
    except Exception as e:
        t.failed(str(e))


if __name__ == "__main__":
    print("Running Reasoning tests...")
    test_reasoning_basic()
    test_reasoning_medium_effort()
    test_reasoning_with_summary()

    summary = runner.summary()
    print(f"\nResults: {summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['skipped']} skipped ({summary['total']} total)")

    runner.save_results(Path(__file__).parent / "04_reasoning_results.json")
