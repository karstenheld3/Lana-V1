"""Prototype A: Structured Log

Every line is typed, classified, and indented by hierarchy.
Reference: LANAUSRX-IN03 Section 3.2

Category prefixes: [think], [tool], [sys], [action]
Indent: 2-space for categories, 4-space for sub-items
Content: column 0, no prefix, no indent
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proto_shared import (
    MockEvent, SpinnerManager, create_console, format_chars,
    format_duration, play_events, reference_scenario, type_text,
)
from rich.console import Console


class StructuredLogRenderer:
    """Renders events per Approach A: Structured Log (Section 3.2)."""

    def __init__(self, console: Console):
        self.c = console
        self.spinner = SpinnerManager(console)
        self._turn_count = 0
        self._phase = ""  # "preparing", "thinking", "tool", ""

    def tick(self):
        self.spinner.tick()

    def _flush_spinner(self):
        """Stop active spinner and print its permanent line."""
        if not self.spinner.active:
            return
        elapsed = self.spinner.stop()
        if self._phase == "preparing" and elapsed > 0:
            self.c.print(
                f"  [think] preparing... {format_duration(elapsed)}",
                style="dim", markup=False,
            )
        elif self._phase == "thinking" and elapsed > 0:
            self.c.print(
                f"  [think] thinking... {format_duration(elapsed)}",
                style="dim", markup=False,
            )
        elif self._phase == "tool" and elapsed > 0:
            self.c.print(
                f"    running... {format_duration(elapsed)}",
                style="dim", markup=False,
            )
        self._phase = ""

    def handle(self, event: MockEvent):
        t = event.event_type
        d = event.data

        if t == "turn_started":
            self._turn_count += 1
            if self._phase == "preparing":
                # Preparing spinner already running from previous turn_finished.
                # Switch to thinking spinner.
                self._flush_spinner()
                self.spinner.start("  [think] thinking...")
                self._phase = "thinking"
            else:
                # First turn or no preparing: start thinking directly
                self.spinner.start("  [think] thinking...")
                self._phase = "thinking"

        elif t == "thinking_delta":
            if self._phase == "preparing":
                # Switch from preparing to thinking
                self._flush_spinner()
                self.spinner.start("  [think] thinking...")
                self._phase = "thinking"
            elif self._phase != "thinking":
                self.spinner.start("  [think] thinking...")
                self._phase = "thinking"

        elif t == "text_delta":
            self._flush_spinner()
            type_text(self.c, d["text"])

        elif t == "tool_call_requested":
            self._flush_spinner()
            name = d["name"]
            args = d.get("args", "")
            self.c.print(
                f"  [tool] {name} {args}...",
                style="dim", markup=False,
            )
            self.spinner.start("    running...")
            self._phase = "tool"

        elif t == "tool_call_finished":
            self._flush_spinner()
            status = d.get("status", "ok")
            chars = d.get("chars", 0)
            if status == "ok":
                self.c.print(
                    f"    OK. {format_chars(chars)}",
                    style="dim", markup=False,
                )
            else:
                self.c.print(
                    f"    ERROR: {d.get('error', 'unknown')}",
                    style="dim", markup=False,
                )

        elif t == "turn_finished":
            self._flush_spinner()
            in_tok = d["input_tokens"]
            out_tok = d["output_tokens"]
            cost = d["cost"]
            self.c.print(
                f"  [sys] in={in_tok} out={out_tok} ${cost:.3f}",
                style="dim", markup=False,
            )
            # Blank separator line between turns (Section 3.2)
            self.c.print(markup=False)
            # Start preparing spinner for post-turn gap (DA-02)
            self.spinner.start("  [think] preparing...")
            self._phase = "preparing"

        elif t == "error":
            self._flush_spinner()
            level = d.get("level", "ERROR")
            msg = d.get("message", "")
            if level == "WARNING":
                self.c.print(
                    f"WARNING: {msg}", style="yellow", markup=False,
                )
            elif level == "ERROR":
                self.c.print(
                    f"ERROR: {msg}", style="red", markup=False,
                )
            elif level == "NOTICE":
                self.c.print(
                    f"  [sys] {msg}", style="dim", markup=False,
                )

        elif t == "checkpoint_created":
            self._flush_spinner()
            before = d.get("before", 0)
            after = d.get("after", 0)
            self.c.print(
                f"  [sys] Compacted: {before} messages \u2192 {after}",
                style="dim", markup=False,
            )

        elif t == "approval_required":
            self._flush_spinner()
            action = d.get("action", "")
            detail = d.get("detail", "")
            self.c.print(
                f"  [action] {action} {detail}",
                style="bold", markup=False,
            )
            self.c.print(
                "  Approve? [ y = yes, n = no, a = all ] ", end="", markup=False,
            )
            time.sleep(1.5)
            self.c.print("y = yes", style="bold", markup=False)


def main():
    console = create_console()
    events = reference_scenario()
    renderer = StructuredLogRenderer(console)

    console.print("\n=== Approach A: Structured Log ===\n", style="bold")
    console.print("> fix the import error in parser.py\n", markup=False)

    play_events(events, renderer.handle, renderer.tick)
    renderer._flush_spinner()  # stop trailing preparing spinner
    console.print()


if __name__ == "__main__":
    main()
