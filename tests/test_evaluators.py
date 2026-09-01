"""Tests for eval suite Tier 2 assert types (LANATEST-SP01 FR-07)."""
import json
from pathlib import Path
import pytest
from evals.suite.runner.evaluators import (
  assert_tool_called, assert_forbidden_tool, assert_read_before_edit,
  assert_forbidden_tool_args, assert_tool_call_count, assert_tool_call_errors,
  evaluate_process, evaluate_structure,
)


# ---- helpers ----

def make_requested(tool: str, args: dict | None = None, id: str = "c1") -> dict:
  return {"type": "tool_call_requested", "tool": tool, "args": args or {}, "id": id}

def make_finished(id: str = "c1", status: str = "ok", result: str = "") -> dict:
  return {"type": "tool_call_finished", "id": id, "status": status, "result": result}

def write_session(workspace: Path, events: list[dict]) -> None:
  sessions_dir = workspace / ".lana-data" / "sessions"
  sessions_dir.mkdir(parents=True, exist_ok=True)
  lines = [json.dumps(e, ensure_ascii=False) for e in events]
  (sessions_dir / "test-session.jsonl").write_text("\n".join(lines), encoding="utf-8")


# ---- assert_tool_called ----

class TestToolCalled:
  def test_min_pass(self):
    events = [make_requested("read_file"), make_requested("read_file"), make_requested("edit")]
    ok, detail = assert_tool_called(events, {"type": "tool_called", "tool": "read_file", "min": 2})
    assert ok
    assert "2 calls" in detail

  def test_min_fail(self):
    events = [make_requested("read_file")]
    ok, _ = assert_tool_called(events, {"type": "tool_called", "tool": "read_file", "min": 3})
    assert not ok

  def test_max_pass(self):
    events = [make_requested("read_file"), make_requested("read_file")]
    ok, detail = assert_tool_called(events, {"type": "tool_called", "tool": "read_file", "min": 1, "max": 3})
    assert ok
    assert "1..3" in detail

  def test_max_fail_over(self):
    events = [make_requested("read_file")] * 5
    ok, _ = assert_tool_called(events, {"type": "tool_called", "tool": "read_file", "min": 1, "max": 3})
    assert not ok

  def test_max_fail_under(self):
    events = []
    ok, _ = assert_tool_called(events, {"type": "tool_called", "tool": "read_file", "min": 1, "max": 3})
    assert not ok

  def test_args_regex_filter(self):
    events = [
      make_requested("read_file", {"file_path": "/ws/NOTES.md"}),
      make_requested("read_file", {"file_path": "/ws/FAILS.md"}),
      make_requested("read_file", {"file_path": "/ws/src/main.py"}),
    ]
    ok, detail = assert_tool_called(events, {"type": "tool_called", "tool": "read_file", "min": 0, "max": 1, "args_regex": "FAILS\\.md"})
    assert ok
    assert "1 call" in detail

  def test_args_regex_with_max_fail(self):
    events = [
      make_requested("read_file", {"file_path": "/ws/FAILS.md"}),
      make_requested("read_file", {"file_path": "/ws/FAILS.md"}),
    ]
    ok, _ = assert_tool_called(events, {"type": "tool_called", "tool": "read_file", "min": 0, "max": 1, "args_regex": "FAILS\\.md"})
    assert not ok

  def test_edit_grouping(self):
    events = [make_requested("edit"), make_requested("multi_edit")]
    ok, _ = assert_tool_called(events, {"type": "tool_called", "tool": "edit", "min": 2})
    assert ok

  def test_default_min_is_one(self):
    events = [make_requested("search_web")]
    ok, _ = assert_tool_called(events, {"type": "tool_called", "tool": "search_web"})
    assert ok


# ---- assert_forbidden_tool_args ----

