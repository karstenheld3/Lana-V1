"""ProviderAdapter protocol: stream_turn deltas over the canonical model (IS-11, DD-06).

FR-16 BL-05/UX-03: SDK clients get explicit timeouts and zero SDK-internal retries - Lana owns
up to RETRY_MAX visible retries on retryable failures occurring before the first streamed delta.
"""
from dataclasses import dataclass
from typing import AsyncIterator, Optional, Protocol
try:
  import httpx2 as httpx  # openai>=3 / anthropic>=1 migrated to httpx2 - Timeout must be THEIR variant (intentionally undeclared: always arrives with the SDKs)
except ModuleNotFoundError:
  import httpx
from lana.config import ResolvedRole
from lana.models import Message, ThinkingBlock, ToolCall, Usage

PROVIDER_TIMEOUT = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0)  # FR-16 BL-05
RETRYABLE_STATUS = (408, 429, 500, 502, 503, 504)
RETRY_DELAYS_SECONDS = (2.0, 8.0)  # FR-16 UX-03: up to 2 Lana-owned retries, each announced


class ProviderError(Exception):
  pass


# Retryable = transient transport/status failures; anything else (auth, invalid request) fails immediately
def is_retryable_error(error: Exception) -> bool:
  status = getattr(error, "status_code", None)
  if status is not None: return status in RETRYABLE_STATUS
  return type(error).__name__ in ("APIConnectionError", "APITimeoutError")


# One streamed increment from a provider: exactly one payload field set per kind
@dataclass
class AdapterDelta:
  kind: str  # text | thinking | tool_call | usage | notice
  text: str = ""
  tool_call: Optional[ToolCall] = None
  thinking: Optional[ThinkingBlock] = None
  usage: Optional[Usage] = None


class ProviderAdapter(Protocol):
  def stream_turn(self, system: str, tools: list[dict], messages: list[Message], role: ResolvedRole) -> AsyncIterator[AdapterDelta]: ...

  def supports_web_search(self) -> bool: ...
