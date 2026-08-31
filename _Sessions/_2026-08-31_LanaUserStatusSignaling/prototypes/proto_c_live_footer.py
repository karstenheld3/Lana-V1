"""Prototype C: Live Footer (zero Rich dependency)

Two rendering surfaces: scrollback (permanent) + footer (ephemeral).
Scrollback: model text, errors, approvals only.
Footer: real-time status with box-drawing border, updated via ANSI escapes.
Reference: LANAUSRX-IN03 Section 5.3
"""

import shutil
import sys
import textwrap
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proto_shared import (
    APPROVAL_PAUSE, COMPACT_DELAY, FAST_TOOL, MockEvent, SLOW_TOOL,
    TEXT_CHAR, THINK_TICK, TURN_GAP,
    format_duration, play_events, reference_scenario,
)

# ---------------------------------------------------------------------------
# ANSI helpers (replaces Rich)
# ---------------------------------------------------------------------------

_RST = "\033[0m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BCYAN = "\033[1;36m"  # bold cyan

def _styled(text: str, style: str) -> str:
    return f"{style}{text}{_RST}"

def _print(text: str = "", style: str = "", end: str = "\n"):
    if style:
        sys.stdout.write(f"{style}{text}{_RST}{end}")
    else:
        sys.stdout.write(f"{text}{end}")
    sys.stdout.flush()

def _type_text(text: str, delay: float = TEXT_CHAR, prefix: str = ""):
    width = shutil.get_terminal_size((80, 24)).columns
    usable = width - len(prefix) - 1
    lines = textwrap.wrap(text, width=usable) if usable > 20 else [text]
    for i, line in enumerate(lines):
        if i > 0:
            sys.stdout.write(f"{_DIM}{prefix}{_RST}")
        for ch in line:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write("\n")
    sys.stdout.flush()

# ---------------------------------------------------------------------------
# Footer via ANSI cursor control
# ---------------------------------------------------------------------------

# Braille dots spinner frames
_SPINNER = ["\u280b", "\u2819", "\u2839", "\u2838", "\u283c", "\u2834", "\u2826", "\u2827", "\u2807", "\u280f"]

# Left bracket scope
_BRK = "\u2502 "
_BRK_EMPTY = "\u2502"

# Footer is 3 lines: top border, content, bottom border
_FOOTER_LINES = 3
_UP = f"\033[{_FOOTER_LINES}F"  # cursor up N lines
_CLR = "\033[K"                  # clear to end of line
_HIDE_CUR = "\033[?25l"          # hide cursor
_SHOW_CUR = "\033[?25h"          # show cursor


def _footer_text(spinner_char: str, activity: str, elapsed: int,
                 tool_count: int, total_tools: int, cost: float) -> list[str]:
    """Build 3 footer lines with box border and bracket prefix."""
    elapsed_str = format_duration(elapsed) if elapsed > 0 else ""
    parts = []
    act_part = activity or ""
    if elapsed_str:
        act_part = f"{act_part} {elapsed_str}" if act_part else elapsed_str
    if act_part:
        parts.append(act_part)
    if total_tools > 0:
        parts.append(f"{tool_count}/{total_tools} tools")
    if cost > 0:
        parts.append(f"${cost:.3f}")
    content = " | ".join(parts)
    inner = f"{spinner_char} {content}"
    width = max(len(inner) + 4, 60)
    top = "\u250c" + "\u2500" * (width - 2) + "\u2510"
    mid = "\u2502 " + inner.ljust(width - 3) + "\u2502"
    bot = "\u2514" + "\u2500" * (width - 2) + "\u2518"
    return [f"{_BRK}{top}", f"{_BRK}{mid}", f"{_BRK}{bot}"]


class LiveFooterRenderer:
    """Renders events per Approach C: Live Footer (Section 5.3)."""

    def __init__(self):
        self._footer_active: bool = False
        self._start_time: float = 0.0
        self._spinner_idx: int = 0
        self._activity: str = ""
        self._turn_count: int = 0
        self._tool_count: int = 0
        self._total_tools: int = 0
        self._total_cost: float = 0.0
        self._thinking: bool = False
        self._had_text: bool = False
        self._session_start: float = time.monotonic()

    def _spinner_char(self) -> str:
        return _SPINNER[self._spinner_idx % len(_SPINNER)]

    def _draw_footer(self):
        """Draw footer (3 lines) at current cursor position."""
        elapsed = int(time.monotonic() - self._start_time) if self._start_time else 0
        lines = _footer_text(
            self._spinner_char(), self._activity, elapsed,
            self._tool_count, self._total_tools, self._total_cost,
        )
        sys.stdout.write(_HIDE_CUR)
        for line in lines:
            sys.stdout.write(f"{_DIM}{_CLR}{line}{_RST}\n")
        sys.stdout.flush()
        self._footer_active = True

    def _update_footer(self):
        """Redraw footer in-place using ANSI cursor up."""
        if not self._footer_active:
            return
        sys.stdout.write(_UP)
        self._draw_footer()

    def _start_footer(self, activity: str):
        self._activity = activity
        self._start_time = time.monotonic()
        if not self._footer_active:
            self._draw_footer()
        else:
            self._update_footer()

    def _stop_footer(self):
        """Erase footer by moving up and clearing lines."""
        if not self._footer_active:
            return
        sys.stdout.write(_UP)
        for _ in range(_FOOTER_LINES):
            sys.stdout.write(f"{_CLR}\n")
        sys.stdout.write(_UP)
        sys.stdout.write(_SHOW_CUR)
        sys.stdout.flush()
        self._footer_active = False

    def _pause_footer(self):
        self._stop_footer()

    def _resume_footer(self):
        if self._activity:
            self._draw_footer()

    def tick(self):
        self._spinner_idx += 1
        self._update_footer()

    def handle(self, event: MockEvent):
        t = event.event_type
        d = event.data

        if t == "turn_started":
            self._turn_count += 1
            self._start_footer("thinking...")
            self._thinking = True

        elif t == "thinking_delta":
            self._update_footer()

        elif t == "text_delta":
            self._thinking = False
            self._activity = ""
            self._stop_footer()
            if self._had_text:
                _print(_BRK_EMPTY, _DIM)
            sys.stdout.write(f"{_DIM}{_BRK}{_RST}")
            sys.stdout.flush()
            _type_text(d["text"], prefix=_BRK)
            self._had_text = True

        elif t == "tool_call_requested":
            self._thinking = False
            self._total_tools += 1
            name = d["name"]
            self._start_footer(f"running {name}...")

        elif t == "tool_call_finished":
            self._tool_count += 1
            self._activity = "working..."
            self._update_footer()

        elif t == "turn_finished":
            self._thinking = False
            cost = d.get("cost", 0)
            self._total_cost += cost
            self._activity = f"turn {self._turn_count} complete"
            self._update_footer()

        elif t == "error":
            level = d.get("level", "ERROR")
            msg = d.get("message", "")
            if level == "WARNING":
                self._pause_footer()
                _print(_BRK_EMPTY, _DIM)
                _print(f"{_BRK}WARNING: {msg}", _YELLOW)
                self._resume_footer()
            elif level == "ERROR":
                self._pause_footer()
                _print(_BRK_EMPTY, _DIM)
                _print(f"{_BRK}ERROR: {msg}", _RED)
                self._resume_footer()
            elif level == "NOTICE":
                self._activity = msg
                self._update_footer()

        elif t == "checkpoint_created":
            before = d.get("before", 0)
            after = d.get("after", 0)
            self._activity = f"compacted: {before} \u2192 {after}"
            self._update_footer()

        elif t == "approval_required":
            self._stop_footer()
            action = d.get("action", "")
            detail = d.get("detail", "")
            content = f"{action} {detail}"
            prompt = "Approve? [ y = yes, n = no, a = all ]"
            answer_line = "Answer: y = yes"
            box_w = max(len(content), len(prompt), len(answer_line)) + 4
            label = "[ Action ]"
            bdr = "\u2500"
            top = f"\u250c\u2500{label}" + bdr * (box_w - 2 - 1 - len(label)) + "\u2510"
            mid = "\u2502 " + content.ljust(box_w - 3) + "\u2502"
            prm = "\u2502 " + prompt.ljust(box_w - 3) + "\u2502"
            sep = "\u251c" + bdr * (box_w - 2) + "\u2524"
            bot = "\u2514" + bdr * (box_w - 2) + "\u2518"
            _print(_BRK_EMPTY, _DIM)
            _print(f"{_BRK}{top}", _BCYAN)
            _print(f"{_BRK}{mid}", _BCYAN)
            _print(f"{_BRK}{prm}", _BCYAN)
            _print(f"{_BRK}{sep}", _BCYAN)
            _print(f"{_BRK}\u2502 Answer: ", _BCYAN, end="")
            time.sleep(1.5)
            answer_text = "y = yes"
            pad = box_w - 3 - len("Answer: ") - len(answer_text)
            _print(answer_text + " " * max(pad, 0) + "\u2502", _BCYAN)
            _print(f"{_BRK}{bot}", _BCYAN)
            _print(_BRK_EMPTY, _DIM)


# ---------------------------------------------------------------------------
# Demo scenarios covering all interaction types
# ---------------------------------------------------------------------------

def scenario_pure_text():
    """Prompt 1: Pure Q&A - no tools, just model text response."""
    return [
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "recalling config module"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "structure"}, pre_delay=THINK_TICK),
        MockEvent("text_delta", {
            "text": "The config module loads settings from `lana-config.json` at startup. "
                    "It validates required fields (model, provider, temperature) and "
                    "falls back to defaults for optional ones.",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 1200, "output_tokens": 58,
            "cached_tokens": 900, "cost": 0.001,
        }, pre_delay=0.2),
    ]

