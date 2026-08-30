"""ACP session/load and CLI-flag tests (LANAACPB-IP01 Categories 7-8: TC-34..39)
plus black-box cross-frontend scenarios (LANAACPB-TP01-TC-03/04)."""
import json, subprocess, sys, time
import pytest
from tests.acp_harness import AcpClient, assert_stdout_pure
from tests.conftest import write_config_dir, write_prompt_system
from tests.harness import LanaProc
from tests.scripted_adapter import write_script

TOOL_TURNS = [{"text": "Reading.", "tool_calls": [{"name": "list_dir", "args": {"DirectoryPath": "."}}], "usage": {"input": 900, "output": 40}},
              {"text": "All done.", "usage": {"input": 1100, "output": 30}}]


@pytest.fixture
def loaded_workspace(tmp_path):
  """Workspace with config + fake system + a script that supports two full prompts."""
  workspace = tmp_path / "ws"
  workspace.mkdir()
  fake_system = write_prompt_system(tmp_path / "fs", workflows={"hello": "---\ndescription: Say hello\n---\n# Hello\n\nSay hello."})
  write_config_dir(workspace, lana_overrides={"agent_folder": str(fake_system)})
  script = write_script(workspace / "script.jsonl", TOOL_TURNS + TOOL_TURNS)
  return workspace, script


def make_acp_session_with_turn(workspace, script):
  client = AcpClient(workspace, script_path=script).start()
  client.handshake()
  session_id, _ = client.session_new()
  client.request("session/prompt", {"sessionId": session_id, "prompt": [{"type": "text", "text": "list please"}]})
  client.stop()
  return session_id


# TC-34 + TP01-TC-04 direction ACP->ACP: load replays history in original order, then a follow-up turn works
def test_tc34_load_replays_acp_session(loaded_workspace):
  workspace, script = loaded_workspace
  session_id = make_acp_session_with_turn(workspace, script)
  client = AcpClient(workspace, script_path=script).start()
  try:
    client.handshake()
    response, collected = client.request("session/load", {"sessionId": session_id, "cwd": str(workspace)})
    assert response["result"] == {}
    updates = client.updates(collected)
    kinds = [update["sessionUpdate"] for update in updates]
    assert "user_message_chunk" in kinds  # replay echoes the user message (FR-06 replay exception)
    assert kinds.index("user_message_chunk") < kinds.index("tool_call") < kinds.index("tool_call_update")
    user_chunk = next(update for update in updates if update["sessionUpdate"] == "user_message_chunk")
    assert "list please" in user_chunk["content"]["text"]
    follow_up, _ = client.request("session/prompt", {"sessionId": session_id, "prompt": [{"type": "text", "text": "again"}]})
    assert follow_up["result"]["stopReason"] == "end_turn"
    assert_stdout_pure(client)
  finally:
    client.stop()


# TC-35 + TP01-TC-04 direction CLI->ACP: a CLI-created session loads identically over ACP (IG-02)
def test_tc35_load_cli_session(loaded_workspace):
  workspace, script = loaded_workspace
  proc = LanaProc(workspace, script_path=script)
  result = proc.run_headless("cli input")
  assert result.returncode == 0
  session_id = proc.session_files()[-1].stem
  client = AcpClient(workspace, script_path=script).start()
  try:
    client.handshake()
    response, collected = client.request("session/load", {"sessionId": session_id, "cwd": str(workspace)})
    assert response["result"] == {}
    kinds = [update["sessionUpdate"] for update in client.updates(collected)]
    assert "user_message_chunk" in kinds and "tool_call" in kinds and "agent_message_chunk" in kinds
  finally:
    client.stop()


# TC-36 + TP01-TC-03 (ACP -> CLI resume): recorded environment wins; capture oracle proves byte identity
def test_tc36_recorded_environment_authority(loaded_workspace):
  workspace, script = loaded_workspace
  capture_path = workspace / "capture.jsonl"
  client = AcpClient(workspace, script_path=script)
  client.extra_env["LANA_SCRIPTED_CAPTURE"] = str(capture_path)
  client.start()
  try:
    client.handshake()
    session_id, _ = client.session_new()
    client.request("session/prompt", {"sessionId": session_id, "prompt": [{"type": "text", "text": "first"}]})
  finally:
    client.stop()
  # CLI resume of the ACP session: /cost seeded, then a prompt with the RECORDED system prompt (LANAAGNT-FR-08)
  session_file = workspace / ".lana-data" / "sessions" / f"{session_id}.jsonl"
  proc = LanaProc(workspace, script_path=script)
  proc.extra_env["LANA_SCRIPTED_CAPTURE"] = str(capture_path)
  result = proc.run_headless("again", extra_args=["--resume", str(session_file)])
  assert result.returncode == 0
  captures = [json.loads(line) for line in capture_path.read_text(encoding="utf-8").splitlines()]
  assert len(captures) >= 3
  assert captures[-1]["system"] == captures[0]["system"] and captures[-1]["tools"] == captures[0]["tools"]  # byte identity


# TC-37: unknown sessionId -> error naming the sessions dir; legacy file without session_started -> loads with warning
def test_tc37_unknown_and_legacy(loaded_workspace):
  workspace, script = loaded_workspace
  session_id = make_acp_session_with_turn(workspace, script)
  session_file = workspace / ".lana-data" / "sessions" / f"{session_id}.jsonl"
  lines = session_file.read_text(encoding="utf-8").splitlines()
  legacy_file = workspace / ".lana-data" / "sessions" / "legacy_0000.jsonl"
  legacy_file.write_text("\n".join(lines[1:]) + "\n", encoding="utf-8")  # strip session_started (EC-18)
  client = AcpClient(workspace, script_path=script).start()
  try:
    client.handshake()
    response, _ = client.request("session/load", {"sessionId": "2026-01-01_000000_zzzz", "cwd": str(workspace)})
    assert "error" in response and ".lana-data" in response["error"]["message"]  # EC-17: self-contained
    response, _ = client.request("session/load", {"sessionId": "legacy_0000", "cwd": str(workspace)})
    assert response["result"] == {}
    assert "legacy session file" in client.stderr_text()
  finally:
    client.stop()


# TC-38: --acp mutually exclusive with -p and --resume -> exit 2 (DD-09)
def test_tc38_flag_exclusivity(loaded_workspace):
  workspace, script = loaded_workspace
  for extra in (["-p", "hi"], ["--resume", "x.jsonl"]):
    result = subprocess.run([sys.executable, "-m", "lana", "--acp", *extra], cwd=workspace, capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert result.returncode == 2 and "mutually exclusive" in result.stderr
    assert result.stdout == ""  # IG-01 even on the error path


# TC-39: startup sends nothing before the first request; EOF -> exit 0 (FR-01, FR-02)
def test_tc39_silent_startup_clean_eof(loaded_workspace):
  workspace, script = loaded_workspace
  client = AcpClient(workspace, script_path=script).start()
  time.sleep(1.0)
  assert client.raw_stdout == []  # FR-02: nothing before initialize
  client.close_stdin()
  assert client.wait_exit() == 0
  assert client.raw_stdout == []
