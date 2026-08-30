"""ACP server: handshake state machine, method router, session registry (LANAACPB-IP01 IS-03/04/13).

One asyncio loop coordinates the stdin read loop, turn execution, and client-bound requests
(SP01 Technical Constraints). session/prompt runs as an asyncio.Task so `session/cancel` stays
processable while a turn is active (FR-10, EC-08/EC-22). Nothing is sent before `initialize`
arrives (FR-02); the Lana runtime is built per session at `session/new` (FR-03).
"""
import argparse, asyncio, contextlib, os, sys
from importlib import metadata
from pathlib import Path
from lana.acp import log
from lana.acp.jsonrpc import (
  INTERNAL_ERROR, INVALID_PARAMS, INVALID_REQUEST, METHOD_NOT_FOUND, REQUEST_CANCELLED, Connection, Notification, Request, error_body,
)
from lana.acp.bridge import ElicitationBroker, PermissionBroker
from lana.acp.translator import EventTranslator, generator_context_window
from lana.agent import UnknownWorkflowError
from lana.config import ConfigError
from lana.session import resume as resume_session
from lana.tools.shell_tools import terminate_tool_processes

PROTOCOL_VERSION = 1


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

  def __init__(self, session_id: str, agent, cost_tracker, prompt_system, app, translator, broker):
    self.session_id = session_id
    self.agent = agent
    self.cost_tracker = cost_tracker
    self.prompt_system = prompt_system
    self.app = app
    self.translator = translator
    self.broker = broker
    self.active_task: asyncio.Task | None = None  # at most one turn per session (FR-05, EC-08)
    self.prompt_request_id = None                 # id of the pending session/prompt (FR-10, $/cancel_request)
    self.cancel_with_error = False                # $/cancel_request path answers -32800 instead of stopReason


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
        with contextlib.suppress(asyncio.CancelledError, Exception):
          await session.active_task
    for session in self.sessions.values():  # FR-01 BL-06: no tool child process outlives the server
      self.cleanup_session_processes(session, include_background=True)
    self.connection.close()  # drain the stdout writer thread (BL-01)
    log("stdin EOF - ACP server shut down.")
    return 0

  # FR-10 BL-02: terminate live tool children; foreground always, background only at shutdown
  def cleanup_session_processes(self, session: "AcpSession", include_background: bool) -> None:
    terminated, survivors = terminate_tool_processes(session.agent.tool_context, include_background=include_background)
    if terminated: log(f"  terminated tool process(es): {', '.join(terminated)}.")
    if survivors: log(f"  WARNING: tool process(es) still running: {', '.join(survivors)}.")

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
    if request.method == "session/load": return await self.handle_session_load(request)
    if request.method == "session/prompt": return self.handle_session_prompt(request)
    raise AcpError(METHOD_NOT_FOUND, f"Method not found: '{request.method}'.")  # EC-02

  async def handle_notification(self, notification: Notification) -> None:
    if notification.method == "initialized":
      if self.state == "awaiting_initialized": self.state = "initialized"
      else: log(f"  WARNING: 'initialized' in state '{self.state}' ignored.")
      return
    if notification.method == "session/cancel": return self.handle_session_cancel(notification.params)
    if notification.method == "$/cancel_request": return self.handle_cancel_request(notification.params)
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
    app, agent, cost_tracker, prompt_system = await self.build_session_runtime("session/new", self.args, cwd)
    session_id = agent.session.path.stem
    self.sessions[session_id] = self.make_acp_session(session_id, agent, cost_tracker, prompt_system, app)
    self.connection.respond(request.id, result={"sessionId": session_id})
    self.send_available_commands(session_id, prompt_system)
    log(f"session/new: created '{session_id}' in '{cwd}'.")

  # FR-04: resume under recorded-environment authority, replay history, then complete the load
  async def handle_session_load(self, request: Request) -> None:
    params = request.params
    session_id, cwd = params.get("sessionId", ""), params.get("cwd")
    if not cwd: raise AcpError(INVALID_PARAMS, "session/load requires 'cwd' (absolute workspace path).")
    if params.get("mcpServers"): log("  WARNING: 'mcpServers' ignored - Lana has no MCP client.")  # EC-19
    # Resolve data_dir: load config to get the configured data_dir, then look for session file
    config_override = self.args.config or os.environ.get("LANA_CONFIG") or None
    from lana.config import load_lana_config
    temp_app = load_lana_config(Path(cwd), Path(config_override) if config_override else None, require_keys=False)
    sessions_dir = temp_app.data_dir / "sessions"
    session_file = sessions_dir / f"{session_id}.jsonl"
    if not session_file.is_file():
      raise AcpError(INVALID_PARAMS, f"Unknown sessionId '{session_id}' - no session file in '{sessions_dir}'.")  # EC-17
    load_args = argparse.Namespace(**{**vars(self.args), "resume": str(session_file)})
    app, agent, cost_tracker, prompt_system = await self.build_session_runtime("session/load", load_args, cwd)
    session = self.make_acp_session(session_id, agent, cost_tracker, prompt_system, app)
    self.sessions[session_id] = session
    replayer = EventTranslator(cost_tracker, session.translator.context_window, replaying=True)
    replayed = 0
    for event in resume_session(session_file).events:  # replay BEFORE the response completes the load (FR-04)
      for update in replayer.translate(event):
        self.send_update(session_id, update)
        replayed += 1
    self.connection.respond(request.id, result={})
    self.send_available_commands(session_id, prompt_system)
    log(f"session/load: '{session_id}' - {replayed} updates replayed.")

  # Shared runtime construction for session/new and session/load; loader output diverted to stderr (IG-01).
  # FR-03 BL-04: runs in the default executor - cancel/EOF processing stays live during the load
  async def build_session_runtime(self, method: str, args, cwd: str):
    from lana.cli import build_runtime  # lazy: lana.cli is the composition root - importing it at module load would couple the frontends
    def build():
      with contextlib.redirect_stdout(sys.stderr):  # redirect inside the callable - it must wrap the executor thread's prints
        return build_runtime(args, Path(cwd), interactive=False)
    try:
      return await asyncio.get_running_loop().run_in_executor(None, build)
    except (ConfigError, OSError) as error:  # FR-16 CR-01 parity: filesystem failures answer as structured errors
      raise AcpError(INVALID_PARAMS, f"{method} failed: {error}")

  # Wire the ACP brokers into the Agent's callback seam (IS-06/07/08)
  def make_acp_session(self, session_id: str, agent, cost_tracker, prompt_system, app) -> AcpSession:
    broker = PermissionBroker(self.connection, session_id)
    elicitation = ElicitationBroker(self.connection, session_id, self.elicitation_form)
    agent.approve_callback = broker.approve
    agent.continue_callback = broker.ask_continue
    agent.executor_dispatch = True  # EC-22: blocking executors off-loop, read loop stays responsive
    agent.tool_context.ask_user = elicitation.ask
    translator = EventTranslator(cost_tracker, generator_context_window(cost_tracker))
    return AcpSession(session_id, agent, cost_tracker, prompt_system, app, translator, broker)

  # FR-05: one turn per session, runs as a Task so cancel notifications stay processable
  def handle_session_prompt(self, request: Request) -> None:
    session = self.require_session(request.params)
    if session.active_task and not session.active_task.done():
      raise AcpError(INVALID_REQUEST, f"A prompt turn is already active for session '{session.session_id}' (one turn per session).")  # EC-08
    text = self.assemble_prompt_text(request.params)
    session.prompt_request_id = request.id
    session.cancel_with_error = False
    session.active_task = asyncio.create_task(self.run_prompt_turn(session, request.id, text))

  # FR-05 baseline: text verbatim, resource_link inlined; capability-gated types rejected (EC-03)
  def assemble_prompt_text(self, params: dict) -> str:
    parts = []
    for block in params.get("prompt") or []:
      block_type = block.get("type")
      if block_type == "text": parts.append(block.get("text", ""))
      elif block_type == "resource_link": parts.append(f"[resource: {block.get('name') or block.get('uri', '')}]({block.get('uri', '')})")
      else: raise AcpError(INVALID_PARAMS, f"Unsupported content block type '{block_type}' - this agent accepts 'text' and 'resource_link' (promptCapabilities: image/audio/embeddedContext all false).")
    text = "\n".join(part for part in parts if part)
    if not text.strip(): raise AcpError(INVALID_PARAMS, "Prompt contains no text content.")
    return text

  async def run_prompt_turn(self, session: AcpSession, request_id, text: str) -> None:
    log("session/prompt: turn started.")
    last_error = ""
    try:
      async for event in session.agent.run_prompt(text):
        if event.type == "tool_call_requested": session.broker.current_tool_call_id = event.id
        if event.type == "error": last_error = event.message
        for update in session.translator.translate(event):
          self.send_update(session.session_id, update)
    except UnknownWorkflowError as error:  # client user typo-ed a slash command - not a wire error (IS-09)
      self.send_update(session.session_id, {"sessionUpdate": "agent_message_chunk", "messageId": session.translator.message_id, "content": {"type": "text", "text": str(error)}})
      self.connection.respond(request_id, result={"stopReason": "end_turn"})
      log(f"session/prompt: unknown workflow - {error}")
      return
    except asyncio.CancelledError:  # session/cancel or $/cancel_request (FR-10)
      session.agent.note_cancellation()  # completed calls kept, cancellation note appended (LANAAGNT-FR-04)
      self.cleanup_session_processes(session, include_background=False)  # FR-10 BL-02: the abandoned foreground tool must not keep mutating the workspace
      if session.cancel_with_error: self.connection.respond(request_id, error=error_body(REQUEST_CANCELLED, "Request cancelled."))
      else: self.connection.respond(request_id, result={"stopReason": "cancelled"})
      log("session/prompt: cancelled.")
      return
    except Exception as error:  # never crash the connection (FR-11)
      self.connection.respond(request_id, error=error_body(INTERNAL_ERROR, f"{type(error).__name__}: {error}"))
      log(f"  ERROR: session/prompt: {type(error).__name__}: {error}")
      return
    if session.agent.stop_reason == "provider_error":  # EC-13: JSON-RPC error on the prompt id
      self.connection.respond(request_id, error=error_body(INTERNAL_ERROR, last_error or "Provider error."))
      log("session/prompt: provider error.")
      return
    self.connection.respond(request_id, result={"stopReason": "end_turn"})  # stopReason ONLY (LANAACPB-IN01)
    log("session/prompt: end_turn.")

  # FR-10: notification - cancel the active turn, resolve blocked round-trips, never respond to it
  def handle_session_cancel(self, params: dict) -> None:
    session = self.sessions.get(params.get("sessionId", ""))
    if session is None or session.active_task is None or session.active_task.done():
      log("  session/cancel: no active turn - ignored.")  # EC-09
      return
    self.connection.cancel_pending("session/cancel")  # IG-05: pending permission/elicitation resolve as cancelled
    session.active_task.cancel()

  # FR-10: $/cancel_request on the active session/prompt id -> same path, -32800 response (EC-16 otherwise)
  def handle_cancel_request(self, params: dict) -> None:
    request_id = params.get("requestId", params.get("id"))  # tolerant: exact v1 field name unverified [ASSUMED]
    for session in self.sessions.values():
      if session.active_task and not session.active_task.done() and session.prompt_request_id == request_id:
        session.cancel_with_error = True
        self.connection.cancel_pending("$/cancel_request")
        session.active_task.cancel()
        return
    log(f"  $/cancel_request: no cancellable request with id {request_id!r} - ignored.")  # EC-16

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
      raise AcpError(INVALID_PARAMS, f"Unknown sessionId '{session_id}'. Create one with session/new or load one with session/load.")  # EC-17
    return session


# Entry point for `lana --acp` (FR-01): UTF-8 pipes, LF framing, nothing sent before initialize
async def run_acp(args) -> int:
  if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
  return await AcpServer(args).run()
