"""PermissionBroker and ElicitationBroker: Agent callbacks over client round-trips (LANAACPB-IP01 IS-07/08).

Both brokers are async callbacks plugged into the Agent seam (IS-06). They block the tool dispatch
while the stdin read loop keeps processing - cancellation resolves their pending futures (IG-05).
"""
from lana.acp import log
from lana.acp.jsonrpc import ClientErrorResponse, RoundTripCancelled

PERMISSION_OPTIONS = [
  {"optionId": "allow-once", "name": "Allow once", "kind": "allow_once"},
  {"optionId": "allow-always", "name": "Always allow", "kind": "allow_always"},
  {"optionId": "reject-once", "name": "Reject", "kind": "reject_once"},
  {"optionId": "reject-always", "name": "Always reject", "kind": "reject_always"},
]
CONTINUE_OPTIONS = [
  {"optionId": "allow-once", "name": "Continue", "kind": "allow_once"},
  {"optionId": "reject-once", "name": "Stop here", "kind": "reject_once"},
]
NO_ELICITATION_FALLBACK = "Client does not support structured questions - ask in plain text"


class PermissionBroker:
  """Implements the Agent's approve/continue callbacks via session/request_permission (FR-08)."""

  def __init__(self, connection, session_id: str):
    self.connection = connection
    self.session_id = session_id
    self.current_tool_call_id = "unknown"       # server updates on every tool_call_requested event
    self.always: dict[tuple, bool] = {}         # (action, first detail token) -> remembered decision, session lifetime
    self.continue_counter = 0

  @staticmethod
  def memory_key(action: str, detail: str) -> tuple:
    return (action, (detail.split() or [""])[0])

  async def approve(self, action: str, detail: str) -> bool:
    key = self.memory_key(action, detail)
    if key in self.always:
      log(f"  request_permission skipped - remembered '{'allow' if self.always[key] else 'reject'}-always' for {key}.")  # EC-12
      return self.always[key]
    outcome = await self.request_outcome(self.current_tool_call_id, PERMISSION_OPTIONS)
    option = outcome.get("optionId", "") if outcome.get("outcome") == "selected" else ""
    approved = option.startswith("allow")
    if option in ("allow-always", "reject-always"): self.always[key] = approved
    log(f"  request_permission {self.current_tool_call_id} ({action}) -> {option or 'cancelled'}.")
    return approved

  # Tool-call-limit continue prompt on a synthetic toolCallId (FR-08 [ASSUMED])
  async def ask_continue(self, calls_done: int) -> bool:
    self.continue_counter += 1
    outcome = await self.request_outcome(f"continue_{self.continue_counter}", CONTINUE_OPTIONS)
    approved = outcome.get("outcome") == "selected" and outcome.get("optionId") == "allow-once"
    call_label = "1 call" if calls_done == 1 else f"{calls_done} calls"
    log(f"  continue prompt ({call_label}) -> {'continue' if approved else 'stop'}.")
    return approved

  async def request_outcome(self, tool_call_id: str, options: list[dict]) -> dict:
    params = {"sessionId": self.session_id, "toolCall": {"toolCallId": tool_call_id}, "options": options}
    try:
      result = await self.connection.request("session/request_permission", params)
    except RoundTripCancelled:
      return {"outcome": "cancelled"}
    except ClientErrorResponse as error:  # EC-14: client error counts as rejection
      log(f"  WARNING: client answered request_permission with an error - treated as rejection: {error}")
      return {"outcome": "cancelled"}
    return (result or {}).get("outcome") or {"outcome": "cancelled"}


class ElicitationBroker:
  """Implements the ask_user_question tool over elicitation/create form mode (FR-09)."""

  def __init__(self, connection, session_id: str, form_supported: bool):
    self.connection = connection
    self.session_id = session_id
    self.form_supported = form_supported  # client advertised elicitation.form present AND non-null

  async def ask(self, args: dict) -> str:
    if not self.form_supported: return NO_ELICITATION_FALLBACK  # EC-20: zero wire requests
    labels = [option.get("label", "") for option in (args.get("options") or []) if option.get("label")]
    if args.get("allowMultiple"):
      answer_schema = {"type": "array", "items": {"type": "string", "enum": labels}} if labels else {"type": "array", "items": {"type": "string"}}
    else:
      answer_schema = {"type": "string", "enum": labels} if labels else {"type": "string"}
    params = {"sessionId": self.session_id, "mode": "form", "message": args.get("question", ""),
              "requestedSchema": {"type": "object", "properties": {"answer": answer_schema}, "required": ["answer"]}}
    try:
      result = await self.connection.request("elicitation/create", params)
    except RoundTripCancelled:
      return "no answer (cancelled)"
    except ClientErrorResponse as error:
      log(f"  WARNING: client answered elicitation/create with an error: {error}")
      return "no answer (client error)"
    if (result or {}).get("action") != "accept": return "no answer (user declined)"  # decline/cancel -> fallback (FR-09)
    answer = ((result or {}).get("content") or {}).get("answer")
    if isinstance(answer, list): return ", ".join(str(item) for item in answer)
    return str(answer) if answer is not None else "no answer (empty response)"
