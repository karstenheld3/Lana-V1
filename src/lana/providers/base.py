"""ProviderAdapter protocol: stream_turn deltas over the canonical model (IS-11, DD-06)."""
from dataclasses import dataclass
from typing import AsyncIterator, Optional, Protocol
from lana.config import ResolvedRole
from lana.models import Message, ThinkingBlock, ToolCall, Usage


class ProviderError(Exception):
  pass


# One streamed increment from a provider: exactly one payload field set per kind
@dataclass
class AdapterDelta:
  kind: str  # text | thinking | tool_call | usage
  text: str = ""
  tool_call: Optional[ToolCall] = None
  thinking: Optional[ThinkingBlock] = None
  usage: Optional[Usage] = None


class ProviderAdapter(Protocol):
  def stream_turn(self, system: str, tools: list[dict], messages: list[Message], role: ResolvedRole) -> AsyncIterator[AdapterDelta]: ...

  def supports_web_search(self) -> bool: ...
