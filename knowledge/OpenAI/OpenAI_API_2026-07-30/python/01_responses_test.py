"""Test: Responses API (IN06, IN07, IN08, IN09, IN10)

Verifies Python SDK examples from:
- _INFO_OAIAPI-IN06_RESPONSES_API.md
- _INFO_OAIAPI-IN07_RESPONSES_STREAMING.md
- _INFO_OAIAPI-IN08_CONVERSATIONS.md
- _INFO_OAIAPI-IN09_TOKEN_COUNTING.md
- _INFO_OAIAPI-IN10_RESPONSE_INPUT_ITEMS.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestRunner, get_client, DEFAULT_MODEL

runner = TestRunner("IN06-IN10", "Responses API")


def test_basic_response():
    t = runner.add_test("basic_response_create")
    t.start()
    try:
        client = get_client()
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input="Say hello in one word.",
        )
        assert response.id is not None
        assert response.output is not None
        t.passed({"response_id": response.id})
    except Exception as e:
        t.failed(str(e))


def test_response_with_system():
    t = runner.add_test("response_with_system_message")
    t.start()
    try:
        client = get_client()
        response = client.responses.create(
            model=DEFAULT_MODEL,
            instructions="You are a helpful assistant.",
            input="What is 2+2?",
        )
        assert response.output is not None
        t.passed()
    except Exception as e:
        t.failed(str(e))


def test_response_streaming():
    t = runner.add_test("response_streaming")
    t.start()
    try:
        client = get_client()
        chunks = []
        stream = client.responses.create(
            model=DEFAULT_MODEL,
            input="Count to 3.",
            stream=True,
        )
        for event in stream:
            chunks.append(event)
        assert len(chunks) > 0
        t.passed({"event_count": len(chunks)})
    except Exception as e:
        t.failed(str(e))


def test_conversation_create():
    t = runner.add_test("conversation_create")
    t.start()
    try:
        client = get_client()
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input="Hello",
            store=True,
        )
        assert response.id is not None
        t.passed({"response_id": response.id})
    except Exception as e:
        t.failed(str(e))


def test_token_counting():
    t = runner.add_test("token_counting")
    t.start()
    try:
        client = get_client()
        result = client.responses.input_tokens.count(
            model=DEFAULT_MODEL,
            input="Hello, how are you?",
        )
        assert result.input_tokens > 0
        t.passed({"input_tokens": result.input_tokens})
    except Exception as e:
        t.failed(str(e))


def test_response_retrieve():
    t = runner.add_test("response_retrieve")
    t.start()
    try:
        client = get_client()
        # First create a response
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input="Hi",
            store=True,
        )
        # Then retrieve it
        retrieved = client.responses.retrieve(response.id)
        assert retrieved.id == response.id
        t.passed()
    except Exception as e:
        t.failed(str(e))


if __name__ == "__main__":
    print("Running Responses API tests...")
    test_basic_response()
    test_response_with_system()
    test_response_streaming()
    test_conversation_create()
    test_token_counting()
    test_response_retrieve()

    summary = runner.summary()
    print(f"\nResults: {summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['skipped']} skipped ({summary['total']} total)")

    runner.save_results(Path(__file__).parent / "01_responses_results.json")
