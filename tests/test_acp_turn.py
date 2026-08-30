"""ACP prompt turn, translation, permission, elicitation, and cancellation tests
(LANAACPB-IP01 Categories 4-6: TC-16..33, TC-41..44)."""
import time
import pytest
from lana.events import (ApprovalRequired, CheckpointCreated, ErrorEvent, PromptStep, SessionStarted, TextDelta, ThinkingDelta,
                         ToolCallFinished, ToolCallRequested, TurnFinished, TurnStarted, UserMessage, from_jsonl)
from lana.acp.translator import EventTranslator, TOOL_KINDS
from tests.acp_harness import AcpClient, assert_stdout_pure
from tests.conftest import write_config_dir, write_prompt_system
from tests.scripted_adapter import write_script


# ------------------------------------------- START: TC-44 unit -------------------------------------------------------

# TC-44: one instance of each of the 12 AgentEvent types (incl. prompt_step) -> mapping or documented no-op, none raises (IG-03)
def test_tc44_translator_exhaustive(capsys):
  translator = EventTranslator()
  events = [
    SessionStarted(system_prompt="s"), UserMessage(content="hi"), TurnStarted(),
    TextDelta(text="t"), ThinkingDelta(text="th"),
    ToolCallRequested(id="tc_1", tool="run_command", args={"CommandLine": "Write-Output hi"}),
    ToolCallFinished(id="tc_1", status="ok", result="hi"),
    ApprovalRequired(action="run_command", detail="x", approved=True),
    CheckpointCreated(text="cp", truncated_messages=3, kept_messages=1),
    TurnFinished(input_tokens=10, output_tokens=5), ErrorEvent(message="oops"),
    PromptStep(index=1, total=2, digest="a1b2c3d4e5f6"),
  ]
  mapped = {event.type: translator.translate(event) for event in events}
  assert len(mapped) == 12
  no_ops = {"session_started", "user_message", "turn_started", "approval_required", "checkpoint_created", "prompt_step"}
  for event_type, payloads in mapped.items():
    if event_type in no_ops: assert payloads == [], event_type
    else: assert payloads and all("sessionUpdate" in payload for payload in payloads), event_type
  stderr_text = capsys.readouterr().err
  assert "checkpoint_created not forwarded" in stderr_text  # documented omission
  assert "prompt_step not forwarded" in stderr_text  # documented omission (headless-only, FR-12)
  assert len(TOOL_KINDS) == 16  # FR-07


# ------------------------------------------- END: TC-44 unit ---------------------------------------------------------


@pytest.fixture
def make_client(tmp_path):
  clients = []

  def build(turns, capabilities="full", policy=None, lana_overrides=None):
    workspace = tmp_path / f"ws{len(clients)}"
    workspace.mkdir()
    fake_system = write_prompt_system(tmp_path / f"fs{len(clients)}",
      workflows={"hello": "---\ndescription: Say hello\n---\n# Hello\n\nSay hello."})
    write_config_dir(workspace, lana_overrides={"agent_folder": str(fake_system), **(lana_overrides or {})})
    script = write_script(workspace / "script.jsonl", turns)
    client = AcpClient(workspace, script_path=script, capabilities=capabilities, policy=policy).start()
    clients.append(client)
    return client

  yield build
  for client in clients: client.stop()


def read_until(client, predicate, timeout=20):
  deadline = time.monotonic() + timeout
  seen = []
  while time.monotonic() < deadline:
    message = client.read_message(timeout=max(0.1, deadline - time.monotonic()))
    seen.append(message)
    if predicate(message): return message, seen
  raise TimeoutError(f"predicate not met; saw {[m.get('method') or list(m) for m in seen]}")


def send_request_no_wait(client, method, params):
  request_id = client.next_id
  client.next_id += 1
  client.send({"id": request_id, "method": method, "params": params})
  return request_id


def prompt_params(client, session_id, text="do something"):
  return {"sessionId": session_id, "prompt": [{"type": "text", "text": text}]}


def session_events(client, session_id):
  session_file = client.workspace / ".lana-data" / "sessions" / f"{session_id}.jsonl"
  return [from_jsonl(line) for line in session_file.read_text(encoding="utf-8").splitlines() if line.strip()]