def scenario_multi_tool():
    """Prompt 2: Multiple fast tools + slow tool - the original reference scenario."""
    return reference_scenario()

def scenario_tool_failure():
    """Prompt 3: Tool failure, WARNING, retry, recovery."""
    return [
        # Turn 1: attempt edit, tool fails, retry succeeds
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "plan refactoring"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "steps"}, pre_delay=THINK_TICK),
        MockEvent("text_delta", {
            "text": "I'll refactor the database connection pooling.",
        }, pre_delay=0.3),
        MockEvent("tool_call_requested", {
            "name": "read_file", "args": "'src/db.py'",
        }),
        MockEvent("tool_call_finished", {
            "name": "read_file", "status": "ok",
            "chars": 1520, "display": "1520 chars.",
            "duration_secs": 0.9,
        }, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {
            "name": "read_file", "args": "'src/db_utils.py'",
        }),
        MockEvent("tool_call_finished", {
            "name": "read_file", "status": "ok",
            "chars": 890, "display": "890 chars.",
            "duration_secs": 0.6,
        }, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {
            "name": "edit", "args": "'src/db.py'",
        }),
        MockEvent("tool_call_finished", {
            "name": "edit", "status": "error",
            "chars": 0, "display": "FAIL",
            "duration_secs": 0.3,
        }, pre_delay=FAST_TOOL),
        # Error breaks through
        MockEvent("error", {
            "level": "ERROR",
            "message": "Edit failed: file is read-only (src/db.py)",
        }, pre_delay=0.3),
        MockEvent("error", {
            "level": "NOTICE",
            "message": "Retrying with elevated permissions",
        }, pre_delay=0.5),
        # Retry succeeds
        MockEvent("tool_call_requested", {
            "name": "edit", "args": "'src/db.py'",
        }),
        MockEvent("tool_call_finished", {
            "name": "edit", "status": "ok",
            "chars": 1, "display": "OK.",
            "duration_secs": 0.4,
        }, pre_delay=FAST_TOOL),
        MockEvent("turn_finished", {
            "input_tokens": 3800, "output_tokens": 210,
            "cached_tokens": 2900, "cost": 0.005,
        }, pre_delay=0.3),
    ]

