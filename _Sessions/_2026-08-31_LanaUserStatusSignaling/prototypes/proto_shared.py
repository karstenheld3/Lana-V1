"""Shared mock event infrastructure for CLI console design prototypes.

Reference: LANAUSRX-IN03 Section 2 (Reference Scenario)
           LANAUSRX-IN03 Section 1.1 (CLI Color Map)
"""

import time
from dataclasses import dataclass, field

from rich.console import Console
from rich.status import Status


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class MockEvent:
    """A mock agent event for prototype playback."""

    event_type: str
    data: dict = field(default_factory=dict)
    pre_delay: float = 0.0  # seconds to wait BEFORE this event


# ---------------------------------------------------------------------------
# Timing constants (compressed for movie playback)
# ---------------------------------------------------------------------------

THINK_TICK = 0.7  # per thinking_delta tick (~3s total per 4 ticks)
FAST_TOOL = 0.5  # fast tool execution (<2 secs real)
SLOW_TOOL = 4.0  # slow tool (pytest 12s -> 4s compressed)
TURN_GAP = 1.0  # gap between turns (post-turn dead air)
COMPACT_DELAY = 0.8  # compaction event
APPROVAL_PAUSE = 2.0  # approval prompt visible
TEXT_CHAR = 0.015  # per character typing delay


# ---------------------------------------------------------------------------
# Formatting helpers (LOG-GN-04 compliant)
# ---------------------------------------------------------------------------

def format_duration(seconds) -> str:
    """Format duration: '1 sec' or 'N secs'. Never 's' or 'm'."""
    seconds = int(seconds)
    if seconds == 1:
        return "1 sec"
    return f"{seconds} secs"


def format_tokens(count: int) -> str:
    """Format token count as 'N.NK' for display."""
    if count >= 1000:
        k = count / 1000
        if k == int(k):
            return f"{int(k)}K"
        return f"{k:.1f}K"
    return str(count)


def format_chars(count: int) -> str:
    """Format char count with singular/plural."""
    if count == 1:
        return "1 char."
    return f"{count} chars."


# ---------------------------------------------------------------------------
# Console factory
# ---------------------------------------------------------------------------

def create_console() -> Console:
    """Create Rich Console with markup=False (BG-0004)."""
    return Console(markup=False)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def type_text(console: Console, text: str, style: str = "", end: str = "\n"):
    """Simulate character-by-character text output (streaming effect)."""
    for char in text:
        kwargs = {"end": "", "markup": False}
        if style:
            kwargs["style"] = style
        console.print(char, **kwargs)
        time.sleep(TEXT_CHAR)
    if end:
        console.print(end, end="", markup=False)


# ---------------------------------------------------------------------------
# Spinner helper
# ---------------------------------------------------------------------------

class SpinnerManager:
    """Manages a Rich Status spinner with elapsed time display."""

    def __init__(self, console: Console):
        self.console = console
        self._status: Status | None = None
        self._start_time: float = 0
        self._base_text: str = ""
        self._style: str = "dim"

    @property
    def active(self) -> bool:
        return self._status is not None

    def start(self, text: str, style: str = "dim"):
        """Start spinner with given text. Elapsed time appended on tick()."""
        self.stop_silent()
        self._base_text = text
        self._style = style
        self._start_time = time.monotonic()
        self._status = Status(
            text,
            console=self.console,
            spinner="dots",
            spinner_style=style,
        )
        self._status.start()

    def tick(self):
        """Update spinner text with current elapsed time."""
        if self._status:
            elapsed = int(time.monotonic() - self._start_time)
            if elapsed > 0:
                dur = format_duration(elapsed)
                self._status.update(f"{self._base_text} {dur}")

    def stop(self) -> int:
        """Stop spinner, return elapsed seconds."""
        elapsed = int(time.monotonic() - self._start_time) if self._start_time else 0
        self.stop_silent()
        return elapsed

    def stop_silent(self):
        """Stop spinner without returning elapsed."""
        if self._status:
            self._status.stop()
            self._status = None
        self._start_time = 0

    @property
    def elapsed(self) -> int:
        if self._start_time:
            return int(time.monotonic() - self._start_time)
        return 0


# ---------------------------------------------------------------------------
# Event playback
# ---------------------------------------------------------------------------