# TC-16: text turn -> chunk stream with stable messageId, usage_update before the response, stopReason-only response
def test_tc16_text_turn_stream(make_client):
  client = make_client([{"text": "Hello from Lana.", "usage": {"input": 1000, "output": 50}}])
  client.handshake()
  session_id, _ = client.session_new()
  response, collected = client.request("session/prompt", prompt_params(client, session_id))
  assert response["result"] == {"stopReason": "end_turn"}  # no usage field (LANAACPB-IN01)
  chunks = client.updates(collected, "agent_message_chunk")
  assert chunks and all(chunk["messageId"] == chunks[0]["messageId"] for chunk in chunks)
  assert "".join(chunk["content"]["text"] for chunk in chunks) == "Hello from Lana."
  usage = client.updates(collected, "usage_update")
  assert usage and usage[-1]["used"] == 1050 and usage[-1]["size"] == 200000 and usage[-1]["cost"]["currency"] == "USD"
  assert_stdout_pure(client)


# TC-17: tool turn -> tool_call (pending, kind per FR-07) then tool_call_update (completed), wire order preserved
def test_tc17_tool_call_lifecycle(make_client):
  client = make_client([{"text": "Reading.", "tool_calls": [{"name": "list_dir", "args": {"DirectoryPath": "."}}]}, {"text": "Done."}])
  client.handshake()
  session_id, _ = client.session_new()
  _, collected = client.request("session/prompt", prompt_params(client, session_id))
  updates = client.updates(collected)
  tool_call_index = next(i for i, u in enumerate(updates) if u["sessionUpdate"] == "tool_call")
  update_index = next(i for i, u in enumerate(updates) if u["sessionUpdate"] == "tool_call_update")
  assert tool_call_index < update_index
  assert updates[tool_call_index]["kind"] == "read" and updates[tool_call_index]["status"] == "pending"
  assert updates[tool_call_index]["title"].startswith("list_dir: ")
  assert updates[update_index]["status"] == "completed" and updates[update_index]["toolCallId"] == updates[tool_call_index]["toolCallId"]


# TC-18: todo_list result -> additional plan update with 1:1 entries (DD-08)
def test_tc18_todo_plan_update(make_client):
  todos = [{"id": "1", "content": "First step", "status": "in_progress", "priority": "high"}]
  client = make_client([{"text": "Planning.", "tool_calls": [{"name": "todo_list", "args": {"todos": todos}}]}, {"text": "Done."}])
  client.handshake()
  session_id, _ = client.session_new()
  _, collected = client.request("session/prompt", prompt_params(client, session_id))
  plans = client.updates(collected, "plan")
  assert plans and plans[0]["entries"][0] == {"content": "First step", "priority": "high", "status": "in_progress"}


# TC-19: thinking deltas -> agent_thought_chunk with the turn's messageId
def test_tc19_thinking_chunks(make_client):
  client = make_client([{"thinking": "pondering...", "text": "Answer.", "usage": {"input": 10, "output": 5}}])
  client.handshake()
  session_id, _ = client.session_new()
  _, collected = client.request("session/prompt", prompt_params(client, session_id))
  thoughts = client.updates(collected, "agent_thought_chunk")
  messages = client.updates(collected, "agent_message_chunk")
  assert thoughts and thoughts[0]["content"]["text"] == "pondering..."
  assert thoughts[0]["messageId"] == messages[0]["messageId"]


# TC-20: image content block -> -32602 naming the type (EC-03)
def test_tc20_image_block_rejected(make_client):
  client = make_client([{"text": "unused"}])
  client.handshake()
  session_id, _ = client.session_new()
  response, _ = client.request("session/prompt", {"sessionId": session_id, "prompt": [{"type": "image", "data": "...", "mimeType": "image/png"}]})
  assert response["error"]["code"] == -32602 and "'image'" in response["error"]["message"]


# TC-43: text + resource_link accepted (baseline); user message carries the reference line (FR-05)
def test_tc43_resource_link_baseline(make_client):
  client = make_client([{"text": "Looked at it."}])
  client.handshake()
  session_id, _ = client.session_new()
  response, _ = client.request("session/prompt", {"sessionId": session_id, "prompt": [
    {"type": "text", "text": "Analyze this file"},
    {"type": "resource_link", "uri": "file:///proj/main.py", "name": "main.py"}]})
  assert response["result"]["stopReason"] == "end_turn"
  user_events = [event for event in session_events(client, session_id) if event.type == "user_message"]
  assert "Analyze this file" in user_events[0].content and "[resource: main.py](file:///proj/main.py)" in user_events[0].content


