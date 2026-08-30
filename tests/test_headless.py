"""TK-024: headless mode, exit codes, non-terminal fallback (IP01 TC-50..52, TC-55; FR-14)."""
import json
import re
import pytest
from lana.events import from_jsonl
from tests.conftest import write_config_dir, write_prompt_system
from tests.harness import LanaProc
from tests.scripted_adapter import write_script


@pytest.fixture
def cli_workspace(tmp_path):
  workspace = tmp_path / "cli_ws"
  workspace.mkdir()
  system = write_prompt_system(workspace / "ps", rules={"main.md": "Rule body"}, workflows={"help2": "---\ndescription: Help twin\n---\nbody", "prime": "---\ndescription: Prime\n---\nPrime body"})
  config_dir = write_config_dir(workspace, lana_overrides={"agent_folder": str(system).replace("\\", "/")}, key_lines=None)
  return workspace, config_dir / "lana-config.json"


def make_proc(cli_workspace, turns, **kwargs):
  workspace, config_path = cli_workspace
  script = write_script(workspace / "script.jsonl", turns) if turns is not None else None
  return LanaProc(workspace, config_path=config_path, script_path=script, **kwargs)


# TC-50: lana -p "hello" with 1-turn script -> final text on stdout, exit 0
def test_tc50_headless_text_output(cli_workspace):
  proc = make_proc(cli_workspace, [{"text": "scripted reply", "usage": {"input": 10, "output": 5}}])
  result = proc.run_headless("hello", output_format="text")
  assert result.returncode == 0, result.stderr
  assert "scripted reply" in result.stdout
  assert "SCRIPTED" in result.stdout  # banner marks scripted sessions (FR-14)


def test_tc50b_headless_jsonl_stream(cli_workspace):
  proc = make_proc(cli_workspace, [{"text": "jsonl reply", "usage": {"input": 10, "output": 5}}])
  result = proc.run_headless("hello", output_format="jsonl")
  assert result.returncode == 0, result.stderr
  types = [event.type for event in proc.events()]
  assert types[0] == "user_message" and "turn_finished" in types and "text_delta" in types


# TC-51: missing config -> stderr names file and fix, exit 2
def test_tc51_missing_config_exit_2(tmp_path):
  workspace = tmp_path / "no_config"
  workspace.mkdir()
  proc = LanaProc(workspace, config_path=workspace / "config" / "lana-config.json", script_path=None)
  script_free_env_result = proc.run_headless("hello", output_format="text")
  assert script_free_env_result.returncode == 2
  assert "lana-config.json" in script_free_env_result.stderr and "HINT:" in script_free_env_result.stderr


# TC-52: denylisted run_command headless -> denial in result, loop continues, exit 0
def test_tc52_denylisted_command_denied_headless(cli_workspace):
  turns = [
    {"text": "trying", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "Remove-Item x", "SafeToAutoRun": True}}]},
    {"text": "continued after denial", "usage": {"input": 10, "output": 5}},
  ]
  proc = make_proc(cli_workspace, turns, policy="turbo")
  result = proc.run_headless("go", output_format="jsonl")
  assert result.returncode == 0, result.stderr
  events = proc.events()
  denial = [event for event in events if event.type == "tool_call_finished"][0]
  assert "approval denied (non-interactive session)" in denial.result
  assert any(event.type == "approval_required" and event.approved is False for event in events)
  assert any(event.type == "text_delta" and "continued after denial" in event.text for event in events)


def test_exit_code_3_on_provider_error(cli_workspace):
  proc = make_proc(cli_workspace, [{"error": "simulated outage"}])
  result = proc.run_headless("go")
  assert result.returncode == 3


def test_exit_code_4_on_limit_stop(cli_workspace):
  workspace, config_path = cli_workspace
  content = json.loads(config_path.read_text(encoding="utf-8"))
  content["max_tool_calls_per_prompt"] = 2
  limited = workspace / "config" / "lana-config-limited.json"
  limited.write_text(json.dumps(content), encoding="utf-8")
  calls = [{"name": "list_dir", "args": {"DirectoryPath": str(workspace)}}] * 3
  proc = make_proc(cli_workspace, [{"text": "burst", "tool_calls": calls}, {"text": "never"}])
  proc.config_path = limited
  result = proc.run_headless("go")
  assert result.returncode == 4


# Improve run 3: jsonl stdout purity - ONLY serialized AgentEvents on stdout, diagnostics on stderr (strict-consumer contract)
def test_jsonl_stdout_purity(cli_workspace):
  proc = make_proc(cli_workspace, [{"text": "pure stream", "usage": {"input": 10, "output": 5}}])
  result = proc.run_headless("hello", output_format="jsonl")
  assert result.returncode == 0, result.stdout + result.stderr
  stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
  assert stdout_lines, "expected events on stdout"
  for line in stdout_lines:
    from_jsonl(line)  # every stdout line MUST parse as an AgentEvent - raises otherwise
  assert re.search(r"Lana \d+\.\d+\.\d+", result.stderr) and "SCRIPTED" in result.stderr  # banner rerouted to stderr
  assert not re.search(r"Lana \d+\.\d+\.\d+", result.stdout)


def test_jsonl_unknown_workflow_message_on_stderr(cli_workspace):
  proc = make_proc(cli_workspace, [])
  result = proc.run_headless("/nonexistent-workflow", output_format="jsonl")
  assert result.returncode == 0
  assert "Unknown workflow" in result.stderr and "Unknown workflow" not in result.stdout


# Gap 09 regression: built-ins dispatched in headless -p mode, never sent to the Generator
def test_headless_builtins(cli_workspace):
  proc = make_proc(cli_workspace, [])
  help_result = proc.run_headless("/help", output_format="text")
  assert help_result.returncode == 0 and "/prime: Prime" in help_result.stdout
  cost_result = proc.run_headless("/cost", output_format="text")
  assert cost_result.returncode == 0 and "No usage recorded" in cost_result.stdout
  assert "Unknown workflow" not in help_result.stdout + cost_result.stdout


# BG-0005 regression: --resume with a missing file -> self-contained error, exit 2, never a traceback (IG-05, FR-14)
def test_bg0005_resume_missing_file_exit_2(cli_workspace):
  proc = make_proc(cli_workspace, [{"text": "never reached"}])
  result = proc.run_headless("hi", extra_args=["--resume", "no-such-session.jsonl"])
  assert result.returncode == 2
  assert "no-such-session.jsonl" in result.stderr and "HINT:" in result.stderr
  assert "Traceback" not in result.stderr


# Regression (eval suite 02-T02 finding): non-ASCII in scripted text/tool results must not crash jsonl output on cp1252 pipes
def test_jsonl_utf8_content_survives_piped_stdout(cli_workspace):
  proc = make_proc(cli_workspace, [{"text": "status: \u2705 done, \u274c open, umlaut \u00e4", "usage": {"input": 10, "output": 5}}])
  result = proc.run_headless("report status", output_format="jsonl")
  assert result.returncode == 0, result.stderr
  assert any(event.type == "text_delta" and "\u2705" in event.text for event in proc.events())


# TC-55: piped stdin session -> workflow list printed, clean exit (non-terminal fallback)
def test_tc55_piped_stdin_help(cli_workspace):
  proc = make_proc(cli_workspace, [])
  result = proc.run_piped("/help\n/exit\n")
  assert result.returncode == 0, result.stderr
  assert "/prime: Prime" in result.stdout and "Built-ins:" in result.stdout
