"""Black-box ACP scenarios against the real executable (LANAACPB-TP01-TC-01/07/09/10).
Remaining TP01 scenarios live in test_acp_turn.py / test_acp_load.py (mapping in each test's docstring there)."""
import json, time
import pytest
from lana.events import from_jsonl
from tests.acp_harness import AcpClient, assert_stdout_pure
from tests.conftest import write_config_dir, write_prompt_system
from tests.harness import assert_no_secret_leak
from tests.scripted_adapter import write_script

FAKE_KEYS = ["sk-test-openai", "sk-test-anthropic"]


@pytest.fixture
def scenario_workspace(tmp_path):
  workspace = tmp_path / "ws"
  workspace.mkdir()
  fake_system = write_prompt_system(tmp_path / "fs", workflows={"hello": "---\ndescription: Say hello\n---\n# Hello\n\nSay hello."})
  write_config_dir(workspace, lana_overrides={"prompt_system_paths": [str(fake_system)]})
  return workspace


def make_client(workspace, turns, **kwargs):
  script = write_script(workspace / "script.jsonl", turns)
  return AcpClient(workspace, script_path=script, **kwargs).start()


def session_events(workspace, session_id):
  session_file = workspace / ".lana" / "sessions" / f"{session_id}.jsonl"
  return [from_jsonl(line) for line in session_file.read_text(encoding="utf-8").splitlines() if line.strip()]


# TP01-TC-01: full happy path - handshake, session, rich turn, ordered updates, purity, clean EOF
def test_tp01_tc01_full_happy_path(scenario_workspace):
  todos = [{"id": "1", "content": "Inspect", "status": "pending", "priority": "high"}]
  turns = [{"thinking": "hm", "text": "Working.", "tool_calls": [
              {"name": "list_dir", "args": {"DirectoryPath": "."}},
              {"name": "todo_list", "args": {"todos": todos}}], "usage": {"input": 800, "output": 60}},
           {"text": "Finished.", "usage": {"input": 950, "output": 25}}]
  client = make_client(scenario_workspace, turns)
  try:
    result = client.handshake()
    assert result["agentCapabilities"]["loadSession"] is True
    session_id, collected_new = client.session_new()
    commands = client.updates(collected_new, "available_commands_update") or [client.read_message()["params"]["update"]]
    assert [command["name"] for command in commands[0]["availableCommands"]] == ["hello"]
    response, collected = client.request("session/prompt", {"sessionId": session_id, "prompt": [{"type": "text", "text": "go"}]})
    assert response["result"] == {"stopReason": "end_turn"}
    kinds = [update["sessionUpdate"] for update in client.updates(collected)]
    for expected in ("agent_thought_chunk", "agent_message_chunk", "tool_call", "tool_call_update", "plan", "usage_update"):
      assert expected in kinds, f"missing {expected} in {kinds}"
    assert kinds.index("tool_call") < kinds.index("tool_call_update")
    client.close_stdin()
    assert client.wait_exit() == 0
    assert_stdout_pure(client)
  finally:
    client.stop()


# TP01-TC-07: allow_always remembered across TURNS in one session; a fresh process asks again (FR-08 in-memory scope)
def test_tp01_tc07_allow_always_scope(scenario_workspace):
  call = {"name": "run_command", "args": {"CommandLine": "Write-Output scoped", "Blocking": True}}
  turns = [{"text": "One.", "tool_calls": [call]}, {"text": "Done1."},
           {"text": "Two.", "tool_calls": [call]}, {"text": "Done2."}]
  client = make_client(scenario_workspace, turns)
  client.auto_responders["session/request_permission"] = lambda params: {"outcome": {"outcome": "selected", "optionId": "allow-always"}}
  try:
    client.handshake()
    session_id, _ = client.session_new()
    _, first = client.request("session/prompt", {"sessionId": session_id, "prompt": [{"type": "text", "text": "one"}]})
    _, second = client.request("session/prompt", {"sessionId": session_id, "prompt": [{"type": "text", "text": "two"}]})
    assert sum(1 for m in first if m.get("method") == "session/request_permission") == 1
    assert sum(1 for m in second if m.get("method") == "session/request_permission") == 0  # remembered across turns
  finally:
    client.stop()
  fresh = make_client(scenario_workspace, turns)  # new process = new session = asks again
  fresh.auto_responders["session/request_permission"] = lambda params: {"outcome": {"outcome": "selected", "optionId": "allow-once"}}
  try:
    fresh.handshake()
    fresh_session, _ = fresh.session_new()
    _, collected = fresh.request("session/prompt", {"sessionId": fresh_session, "prompt": [{"type": "text", "text": "one"}]})
    assert any(m.get("method") == "session/request_permission" for m in collected)
  finally:
    fresh.stop()