def scenario_deploy_approval():
    """Prompt 4: Approval gate + long-running deploy + error mid-operation."""
    return [
        # Turn 1: ask for approval, run deploy
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "deployment steps"}, pre_delay=THINK_TICK),
        MockEvent("text_delta", {
            "text": "I'll deploy the current build to staging.",
        }, pre_delay=0.3),
        MockEvent("approval_required", {
            "action": "run_command",
            "detail": "deploy --env staging --tag v1.2.3",
        }, pre_delay=0.5),
        MockEvent("tool_call_requested", {
            "name": "run_command", "args": "'deploy --env staging --tag v1.2.3'",
        }),
        MockEvent("tool_call_finished", {
            "name": "run_command", "status": "ok",
            "chars": 3420, "display": "3420 chars.",
            "duration_secs": 18.5,
        }, pre_delay=SLOW_TOOL + 2.0),
        MockEvent("turn_finished", {
            "input_tokens": 2100, "output_tokens": 45,
            "cached_tokens": 1800, "cost": 0.002,
        }, pre_delay=0.3),
        # Turn 2: report result
        MockEvent("turn_started", {}, pre_delay=TURN_GAP),
        MockEvent("thinking_delta", {"text": "check output"}, pre_delay=THINK_TICK),
        MockEvent("text_delta", {
            "text": "Deployment complete. Build v1.2.3 is live on staging. "
                    "Health check passed: 3/3 endpoints responding.",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 5600, "output_tokens": 38,
            "cached_tokens": 5200, "cost": 0.002,
        }, pre_delay=0.2),
    ]

