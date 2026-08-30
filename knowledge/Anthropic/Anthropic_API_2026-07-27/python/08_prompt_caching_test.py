"""IN20, IN42: Prompt caching - auto, explicit, TTL, cache diagnostics."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import client, test, finish, DEFAULT_MODEL

# Padding to exceed min cacheable prefix size
PADDING = "x" * 2048

def test_auto_cache():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=64,
    cache_control={"type": "ephemeral"},
    system="You are a helpful assistant. " + PADDING,
    messages=[{"role": "user", "content": "Reply with: OK"}],
  )
  return {
    "cache_creation": msg.usage.cache_creation_input_tokens,
    "cache_read": msg.usage.cache_read_input_tokens,
  }

test("Automatic caching (cache_control top-level)", test_auto_cache)

def test_explicit_cache():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=64,
    system=[{
      "type": "text",
      "text": "You are an expert assistant. " + PADDING,
      "cache_control": {"type": "ephemeral"},
    }],
    messages=[{"role": "user", "content": "Reply with: OK"}],
  )
  return {
    "cache_creation": msg.usage.cache_creation_input_tokens,
    "cache_read": msg.usage.cache_read_input_tokens,
  }

test("Explicit cache breakpoint on system block", test_explicit_cache)

def test_1h_ttl():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=64,
    system=[{
      "type": "text",
      "text": "Large shared context. " + PADDING,
      "cache_control": {"type": "ephemeral", "ttl": "1h"},
    }],
    messages=[{"role": "user", "content": "Reply with: OK"}],
  )
  return {"cache_creation": msg.usage.cache_creation_input_tokens}

test("1-hour TTL cache", test_1h_ttl)

# IN20: Multi-turn with automatic caching extends cache
def test_multi_turn_cache():
  messages = [
    {"role": "user", "content": "What is quantum entanglement?"},
    {"role": "assistant", "content": "Quantum entanglement is a phenomenon..."},
    {"role": "user", "content": "How is it used in quantum computing?"},
  ]
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=128,
    cache_control={"type": "ephemeral"},
    system="You are a physics expert. " + PADDING,
    messages=messages,
  )
  return {
    "cache_creation": msg.usage.cache_creation_input_tokens,
    "cache_read": msg.usage.cache_read_input_tokens,
    "input_tokens": msg.usage.input_tokens,
  }

test("Multi-turn with automatic cache extension", test_multi_turn_cache)

# IN42: Verify usage fields for cache tracking
def test_cache_diagnostics():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=64,
    cache_control={"type": "ephemeral"},
    system="Cache diagnostic test. " + PADDING,
    messages=[{"role": "user", "content": "Reply: OK"}],
  )
  usage = msg.usage
  return {
    "input_tokens": usage.input_tokens,
    "output_tokens": usage.output_tokens,
    "cache_creation": usage.cache_creation_input_tokens,
    "cache_read": usage.cache_read_input_tokens,
  }

test("Cache diagnostic usage fields (IN42)", test_cache_diagnostics)

finish(__file__)
