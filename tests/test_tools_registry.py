"""TK-009: registry dispatch, validation, cap_result (IS-06, EC-04/22/23)."""
import pytest
from lana.tools import ToolContext, ToolError, ToolRegistry, cap_result


@pytest.fixture
def registry():
  reg = ToolRegistry(os_name="windows", shell="pwsh")
  reg.register("read_file", lambda args, context: f"content of {args['file_path']}")
  reg.register("todo_list", lambda args, context: "Todo list updated:")
  return reg


@pytest.fixture
def context(tmp_path):
  return ToolContext(workspace=tmp_path, tool_result_max_chars=100)


def test_dispatch_by_name(registry, context):
  assert registry.dispatch("read_file", {"file_path": "x.md"}, context) == "content of x.md"


def test_unknown_tool_lists_available(registry, context):
  with pytest.raises(ToolError) as error: registry.dispatch("no_such_tool", {}, context)
  assert "read_file" in str(error.value) and "Unknown tool" in str(error.value)


def test_invalid_args_schema_message(registry, context):
  with pytest.raises(ToolError) as error: registry.dispatch("read_file", {}, context)
  assert "file_path" in str(error.value)
  with pytest.raises(ToolError) as error: registry.dispatch("read_file", {"file_path": "x", "bogus": 1}, context)
  assert "bogus" in str(error.value)
  with pytest.raises(ToolError) as error: registry.dispatch("read_file", {"file_path": 42}, context)
  assert "string" in str(error.value)


def test_nested_array_item_validation(registry, context):
  with pytest.raises(ToolError) as error: registry.dispatch("todo_list", {"todos": [{"id": "1", "content": "x", "status": "bogus", "priority": "high"}]}, context)
  assert "status" in str(error.value)


def test_result_cap_applied(registry, context):
  registry.register("list_dir", lambda args, context_: "Y" * 500)
  result = registry.dispatch("list_dir", {"DirectoryPath": "x"}, context)
  assert result.endswith("<truncated 400 chars>") and result.startswith("Y" * 100)


def test_cap_result_exact_marker():
  assert cap_result("A" * 60, 50) == "A" * 50 + "\n<truncated 10 chars>"
  assert cap_result("short", 50) == "short"


def test_run_command_substitution():
  registry = ToolRegistry(os_name="windows", shell="pwsh")
  registry.register("run_command", lambda args, context: "")
  description = registry.definitions["run_command"]["description"]
  assert "Operating System: windows. Shell: pwsh." in description and "{OS}" not in description
