"""IN11: All stop reason values and handling patterns."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import client, test, finish, DEFAULT_MODEL

def test_end_turn():
  response = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=1024,
    messages=[{"role": "user", "content": "What is 2+2?"}],
  )
  return {"stop_reason": response.stop_reason, "text": response.content[0].text}

test("end_turn stop reason", test_end_turn)

def test_max_tokens():
  response = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=5,
    messages=[{"role": "user", "content": "Explain quantum physics in great detail"}],
  )
  return {"stop_reason": response.stop_reason, "truncated": response.stop_reason == "max_tokens"}

test("max_tokens stop reason", test_max_tokens)

def test_stop_sequence():
  response = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=1024,
    stop_sequences=["END"],
    messages=[{"role": "user", "content": "Write: Hello END World"}],
  )
  return {"stop_reason": response.stop_reason, "stop_sequence": response.stop_sequence}

test("stop_sequence stop reason", test_stop_sequence)

def test_tool_use():
  response = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=1024,
    tools=[{
      "name": "get_weather",
      "description": "Get the current weather in a given location",
      "input_schema": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]},
    }],
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
  )
  return {"stop_reason": response.stop_reason, "has_tool_use": any(b.type == "tool_use" for b in response.content)}

test("tool_use stop reason", test_tool_use)

# Match/case pattern from IN11 docs
def test_match_case_handler():
  response = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=64,
    messages=[{"role": "user", "content": "Reply with: OK"}],
  )
  match response.stop_reason:
    case "end_turn":
      result = response.content[0].text
    case "max_tokens":
      result = response.content[0].text + " [TRUNCATED]"
    case "stop_sequence":
      result = response.content[0].text
    case "tool_use":
      result = "[tool_use]"
    case "pause_turn":
      result = "[pause_turn]"
    case "refusal":
      result = "Request declined"
    case _:
      result = f"Unknown: {response.stop_reason}"
  return {"result": result, "stop_reason": response.stop_reason}

test("match/case stop reason handler", test_match_case_handler)

# pause_turn requires server tools; verify the pattern compiles
def test_pause_turn():
  response = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=2048,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{"role": "user", "content": "Search for latest AI research papers"}],
  )
  # May get end_turn or pause_turn depending on search iteration
  return {"stop_reason": response.stop_reason, "content_types": [b.type for b in response.content]}

test("pause_turn pattern (web_search server tool)", test_pause_turn)

finish(__file__)
