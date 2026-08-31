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
    COMPACT_DELAY, FAST_TOOL, MockEvent, SLOW_TOOL,
    TEXT_CHAR, THINK_TICK, TURN_GAP,
    format_duration, play_events,
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

def _strip_time_unit(entry: str) -> str:
    """Strip trailing ' secs' or ' sec' from a log entry, keeping just the number."""
    if entry.endswith(" secs"):
        return entry[:-5]
    if entry.endswith(" sec"):
        return entry[:-4]
    return entry

_CLR = "\033[K"                  # clear to end of line
_HIDE_CUR = "\033[?25l"          # hide cursor
_SHOW_CUR = "\033[?25h"          # show cursor
_MIN_BOX_W = 60                  # min footer box width


class LiveFooterRenderer:
    """Renders events per Approach C: Live Footer (Section 5.3).

    The footer box grows line-by-line as activities happen (thinking,
    tool calls, etc.). When the turn ends or text begins, the box
    collapses into a single dim summary line in scrollback.
    """

    def __init__(self):
        self._footer_active: bool = False
        self._footer_line_count: int = 0  # current rendered line count
        self._start_time: float = 0.0
        self._spinner_idx: int = 0
        self._activity: str | list[str] = ""  # str or list for multi-line
        self._current_tool_short: str = ""  # short name (e.g. "running edit...")
        self._current_tool_sig_single: str = ""  # full single-line sig for log
        self._log: list[str] = []  # chronological activity entries
        self._turn_count: int = 0
        self._tool_count: int = 0
        self._total_tools: int = 0
        self._total_cost: float = 0.0
        self._thinking: bool = False
        self._had_text: bool = False
        self._session_start: float = time.monotonic()

    def _spinner_char(self) -> str:
        return _SPINNER[self._spinner_idx % len(_SPINNER)]

    def _box_width(self) -> int:
        max_entry = max((len(e) for e in self._log), default=0)
        # spinner + space + longest entry + padding
        return max(max_entry + 8, _MIN_BOX_W)

    def _format_tool_signature(self, name: str, args: str) -> list[str]:
        """Format tool call as running [ name(args) ]... with multi-line overflow."""
        if not args:
            return [f"running [ {name}() ]..."]
        # Parse comma-separated args
        arg_list = [a.strip().strip("'\"") for a in args.split(",")]
        single = f"running [ {name}({', '.join(arg_list)}) ]..."
        if len(single) < self._box_width() - 6:
            return [single]
        # Multi-line: tool name on first line, params indented, closing on own line
        result = [f"running [ {name}("]
        for i, arg in enumerate(arg_list):
            suffix = "," if i < len(arg_list) - 1 else ""
            result.append(f"      {arg}{suffix}")
        result.append("  ) ]...")
        return result

    def _build_footer_lines(self, finalized: bool = False) -> list[str]:
        """Build the activity box.

        finalized=False: growing box with spinner on active line.
        finalized=True:  static box for permanent scrollback (no spinner).
        """
        w = self._box_width()
        bdr = "\u2500"
        lines = []
        # Top border
        lines.append(f"{_BRK}\u250c{bdr * (w - 2)}\u2510")
        # Completed log entries
        for entry in self._log:
            lines.append(f"{_BRK}\u2502 {entry.ljust(w - 3)}\u2502")
        if not finalized:
            # Active line(s) with spinner on first line
            elapsed = int(time.monotonic() - self._start_time) if self._start_time else 0
            elapsed_str = f" {format_duration(elapsed)}" if elapsed > 0 else ""
            if isinstance(self._activity, list):
                for i, part in enumerate(self._activity):
                    if i == 0:
                        active = f"{self._spinner_char()} {part}"
                    else:
                        active = f"  {part}"
                        if i == len(self._activity) - 1:
                            active = f"  {part.rstrip()}"
                    lines.append(f"{_BRK}\u2502 {active.ljust(w - 3)}\u2502")
            else:
                active = f"{self._spinner_char()} {self._activity}{elapsed_str}"
                lines.append(f"{_BRK}\u2502 {active.ljust(w - 3)}\u2502")
        # Bottom border
        lines.append(f"{_BRK}\u2514{bdr * (w - 2)}\u2518")
        return lines

    def _draw_footer(self):
        """Draw footer at current cursor position."""
        lines = self._build_footer_lines()
        sys.stdout.write(_HIDE_CUR)
        for line in lines:
            sys.stdout.write(f"{_DIM}{_CLR}{line}{_RST}\n")
        sys.stdout.flush()
        self._footer_line_count = len(lines)
        self._footer_active = True

    def _update_footer(self):
        """Redraw footer in-place. Handles growing box."""
        if not self._footer_active:
            return
        new_lines = self._build_footer_lines()
        # Move up by OLD line count, redraw with NEW line count
        if self._footer_line_count > 0:
            sys.stdout.write(f"\033[{self._footer_line_count}F")
        sys.stdout.write(_HIDE_CUR)
        for line in new_lines:
            sys.stdout.write(f"{_DIM}{_CLR}{line}{_RST}\n")
        # Clear any leftover lines if box shrank (shouldn't happen but safe)
        for _ in range(max(0, self._footer_line_count - len(new_lines))):
            sys.stdout.write(f"{_CLR}\n")
        sys.stdout.flush()
        self._footer_line_count = len(new_lines)

    def _erase_footer(self):
        """Erase all footer lines from screen."""
        if not self._footer_active:
            return
        if self._footer_line_count > 0:
            sys.stdout.write(f"\033[{self._footer_line_count}F")
        for _ in range(self._footer_line_count):
            sys.stdout.write(f"{_CLR}\n")
        if self._footer_line_count > 0:
            sys.stdout.write(f"\033[{self._footer_line_count}F")
        sys.stdout.write(_SHOW_CUR)
        sys.stdout.flush()
        self._footer_active = False
        self._footer_line_count = 0

    def _collapse_footer(self):
        """Finalize the activity box as permanent scrollback.

        Redraws the box in-place without the spinner/active line,
        leaving only completed log entries inside the box borders.
        """
        if not self._footer_active:
            if self._log:
                # Footer was never drawn (e.g. paused), draw finalized box fresh
                final_lines = self._build_footer_lines(finalized=True)
                for line in final_lines:
                    sys.stdout.write(f"{_DIM}{_CLR}{line}{_RST}\n")
                sys.stdout.write(_SHOW_CUR)
                sys.stdout.flush()
            self._log.clear()
            return
        # Redraw box in-place as finalized (no spinner, no active line)
        final_lines = self._build_footer_lines(finalized=True)
        if self._footer_line_count > 0:
            sys.stdout.write(f"\033[{self._footer_line_count}F")
        sys.stdout.write(_HIDE_CUR)
        for line in final_lines:
            sys.stdout.write(f"{_DIM}{_CLR}{line}{_RST}\n")
        # Clear leftover lines from the old (larger) box
        for _ in range(max(0, self._footer_line_count - len(final_lines))):
            sys.stdout.write(f"{_CLR}\n")
        if self._footer_line_count > len(final_lines):
            leftover = self._footer_line_count - len(final_lines)
            sys.stdout.write(f"\033[{leftover}F")
        sys.stdout.write(_SHOW_CUR)
        sys.stdout.flush()
        self._footer_active = False
        self._footer_line_count = 0
        self._log.clear()

    def _add_log(self, entry: str):
        """Freeze current activity into log, set new activity."""
        activity = self._activity
        if isinstance(activity, list):
            # Multi-line tool signature -> use short name for log
            activity = self._current_tool_short or "working..."
        if activity and activity not in ("working...",):
            elapsed = int(time.monotonic() - self._start_time) if self._start_time else 0
            self._log.append(f"{activity} {format_duration(elapsed)}")

    def _start_footer(self, activity: str):
        self._activity = activity
        self._start_time = time.monotonic()
        if not self._footer_active:
            self._draw_footer()
        else:
            self._update_footer()

    def _stop_footer(self):
        self._collapse_footer()

    def _pause_footer(self):
        self._erase_footer()

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
            self._log.clear()
            self._start_footer("thinking...")
            self._thinking = True

        elif t == "thinking_delta":
            self._update_footer()

        elif t == "text_delta":
            self._thinking = False
            self._add_log("thinking...")
            self._activity = ""
            self._stop_footer()
            if self._had_text:
                _print(_BRK_EMPTY, _DIM)
            sys.stdout.write(f"{_DIM}{_BRK}{_RST}")
            sys.stdout.flush()
            _type_text(d["text"], prefix=_BRK)
            self._had_text = True

        elif t == "tool_call_requested":
            if self._thinking:
                self._add_log("thinking...")
                self._thinking = False
            else:
                self._add_log(self._activity)
            self._total_tools += 1
            name = d["name"]
            args = d.get("args", "")
            sig_lines = self._format_tool_signature(name, args)
            self._current_tool_short = f"running [ {name}(...) ]..."
            # Always compute single-line signature for finalized log
            arg_list = [a.strip().strip("'\"")
                        for a in args.split(",")] if args else []
            self._current_tool_sig_single = (
                f"running [ {name}({', '.join(arg_list)}) ]..."
                if arg_list else f"running [ {name}() ]..."
            )
            if len(sig_lines) == 1:
                self._activity = sig_lines[0]
            else:
                self._activity = sig_lines
            self._start_time = time.monotonic()
            self._update_footer() if self._footer_active else self._start_footer(self._activity)

        elif t == "tool_call_finished":
            self._tool_count += 1
            status = d.get("status", "ok")
            if status == "error":
                # Log with FAIL suffix instead of elapsed time
                sig = self._current_tool_short or f"running [ {d.get('name', '')}(...) ]..."
                self._log.append(f"{sig} FAIL")
            else:
                self._add_log(self._activity)
            self._activity = "working..."
            self._current_tool_short = ""
            self._current_tool_sig_single = ""
            self._start_time = time.monotonic()
            self._update_footer()

        elif t == "turn_finished":
            self._thinking = False
            cost = d.get("cost", 0)
            self._total_cost += cost
            self._add_log(self._activity)
            self._stop_footer()

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
            self._add_log(self._activity)
            self._activity = f"compacted: {before} \u2192 {after}"
            self._start_time = time.monotonic()
            self._update_footer()

        elif t == "approval_required":
            self._add_log(self._activity)
            self._erase_footer()
            action = d.get("action", "")
            detail = d.get("detail", "")
            answer = d.get("answer", "y")  # y, n, or a
            content = f"{action} {detail}"
            prompt = "Approve? [ y = yes, n = no, a = all ]"
            answers = {"y": "y = yes", "n": "n = no", "a": "a = all"}
            answer_text = answers.get(answer, "y = yes")
            answer_line = f"Answer: {answer_text}"
            box_w = max(len(content), len(prompt), len(answer_line)) + 4
            label = "[ Approval ]"
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
            pad = box_w - 3 - len("Answer: ") - len(answer_text)
            _print(answer_text + " " * max(pad, 0) + "\u2502", _BCYAN)
            _print(f"{_BRK}{bot}", _BCYAN)
            _print(_BRK_EMPTY, _DIM)
            # Restart footer after approval
            self._log.clear()
            self._start_footer("working...")


