"""TK-018: scripted adapter replay (IS-22 format)."""
import asyncio
import pytest
from lana.config import ResolvedRole
from lana.providers.base import ProviderError
from lana.providers.scripted_adapter import ScriptedAdapter
from tests.scripted_adapter import write_script

ROLE = ResolvedRole(name="generator", model_id="scripted", provider="openai", method="temperature", effort="low", max_input=100000, max_output=1000)


def stream_all(adapter):
  async def consume():
    return [delta async for delta in adapter.stream_turn("sys", [], [], ROLE)]
  return asyncio.run(consume())


def test_replays_text_thinking_tool_calls_usage(tmp_path):
  script = write_script(tmp_path / "s.jsonl", [{"text": "hello", "thinking": "hmm", "tool_calls": [{"name": "read_file", "args": {"file_path": "x"}}], "usage": {"input": 42, "output": 7}}])
  deltas = stream_all(ScriptedAdapter(script))
  kinds = [delta.kind for delta in deltas]
  assert kinds == ["thinking", "text", "tool_call", "usage"]
  assert deltas[1].text == "hello"
  assert deltas[2].tool_call.name == "read_file" and deltas[2].tool_call.args() == {"file_path": "x"}
  assert deltas[3].usage.input_tokens == 42 and deltas[3].usage.output_tokens == 7


def test_error_line_raises_provider_error(tmp_path):
  script = write_script(tmp_path / "s.jsonl", [{"error": "rate limited"}])
  with pytest.raises(ProviderError) as error: stream_all(ScriptedAdapter(script))
  assert "rate limited" in str(error.value)


def test_exhausted_script_raises(tmp_path):
  script = write_script(tmp_path / "s.jsonl", [{"text": "only turn"}])
  adapter = ScriptedAdapter(script)
  stream_all(adapter)
  with pytest.raises(ProviderError) as error: stream_all(adapter)
  assert "exhausted" in str(error.value)


def test_turns_replay_in_order(tmp_path):
  script = write_script(tmp_path / "s.jsonl", [{"text": "first"}, {"text": "second"}])
  adapter = ScriptedAdapter(script)
  assert stream_all(adapter)[0].text == "first"
  assert stream_all(adapter)[0].text == "second"
