"""Agent turn loop: slash expansion, sequential tool dispatch through safety, limits, cancellation (LANAAGNT-FR-04/05, IS-13).

The loop is a pure async generator over AgentEvents - frontends only consume events (DD-06).
Every event is appended to the session JSONL at occurrence, user events before the turn starts (IG-02).
Per-turn variability (date, cwd) lives in the user message metadata block, never in the system prompt (IG-01).
"""
import datetime, difflib
from typing import AsyncIterator, Callable, Optional
from lana.config import AppConfig
from lana.events import ApprovalRequired, ErrorEvent, TextDelta, ThinkingDelta, ToolCallFinished, ToolCallRequested, TurnFinished, TurnStarted, UserMessage
from lana.loader import PromptSystem
from lana.models import Message, ToolCall
from lana.providers import get_adapter
from lana.safety import classify, write_needs_approval
from lana.session import SessionStore
from lana.tools import ToolContext, ToolError, ToolRegistry

APPROVAL_DENIED_NON_INTERACTIVE = "approval denied (non-interactive session)"
APPROVAL_DENIED_BY_USER = "approval denied by user"
WRITE_TOOLS = ("edit", "multi_edit", "write_to_file")
CONTEXT_OVERFLOW_MARKERS = ("context_length_exceeded", "maximum context length", "prompt is too long", "too many tokens", "context window", "input length exceeds")


# Provider 400 "too long" detection (EC-20) - message-based, both providers covered
def is_context_overflow(error_text: str) -> bool:
  lowered = error_text.casefold()
  return any(marker in lowered for marker in CONTEXT_OVERFLOW_MARKERS)


class UnknownWorkflowError(Exception):
  def __init__(self, name: str, suggestions: list[str]):
    self.name, self.suggestions = name, suggestions
    hint = f" Closest matches: {', '.join('/' + item for item in suggestions)}" if suggestions else ""
    super().__init__(f"Unknown workflow '/{name}'.{hint}")


# Expand /name input into the Cascade user message format (FR-05, OQ-22); returns (content, workflow_name)
def expand_slash_command(user_input: str, prompt_system: PromptSystem) -> tuple[str, Optional[str]]:
  stripped = user_input.strip()
  if not stripped.startswith("/"): return user_input, None
  name = stripped.split()[0][1:]
  workflow = prompt_system.find_workflow(name)
  if workflow is None:
    names = [item.name for item in prompt_system.workflows]
    prefixed = [candidate for candidate in names if candidate.startswith(name)]
    suggestions = (prefixed + [item for item in difflib.get_close_matches(name, names, n=3) if item not in prefixed])[:3]
    raise UnknownWorkflowError(name, suggestions)
  content = (f"<user_request>\n{stripped}\n</user_request>\n<workflows>\n@[/{workflow.name}] is a [Workflow]:\n<workflow>\n"
             f"The user mentioned the ({workflow.name}) workflow. Here are its contents:\n{workflow.content}\n</workflow>\n</workflows>")
  return content, workflow.name