def scenario_compaction_heavy():
    """Prompt 5: Long conversation triggers compaction + multi-turn."""
    return [
        # Turn 1: thinking, text
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "analyzing"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "test coverage"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "gaps"}, pre_delay=THINK_TICK),
        MockEvent("text_delta", {
            "text": "Looking at the test coverage report for the auth module.",
        }, pre_delay=0.3),
        MockEvent("tool_call_requested", {
            "name": "run_command", "args": "'pytest --cov=auth tests/'",
        }),
        MockEvent("tool_call_finished", {
            "name": "run_command", "status": "ok",
            "chars": 4200, "display": "4200 chars.",
            "duration_secs": 8.2,
        }, pre_delay=SLOW_TOOL),
        MockEvent("turn_finished", {
            "input_tokens": 8200, "output_tokens": 156,
            "cached_tokens": 7500, "cost": 0.008,
        }, pre_delay=0.3),
        # Compaction happens between turns
        MockEvent("checkpoint_created", {
            "before": 86, "after": 32,
        }, pre_delay=COMPACT_DELAY),
        MockEvent("error", {
            "level": "WARNING",
            "message": "Token budget at 92%, compacted context",
        }, pre_delay=0.3),
        MockEvent("error", {
            "level": "NOTICE",
            "message": "Resuming after compaction",
        }, pre_delay=0.2),
        # Turn 2: analysis result
        MockEvent("turn_started", {}, pre_delay=TURN_GAP),
        MockEvent("thinking_delta", {"text": "interpreting"}, pre_delay=THINK_TICK),
        MockEvent("text_delta", {
            "text": "Coverage is 67%. The main gaps are in `token_refresh()` "
                    "and `session_validate()`. I'll write tests for both.",
        }, pre_delay=0.3),
        MockEvent("tool_call_requested", {
            "name": "write_file", "args": "'tests/test_token_refresh.py'",
        }),
        MockEvent("tool_call_finished", {
            "name": "write_file", "status": "ok",
            "chars": 1, "display": "OK.",
            "duration_secs": 0.3,
        }, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {
            "name": "write_file", "args": "'tests/test_session_validate.py'",
        }),
        MockEvent("tool_call_finished", {
            "name": "write_file", "status": "ok",
            "chars": 1, "display": "OK.",
            "duration_secs": 0.4,
        }, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {
            "name": "run_command", "args": "'pytest --cov=auth tests/'",
        }),
        MockEvent("tool_call_finished", {
            "name": "run_command", "status": "ok",
            "chars": 5100, "display": "5100 chars.",
            "duration_secs": 9.1,
        }, pre_delay=SLOW_TOOL),
        MockEvent("turn_finished", {
            "input_tokens": 9400, "output_tokens": 280,
            "cached_tokens": 8800, "cost": 0.010,
        }, pre_delay=0.3),
        # Turn 3: final summary
        MockEvent("turn_started", {}, pre_delay=TURN_GAP),
        MockEvent("thinking_delta", {"text": "done"}, pre_delay=THINK_TICK),
        MockEvent("text_delta", {
            "text": "Coverage improved to 89%. All 24 tests pass.",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 9800, "output_tokens": 22,
            "cached_tokens": 9400, "cost": 0.003,
        }, pre_delay=0.2),
    ]


def play_prompt(prompt: str, events: list[MockEvent],
                model: str = "claude-4-sonnet", context_pct: int = 80,
                context_total: str = "0.2M"):
    """Play one prompt with left-bracket scoping."""
    renderer = LiveFooterRenderer()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    header = f"[ {model} | {context_pct}% (of {context_total} context) | {ts} ]"
    _print(f"> {prompt}")
    _print(f"\u250c\u2500{header}", _DIM)
    _print(_BRK_EMPTY, _DIM)

    play_events(events, renderer.handle, renderer.tick)

    renderer._stop_footer()
    _print(_BRK_EMPTY, _DIM)
    total_cost = renderer._total_cost
    turns = renderer._turn_count
    tools = renderer._tool_count
    total_elapsed = int(time.monotonic() - renderer._session_start)
    summary = f"{turns} turn{'s' if turns != 1 else ''} | {tools} tool{'s' if tools != 1 else ''} | ${total_cost:.3f} | {format_duration(total_elapsed)}"
    _print(f"\u2514\u2500[ {summary} ]", _DIM)
    _print()


def main():
    _print(f"\n{_BOLD}=== Approach C: Live Footer ==={_RST}\n")

    prompts = [
        ("what does the config module do?", scenario_pure_text()),
        ("fix the import error in parser.py", scenario_multi_tool()),
        ("refactor the database connection pooling", scenario_tool_failure()),
        ("deploy the current build to staging", scenario_deploy_approval()),
        ("improve auth module test coverage", scenario_compaction_heavy()),
    ]

    for i, (prompt, events) in enumerate(prompts):
        if i > 0:
            _print()
            time.sleep(1.0)
        play_prompt(prompt, events)


if __name__ == "__main__":
    main()
