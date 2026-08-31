"""Debug console viewer: reads JSONL lines from stdin, renders colorized aligned lines (LANADEBG-SP01 FR-06).

Runs in its own console window, spawned by debuglog.enable() with Lana's stdin pipe attached.
stdin EOF means Lana exited (EC-04) - the viewer announces it and waits for a keypress so the
tail of the log stays readable. Malformed lines render raw and dim, never crash the viewer (EC-06).
"""
import json, sys
from rich.console import Console

DOMAIN_STYLES = {"llm": "cyan", "tool": "green", "acp": "magenta", "app": "white"}
ERROR_OPS = ("error", "compaction_failed")


def format_cost(value) -> str:
  return "$?" if value is None else f"${value:.4f}"


# LOG-GN-04 duration format: '245 ms' | '1.5 secs' | '2 mins 30 secs' | '1 hour 15 mins'
def format_duration(ms) -> str:
  if ms < 1000: return f"{ms} ms"
  if ms < 60000: return f"{ms / 1000:.1f} secs"
  minutes, seconds = divmod(round(ms / 1000), 60)
  if minutes < 60: return f"{minutes} min" + ("s" if minutes != 1 else "") + f" {seconds} sec" + ("s" if seconds != 1 else "")
  hours, minutes = divmod(minutes, 60)
  return f"{hours} hour" + ("s" if hours != 1 else "") + f" {minutes} min" + ("s" if minutes != 1 else "")


# One human-readable detail string per (dom, op); unknown ops fall back to raw field dump
def format_detail(entry: dict) -> str:
  dom, op = entry.get("dom", ""), entry.get("op", "")
  if dom == "llm":
    if op == "request": return f"{entry.get('role', '')} {entry.get('provider', '')} {entry.get('model', '')} msgs={entry.get('msgs', 0)} tools={entry.get('tools', 0)}"
    if op == "first_token": return format_duration(entry.get("dur_ms", 0))
    if op == "response":
      return (f"{format_duration(entry.get('dur_ms', 0))} in={entry.get('in_tok', 0)} (cache {entry.get('cache_read', 0)}) out={entry.get('out_tok', 0)} "
              f"{format_cost(entry.get('cost_usd'))} tool_calls={entry.get('tool_calls', 0)}")
    if op == "retry": return str(entry.get("err", ""))
    if op == "error": return str(entry.get("err", ""))
    if op == "sidecall": return f"{entry.get('role', '')} {entry.get('provider', '')} {entry.get('model', '')} {format_duration(entry.get('dur_ms', 0))} results={entry.get('results', 0)}"
  elif dom == "tool":
    if op == "start":
      args = entry.get("args", "")
      return f"{entry.get('tool', '')} '{args}'" if args else f"{entry.get('tool', '')}"  # LOG-GN-02: quote identifiers
    if op == "end":
      base = f"{entry.get('tool', '')} {format_duration(entry.get('dur_ms', 0))} {entry.get('status', '')} {entry.get('chars', 0)} chars"
      return f"{base} {entry['err']}" if entry.get("err") else base
    if op == "approval": return f"{entry.get('action', '')} {format_duration(entry.get('dur_ms', 0))} {'approved' if entry.get('approved') else 'denied'}"
  elif dom == "acp":
    if op == "recv": return f"{entry.get('method', '')}" + (f" id={entry['id']}" if "id" in entry else "")
    if op == "send": return f"{entry.get('method', '')} id={entry.get('id', '')} {format_duration(entry.get('dur_ms', 0))} {entry.get('status', '')}"
    if op == "roundtrip": return f"{entry.get('method', '')} {format_duration(entry.get('dur_ms', 0))} {entry.get('outcome', '')}"
    if op == "turn": return f"id={entry.get('id', '')} {format_duration(entry.get('dur_ms', 0))} {entry.get('stop', '')} updates={entry.get('updates', 0)}"
    if op == "eof": return "stdin EOF - server shutting down"
  elif dom == "app":
    if op == "startup": return f"{entry.get('mode', '')} v{entry.get('version', '')}"
    if op == "roles": return str(entry.get("roles", ""))
    if op == "session":
      dur = f" {format_duration(entry['dur_ms'])}" if "dur_ms" in entry else ""
      return f"'{entry.get('file', '')}'" + (" (resumed)" if entry.get("resumed") else "") + dur  # LOG-GN-02: quote file names
    if op == "prompt_system": return f"{entry.get('rules', 0)} rules, {entry.get('workflows', 0)} workflows, {entry.get('skills', 0)} skills {format_duration(entry.get('dur_ms', 0))}"
    if op == "compaction_start": return f"projected={entry.get('projected', 0)} threshold={entry.get('threshold', 0)} tokens"
    if op == "compaction": return f"truncated={entry.get('truncated', 0)} kept={entry.get('kept', 0)} checkpoint={entry.get('checkpoint_chars', 0)} chars"
    if op == "compaction_failed": return str(entry.get("err", ""))
  rest = {key: value for key, value in entry.items() if key not in ("ts", "dom", "op")}
  return json.dumps(rest, ensure_ascii=False) if rest else ""


def render_line(console, entry: dict) -> None:
  dom, op = entry.get("dom", "?"), entry.get("op", "?")
  detail = format_detail(entry)
  is_error = op in ERROR_OPS or entry.get("status") == "error"
  console.print(f"{entry.get('ts', '')[-12:]} ", style="dim", end="", markup=False)  # display time only; the wire ts carries the full date (LOG-AP-01)
  console.print(f"{dom:<4} ", style="red" if is_error else DOMAIN_STYLES.get(dom, "white"), end="", markup=False)
  console.print(f"{op:<12} ", style="bold red" if is_error else "bold", end="", markup=False)
  console.print(detail, style="red" if is_error else "", markup=False)


def wait_for_key() -> None:
  if sys.platform == "win32":
    import msvcrt  # Windows-only module - console-direct read, stdin is the (now closed) pipe
    msvcrt.getch()
  else:
    try:
      input()
    except (EOFError, KeyboardInterrupt):
      pass


# The spawned window's stdout handle points at the PARENT (STARTF_USESTDHANDLES side effect of stdin=PIPE);
# CONOUT$ addresses this process's own console regardless of inherited handles (EC-08)
def make_console():
  if sys.platform == "win32":
    try:
      import ctypes  # windll is Windows-only - import scoped to the win32 branch
      ctypes.windll.kernel32.SetConsoleTitleW("Lana Debug Console")
      conout = open("CONOUT$", "w", encoding="utf-8")
      return Console(file=conout, highlight=False, soft_wrap=True)
    except OSError:  # no own console (direct piped invocation, EC-07) - fall back to stdout
      pass
  return Console(highlight=False, soft_wrap=True)


def run_viewer() -> int:
  console = make_console()  # rich Console bound to CONOUT$ on Windows (EC-08)
  console.print("Lana Debug Console - connected", style="bold")
  for raw in sys.stdin:
    line = raw.strip()
    if not line: continue
    try:
      entry = json.loads(line)
    except json.JSONDecodeError:  # EC-06: raw render, never crash
      console.print(line, style="dim", markup=False)
      continue
    try:
      render_line(console, entry)
    except Exception:  # defensive: a bad field must not kill the viewer
      console.print(line, style="dim", markup=False)
  console.print("-- connection closed (Lana exited) - press any key to close --", style="bold yellow")
  wait_for_key()
  return 0
