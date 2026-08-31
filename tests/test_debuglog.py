"""LANADEBG-SP01: debug console writer, viewer formatting, agent instrumentation."""
import io, json
import lana.debuglog as debuglog
from lana.debuglog import DebugLogWriter, args_summary, dlog
from lana.debug_viewer import format_detail, format_duration, render_line
from tests.conftest import collect_events


class FakeStdin:
  def __init__(self, fail: bool = False):
    self.lines: list[str] = []
    self.flushes = 0
    self.fail = fail

  def write(self, text: str) -> None:
    if self.fail: raise OSError("pipe broken")
    self.lines.append(text)

  def flush(self) -> None:
    self.flushes += 1


class FakeViewer:
  def __init__(self, stdin):
    self.stdin = stdin
    self.pid = 999


def install_fake(monkeypatch, fail: bool = False) -> tuple[FakeStdin, DebugLogWriter]:
  stdin = FakeStdin(fail)
  writer = DebugLogWriter(FakeViewer(stdin))
  monkeypatch.setattr(debuglog, "_writer", writer)
  return stdin, writer


def parsed_lines(stdin: FakeStdin) -> list[dict]:
  return [json.loads(line) for line in stdin.lines]


# IG-04: flag absent -> dlog is a no-op behind one None check, enabled() False
def test_dlog_disabled_is_noop(monkeypatch):
  monkeypatch.setattr(debuglog, "_writer", None)
  dlog("llm", "request", model="m")  # must not raise
  assert debuglog.enabled() is False


# NFR-03: one JSONL line per call, flushed at write time, ts/dom/op always present
def test_dlog_writes_flushed_jsonl(monkeypatch):
  stdin, _ = install_fake(monkeypatch)
  dlog("llm", "request", model="claude-sonnet-4-5", msgs=3)
  assert len(stdin.lines) == 1 and stdin.flushes == 1
  entry = parsed_lines(stdin)[0]
  assert entry["dom"] == "llm" and entry["op"] == "request" and entry["model"] == "claude-sonnet-4-5" and entry["msgs"] == 3
  assert len(entry["ts"]) == 23  # YYYY-MM-DD HH:MM:SS.mmm (LOG-AP-01)


# EC-01 / IG-02: first pipe failure disables permanently, warns once on stderr, never raises
def test_pipe_failure_disables_permanently(monkeypatch, capsys):
  stdin, writer = install_fake(monkeypatch, fail=True)
  dlog("tool", "start", tool="read_file")  # must not raise
  assert writer.dead is True and debuglog.enabled() is False
  dlog("tool", "end", tool="read_file")  # no-op, no second warning
  captured = capsys.readouterr()
  assert captured.err.count("debug console pipe broken") == 1 and captured.out == ""


# IG-05: identifiers only, truncated to 120 chars, empty for unknown shapes
def test_args_summary():
  assert args_summary({"CommandLine": "echo hi", "Cwd": "c:/x"}) == "echo hi"
  assert args_summary({"file_path": "x" * 200}) == "x" * 120
  assert args_summary({"old_string": "secret payload"}) == ""
  assert args_summary({}) == ""


# LOG-GN-04: duration format thresholds
def test_format_duration():
  assert format_duration(245) == "245 ms"
  assert format_duration(1500) == "1.5 secs"
  assert format_duration(90000) == "1 min 30 secs"
  assert format_duration(150000) == "2 mins 30 secs"
  assert format_duration(4500000) == "1 hour 15 mins"
  assert format_duration(61000) == "1 min 1 sec"  # LOG-GN-05: singular second
  assert format_duration(3660000) == "1 hour 1 min"  # LOG-GN-05: singular minute


# FR-06: op-specific human-readable detail per domain (LOG-GN-02 quoting, LOG-GN-04 durations)
def test_viewer_format_detail():
  assert "generator anthropic claude msgs=3 tools=17" == format_detail({"dom": "llm", "op": "request", "role": "generator", "provider": "anthropic", "model": "claude", "msgs": 3, "tools": 17})
  assert "878 ms" == format_detail({"dom": "llm", "op": "first_token", "dur_ms": 878})
  assert format_detail({"dom": "llm", "op": "response", "dur_ms": 9287, "in_tok": 24130, "cache_read": 23800, "out_tok": 512, "cost_usd": 0.0214, "tool_calls": 2}) == "9.3 secs in=24130 (cache 23800) out=512 $0.0214 tool_calls=2"
  assert format_detail({"dom": "llm", "op": "response", "dur_ms": 1, "cost_usd": None}).endswith("$? tool_calls=0")  # EC-24: unpriced model
  assert format_detail({"dom": "tool", "op": "start", "tool": "read_file", "args": "e:/x/y.md"}) == "read_file 'e:/x/y.md'"  # LOG-GN-02
  assert format_detail({"dom": "tool", "op": "end", "tool": "read_file", "dur_ms": 18, "status": "ok", "chars": 4213}) == "read_file 18 ms ok 4213 chars"
  assert format_detail({"dom": "tool", "op": "end", "tool": "read_file", "dur_ms": 2, "status": "error", "chars": 14, "err": "File not found"}) == "read_file 2 ms error 14 chars File not found"
  assert format_detail({"dom": "llm", "op": "sidecall", "role": "websearch", "provider": "openai", "model": "gpt-4.1-mini", "dur_ms": 2140, "results": 5}) == "websearch openai gpt-4.1-mini 2.1 secs results=5"
  assert format_detail({"dom": "app", "op": "roles", "roles": "generator: x (medium)"}) == "generator: x (medium)"
  assert format_detail({"dom": "tool", "op": "approval", "action": "run_command", "dur_ms": 8213, "approved": True}) == "run_command 8.2 secs approved"
  assert format_detail({"dom": "acp", "op": "recv", "method": "session/prompt", "id": 3}) == "session/prompt id=3"
  assert format_detail({"dom": "acp", "op": "turn", "id": 3, "dur_ms": 11500, "stop": "end_turn", "updates": 47}) == "id=3 11.5 secs end_turn updates=47"
  assert format_detail({"dom": "app", "op": "session", "file": "s.jsonl", "resumed": True, "dur_ms": 40}) == "'s.jsonl' (resumed) 40 ms"
  assert format_detail({"dom": "app", "op": "prompt_system", "dur_ms": 32, "rules": 8, "workflows": 48, "skills": 24}) == "8 rules, 48 workflows, 24 skills 32 ms"
  assert format_detail({"dom": "app", "op": "compaction_start", "projected": 152000, "threshold": 120000}) == "projected=152000 threshold=120000 tokens"
  assert format_detail({"dom": "app", "op": "compaction", "truncated": 40, "kept": 6, "checkpoint_chars": 5120}) == "truncated=40 kept=6 checkpoint=5120 chars"
  assert format_detail({"dom": "app", "op": "unknown_op", "extra": 1}) == '{"extra": 1}'  # fallback: raw field dump


