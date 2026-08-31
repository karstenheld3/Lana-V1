"""Session store: append-only flushed JSONL + resume projection (LANAAGNT-FR-08, IS-14).

Every event line is flushed at write time - external processes tail the session file as a
live activity monitor (test harness contract, DD-20). The event log is the single source of
truth; conversation state is a projection of it (Key Mechanisms: event-sourced session).
"""
import datetime, json, uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from lana.events import from_jsonl
from lana.models import Message, ThinkingBlock, ToolCall, Usage

CANCELLATION_NOTE_PREFIX = "turn cancelled after"


class SessionStore:
  def __init__(self, path: Path):
    self.path = path
    self.path.parent.mkdir(parents=True, exist_ok=True)
    self.file = open(self.path, "a", encoding="utf-8", newline="\n")

  @staticmethod
  def create(data_dir: Path) -> "SessionStore":
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return SessionStore(data_dir / "sessions" / f"{stamp}_{uuid.uuid4().hex[:6]}.jsonl")

  # Append + flush per line (FR-08 flush contract, IG-02)
  def append(self, event) -> None:
    self.file.write(event.to_jsonl() + "\n")
    self.file.flush()

  def close(self) -> None:
    self.file.close()


@dataclass
class ResumedState:
  messages: list[Message] = field(default_factory=list)
  events: list = field(default_factory=list)
  todo_state: Optional[list[dict]] = None
  usage_by_role: dict[str, Usage] = field(default_factory=dict)
  cost_by_role: dict[str, float] = field(default_factory=dict)
  turns_by_role: dict[str, int] = field(default_factory=dict)
  skipped_lines: int = 0
  # Full-recall environment from session_started (FR-08, IS-24); all None on legacy files (EC-28)
  system_prompt: Optional[str] = None
  tool_definitions: Optional[list[dict]] = None
  config_snapshot: Optional[dict] = None
  prompt_system_fingerprint: Optional[dict] = None


# ----------------------------------------- START: Resume Projection ----------------------------------------------------------

class _Projector:
  """Replays events into canonical messages (IS-14). One assistant message per turn_started..turn_finished span."""

  def __init__(self):
    self.messages: list[Message] = []
    self.text_parts: list[str] = []
    self.tool_calls: list[ToolCall] = []
    self.results: list[Message] = []
    self.in_turn = False
    self.cancelled_call_count = 0

  def flush_assistant(self, usage: Optional[Usage] = None, thinking: Optional[list[ThinkingBlock]] = None) -> None:
    if self.text_parts or self.tool_calls:
      self.messages.append(Message(role="assistant", content="".join(self.text_parts), tool_calls=self.tool_calls, thinking=thinking or [], usage=usage))
      self.messages.extend(self.results)
    self.text_parts, self.tool_calls, self.results = [], [], []

  def apply(self, event) -> None:
    kind = event.type
    if kind == "user_message":
      self.flush_assistant()
      self.messages.append(Message(role="user", content=event.content))
      self.in_turn = False
    elif kind == "turn_started":
      self.flush_assistant()
      self.in_turn = True
    elif kind == "text_delta": self.text_parts.append(event.text)
    elif kind == "tool_call_requested":
      self.tool_calls.append(ToolCall(id=event.id, name=event.tool, args_json=json.dumps(event.args, ensure_ascii=False), status="pending"))
    elif kind == "tool_call_finished":
      for call in self.tool_calls:
        if call.id == event.id: call.status = event.status; call.result = event.result
      self.results.append(Message(role="tool", content=event.result, tool_call_id=event.id))
    elif kind == "turn_finished":
      usage = Usage(input_tokens=event.input_tokens, output_tokens=event.output_tokens, cache_read_tokens=event.cache_read_tokens)
      thinking = [ThinkingBlock(provider=item["provider"], payload=item["payload"]) for item in (event.thinking_payloads or [])]  # FR-08 full recall
      self.flush_assistant(usage, thinking)
      self.in_turn = False
    elif kind == "checkpoint_created":
      self.flush_assistant()
      kept = self.messages[len(self.messages) - event.kept_messages:] if event.kept_messages else []
      self.messages = [Message(role="user", content=event.text)] + kept
    elif kind == "error" and event.message.startswith(CANCELLATION_NOTE_PREFIX):
      completed = [call for call in self.tool_calls if call.status in ("ok", "error")]
      self.cancelled_call_count = len(completed)
      # BG-0001: synthesize tool_results for orphaned tool_use IDs (provider APIs require 1:1 match)
      result_ids = {msg.tool_call_id for msg in self.results}
      for call in self.tool_calls:
        if call.id not in result_ids:
          call.status = "cancelled"
          self.results.append(Message(role="tool", content="Tool execution cancelled.", tool_call_id=call.id))
      self.flush_assistant()  # keep completed calls + synthetic results (EC-10, BG-0001)
      self.messages.append(Message(role="user", content=f"<cancellation_note>{event.message}</cancellation_note>"))
      self.in_turn = False


def resume(path: Path) -> ResumedState:
  """Rebuild conversation state from a session JSONL file; corrupt lines skipped with count (EC-21, IG-06)."""
  state = ResumedState()
  projector = _Projector()
  for line in Path(path).read_text(encoding="utf-8").splitlines():
    if not line.strip(): continue
    try:
      event = from_jsonl(line)
    except Exception:
      state.skipped_lines += 1
      continue
    state.events.append(event)
    projector.apply(event)
    if event.type == "session_started":  # full-recall environment record (FR-08, IS-24)
      state.system_prompt = event.system_prompt
      state.tool_definitions = event.tool_definitions
      state.config_snapshot = event.config_snapshot
      state.prompt_system_fingerprint = event.prompt_system_fingerprint
    if event.type == "tool_call_finished" and event.result.startswith("Todo list updated:"):
      try:
        state.todo_state = json.loads(event.result.split("Todo list updated:\n", 1)[1])
      except (IndexError, json.JSONDecodeError):
        pass
    if event.type == "turn_finished":
      usage = state.usage_by_role.setdefault(event.role, Usage())
      state.usage_by_role[event.role] = usage.add(Usage(input_tokens=event.input_tokens, output_tokens=event.output_tokens, cache_read_tokens=event.cache_read_tokens))
      state.turns_by_role[event.role] = state.turns_by_role.get(event.role, 0) + 1
      if event.cost_usd is not None: state.cost_by_role[event.role] = state.cost_by_role.get(event.role, 0.0) + event.cost_usd
  projector.flush_assistant()
  state.messages = projector.messages
  return state

# ----------------------------------------- END: Resume Projection ------------------------------------------------------------
