"""Canonical provider-neutral conversation model (LANAAGNT-IP01-IS-02)."""
import json
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class Usage(BaseModel):
  input_tokens: int = 0
  output_tokens: int = 0
  cache_read_tokens: int = 0
  cache_write_tokens: int = 0

  def add(self, other: "Usage") -> "Usage":
    return Usage(input_tokens=self.input_tokens + other.input_tokens, output_tokens=self.output_tokens + other.output_tokens,
                 cache_read_tokens=self.cache_read_tokens + other.cache_read_tokens, cache_write_tokens=self.cache_write_tokens + other.cache_write_tokens)


class ToolCall(BaseModel):
  id: str
  name: str
  args_json: str  # raw JSON string as received from the provider
  status: Literal["pending", "ok", "error", "cancelled"] = "pending"
  result: Optional[str] = None

  # Parsed arguments; raises ValueError on invalid JSON (EC-23 handled by caller)
  def args(self) -> dict[str, Any]:
    parsed = json.loads(self.args_json)
    if not isinstance(parsed, dict): raise ValueError(f"tool arguments must be a JSON object, got {type(parsed).__name__}")
    return parsed


class ThinkingBlock(BaseModel):
  provider: Literal["openai", "anthropic", "scripted"]
  payload: dict[str, Any]  # opaque provider item, resent per provider rules


class Message(BaseModel):
  role: Literal["system", "user", "assistant", "tool"]
  content: str = ""
  tool_calls: list[ToolCall] = Field(default_factory=list)
  thinking: list[ThinkingBlock] = Field(default_factory=list)
  usage: Optional[Usage] = None
  tool_call_id: Optional[str] = None  # set on role="tool" result messages