# EC-06 spirit: render_line never raises on odd entries
def test_viewer_render_line_defensive():
  from rich.console import Console
  console = Console(file=io.StringIO(), highlight=False, soft_wrap=True)
  render_line(console, {"ts": "13:04:22.123", "dom": "llm", "op": "error", "err": "boom"})
  render_line(console, {})  # missing everything
  render_line(console, {"dom": "tool", "op": "end", "status": "error", "tool": "x", "dur_ms": 1, "chars": 0})
  output = console.file.getvalue()
  assert "boom" in output


# FR-02/FR-03 integration: scripted turn emits request/first_token/response and tool start/end lines in order
def test_agent_instrumentation_sequence(agent_factory, tmp_path, monkeypatch):
  stdin, _ = install_fake(monkeypatch)
  target_dir = str(tmp_path / "ws")
  turns = [
    {"text": "Reading.", "tool_calls": [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}], "usage": {"input": 1000, "output": 50}},
    {"text": "Done.", "usage": {"input": 1200, "output": 20}},
  ]
  agent = agent_factory(turns)
  collect_events(agent, "go")
  ops = [(entry["dom"], entry["op"]) for entry in parsed_lines(stdin)]
  assert ops == [("llm", "request"), ("llm", "first_token"), ("llm", "response"),
                 ("tool", "start"), ("tool", "end"),
                 ("llm", "request"), ("llm", "first_token"), ("llm", "response")]
  response = parsed_lines(stdin)[2]
  assert response["in_tok"] == 1000 and response["out_tok"] == 50 and response["tool_calls"] == 1
  assert response["cost_usd"] is not None  # pre-computed by the cost engine before the log call (IG-03)
  tool_end = parsed_lines(stdin)[4]
  assert tool_end["tool"] == "list_dir" and tool_end["status"] == "ok" and tool_end["dur_ms"] >= 0 and tool_end["chars"] > 0


# FR-05 + FR-02: compaction emits announce/summarizer/report debug lines with trigger and result values
def test_compaction_debug_lines(agent_factory, monkeypatch):
  stdin, _ = install_fake(monkeypatch)
  turns = [{"text": "Long reply.", "usage": {"input": 5000, "output": 100}},
           {"text": "# Objective:\ngoal\n# Session Summary:\nsummary\n# Code Interaction Summary:\nnone", "usage": {"input": 200, "output": 50}}]
  agent = agent_factory(turns, lana_overrides={"compaction_threshold_max_tokens": 1}, use_compactor=True)  # threshold 1 -> compaction after the first turn
  collect_events(agent, "go")
  ops = [(entry["dom"], entry["op"]) for entry in parsed_lines(stdin)]
  assert ("app", "compaction_start") in ops and ("app", "compaction") in ops
  assert ops.index(("app", "compaction_start")) < ops.index(("app", "compaction"))  # announce before report
  summarizer_requests = [entry for entry in parsed_lines(stdin) if entry["op"] == "request" and entry.get("role") == "summarizer"]
  assert len(summarizer_requests) == 1  # FR-02: summarizer call visible in the llm domain
  start = next(entry for entry in parsed_lines(stdin) if entry["op"] == "compaction_start")
  assert start["projected"] > start["threshold"] == 1  # trigger reason carried on the line
  report = next(entry for entry in parsed_lines(stdin) if entry["op"] == "compaction")
  assert report["checkpoint_chars"] > 0 and "truncated" in report and "kept" in report


# FR-03: approval gate line carries resolution and wait duration (non-interactive auto-deny path)
def test_approval_line_on_denied_command(agent_factory, tmp_path, monkeypatch):
  stdin, _ = install_fake(monkeypatch)
  turns = [{"text": "run", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "echo hi"}}], "usage": {"input": 10, "output": 5}},
           {"text": "ok", "usage": {"input": 12, "output": 4}}]
  agent = agent_factory(turns)  # no approve_callback -> auto-deny (FR-14)
  collect_events(agent, "go")
  approvals = [entry for entry in parsed_lines(stdin) if entry["op"] == "approval"]
  assert len(approvals) == 1 and approvals[0]["approved"] is False and approvals[0]["action"] == "run_command"
  tool_end = next(entry for entry in parsed_lines(stdin) if entry["op"] == "end")
  assert tool_end["status"] == "error"  # denied call never executed
  assert tool_end["err"] == "approval denied (non-interactive session)"  # FR-03: error text on failed calls
