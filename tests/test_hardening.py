"""Hardening tests: zero-setup, resilience, clamps, notices, retries, writer thread (LANAAGNT-IP02 TC-01..15, FR-16)."""
import asyncio, json, subprocess, threading, time
import pytest
from rich.console import Console
from lana.config import ConfigError, load_lana_config
from lana.providers.base import AdapterDelta, ProviderError, is_retryable_error
from lana.render import Renderer
from lana.tools import ToolContext, ToolError
from lana.tools.shell_tools import BackgroundProcess, execute_command_status, terminate_tool_processes
from tests.conftest import DEFAULT_LANA_CONFIG, TEST_MAPPING, TEST_PRICING, TEST_REGISTRY, collect_events, write_config_dir

from io import StringIO


# Model data files only - no lana-config.json (zero-setup creates it)
def write_model_data_only(base_path):
  config_dir = base_path / "config"
  config_dir.mkdir(parents=True, exist_ok=True)
  (config_dir / "model-registry.json").write_text(json.dumps(TEST_REGISTRY), encoding="utf-8")
  (config_dir / "model-parameter-mapping.json").write_text(json.dumps(TEST_MAPPING), encoding="utf-8")
  (config_dir / "model-pricing.json").write_text(json.dumps(TEST_PRICING), encoding="utf-8")
  return config_dir


def make_args(*argv):
  from lana.cli import build_arg_parser
  return build_arg_parser().parse_args(list(argv))


# ----------------------------------------- START: Phase 1 - zero-setup + resilience ------------------------------------------

# TC-01: empty workspace (model data present) -> default config + key template + data dirs + BUNDLED agent library created and reported (LANADIST-FR-08)
def test_tc01_zero_setup_creates_and_reports(tmp_path, monkeypatch, capsys):
  from lana.cli import build_runtime
  from lana.providers import reset_adapter_cache
  write_model_data_only(tmp_path)
  monkeypatch.setenv("LANA_SCRIPTED_ADAPTER", str(tmp_path / "unused-script.jsonl"))
  monkeypatch.delenv("LANA_CONFIG", raising=False)
  reset_adapter_cache()
  app, agent, cost_tracker, prompt_system = build_runtime(make_args(), tmp_path, interactive=False)
  out = capsys.readouterr().out
  assert (tmp_path / "config" / "lana-config.json").is_file()
  assert (tmp_path / "config" / ".api-keys.txt").is_file()  # keyless template (LANADIST-DD-09)
  assert (tmp_path / ".lana-data" / "sessions").is_dir()
  assert (tmp_path / ".lana" / "rules").is_dir() and (tmp_path / ".lana" / "workflows").is_dir() and (tmp_path / ".lana" / "skills").is_dir()
  assert out.count("Created '") == 4 and "(zero-setup)" in out  # config + key template + sessions + agent library
  assert "NOTICE: prompt system is empty" not in out  # bundled library loads with content (LANADIST-FR-08)
  created_config = json.loads((tmp_path / "config" / "lana-config.json").read_text(encoding="utf-8"))
  assert "generator" in created_config["roles"]
  reset_adapter_cache()


# TC-02: explicit --config that does not exist -> ConfigError, nothing auto-created
def test_tc02_explicit_config_missing_stays_error(tmp_path):
  missing = tmp_path / "elsewhere" / "lana-config.json"
  with pytest.raises(ConfigError, match="Config file not found"):
    load_lana_config(tmp_path, missing)
  assert not missing.exists()


# TC-03: data_dir blocked by a FILE -> OSError propagates (main catches it as exit 2 - CR-01)
def test_tc03_data_dir_blocked_by_file(tmp_path, monkeypatch, capsys):
  from lana.cli import build_runtime
  from lana.providers import reset_adapter_cache
  write_config_dir(tmp_path)
  (tmp_path / ".lana-data").write_text("i am a file", encoding="utf-8")
  monkeypatch.setenv("LANA_SCRIPTED_ADAPTER", str(tmp_path / "unused-script.jsonl"))
  monkeypatch.delenv("LANA_CONFIG", raising=False)
  reset_adapter_cache()
  with pytest.raises(OSError):
    build_runtime(make_args(), tmp_path, interactive=False)
  reset_adapter_cache()


