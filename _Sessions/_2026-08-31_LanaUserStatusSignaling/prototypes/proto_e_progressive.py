"""Prototype E: Progressive Disclosure

Three verbosity levels: default, verbose, debug.
Each level is a strict superset of the previous.
Reference: LANAUSRX-IN03 Section 7.4
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


class ProgressiveRenderer:
    """Renders events per Approach E: Progressive Disclosure (Section 7.4).

    Verbosity levels:
      "default" - content + spinner only
      "verbose" - adds tool lines, notices, compaction (B-equivalent)
      "debug"   - adds thinking, prefixes, timing, turn stats (A+timing)
    """

    def __init__(self, console: Console, verbosity: str = "default"):
        self.c = console
        self.spinner = SpinnerManager(console)
        self.verbosity = verbosity  # "default", "verbose", "debug"
        self._turn_count = 0
        self._thinking = False
        self._pending_tool: dict | None = None
        self._tool_start: float = 0.0
        self._debug_reasoning_shown: bool = False

    def tick(self):
        self.spinner.tick()

    def _is_verbose(self) -> bool:
        return self.verbosity in ("verbose", "debug")

    def _is_debug(self) -> bool:
        return self.verbosity == "debug"

    def handle(self, event: MockEvent):
        t = event.event_type
        d = event.data

        if t == "turn_started":
            self._turn_count += 1
            self._debug_reasoning_shown = False
            if self._turn_count > 1:
                self.c.print(markup=False)

            if self._is_debug():
                self.spinner.start("  thinking...")
            elif self._is_verbose():
                self.spinner.start("  thinking...")
            else:
                # Default: generic spinner
                self.spinner.start("thinking...")
            self._thinking = True

        elif t == "thinking_delta":
            if self._is_debug():
                # Debug: show reasoning text as dim inline (Section 7.4)
                text = d.get("text", "")
                if text and not self._debug_reasoning_shown:
                    # Stop spinner, print reasoning, restart spinner
                    elapsed = self.spinner.stop()
                    if elapsed > 0:
                        self.c.print(
                            f"  thinking... {format_duration(elapsed)}",
                            style="dim", markup=False,
                        )
                    self.c.print(
                        f"  <{text}...>",
                        style="dim", markup=False,
                    )
                    self.spinner.start("  thinking...")
                    self._debug_reasoning_shown = True
            self.spinner.tick()

        elif t == "text_delta":
            if self.spinner.active and self._thinking:
                elapsed = self.spinner.stop()
                if self._is_verbose() and elapsed > 0:
                    self.c.print(
                        f"  thinking... {format_duration(elapsed)}",
                        style="dim", markup=False,
                    )
                # Default mode: spinner was ephemeral, no permanent line
            elif self.spinner.active:
                self.spinner.stop()
            self._thinking = False
            type_text(self.c, d["text"])

        elif t == "tool_call_requested":
            if self.spinner.active:
                self.spinner.stop()
            self._thinking = False
            name = d["name"]
            args = d.get("args", "")
            self._pending_tool = {"name": name, "args": args}
            self._tool_start = time.monotonic()

            if self._is_debug():
                # Debug: prefix marker
                self.c.print(
                    f"  [tool] {name} {args}...",
                    style="dim", markup=False,
                )
                self.spinner.start(f"    running...")
            elif self._is_verbose():
                # Verbose: tool name, start spinner
                self.spinner.start(f"  {name} {args}...")
            else:
                # Default: generic spinner, NO tool name
                self.spinner.start("running...")

        elif t == "tool_call_finished":
            elapsed_real = time.monotonic() - self._tool_start if self._tool_start else 0
            status = d.get("status", "ok")
            chars = d.get("chars", 0)
            name = d.get("name", "")
            args = self._pending_tool.get("args", "") if self._pending_tool else ""
            dur = d.get("duration_secs", elapsed_real)

            display = d.get("display", format_chars(chars))

            if self._is_debug():
                # Debug: full detail with timing (always shows chars count)
                elapsed_secs = self.spinner.stop()
                if elapsed_secs > 0:
                    self.c.print(
                        f"    running... {format_duration(elapsed_secs)}",
                        style="dim", markup=False,
                    )
                self.c.print(
                    f"    OK. {format_chars(chars)} ({dur:.1f} secs)",
                    style="dim", markup=False,
                )
            elif self._is_verbose():
                # Verbose: merged fast, detailed slow (B-equivalent)
                if elapsed_real < 2.0:
                    self.spinner.stop_silent()
                    self.c.print(
                        f"  {name} {args}  {display}",
                        style="dim", markup=False,
                    )
                else:
                    elapsed_secs = self.spinner.stop()
                    self.c.print(
                        f"  {name} {args}...",
                        style="dim", markup=False,
                    )
                    self.c.print(
                        f"    {format_duration(elapsed_secs)}  {display}",
                        style="dim", markup=False,
                    )
            else:
                # Default: stop spinner, no output
                self.spinner.stop_silent()
            self._pending_tool = None

        elif t == "turn_finished":
            self.spinner.stop_silent()
            self._thinking = False
            in_tok = d["input_tokens"]
            out_tok = d["output_tokens"]
            cost = d["cost"]
            cached = d.get("cached_tokens", 0)

            if self._is_debug():
                # Debug: full diagnostics with cache
                self.c.print(
                    f"  Turn {self._turn_count}: in={in_tok} "
                    f"(cache {cached}) out={out_tok} | ${cost:.3f}",
                    style="dim", markup=False,
                )
            # Verbose and default: no turn stats (Section 7.4)

        elif t == "error":
            self.spinner.stop_silent()
            level = d.get("level", "ERROR")
            msg = d.get("message", "")
            if level == "WARNING":
                # Always visible
                self.c.print(
                    f"WARNING: {msg}", style="yellow", markup=False,
                )
            elif level == "ERROR":
                # Always visible
                self.c.print(
                    f"ERROR: {msg}", style="red", markup=False,
                )
            elif level == "NOTICE":
                if self._is_verbose():
                    self.c.print(
                        f"  {msg}", style="dim", markup=False,
                    )
                # Default: suppressed

        elif t == "checkpoint_created":
            self.spinner.stop_silent()
            if self._is_verbose():
                before = d.get("before", 0)
                after = d.get("after", 0)
                self.c.print(
                    f"  Compacted: {before} messages \u2192 {after}",
                    style="dim", markup=False,
                )
            # Default: suppressed

        elif t == "approval_required":
            self.spinner.stop_silent()
            action = d.get("action", "")
            detail = d.get("detail", "")
            # Always visible regardless of verbosity
            self.c.print(
                f"[action] {action} {detail}",
                style="bold", markup=False,
            )
            self.c.print(
                "Approve? [ y = yes, n = no, a = all ] ", end="", markup=False,
            )
            time.sleep(1.5)
            self.c.print("y = yes", style="bold", markup=False)


def play_mode(console: Console, mode: str, events: list[MockEvent]):
    """Play one verbosity mode."""
    renderer = ProgressiveRenderer(console, verbosity=mode)
    flag = {"default": "(no flag)", "verbose": "--verbose", "debug": "--debug"}
    console.print(
        f"\n--- {mode.upper()} mode {flag[mode]} ---\n",
        style="bold",
    )
    console.print("> fix the import error in parser.py\n", markup=False)
    play_events(events, renderer.handle, renderer.tick)
    console.print()


def main():
    console = create_console()

    console.print(
        "\n=== Approach E: Progressive Disclosure ===", style="bold",
    )
    console.print(
        "Plays 3 modes sequentially: default -> verbose -> debug\n",
        style="dim",
    )

    for mode in ("default", "verbose", "debug"):
        events = reference_scenario()
        play_mode(console, mode, events)
        if mode != "debug":
            console.print(
                "\n" + "=" * 55 + "\n", style="dim",
            )


if __name__ == "__main__":
    main()