# ---------------------------------------------------------------------------
# Demo scenarios matching SPEC cases 10.5 through 10.14
# ---------------------------------------------------------------------------

def scenario_pure_text():
    """Case 10.5: Pure Text Q&A (No Tools). Single turn, thinking only."""
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


def scenario_fast_tools():
    """Case 10.6: Single Turn with Fast Tools. Quick read + edit."""
    return [
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "finding typo"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "on line 5"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "planning fix"}, pre_delay=THINK_TICK),
        MockEvent("tool_call_requested", {
            "name": "read_file", "args": "path",
        }),
        MockEvent("tool_call_finished", {
            "name": "read_file", "status": "ok",
            "chars": 320, "display": "320 chars.",
        }, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {
            "name": "edit", "args": "path, old_string, new_string",
        }),
        MockEvent("tool_call_finished", {
            "name": "edit", "status": "ok",
            "chars": 1, "display": "OK.",
        }, pre_delay=0.1),
        MockEvent("text_delta", {
            "text": "Fixed the typo on line 5: changed `recieve` to `receive`.",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 2100, "output_tokens": 42,
            "cached_tokens": 1800, "cost": 0.002,
        }, pre_delay=0.2),
    ]


def scenario_multi_turn_approval():
    """Case 10.7: Multi-Turn with Tools, Approval, and Compaction."""
    return [
        # Turn 1: read + edit
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "analyzing"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "found issue"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "planning fix"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "will read file"}, pre_delay=THINK_TICK),
        MockEvent("tool_call_requested", {
            "name": "read_file", "args": "path",
        }),
        MockEvent("tool_call_finished", {
            "name": "read_file", "status": "ok",
            "chars": 234, "display": "234 chars.",
        }, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {
            "name": "edit", "args": "path, old_string, new_string",
        }),
        MockEvent("tool_call_finished", {
            "name": "edit", "status": "ok",
            "chars": 1, "display": "OK.",
        }, pre_delay=0.1),
        MockEvent("text_delta", {
            "text": "I'll read parser.py to find the import error.",
        }, pre_delay=0.2),
        MockEvent("turn_finished", {
            "input_tokens": 4521, "output_tokens": 187,
            "cost": 0.003, "cached_tokens": 3800,
        }),
        # WARNING between turns
        MockEvent("error", {
            "level": "WARNING",
            "message": "Token budget exceeded, compacted context",
        }, pre_delay=0.5),
        # Turn 2: approval + pytest
        MockEvent("turn_started", {}, pre_delay=TURN_GAP),
        MockEvent("thinking_delta", {"text": "need cleanup"}, pre_delay=THINK_TICK),
        MockEvent("approval_required", {
            "action": "run_command",
            "detail": "rm -rf build/ && make clean",
            "answer": "y",
        }, pre_delay=0.5),
        MockEvent("tool_call_requested", {
            "name": "run_command", "args": "cmd",
        }),
        MockEvent("tool_call_finished", {
            "name": "run_command", "status": "ok",
            "chars": 892, "display": "892 chars.",
        }, pre_delay=SLOW_TOOL),
        MockEvent("turn_finished", {
            "input_tokens": 5200, "output_tokens": 94,
            "cost": 0.004, "cached_tokens": 4800,
        }),
        # Turn 3: final answer
        MockEvent("turn_started", {}, pre_delay=TURN_GAP),
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