# TC-04: headless turn raising an unexpected exception -> exit 4 with a self-contained message (CR-02/CR-03)
def test_tc04_headless_survives_unexpected_exception(agent_factory, monkeypatch, capsys):
  import lana.cli as cli
  agent = agent_factory([{"text": "unused"}])
  def explode(*args, **kwargs): raise RuntimeError("disk full")
  monkeypatch.setattr(cli, "run_one_prompt", explode)
  exit_code = cli.run_headless(agent, agent.cost_tracker, "do something", "text")
  captured = capsys.readouterr()
  assert exit_code == cli.EXIT_STOPPED
  assert "unexpected failure" in captured.err and "RuntimeError" in captured.err and "disk full" in captured.err

# ----------------------------------------- END: Phase 1 ----------------------------------------------------------------------


# ----------------------------------------- START: Phase 2 - tool hardening ---------------------------------------------------

class FakePopen:
  def __init__(self, running=True, refuse_terminate=False):
    self.running = running
    self.refuse_terminate = refuse_terminate
    self.terminated = False

  def poll(self):
    return None if self.running else 0

  def terminate(self):
    self.terminated = True
    if not self.refuse_terminate: self.running = False

  def wait(self, timeout=None):
    if self.running: raise subprocess.TimeoutExpired(cmd="fake", timeout=timeout or 0)
    return 0


# TC-05: WaitDurationSeconds above 60 is clamped and the clamp is noted (BL-03)
def test_tc05_command_status_wait_clamp(tmp_path):
  context = ToolContext(workspace=tmp_path)
  process = BackgroundProcess(command_id="cmd_test", command_line="echo hi", popen=FakePopen(running=False))
  process.done, process.exit_code = True, 0
  context.background_processes["cmd_test"] = process
  result = execute_command_status({"CommandId": "cmd_test", "OutputCharacterCount": 1000, "WaitDurationSeconds": 3600}, context)
  assert "clamped to 60 s" in result
  result_ok = execute_command_status({"CommandId": "cmd_test", "OutputCharacterCount": 1000, "WaitDurationSeconds": 5}, context)
  assert "clamped" not in result_ok


# TC-15: terminate_tool_processes - foreground + background terminated, survivors named, finished skipped
def test_tc15_terminate_tool_processes(tmp_path):
  context = ToolContext(workspace=tmp_path)
  foreground = BackgroundProcess(command_id="cmd_fg", command_line="slow build", popen=FakePopen())
  stubborn = BackgroundProcess(command_id="cmd_bg1", command_line="stuck", popen=FakePopen(refuse_terminate=True))
  finished = BackgroundProcess(command_id="cmd_bg2", command_line="done already", popen=FakePopen(running=False))
  context.foreground_process = foreground
  context.background_processes = {"cmd_bg1": stubborn, "cmd_bg2": finished}
  terminated, survivors = terminate_tool_processes(context)
  assert any("cmd_fg" in label for label in terminated)
  assert any("cmd_bg1" in label for label in survivors)
  assert not any("cmd_bg2" in label for label in terminated + survivors)
  assert context.foreground_process is None
  terminated_fg_only, _ = terminate_tool_processes(context, include_background=False)
  assert terminated_fg_only == []  # nothing live in the foreground slot anymore


# TC-14: fetch aborts past the wall-clock deadline even when per-read timeouts never trip (BL-07)
def test_tc14_fetch_wall_clock_deadline(tmp_path, monkeypatch):
  import lana.tools.web_tools as web_tools

  class FakeHeaders:
    def get(self, name, default=""): return "text/html"

  class FakeResponse:
    headers = FakeHeaders()
    def read(self, n): return b"x" * 1024  # trickles forever
    def __enter__(self): return self
    def __exit__(self, *exc): return False

  monkeypatch.setattr(web_tools.urllib.request, "urlopen", lambda request, timeout: FakeResponse())
  clock = iter(range(0, 100000, 61))  # each monotonic() call advances 61 s
  monkeypatch.setattr(web_tools.time, "monotonic", lambda: float(next(clock)))
  context = ToolContext(workspace=tmp_path)
  with pytest.raises(ToolError, match="wall-clock deadline"):
    web_tools.execute_read_url_content({"Url": "https://example.com/slow"}, context)

# ----------------------------------------- END: Phase 2 ----------------------------------------------------------------------


# ----------------------------------------- START: Phase 3 - renderer + compaction --------------------------------------------

def make_renderer(show_thinking=False):
  sink = StringIO()
  console = Console(file=sink, highlight=False, soft_wrap=True, force_terminal=False, width=200)
  return Renderer(console=console, show_thinking=show_thinking), sink


class FakeEvent:
  def __init__(self, type, **fields):
    self.type = type
    for key, value in fields.items(): setattr(self, key, value)


