"""TK-013: run_command and command_status executors (IS-09)."""
import pytest
from lana.tools import ToolContext, ToolError
from lana.tools.shell_tools import execute_command_status, execute_run_command


@pytest.fixture
def context(tmp_path):
  return ToolContext(workspace=tmp_path)


def test_blocking_command_output_and_exit_code(context):
  result = execute_run_command({"CommandLine": "Write-Output hello", "Blocking": True}, context)
  assert "Exit code 0" in result and "hello" in result


def test_blocking_failure_exit_code(context):
  result = execute_run_command({"CommandLine": "exit 3", "Blocking": True}, context)
  assert "Exit code 3" in result


def test_cwd_respected(tmp_path, context):
  sub = tmp_path / "subdir"
  sub.mkdir()
  result = execute_run_command({"CommandLine": "(Get-Location).Path", "Blocking": True, "Cwd": str(sub)}, context)
  assert "subdir" in result


def test_background_and_command_status(context):
  result = execute_run_command({"CommandLine": "Start-Sleep -Milliseconds 500; Write-Output done-marker", "Blocking": False}, context)
  assert "background" in result and "cmd_" in result
  command_id = result.split("ID ")[1].split(".")[0].split()[0]
  status = execute_command_status({"CommandId": command_id, "OutputCharacterCount": 1000, "WaitDurationSeconds": 5}, context)
  assert "Status: done" in status and "done-marker" in status and "Exit code 0" in status


def test_wait_ms_before_async_fast_command(context):
  result = execute_run_command({"CommandLine": "Write-Output quick", "Blocking": False, "WaitMsBeforeAsync": 4000}, context)
  assert "Exit code 0" in result and "quick" in result  # finished within the wait window


def test_command_status_unknown_id(context):
  with pytest.raises(ToolError) as error: execute_command_status({"CommandId": "cmd_nope", "OutputCharacterCount": 100}, context)
  assert "cmd_nope" in str(error.value)


def test_command_status_output_character_count(context):
  execute_run_command({"CommandLine": "Write-Output ('X' * 500)", "Blocking": True}, context)  # blocking result not stored
  start = execute_run_command({"CommandLine": "Start-Sleep -Milliseconds 100; Write-Output ('Y' * 500)", "Blocking": False}, context)
  command_id = start.split("ID ")[1].split(".")[0].split()[0]
  status = execute_command_status({"CommandId": command_id, "OutputCharacterCount": 50, "WaitDurationSeconds": 5}, context)
  output_part = status.split("Output:\n", 1)[1]
  assert len(output_part) <= 50