def scenario_tool_failure():
    """Case 10.8: Tool Failure, ERROR, Retry, Recovery."""
    return [
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "plan refactoring"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "steps"}, pre_delay=THINK_TICK),
        MockEvent("tool_call_requested", {
            "name": "read_file", "args": "path",
        }),
        MockEvent("tool_call_finished", {
            "name": "read_file", "status": "ok",
            "chars": 1520, "display": "1520 chars.",
        }, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {
            "name": "read_file", "args": "path",
        }),
        MockEvent("tool_call_finished", {
            "name": "read_file", "status": "ok",
            "chars": 890, "display": "890 chars.",
        }, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {
            "name": "edit", "args": "path, old_string, new_string",
        }),
        MockEvent("tool_call_finished", {
            "name": "edit", "status": "error",
            "chars": 0, "display": "FAIL",
        }, pre_delay=FAST_TOOL),
        MockEvent("error", {
            "level": "ERROR",
            "message": "Edit failed: file is read-only (src/db.py)",
        }, pre_delay=0.3),
        # Turn 2: retry succeeds
        MockEvent("turn_finished", {
            "input_tokens": 3800, "output_tokens": 90,
            "cached_tokens": 2900, "cost": 0.003,
        }, pre_delay=0.3),
        MockEvent("turn_started", {}, pre_delay=TURN_GAP),
        MockEvent("thinking_delta", {"text": "retry"}, pre_delay=THINK_TICK),
        MockEvent("tool_call_requested", {
            "name": "run_command", "args": "cmd",
        }),
        MockEvent("tool_call_finished", {
            "name": "run_command", "status": "ok",
            "chars": 1, "display": "OK.",
        }, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {
            "name": "edit", "args": "path, old_string, new_string",
        }),
        MockEvent("tool_call_finished", {
            "name": "edit", "status": "ok",
            "chars": 1, "display": "OK.",
        }, pre_delay=FAST_TOOL),
        MockEvent("text_delta", {
            "text": "Made the file writable and applied the refactoring. Connection "
                    "pooling now uses a shared pool with configurable max connections.",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 5200, "output_tokens": 210,
            "cached_tokens": 4500, "cost": 0.004,
        }, pre_delay=0.3),
    ]


