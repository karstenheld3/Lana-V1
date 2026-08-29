"""TK-025: LanaProc harness selftest (IP01 TC-53..54)."""
import time
import pytest
from tests.conftest import write_config_dir, write_prompt_system
from tests.harness import LanaProc, assert_event_order
from tests.scripted_adapter import write_script

TURNS = [
  {"text": "step one", "tool_calls": [{"name": "todo_list", "args": {"todos": [{"id": "1", "content": "x", "status": "pending", "priority": "low"}]}}], "usage": {"input": 100, "output": 10}},
  {"text": "all done", "usage": {"input": 150, "output": 8}},
]


@pytest.fixture
def proc_factory(tmp_path):
  def make(name: str) -> LanaProc:
    workspace = tmp_path / name
    workspace.mkdir()
    system = write_prompt_system(workspace / "ps", rules={"main.md": "Rule"}, workflows={"prime": "---\ndescription: Prime\n---\nbody"})
    config_dir = write_config_dir(workspace, lana_overrides={"prompt_system_paths": [str(system).replace("\\", "/")]}, key_lines=None)
    script = write_script(workspace / "script.jsonl", TURNS)
    return LanaProc(workspace, config_path=config_dir / "lana-config.json", script_path=script)
  return make


def normalized_signature(events) -> list:
  signature = []
  for event in events:
    payload = event.model_dump(exclude={"ts"})
    signature.append(payload)
  return signature


# TC-53: same script run twice -> byte-identical event sequences modulo timestamps/ids
def test_tc53_determinism_across_runs(proc_factory):
  first_proc, second_proc = proc_factory("run1"), proc_factory("run2")
  first = first_proc.run_headless("same prompt")
  second = second_proc.run_headless("same prompt")
  assert first.returncode == second.returncode == 0
  first_events, second_events = normalized_signature(first_proc.events(first)), normalized_signature(second_proc.events(second))
  assert first_events == second_events


# TC-54: tail_session observes tool_call_finished in the flushed file (FR-08 flush contract)
def test_tc54_tail_session_flush_contract(proc_factory):
  proc = proc_factory("tail")
  result = proc.run_headless("go")
  assert result.returncode == 0, result.stderr
  observed = proc.tail_session(lambda event: event.type == "tool_call_finished", timeout=5)
  assert observed is not None and observed.status == "ok"
  event_types = [event.type for event in proc.read_session_events()]
  assert_event_order(proc.read_session_events(), ["user_message", "turn_started", "tool_call_requested", "tool_call_finished", "turn_finished"])
  assert "error" not in event_types


def test_session_file_created_per_run(proc_factory):
  proc = proc_factory("files")
  proc.run_headless("go")
  assert len(proc.session_files()) == 1
