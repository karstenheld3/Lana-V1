"""CLI renderer: subscribes to AgentEvents, streams text, tool lines, prompts (IS-15, SPEC section 12 format)."""
import sys
from typing import Optional
from rich.console import Console
from lana.cost import CostTracker


# Compact one-line summary of tool arguments for the [tool] line
def summarize_args(tool: str, args: dict) -> str:
  for key in ("CommandLine", "file_path", "TargetFile", "DirectoryPath", "SearchPath", "SearchDirectory", "Url", "SkillName", "query", "document_id"):
    if key in args: return str(args[key])[:120]
  return ""


class Renderer:
  def __init__(self, console: Optional[Console] = None, cost_tracker: Optional[CostTracker] = None, policy: str = "manual", show_thinking: bool = False):
    self.console = console or Console(highlight=False, soft_wrap=True)
    self.cost_tracker = cost_tracker
    self.policy = policy
    self.show_thinking = show_thinking
    self.streaming_text = False

  def end_stream(self):
    if self.streaming_text: self.console.print(); self.streaming_text = False

  def handle(self, event) -> None:
    kind = event.type
    if kind == "text_delta":
      self.console.print(event.text, end="")
      self.streaming_text = True
    elif kind == "thinking_delta":
      if self.show_thinking: self.console.print(f"[dim]{event.text}[/dim]", end="")
    elif kind == "tool_call_requested":
      self.end_stream()
      summary = summarize_args(event.tool, event.args)
      policy_suffix = f" (policy: {self.policy})" if event.tool == "run_command" else ""
      self.console.print(f"  [tool] {event.tool} '{summary}'...{policy_suffix}", markup=False)
    elif kind == "tool_call_finished":
      if event.status == "ok": self.console.print(f"    OK. {event.result_chars} chars.")
      else: self.console.print(f"    ERROR: {event.result[:300]}")
    elif kind == "approval_required":
      resolution = "approved" if event.approved else "denied"
      self.console.print(f"    [{event.action}] {resolution}.", markup=False)
    elif kind == "turn_finished":
      self.end_stream()
      session_part = ""
      if self.cost_tracker:
        total, fully_priced = self.cost_tracker.session_total()
        session_part = f" | session ${total:.4f}" + ("" if fully_priced else " (+?)")
      self.console.print(f"  Turn: in={event.input_tokens} (cache {event.cache_read_tokens}) out={event.output_tokens} | {CostTracker.format_cost(event.cost_usd)}{session_part}")
    elif kind == "checkpoint_created":
      self.end_stream()
      self.console.print(f"  Compacted: {event.truncated_messages} messages -> checkpoint + last {event.kept_messages}.")
    elif kind == "error":
      self.end_stream()
      self.console.print(f"[red]ERROR:[/red] {event.message}")


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
