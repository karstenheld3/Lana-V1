"""IN21, IN48: Context management and mid-conversation features."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import client, test, finish, DEFAULT_MODEL

# IN21: Context preserved across turns
def test_multi_turn_recall():
  msgs = [
    {"role": "user", "content": "Remember: the password is BANANA"},
    {"role": "assistant", "content": "I'll remember that."},
    {"role": "user", "content": "What is the password?"},
  ]
  msg = client.messages.create(model=DEFAULT_MODEL, max_tokens=64, messages=msgs)
  return {"text": msg.content[0].text}

test("Multi-turn context recall", test_multi_turn_recall)

# IN21: Longer conversation with context
def test_long_conversation():
  msgs = [
    {"role": "user", "content": "I have 3 cats named Luna, Milo, and Oscar"},
    {"role": "assistant", "content": "Nice! Three cats: Luna, Milo, and Oscar."},
    {"role": "user", "content": "I also have a dog named Rex"},
    {"role": "assistant", "content": "And a dog named Rex. You have 4 pets total."},
    {"role": "user", "content": "List all my pets"},
  ]
  msg = client.messages.create(model=DEFAULT_MODEL, max_tokens=128, messages=msgs)
  return {"text": msg.content[0].text}

test("Long conversation context", test_long_conversation)

# IN48: Mid-conversation system-like instruction
def test_mid_conversation_shift():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=128,
    messages=[
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi there!"},
      {"role": "user", "content": "From now on, always reply in French."},
      {"role": "assistant", "content": "D'accord!"},
      {"role": "user", "content": "What is 2+2?"},
    ],
  )
  return {"text": msg.content[0].text}

test("Mid-conversation context shift (IN48)", test_mid_conversation_shift)

# IN21: Assistant prefill pattern
def test_prefill():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=128,
    messages=[
      {"role": "user", "content": "What is the capital of France? Answer in JSON."},
      {"role": "assistant", "content": '{"answer": "'},
    ],
  )
  return {"text": msg.content[0].text}

test("Assistant prefill", test_prefill)

finish(__file__)
