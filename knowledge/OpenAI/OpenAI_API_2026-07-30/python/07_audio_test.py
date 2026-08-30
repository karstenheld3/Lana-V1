"""Test: Audio (IN18, IN19)

Verifies Python SDK examples from:
- _INFO_OAIAPI-IN18_AUDIO_TRANSCRIPTION.md
- _INFO_OAIAPI-IN19_TEXT_TO_SPEECH.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestRunner, get_client

runner = TestRunner("IN18-IN19", "Audio")


def test_tts_create():
    t = runner.add_test("text_to_speech")
    t.start()
    try:
        client = get_client()
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input="Hello, this is a test.",
        )
        # Response is audio bytes
        content = response.content
        assert len(content) > 0
        t.passed({"bytes": len(content)})
    except Exception as e:
        t.failed(str(e))


def test_transcription():
    t = runner.add_test("audio_transcription")
    t.start()
    try:
        # Skip - requires audio file input
        t.skipped("Requires audio file input")
    except Exception as e:
        t.failed(str(e))


if __name__ == "__main__":
    print("Running Audio tests...")
    test_tts_create()
    test_transcription()

    summary = runner.summary()
    print(f"\nResults: {summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['skipped']} skipped ({summary['total']} total)")

    runner.save_results(Path(__file__).parent / "07_audio_results.json")
