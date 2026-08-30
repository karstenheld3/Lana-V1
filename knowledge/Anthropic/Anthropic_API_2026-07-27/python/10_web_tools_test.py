"""IN24: Server-side web tools (web_search, web_fetch)."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import client, test, finish, DEFAULT_MODEL

def test_web_search():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=2048,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{"role": "user", "content": "What is the current population of Tokyo?"}],
  )
  content_types = [b.type for b in msg.content]
  return {"stop_reason": msg.stop_reason, "content_types": content_types}

test("Web search tool (server-side)", test_web_search)

def test_web_search_with_user_location():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=2048,
    tools=[{
      "type": "web_search_20250305",
      "name": "web_search",
      "user_location": {"type": "approximate", "city": "London", "country": "GB"},
    }],
    messages=[{"role": "user", "content": "What's the weather like today?"}],
  )
  content_types = [b.type for b in msg.content]
  return {"stop_reason": msg.stop_reason, "content_types": content_types}

test("Web search with user_location", test_web_search_with_user_location)

def test_web_search_disabled_sources():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=2048,
    tools=[{
      "type": "web_search_20250305",
      "name": "web_search",
      "blocked_domains": ["wikipedia.org"],
    }],
    messages=[{"role": "user", "content": "What is quantum computing?"}],
  )
  content_types = [b.type for b in msg.content]
  return {"stop_reason": msg.stop_reason, "content_types": content_types}

test("Web search with blocked_domains", test_web_search_disabled_sources)

finish(__file__)
