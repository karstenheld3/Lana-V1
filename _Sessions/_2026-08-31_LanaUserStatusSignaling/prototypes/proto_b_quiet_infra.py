"""Prototype B: Quiet Infrastructure

Model text IS the product. Everything else is dim, merged, minimal.
Reference: LANAUSRX-IN03 Section 4.2

No prefixes. Merged fast tools. Positional stats. Empty-line turn breaks.
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


class QuietInfraRenderer:
    """Renders events per Approach B: Quiet Infrastructure (Section 4.2)."""

    def __init__(self, console: Console):
        self.c = console
        self.spinner = SpinnerManager(console)
        self._turn_count = 0
        self._thinking = False
        # Tool merging state
        self._pending_tool: dict | None = None
        self._tool_start: float = 0.0

    def tick(self):
        self.spinner.tick()

    def _flush_pending_tool(self):
        """Emit buffered fast tool as merged line."""
        if self._pending_tool:
            t = self._pending_tool
            name = t["name"]
            args = t.get("args", "")
            chars = t.get("chars", 0)
            self.c.print(
                f"  {name} {args}  {format_chars(chars)}",
                style="dim", markup=False,
            )
            self._pending_tool = None

    def handle(self, event: MockEvent):
        t = event.event_type
        d = event.data

        if t == "turn_started":
            self._flush_pending_tool()
            self._turn_count += 1
            if self._turn_count > 1:
                # Empty line between turns (whitespace as design element)
                self.c.print(markup=False)
            # Start thinking spinner (no prefix, 2-space indent)
            self.spinner.start("  thinking...")
            self._thinking = True

        elif t == "thinking_delta":
            self.spinner.tick()

        elif t == "text_delta":
            self._flush_pending_tool()
            if self.spinner.active and self._thinking:
                elapsed = self.spinner.stop()
                self.c.print(
                    f"  thinking... {format_duration(elapsed)}",
                    style="dim", markup=False,
                )
            elif self.spinner.active:
                self.spinner.stop()
            self._thinking = False
            type_text(self.c, d["text"])

        elif t == "tool_call_requested":
            self._flush_pending_tool()
            if self.spinner.active:
                self.spinner.stop()
            self._thinking = False
            name = d["name"]
            args = d.get("args", "")
            self._pending_tool = {"name": name, "args": args}
            self._tool_start = time.monotonic()
            # Start spinner immediately - ephemeral, cleared if fast
            self.spinner.start(f"  {name} {args}...")

        elif t == "tool_call_finished":
            elapsed_real = time.monotonic() - self._tool_start if self._tool_start else 0
            status = d.get("status", "ok")
            chars = d.get("chars", 0)
            name = d.get("name", "")
            args = self._pending_tool.get("args", "") if self._pending_tool else ""

            display = d.get("display", format_chars(chars))

            if elapsed_real < 2.0:
                # Fast tool: stop spinner (ephemeral), emit merged line
                self.spinner.stop_silent()
                if status == "ok":
                    self.c.print(
                        f"  {name} {args}  {display}",
                        style="dim", markup=False,
                    )
                else:
                    self.c.print(
                        f"  {name} {args}  ERROR",
                        style="dim", markup=False,
                    )
            else:
                # Slow tool: print announce, elapsed, result
                elapsed_secs = self.spinner.stop()
                self.c.print(
                    f"  {name} {args}...",
                    style="dim", markup=False,
                )
                self.c.print(
                    f"    {format_duration(elapsed_secs)}  {display}",
                    style="dim", markup=False,
                )
            self._pending_tool = None

        elif t == "turn_finished":
            self._flush_pending_tool()
            self.spinner.stop_silent()
            self._thinking = False
            in_tok = d["input_tokens"]
            out_tok = d["output_tokens"]
            cost = d["cost"]
            # Positional stats, no labels (Section 4.2)
            self.c.print(
                f"  {in_tok} in  {out_tok} out  ${cost:.3f}",
                style="dim", markup=False,
            )

        elif t == "error":
            self._flush_pending_tool()
            self.spinner.stop_silent()
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
                    f"  {msg}", style="dim", markup=False,
                )

        elif t == "checkpoint_created":
            self._flush_pending_tool()
            self.spinner.stop_silent()
            before = d.get("before", 0)
            after = d.get("after", 0)
            self.c.print(
                f"  Compacted: {before} messages \u2192 {after}",
                style="dim", markup=False,
            )

        elif t == "approval_required":
            self._flush_pending_tool()
            self.spinner.stop_silent()
            action = d.get("action", "")
            detail = d.get("detail", "")
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
    renderer = QuietInfraRenderer(console)

    console.print("\n=== Approach B: Quiet Infrastructure ===\n", style="bold")
    console.print("> fix the import error in parser.py\n", markup=False)

    play_events(events, renderer.handle, renderer.tick)
    console.print()


if __name__ == "__main__":
    main()
