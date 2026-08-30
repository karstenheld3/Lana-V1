"""ACP server: handshake state machine, method router, session registry (LANAACPB-IP01 IS-03/04/13).

One asyncio loop coordinates the stdin read loop, turn execution, and client-bound requests
(SP01 Technical Constraints). session/prompt runs as an asyncio.Task so `session/cancel` stays
processable while a turn is active (FR-10, EC-08/EC-22). Nothing is sent before `initialize`
arrives (FR-02); the Lana runtime is built per session at `session/new` (FR-03).
"""
import asyncio, contextlib, datetime, sys
from importlib import metadata
from pathlib import Path
from lana.acp.jsonrpc import (
  INTERNAL_ERROR, INVALID_PARAMS, INVALID_REQUEST, METHOD_NOT_FOUND, Connection, Notification, Request, error_body,
)

PROTOCOL_VERSION = 1


# App-Level logging: stderr only, one line per key operation (SP01 section 11, IG-01)
def log(text: str) -> None:
  print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {text}", file=sys.stderr, flush=True)


def agent_version() -> str:
  try:
    return metadata.version("lana")
  except metadata.PackageNotFoundError:
    return "0.0.0"


class AcpError(Exception):
  """Structured JSON-RPC error raised by handlers; the router turns it into an error response (FR-11)."""

  def __init__(self, code: int, message: str):
    self.code, self.message = code, message
    super().__init__(message)


class AcpSession:
  """Binds an ACP sessionId to one Lana runtime (SP01 Domain Objects)."""

  def __init__(self, session_id: str, agent, cost_tracker, prompt_system, app):
    self.session_id = session_id
    self.agent = agent
    self.cost_tracker = cost_tracker
    self.prompt_system = prompt_system
    self.app = app
    self.active_task: asyncio.Task | None = None  # at most one turn per session (FR-05, EC-08)


