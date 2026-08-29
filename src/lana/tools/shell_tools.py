"""Shell tool executors: run_command (pwsh, Blocking/WaitMsBeforeAsync) and command_status (IS-09)."""
import subprocess, threading, time, uuid
from dataclasses import dataclass, field
from lana.tools import ToolContext, ToolError

DEFAULT_BLOCKING_TIMEOUT_SECONDS = 600


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
  return subprocess.Popen(["pwsh", "-NoProfile", "-Command", command_line], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")


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
  if args.get("Blocking", False):
    reader.join(timeout=DEFAULT_BLOCKING_TIMEOUT_SECONDS)
    if not process.done:
      context.background_processes[process.command_id] = process
      return f"Command still running after {DEFAULT_BLOCKING_TIMEOUT_SECONDS} s - moved to background with ID {process.command_id}. Check it with command_status."
    return f"Exit code {process.exit_code}\nOutput:\n{process.output_text()}"
  wait_ms = args.get("WaitMsBeforeAsync", 0)
  if wait_ms > 0: reader.join(timeout=wait_ms / 1000)
  if process.done: return f"Exit code {process.exit_code}\nOutput:\n{process.output_text()}"
  context.background_processes[process.command_id] = process
  preview = process.output_text()
  suffix = f"\nOutput so far:\n{preview}" if preview else ""
  return f"Command running in background with ID {process.command_id}. Check it with command_status.{suffix}"


def execute_command_status(args: dict, context: ToolContext) -> str:
  command_id = args["CommandId"]
  process = context.background_processes.get(command_id)
  if process is None: raise ToolError(f"Unknown command ID '{command_id}'. Known background IDs: {', '.join(context.background_processes) or '(none)'}")
  wait_seconds = args.get("WaitDurationSeconds", 0)
  deadline = time.monotonic() + wait_seconds
  while not process.done and time.monotonic() < deadline: time.sleep(0.05)
  status = "done" if process.done else "running"
  output = process.output_text()
  max_chars = args["OutputCharacterCount"]
  if len(output) > max_chars: output = output[-max_chars:]
  exit_line = f"\nExit code {process.exit_code}" if process.done else ""
  return f"Status: {status}{exit_line}\nOutput:\n{output}"
