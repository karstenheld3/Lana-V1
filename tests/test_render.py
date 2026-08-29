"""TK-023: renderer event subscription (IS-15, SPEC section 12 format)."""
import io
from rich.console import Console
from lana import events
from lana.render import Renderer, summarize_args


def make_renderer():
  buffer = io.StringIO()
  console = Console(file=buffer, highlight=False, soft_wrap=True, width=200)
  return Renderer(console=console), buffer


def test_text_streams_and_tool_lines():
  renderer, buffer = make_renderer()
  renderer.handle(events.TextDelta(text="Hello "))
  renderer.handle(events.TextDelta(text="world"))
  renderer.handle(events.ToolCallRequested(id="tc_1", tool="read_file", args={"file_path": "notes.md"}))
  renderer.handle(events.ToolCallFinished(id="tc_1", status="ok", result="body", result_chars=4))
  output = buffer.getvalue()
  assert "Hello world" in output
  assert "[tool] read_file 'notes.md'..." in output and "OK. 4 chars." in output


def test_run_command_line_shows_policy():
  renderer, buffer = make_renderer()
  renderer.policy = "manual"
  renderer.handle(events.ToolCallRequested(id="tc_1", tool="run_command", args={"CommandLine": "git status"}))
  assert "(policy: manual)" in buffer.getvalue()


def test_error_result_and_turn_line():
  renderer, buffer = make_renderer()
  renderer.handle(events.ToolCallFinished(id="tc_1", status="error", result="approval denied by user", result_chars=23))
  renderer.handle(events.TurnFinished(input_tokens=21050, output_tokens=412, cache_read_tokens=18200, cost_usd=0.0164))
  output = buffer.getvalue()
  assert "ERROR: approval denied by user" in output
  assert "Turn: in=21050 (cache 18200) out=412 | $0.0164" in output


def test_unknown_pricing_renders_question_mark():
  renderer, buffer = make_renderer()
  renderer.handle(events.TurnFinished(input_tokens=10, output_tokens=5, cost_usd=None))
  assert "| ?" in buffer.getvalue()


def test_checkpoint_and_error_events():
  renderer, buffer = make_renderer()
  renderer.handle(events.CheckpointCreated(text="...", truncated_messages=118, kept_messages=6))
  renderer.handle(events.ErrorEvent(message="Summarizer call failed"))
  output = buffer.getvalue()
  assert "Compacted: 118 messages -> checkpoint + last 6." in output
  assert "Summarizer call failed" in output


def test_summarize_args_priority():
  assert summarize_args("run_command", {"CommandLine": "git log", "Cwd": "x"}) == "git log"
  assert summarize_args("edit", {"file_path": "a.py", "old_string": "x"}) == "a.py"
  assert summarize_args("todo_list", {"todos": []}) == ""
