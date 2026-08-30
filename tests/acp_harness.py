"""AcpClient: fake ACP client driving the real `lana --acp` executable over stdio (LANAACPB-TP01 section 8)."""
import json, os, queue, subprocess, sys, threading, time
from pathlib import Path

DEFAULT_TIMEOUT_SECONDS = 30


class AcpClient:
  def __init__(self, workspace: Path, script_path: Path | None = None, capabilities: str = "full", policy: str | None = None):
    self.workspace = Path(workspace)
    self.script_path = script_path
    self.capabilities = capabilities  # "full" = elicitation.form+url advertised; "bare" = none
    self.policy = policy
    self.extra_env: dict = {}
    self.proc: subprocess.Popen | None = None
    self.raw_stdout: list[str] = []       # every stdout line verbatim (IG-01 purity assertions)
    self.transcript: list[dict] = []      # both directions: {"dir": "in"|"out", "msg": {...}}
    self.auto_responders: dict = {}       # method -> callable(params) -> result dict | None (None = leave pending)
    self.next_id = 0
    self._incoming: queue.Queue = queue.Queue()
    self._stderr_lines: list[str] = []

  def build_env(self) -> dict:
    env = dict(os.environ)
    env.pop("OPENAI_API_KEY", None)
    env.pop("ANTHROPIC_API_KEY", None)
    if self.script_path: env["LANA_SCRIPTED_ADAPTER"] = str(self.script_path)
    else: env.pop("LANA_SCRIPTED_ADAPTER", None)
    env.update(self.extra_env)
    return env

  def start(self) -> "AcpClient":
    command = [sys.executable, "-m", "lana", "--acp"] + (["--policy", self.policy] if self.policy else [])
    self.proc = subprocess.Popen(command, cwd=self.workspace, env=self.build_env(),
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    threading.Thread(target=self._pump_stdout, daemon=True).start()
    threading.Thread(target=self._pump_stderr, daemon=True).start()
    return self

  def _pump_stdout(self) -> None:
    for line in self.proc.stdout:
      line = line.rstrip("\r\n")
      if not line: continue
      self.raw_stdout.append(line)
      try:
        message = json.loads(line)
      except json.JSONDecodeError:
        self._incoming.put({"__unparseable__": line})
        continue
      self.transcript.append({"dir": "in", "msg": message})
      self._incoming.put(message)

  def _pump_stderr(self) -> None:
    for line in self.proc.stderr:
      self._stderr_lines.append(line.rstrip("\r\n"))

  def stderr_text(self) -> str:
    return "\n".join(self._stderr_lines)

  # ------------------------------------------- START: Wire I/O -------------------------------------------------------

  def send_raw(self, line: str) -> None:  # hostile-client injection (TP01-TC-10)
    self.proc.stdin.write(line + "\n")
    self.proc.stdin.flush()

  def send(self, message: dict) -> None:
    message = {"jsonrpc": "2.0", **message}
    self.transcript.append({"dir": "out", "msg": message})
    self.send_raw(json.dumps(message, ensure_ascii=False))

  def notify(self, method: str, params: dict | None = None) -> None:
    self.send({"method": method, "params": params or {}})

  # Next inbound message; auto-answers agent-originated requests when a responder is registered
  def read_message(self, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> dict:
    message = self._incoming.get(timeout=timeout)
    if "method" in message and "id" in message:
      responder = self.auto_responders.get(message["method"])
      if responder is not None:
        result = responder(message["params"])
        if result is not None: self.send({"id": message["id"], "result": result})
    return message

  # Send a request; collect notifications/agent requests until the matching response. Returns (response, collected)
  def request(self, method: str, params: dict | None = None, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> tuple[dict, list[dict]]:
    request_id = self.next_id
    self.next_id += 1
    self.send({"id": request_id, "method": method, "params": params or {}})
    collected = []
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
      message = self.read_message(timeout=max(0.1, deadline - time.monotonic()))
      if message.get("id") == request_id and ("result" in message or "error" in message): return message, collected
      collected.append(message)
    raise TimeoutError(f"no response to '{method}' (id {request_id}) within {timeout}s; collected: {[m.get('method') or m.get('id') for m in collected]}")

  # ------------------------------------------- END: Wire I/O ---------------------------------------------------------

  def handshake(self, protocol_version: int = 1) -> dict:
    client_capabilities = {"elicitation": {"form": {}, "url": {}}} if self.capabilities == "full" else {}
    response, _ = self.request("initialize", {"protocolVersion": protocol_version,
                                              "clientInfo": {"name": "acp-harness", "version": "1.0"},
                                              "clientCapabilities": client_capabilities})
    self.notify("initialized")
    return response["result"]

  def session_new(self, extra_params: dict | None = None) -> tuple[str, list[dict]]:
    response, collected = self.request("session/new", {"cwd": str(self.workspace), **(extra_params or {})})
    return response["result"]["sessionId"], collected

  # Session/update payloads from a collected message list, optionally filtered by sessionUpdate kind
  @staticmethod
  def updates(collected: list[dict], kind: str | None = None) -> list[dict]:
    payloads = [message["params"]["update"] for message in collected if message.get("method") == "session/update"]
    return [payload for payload in payloads if payload.get("sessionUpdate") == kind] if kind else payloads

  def close_stdin(self) -> None:
    self.proc.stdin.close()

  def wait_exit(self, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> int:
    return self.proc.wait(timeout=timeout)

  def kill(self) -> None:
    self.proc.kill()
    self.proc.wait(timeout=10)

  def stop(self) -> int:
    """Graceful shutdown for teardown: close stdin (EOF), wait, kill on timeout."""
    if self.proc is None: return 0
    try:
      if self.proc.stdin and not self.proc.stdin.closed: self.proc.stdin.close()
      return self.proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
      self.kill()
      return -1


# IG-01: every stdout byte belongs to a valid JSON-RPC message
def assert_stdout_pure(client: AcpClient) -> None:
  for line in client.raw_stdout:
    parsed = json.loads(line)  # raises on impurity
    assert parsed.get("jsonrpc") == "2.0", f"stdout line is JSON but not JSON-RPC 2.0: {line[:120]}"