def scenario_approval_denied():
    """Case 10.9: Approval Denied. User denies dangerous command."""
    return [
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "cleanup plan"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "identifying targets"}, pre_delay=THINK_TICK),
        MockEvent("approval_required", {
            "action": "run_command",
            "detail": "rm -rf /tmp/project_* && rm -rf ~/.cache/lana",
            "answer": "n",
        }, pre_delay=0.5),
        # After denial, agent takes different approach
        MockEvent("tool_call_requested", {
            "name": "run_command", "args": "cmd",
        }),
        MockEvent("tool_call_finished", {
            "name": "run_command", "status": "ok",
            "chars": 42, "display": "42 chars.",
        }, pre_delay=FAST_TOOL),
        MockEvent("text_delta", {
            "text": "Understood. I cleaned only the project build artifacts instead.",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 3200, "output_tokens": 35,
            "cached_tokens": 2800, "cost": 0.004,
        }, pre_delay=0.2),
    ]


def scenario_long_running():
    """Case 10.10: Long-Running Tool. Single tool dominates elapsed."""
    return [
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "preparing"}, pre_delay=THINK_TICK),
        MockEvent("tool_call_requested", {
            "name": "run_command", "args": "cmd",
        }),
        MockEvent("tool_call_finished", {
            "name": "run_command", "status": "ok",
            "chars": 12400, "display": "12400 chars.",
        }, pre_delay=SLOW_TOOL + 3.0),
        MockEvent("text_delta", {
            "text": "All 847 tests passed. No failures, 3 skipped.",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 4800, "output_tokens": 28,
            "cached_tokens": 4200, "cost": 0.003,
        }, pre_delay=0.2),
    ]