class Agent:
  def __init__(self, app: AppConfig, prompt_system: PromptSystem, system_prompt: str, registry: ToolRegistry, tool_context: ToolContext, session: SessionStore,
               messages: Optional[list[Message]] = None, approve_callback: Optional[Callable[[str, str], bool]] = None,
               continue_callback: Optional[Callable[[int], bool]] = None, cost_fn: Optional[Callable] = None, compactor: Optional[Callable] = None,
               tool_definitions: Optional[list[dict]] = None):
    self.app = app
    self.prompt_system = prompt_system
    self.system_prompt = system_prompt
    self.registry = registry
    self.tool_context = tool_context
    self.session = session
    self.messages: list[Message] = messages or []
    self.approve_callback = approve_callback    # (action, detail) -> bool; None = non-interactive auto-deny (FR-14)
    self.continue_callback = continue_callback  # (calls_done) -> bool; None = stop at limit (EC-11)
    self.cost_fn = cost_fn                      # (role_name, usage) -> float | None (FR-09; EC-24 -> None)
    self.compactor = compactor                  # post-turn compaction hook (FR-07, wired in Phase G)
    self.tool_definitions = tool_definitions    # recorded definitions override on resume (FR-08 full recall, IS-24)
    self.stop_reason: Optional[str] = None      # None | "limit" | "cancelled" | "provider_error"
    self.current_turn_completed_calls = 0
    self.final_text = ""

  def emit(self, event):
    self.session.append(event)
    return event

  # Metadata block: per-turn variability lives HERE, not in the system prompt (IG-01)
  def build_user_message(self, content: str) -> Message:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    metadata = f"<user_metadata>\ndate: {now}\ncwd: {self.tool_context.workspace}\n</user_metadata>"
    return Message(role="user", content=f"{content}\n\n{metadata}")

  # Approval gate (FR-12/13): returns (needs_approval, action, detail)
  def approval_needed(self, call: ToolCall, args: dict) -> tuple[bool, str, str]:
    if call.name == "run_command":
      decision = classify(args.get("CommandLine", ""), self.app.lana.execution_policy, self.app.lana.command_denylist, args.get("SafeToAutoRun", False))
      detail = f"{args.get('CommandLine', '')} (cwd: {args.get('Cwd') or self.tool_context.workspace})"
      return decision.action == "ASK", "run_command", detail
    if call.name in WRITE_TOOLS:
      target = args.get("file_path") or args.get("TargetFile") or ""
      if target and write_needs_approval(target, self.tool_context.workspace): return True, "write_outside_workspace", str(target)
      return False, "", ""
    if call.name == "read_url_content": return True, "read_url_content", args.get("Url", "")  # Cascade parity: always approved interactively
    return False, "", ""

  # Resolve the approval gate; returns the ApprovalRequired event to yield (or None) and applies denial to the call (BG-0001)
  def resolve_approval(self, call: ToolCall, args: dict) -> Optional[ApprovalRequired]:
    needs_approval, action, detail = self.approval_needed(call, args)
    if not needs_approval: return None
    approved = self.approve_callback(action, detail) if self.approve_callback else False
    if not approved:
      call.status = "error"
      call.result = APPROVAL_DENIED_BY_USER if self.approve_callback else APPROVAL_DENIED_NON_INTERACTIVE
    return ApprovalRequired(action=action, detail=detail, approved=approved)

  def dispatch_call(self, call: ToolCall, args: dict) -> ToolCall:
    try:
      call.result = self.registry.dispatch(call.name, args, self.tool_context)
      call.status = "ok"
    except ToolError as error:
      call.status, call.result = "error", str(error)
    except Exception as error:  # executor crash must not kill the loop (EC-22 spirit)
      call.status, call.result = "error", f"Tool execution failed: {type(error).__name__}: {error}"
    return call

  async def run_prompt(self, user_input: str) -> AsyncIterator:
    """One user message -> Generator/tool loop until no tool calls, limit, cancellation, or provider error (FR-04)."""
    self.stop_reason = None
    self.current_turn_completed_calls = 0
    self.final_text = ""
    content, workflow_name = expand_slash_command(user_input, self.prompt_system)  # UnknownWorkflowError propagates (EC-05)
    yield self.emit(UserMessage(content=user_input, expanded_workflow=workflow_name))
    self.messages.append(self.build_user_message(content))
    role = self.app.roles["generator"]
    adapter = get_adapter(role, self.app)
    calls_this_prompt = 0
    while True:
      yield self.emit(TurnStarted(role="generator"))
      text_parts, thinking_blocks, tool_calls, usage = [], [], [], None
      try:
        async for delta in adapter.stream_turn(self.system_prompt, self.tool_definitions or self.registry.definition_list(), self.messages, role):
          if delta.kind == "text": text_parts.append(delta.text); yield self.emit(TextDelta(text=delta.text))
          elif delta.kind == "thinking":
            if delta.thinking: thinking_blocks.append(delta.thinking)
            yield self.emit(ThinkingDelta(text=delta.text))
          elif delta.kind == "tool_call": tool_calls.append(delta.tool_call)
          elif delta.kind == "usage": usage = delta.usage
      except Exception as error:
        self.stop_reason = "provider_error"
        message = f"Provider error: {error}"
        if is_context_overflow(str(error)): message += " - the conversation exceeds the model's context window. Switch the generator to a larger-window model or start a new session; the request was not retried (EC-20)."
        yield self.emit(ErrorEvent(message=message))
        return
      assistant = Message(role="assistant", content="".join(text_parts), tool_calls=tool_calls, thinking=thinking_blocks, usage=usage)
      self.messages.append(assistant)
      self.final_text = assistant.content or self.final_text
      cost = self.cost_fn("generator", usage) if (self.cost_fn and usage) else None
      payloads = [{"provider": block.provider, "payload": block.payload} for block in thinking_blocks] or None  # FR-08 full recall
      finished = TurnFinished(role="generator", input_tokens=usage.input_tokens if usage else 0, output_tokens=usage.output_tokens if usage else 0,
                              cache_read_tokens=usage.cache_read_tokens if usage else 0, cost_usd=cost, thinking_payloads=payloads)
      if not tool_calls:
        yield self.emit(finished)
        async for event in self.maybe_compact(): yield event
        break
      for call in tool_calls:
        yield self.emit(ToolCallRequested(id=call.id, tool=call.name, args=self.safe_args(call), args_json=call.args_json))
        try:
          args = call.args()
        except ValueError as error:
          args, call.status, call.result = None, "error", f"Invalid tool arguments: {error}"
        if args is not None:
          approval_event = self.resolve_approval(call, args)
          if approval_event is not None: yield self.emit(approval_event)
          if call.status != "error": self.dispatch_call(call, args)
        self.messages.append(Message(role="tool", content=call.result or "", tool_call_id=call.id))
        self.current_turn_completed_calls += 1
        calls_this_prompt += 1
        yield self.emit(ToolCallFinished(id=call.id, status=call.status, result=call.result or "", result_chars=len(call.result or "")))
        if calls_this_prompt >= self.app.lana.max_tool_calls_per_prompt:
          if self.app.lana.auto_continue: calls_this_prompt = 0  # EC-11: auto_continue skips the pause
          elif self.continue_callback and self.continue_callback(calls_this_prompt): calls_this_prompt = 0
          else:
            self.stop_reason = "limit"
            yield self.emit(finished)
            yield self.emit(ErrorEvent(message=f"tool call limit reached ({self.app.lana.max_tool_calls_per_prompt} calls) - continue by sending a new prompt or set auto_continue"))
            return
      yield self.emit(finished)
      async for event in self.maybe_compact(): yield event  # FR-07: checked after EACH turn, not only post-prompt

  # Post-turn compaction hook (FR-07); events emitted and persisted like all others
  async def maybe_compact(self):
    if self.compactor is None: return
    async for event in self.compactor(self): yield self.emit(event)

  @staticmethod
  def safe_args(call: ToolCall) -> dict:
    try:
      return call.args()
    except ValueError:
      return {}

  # Ctrl+C handling (EC-10): completed calls kept, synthetic note appended, prompt returns
  def note_cancellation(self):
    self.stop_reason = "cancelled"
    count = self.current_turn_completed_calls
    note = f"turn cancelled after {count} tool call" + ("s" if count != 1 else "")
    self.emit(ErrorEvent(message=note))
    self.messages.append(Message(role="user", content=f"<cancellation_note>{note}</cancellation_note>"))
    return note
