"""TK-032: offline end-to-end - fake-adapter prime-like flow, transcript per SPEC section 12 (IP01 TC-46)."""
import re
from tests.harness import assert_no_secret_leak
from tests.scenario_utils import build_scenario_proc
from tests.scripted_adapter import write_script


# TC-46: full workflow flow: expansion -> read -> edit round trip -> todo -> final text; transcript format checked
def test_tc46_offline_e2e_prime_like_flow(tmp_path):
  proc = build_scenario_proc(tmp_path, "e2e", None, policy="turbo")
  notes = proc.workspace / "NOTES.md"
  notes.write_text("# Notes\n\nstatus: draft\n", encoding="utf-8")
  turns = [
    {"text": "Priming the workspace.", "thinking": "planning the flow", "tool_calls": [
      {"name": "read_file", "args": {"file_path": str(notes)}},
      {"name": "todo_list", "args": {"todos": [{"id": "1", "content": "update status", "status": "in_progress", "priority": "high"}]}},
    ], "usage": {"input": 1200, "output": 60}},
    {"text": "Updating the notes.", "tool_calls": [
      {"name": "edit", "args": {"file_path": str(notes), "old_string": "status: draft", "new_string": "status: primed"}},
      {"name": "run_command", "args": {"CommandLine": "Write-Output primed-ok", "SafeToAutoRun": True, "Blocking": True}},
    ], "usage": {"input": 1800, "output": 50}},
    {"text": "Prime flow finished. Status set to primed.", "usage": {"input": 2200, "output": 30}},
  ]
  proc.script_path = write_script(proc.workspace / "script.jsonl", turns)
  result = proc.run_headless("/prime-like", output_format="text")
  assert result.returncode == 0, result.stdout + result.stderr
  transcript = result.stdout
  # SPEC section 12 transcript essentials
  assert re.search(r"Lana MVP-1 \| generator: claude-sonnet-4-5 \(medium\)", transcript)
  assert "3 rules" in transcript and "3 workflows" in transcript
  assert "[tool] read_file" in transcript and "[tool] edit" in transcript
  assert "[tool] run_command 'Write-Output primed-ok'... (policy: turbo)" in transcript
  assert transcript.count("OK.") >= 4
  assert re.search(r"Turn: in=1200 \(cache 0\) out=60 \| \$[\d.]+ \| session \$[\d.]+", transcript)
  assert "Prime flow finished." in transcript
  # File state proves the edit round trip actually happened through the real executable
  assert notes.read_text(encoding="utf-8") == "# Notes\n\nstatus: primed\n"
  assert_no_secret_leak([transcript], ["sk-test-openai", "sk-test-anthropic"])


def test_tc46b_full_suite_event_log_matches_stdout(tmp_path):
  proc = build_scenario_proc(tmp_path, "e2e_jsonl", None, policy="turbo")
  turns = [{"text": "only text", "usage": {"input": 100, "output": 5}}]
  proc.script_path = write_script(proc.workspace / "script.jsonl", turns)
  result = proc.run_headless("hello", output_format="jsonl")
  stdout_types = [event.type for event in proc.events(result)]
  session_types = [event.type for event in proc.read_session_events()]
  assert stdout_types == session_types  # one serializer, two sinks (IS-21)