def scenario_heavy_compaction():
    """Case 10.11: Heavy Compaction with Many Tools. Many reads + compaction."""
    return [
        # Turn 1: many reads
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "analyzing"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "source tree"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "dependencies"}, pre_delay=THINK_TICK),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 800}, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 650}, pre_delay=0.2),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 920}, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 400}, pre_delay=0.2),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 1100}, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {"name": "grep_search", "args": "query, path"}),
        MockEvent("tool_call_finished", {"name": "grep_search", "status": "ok", "chars": 300}, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {"name": "grep_search", "args": "query, path"}),
        MockEvent("tool_call_finished", {"name": "grep_search", "status": "ok", "chars": 200}, pre_delay=0.2),
        MockEvent("text_delta", {
            "text": "I've analyzed the source tree. Here are the key dependencies:",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 18000, "output_tokens": 320,
            "cached_tokens": 16000, "cost": 0.015,
        }, pre_delay=0.3),
        # Turn 2: more reads
        MockEvent("turn_started", {}, pre_delay=TURN_GAP),
        MockEvent("thinking_delta", {"text": "deeper analysis"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "tracing imports"}, pre_delay=THINK_TICK),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 500}, pre_delay=0.2),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 600}, pre_delay=0.2),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 700}, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 450}, pre_delay=0.2),
        MockEvent("turn_finished", {
            "input_tokens": 22000, "output_tokens": 180,
            "cached_tokens": 20000, "cost": 0.012,
        }, pre_delay=0.3),
        # Compaction
        MockEvent("error", {
            "level": "WARNING",
            "message": "Context 95% full, compacting to preserve conversation",
        }, pre_delay=COMPACT_DELAY),
        # Turn 3: final
        MockEvent("turn_started", {}, pre_delay=TURN_GAP),
        MockEvent("thinking_delta", {"text": "summarizing"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "graph"}, pre_delay=THINK_TICK),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 300}, pre_delay=FAST_TOOL),
        MockEvent("tool_call_requested", {"name": "read_file", "args": "path"}),
        MockEvent("tool_call_finished", {"name": "read_file", "status": "ok", "chars": 200}, pre_delay=0.2),
        MockEvent("text_delta", {
            "text": "The complete dependency graph shows 4 clusters with 2 circular "
                    "dependencies between agent.py and tools/__init__.py.",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 18500, "output_tokens": 95,
            "cached_tokens": 17000, "cost": 0.014,
        }, pre_delay=0.2),
    ]


