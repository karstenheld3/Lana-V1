"""AgentEvent union - the 11 event types from LANAAGNT-SP01 Domain Objects plus prompt_step (LANAACPB-FR-12), JSONL serialization (IS-02, IS-24)."""
import datetime, json
from typing import Annotated, Any, Literal, Optional, Union
from pydantic import BaseModel, Field, TypeAdapter


def now_ts() -> str:
  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class EventBase(BaseModel):
  ts: str = Field(default_factory=now_ts)

  def to_jsonl(self) -> str:
    return json.dumps(self.model_dump(exclude_none=True), ensure_ascii=False, separators=(",", ":"))


# Full-recall environment record - FIRST line of every session file (FR-08, IG-07)
class SessionStarted(EventBase):
  type: Literal["session_started"] = "session_started"
  system_prompt: str
  tool_definitions: list[dict[str, Any]] = Field(default_factory=list)
  config_snapshot: dict[str, Any] = Field(default_factory=dict)
  prompt_system_fingerprint: dict[str, Any] = Field(default_factory=dict)


class UserMessage(EventBase):
  type: Literal["user_message"] = "user_message"
  content: str
  expanded_workflow: Optional[str] = None


class TurnStarted(EventBase):
  type: Literal["turn_started"] = "turn_started"
  role: str = "generator"


class TextDelta(EventBase):
  type: Literal["text_delta"] = "text_delta"
  text: str


class ThinkingDelta(EventBase):
  type: Literal["thinking_delta"] = "thinking_delta"
  text: str


class ToolCallRequested(EventBase):
  type: Literal["tool_call_requested"] = "tool_call_requested"
  id: str
  tool: str
  args: dict[str, Any] = Field(default_factory=dict)
  args_json: Optional[str] = None  # raw string kept when args JSON is invalid (EC-23)


class ToolCallFinished(EventBase):
  type: Literal["tool_call_finished"] = "tool_call_finished"
  id: str
  status: Literal["ok", "error", "cancelled"]
  result: str = ""  # full result text - required for resume projection (IG-02)
  result_chars: int = 0


class ApprovalRequired(EventBase):
  type: Literal["approval_required"] = "approval_required"
  action: str  # run_command | write_outside_workspace | read_url_content
  detail: str  # exact command line + cwd, or path/URL
  approved: Optional[bool] = None  # recorded resolution


class CheckpointCreated(EventBase):
  type: Literal["checkpoint_created"] = "checkpoint_created"
  text: str  # full checkpoint text (resume replay requirement)
  truncated_messages: int = 0
  kept_messages: int = 0  # tail messages kept after the checkpoint (resume projection)


class TurnFinished(EventBase):
  type: Literal["turn_finished"] = "turn_finished"
  role: str = "generator"
  input_tokens: int = 0
  output_tokens: int = 0
  cache_read_tokens: int = 0
  cost_usd: Optional[float] = None  # None when model missing from pricing (EC-24)
  thinking_payloads: Optional[list[dict[str, Any]]] = None  # the turn's resendable thinking blocks [{provider, payload}] (FR-08 full recall)


class ErrorEvent(EventBase):
  type: Literal["error"] = "error"
  message: str


# Prompt queue boundary - one per queue entry, headless-only (LANAACPB-FR-12)
class PromptStep(EventBase):
  type: Literal["prompt_step"] = "prompt_step"
  index: int  # 1-based queue position
  total: int
  digest: str = ""  # first 12 hex chars of SHA-256 over the prompt text


AgentEvent = Annotated[Union[SessionStarted, UserMessage, TurnStarted, TextDelta, ThinkingDelta, ToolCallRequested, ToolCallFinished, ApprovalRequired, CheckpointCreated, TurnFinished, ErrorEvent, PromptStep], Field(discriminator="type")]
EVENT_ADAPTER: TypeAdapter = TypeAdapter(AgentEvent)


def from_jsonl(line: str):
  return EVENT_ADAPTER.validate_json(line)
