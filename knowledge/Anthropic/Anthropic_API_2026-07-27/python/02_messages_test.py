"""IN08: Messages API - basic, system prompt, multi-turn, parameters."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import client, test, finish, DEFAULT_MODEL

def test_basic_message():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=128,
    messages=[{"role": "user", "content": "What is 2+2? Answer with just the number."}],
  )
  return {"text": msg.content[0].text, "stop_reason": msg.stop_reason, "model": msg.model}

test("Basic message create", test_basic_message)

def test_system_string():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=128,
    system="Always respond with exactly: PONG",
    messages=[{"role": "user", "content": "PING"}],
  )
  return {"text": msg.content[0].text}

test("System prompt (string)", test_system_string)

def test_system_array():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=128,
    system=[{"type": "text", "text": "Always respond with exactly: PONG"}],
    messages=[{"role": "user", "content": "PING"}],
  )
  return {"text": msg.content[0].text}

test("System prompt (array of blocks)", test_system_array)

def test_multi_turn():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=128,
    messages=[
      {"role": "user", "content": "My name is Alice"},
      {"role": "assistant", "content": "Hello Alice!"},
      {"role": "user", "content": "What is my name?"},
    ],
  )
  return {"text": msg.content[0].text}

test("Multi-turn conversation", test_multi_turn)

def test_temperature():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=64,
    temperature=0.0,
    messages=[{"role": "user", "content": "Reply with: OK"}],
  )
  return {"text": msg.content[0].text}

test("Temperature parameter (0.0)", test_temperature)

def test_stop_sequences():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=256,
    stop_sequences=["END"],
    messages=[{"role": "user", "content": "Count 1-5, then write END"}],
  )
  return {"text": msg.content[0].text, "stop_reason": msg.stop_reason}

test("Stop sequences", test_stop_sequences)

def test_metadata():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=64,
    metadata={"user_id": "test-user-123"},
    messages=[{"role": "user", "content": "Reply with: OK"}],
  )
  return {"text": msg.content[0].text}

test("Metadata (user_id)", test_metadata)

def test_top_k():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=64,
    top_k=5,
    messages=[{"role": "user", "content": "Reply with: OK"}],
  )
  return {"text": msg.content[0].text}

test("top_k parameter", test_top_k)

finish(__file__)