def scenario_provider_retry():
    """Case 10.12: Provider Retry with WARNING. Rate limit then recovery."""
    return [
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "analyzing"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "caching"}, pre_delay=THINK_TICK),
        # Rate limit hit
        MockEvent("error", {
            "level": "WARNING",
            "message": "Rate limit exceeded (429), retrying in 8 secs",
        }, pre_delay=0.3),
        # Retry after delay (simulated as longer thinking)
        MockEvent("thinking_delta", {"text": "retrying"}, pre_delay=SLOW_TOOL + 2.0),
        MockEvent("text_delta", {
            "text": "The caching strategy uses prompt caching for the system prompt "
                    "and tool definitions, reducing input tokens by 60-80%.",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 3200, "output_tokens": 52,
            "cached_tokens": 2800, "cost": 0.002,
        }, pre_delay=0.2),
    ]


def scenario_multi_line_params():
    """Case 10.2 Stage 5: Multi-line params overflow in activity box."""
    return [
        MockEvent("turn_started", {}),
        MockEvent("thinking_delta", {"text": "planning edit"}, pre_delay=THINK_TICK),
        MockEvent("thinking_delta", {"text": "preparing"}, pre_delay=THINK_TICK),
        MockEvent("tool_call_requested", {
            "name": "edit",
            "args": "file_path, old_string, new_string, explanation, replace_all",
        }),
        MockEvent("tool_call_finished", {
            "name": "edit", "status": "ok",
            "chars": 1, "display": "OK.",
        }, pre_delay=FAST_TOOL + 1.0),
        MockEvent("text_delta", {
            "text": "Applied the multi-parameter edit successfully.",
        }, pre_delay=0.3),
        MockEvent("turn_finished", {
            "input_tokens": 2800, "output_tokens": 22,
            "cached_tokens": 2400, "cost": 0.002,
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
    tc_label = 'tool call' if tools == 1 else 'tool calls'
    summary = f"{turns} turn{'s' if turns != 1 else ''} | {tools} {tc_label} | ${total_cost:.3f} | {format_duration(total_elapsed)}"
    _print(f"\u2514\u2500[ {summary} ]", _DIM)
    _print()


def main():
    _print(f"\n{_BOLD}=== Prototype C: Spec LANAUSRX-SP01 Demo ==={_RST}\n")

    prompts = [
        # Case 10.5: Pure text
        ("what does the config module do?",
         scenario_pure_text(), 80),
        # Case 10.6: Fast tools
        ("read the README and fix the typo on line 5",
         scenario_fast_tools(), 15),
        # Case 10.7: Multi-turn + approval + compaction
        ("fix the import error in parser.py",
         scenario_multi_turn_approval(), 12),
        # Case 10.8: Tool failure + ERROR + retry
        ("refactor the database connection pooling",
         scenario_tool_failure(), 45),
        # Case 10.9: Approval denied
        ("clean up all temporary files",
         scenario_approval_denied(), 30),
        # Case 10.10: Long-running tool
        ("run the full test suite",
         scenario_long_running(), 55),
        # Case 10.11: Heavy compaction + many tools
        ("analyze all source files and create a dependency graph",
         scenario_heavy_compaction(), 92),
        # Case 10.12: Provider retry
        ("explain the caching strategy",
         scenario_provider_retry(), 40),
        # Stage 5: Multi-line params overflow
        ("apply the complex edit to render.py",
         scenario_multi_line_params(), 25),
    ]

    for i, (prompt, events, ctx_pct) in enumerate(prompts):
        if i > 0:
            _print()
            time.sleep(1.0)
        play_prompt(prompt, events, context_pct=ctx_pct)


if __name__ == "__main__":
    main()
