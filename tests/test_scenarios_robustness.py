"""TK-031: TP01 robustness scenarios TC-06..07 - kill/resume and output cap (NFR-02, EC-21, RF-03)."""
from lana.session import resume
from tests.scenario_utils import build_scenario_proc
from tests.scripted_adapter import write_script


# TP01-TC-06: kill mid-script (after 2nd tool_call_finished via tail), then --resume -> prior events intact (NFR-02)
def test_tp01_tc06_kill_and_resume(tmp_path):
  proc = build_scenario_proc(tmp_path, "tc06", None, policy="turbo")
  turns = [
    {"text": "working", "tool_calls": [
      {"name": "list_dir", "args": {"DirectoryPath": str(proc.workspace)}},
      {"name": "list_dir", "args": {"DirectoryPath": str(proc.workspace)}},
      {"name": "run_command", "args": {"CommandLine": "Start-Sleep -Seconds 30", "SafeToAutoRun": True, "Blocking": True}},
    ], "usage": {"input": 500, "output": 20}},
    {"text": "never reached"},
  ]
  proc.script_path = write_script(proc.workspace / "script.jsonl", turns)
  proc.start_piped()
  proc.send("go")
  seen = {"count": 0}

  def second_finished(event):
    if event.type == "tool_call_finished": seen["count"] += 1; return seen["count"] >= 2
    return False

  observed = proc.tail_session(lambda event: event.type == "tool_call_finished" and second_finished(event), timeout=20)
  assert observed is not None, "second tool_call_finished never appeared in the tailed session file"
  proc.kill()  # hard kill during the sleeping third call
  session_file = proc.session_files()[0]
  state = resume(session_file)
  assert state.skipped_lines <= 1  # EC-21: at most the in-flight line lost
  finished = [event for event in state.events if event.type == "tool_call_finished"]
  assert len(finished) >= 2 and all(event.status == "ok" for event in finished[:2])
  proc.script_path = write_script(proc.workspace / "script2.jsonl", [{"text": "resumed fine", "usage": {"input": 100, "output": 5}}])
  continuation = proc.run_headless("continue", extra_args=["--resume", str(session_file)])
  assert continuation.returncode == 0, continuation.stdout + continuation.stderr
  assert any(event.type == "text_delta" and "resumed fine" in event.text for event in proc.events(continuation))


# TP01-TC-07: oversized tool output capped at 50K with marker; next turn succeeds (FR-04, RF-03)
def test_tp01_tc07_oversized_output_capped(tmp_path):
  proc = build_scenario_proc(tmp_path, "tc07", None, policy="turbo")
  turns = [
    {"text": "big output", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "Write-Output ('X' * 200000)", "SafeToAutoRun": True, "Blocking": True}}], "usage": {"input": 400, "output": 20}},
    {"text": "handled the big output", "usage": {"input": 600, "output": 20}},
  ]
  proc.script_path = write_script(proc.workspace / "script.jsonl", turns)
  result = proc.run_headless("go")
  assert result.returncode == 0, result.stdout + result.stderr
  events = proc.events()
  capped = [event for event in events if event.type == "tool_call_finished"][0]
  assert capped.result_chars <= 50000 + 40  # 50K + marker
  assert "<truncated " in capped.result
  assert any(event.type == "text_delta" and "handled the big output" in event.text for event in events)