# TC-08: severity rendering - WARNING as-is, NOTICE stripped + indented, plain gets ERROR prefix (DD-24)
def test_tc08_severity_prefix_rendering():
  renderer, sink = make_renderer()
  renderer.handle(FakeEvent("error", message="WARNING: retrying in 8s"))
  renderer.handle(FakeEvent("error", message="NOTICE: Compacting context (~5000 tokens)..."))
  renderer.handle(FakeEvent("error", message="something broke"))
  output = sink.getvalue()
  assert "WARNING: retrying in 8s" in output
  assert "  Compacting context (~5000 tokens)..." in output and "NOTICE:" not in output.split("WARNING: retrying in 8s")[1].split("ERROR")[0]
  assert "ERROR: something broke" in output
  assert "ERROR: WARNING" not in output  # warnings never carry the ERROR prefix


# TC-09: status lifecycle - turn_started starts, hidden thinking ticks, first visible output stops; no crash on repeats
def test_tc09_status_spinner_lifecycle():
  renderer, sink = make_renderer(show_thinking=False)
  renderer.handle(FakeEvent("turn_started", role="generator"))
  assert renderer.status is not None
  renderer.handle(FakeEvent("thinking_delta", text="pondering"))  # hidden: spinner stays, ticker updates
  assert renderer.status is not None
  assert "pondering" not in sink.getvalue()
  renderer.handle(FakeEvent("text_delta", text="hello"))
  assert renderer.status is None  # visible output stopped the spinner
  assert "hello" in sink.getvalue()
  renderer.handle(FakeEvent("turn_started", role="generator"))  # second turn in the same loop
  renderer.handle(FakeEvent("turn_finished", input_tokens=1, output_tokens=1, cache_read_tokens=0, cost_usd=None))
  assert renderer.status is None


def test_tc09b_show_thinking_streams_dim():
  renderer, sink = make_renderer(show_thinking=True)
  renderer.handle(FakeEvent("turn_started", role="generator"))
  renderer.handle(FakeEvent("thinking_delta", text="visible thought"))
  assert renderer.status is None  # visible thinking counts as output
  assert "visible thought" in sink.getvalue()


SUMMARY_TEXT = "# Objective:\nFinish.\n# Session Summary:\nWorked.\n# Code Interaction Summary:\nEdited."


# TC-07: NOTICE precedes checkpoint_created on successful compaction (UX-04)
def test_tc07_compaction_notice_before_checkpoint(agent_factory):
  turns = [
    {"text": "long answer " * 20, "usage": {"input": 3000, "output": 100}},
    {"text": SUMMARY_TEXT},
  ]
  agent = agent_factory(turns, lana_overrides={"compaction_threshold_max_tokens": 40}, use_compactor=True)
  events = collect_events(agent, "go")
  types_with_notice = [("notice" if event.type == "error" and event.message.startswith("NOTICE: Compacting") else event.type) for event in events]
  assert "notice" in types_with_notice and "checkpoint_created" in types_with_notice
  assert types_with_notice.index("notice") < types_with_notice.index("checkpoint_created")


# TC-06: post-Summarizer failure -> WARNING, no truncation, turn continues (CR-04)
def test_tc06_compaction_post_summarizer_failsafe(agent_factory, monkeypatch):
  import lana.compaction as compaction
  def explode(text): raise ValueError("defective splitter")
  monkeypatch.setattr(compaction, "split_sections", explode)
  turns = [
    {"text": "long answer", "usage": {"input": 3000, "output": 100}},
    {"text": SUMMARY_TEXT},
  ]
  agent = agent_factory(turns, lana_overrides={"compaction_threshold_max_tokens": 40}, use_compactor=True)
  events = collect_events(agent, "go")
  assert not [event for event in events if event.type == "checkpoint_created"]
  warning = [event for event in events if event.type == "error" and "Compaction failed after the Summarizer call" in event.message][0]
  assert "defective splitter" in warning.message
  assert any(message.content == "long answer" for message in agent.messages)  # nothing truncated
  assert agent.stop_reason is None

# ----------------------------------------- END: Phase 3 ----------------------------------------------------------------------


# ----------------------------------------- START: Phase 4 - provider retries -------------------------------------------------

# TC-10: retryable classification - status wins, connection/timeout by type name, others fail fast
def test_tc10_is_retryable_error():
  for status in (408, 429, 500, 502, 503, 504):
    error = type("APIStatusError", (Exception,), {"status_code": status})()
    assert is_retryable_error(error), f"status {status} must be retryable"
  for status in (400, 401, 403, 404, 422):
    error = type("APIStatusError", (Exception,), {"status_code": status})()
    assert not is_retryable_error(error), f"status {status} must fail fast"
  assert is_retryable_error(type("APIConnectionError", (Exception,), {})())
  assert is_retryable_error(type("APITimeoutError", (Exception,), {})())
  assert not is_retryable_error(ValueError("nope"))


