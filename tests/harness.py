"""LanaProc: spawn the real `lana` CLI, inject prompts, parse stdout JSONL, tail the flushed session file (IS-22, TP01 section 8)."""
import os, subprocess, sys, time
from pathlib import Path
from lana.events import from_jsonl

DEFAULT_TIMEOUT_SECONDS = 60


class LanaProc:
  def __init__(self, workspace: Path, config_path: Path | None = None, script_path: Path | None = None, policy: str | None = None):
    self.workspace = Path(workspace)
    self.config_path = config_path
    self.script_path = script_path
    self.policy = policy
    self.last_result: subprocess.CompletedProcess | None = None

  def build_env(self) -> dict:
    env = dict(os.environ)
    env.pop("OPENAI_API_KEY", None)
    env.pop("ANTHROPIC_API_KEY", None)
    if self.config_path: env["LANA_CONFIG"] = str(self.config_path)
    if self.script_path: env["LANA_SCRIPTED_ADAPTER"] = str(self.script_path)
    else: env.pop("LANA_SCRIPTED_ADAPTER", None)
    return env

  def build_command(self, extra_args: list[str]) -> list[str]:
    command = [sys.executable, "-m", "lana"]
    if self.policy: command += ["--policy", self.policy]
    return command + extra_args

  # Headless run: lana -p "<prompt>" [--output-format jsonl] (FR-14)
  def run_headless(self, prompt: str, output_format: str = "jsonl", timeout: int = DEFAULT_TIMEOUT_SECONDS, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    command = self.build_command(["-p", prompt, "--output-format", output_format] + (extra_args or []))
    self.last_result = subprocess.run(command, cwd=self.workspace, env=self.build_env(), capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    return self.last_result

  # Piped stdin session: lines fed to the plain-input REPL fallback (TC-55)
  def run_piped(self, stdin_text: str, timeout: int = DEFAULT_TIMEOUT_SECONDS, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    command = self.build_command(extra_args or [])
    self.last_result = subprocess.run(command, cwd=self.workspace, env=self.build_env(), input=stdin_text, capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    return self.last_result

  # Parse AgentEvents from headless jsonl stdout (banner lines are not JSON and are skipped)
  def events(self, result: subprocess.CompletedProcess | None = None) -> list:
    result = result or self.last_result
    parsed = []
    for line in (result.stdout or "").splitlines():
      line = line.strip()
      if not line.startswith("{"): continue
      try:
        parsed.append(from_jsonl(line))
      except Exception:
        continue
    return parsed

  def session_files(self) -> list[Path]:
    sessions_dir = self.workspace / ".lana" / "sessions"
    if not sessions_dir.is_dir(): return []
    return sorted(sessions_dir.glob("*.jsonl"), key=lambda path: path.stat().st_mtime)

  def read_session_events(self, session_file: Path | None = None) -> list:
    files = self.session_files()
    target = session_file or (files[-1] if files else None)
    if target is None: return []
    parsed = []
    for line in target.read_text(encoding="utf-8").splitlines():
      try:
        parsed.append(from_jsonl(line))
      except Exception:
        continue
    return parsed

  # Poll the flushed session file until predicate(event) matches (FR-08 external tail contract)
  def tail_session(self, predicate, timeout: float = 10.0, poll_interval: float = 0.1):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
      for event in self.read_session_events():
        if predicate(event): return event
      time.sleep(poll_interval)
    return None


  # Non-blocking spawn with piped stdin for kill/resume scenarios (TP01-TC-06)
  def start_piped(self, extra_args: list[str] | None = None) -> subprocess.Popen:
    command = self.build_command(extra_args or [])
    self.popen = subprocess.Popen(command, cwd=self.workspace, env=self.build_env(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    return self.popen

  def send(self, line: str) -> None:
    self.popen.stdin.write(line + "\n")
    self.popen.stdin.flush()

  def kill(self) -> None:
    self.popen.kill()
    self.popen.wait(timeout=10)

  def wait_exit(self, timeout: int = 30) -> int:
    return self.popen.wait(timeout=timeout)


# NFR-01: key material must never appear in any observable output
def assert_no_secret_leak(outputs: list[str], key_values: list[str]) -> None:
  for secret in key_values:
    if not secret: continue
    for output in outputs:
      assert secret not in (output or ""), f"secret value leaked into output (starts '{secret[:8]}...')"


# Assert helper: event sequence contains the given types in order (gaps allowed)
def assert_event_order(events: list, expected_types: list[str]) -> None:
  positions = []
  cursor = 0
  for expected in expected_types:
    found = None
    for index in range(cursor, len(events)):
      if events[index].type == expected: found = index; break
    assert found is not None, f"missing event '{expected}' after position {cursor}; got {[event.type for event in events]}"
    positions.append(found)
    cursor = found + 1
