"""TK-030: TP01 conversation scenarios TC-01..03 - real executable, scripted adapter."""
import json
from tests.harness import assert_event_order, assert_no_secret_leak
from tests.scenario_utils import build_scenario_proc

TODO_A = [{"id": "1", "content": "first state", "status": "pending", "priority": "high"}]
TODO_B = [{"id": "1", "content": "first state", "status": "completed", "priority": "high"}, {"id": "2", "content": "second state", "status": "in_progress", "priority": "medium"}]


# TP01-TC-01: workflow round trip - expansion, 2 tool calls, created file exists, exit 0 (FR-04, FR-05, IG-02)
def test_tp01_tc01_workflow_round_trip(tmp_path):
  proc = build_scenario_proc(tmp_path, "tc01", None)
  (proc.workspace / "input.md").write_text("input body", encoding="utf-8")
  turns = [
    {"text": "Executing workflow.", "tool_calls": [
      {"name": "read_file", "args": {"file_path": str(proc.workspace / "input.md")}},
      {"name": "write_to_file", "args": {"TargetFile": str(proc.workspace / "output.md"), "CodeContent": "workflow output", "EmptyFile": False}},
    ], "usage": {"input": 800, "output": 40}},
    {"text": "Workflow complete.", "usage": {"input": 1000, "output": 20}},
  ]
  from tests.scripted_adapter import write_script
  proc.script_path = write_script(proc.workspace / "script.jsonl", turns)
  result = proc.run_headless("/tooluse")
  assert result.returncode == 0, result.stdout + result.stderr
  events = proc.events()
  user_message = [event for event in events if event.type == "user_message"][0]
  assert user_message.expanded_workflow == "tooluse"
  assert_event_order(events, ["user_message", "turn_started", "tool_call_requested", "tool_call_finished", "tool_call_requested", "tool_call_finished", "turn_finished", "turn_started", "turn_finished"])
  assert (proc.workspace / "output.md").read_text(encoding="utf-8") == "workflow output"
  session_types = [event.type for event in proc.read_session_events()]
  assert session_types == [event.type for event in events]  # IG-02: stream == session log
  assert_no_secret_leak([result.stdout], ["sk-test-openai", "sk-test-anthropic"])


# TP01-TC-02: multi-turn piped session -> 3 turn_finished; --resume + /cost replays state (FR-08, IG-06)
def test_tp01_tc02_multi_turn_piped_and_resume(tmp_path):
  turns = [{"text": f"answer {index}", "usage": {"input": 100 * index, "output": 10}} for index in (1, 2, 3)]
  proc = build_scenario_proc(tmp_path, "tc02", turns)
  result = proc.run_piped("first\nsecond\nthird\n/exit\n")
  assert result.returncode == 0, result.stdout + result.stderr
  session_events = proc.read_session_events()
  finished = [event for event in session_events if event.type == "turn_finished"]
  assert len(finished) == 3
  session_file = proc.session_files()[0]
  from tests.scripted_adapter import write_script
  proc.script_path = write_script(proc.workspace / "script2.jsonl", [{"text": "resumed answer"}])
  resumed = proc.run_piped("/cost\n/exit\n", extra_args=["--resume", str(session_file)])
  assert resumed.returncode == 0, resumed.stdout + resumed.stderr
  assert "Resumed session" in resumed.stdout and "6 messages" in resumed.stdout  # 3 user + 3 assistant (IG-06)
  assert "generator: 3 turns" in resumed.stdout  # /cost totals rebuilt from the log
  assert_no_secret_leak([result.stdout, resumed.stdout], ["sk-test-openai", "sk-test-anthropic"])


# TP01-TC-03: todo lifecycle - second todo state survives compaction byte-identically (FR-07, IG-04)
def test_tp01_tc03_todo_survives_compaction(tmp_path):
  turns = [
    {"text": "planning", "tool_calls": [{"name": "todo_list", "args": {"todos": TODO_A}}], "usage": {"input": 300, "output": 20}},
    {"text": "updating", "tool_calls": [{"name": "todo_list", "args": {"todos": TODO_B}}], "usage": {"input": 600, "output": 20}},
    {"text": "big turn done", "usage": {"input": 5000, "output": 100}},
    {"text": "# Objective:\nDemo.\n# Session Summary:\nWorked.\n# Code Interaction Summary:\nTools."},
  ]
  # FR-07 per-turn semantics: 4000 keeps the two small todo turns uncompacted, fires after the big turn
  proc = build_scenario_proc(tmp_path, "tc03", turns, lana_overrides={"compaction_threshold_max_tokens": 4000})
  result = proc.run_headless("/prime-like")
  assert result.returncode == 0, result.stdout + result.stderr
  checkpoints = [event for event in proc.events() if event.type == "checkpoint_created"]
  assert len(checkpoints) == 1
  expected_json = json.dumps(TODO_B, indent=2, ensure_ascii=False, sort_keys=True)
  assert expected_json in checkpoints[0].text  # byte-identical second state (IG-04)
  assert "first state" in checkpoints[0].text
