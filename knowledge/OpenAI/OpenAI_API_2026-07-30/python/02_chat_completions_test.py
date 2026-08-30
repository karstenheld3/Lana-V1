"""Test: Chat Completions (IN55, IN56, IN57)

Verifies Python SDK examples from:
- _INFO_OAIAPI-IN55_CHAT_COMPLETIONS.md
- _INFO_OAIAPI-IN56_CHAT_STREAMING.md
- _INFO_OAIAPI-IN57_CHAT_MESSAGES.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestRunner, get_client, DEFAULT_MODEL

runner = TestRunner("IN55-IN57", "Chat Completions")


def test_basic_chat():
    t = runner.add_test("basic_chat_completion")
    t.start()
    try:
        client = get_client()
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one word."},
            ],
        )
        assert completion.choices[0].message.content is not None
        t.passed({"model": completion.model})
    except Exception as e:
        t.failed(str(e))


def test_chat_streaming():
    t = runner.add_test("chat_streaming")
    t.start()
    try:
        client = get_client()
        chunks = []
        stream = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "Count to 3."}],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                chunks.append(chunk.choices[0].delta.content)
        assert len(chunks) > 0
        t.passed({"chunk_count": len(chunks)})
    except Exception as e:
        t.failed(str(e))


def test_chat_with_temperature():
    t = runner.add_test("chat_with_temperature")
    t.start()
    try:
        client = get_client()
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "Pick a random color."}],
            temperature=0.0,
        )
        assert completion.choices[0].message.content is not None
        t.passed()
    except Exception as e:
        t.failed(str(e))


def test_chat_multi_turn():
    t = runner.add_test("chat_multi_turn")
    t.start()
    try:
        client = get_client()
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a math tutor."},
                {"role": "user", "content": "What is 5+3?"},
                {"role": "assistant", "content": "5+3 = 8"},
                {"role": "user", "content": "And times 2?"},
            ],
        )
        assert "16" in completion.choices[0].message.content
        t.passed()
    except Exception as e:
        t.failed(str(e))


if __name__ == "__main__":
    print("Running Chat Completions tests...")
    test_basic_chat()
    test_chat_streaming()
    test_chat_with_temperature()
    test_chat_multi_turn()

    summary = runner.summary()
    print(f"\nResults: {summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['skipped']} skipped ({summary['total']} total)")

    runner.save_results(Path(__file__).parent / "02_chat_completions_results.json")
