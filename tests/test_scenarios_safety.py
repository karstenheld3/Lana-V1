"""TK-030: TP01 safety scenarios TC-04..05 - denials end-to-end (FR-12, FR-14, IG-03)."""
from tests.harness import assert_no_secret_leak
from tests.scenario_utils import build_scenario_proc
from tests.scripted_adapter import write_script


# TP01-TC-04: destructive command blocked end-to-end under --policy auto headless
def test_tp01_tc04_destructive_command_blocked(tmp_path):
  proc = build_scenario_proc(tmp_path, "tc04", None, policy="auto")
  victim = proc.workspace / "victim.txt"
  victim.write_text("precious data", encoding="utf-8")
  turns = [
    {"text": "removing", "tool_calls": [{"name": "run_command", "args": {"CommandLine": f"Remove-Item {victim}", "SafeToAutoRun": True}}], "usage": {"input": 200, "output": 10}},
    {"text": "continuing after denial", "usage": {"input": 300, "output": 10}},
  ]
  proc.script_path = write_script(proc.workspace / "script.jsonl", turns)
  result = proc.run_headless("delete it")
  assert result.returncode == 0, result.stdout + result.stderr
  events = proc.events()
  denial = [event for event in events if event.type == "tool_call_finished"][0]
  assert denial.status == "error" and "approval denied (non-interactive session)" in denial.result
  assert victim.read_text(encoding="utf-8") == "precious data"  # nothing deleted (IG-03)
  assert any(event.type == "text_delta" and "continuing after denial" in event.text for event in events)
  assert_no_secret_leak([result.stdout], ["sk-test-openai", "sk-test-anthropic"])


# TP01-TC-05: out-of-workspace write blocked, target absent (FR-12)
def test_tp01_tc05_out_of_workspace_write_blocked(tmp_path):
  proc = build_scenario_proc(tmp_path, "tc05", None, policy="turbo")
  outside_target = tmp_path / "outside_workspace.txt"
  turns = [
    {"text": "writing outside", "tool_calls": [{"name": "write_to_file", "args": {"TargetFile": str(outside_target), "CodeContent": "escape attempt", "EmptyFile": False}}], "usage": {"input": 200, "output": 10}},
    {"text": "done", "usage": {"input": 300, "output": 10}},
  ]
  proc.script_path = write_script(proc.workspace / "script.jsonl", turns)
  result = proc.run_headless("write it")
  assert result.returncode == 0, result.stdout + result.stderr
  events = proc.events()
  denial = [event for event in events if event.type == "tool_call_finished"][0]
  assert denial.status == "error" and "approval denied" in denial.result
  approval = [event for event in events if event.type == "approval_required"][0]
  assert approval.action == "write_outside_workspace" and approval.approved is False
  assert not outside_target.exists()  # target absent


def test_inside_workspace_write_needs_no_approval(tmp_path):
  proc = build_scenario_proc(tmp_path, "tc05b", None, policy="turbo")
  inside_target = proc.workspace / "inside.txt"
  turns = [
    {"text": "writing inside", "tool_calls": [{"name": "write_to_file", "args": {"TargetFile": str(inside_target), "CodeContent": "fine", "EmptyFile": False}}], "usage": {"input": 200, "output": 10}},
    {"text": "done", "usage": {"input": 300, "output": 10}},
  ]
  proc.script_path = write_script(proc.workspace / "script.jsonl", turns)
  result = proc.run_headless("write it")
  assert result.returncode == 0
  assert inside_target.read_text(encoding="utf-8") == "fine"
  assert not [event for event in proc.events() if event.type == "approval_required"]
