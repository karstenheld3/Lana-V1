"""Debug console writer: spawns the viewer window, writes one JSONL line per operation (LANADEBG-SP01).

Module-level singleton (DD-02): ACP mode needs the console before any AppConfig exists, and the
jsonrpc/adapter layers have no AppConfig access. Callers pre-compute every value - durations from
monotonic clocks, cost from the cost engine - this module only serializes and writes (NFR-01, IG-03).
First pipe failure disables logging for the process lifetime with one stderr warning (IG-02, EC-01).
stdout and stdin are NEVER touched - ACP protocol integrity (IG-01).
"""
import datetime, json, os, subprocess, sys

_writer = None  # module singleton: None = disabled, dlog() returns after one check (IG-04)


# Full date for machine parsing and session-JSONL correlation (LOG-AP-01); the viewer strips the date for display
def now_ts() -> str:
  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


class DebugLogWriter:
  def __init__(self, viewer, log_file=None):
    self.viewer = viewer  # None = POSIX stderr fallback (DD-07, EC-03)
    self.log_file = log_file  # None = no file logging
    self.dead = False

  def write(self, line: str) -> None:
    if self.dead: return
    try:
      if self.viewer is not None:
        self.viewer.stdin.write(line + "\n")
        self.viewer.stdin.flush()  # NFR-03: line visible before the next operation starts
      else:
        print(line, file=sys.stderr, flush=True)
    except OSError:  # EC-01: viewer window closed - disable permanently, warn once, never raise (IG-02)
      self.dead = True
      print("WARNING: debug console pipe broken - debug logging disabled for this session.", file=sys.stderr)
    if self.log_file is not None:
      try:
        self.log_file.write(line + "\n")
        self.log_file.flush()
      except (OSError, ValueError):
        self.log_file = None
        print("WARNING: debug log file write failed - file logging disabled.", file=sys.stderr)


def enable(log_dir: str | None = None) -> None:
  """Spawn the viewer window and activate dlog(); called once at startup (FR-01)."""
  global _writer
  if _writer is not None: return
  log_file = None
  if log_dir:
    log_path = os.path.join(log_dir, f"lana-debug-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jsonl")
    try:
      os.makedirs(log_dir, exist_ok=True)
      log_file = open(log_path, "w", encoding="utf-8")
      print(f"Debug log file: {log_path}", file=sys.stderr)
    except (OSError, ValueError) as error:
      print(f"WARNING: cannot create debug log file ({error}) - continuing without it.", file=sys.stderr)
  if os.name == "nt":
    try:  # DD-03: Lana re-invoked as the viewer - works from source and PyApp binary alike.
      # stdout/stderr -> DEVNULL: the child would otherwise inherit the PARENT's streams (STARTF_USESTDHANDLES)
      # and could pollute the ACP protocol; the viewer renders via its own console (CONOUT$, EC-08)
      viewer = subprocess.Popen([sys.executable, "-m", "lana", "--debug-viewer"], stdin=subprocess.PIPE,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                text=True, encoding="utf-8", creationflags=subprocess.CREATE_NEW_CONSOLE)
    except OSError as error:  # EC-02: spawn failure - Lana starts normally without the console
      print(f"WARNING: cannot open debug console ({error}) - continuing without it.", file=sys.stderr)
      return
    print(f"Debug console opened (PID {viewer.pid}).", file=sys.stderr)
    _writer = DebugLogWriter(viewer, log_file)
  else:  # DD-07: viewer window is Windows-only; POSIX gets the same lines on stderr
    print("NOTICE: debug console window is Windows-only - debug lines go to stderr.", file=sys.stderr)
    _writer = DebugLogWriter(None, log_file)


def dlog(dom: str, op: str, **fields) -> None:
  """One debug line; no-op when the console is disabled (IG-04 fast path)."""
  if _writer is None: return
  payload = {"ts": now_ts(), "dom": dom, "op": op, **fields}
  _writer.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str))


def enabled() -> bool:
  return _writer is not None and not _writer.dead


# Compact one-line argument summary for tool lines - identifiers only, never payloads (IG-05)
SUMMARY_KEYS = ("CommandLine", "file_path", "TargetFile", "DirectoryPath", "SearchPath", "SearchDirectory", "Url", "SkillName", "query", "Query", "document_id", "ID")


def args_summary(args: dict) -> str:
  for key in SUMMARY_KEYS:
    if key in args: return str(args[key])[:120]
  return ""
