"""IN10: Token counting endpoint."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import client, test, finish, DEFAULT_MODEL

def test_basic_count():
  result = client.messages.count_tokens(
    model=DEFAULT_MODEL,
    messages=[{"role": "user", "content": "What is the meaning of life?"}],
  )
  return {"input_tokens": result.input_tokens}

test("Basic token count", test_basic_count)

def test_with_system():
  result = client.messages.count_tokens(
    model=DEFAULT_MODEL,
    system="You are a helpful weather assistant.",
    messages=[{"role": "user", "content": "What's the weather?"}],
  )
  return {"input_tokens": result.input_tokens}

test("Token count with system prompt", test_with_system)

def test_with_tools():
  result = client.messages.count_tokens(
    model=DEFAULT_MODEL,
    system="You are a helpful weather assistant.",
    tools=[{
      "name": "get_weather",
      "description": "Get weather for a location.",
      "input_schema": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]},
    }],
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
  )
  return {"input_tokens": result.input_tokens}

test("Token count with tools", test_with_tools)

def test_with_thinking():
  result = client.messages.count_tokens(
    model=DEFAULT_MODEL,
    thinking={"type": "enabled", "budget_tokens": 4000},
    messages=[{"role": "user", "content": "Hello"}],
  )
  return {"input_tokens": result.input_tokens}

test("Token count with thinking config", test_with_thinking)

# IN14 pattern: count tokens -> estimate cost
def test_cost_estimation():
  INPUT_COST_PER_MTOK = 3.00
  count = client.messages.count_tokens(
    model=DEFAULT_MODEL,
    messages=[{"role": "user", "content": "Write a comprehensive analysis of AI"}],
  )
  estimated_cost = (count.input_tokens / 1_000_000) * INPUT_COST_PER_MTOK
  return {"tokens": count.input_tokens, "estimated_cost_usd": f"${estimated_cost:.6f}"}

test("Cost estimation pattern (IN14)", test_cost_estimation)

finish(__file__)
