"""TK-016/017: provider adapters - offline mapping units + live smokes (IP01 TC-40..42, marked live)."""
import asyncio, json, os
import pytest
from lana.config import ResolvedRole, load_lana_config
from lana.models import Message, ThinkingBlock, ToolCall, Usage
from lana.providers import openai_adapter, anthropic_adapter

OPENAI_ROLE = ResolvedRole(name="generator", model_id="gpt-4.1-mini", provider="openai", method="temperature", effort="low", max_input=1047576, max_output=1024, params={"temperature": 0.4})
OPENAI_REASONING_ROLE = ResolvedRole(name="generator", model_id="gpt-5.5", provider="openai", method="reasoning_effort", effort="medium", max_input=1050000, max_output=2048, params={"reasoning_effort": "medium"})
ANTHROPIC_ROLE = ResolvedRole(name="generator", model_id="claude-sonnet-4-5-20250929", provider="anthropic", method="thinking", effort="medium", max_input=200000, max_output=2048, params={"thinking_budget": 4096})

CONVERSATION = [
  Message(role="user", content="read the notes"),
  Message(role="assistant", content="Reading now.", tool_calls=[ToolCall(id="call_1", name="read_file", args_json='{"file_path": "notes.md"}', status="ok", result="body")],
          thinking=[ThinkingBlock(provider="openai", payload={"type": "reasoning", "id": "rs_1", "summary": []}), ThinkingBlock(provider="anthropic", payload={"type": "thinking", "thinking": "hmm", "signature": "sig1"})]),
  Message(role="tool", content="file body here", tool_call_id="call_1"),
  Message(role="tool", content="second result", tool_call_id="call_2"),
]

