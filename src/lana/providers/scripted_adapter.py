"""Deterministic replay adapter for LANA_SCRIPTED_ADAPTER (FR-14, IS-22).

Lives in the lana package (not tests/) so the installed `lana` executable can use it when the
env var is set - the harness spawns real subprocesses that cannot import the tests package.
Script format: JSONL, one line per Generator turn:
  {"text": str, "thinking": str?, "tool_calls": [{"name": str, "args": {}}]?, "usage": {"input": int, "output": int}?}
  {"error": str}   -> raises a simulated provider failure (deterministic exit-code-3 testing)
LANA_SCRIPTED_CAPTURE=<path>: append {"system": ..., "tools": ...} per call - the byte-identity
oracle for what the Generator actually received (FR-08 full recall, TC-65/TP01-TC-11).
"""
import json, os
from pathlib import Path
from typing import AsyncIterator
from lana.config import ResolvedRole
from lana.models import Message, ThinkingBlock, ToolCall, Usage
from lana.providers.base import AdapterDelta, ProviderError


class ScriptedAdapter:
  def __init__(self, script_path: str | Path):
    self.script_path = Path(script_path)
    if not self.script_path.exists(): raise ProviderError(f"Scripted adapter file not found: '{self.script_path}'")
    self.turns = [json.loads(line) for line in self.script_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    self.position = 0
    self.call_counter = 0

  def supports_web_search(self) -> bool:
    return False

  async def stream_turn(self, system: str, tools: list[dict], messages: list[Message], role: ResolvedRole) -> AsyncIterator[AdapterDelta]:
    capture_path = os.environ.get("LANA_SCRIPTED_CAPTURE")
    if capture_path:  # request oracle (FR-08 full recall)
      with open(capture_path, "a", encoding="utf-8", newline="\n") as capture_file:
        capture_file.write(json.dumps({"system": system, "tools": tools}, ensure_ascii=False) + "\n")
    if self.position >= len(self.turns): raise ProviderError(f"Scripted adapter exhausted after {len(self.turns)} turns (script '{self.script_path.name}')")
    turn = self.turns[self.position]
    self.position += 1
    if "error" in turn: raise ProviderError(f"Simulated provider failure: {turn['error']}")
    if turn.get("thinking"): yield AdapterDelta(kind="thinking", text=turn["thinking"], thinking=ThinkingBlock(provider="scripted", payload={"thinking": turn["thinking"]}))
    if turn.get("text"): yield AdapterDelta(kind="text", text=turn["text"])
    for requested in turn.get("tool_calls", []):
      self.call_counter += 1
      call = ToolCall(id=f"tc_{self.call_counter:03d}", name=requested["name"], args_json=json.dumps(requested.get("args", {}), ensure_ascii=False))
      yield AdapterDelta(kind="tool_call", tool_call=call)
    usage_spec = turn.get("usage", {"input": 100, "output": 10})
    yield AdapterDelta(kind="usage", usage=Usage(input_tokens=usage_spec.get("input", 0), output_tokens=usage_spec.get("output", 0), cache_read_tokens=usage_spec.get("cache_read", 0)))
