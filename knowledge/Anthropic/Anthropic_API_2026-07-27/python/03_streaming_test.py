"""IN09: Streaming - text_stream, event types, get_final_message, thinking deltas."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import client, test, finish, DEFAULT_MODEL

def test_text_stream():
  text = ""
  with client.messages.stream(
    model=DEFAULT_MODEL, max_tokens=64,
    messages=[{"role": "user", "content": "Reply with: OK"}],
  ) as stream:
    for chunk in stream.text_stream:
      text += chunk
  return {"text": text}

test("Basic streaming (text_stream)", test_text_stream)

def test_event_types():
  event_types = set()
  with client.messages.stream(
    model=DEFAULT_MODEL, max_tokens=64,
    messages=[{"role": "user", "content": "Reply with: OK"}],
  ) as stream:
    for event in stream:
      event_types.add(type(event).__name__)
  return {"event_types": sorted(event_types)}

test("Stream event types", test_event_types)

def test_get_final_message():
  with client.messages.stream(
    model=DEFAULT_MODEL, max_tokens=64,
    messages=[{"role": "user", "content": "Reply with: OK"}],
  ) as stream:
    msg = stream.get_final_message()
  return {"text": msg.content[0].text, "stop_reason": msg.stop_reason}

test("get_final_message()", test_get_final_message)

def test_streaming_thinking():
  thinking_text = ""
  answer_text = ""
  with client.messages.stream(
    model=DEFAULT_MODEL, max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 2000},
    messages=[{"role": "user", "content": "Reply with: OK"}],
  ) as stream:
    for event in stream:
      if hasattr(event, "type"):
        if event.type == "content_block_delta":
          if hasattr(event.delta, "thinking"):
            thinking_text += event.delta.thinking
          elif hasattr(event.delta, "text"):
            answer_text += event.delta.text
  return {"has_thinking": len(thinking_text) > 0, "answer": answer_text}

test("Streaming with thinking_delta", test_streaming_thinking)

# Full event handling pattern from IN09
def test_event_switch():
  model_name = ""
  stop_reason = ""
  output_tokens = 0
  text = ""
  with client.messages.stream(
    model=DEFAULT_MODEL, max_tokens=128,
    messages=[{"role": "user", "content": "Reply with: OK"}],
  ) as stream:
    for event in stream:
      if hasattr(event, "type"):
        if event.type == "message_start":
          model_name = event.message.model
        elif event.type == "content_block_delta" and hasattr(event.delta, "text"):
          text += event.delta.text
        elif event.type == "message_delta":
          stop_reason = event.delta.stop_reason
          output_tokens = event.usage.output_tokens
  return {"model": model_name, "text": text, "stop_reason": stop_reason, "output_tokens": output_tokens}

test("Full event handling (message_start/delta/stop)", test_event_switch)

finish(__file__)