class AcpServer:
  def __init__(self, args, connection: Connection | None = None):
    self.args = args
    self.connection = connection or Connection()
    self.state = "uninitialized"  # -> awaiting_initialized -> initialized
    self.sessions: dict[str, AcpSession] = {}
    self.elicitation_form = False  # client capability, present AND non-null (FR-09, LANAACPB-IN01)

  async def run(self) -> int:
    await self.connection.read_loop(self.handle)
    for session in self.sessions.values():  # stdin EOF mid-turn: cancel cleanly, then exit 0 (FR-01, EC-11)
      if session.active_task and not session.active_task.done():
        session.active_task.cancel()
        with contextlib.suppress(BaseException):
          await session.active_task
    log("stdin EOF - ACP server shut down.")
    return 0

  # ------------------------------------------- START: Router ---------------------------------------------------------

  async def handle(self, message) -> None:
    if isinstance(message, Request):
      try:
        await self.handle_request(message)
      except AcpError as error:
        self.connection.respond(message.id, error=error_body(error.code, error.message))
      except Exception as error:  # FR-11: errors never crash the connection
        log(f"  ERROR: {message.method}: {type(error).__name__}: {error}")
        self.connection.respond(message.id, error=error_body(INTERNAL_ERROR, f"{type(error).__name__}: {error}"))
    elif isinstance(message, Notification):
      try:
        await self.handle_notification(message)
      except Exception as error:  # notifications have no response channel - log and continue
        log(f"  ERROR: notification {message.method}: {type(error).__name__}: {error}")

  async def handle_request(self, request: Request) -> None:
    if request.method == "initialize": return self.handle_initialize(request)
    if self.state != "initialized":
      raise AcpError(INVALID_REQUEST, f"'{request.method}' rejected: handshake incomplete (state '{self.state}') - send initialize, then the initialized notification first.")  # EC-06
    if request.method == "session/new": return await self.handle_session_new(request)
    raise AcpError(METHOD_NOT_FOUND, f"Method not found: '{request.method}'.")  # EC-02

  async def handle_notification(self, notification: Notification) -> None:
    if notification.method == "initialized":
      if self.state == "awaiting_initialized": self.state = "initialized"
      else: log(f"  WARNING: 'initialized' in state '{self.state}' ignored.")
      return
    log(f"  WARNING: unknown notification '{notification.method}' ignored.")  # EC-02

  # ------------------------------------------- END: Router -----------------------------------------------------------

  # FR-02: protocolVersion 1, agentInfo, exactly the MVP-2 capabilities (LANAACPB-IN01 verified shape)
  def handle_initialize(self, request: Request) -> None:
    if self.state != "uninitialized": raise AcpError(INVALID_REQUEST, "initialize already completed.")  # EC-07
    client_info = request.params.get("clientInfo") or {}
    elicitation = (request.params.get("clientCapabilities") or {}).get("elicitation") or {}
    self.elicitation_form = elicitation.get("form") is not None  # `{}` does NOT imply form support
    self.connection.respond(request.id, result={
      "protocolVersion": PROTOCOL_VERSION,  # EC-04: always respond with our version; the client decides
      "agentInfo": {"name": "lana", "version": agent_version()},
      "agentCapabilities": {"loadSession": True, "promptCapabilities": {"image": False, "audio": False, "embeddedContext": False}},
    })
    self.state = "awaiting_initialized"
    client_label = f"{client_info.get('name', 'unknown')} {client_info.get('version', '')}".strip()
    log(f"initialize: client '{client_label}', negotiated protocolVersion {PROTOCOL_VERSION}.")

  # FR-03: build the Lana runtime for the session's cwd; session JSONL starts with session_started (IG-02)
  async def handle_session_new(self, request: Request) -> None:
    cwd = request.params.get("cwd")
    if not cwd: raise AcpError(INVALID_PARAMS, "session/new requires 'cwd' (absolute workspace path).")
    if request.params.get("mcpServers"): log("  WARNING: 'mcpServers' ignored - Lana has no MCP client.")  # EC-19
    if request.params.get("additionalDirectories"): log("  WARNING: 'additionalDirectories' ignored - Lana has a single-workspace model.")  # EC-19
    from lana.cli import build_runtime  # lazy: cli imports acp.server lazily as well - no import cycle at module load
    from lana.config import ConfigError
    try:
      with contextlib.redirect_stdout(sys.stderr):  # IG-01: loader banner and warnings go to stderr
        app, agent, cost_tracker, prompt_system = build_runtime(self.args, Path(cwd), interactive=False)
    except ConfigError as error:
      raise AcpError(INVALID_PARAMS, f"session/new failed: {error}")
    session_id = agent.session.path.stem
    self.sessions[session_id] = AcpSession(session_id, agent, cost_tracker, prompt_system, app)
    self.connection.respond(request.id, result={"sessionId": session_id})
    self.send_available_commands(session_id, prompt_system)
    log(f"session/new: created '{session_id}' in '{cwd}'.")

  # FR-03: workflows advertised after the response; built-ins are CLI-only and not advertised
  def send_available_commands(self, session_id: str, prompt_system) -> None:
    commands = [{"name": workflow.name, "description": workflow.description} for workflow in prompt_system.workflows]
    self.send_update(session_id, {"sessionUpdate": "available_commands_update", "availableCommands": commands})

  def send_update(self, session_id: str, update: dict) -> None:
    self.connection.send({"method": "session/update", "params": {"sessionId": session_id, "update": update}})

  def require_session(self, params: dict) -> AcpSession:
    session_id = params.get("sessionId", "")
    session = self.sessions.get(session_id)
    if session is None:
      raise AcpError(INVALID_PARAMS, f"Unknown sessionId '{session_id}'. Sessions live in '<workspace>/.lana/sessions/'; create one with session/new or load one with session/load.")  # EC-17
    return session


# Entry point for `lana --acp` (FR-01): UTF-8 pipes, LF framing, nothing sent before initialize
async def run_acp(args) -> int:
  if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
  return await AcpServer(args).run()