# TP01-TC-09: kill mid-turn -> session JSONL intact; a fresh process loads it and completes a new turn (NFR-03)
def test_tp01_tc09_kill_and_reload(scenario_workspace):
  turns = [{"text": "Slow.", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "Start-Sleep -Seconds 20", "SafeToAutoRun": True}}]},
           {"text": "Recovered.", "usage": {"input": 500, "output": 20}}]
  client = make_client(scenario_workspace, turns, policy="turbo")
  client.handshake()
  session_id, _ = client.session_new()
  client.send({"id": 99, "method": "session/prompt", "params": {"sessionId": session_id, "prompt": [{"type": "text", "text": "go"}]}})
  deadline = time.monotonic() + 15
  while time.monotonic() < deadline:  # wait until the tool_call is on the wire (turn is mid-flight)
    message = client.read_message(timeout=10)
    if message.get("method") == "session/update" and message["params"]["update"].get("sessionUpdate") == "tool_call": break
  client.kill()  # hard kill mid-tool
  events = session_events(scenario_workspace, session_id)
  assert events and events[0].type == "session_started"  # file intact, first line preserved
  reload_client = make_client(scenario_workspace, turns[1:], policy="turbo")
  try:
    reload_client.handshake()
    response, _ = reload_client.request("session/load", {"sessionId": session_id, "cwd": str(scenario_workspace)})
    assert response["result"] == {}
    follow_up, _ = reload_client.request("session/prompt", {"sessionId": session_id, "prompt": [{"type": "text", "text": "continue"}]})
    assert follow_up["result"]["stopReason"] == "end_turn"
  finally:
    reload_client.stop()


# TP01-TC-10: hostile client battery in ONE connection, then a valid turn; secret sweep over all outputs (FR-11, NFR-02)
def test_tp01_tc10_hostile_battery_secret_sweep(scenario_workspace):
  client = make_client(scenario_workspace, [{"text": "Still alive.", "usage": {"input": 100, "output": 10}}])
  try:
    early, _ = client.request("session/prompt", {"sessionId": "x", "prompt": []})  # before handshake
    assert "error" in early
    client.handshake()
    client.send_raw("{garbage")
    parse_error = client.read_message()
    assert parse_error["error"]["code"] == -32700 and parse_error["id"] is None
    unknown, _ = client.request("session/wat", {})
    assert unknown["error"]["code"] == -32601
    session_id, _ = client.session_new()
    image, _ = client.request("session/prompt", {"sessionId": session_id, "prompt": [{"type": "image", "data": "x", "mimeType": "image/png"}]})
    assert image["error"]["code"] == -32602
    valid, _ = client.request("session/prompt", {"sessionId": session_id, "prompt": [{"type": "text", "text": "hello"}]})
    assert valid["result"]["stopReason"] == "end_turn"  # connection survived the battery
    session_text = (scenario_workspace / ".lana" / "sessions" / f"{session_id}.jsonl").read_text(encoding="utf-8")
    assert_no_secret_leak(["\n".join(client.raw_stdout), client.stderr_text(), session_text], FAKE_KEYS)
    assert_stdout_pure(client)
  finally:
    client.stop()
