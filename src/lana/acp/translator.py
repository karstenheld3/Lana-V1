"""EventTranslator: AgentEvent -> session/update payloads (LANAACPB-IP01 IS-05, SP01 FR-06/07).

Exhaustive over the 11 AgentEvent types (IG-03): every type yields its mapping or a documented
no-op. Owns messageId rotation - one logical message per turn (DD-06, v2 forward compatibility).
"""
import json
from lana.acp import log

# FR-07: 16 tools -> ACP kinds (LANAACPB-IN01 / ACP-IN08 kind vocabulary)
TOOL_KINDS = {
  "read_file": "read", "list_dir": "read", "view_content_chunk": "read",
  "grep_search": "search", "find_by_name": "search", "trajectory_search": "search",
  "edit": "edit", "multi_edit": "edit", "write_to_file": "edit",
  "run_command": "execute", "command_status": "execute",
  "search_web": "fetch", "read_url_content": "fetch",
  "todo_list": "think",
  "skill": "other", "ask_user_question": "other",
}

PRIMARY_ARGUMENT_KEYS = ("CommandLine", "file_path", "TargetFile", "AbsolutePath", "DirectoryPath", "SearchPath", "SearchDirectory", "Url", "Query", "Pattern", "query", "question", "SkillName", "ID")
TODO_RESULT_PREFIX = "Todo list updated:\n"


def primary_argument(args: dict) -> str:
  for key in PRIMARY_ARGUMENT_KEYS:
    value = args.get(key)
    if isinstance(value, str) and value: return value
  for value in args.values():
    if isinstance(value, str) and value: return value
  return ""


class EventTranslator:
  """Maps one AgentEvent to zero or more `session/update` payloads (FR-06 table)."""

  def __init__(self, cost_tracker=None, context_window: int = 0, replaying: bool = False):
    self.cost_tracker = cost_tracker
    self.context_window = context_window  # generator context window for usage_update `size`
    self.replaying = replaying            # session/load replay: user_message becomes user_message_chunk (FR-06)
    self.turn_counter = 0
    self.message_id = "msg_0"

  def translate(self, event) -> list[dict]:
    kind = event.type
    if kind == "turn_started":  # no notification; rotates the messageId (FR-06)
      self.turn_counter += 1
      self.message_id = f"msg_{self.turn_counter}"
      return []
    if kind == "text_delta":
      return [{"sessionUpdate": "agent_message_chunk", "messageId": self.message_id, "content": {"type": "text", "text": event.text}}]
    if kind == "thinking_delta":
      return [{"sessionUpdate": "agent_thought_chunk", "messageId": self.message_id, "content": {"type": "text", "text": event.text}}]
    if kind == "tool_call_requested":
      argument = primary_argument(event.args)
      title = f"{event.tool}: {argument}" if argument else event.tool
      return [{"sessionUpdate": "tool_call", "toolCallId": event.id, "title": title[:200], "kind": TOOL_KINDS.get(event.tool, "other"), "status": "pending"}]
    if kind == "tool_call_finished":
      status = "completed" if event.status == "ok" else "failed"
      payloads = [{"sessionUpdate": "tool_call_update", "toolCallId": event.id, "status": status,
                   "content": [{"type": "content", "content": {"type": "text", "text": event.result}}]}]
      if event.result.startswith(TODO_RESULT_PREFIX):  # DD-08: todo state additionally maps to a whole-plan update
        plan = self.todo_plan(event.result)
        if plan is not None: payloads.append(plan)
      return payloads
    if kind == "turn_finished":
      return [self.usage_update(event)]
    if kind == "user_message":
      if not self.replaying: return []  # live: the client owns the user's message (FR-06)
      return [{"sessionUpdate": "user_message_chunk", "content": {"type": "text", "text": event.content}}]
    if kind == "error":  # v1 has no dedicated error update type - render inline (FR-06 [ASSUMED])
      return [{"sessionUpdate": "agent_message_chunk", "messageId": self.message_id, "content": {"type": "text", "text": event.message}}]
    if kind == "checkpoint_created":  # no ACP mapping in v1 (Session Compaction RFD is Draft) - documented omission
      message_label = "1 message" if event.truncated_messages == 1 else f"{event.truncated_messages} messages"
      log(f"  checkpoint_created not forwarded - no v1 ACP mapping ({message_label} compacted).")
      return []
    return []  # session_started, approval_required: session-file-only / consumed by the PermissionBroker (FR-06)

  def todo_plan(self, result: str):
    try:
      entries = json.loads(result.split(TODO_RESULT_PREFIX, 1)[1])
    except (IndexError, json.JSONDecodeError):
      return None
    return {"sessionUpdate": "plan",
            "entries": [{"content": item.get("content", ""), "priority": item.get("priority", "medium"), "status": item.get("status", "pending")} for item in entries]}

  # Official v1 shape used/size/cost (LANAACPB-IN01); used = the turn's context consumption [ASSUMED mapping]
  def usage_update(self, event) -> dict:
    update = {"sessionUpdate": "usage_update", "used": event.input_tokens + event.output_tokens, "size": self.context_window}
    if self.cost_tracker is not None:
      total, _ = self.cost_tracker.session_total()
      update["cost"] = {"amount": total, "currency": "USD"}
    return update


# Generator context window from the pricing entry (context_window_k); 0 when unpriced
def generator_context_window(cost_tracker) -> int:
  rates = cost_tracker.rates("generator") if cost_tracker else None
  return int(rates.get("context_window_k", 0)) * 1000 if rates else 0
