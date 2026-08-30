"""Test: Models API (IN03, IN27)

Verifies Python SDK examples from:
- _INFO_OAIAPI-IN03_MODELS.md
- _INFO_OAIAPI-IN27_MODELS_API.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestRunner, get_client

runner = TestRunner("IN03-IN27", "Models API")


def test_models_list():
    t = runner.add_test("models_list")
    t.start()
    try:
        client = get_client()
        models = client.models.list()
        model_list = list(models)
        assert len(model_list) > 0
        t.passed({"model_count": len(model_list)})
    except Exception as e:
        t.failed(str(e))


def test_model_retrieve():
    t = runner.add_test("model_retrieve")
    t.start()
    try:
        client = get_client()
        model = client.models.retrieve("gpt-4o-mini")
        assert model.id == "gpt-4o-mini"
        t.passed({"owned_by": model.owned_by})
    except Exception as e:
        t.failed(str(e))


if __name__ == "__main__":
    print("Running Models API tests...")
    test_models_list()
    test_model_retrieve()

    summary = runner.summary()
    print(f"\nResults: {summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['skipped']} skipped ({summary['total']} total)")

    runner.save_results(Path(__file__).parent / "09_models_results.json")