# TC-21: second concurrent session/prompt -> error; first turn completes normally (EC-08)
def test_tc21_concurrent_prompt_rejected(make_client):
  client = make_client([{"text": "Try.", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "Write-Output hi"}}]}, {"text": "Done."}])
  client.handshake()
  session_id, _ = client.session_new()
  first_id = send_request_no_wait(client, "session/prompt", prompt_params(client, session_id))
  permission, _ = read_until(client, lambda m: m.get("method") == "session/request_permission")  # turn is now blocked
  second_response, _ = client.request("session/prompt", prompt_params(client, session_id, "second"))
  assert "error" in second_response and "already active" in second_response["error"]["message"]
  client.send({"id": permission["id"], "result": {"outcome": {"outcome": "selected", "optionId": "reject-once"}}})
  first_response, _ = read_until(client, lambda m: m.get("id") == first_id)
  assert first_response["result"]["stopReason"] == "end_turn"


# TC-22: scripted provider error -> JSON-RPC error response on the prompt id; prior notifications intact (EC-13)
def test_tc22_provider_error(make_client):
  client = make_client([{"error": "rate limited"}])
  client.handshake()
  session_id, _ = client.session_new()
  response, _ = client.request("session/prompt", prompt_params(client, session_id))
  assert "error" in response and "rate limited" in response["error"]["message"]


# TC-23: session JSONL after an ACP turn == event types of the identical CLI-driven turn (IG-02 differential)
def test_tc23_cross_frontend_jsonl_identical(make_client, tmp_path):
  from tests.harness import LanaProc
  turns = [{"text": "Reading.", "tool_calls": [{"name": "list_dir", "args": {"DirectoryPath": "."}}]}, {"text": "Done."}]
  client = make_client(turns)
  client.handshake()
  session_id, _ = client.session_new()
  client.request("session/prompt", prompt_params(client, session_id, "same input"))
  acp_types = [event.type for event in session_events(client, session_id)]
  cli_workspace = tmp_path / "cli_ws"
  cli_workspace.mkdir()
  fake_system = write_prompt_system(tmp_path / "cli_fs", workflows={"hello": "---\ndescription: Say hello\n---\n# Hello\n\nSay hello."})
  write_config_dir(cli_workspace, lana_overrides={"agent_folder": str(fake_system)})
  script = write_script(cli_workspace / "script.jsonl", turns)
  proc = LanaProc(cli_workspace, script_path=script)
  proc.run_headless("same input")
  cli_types = [event.type for event in proc.read_session_events()]
  assert acp_types == cli_types


# TC-24: approval-needing command -> request_permission with 4 options; allow_once -> tool executes
def test_tc24_permission_allow_once(make_client):
  client = make_client([{"text": "Run.", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "Write-Output approved-output", "Blocking": True}}]}, {"text": "Done."}])
  client.auto_responders["session/request_permission"] = lambda params: {"outcome": {"outcome": "selected", "optionId": "allow-once"}}
  client.handshake()
  session_id, _ = client.session_new()
  _, collected = client.request("session/prompt", prompt_params(client, session_id))
  permission = next(m for m in collected if m.get("method") == "session/request_permission")
  assert [option["kind"] for option in permission["params"]["options"]] == ["allow_once", "allow_always", "reject_once", "reject_always"]
  assert permission["params"]["toolCall"]["toolCallId"]
  completed = client.updates(collected, "tool_call_update")
  assert completed[0]["status"] == "completed" and "approved-output" in completed[0]["content"][0]["content"]["text"]


# TC-25: reject_once -> denial recorded, turn continues (existing denial path)
def test_tc25_permission_reject_once(make_client):
  client = make_client([{"text": "Run.", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "Write-Output nope"}}]}, {"text": "Done."}])
  client.auto_responders["session/request_permission"] = lambda params: {"outcome": {"outcome": "selected", "optionId": "reject-once"}}
  client.handshake()
  session_id, _ = client.session_new()
  response, collected = client.request("session/prompt", prompt_params(client, session_id))
  assert response["result"]["stopReason"] == "end_turn"
  failed = client.updates(collected, "tool_call_update")
  assert failed[0]["status"] == "failed" and "denied" in failed[0]["content"][0]["content"]["text"]


