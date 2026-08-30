"""IN23, IN29: Tool use - definition, agentic loop, tool_choice, streaming tools."""
import json, sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import client, test, finish, DEFAULT_MODEL

WEATHER_TOOL = {
  "name": "get_weather",
  "description": "Get current weather for a location",
  "input_schema": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]},
}

def test_tool_definition():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=1024,
    tools=[WEATHER_TOOL],
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
  )
  tool_block = next((b for b in msg.content if b.type == "tool_use"), None)
  return {"stop_reason": msg.stop_reason, "tool_name": tool_block.name if tool_block else None}

test("Tool definition + invocation", test_tool_definition)

# Full agentic loop: tool_use -> tool_result -> end_turn
def test_agentic_loop():
  tools = [WEATHER_TOOL]
  messages = [{"role": "user", "content": "What's the weather in NYC?"}]
  loops = 0
  final_text = ""
  for _ in range(5):
    loops += 1
    response = client.messages.create(model=DEFAULT_MODEL, max_tokens=1024, tools=tools, messages=messages)
    if response.stop_reason == "end_turn":
      for b in response.content:
        if b.type == "text":
          final_text += b.text
      break
    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for b in response.content:
      if b.type == "tool_use":
        tool_results.append({"type": "tool_result", "tool_use_id": b.id, "content": '{"temp": "72F", "condition": "sunny"}'})
    messages.append({"role": "user", "content": tool_results})
  return {"loops": loops, "has_text": len(final_text) > 0}

test("Agentic loop (tool_use -> tool_result -> end_turn)", test_agentic_loop)

def test_tool_choice_specific():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=1024,
    tools=[WEATHER_TOOL],
    tool_choice={"type": "tool", "name": "get_weather"},
    messages=[{"role": "user", "content": "Tokyo weather"}],
  )
  tool_block = next((b for b in msg.content if b.type == "tool_use"), None)
  return {"forced_tool": tool_block.name if tool_block else None}

test("tool_choice: specific tool", test_tool_choice_specific)

def test_tool_choice_any():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=1024,
    tools=[WEATHER_TOOL],
    tool_choice={"type": "any"},
    messages=[{"role": "user", "content": "Hello, how are you?"}],
  )
  has_tool = any(b.type == "tool_use" for b in msg.content)
  return {"stop_reason": msg.stop_reason, "forced_any_tool": has_tool}

test("tool_choice: any", test_tool_choice_any)

# IN29: Streaming tool use with input_json_delta accumulation
def test_streaming_tool():
  tool_name = ""
  tool_input = ""
  with client.messages.stream(
    model=DEFAULT_MODEL, max_tokens=1024,
    tools=[WEATHER_TOOL],
    tool_choice={"type": "tool", "name": "get_weather"},
    messages=[{"role": "user", "content": "Tokyo weather"}],
  ) as stream:
    for event in stream:
      if hasattr(event, "type"):
        if event.type == "content_block_start" and event.content_block.type == "tool_use":
          tool_name = event.content_block.name
        elif event.type == "content_block_delta" and event.delta.type == "input_json_delta":
          tool_input += event.delta.partial_json
  parsed = json.loads(tool_input) if tool_input else None
  return {"tool_name": tool_name, "input": parsed}

test("Streaming tool use (input_json_delta)", test_streaming_tool)

# Multiple tools defined
def test_multi_tool():
  tools = [
    WEATHER_TOOL,
    {
      "name": "get_time",
      "description": "Get current time in a timezone",
      "input_schema": {"type": "object", "properties": {"timezone": {"type": "string"}}, "required": ["timezone"]},
    },
  ]
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What time is it in Tokyo?"}],
  )
  tool_block = next((b for b in msg.content if b.type == "tool_use"), None)
  return {"stop_reason": msg.stop_reason, "tool_used": tool_block.name if tool_block else None}

test("Multiple tool definitions", test_multi_tool)

finish(__file__)
