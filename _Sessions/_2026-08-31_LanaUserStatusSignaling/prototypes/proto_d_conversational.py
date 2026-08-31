"""Prototype D: Conversational Asides

Metadata in parentheses. Double encoding: parens + dim.
Errors and approvals ESCAPE parentheses.
Reference: LANAUSRX-IN03 Section 6.2
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proto_shared import (
    MockEvent, SpinnerManager, create_console, format_chars,
    format_duration, format_tokens, play_events, reference_scenario,
    type_text,
)
from rich.console import Console


class ConversationalRenderer:
    """Renders events per Approach D: Conversational Asides (Section 6.2)."""

    def __init__(self, console: Console):
        self.c = console
        self.spinner = SpinnerManager(console)
        self._turn_count = 0
        self._thinking = False
        # Tool buffering for fast merge
        self._pending_tool: dict | None = None
        self._tool_start: float = 0.0

    def tick(self):
        self.spinner.tick()

    def handle(self, event: MockEvent):
        t = event.event_type
        d = event.data

        if t == "turn_started":
            self._turn_count += 1
            if self._turn_count > 1:
                # Empty line between turns
                self.c.print(markup=False)
            # Parenthetical spinner
            self.spinner.start("(thinking...)")
            self._thinking = True

        elif t == "thinking_delta":
            self.spinner.tick()

        elif t == "text_delta":
            if self.spinner.active and self._thinking:
                elapsed = self.spinner.stop()
                self.c.print(
                    f"(thinking... {format_duration(elapsed)})",
                    style="dim", markup=False,
                )
            elif self.spinner.active:
                self.spinner.stop()
            self._thinking = False
            # Model text at column 0, NO parentheses, no style
            type_text(self.c, d["text"])

        elif t == "tool_call_requested":
            if self.spinner.active:
                self.spinner.stop()
            self._thinking = False
            name = d["name"]
            args = d.get("args", "")
            self._pending_tool = {"name": name, "args": args}
            self._tool_start = time.monotonic()
            # Start spinner as parenthetical
            self.spinner.start(f"(running {name} {args}...)")

        elif t == "tool_call_finished":
            elapsed_real = time.monotonic() - self._tool_start if self._tool_start else 0
            status = d.get("status", "ok")
            chars = d.get("chars", 0)
            name = d.get("name", "")
            args = self._pending_tool.get("args", "") if self._pending_tool else ""

            display = d.get("display", format_chars(chars))

            if elapsed_real < 2.0:
                # Fast tool: merge into single parenthetical aside
                self.spinner.stop_silent()
                if status == "ok":
                    self.c.print(
                        f"({name} {args}, {display})",
                        style="dim", markup=False,
                    )
                else:
                    self.c.print(
                        f"({name} {args}, ERROR)",
                        style="dim", markup=False,
                    )
            else:
                # Slow tool: multi-line parenthetical
                elapsed_secs = self.spinner.stop()
                # Open paren on announce line
                self.c.print(
                    f"({name} {args}...",
                    style="dim", markup=False,
                )
                # Close paren on result line with indent
                self.c.print(
                    f"  {format_duration(elapsed_secs)}, {display})",
                    style="dim", markup=False,
                )
            self._pending_tool = None

        elif t == "turn_finished":
            self.spinner.stop_silent()
            self._thinking = False
            in_tok = d["input_tokens"]
            out_tok = d["output_tokens"]
            cost = d["cost"]
            # Natural language stats in parentheses (Section 6.2)
            # Preview uses input tokens only: (4.5K tokens, $0.003)
            tok_str = format_tokens(in_tok)
            self.c.print(
                f"({tok_str} tokens, ${cost:.3f})",
                style="dim", markup=False,
            )

        elif t == "error":
            self.spinner.stop_silent()
            level = d.get("level", "ERROR")
            msg = d.get("message", "")
            if level == "WARNING":
                # NO parentheses - escapes aside pattern
                self.c.print(
                    f"WARNING: {msg}", style="yellow", markup=False,
                )
            elif level == "ERROR":
                # NO parentheses - escapes aside pattern
                self.c.print(
                    f"ERROR: {msg}", style="red", markup=False,
                )
            elif level == "NOTICE":
                # Parenthetical
                self.c.print(
                    f"({msg})", style="dim", markup=False,
                )

        elif t == "checkpoint_created":
            self.spinner.stop_silent()
            before = d.get("before", 0)
            after = d.get("after", 0)
            self.c.print(
                f"(compacted: {before} messages \u2192 {after})",
                style="dim", markup=False,
            )

        elif t == "approval_required":
            self.spinner.stop_silent()
            action = d.get("action", "")
            detail = d.get("detail", "")
            # NO parentheses - approval escapes aside pattern
            self.c.print(
                f"[action] {action} {detail}",
                style="bold", markup=False,
            )
            self.c.print(
                "Approve? [ y = yes, n = no, a = all ] ", end="", markup=False,
            )
            time.sleep(1.5)
            self.c.print("y = yes", style="bold", markup=False)


def main():
    console = create_console()
    events = reference_scenario()
    renderer = ConversationalRenderer(console)

    console.print(
        "\n=== Approach D: Conversational Asides ===\n", style="bold",
    )
    console.print("> fix the import error in parser.py\n", markup=False)

    play_events(events, renderer.handle, renderer.tick)
    console.print()


if __name__ == "__main__":
    main()