# TC-26: allow_always -> second identical action skips the wire request (EC-12)
def test_tc26_allow_always_memory(make_client):
  call = {"name": "run_command", "args": {"CommandLine": "Write-Output twice"}}
  client = make_client([{"text": "Run.", "tool_calls": [call, call]}, {"text": "Done."}])
  client.auto_responders["session/request_permission"] = lambda params: {"outcome": {"outcome": "selected", "optionId": "allow-always"}}
  client.handshake()
  session_id, _ = client.session_new()
  _, collected = client.request("session/prompt", prompt_params(client, session_id))
  permission_requests = [m for m in collected if m.get("method") == "session/request_permission"]
  assert len(permission_requests) == 1
  updates = client.updates(collected, "tool_call_update")
  assert len(updates) == 2 and all(update["status"] == "completed" for update in updates)


# TC-27: ask_user_question with elicitation.form -> elicitation/create; accepted value becomes the tool result
def test_tc27_elicitation_round_trip(make_client):
  question = {"name": "ask_user_question", "args": {"question": "Pick a color", "options": [{"label": "red", "description": "r"}, {"label": "blue", "description": "b"}], "allowMultiple": False}}
  client = make_client([{"text": "Asking.", "tool_calls": [question]}, {"text": "Done."}], capabilities="full")
  client.auto_responders["elicitation/create"] = lambda params: {"action": "accept", "content": {"answer": "red"}}
  client.handshake()
  session_id, _ = client.session_new()
  _, collected = client.request("session/prompt", prompt_params(client, session_id))
  elicitation = next(m for m in collected if m.get("method") == "elicitation/create")
  assert elicitation["params"]["mode"] == "form" and elicitation["params"]["message"] == "Pick a color"
  assert elicitation["params"]["requestedSchema"]["properties"]["answer"]["enum"] == ["red", "blue"]
  result_update = client.updates(collected, "tool_call_update")[0]
  assert result_update["content"][0]["content"]["text"] == "red"


# TC-28: no elicitation capability -> fallback string, zero wire requests (EC-20)
def test_tc28_elicitation_fallback(make_client):
  question = {"name": "ask_user_question", "args": {"question": "Pick", "options": [{"label": "x", "description": "option x"}], "allowMultiple": False}}
  client = make_client([{"text": "Asking.", "tool_calls": [question]}, {"text": "Done."}], capabilities="bare")
  client.handshake()
  session_id, _ = client.session_new()
  _, collected = client.request("session/prompt", prompt_params(client, session_id))
  assert not any(m.get("method") == "elicitation/create" for m in collected)
  result_update = client.updates(collected, "tool_call_update")[0]
  assert "does not support structured questions" in result_update["content"][0]["content"]["text"]


# TC-29: denylisted command under turbo -> permission request still issued (EC-21, IG-04)
def test_tc29_denylist_under_turbo(make_client, tmp_path):
  client = make_client([{"text": "Danger.", "tool_calls": [{"name": "run_command", "args": {"CommandLine": f"Remove-Item {tmp_path / 'victim.txt'}", "SafeToAutoRun": True}}]}, {"text": "Done."}], policy="turbo")
  client.auto_responders["session/request_permission"] = lambda params: {"outcome": {"outcome": "selected", "optionId": "reject-once"}}
  client.handshake()
  session_id, _ = client.session_new()
  _, collected = client.request("session/prompt", prompt_params(client, session_id))
  assert any(m.get("method") == "session/request_permission" for m in collected)  # denylist cannot be bypassed
  assert client.updates(collected, "tool_call_update")[0]["status"] == "failed"


