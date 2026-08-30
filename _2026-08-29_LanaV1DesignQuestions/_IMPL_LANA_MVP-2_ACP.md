# IMPL: Lana MVP-2 - ACP Frontend

**Doc ID**: LANAACPB-IP01
**Feature**: acp-frontend
**Goal**: Implement the native ACP v1 frontend (LANAACPB-SP01) in six phases: jsonrpc core → method router → event translator → permission bridge → session/load → CLI flag.
**Timeline**: Created 2026-08-30

**Target file(s)**:
- `src/lana/acp/__init__.py` (NEW ~10 lines)
- `src/lana/acp/jsonrpc.py` (NEW ~130 lines)
- `src/lana/acp/server.py` (NEW ~220 lines)
- `src/lana/acp/translator.py` (NEW ~110 lines)
- `src/lana/acp/bridge.py` (NEW ~110 lines)
- `src/lana/agent.py` (MODIFY - async-capable callback seam, ~10 lines changed)
- `src/lana/tools/interact_tools.py` (MODIFY - awaitable passthrough, 2 lines)
- `src/lana/cli.py` (EXTEND +25 lines - `--acp` flag, runtime builder reuse)
- `tests/acp_harness.py` (NEW ~80 lines)
- `tests/test_acp_*.py` (NEW, test cases below)

**Depends on:**
- `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` for all wire shapes, FRs, DDs, IGs
- `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` for Agent core contracts (FR-04 loop, FR-08 full recall, FR-12 approvals)
- `docs/AI-Standards/ACP-AgentClientProtocol_2026-08-30/` [ACP-IN04..08, IN10, IN15] for JSON fixtures

**Does not depend on:**
- The official ACP Python SDK (LANAACPB-DD-01: hand-rolled)
- ACP v2 Draft surfaces

## MUST-NOT-FORGET

- stdout purity (LANAACPB-IG-01): in `--acp` mode every stdout byte is a JSON-RPC message; wrap ALL runtime construction in `redirect_stdout(sys.stderr)`
- Session JSONL frontend-neutrality (LANAACPB-IG-02): the ACP path emits/persists the same AgentEvents as the CLI - the translator CONSUMES events, never suppresses their persistence
- FR-06 mapping is exhaustive over 11 event types incl. no-op mappings (`turn_started`, `approval_required`, `session_started`)
- Callbacks: CLI stays sync, ACP brokers are async - the Agent seam awaits awaitables, never wraps sync results
- `messageId` on every chunk from day one (LANAACPB-DD-06)
- One turn per session (FR-05); `session/cancel` is a NOTIFICATION - never respond to it
- Denylist classification is agent-side (`safety.classify`), untouched by any client response (LANAACPB-IG-04)
- No new dependencies (LANAAGNT-DD-17); jsonrpc core is stdlib-only
- Offline tests use the scripted adapter (`LANA_SCRIPTED`); no provider calls

## Table of Contents

