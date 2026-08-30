"""CLI renderer: subscribes to AgentEvents, streams text, tool lines, prompts (IS-15, SPEC section 12 format).

FR-16 UX-01/02: a status spinner covers the dead air between turn start and first visible output,
ticking elapsed seconds while thinking stays hidden. DD-24: `error` events render by severity prefix.
"""
import contextlib, time
from typing import Optional
from rich.console import Console
from lana.cost import CostTracker


# Compact one-line summary of tool arguments for the [tool] line
def summarize_args(tool: str, args: dict) -> str:
  for key in ("CommandLine", "file_path", "TargetFile", "DirectoryPath", "SearchPath", "SearchDirectory", "Url", "SkillName", "query", "document_id", "ID"):
    if key in args: return str(args[key])[:120]
  return ""


class Renderer:
  def __init__(self, console: Optional[Console] = None, cost_tracker: Optional[CostTracker] = None, policy: str = "manual", show_thinking: bool = False):
    self.console = console or Console(highlight=False, soft_wrap=True)
    self.cost_tracker = cost_tracker
    self.policy = policy
    self.show_thinking = show_thinking
    self.streaming_text = False
    self.status = None            # active rich status spinner (FR-16 UX-01)
    self.status_started = 0.0

  def end_stream(self):
    if self.streaming_text: self.console.print(); self.streaming_text = False

  # FR-16 UX-01: spinner between turn start and the first visible output
  def start_status(self):
    self.stop_status()
    self.status_started = time.monotonic()
    try:
      self.status = self.console.status("  generator thinking...")
      self.status.start()
    except Exception:  # non-terminal consoles that reject live displays - dead air stays, nothing breaks
      self.status = None

  def stop_status(self):
    if self.status is not None:
      with contextlib.suppress(Exception): self.status.stop()
      self.status = None

  # FR-16 UX-02: hidden thinking still ticks the elapsed counter - content exists, the user sees progress
  def tick_status(self):
    if self.status is not None:
      elapsed = int(time.monotonic() - self.status_started)
      with contextlib.suppress(Exception): self.status.update(f"  generator thinking... {elapsed}s")

  # BG-0004: event payloads (model text, tool results, provider messages) are UNTRUSTED - always markup=False;
  # styling goes through the style= parameter, never through inline tags mixed with payload text
  def handle(self, event) -> None:
    kind = event.type
    if kind == "turn_started":
      self.start_status()
      return
    if kind == "thinking_delta" and not self.show_thinking:
      self.tick_status()  # hidden thinking: keep the spinner honest (UX-02)
      return
    self.stop_status()  # any visible output ends the dead-air spinner (UX-01)
    if kind == "text_delta":
      self.console.print(event.text, end="", markup=False)
      self.streaming_text = True
    elif kind == "thinking_delta":
      self.console.print(event.text, end="", style="dim", markup=False)
    elif kind == "tool_call_requested":
      self.end_stream()
      summary = summarize_args(event.tool, event.args)
      policy_suffix = f" (policy: {self.policy})" if event.tool == "run_command" else ""
      self.console.print(f"  [tool] {event.tool} '{summary}'...{policy_suffix}", markup=False)
    elif kind == "tool_call_finished":
      if event.status == "ok": self.console.print(f"    OK. {event.result_chars} chars.", markup=False)
      else: self.console.print(f"    ERROR: {event.result[:300]}", markup=False)
    elif kind == "approval_required":
      resolution = "approved" if event.approved else "denied"
      self.console.print(f"    [{event.action}] {resolution}.", markup=False)
    elif kind == "turn_finished":
      self.end_stream()
      session_part = ""
      if self.cost_tracker:
        total, fully_priced = self.cost_tracker.session_total()
        session_part = f" | session ${total:.4f}" + ("" if fully_priced else " (+?)")
      self.console.print(f"  Turn: in={event.input_tokens} (cache {event.cache_read_tokens}) out={event.output_tokens} | {CostTracker.format_cost(event.cost_usd)}{session_part}", markup=False)
    elif kind == "checkpoint_created":
      self.end_stream()
      self.console.print(f"  Compacted: {event.truncated_messages} messages -> checkpoint + last {event.kept_messages}.", markup=False)
    elif kind == "error":  # DD-24: severity by message prefix - WARNING yellow, NOTICE dim, else red ERROR
      self.end_stream()
      message = event.message
      if message.startswith("WARNING:"): self.console.print(message, style="yellow", markup=False)
      elif message.startswith("NOTICE:"): self.console.print(f"  {message[len('NOTICE:'):].strip()}", style="dim", markup=False)
      else: self.console.print(f"ERROR: {message}", style="red", markup=False)


# ----------------------------------------- START: Interactive Prompts --------------------------------------------------------

# y/n approval showing exact command line + working directory (FR-12); reads from stdin
def prompt_approval(action: str, detail: str) -> bool:
  print(f"  [{action}] {detail}")
  try:
    answer = input("    Approve? [y/n] ").strip().lower()
  except (EOFError, KeyboardInterrupt):
    return False
  return answer in ("y", "yes")


# Numbered choice prompt for ask_user_question (SPEC section 11)
def prompt_question(args: dict) -> str:
  print(f"  [question] {args['question']}")
  options = args.get("options", [])
  for index, option in enumerate(options, start=1): print(f"    {index}) {option['label']} - {option['description']}")
  try:
    answer = input("    Answer (number or free text): ").strip()
  except (EOFError, KeyboardInterrupt):
    return "no answer"
  if answer.isdigit() and 1 <= int(answer) <= len(options):
    selected = options[int(answer) - 1]
    return selected["label"]
  return answer or "no answer"


def prompt_continue(calls_done: int) -> bool:
  try:
    answer = input(f"  Tool call limit reached ({calls_done} calls). Continue? [y/n] ").strip().lower()
  except (EOFError, KeyboardInterrupt):
    return False
  return answer in ("y", "yes")

# ----------------------------------------- END: Interactive Prompts ----------------------------------------------------------