# TC-11: adapter retry loop - 2 retryable failures then success -> 2 notice deltas + content; 400 fails fast
def test_tc11_openai_adapter_retry_loop(monkeypatch):
  import openai
  import lana.providers.openai_adapter as openai_adapter
  from lana.config import ResolvedRole
  monkeypatch.setattr(openai_adapter, "RETRY_DELAYS_SECONDS", (0.0, 0.0))
  adapter = openai_adapter.OpenAIAdapter(api_key="sk-test")
  role = ResolvedRole(name="generator", model_id="gpt-4.1-mini", provider="openai", method="temperature", effort="low", max_input=100000, max_output=1000, params={"temperature": 0.2})

  connection_error = type("APIConnectionError", (openai.OpenAIError,), {})("boom")
  attempts = {"count": 0}
  async def flaky_stream(request):
    attempts["count"] += 1
    if attempts["count"] <= 2: raise connection_error
    yield AdapterDelta(kind="text", text="recovered")
  monkeypatch.setattr(adapter, "_stream_once", flaky_stream)

  async def run():
    return [delta async for delta in adapter.stream_turn("system", [], [], role)]
  deltas = asyncio.run(run())
  notices = [delta for delta in deltas if delta.kind == "notice"]
  assert len(notices) == 2 and all("retrying" in notice.text for notice in notices)
  assert [delta.text for delta in deltas if delta.kind == "text"] == ["recovered"]

  bad_request = type("APIStatusError", (openai.OpenAIError,), {"status_code": 400})("bad request")
  async def hard_failure(request):
    raise bad_request
    yield  # pragma: no cover - makes this an async generator
  monkeypatch.setattr(adapter, "_stream_once", hard_failure)
  async def run_fail():
    return [delta async for delta in adapter.stream_turn("system", [], [], role)]
  with pytest.raises(ProviderError, match="OpenAI API error"):
    asyncio.run(run_fail())


# TC-12: notice deltas surface as WARNING error events on the agent stream and in the session JSONL
def test_tc12_agent_notice_becomes_warning_event(agent_factory, monkeypatch):
  import lana.agent as agent_module
  from lana.models import Usage
  agent = agent_factory([{"text": "unused"}])

  class NoticeAdapter:
    async def stream_turn(self, system, tools, messages, role):
      yield AdapterDelta(kind="notice", text="OpenAI APIConnectionError - retrying in 2s (attempt 1/2)...")
      yield AdapterDelta(kind="text", text="done")
      yield AdapterDelta(kind="usage", usage=Usage(input_tokens=10, output_tokens=5))
  monkeypatch.setattr(agent_module, "get_adapter", lambda role, app: NoticeAdapter())
  events = collect_events(agent, "hello")
  warnings = [event for event in events if event.type == "error" and event.message.startswith("WARNING:")]
  assert len(warnings) == 1 and "retrying" in warnings[0].message
  assert agent.stop_reason is None and agent.final_text == "done"
  recorded = (agent.session.path).read_text(encoding="utf-8")
  assert "WARNING: OpenAI APIConnectionError" in recorded  # notice persisted like every event (IG-02)

# ----------------------------------------- END: Phase 4 ----------------------------------------------------------------------


# ----------------------------------------- START: Phase 5 - ACP writer thread ------------------------------------------------

# TC-13: StdoutWriter - ordered delivery, overflow drops with count, close drains
def test_tc13_stdout_writer_order_overflow_close():
  from lana.acp.jsonrpc import StdoutWriter
  delivered = []
  gate = threading.Event()

  def blocking_sink(line):
    gate.wait(timeout=5)
    delivered.append(line)

  writer = StdoutWriter(sink=blocking_sink, maxsize=1)
  writer.write("first")            # dequeued by the thread, blocks in the sink
  time.sleep(0.2)                  # let the thread pick it up
  writer.write("second")           # fills the queue (maxsize=1)
  writer.write("third")            # overflow -> dropped
  assert writer.dropped == 1
  gate.set()
  writer.close()
  assert delivered == ["first", "second"]


def test_tc13b_stdout_writer_plain_order():
  from lana.acp.jsonrpc import StdoutWriter
  delivered = []
  writer = StdoutWriter(sink=delivered.append)
  for index in range(50): writer.write(f"line-{index}")
  writer.close()
  assert delivered == [f"line-{index}" for index in range(50)]

# ----------------------------------------- END: Phase 5 ----------------------------------------------------------------------