1. [File Structure](#1-file-structure)
2. [Edge Cases](#2-edge-cases)
3. [Implementation Steps](#3-implementation-steps)
4. [Logging Preview](#4-logging-preview)
5. [Test Cases](#5-test-cases)
6. [Verification Checklist](#6-verification-checklist)
7. [Document History](#7-document-history)

## 1. File Structure

```
src/lana/
├── acp/                       [NEW package]
│   ├── __init__.py            # run_acp() entry point re-export (~10 lines) [NEW]
│   ├── jsonrpc.py             # Framing, message model, Connection (read loop, write+flush, id correlation) (~130 lines) [NEW]
│   ├── server.py              # AcpServer: handshake state, method router, AcpSession, session/new|load|prompt|cancel (~220 lines) [NEW]
│   ├── translator.py          # EventTranslator: AgentEvent -> session/update; tool-kind map; plan updates (~110 lines) [NEW]
│   └── bridge.py              # PermissionBroker, ElicitationBroker, continue-prompt bridge (~110 lines) [NEW]
├── agent.py                   # Async-capable callback seam in resolve_approval/dispatch_call/continue path [MODIFY ~10 lines]
├── tools/interact_tools.py    # ask_user callback may return an awaitable - pass it through [MODIFY 2 lines]
└── cli.py                     # --acp flag, mutual exclusion, dispatch to run_acp [EXTEND +25 lines]
tests/
├── acp_harness.py             # Fake ACP client: spawn `lana --acp`, exchange JSON lines, assert wire shapes (~80 lines) [NEW]
├── test_acp_jsonrpc.py        # Category 1 unit tests [NEW]
├── test_acp_handshake.py      # Categories 2-3 [NEW]
├── test_acp_turn.py           # Categories 4-6 [NEW]
└── test_acp_load.py           # Categories 7-8 [NEW]
```

## 2. Edge Cases

Input boundaries:
- **LANAACPB-IP01-EC-01**: Unparseable stdin line -> `-32700` response with `id: null`, connection continues (FR-11)
- **LANAACPB-IP01-EC-02**: Unknown method -> `-32601`; notification with unknown method -> stderr log only, no response
- **LANAACPB-IP01-EC-03**: `session/prompt` with an `image`/`audio`/`resource` block -> `-32602` naming the unsupported type; `text` + `resource_link` always accepted (FR-05 baseline)
- **LANAACPB-IP01-EC-04**: Client requests `protocolVersion: 2` -> respond `1`; client disconnect afterwards is a clean EOF exit (FR-02)
- **LANAACPB-IP01-EC-05**: JSON content containing newlines/CRLF -> `json.dumps` escapes them; wire line stays single-line (FR-01)

State transitions:
- **LANAACPB-IP01-EC-06**: Session method before `initialized` notification -> JSON-RPC error (FR-02)
- **LANAACPB-IP01-EC-07**: Second `initialize` after handshake -> JSON-RPC error, state unchanged
- **LANAACPB-IP01-EC-08**: Second `session/prompt` while a turn is active -> JSON-RPC error, active turn unaffected (FR-05)
- **LANAACPB-IP01-EC-09**: `session/cancel` with no active turn -> ignored with one stderr log line (FR-10)
- **LANAACPB-IP01-EC-10**: `session/cancel` while a permission/elicitation request is pending -> pending future resolves as cancelled, tool result records denial, `stopReason: "cancelled"` (IG-05)
- **LANAACPB-IP01-EC-11**: EOF on stdin mid-turn -> cancel active turn (existing `note_cancellation` path), exit 0 (FR-01)
- **LANAACPB-IP01-EC-12**: `allow_always` then identical action kind + first command token -> no second `session/request_permission` (FR-08)

External failures:
- **LANAACPB-IP01-EC-13**: Provider failure mid-turn -> JSON-RPC error response on the `session/prompt` id; already-sent `session/update` notifications stand (FR-05)
- **LANAACPB-IP01-EC-14**: Client error response to `session/request_permission` -> treated as rejection, stderr warning (FR-08 cancelled outcome path)
- **LANAACPB-IP01-EC-15**: Response arrives for an unknown/settled request id -> stderr warning, ignored
- **LANAACPB-IP01-EC-16**: `$/cancel_request` for an unknown or already-answered id -> ignored (FR-10)

Data anomalies:
- **LANAACPB-IP01-EC-17**: Unknown `sessionId` in `session/load`/`session/prompt` -> JSON-RPC error naming the id and sessions directory (FR-04)
- **LANAACPB-IP01-EC-18**: Legacy session JSONL without `session_started` -> load proceeds with disk assembly + stderr warning (FR-04, LANAAGNT-FR-08 fallback)
- **LANAACPB-IP01-EC-19**: `mcpServers`/`additionalDirectories` params on `session/new` -> ignored, one stderr warning each (FR-03)
- **LANAACPB-IP01-EC-20**: Elicitation capability absent + `ask_user_question` called -> tool result is the capability-missing fallback string, no wire request (FR-09)
- **LANAACPB-IP01-EC-21**: Denylisted command under `turbo` policy -> `session/request_permission` still issued (agent-side classify unchanged, IG-04)
- **LANAACPB-IP01-EC-22**: `session/cancel` arrives while a long sync tool executor runs (e.g., 30s `run_command`) -> read loop stays responsive (sync dispatch runs in the default executor); cancellation takes effect at the next event boundary, completed calls kept
- **LANAACPB-IP01-EC-23**: Second `session/new` on the same connection -> second AcpSession in the registry; turns across sessions serialize (one active turn per CONNECTION in MVP-2 - runtime construction is workspace-scoped, concurrent cross-session turns are untested territory)

## 3. Implementation Steps

### Phase 1: JSON-RPC Core

#### LANAACPB-IP01-IS-01: Message model and framing

**Location**: `src/lana/acp/jsonrpc.py` (new)

**Action**: Add message dataclasses and line codec (stdlib only: `json`, `dataclasses`)

**Code**:
```python
# Parse one line -> Request(id, method, params) | Notification(method, params) | Response(id, result, error)
def parse_line(line: str): ...
# Serialize any outbound message to one escaped JSON line (ensure_ascii=False, no embedded raw newlines)
def to_line(message: dict) -> str: ...
PARSE_ERROR, METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL_ERROR, REQUEST_CANCELLED = -32700, -32601, -32602, -32603, -32800
```

**Note**: Malformed JSON returns a sentinel so the caller can send EC-01's `-32700` and continue.

#### LANAACPB-IP01-IS-02: Connection - read loop, writes, id correlation

**Location**: `src/lana/acp/jsonrpc.py`

**Action**: Add `Connection` class owning both pipes and both id spaces

**Code**:
```python
class Connection:
  # stdin readline via loop.run_in_executor (Windows: no native async console stdin); UTF-8 both pipes
  async def read_loop(self, dispatch): ...          # parse -> route: response -> resolve pending future; request/notification -> dispatch
  def send(self, message: dict): ...                # write one line to stdout + flush (IG-01: only valid messages pass here)
  async def request(self, method, params): ...      # agent-side id counter -> pending[id] = asyncio.Future -> await
  def respond(self, id, result=None, error=None): ...
  def cancel_pending(self, reason): ...             # resolve every pending agent-bound future as cancelled (IG-05)
```

**Note**: Agent-originated and client-originated id spaces are independent (SPEC Key Mechanisms); `pending` only tracks agent-originated ids. `run_in_executor` for readline refines the SPEC single-loop constraint - coordination stays on one loop, only the blocking read sits in the default executor.

### Phase 2: Method Router

#### LANAACPB-IP01-IS-03: AcpServer - handshake state and dispatch table

**Location**: `src/lana/acp/server.py` (new)

**Action**: Add `AcpServer` with state machine `uninitialized → initialized → shutdown` and method table

**Code**:
```python
class AcpServer:
  METHODS = {"initialize": ..., "session/new": ..., "session/load": ..., "session/prompt": ...}
  NOTIFICATIONS = {"initialized": ..., "session/cancel": ..., "$/cancel_request": ...}
  async def handle(self, message): ...   # state gate (EC-06/07) -> method handler -> respond; unknown -> -32601
  def handle_initialize(self, params): ...  # protocolVersion 1, agentInfo, capabilities per FR-02
```

**Note**: Capability response exactly per SPEC Data Structures (LANAACPB-IN01 verified shape): top-level `loadSession: true`, `promptCapabilities: {image: false, audio: false, embeddedContext: false}`, nothing else.

#### LANAACPB-IP01-IS-04: session/new - runtime construction per session

**Location**: `src/lana/acp/server.py`

**Action**: Add `session/new` handler building the Lana runtime for `cwd`

**Code**:
```python
async def handle_session_new(self, params):
  with contextlib.redirect_stdout(sys.stderr):   # IG-01: banner/warnings from loaders go to stderr
    ...  # load_lana_config, load_prompt_systems, build_system_prompt, ToolRegistry + EXECUTORS, SessionStore.create, session_started first line - same sequence as cli.build_runtime
  # respond {sessionId}; then send available_commands_update from prompt_system.workflows (FR-03; built-ins not advertised)
```

**Note**: Reuse `cli.EXECUTORS` and the `build_runtime` component sequence - extract shared pieces only if reuse without args is impossible; do NOT duplicate config/loader logic. `mcpServers`/`additionalDirectories` -> EC-19 warnings.

### Phase 3: Event Translator

#### LANAACPB-IP01-IS-05: EventTranslator - the FR-06 mapping table

**Location**: `src/lana/acp/translator.py` (new)

**Action**: Add translator mapping each AgentEvent to zero or more `session/update` params dicts

**Code**:
```python
TOOL_KINDS = {"read_file": "read", ..., "ask_user_question": "other"}   # 16 tools per FR-07
class EventTranslator:
  def translate(self, event) -> list[dict]: ...
  # turn_started -> [] + rotate messageId; text_delta -> agent_message_chunk; thinking_delta -> agent_thought_chunk
  # tool_call_requested -> tool_call (pending, kind, title="tool: primary arg")
  # tool_call_finished -> tool_call_update (+ plan update when result starts with "Todo list updated:")
  # turn_finished -> usage_update {used: cumulative in+out tokens, size: generator context window, cost: {amount, currency}} (LANAACPB-IN01 shape)
  # error -> agent_message_chunk; approval_required/session_started/checkpoint_created -> [] (+ stderr note for checkpoint)
```

**Note**: `messageId` = `msg_<turn counter>` rotated on `turn_started` (DD-06 forward compatibility). Todo-plan extraction reuses the `"Todo list updated:"` result contract already used by `session.resume`.

### Phase 4: Permission Bridge

#### LANAACPB-IP01-IS-06: Agent async-capable callback seam

**Location**: `src/lana/agent.py` > `resolve_approval()`, `dispatch_call()`, `run_prompt()` limit branch

**Action**: Modify - callbacks and tool dispatch results may be awaitable; await them inside the async loop

**Code**:
```python
async def _maybe_await(value): ...            # inspect.isawaitable(value) -> await
# resolve_approval becomes async: approved = await _maybe_await(self.approve_callback(action, detail))
# dispatch_call becomes async: result = await _maybe_await(self.registry.dispatch(...))
# limit branch: await _maybe_await(self.continue_callback(calls_this_prompt))
```

**Note**: CLI callbacks stay sync (plain values pass through `_maybe_await` untouched) - zero behavior change; existing 179 offline tests must stay green. This is the callback seam the SPEC Technical Constraints permit. In ACP mode, sync tool executors dispatch via `loop.run_in_executor` so the read loop keeps processing `session/cancel` during long tool runs (EC-22); the CLI path keeps direct sync dispatch.

#### LANAACPB-IP01-IS-07: PermissionBroker

**Location**: `src/lana/acp/bridge.py` (new)

**Action**: Add async `approve_callback`/`continue_callback` implementations over `session/request_permission`

**Code**:
```python
class PermissionBroker:
  async def approve(self, action, detail) -> bool: ...   # 4 options per FR-08; outcome selected/cancelled -> bool
  async def ask_continue(self, calls_done) -> bool: ...  # synthetic toolCallId, allow_once/reject_once only (FR-08 [ASSUMED])
  # allow_always/reject_always memory: dict keyed by (action, first command token), session lifetime, in-memory (FR-08)
```

**Note**: The broker references the CURRENT announced `toolCallId` (translator exposes it). Client error response -> rejection (EC-14). `outcome: "cancelled"` -> rejection recorded via existing denial path.

#### LANAACPB-IP01-IS-08: ElicitationBroker

**Location**: `src/lana/acp/bridge.py`

**Action**: Add async `ask_user` implementation over `elicitation/create` (form mode)

**Code**:
```python
class ElicitationBroker:
  async def ask(self, args: dict) -> str: ...
  # client has elicitation.form: question -> title, options -> required select (allowMultiple -> multi-select); response values -> result string
  # capability absent: return "no answer (client does not support elicitation)" without any wire request (EC-20)
```

**Note**: `tools/interact_tools.py` MODIFY: `execute_ask_user_question` returns `ask_callback(args)` unchanged - a coroutine now flows up to `dispatch_call`, which awaits it (IS-06).

#### LANAACPB-IP01-IS-09: session/prompt handler

**Location**: `src/lana/acp/server.py`

**Action**: Add prompt turn execution wiring translator + brokers

**Code**:
```python
async def handle_session_prompt(self, params):
  # guards: known sessionId (EC-17), no active turn (EC-08); baseline blocks accepted: text verbatim, resource_link -> "[resource: name](uri)" line; image/audio/resource -> -32602 (EC-03, FR-05)
  # assembled input -> async for event in agent.run_prompt(text): for update in translator.translate(event): connection.send(session/update)
  # respond {stopReason: "end_turn"|"cancelled"} - stopReason ONLY, usage flows via usage_update (FR-05); provider_error -> JSON-RPC error response (EC-13)
```

**Note**: `UnknownWorkflowError` -> `agent_message_chunk` with the hint text + `end_turn` (mirrors REPL behavior; the client user typo-ed a slash command - not a wire error).

#### LANAACPB-IP01-IS-10: Cancellation paths

**Location**: `src/lana/acp/server.py`

**Action**: Add `session/cancel` and `$/cancel_request` handlers

**Code**:
```python
def handle_session_cancel(self, params): ...
  # cancel active turn task -> agent.note_cancellation() (keeps completed calls, appends note - FR-10)
  # connection.cancel_pending("cancelled") resolves blocked permission/elicitation futures (IG-05)
  # prompt handler then responds {stopReason: "cancelled"}
def handle_cancel_request(self, params): ...   # id matches active session/prompt -> same path, respond -32800 if no partial result
```

**Note**: Cancellation arrives on the read loop while the turn coroutine is blocked - futures + `asyncio.Task.cancel` on the turn task; `CancelledError` inside `run_prompt` is absorbed by the existing `note_cancellation` pattern in the handler, not inside Agent.

### Phase 5: session/load from Full-Recall JSONL

#### LANAACPB-IP01-IS-11: session/load handler with history replay

**Location**: `src/lana/acp/server.py`

**Action**: Add load handler reusing `session.resume` (one projection, two consumers)

**Code**:
```python
async def handle_session_load(self, params):
  # resolve sessionId -> <workspace>/.lana/sessions/<id>.jsonl; missing -> EC-17 error
  # resumed = resume(path): recorded system_prompt/tool_definitions win (LANAAGNT-FR-08); fingerprint/model warnings -> stderr
  # replay resumed.events through EventTranslator -> session/update stream (user_message -> user_message_chunk during replay ONLY, FR-06)
  # construct Agent with resumed.messages + recorded environment (same as cli.py resume branch); respond after replay completes
```

**Note**: Replay uses recorded events, not the message projection - tool_call/tool_call_update pairs come out in original order. The translator gets a `replaying=True` flag to emit `user_message_chunk` (suppressed live per FR-06).

### Phase 6: CLI Flag

#### LANAACPB-IP01-IS-12: --acp activation

**Location**: `src/lana/cli.py` > `build_arg_parser()`, `main()`

**Action**: Extend - add flag and dispatch

**Code**:
```python
parser.add_argument("--acp", action="store_true", help="ACP agent mode: JSON-RPC 2.0 over stdio (MVP-2)")
# main(): args.acp and args.prompt -> argparse error (mutually exclusive); args.acp -> return asyncio.run(run_acp(args, workspace))
```

**Note**: `--resume` is also mutually exclusive with `--acp` (sessions come from `session/new`/`session/load`). `run_acp` builds nothing until `session/new` arrives - startup sends nothing (FR-02).

#### LANAACPB-IP01-IS-13: stderr App-Level logging

**Location**: `src/lana/acp/server.py` (log helper)

**Action**: Add one-line stderr logger used by all handlers per SPEC section 11

**Code**:
```python
def log(text: str): print(f"{now} {text}", file=sys.stderr, flush=True)
# key operations: initialize, session new/load, prompt start/end, permission outcomes, ignored params, translation omissions
```

## 4. Logging Preview

**ACP session with one ignored param and one permission round-trip (stderr):**
```
2026-08-30 12:00:01 initialize: client 'Zed 0.175.0', negotiated protocolVersion 1.
2026-08-30 12:00:02 session/new: created '2026-08-30_120000_a1b2' in 'E:/proj'.
2026-08-30 12:00:02   WARNING: 'mcpServers' ignored - Lana has no MCP client.
2026-08-30 12:00:05 session/prompt: turn started.
2026-08-30 12:00:08   request_permission tc_001 (execute) -> allow-once.
2026-08-30 12:00:09 session/prompt: end_turn, 2300 tokens.
```

**Error case - session/load with unknown id (stderr + wire error):**
```
2026-08-30 12:01:00 session/load: unknown sessionId '2026-01-01_000000_zzzz'.
```

**Error case - legacy session file (stderr):**
```
2026-08-30 12:02:00 session/load: '2026-08-29_090000_ff00' - 42 events replayed.
2026-08-30 12:02:00   WARNING: legacy session file - recorded environment unavailable, system prompt assembled from current prompt system.
```

stdout carries no log lines in any case (LANAACPB-IG-01).

## 5. Test Cases

### Category 1: JSON-RPC Core (unit, no subprocess) (6 tests)

- **LANAACPB-IP01-TC-01**: `parse_line` on request/notification/response fixtures -> correct message type and fields
- **LANAACPB-IP01-TC-02**: `parse_line` on malformed JSON -> parse-error sentinel (EC-01 input)
- **LANAACPB-IP01-TC-03**: `to_line` with embedded `\n` and CRLF in content -> single escaped line, round-trips (EC-05)
- **LANAACPB-IP01-TC-04**: Agent-originated request ids increment independently of client-originated ids
- **LANAACPB-IP01-TC-05**: Response to unknown pending id -> ignored + warning, no crash (EC-15)
- **LANAACPB-IP01-TC-06**: `cancel_pending` resolves all outstanding futures as cancelled (IG-05 unit)

### Category 2: Handshake and Routing (harness, scripted adapter) (5 tests)

- **LANAACPB-IP01-TC-07**: `initialize` -> exact capability response per SPEC Data Structures (byte-structural compare)
- **LANAACPB-IP01-TC-08**: `protocolVersion: 2` request -> response carries `1` (EC-04)
- **LANAACPB-IP01-TC-09**: `session/new` before `initialized` -> JSON-RPC error (EC-06)
- **LANAACPB-IP01-TC-10**: Unknown method -> `-32601`; unparseable line -> `-32700` with null id, connection alive after both (EC-01, EC-02)
- **LANAACPB-IP01-TC-11**: Second `initialize` -> error, previous handshake state kept (EC-07)

### Category 3: Session Creation (4 tests)

- **LANAACPB-IP01-TC-12**: `session/new` -> `sessionId` = created JSONL file stem; first line is `session_started` (IG-02)
- **LANAACPB-IP01-TC-13**: `session/new` with `mcpServers` + `additionalDirectories` -> both ignored, 2 stderr warnings, session still created (EC-19)
- **LANAACPB-IP01-TC-14**: `available_commands_update` after `session/new` lists workflows, excludes `/help` `/cost` `/exit`
- **LANAACPB-IP01-TC-15**: Full stdout capture during `session/new` -> every line parses as JSON-RPC (IG-01)

### Category 4: Prompt Turn and Translation (9 tests)

- **LANAACPB-IP01-TC-16**: Scripted text turn -> `agent_message_chunk` stream with stable `messageId`, `usage_update` (used/size/cost) before the response, response `{stopReason: "end_turn"}` with no usage field
- **LANAACPB-IP01-TC-17**: Scripted tool turn -> `tool_call` (pending, correct kind per FR-07) then `tool_call_update` (completed), wire order preserved
- **LANAACPB-IP01-TC-18**: `todo_list` result -> additional `plan` update with 1:1 entries (DD-08)
- **LANAACPB-IP01-TC-19**: Thinking deltas -> `agent_thought_chunk` with same `messageId` as the turn's message chunks
- **LANAACPB-IP01-TC-20**: `image` content block -> `-32602` naming the type (EC-03)
- **LANAACPB-IP01-TC-21**: Second concurrent `session/prompt` -> error; first turn completes normally (EC-08)
- **LANAACPB-IP01-TC-22**: Scripted provider error -> JSON-RPC error response on the prompt id; prior notifications intact (EC-13)
- **LANAACPB-IP01-TC-23**: Session JSONL after ACP turn == event types of identical CLI-driven turn (IG-02 differential)
- **LANAACPB-IP01-TC-43**: Prompt with `text` + `resource_link` blocks -> accepted; user message carries the text plus `[resource: name](uri)` line (LANA_SCRIPTED_CAPTURE oracle, FR-05 baseline)

### Category 5: Permission and Elicitation (7 tests)

- **LANAACPB-IP01-TC-24**: Approval-needing command -> `session/request_permission` with 4 options; `allow_once` -> tool executes
- **LANAACPB-IP01-TC-25**: `reject_once` -> tool result records denial, turn continues (existing denial path)
- **LANAACPB-IP01-TC-26**: `allow_always` -> second identical action skips the wire request (EC-12)
- **LANAACPB-IP01-TC-27**: `ask_user_question` with `elicitation.form` capability -> `elicitation/create` form; response values become tool result
- **LANAACPB-IP01-TC-28**: `ask_user_question` without capability -> fallback string, zero wire requests (EC-20)
- **LANAACPB-IP01-TC-29**: Denylisted command under `turbo` -> permission request still issued (EC-21, IG-04)
- **LANAACPB-IP01-TC-41**: Tool-call limit reached -> `session/request_permission` on synthetic toolCallId with allow_once/reject_once; `allow_once` -> turn continues, `reject_once` -> `end_turn` (FR-08 continue prompt)

### Category 6: Cancellation (5 tests)

- **LANAACPB-IP01-TC-30**: `session/cancel` mid-turn -> `stopReason: "cancelled"`, completed calls kept in JSONL (FR-10)
- **LANAACPB-IP01-TC-31**: `session/cancel` while permission request pending -> pending request resolved, denial recorded, cancelled response (EC-10)
- **LANAACPB-IP01-TC-32**: `session/cancel` with no active turn -> no response, one stderr line (EC-09)
- **LANAACPB-IP01-TC-33**: `$/cancel_request` on active prompt id -> `-32800`; on unknown id -> ignored (EC-16)
- **LANAACPB-IP01-TC-42**: `session/cancel` during a slow scripted tool execution -> processed without waiting for the tool; `stopReason: "cancelled"`, completed calls kept (EC-22)

### Category 7: Session Load (4 tests)

- **LANAACPB-IP01-TC-34**: `session/load` of an ACP-created session -> history replayed as session/update stream (user + agent chunks, tool pairs in order), then response
- **LANAACPB-IP01-TC-35**: `session/load` of a CLI-created session -> identical replay behavior (IG-02 cross-frontend)
- **LANAACPB-IP01-TC-36**: Loaded session uses recorded system prompt + tool definitions (LANA_SCRIPTED_CAPTURE oracle, LANAAGNT-FR-08)
- **LANAACPB-IP01-TC-37**: Unknown sessionId -> error naming sessions dir (EC-17); legacy file -> loads with stderr warning (EC-18)

### Category 8: CLI Flag and Purity (3 tests)

- **LANAACPB-IP01-TC-38**: `--acp` with `-p` or `--resume` -> argparse error, exit 2
- **LANAACPB-IP01-TC-39**: `lana --acp` startup -> zero stdout bytes before first request; EOF -> exit 0 (FR-01, FR-02)
- **LANAACPB-IP01-TC-40**: Existing offline suite (179 tests) green after the agent.py callback seam - CLI behavior unchanged (IS-06 regression gate)

## 6. Verification Checklist

### Prerequisites
- [ ] **LANAACPB-IP01-VC-01**: LANAACPB-SP01 and LANAAGNT-SP01 FR-04/08/12 read; ACP-IN04..08/10/15 fixtures located
- [ ] **LANAACPB-IP01-VC-02**: TC-40 regression gate defined BEFORE agent.py modification

### Implementation
- [ ] **LANAACPB-IP01-VC-03**: Phase 1 (IS-01, IS-02) complete, Category 1 green
- [ ] **LANAACPB-IP01-VC-04**: Phase 2 (IS-03, IS-04) complete, Categories 2-3 green
- [ ] **LANAACPB-IP01-VC-05**: Phase 3 (IS-05) complete, Category 4 green
- [ ] **LANAACPB-IP01-VC-06**: Phase 4 (IS-06..IS-10) complete, Categories 5-6 green + TC-40 regression
- [ ] **LANAACPB-IP01-VC-07**: Phase 5 (IS-11) complete, Category 7 green
- [ ] **LANAACPB-IP01-VC-08**: Phase 6 (IS-12, IS-13) complete, Category 8 green

### Validation
- [ ] **LANAACPB-IP01-VC-09**: All 43 test cases pass offline (scripted adapter, no provider calls)
- [ ] **LANAACPB-IP01-VC-10**: Wire fixtures byte-structurally match the official v1 shapes per LANAACPB-IN01 (NFR-01; the 2026-08-30 snapshot is NOT the wire authority - 4 shapes hallucinated)
- [ ] **LANAACPB-IP01-VC-11**: Manual smoke against a real ACP client (Zed or `npx @zed-industries/acp` inspector if available; else scripted harness replay documented)
- [ ] **LANAACPB-IP01-VC-12**: SPEC sync: Technical Constraints refined (executor readline, callback seam) reverse-updated into LANAACPB-SP01

## 7. Document History

**[2026-08-30 14:05]**
- Fixed: wire shapes per `/research` verification (LANAACPB-IN01) - IS-03 capabilities (`promptCapabilities`, top-level `loadSession`), IS-05 usage_update (used/size/cost), IS-09 baseline resource_link acceptance + stopReason-only response, EC-03/TC-16/TC-20 adjusted, TC-43 added (resource_link acceptance), VC-10 re-anchored to LANAACPB-IN01

**[2026-08-30 13:50]**
- Added: EC-22 (read-loop responsiveness during long sync tool runs - executor dispatch in ACP mode) + TC-42; EC-23 (multi-session registry, turns serialized per connection in MVP-2)
- Changed: MNF protocol line - v1 LATEST stable, v2 breaking changes POSTPONED [user decision 2026-08-30]

**[2026-08-30 13:20]**
- Initial implementation plan created: 6 phases per user directive (jsonrpc core → method router → event translator → permission bridge → session/load → CLI flag), 21 ECs, 13 ISs, 41 TCs, 12 VCs; codebase analysis found the sync-callback seam (IS-06) and Windows executor-readline refinement (IS-02 note) - both flagged for SPEC sync (VC-12); verify pass added TC-41 (FR-08 continue prompt coverage)