def play_events(events: list[MockEvent], handler, tick_fn=None):
    """Play events through a handler with timing delays.

    handler: callable(event) -> None
    tick_fn: callable() -> None, called every 0.1s during delays
    """
    for event in events:
        if event.pre_delay > 0:
            remaining = event.pre_delay
            while remaining > 0:
                step = min(0.1, remaining)
                time.sleep(step)
                remaining -= step
                if tick_fn:
                    tick_fn()
        handler(event)


# ---------------------------------------------------------------------------
# Reference scenario
# ---------------------------------------------------------------------------

def reference_scenario() -> list[MockEvent]:
    """3-turn reference scenario + extended events (compaction, approval).

    From LANAUSRX-IN03 Section 2:
    - Turn 1: Think ~1.6s, type, read_file (fast), edit (fast)
    - Turn 2: Think ~1.2s, type, run_command/pytest (slow, 3s)
    - Extended: checkpoint, WARNING, NOTICE, approval
    - Turn 3: Think ~0.6s, type final answer

    Total compressed playback: ~12 secs
    """
    return [
        # === Turn 1 ===
        MockEvent("turn_started", {"turn": 1}),
        MockEvent("thinking_delta", {"text": "analyzing"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "found issue"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "planning fix"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "will read file"}, pre_delay=THINK_TICK),
        MockEvent("text_delta", {
            "text": "I'll read parser.py to find the import error.",
        }),
        MockEvent("tool_call_requested", {
            "name": "read_file", "args": "'src/parser.py'",
        }),
        MockEvent("tool_call_finished", {
            "name": "read_file", "status": "ok",
            "chars": 234, "display": "234 chars.",
            "duration_secs": 0.8,
        }, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {
            "name": "edit", "args": "'src/parser.py'",
        }),
        MockEvent("tool_call_finished", {
            "name": "edit", "status": "ok",
            "chars": 1, "display": "OK.",
            "duration_secs": 0.2,
        }, pre_delay=0.1),
        MockEvent("turn_finished", {
            "input_tokens": 4521, "output_tokens": 187,
            "cost": 0.003, "cached_tokens": 3800,
        }),

        # === Turn 2 ===
        MockEvent("turn_started", {"turn": 2}, pre_delay=TURN_GAP),
        MockEvent("thinking_delta", {"text": "need to verify"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "will run tests"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "preparing"}, pre_delay=THINK_TICK),
        MockEvent("text_delta", {
            "text": "Running tests to verify.",
        }),
        MockEvent("tool_call_requested", {
            "name": "run_command", "args": "'pytest tests/test_parser.py'",
        }),
        MockEvent("tool_call_finished", {
            "name": "run_command", "status": "ok",
            "chars": 892, "display": "892 chars.",
            "duration_secs": 12.3,
        }, pre_delay=SLOW_TOOL),
        MockEvent("turn_finished", {
            "input_tokens": 5200, "output_tokens": 94,
            "cost": 0.004, "cached_tokens": 4800,
        }),

        # === Extended: compaction + warning + notice + approval ===
        MockEvent("checkpoint_created", {
            "before": 42, "after": 18,
        }, pre_delay=COMPACT_DELAY),
        MockEvent("error", {
            "level": "WARNING",
            "message": "Token budget exceeded, compacted context",
        }),
        MockEvent("error", {
            "level": "NOTICE",
            "message": "Resuming after compaction",
        }, pre_delay=0.3),
        MockEvent("approval_required", {
            "action": "run_command",
            "detail": "rm -rf build/ && make clean",
        }, pre_delay=0.5),

        # === Turn 3 ===
        MockEvent("turn_started", {"turn": 3}, pre_delay=TURN_GAP),
        MockEvent("thinking_delta", {"text": "confirmed"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "summarizing"}, pre_delay=THINK_TICK),
        MockEvent("text_delta", {
            "text": "Fixed. Changed `json_parser` to `parser_core` on "
                    "line 3. All 12 tests pass.",
        }),
        MockEvent("turn_finished", {
            "input_tokens": 5800, "output_tokens": 42,
            "cost": 0.002, "cached_tokens": 5400,
        }),
    ]


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    console = create_console()
    events = reference_scenario()
    total_delay = sum(e.pre_delay for e in events)
    console.print(f"Reference scenario: {len(events)} events", style="bold")
    for i, e in enumerate(events):
        delay = f"  (+{e.pre_delay:.1f}s)" if e.pre_delay > 0 else ""
        console.print(
            f"  {i + 1:2d}. {e.event_type}{delay}",
            style="dim", markup=False,
        )
    console.print(f"\nTotal delay: {total_delay:.1f} secs", style="bold")
