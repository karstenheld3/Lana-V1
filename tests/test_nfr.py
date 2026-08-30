"""TK-032: NFR verification fixtures (IS-19) - IG-01 byte identity on the real system, IG-02 JSONL completeness audit."""
import platform
from pathlib import Path
import pytest
from lana.loader import load_prompt_systems
from lana.prompt import build_system_prompt
from tests.scenario_utils import build_scenario_proc
from tests.scripted_adapter import write_script

IPPS_PATH = Path(__file__).resolve().parent.parent / ".lana"


# IG-01: system prompt byte-identical across builds with the REAL IPPS content
def test_ig01_byte_identity_real_system():
  if not IPPS_PATH.is_dir(): pytest.skip("IPPS not present on this machine")
  workspace_info = {"os": platform.system().lower(), "workspace": "e:/Dev/Sample", "git_root": "e:/Dev/Sample"}
  first_load = build_system_prompt(load_prompt_systems([IPPS_PATH]), workspace_info)
  second_load = build_system_prompt(load_prompt_systems([IPPS_PATH]), workspace_info)
  assert first_load == second_load
  assert len(first_load) > 30000  # 8 rules with real content injected


# IG-02: no tool executes without a session JSONL entry recording its arguments and result
def test_ig02_jsonl_completeness_audit(tmp_path):
  proc = build_scenario_proc(tmp_path, "ig02", None, policy="turbo")
  (proc.workspace / "audit.txt").write_text("audit body", encoding="utf-8")
  turns = [
    {"text": "auditing", "tool_calls": [
      {"name": "read_file", "args": {"file_path": str(proc.workspace / "audit.txt")}},
      {"name": "run_command", "args": {"CommandLine": "Write-Output audited", "SafeToAutoRun": True, "Blocking": True}},
      {"name": "todo_list", "args": {"todos": [{"id": "1", "content": "a", "status": "pending", "priority": "low"}]}},
    ], "usage": {"input": 500, "output": 30}},
    {"text": "audit complete", "usage": {"input": 700, "output": 10}},
  ]
  proc.script_path = write_script(proc.workspace / "script.jsonl", turns)
  result = proc.run_headless("go")
  assert result.returncode == 0
  session_events = proc.read_session_events()
  requested = {event.id: event for event in session_events if event.type == "tool_call_requested"}
  finished = {event.id: event for event in session_events if event.type == "tool_call_finished"}
  assert len(requested) == 3 and set(requested) == set(finished)
  for call_id, request_event in requested.items():
    assert request_event.args, f"arguments missing in JSONL for {call_id}"
    assert finished[call_id].result, f"result missing in JSONL for {call_id}"
  command_result = [event for event in finished.values() if "audited" in event.result]
  assert command_result, "run_command output not recorded in the session log"
