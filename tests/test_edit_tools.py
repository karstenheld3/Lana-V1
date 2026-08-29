"""TK-011: edit tools with ReadLedger gate (IP01 TC-19..22)."""
import os, time
import pytest
from lana.tools import ToolContext, ToolError
from lana.tools.edit_tools import execute_edit, execute_multi_edit, execute_write_to_file
from lana.tools.file_tools import execute_read_file


@pytest.fixture
def context(tmp_path):
  return ToolContext(workspace=tmp_path)


def make_read_file(tmp_path, context, name="target.txt", content="alpha\nbeta\ngamma\n"):
  target = tmp_path / name
  target.write_text(content, encoding="utf-8")
  execute_read_file({"file_path": str(target)}, context)
  return target


# TC-19: edit without read (EC-07) -> gate error naming the required action
def test_tc19_edit_without_read_gate(tmp_path, context):
  target = tmp_path / "unread.txt"
  target.write_text("alpha", encoding="utf-8")
  with pytest.raises(ToolError) as error: execute_edit({"file_path": str(target), "old_string": "alpha", "new_string": "beta"}, context)
  assert "read_file" in str(error.value) and "not read" in str(error.value)


# TC-20: external modification (EC-08) -> gate error; self-edit then edit again -> passes (RF-10)
def test_tc20_external_modification_gate(tmp_path, context):
  target = make_read_file(tmp_path, context)
  future = time.time() + 10
  os.utime(target, (future, future))  # simulate external modification
  with pytest.raises(ToolError) as error: execute_edit({"file_path": str(target), "old_string": "alpha", "new_string": "ALPHA"}, context)
  assert "modified externally" in str(error.value)
  execute_read_file({"file_path": str(target)}, context)  # re-read clears the gate
  execute_edit({"file_path": str(target), "old_string": "alpha", "new_string": "ALPHA"}, context)
  execute_edit({"file_path": str(target), "old_string": "beta", "new_string": "BETA"}, context)  # self-edit updated ledger -> passes
  assert target.read_text(encoding="utf-8") == "ALPHA\nBETA\ngamma\n"


def test_edit_uniqueness_and_noop(tmp_path, context):
  target = make_read_file(tmp_path, context, content="dup\ndup\nunique\n")
  with pytest.raises(ToolError) as error: execute_edit({"file_path": str(target), "old_string": "dup", "new_string": "x"}, context)
  assert "2 times" in str(error.value)  # EC-09 occurrence count
  execute_edit({"file_path": str(target), "old_string": "dup", "new_string": "x", "replace_all": True}, context)
  assert target.read_text(encoding="utf-8") == "x\nx\nunique\n"
  with pytest.raises(ToolError): execute_edit({"file_path": str(target), "old_string": "unique", "new_string": "unique"}, context)
  with pytest.raises(ToolError) as error: execute_edit({"file_path": str(target), "old_string": "absent", "new_string": "y"}, context)
  assert "not found" in str(error.value)


# TC-21: multi_edit atomicity - failing edit 3 of 3 leaves file untouched
def test_tc21_multi_edit_atomicity(tmp_path, context):
  target = make_read_file(tmp_path, context)
  original = target.read_text(encoding="utf-8")
  edits = [{"old_string": "alpha", "new_string": "A"}, {"old_string": "beta", "new_string": "B"}, {"old_string": "MISSING", "new_string": "C"}]
  with pytest.raises(ToolError) as error: execute_multi_edit({"file_path": str(target), "edits": edits}, context)
  assert "edit 3 of 3" in str(error.value) and "no changes were applied" in str(error.value)
  assert target.read_text(encoding="utf-8") == original
  good_edits = [{"old_string": "alpha", "new_string": "A"}, {"old_string": "beta", "new_string": "B"}]
  result = execute_multi_edit({"file_path": str(target), "edits": good_edits}, context)
  assert "2 edits applied" in result and target.read_text(encoding="utf-8") == "A\nB\ngamma\n"


# TC-22: write_to_file on existing file -> error
def test_tc22_write_to_file_create_only(tmp_path, context):
  target = tmp_path / "brand" / "new.txt"
  result = execute_write_to_file({"TargetFile": str(target), "CodeContent": "hello", "EmptyFile": False}, context)
  assert target.read_text(encoding="utf-8") == "hello" and "5 chars" in result
  with pytest.raises(ToolError) as error: execute_write_to_file({"TargetFile": str(target), "CodeContent": "again", "EmptyFile": False}, context)
  assert "already exists" in str(error.value)
  empty_target = tmp_path / "empty.txt"
  execute_write_to_file({"TargetFile": str(empty_target), "CodeContent": "ignored", "EmptyFile": True}, context)
  assert empty_target.read_text(encoding="utf-8") == ""


def test_write_to_file_enables_immediate_edit(tmp_path, context):
  target = tmp_path / "written.txt"
  execute_write_to_file({"TargetFile": str(target), "CodeContent": "start", "EmptyFile": False}, context)
  execute_edit({"file_path": str(target), "old_string": "start", "new_string": "changed"}, context)  # ledger updated by write (FR-11)
  assert target.read_text(encoding="utf-8") == "changed"
