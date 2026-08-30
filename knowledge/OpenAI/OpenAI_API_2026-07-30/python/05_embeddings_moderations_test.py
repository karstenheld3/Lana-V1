"""Test: Embeddings and Moderations (IN25, IN26)

Verifies Python SDK examples from:
- _INFO_OAIAPI-IN25_EMBEDDINGS.md
- _INFO_OAIAPI-IN26_MODERATIONS.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestRunner, get_client

runner = TestRunner("IN25-IN26", "Embeddings and Moderations")


def test_embedding_create():
    t = runner.add_test("embedding_create")
    t.start()
    try:
        client = get_client()
        result = client.embeddings.create(
            model="text-embedding-3-small",
            input="Hello world",
        )
        assert len(result.data) > 0
        assert len(result.data[0].embedding) > 0
        t.passed({"dimensions": len(result.data[0].embedding)})
    except Exception as e:
        t.failed(str(e))


def test_embedding_batch():
    t = runner.add_test("embedding_batch")
    t.start()
    try:
        client = get_client()
        result = client.embeddings.create(
            model="text-embedding-3-small",
            input=["Hello", "World", "Test"],
        )
        assert len(result.data) == 3
        t.passed()
    except Exception as e:
        t.failed(str(e))


def test_embedding_dimensions():
    t = runner.add_test("embedding_custom_dimensions")
    t.start()
    try:
        client = get_client()
        result = client.embeddings.create(
            model="text-embedding-3-small",
            input="Hello world",
            dimensions=256,
        )
        assert len(result.data[0].embedding) == 256
        t.passed()
    except Exception as e:
        t.failed(str(e))


def test_moderation_create():
    t = runner.add_test("moderation_create")
    t.start()
    try:
        client = get_client()
        result = client.moderations.create(
            model="omni-moderation-latest",
            input="I love puppies",
        )
        assert result.results is not None
        assert len(result.results) > 0
        assert result.results[0].flagged is False
        t.passed()
    except Exception as e:
        t.failed(str(e))


def test_moderation_flagged():
    t = runner.add_test("moderation_flagged_content")
    t.start()
    try:
        client = get_client()
        result = client.moderations.create(
            model="omni-moderation-latest",
            input="I want to hurt someone badly",
        )
        assert result.results[0].flagged is True
        t.passed({"categories": {k: v for k, v in result.results[0].categories.model_dump().items() if v}})
    except Exception as e:
        t.failed(str(e))


if __name__ == "__main__":
    print("Running Embeddings and Moderations tests...")
    test_embedding_create()
    test_embedding_batch()
    test_embedding_dimensions()
    test_moderation_create()
    test_moderation_flagged()

    summary = runner.summary()
    print(f"\nResults: {summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['skipped']} skipped ({summary['total']} total)")

    runner.save_results(Path(__file__).parent / "05_embeddings_moderations_results.json")