class TestForbiddenToolArgs:
  def test_pass_no_matching_args(self):
    events = [
      make_requested("read_file", {"file_path": "/ws/.lana/rules/default.md"}),
      make_requested("read_file", {"file_path": "/ws/src/main.py"}),
    ]
    ok, detail = assert_forbidden_tool_args(events, {"type": "forbidden_tool_args", "tool": "read_file", "args_regex": "\\.devin/"})
    assert ok
    assert "never called with forbidden args" in detail

  def test_fail_matching_args(self):
    events = [
      make_requested("read_file", {"file_path": "/ws/.devin/rules/default.md"}),
    ]
    ok, detail = assert_forbidden_tool_args(events, {"type": "forbidden_tool_args", "tool": "read_file", "args_regex": "\\.devin/"})
    assert not ok
    assert "1 time" in detail

  def test_other_tools_not_affected(self):
    events = [
      make_requested("grep_search", {"SearchPath": "/ws/.devin/rules/"}),
      make_requested("read_file", {"file_path": "/ws/src/main.py"}),
    ]
    ok, _ = assert_forbidden_tool_args(events, {"type": "forbidden_tool_args", "tool": "read_file", "args_regex": "\\.devin/"})
    assert ok

  def test_edit_grouping(self):
    events = [make_requested("multi_edit", {"file_path": "/ws/.devin/rules/bad.md"})]
    ok, _ = assert_forbidden_tool_args(events, {"type": "forbidden_tool_args", "tool": "edit", "args_regex": "\\.devin/"})
    assert not ok

  def test_multiple_violations(self):
    events = [
      make_requested("read_file", {"file_path": "/ws/.devin/a.md"}),
      make_requested("read_file", {"file_path": "/ws/.devin/b.md"}),
    ]
    ok, detail = assert_forbidden_tool_args(events, {"type": "forbidden_tool_args", "tool": "read_file", "args_regex": "\\.devin/"})
    assert not ok
    assert "2 times" in detail


# ---- assert_tool_call_count ----

class TestToolCallCount:
  def test_max_pass(self):
    events = [make_requested("read_file"), make_requested("edit"), make_requested("search_web")]
    ok, detail = assert_tool_call_count(events, {"type": "tool_call_count", "max": 5})
    assert ok
    assert "3 total" in detail

  def test_max_fail(self):
    events = [make_requested("read_file")] * 10
    ok, _ = assert_tool_call_count(events, {"type": "tool_call_count", "max": 5})
    assert not ok

  def test_min_only(self):
    events = [make_requested("read_file")] * 3
    ok, _ = assert_tool_call_count(events, {"type": "tool_call_count", "min": 2})
    assert ok

  def test_min_fail(self):
    events = [make_requested("read_file")]
    ok, _ = assert_tool_call_count(events, {"type": "tool_call_count", "min": 5})
    assert not ok

  def test_range(self):
    events = [make_requested("read_file")] * 7
    ok, _ = assert_tool_call_count(events, {"type": "tool_call_count", "min": 5, "max": 10})
    assert ok

  def test_empty_session(self):
    ok, _ = assert_tool_call_count([], {"type": "tool_call_count", "max": 15})
    assert ok

  def test_ignores_non_requested(self):
    events = [
      make_requested("read_file"),
      make_finished("c1", "ok"),
      {"type": "text_delta", "text": "hello"},
    ]
    ok, detail = assert_tool_call_count(events, {"type": "tool_call_count", "max": 1})
    assert ok
    assert "1 total" in detail


# ---- assert_tool_call_errors ----

