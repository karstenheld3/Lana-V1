"""Shell tool executors: run_command (pwsh, Blocking/WaitMsBeforeAsync) and command_status (IS-09)."""
import os, subprocess, threading, time, uuid
from dataclasses import dataclass, field
from lana.tools import ToolContext, ToolError

DEFAULT_BLOCKING_TIMEOUT_SECONDS = 600
MAX_STATUS_WAIT_SECONDS = 60  # FR-16 BL-03: the bound the command_status description promises
TERMINATE_WAIT_SECONDS = 3


@dataclass
class BackgroundProcess:
  command_id: str
  command_line: str
  popen: subprocess.Popen
  output_lines: list[str] = field(default_factory=list)
  done: bool = False
  exit_code: int | None = None

  def output_text(self) -> str:
    return "\n".join(self.output_lines)


def drain_output(process: BackgroundProcess) -> None:
  for line in process.popen.stdout: process.output_lines.append(line.rstrip("\r\n"))
  process.popen.wait()
  process.exit_code = process.popen.returncode
  process.done = True


def start_process(command_line: str, cwd: str) -> subprocess.Popen:
  environment = dict(os.environ, PAGER="cat")  # Cascade contract: commands run with PAGER=cat (run_command description)
  return subprocess.Popen(["pwsh", "-NoProfile", "-Command", command_line], cwd=cwd, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")


def execute_run_command(args: dict, context: ToolContext) -> str:
  command_line = args["CommandLine"]
  cwd = args.get("Cwd") or str(context.workspace)
  try:
    popen = start_process(command_line, cwd)
  except FileNotFoundError:
    raise ToolError("Cannot start 'pwsh' - PowerShell 7 is required on PATH.") from None
  except OSError as error:
    raise ToolError(f"Cannot run command: {error}") from None
  process = BackgroundProcess(command_id=f"cmd_{uuid.uuid4().hex[:8]}", command_line=command_line, popen=popen)
  reader = threading.Thread(target=drain_output, args=(process,), daemon=True)
  reader.start()
  context.foreground_process = process  # FR-16 BL-02: cancellation/exit can terminate the live foreground child
  try:
    if args.get("Blocking", False):
      reader.join(timeout=DEFAULT_BLOCKING_TIMEOUT_SECONDS)
      if not process.done:
        context.background_processes[process.command_id] = process
        return f"Command still running after {DEFAULT_BLOCKING_TIMEOUT_SECONDS} s - moved to background with ID {process.command_id}. Check it with command_status."
      return f"Exit code {process.exit_code}\nOutput:\n{process.output_text()}"
    wait_ms = args.get("WaitMsBeforeAsync", 0)
    if wait_ms > 0: reader.join(timeout=wait_ms / 1000)
    if process.done: return f"Exit code {process.exit_code}\nOutput:\n{process.output_text()}"
  finally:
    context.foreground_process = None
  context.background_processes[process.command_id] = process
  preview = process.output_text()
  suffix = f"\nOutput so far:\n{preview}" if preview else ""
  return f"Command running in background with ID {process.command_id}. Check it with command_status.{suffix}"


def execute_command_status(args: dict, context: ToolContext) -> str:
  command_id = args["CommandId"]
  process = context.background_processes.get(command_id)
  if process is None: raise ToolError(f"Unknown command ID '{command_id}'. Known background IDs: {', '.join(context.background_processes) or '(none)'}")
  wait_requested = args.get("WaitDurationSeconds", 0)
  wait_seconds = min(wait_requested, MAX_STATUS_WAIT_SECONDS)  # FR-16 BL-03: clamp to the promised bound
  deadline = time.monotonic() + wait_seconds
  while not process.done and time.monotonic() < deadline: time.sleep(0.05)
  status = "done" if process.done else "running"
  output = process.output_text()
  max_chars = args["OutputCharacterCount"]
  if len(output) > max_chars: output = output[-max_chars:]
  exit_line = f"\nExit code {process.exit_code}" if process.done else ""
  clamp_note = f"\nNOTE: WaitDurationSeconds {wait_requested} clamped to {MAX_STATUS_WAIT_SECONDS} s (tool contract maximum)." if wait_requested > MAX_STATUS_WAIT_SECONDS else ""
  return f"Status: {status}{exit_line}{clamp_note}\nOutput:\n{output}"


# FR-16 BL-02/BL-06: terminate live tool child processes (foreground always; background on exit/EOF).
# Returns (terminated labels, survivor labels) - the caller reports them in one line each.
def terminate_tool_processes(context, include_background: bool = True) -> tuple[list[str], list[str]]:
  candidates: list[BackgroundProcess] = []
  foreground = getattr(context, "foreground_process", None)
  if foreground is not None: candidates.append(foreground)
  if include_background: candidates.extend(context.background_processes.values())
  terminated, survivors = [], []
  for process in candidates:
    if process.popen.poll() is not None: continue  # already finished
    label = f"{process.command_id} ({process.command_line[:60]})"
    try:
      process.popen.terminate()
      process.popen.wait(timeout=TERMINATE_WAIT_SECONDS)
      terminated.append(label)
    except Exception:
      survivors.append(label)
  context.foreground_process = None
  return terminated, survivors