TOOLS = [{"name": "read_file", "description": "Reads a file", "schema": {"type": "object", "additionalProperties": False, "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}]


# ----------------------------------------- START: Offline mapping units ------------------------------------------------------

def test_openai_input_items_mapping():
  items = openai_adapter.build_input_items(CONVERSATION)
  types = [item.get("type") or item.get("role") for item in items]
  assert types == ["user", "reasoning", "assistant", "function_call", "function_call_output", "function_call_output"]
  function_call = items[3]
  assert function_call["call_id"] == "call_1" and function_call["arguments"] == '{"file_path": "notes.md"}'
  assert items[1]["id"] == "rs_1"  # openai reasoning item resent verbatim; anthropic thinking excluded


def test_openai_request_params():
  assert openai_adapter.build_request_params(OPENAI_ROLE) == {"max_output_tokens": 1024, "temperature": 0.4}
  reasoning_params = openai_adapter.build_request_params(OPENAI_REASONING_ROLE)
  assert reasoning_params["reasoning"] == {"effort": "medium"} and "temperature" not in reasoning_params
  assert reasoning_params["include"] == ["reasoning.encrypted_content"]


def test_openai_tools_shape():
  tools = openai_adapter.build_tools(TOOLS)
  assert tools[0]["type"] == "function" and tools[0]["name"] == "read_file" and tools[0]["parameters"]["required"] == ["file_path"]


def test_anthropic_messages_mapping():
  messages = anthropic_adapter.build_messages(CONVERSATION)
  assert [message["role"] for message in messages] == ["user", "assistant", "user"]
  assistant_blocks = messages[1]["content"]
  assert assistant_blocks[0]["type"] == "thinking" and assistant_blocks[0]["signature"] == "sig1"  # anthropic thinking resent, openai excluded
  assert assistant_blocks[1] == {"type": "text", "text": "Reading now."}
  assert assistant_blocks[2]["type"] == "tool_use" and assistant_blocks[2]["input"] == {"file_path": "notes.md"}
  tool_results = messages[2]["content"]
  assert len(tool_results) == 2 and all(block["type"] == "tool_result" for block in tool_results)  # consecutive results merged


def test_anthropic_tools_cache_breakpoint():
  tools = anthropic_adapter.build_tools(TOOLS + [{"name": "list_dir", "description": "d", "schema": {"type": "object", "additionalProperties": False, "properties": {}, "required": []}}])
  assert "cache_control" not in tools[0] and tools[-1]["cache_control"] == {"type": "ephemeral"}


def test_anthropic_request_params_thinking_budget():
  params = anthropic_adapter.build_request_params(ANTHROPIC_ROLE)
  assert params["thinking"] == {"type": "enabled", "budget_tokens": 4096}
  assert params["max_tokens"] >= 4096 + 2048
  assert params["extra_body"]["cache_control"] == {"type": "ephemeral"}  # automatic caching (FR-06)
  tiny = ResolvedRole(name="g", model_id="claude-sonnet-4-5-20250929", provider="anthropic", method="thinking", effort="none", max_input=200000, max_output=2048, params={"thinking_budget": 0})
  assert "thinking" not in anthropic_adapter.build_request_params(tiny)  # budget below 1024 -> disabled


def test_anthropic_usage_normalization():
  class FakeUsage: input_tokens = 2850; output_tokens = 412; cache_read_input_tokens = 18200; cache_creation_input_tokens = 100
  usage = anthropic_adapter.normalize_usage(FakeUsage())
  assert usage.input_tokens == 2850 + 18200 + 100  # normalized to include cache reads (cost.py contract)
  assert usage.cache_read_tokens == 18200 and usage.cache_write_tokens == 100


def test_openai_usage_normalization():
  class FakeDetails: cached_tokens = 100
  class FakeUsage: input_tokens = 150; output_tokens = 1200; input_tokens_details = FakeDetails()
  usage = openai_adapter.normalize_usage(FakeUsage())
  assert usage.input_tokens == 150 and usage.cache_read_tokens == 100

# ----------------------------------------- END: Offline mapping units --------------------------------------------------------


# ----------------------------------------- START: Live smokes (TC-40..42, keys required) --------------------------------------

def live_app(tmp_path):
  from tests.conftest import write_config_dir
  write_config_dir(tmp_path, key_lines=None)  # keys must come from real env
  return load_lana_config(tmp_path)


def run_turn(adapter, role, messages, tools=TOOLS):
  async def consume():
    return [delta async for delta in adapter.stream_turn("You are a test agent. Use the read_file tool once, then answer DONE.", tools, messages, role)]
  return asyncio.run(consume())


@pytest.mark.live
def test_tc40_openai_function_round_trip(tmp_path):
  if not os.environ.get("OPENAI_API_KEY"): pytest.skip("OPENAI_API_KEY not set")
  adapter = openai_adapter.OpenAIAdapter(api_key=os.environ["OPENAI_API_KEY"])
  deltas = run_turn(adapter, OPENAI_ROLE, [Message(role="user", content="Read the file 'notes.md' using the read_file tool.")])
  tool_calls = [delta for delta in deltas if delta.kind == "tool_call"]
  assert tool_calls and tool_calls[0].tool_call.name == "read_file"
  followup = [
    Message(role="user", content="Read the file 'notes.md' using the read_file tool."),
    Message(role="assistant", content="", tool_calls=[tool_calls[0].tool_call], thinking=[delta.thinking for delta in deltas if delta.kind == "thinking" and delta.thinking]),
    Message(role="tool", content="notes body: all fine", tool_call_id=tool_calls[0].tool_call.id),
  ]
  final = run_turn(adapter, OPENAI_ROLE, followup)
  assert any(delta.kind == "text" for delta in final)
  assert any(delta.kind == "usage" and delta.usage.input_tokens > 0 for delta in final)


@pytest.mark.live
def test_tc41_anthropic_round_trip_and_cache(tmp_path):
  if not os.environ.get("ANTHROPIC_API_KEY"): pytest.skip("ANTHROPIC_API_KEY not set")
  adapter = anthropic_adapter.AnthropicAdapter(api_key=os.environ["ANTHROPIC_API_KEY"])
  big_system_tools = TOOLS + [{"name": f"filler_tool_{index}", "description": "Filler tool for cache minimum size. " * 40, "schema": {"type": "object", "additionalProperties": False, "properties": {"x": {"type": "string"}}, "required": ["x"]}} for index in range(6)]
  first_messages = [Message(role="user", content="Read the file 'notes.md' using the read_file tool.")]
  deltas = run_turn(adapter, ANTHROPIC_ROLE, first_messages, tools=big_system_tools)
  tool_calls = [delta for delta in deltas if delta.kind == "tool_call"]
  assert tool_calls and tool_calls[0].tool_call.name == "read_file"
  followup = first_messages + [
    Message(role="assistant", content="", tool_calls=[tool_calls[0].tool_call], thinking=[delta.thinking for delta in deltas if delta.kind == "thinking" and delta.thinking]),
    Message(role="tool", content="notes body: all fine", tool_call_id=tool_calls[0].tool_call.id),
  ]
  final = run_turn(adapter, ANTHROPIC_ROLE, followup, tools=big_system_tools)
  usage = [delta for delta in final if delta.kind == "usage"][0].usage
  assert usage.cache_read_tokens > 0, f"expected cache hit on call 2, usage: {usage}"  # NFR-03


@pytest.mark.live
def test_anthropic_web_search_branch(tmp_path):
  if not os.environ.get("ANTHROPIC_API_KEY"): pytest.skip("ANTHROPIC_API_KEY not set")
  adapter = anthropic_adapter.AnthropicAdapter(api_key=os.environ["ANTHROPIC_API_KEY"])
  role = ResolvedRole(name="websearch", model_id="claude-haiku-4-5-20251001", provider="anthropic", method="thinking", effort="low", max_input=200000, max_output=2048, params={"thinking_budget": 0})
  results = adapter.run_web_search("Python programming language official documentation", None, role)
  assert results and any(result.get("url", "").startswith("http") for result in results)  # BG-0003 regression: request accepted, results parsed


@pytest.mark.live
def test_tc42_openai_reasoning_model_tool_call(tmp_path):
  if not os.environ.get("OPENAI_API_KEY"): pytest.skip("OPENAI_API_KEY not set")
  adapter = openai_adapter.OpenAIAdapter(api_key=os.environ["OPENAI_API_KEY"])
  role = ResolvedRole(name="generator", model_id="gpt-5-mini", provider="openai", method="reasoning_effort", effort="medium", max_input=256000, max_output=4096, params={"reasoning_effort": "medium"})
  deltas = run_turn(adapter, role, [Message(role="user", content="Read the file 'notes.md' using the read_file tool.")])
  assert any(delta.kind == "tool_call" and delta.tool_call.name == "read_file" for delta in deltas)  # RF-01 regression

# ----------------------------------------- END: Live smokes -------------------------------------------------------------------