class TestToolCallErrors:
  def test_zero_errors_pass(self):
    events = [
      make_requested("read_file", id="c1"),
      make_finished("c1", "ok"),
      make_requested("edit", id="c2"),
      make_finished("c2", "ok"),
    ]
    ok, detail = assert_tool_call_errors(events, {"type": "tool_call_errors", "max": 0})
    assert ok
    assert "0 tool errors" in detail

  def test_error_detected(self):
    events = [
      make_requested("read_file", id="c1"),
      make_finished("c1", "error", "File not found: /ws/missing.py"),
    ]
    ok, detail = assert_tool_call_errors(events, {"type": "tool_call_errors", "max": 0})
    assert not ok
    assert "1 tool error" in detail

  def test_multiple_errors(self):
    events = [
      make_finished("c1", "error", "not found"),
      make_finished("c2", "error", "permission denied"),
      make_finished("c3", "ok"),
    ]
    ok, detail = assert_tool_call_errors(events, {"type": "tool_call_errors", "max": 1})
    assert not ok
    assert "2 tool errors" in detail

  def test_cancelled_not_counted(self):
    events = [make_finished("c1", "cancelled", "user cancelled")]
    ok, _ = assert_tool_call_errors(events, {"type": "tool_call_errors", "max": 0})
    assert ok

  def test_result_regex_filter(self):
    events = [
      make_finished("c1", "error", "File not found: /ws/missing.py"),
      make_finished("c2", "error", "Permission denied: /ws/secret.py"),
    ]
    ok, detail = assert_tool_call_errors(events, {"type": "tool_call_errors", "max": 0, "result_regex": "not found"})
    assert not ok
    assert "1 tool error" in detail

  def test_result_regex_no_match(self):
    events = [make_finished("c1", "error", "Permission denied")]
    ok, _ = assert_tool_call_errors(events, {"type": "tool_call_errors", "max": 0, "result_regex": "not found"})
    assert ok

  def test_min_errors(self):
    events = [make_finished("c1", "error", "expected failure")]
    ok, _ = assert_tool_call_errors(events, {"type": "tool_call_errors", "min": 1, "max": 2})
    assert ok

  def test_min_errors_fail(self):
    events = [make_finished("c1", "ok")]
    ok, _ = assert_tool_call_errors(events, {"type": "tool_call_errors", "min": 1, "max": 2})
    assert not ok


# ---- evaluate_process integration ----

class TestEvaluateProcess:
  def test_all_new_asserts(self, tmp_path):
    workspace = tmp_path / "ws"
    events = [
      make_requested("read_file", {"file_path": "/ws/.lana/rules/a.md"}, id="c1"),
      make_finished("c1", "ok"),
      make_requested("read_file", {"file_path": "/ws/src/main.py"}, id="c2"),
      make_finished("c2", "ok"),
      make_requested("edit", {"file_path": "/ws/src/main.py"}, id="c3"),
      make_finished("c3", "ok"),
    ]
    write_session(workspace, events)
    checks = {"checks": [
      {"id": "no_devin", "severity": "CRITICAL", "assert": {"type": "forbidden_tool_args", "tool": "read_file", "args_regex": "\\.devin/"}},
      {"id": "efficient", "severity": "HIGH", "assert": {"type": "tool_call_count", "max": 10}},
      {"id": "no_errors", "severity": "HIGH", "assert": {"type": "tool_call_errors", "max": 0}},
      {"id": "limited_reads", "severity": "MEDIUM", "assert": {"type": "tool_called", "tool": "read_file", "min": 1, "max": 3}},
      {"id": "read_before_edit", "severity": "CRITICAL", "assert": {"type": "read_before_edit"}},
    ]}
    result = evaluate_process(workspace, checks)
    assert result["score"] == 1.0
    assert all(c["passed"] for c in result["checks"])
    assert len(result["checks"]) == 5

  def test_critical_cap(self, tmp_path):
    workspace = tmp_path / "ws"
    events = [
      make_requested("read_file", {"file_path": "/ws/.devin/rules/bad.md"}, id="c1"),
      make_finished("c1", "ok"),
    ]
    write_session(workspace, events)
    checks = {"checks": [
      {"id": "no_devin", "severity": "CRITICAL", "assert": {"type": "forbidden_tool_args", "tool": "read_file", "args_regex": "\\.devin/"}},
      {"id": "efficient", "severity": "HIGH", "assert": {"type": "tool_call_count", "max": 10}},
    ]}
    result = evaluate_process(workspace, checks)
    assert not result["checks"][0]["passed"]
    assert result["checks"][1]["passed"]
    assert result["score"] <= 0.5  # CRITICAL cap

  def test_unknown_assert_type(self, tmp_path):
    workspace = tmp_path / "ws"
    write_session(workspace, [])
    checks = {"checks": [{"id": "bad", "severity": "HIGH", "assert": {"type": "nonexistent_type"}}]}
    result = evaluate_process(workspace, checks)
    assert not result["checks"][0]["passed"]
    assert "unknown" in result["checks"][0]["detail"]

  def test_empty_checks(self, tmp_path):
    workspace = tmp_path / "ws"
    write_session(workspace, [])
    result = evaluate_process(workspace, {"checks": []})
    assert result["score"] == 1.0
    assert result["checks"] == []
