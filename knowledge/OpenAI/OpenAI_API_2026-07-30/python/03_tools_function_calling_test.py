"""Test: Tools and Function Calling (IN12, IN13, IN14, IN15)

Verifies Python SDK examples from:
- _INFO_OAIAPI-IN12_TOOLS_OVERVIEW.md
- _INFO_OAIAPI-IN13_FUNCTION_CALLING.md
- _INFO_OAIAPI-IN14_WEB_SEARCH.md
- _INFO_OAIAPI-IN15_STRUCTURED_OUTPUTS.md
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestRunner, get_client, DEFAULT_MODEL

runner = TestRunner("IN12-IN15", "Tools and Function Calling")


def test_function_calling():
    t = runner.add_test("function_calling_basic")
    t.start()
    try:
        client = get_client()
        tools = [
            {
                "type": "function",
                "name": "get_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"},
                    },
                    "required": ["location"],
                },
            }
        ]
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input="What's the weather in Paris?",
            tools=tools,
        )
        # Should trigger a function call
        has_tool_call = any(
            item.type == "function_call" for item in response.output
        )
        assert has_tool_call, "Expected function_call in output"
        t.passed()
    except Exception as e:
        t.failed(str(e))


def test_web_search():
    t = runner.add_test("web_search_tool")
    t.start()
    try:
        client = get_client()
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input="What is the latest news about OpenAI?",
            tools=[{"type": "web_search_preview"}],
        )
        assert response.output is not None
        t.passed()
    except Exception as e:
        t.failed(str(e))


def test_structured_output_json_schema():
    t = runner.add_test("structured_output_json_schema")
    t.start()
    try:
        client = get_client()
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input="List 3 colors as JSON",
            text={
                "format": {
                    "type": "json_schema",
                    "name": "colors",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "colors": {
                                "type": "array",
                                "items": {"type": "string"},
                            }
                        },
                        "required": ["colors"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                }
            },
        )
        output_text = response.output_text
        assert output_text is not None
        parsed = json.loads(output_text)
        assert "colors" in parsed
        t.passed({"colors": parsed["colors"]})
    except Exception as e:
        t.failed(str(e))


def test_structured_output_json_object():
    t = runner.add_test("structured_output_json_object")
    t.start()
    try:
        client = get_client()
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input="Return a JSON object with key 'answer' and value 42",
            text={"format": {"type": "json_object"}},
        )
        output_text = response.output_text
        assert output_text is not None
        parsed = json.loads(output_text)
        assert "answer" in parsed
        t.passed()
    except Exception as e:
        t.failed(str(e))


if __name__ == "__main__":
    print("Running Tools and Function Calling tests...")
    test_function_calling()
    test_web_search()
    test_structured_output_json_schema()
    test_structured_output_json_object()

    summary = runner.summary()
    print(f"\nResults: {summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['skipped']} skipped ({summary['total']} total)")

    runner.save_results(Path(__file__).parent / "03_tools_function_calling_results.json")
