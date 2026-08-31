"""JSON-RPC 2.0 line codec and connection for the ACP frontend (LANAACPB-IP01 IS-01/IS-02).

stdout carries ONLY serialized JSON-RPC messages (IG-01); one message per line, no embedded
raw newlines (FR-01). Agent-originated and client-originated request id spaces are independent -
`pending` tracks agent-originated ids only (SP01 Key Mechanisms). The blocking stdin readline
runs in the default executor (Windows has no async console stdin), coordination stays on one loop.

FR-01 hardening (LANAAGNT-IN03 BL-01): stdout writes run on a dedicated writer thread fed by a
bounded queue - a client that stops draining stdout cannot freeze the event loop.
"""
import asyncio, contextlib, json, queue, sys, threading, time
from dataclasses import dataclass
from typing import Any, Optional
from lana.acp import log
from lana.debuglog import dlog

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL_ERROR, REQUEST_CANCELLED = -32700, -32600, -32601, -32602, -32603, -32800


@dataclass
class Request:
  id: Any
  method: str
  params: dict


@dataclass
class Notification:
  method: str
  params: dict


@dataclass
class Response:
  id: Any
  result: Optional[dict] = None
  error: Optional[dict] = None


@dataclass
class ParseFailure:
  detail: str


# One stdin line -> Request | Notification | Response | ParseFailure (EC-01: caller sends -32700 and continues)
def parse_line(line: str):
  try:
    data = json.loads(line)
  except json.JSONDecodeError as error:
    return ParseFailure(detail=str(error))
  if not isinstance(data, dict) or data.get("jsonrpc") != "2.0": return ParseFailure(detail="not a JSON-RPC 2.0 object")
  if "method" in data:
    params = data.get("params") or {}
    if "id" in data: return Request(id=data["id"], method=data["method"], params=params)
    return Notification(method=data["method"], params=params)
  if "id" in data and ("result" in data or "error" in data):
    return Response(id=data["id"], result=data.get("result"), error=data.get("error"))
  return ParseFailure(detail="neither request, notification, nor response")


# Serialize one outbound message to a single escaped line (EC-05: embedded newlines JSON-escape)
def to_line(message: dict) -> str:
  return json.dumps({"jsonrpc": "2.0", **message}, ensure_ascii=False, separators=(",", ":"))


def error_body(code: int, message: str) -> dict:
  return {"code": code, "message": message}


class ClientErrorResponse(Exception):
  """The client answered an agent-originated request with an error (EC-14: treated as rejection upstream)."""

  def __init__(self, error: dict):
    self.error = error or {}
    super().__init__(self.error.get("message", "client error response"))


class RoundTripCancelled(Exception):
  """A pending agent-originated request was cancelled locally (IG-05)."""


class StdoutWriter:
  """Dedicated stdout writer thread (BL-01): the event loop enqueues, the thread writes + flushes.

  Bounded queue: on overflow the message is DROPPED with a stderr log - blocking would re-freeze the
  loop, which is the exact hazard this thread removes. Wire bytes are unchanged on the happy path.
  """

  def __init__(self, sink=None, maxsize: int = 1000):
    self._stdout = sys.stdout  # bind the REAL stream now - a later redirect_stdout (session build, BL-04) must never divert protocol bytes
    self.sink = sink or self._stdout_sink
    self.queue: queue.Queue = queue.Queue(maxsize=maxsize)
    self.dropped = 0
    self.thread = threading.Thread(target=self._run, daemon=True, name="acp-stdout-writer")
    self.thread.start()

  def _stdout_sink(self, line: str) -> None:
    self._stdout.write(line + "\n")
    self._stdout.flush()  # FR-01: flush per message

  def _run(self) -> None:
    while True:
      line = self.queue.get()
      if line is None: return
      with contextlib.suppress(Exception):  # a broken stdout pipe must not kill the thread loudly
        self.sink(line)

  def write(self, line: str) -> None:
    try:
      self.queue.put_nowait(line)
    except queue.Full:  # EC: overflow drops with a log line - never blocks the event loop
      self.dropped += 1
      log(f"  WARNING: stdout writer queue full - message dropped ({self.dropped} total).")

  def close(self) -> None:
    with contextlib.suppress(queue.Full): self.queue.put_nowait(None)
    self.thread.join(timeout=3)


class Connection:
  """One stdio link: reads client lines, writes agent lines, correlates agent-originated requests."""

  def __init__(self, read_line=None, write_line=None):
    self.read_line = read_line or self._read_stdin    # async () -> str | None (None = EOF)
    self.write_line = write_line or self._write_stdout
    self.pending: dict[Any, asyncio.Future] = {}      # agent-originated id -> response future
    self.next_id = 100                                # distinct start aids log reading; id spaces are independent regardless
    self._writer: Optional[StdoutWriter] = None       # lazy: only the default stdout path spawns the writer thread (BL-01)

  def _write_stdout(self, line: str) -> None:
    if self._writer is None: self._writer = StdoutWriter()
    self._writer.write(line)

  def close(self) -> None:
    if self._writer is not None:
      self._writer.close()
      self._writer = None

  async def _read_stdin(self) -> Optional[str]:
    line = await asyncio.get_running_loop().run_in_executor(None, sys.stdin.readline)
    return line if line else None                     # '' = EOF

  def send(self, message: dict) -> None:
    self.write_line(to_line(message))

  def respond(self, id: Any, result: Optional[dict] = None, error: Optional[dict] = None) -> None:
    if error is not None: self.send({"id": id, "error": error})
    else: self.send({"id": id, "result": result if result is not None else {}})

  async def request(self, method: str, params: dict):
    """Agent-to-client request; awaits the response while the read loop keeps processing."""
    request_id = self.next_id
    self.next_id += 1
    future = asyncio.get_running_loop().create_future()
    self.pending[request_id] = future
    self.send({"id": request_id, "method": method, "params": params})
    started_at = time.perf_counter()  # LANADEBG-FR-04: round-trip = send to client response
    try:
      result = await future
    except (RoundTripCancelled, ClientErrorResponse) as error:
      dlog("acp", "roundtrip", method=method, dur_ms=int((time.perf_counter() - started_at) * 1000), outcome=type(error).__name__)
      raise
    finally:
      self.pending.pop(request_id, None)
    dlog("acp", "roundtrip", method=method, dur_ms=int((time.perf_counter() - started_at) * 1000), outcome="ok")
    return result

  # Route a client response to its pending future; False when the id is unknown or settled (EC-15)
  def resolve_response(self, response: Response) -> bool:
    future = self.pending.get(response.id)
    if future is None or future.done(): return False
    if response.error is not None: future.set_exception(ClientErrorResponse(response.error))
    else: future.set_result(response.result)
    return True

  # Resolve every outstanding agent-originated request as cancelled (IG-05)
  def cancel_pending(self, reason: str) -> None:
    for future in list(self.pending.values()):
      if not future.done(): future.set_exception(RoundTripCancelled(reason))

  async def read_loop(self, dispatch) -> None:
    """Read until EOF; responses resolve futures, requests/notifications go to `dispatch` (async)."""
    while True:
      raw = await self.read_line()
      if raw is None: break
      line = raw.strip()
      if not line: continue
      message = parse_line(line)
      if isinstance(message, ParseFailure):
        self.respond(None, error=error_body(PARSE_ERROR, f"Parse error: {message.detail}"))  # EC-01: null id, continue
        continue
      if isinstance(message, Response):
        if not self.resolve_response(message): log(f"  WARNING: response for unknown request id {message.id!r} ignored.")  # EC-15
        continue
      await dispatch(message)
