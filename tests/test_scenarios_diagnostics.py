"""TK-031: TP01 scenarios TC-08..10 - real prompt system startup, diagnostics, exit codes."""
import re
from pathlib import Path
import pytest
from tests.conftest import write_config_dir
from tests.harness import LanaProc, assert_no_secret_leak
from tests.scenario_utils import build_scenario_proc
from tests.scripted_adapter import write_script

DEVSYSTEM_PATH = Path("e:/Dev/IPPS/DevSystemV4.2")


# TP01-TC-08: DevSystemV4.2 startup + /help via pipe -> 8/46/21, prime + verify listed, load < 2 s (FR-02, NFR-03)
def test_tp01_tc08_devsystem_startup(tmp_path):
  if not DEVSYSTEM_PATH.is_dir(): pytest.skip("DevSystemV4.2 not present on this machine")
  workspace = tmp_path / "tc08"
  workspace.mkdir()
  config_dir = write_config_dir(workspace, lana_overrides={"prompt_system_paths": [str(DEVSYSTEM_PATH)]}, key_lines=None)
  proc = LanaProc(workspace, config_path=config_dir / "lana-config.json", script_path=write_script(workspace / "s.jsonl", []))
  result = proc.run_piped("/help\n/exit\n")
  assert result.returncode == 0, result.stdout + result.stderr
  # Counts from the filesystem - DevSystemV4.2 evolves (8/46/21 at SPEC analysis; growing since)
  rule_count = len(list((DEVSYSTEM_PATH / "rules").glob("*.md")))
  workflow_count = len(list((DEVSYSTEM_PATH / "workflows").glob("*.md")))
  skill_count = len(list((DEVSYSTEM_PATH / "skills").glob("*/SKILL.md")))
  assert re.search(rf"{rule_count} rules \(\d+ injected.*\), {workflow_count} workflows, {skill_count} skills\.", result.stdout)
  assert "/prime:" in result.stdout and "/verify:" in result.stdout
  load_seconds = float(re.search(r"Loaded in ([\d.]+) secs", result.stdout).group(1))
  assert load_seconds < 2.0


# TP01-TC-09: --debug run -> logs dir exists, no secret leak anywhere, events carry timestamps (NFR-01, NFR-04)
def test_tp01_tc09_debug_and_no_secret_leak(tmp_path, monkeypatch):
  proc = build_scenario_proc(tmp_path, "tc09", [{"text": "debug run", "usage": {"input": 100, "output": 10}}])
  fake_keys = ["sk-fake-openai-value-12345", "sk-fake-anthropic-value-67890"]
  env_result = proc.run_headless("go", extra_args=["--debug"])
  assert env_result.returncode == 0, env_result.stdout + env_result.stderr
  logs_dir = proc.workspace / ".lana" / "logs"
  assert logs_dir.is_dir()  # NFR-04 debug target created
  all_outputs = [env_result.stdout, env_result.stderr]
  for session_file in proc.session_files(): all_outputs.append(session_file.read_text(encoding="utf-8"))
  for log_file in logs_dir.glob("*.json"): all_outputs.append(log_file.read_text(encoding="utf-8"))
  assert_no_secret_leak(all_outputs, fake_keys + ["sk-test-openai", "sk-test-anthropic"])
  for event in proc.events(env_result):
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", event.ts)  # NFR-04 timestamps


# TP01-TC-10: exit code semantics - provider error -> 3; limit without continue -> 4 (FR-14)
def test_tp01_tc10_exit_codes(tmp_path):
  error_proc = build_scenario_proc(tmp_path, "tc10a", [{"error": "provider 500: upstream unavailable"}])
  error_result = error_proc.run_headless("go")
  assert error_result.returncode == 3
  assert "upstream unavailable" in error_result.stdout + error_result.stderr
  limit_proc = build_scenario_proc(tmp_path, "tc10b", None, lana_overrides={"max_tool_calls_per_prompt": 2, "auto_continue": False})
  calls = [{"name": "list_dir", "args": {"DirectoryPath": str(limit_proc.workspace)}}] * 3
  limit_proc.script_path = write_script(limit_proc.workspace / "script.jsonl", [{"text": "burst", "tool_calls": calls}, {"text": "never"}])
  limit_result = limit_proc.run_headless("go")
  assert limit_result.returncode == 4