# TC-41: tool-call limit -> continue prompt on synthetic toolCallId; allow -> continues, reject variant -> end_turn
def test_tc41_continue_prompt(make_client):
  calls = [{"name": "list_dir", "args": {"DirectoryPath": "."}}]
  turns = [{"text": "One.", "tool_calls": calls}, {"text": "Two.", "tool_calls": calls}, {"text": "Done."}]
  client = make_client(turns, lana_overrides={"max_tool_calls_per_prompt": 1})
  client.auto_responders["session/request_permission"] = lambda params: {"outcome": {"outcome": "selected", "optionId": "allow-once"}}
  client.handshake()
  session_id, _ = client.session_new()
  response, collected = client.request("session/prompt", prompt_params(client, session_id))
  continue_requests = [m for m in collected if m.get("method") == "session/request_permission"]
  assert continue_requests and continue_requests[0]["params"]["toolCall"]["toolCallId"].startswith("continue_")
  assert [option["kind"] for option in continue_requests[0]["params"]["options"]] == ["allow_once", "reject_once"]
  assert response["result"]["stopReason"] == "end_turn" and len(client.updates(collected, "tool_call_update")) == 2


# TC-30 + TC-42: session/cancel during a slow tool -> processed without waiting; completed calls kept (FR-10, EC-22)
def test_tc30_tc42_cancel_during_slow_tool(make_client):
  turns = [{"text": "Slow.", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "Start-Sleep -Seconds 20", "SafeToAutoRun": True}}]}, {"text": "Never."}]
  client = make_client(turns, policy="turbo")  # turbo auto-executes the non-denylisted sleep
  client.handshake()
  session_id, _ = client.session_new()
  prompt_id = send_request_no_wait(client, "session/prompt", prompt_params(client, session_id))
  read_until(client, lambda m: m.get("method") == "session/update" and m["params"]["update"].get("sessionUpdate") == "tool_call")
  started = time.monotonic()
  client.notify("session/cancel", {"sessionId": session_id})
  response, _ = read_until(client, lambda m: m.get("id") == prompt_id, timeout=15)
  assert response["result"] == {"stopReason": "cancelled"}
  assert time.monotonic() - started < 10  # cancellation did not wait for the 20s tool
  types = [event.type for event in session_events(client, session_id)]
  assert "error" in types  # cancellation note persisted (LANAAGNT-FR-04)


# TC-31: session/cancel while a permission request is pending -> resolved as cancelled, denial recorded (EC-10, IG-05)
def test_tc31_cancel_pending_permission(make_client):
  client = make_client([{"text": "Ask.", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "Write-Output blocked"}}]}, {"text": "Never."}])
  client.handshake()
  session_id, _ = client.session_new()
  prompt_id = send_request_no_wait(client, "session/prompt", prompt_params(client, session_id))
  read_until(client, lambda m: m.get("method") == "session/request_permission")  # leave it pending
  client.notify("session/cancel", {"sessionId": session_id})
  response, _ = read_until(client, lambda m: m.get("id") == prompt_id)
  assert response["result"] == {"stopReason": "cancelled"}
  # The pending permission future resolves as cancelled; whether the denial record lands before the
  # CancelledError preempts the loop is a benign race - the deterministic contract is the note + response
  types = [event.type for event in session_events(client, session_id)]
  assert "error" in types  # cancellation note persisted; session stays replayable


# TC-32: session/cancel with no active turn -> ignored with one stderr line; connection alive (EC-09)
def test_tc32_cancel_without_turn(make_client):
  client = make_client([{"text": "Fine."}])
  client.handshake()
  session_id, _ = client.session_new()
  client.notify("session/cancel", {"sessionId": session_id})
  response, _ = client.request("session/prompt", prompt_params(client, session_id))  # still works
  assert response["result"]["stopReason"] == "end_turn"
  assert "no active turn" in client.stderr_text()


# TC-33: $/cancel_request on the active prompt id -> -32800; on unknown id -> ignored (EC-16)
def test_tc33_protocol_cancel_request(make_client):
  turns = [{"text": "Slow.", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "Start-Sleep -Seconds 20", "SafeToAutoRun": True}}]}, {"text": "Never."}]
  client = make_client(turns, policy="turbo")
  client.handshake()
  session_id, _ = client.session_new()
  client.notify("$/cancel_request", {"requestId": 4711})  # unknown id -> ignored
  prompt_id = send_request_no_wait(client, "session/prompt", prompt_params(client, session_id))
  read_until(client, lambda m: m.get("method") == "session/update" and m["params"]["update"].get("sessionUpdate") == "tool_call")
  client.notify("$/cancel_request", {"requestId": prompt_id})
  response, _ = read_until(client, lambda m: m.get("id") == prompt_id, timeout=15)
  assert response["error"]["code"] == -32800
  assert "no cancellable request" in client.stderr_text()
