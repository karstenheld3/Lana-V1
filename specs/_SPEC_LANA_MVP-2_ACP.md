# SPEC: Lana MVP-2 - ACP Frontend

**Doc ID**: LANAACPB-SP01
**Feature**: acp-frontend
**Goal**: Specify a native Agent Client Protocol (v1) frontend so ACP clients (Zed, JetBrains, Neovim, Emacs) can drive Lana as their coding agent.
**Timeline**: Created 2026-08-30
**Target file(s)**:
- `src/lana/acp/` (new package)
- `src/lana/cli.py` (mode activation)

**Depends on:**
- `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` for the Agent core: AgentEvent stream (DD-06), full-recall sessions (FR-08, DD-22), slash expansion (FR-05, DD-13), ExecutionPolicy (FR-12, DD-15), cost tracking (FR-09), headless/test interfaces (FR-14, DD-20)
- `_INFO_LANAACPB-IN01_AcpV1WireShapeVerification.md [LANAACPB-IN01]` for live-verified v1 wire shapes - OVERRIDES the local snapshots on every discrepancy
- `docs/AI-Standards/ACP-AgentClientProtocol_2026-08-30/` [ACP-IN01..15] for protocol narrative (WARNING: 4 wire shapes in this set are hallucinated - see LANAACPB-IN01 section 2; wire shapes MUST be taken from LANAACPB-IN01)

**Does not depend on:**
- `docs/AI-Standards/ACP-AgentClientProtocol_2026-06-12/` (superseded snapshot - do not cite)
- ACP v2 Draft surfaces (published 2026-07-20, unstable - explicitly out of scope)

## MUST-NOT-FORGET

- stdout purity: in ACP mode stdout carries ONLY valid ACP JSON-RPC messages; ALL diagnostics go to stderr (ACP-IN10)
- Newline-delimited framing: one JSON-RPC message per line, no embedded raw newlines (ACP-IN10)
- Protocol v1 only: no session modes, no v2 Draft features, never consume client fs/terminal capabilities (v2 removes them)
- The session JSONL stays frontend-neutral: identical event log whether CLI or ACP drives the Agent (extends LANAAGNT-IG-02)
- Recorded-environment authority (LANAAGNT-FR-08) applies to `session/load` identically to `--resume`
- `elicitation/create` only when the client advertised `elicitation.form`; permission requests only via `session/request_permission`
- `messageId` on every streamed chunk (optional in v1, required in v2 - forward compatibility)
- Cite only the 2026-08-30 ACP INFO docs

## Table of Contents

1. [Scenario](#1-scenario)
2. [Context](#2-context)
3. [Domain Objects](#3-domain-objects)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Design Decisions](#6-design-decisions)
7. [Implementation Guarantees](#7-implementation-guarantees)
8. [Key Mechanisms](#8-key-mechanisms)
9. [Action Flow](#9-action-flow)
10. [Data Structures](#10-data-structures)
11. [Logging Requirements](#11-logging-requirements)
12. [Technical Constraints](#12-technical-constraints)
13. [Document History](#13-document-history)

## 1. Scenario

**Problem:** Lana is CLI-only. Editors standardized agent integration on ACP (35+ agents, 20+ clients); without ACP support, Lana cannot be driven from Zed, JetBrains, Neovim, or Emacs, and every editor integration would be a custom build (the N x M problem ACP exists to solve, ACP-IN03).

**Solution:**
- Native ACP server as a second frontend: `lana --acp` speaks JSON-RPC 2.0 over stdio, subscribing to the same AgentEvent stream the CLI renderer consumes (the structural investment LANAAGNT-DD-06 made for exactly this)
- Hand-rolled protocol layer (no SDK dependency), targeting protocol v1 stable surfaces only
- Lana sessions ARE ACP sessions: `session/new` creates a session JSONL, `session/load` resumes one under full-recall authority

**What we don't want:**
- The official Python SDK as a dependency (pre-1.0 at v0.12.x, breaks the LANAAGNT-DD-17 closed dependency list, abstraction between us and the wire)
- A separate bridge executable translating headless output (approval round-trips are impossible over one-shot headless runs; "adapter tax" per ACP-IN14)
- v2 Draft features (state_update, tool_call upserts, structured diffs) while v2 can still change
- Consuming client fs/terminal capabilities (removed in v2; Lana has its own file and shell tools)
- Session modes API (removed in v2; ExecutionPolicy is not a session mode)
- A second persistence model - the session JSONL remains the single source of truth

## 2. Context

MVP-1 delivered a working CLI agent whose frontend contract is the internal AgentEvent stream (LANAAGNT-DD-06: "the ACP server in MVP-2 subscribes to the same stream"). Full-recall session persistence (LANAAGNT-FR-08) means any session is resumable from its JSONL alone - which is exactly the agent-side substrate ACP's `session/load` expects. Slash commands arrive as plain prompt text in ACP; Lana already expands them agent-side (LANAAGNT-DD-13, confirmed compatible by ACP-IN01: commands are outside ACP scope).

Three implementation options were evaluated (2026-08-30 design discussion):
- **A: Native in-process module, hand-rolled JSON-RPC** - chosen (LANAACPB-DD-01)
- **B: Official Python SDK** - rejected: pre-1.0 dependency, abstraction risk
- **C: Standalone bridge process** - rejected: permission round-trips impossible over headless one-shots

ACP protocol status at spec time: v1 stable (elicitation, request cancellation, message IDs, usage updates, session delete all stabilized mid-2026); v2 Draft published 2026-07-20 with breaking changes; stdio the only widely implemented transport (ACP-IN10, ACP-IN13).

**Protocol version scope [user decision 2026-08-30]:** MVP-2 implements ACP v1 at its LATEST stable state (all mid-2026 stabilizations included: elicitation, `$/cancel_request`, message IDs, usage updates). ACP v2 breaking changes (Draft 2026-07-20: `state_update` lifecycle, unified capabilities, tool-call upserts, fs/terminal removal) are POSTPONED to a later MVP. Only the version-negotiation seam (LANAACPB-DD-02) anticipates v2 - no v2 surface is implemented, stubbed, or tested in MVP-2.

## 3. Domain Objects

### AcpConnection

An **AcpConnection** is one client-agent stdio link: reads JSON-RPC lines from stdin, writes JSON-RPC lines to stdout, tracks handshake state (`uninitialized` → `initialized` → `shutdown`) and outstanding request ids in both directions.

### AcpSession

An **AcpSession** binds an ACP `sessionId` to one Lana Session (JSONL file) and one Agent instance with its conversation state.

**Key properties:**
- `session_id` - ACP-visible id; equals the session JSONL file stem (agent-chosen format, ACP-IN06)
- `agent` - the Lana Agent bound to this session's message projection
- `active_turn` - at most one prompt turn runs per session at any time

### EventTranslator

The **EventTranslator** maps each AgentEvent from the stream to zero or more `session/update` notifications (mapping table in LANAACPB-FR-06). It owns `messageId` assignment per logical message.

### PermissionBroker

The **PermissionBroker** implements the Agent's approval callback (LANAAGNT-FR-12 dual consent) by issuing `session/request_permission` and blocking the tool dispatch until the client responds. Holds the session-scoped `allow_always`/`reject_always` memory.

### ElicitationBroker

The **ElicitationBroker** implements the `ask_user_question` tool over `elicitation/create` (form mode) when the client advertised the capability; otherwise returns the capability-missing fallback (LANAACPB-FR-09).

### JsonRpcMessage

A **JsonRpcMessage** is one line on the wire: request (has `id` + `method`), notification (`method`, no `id`), or response (`id` + `result`|`error`). Fields per JSON-RPC 2.0; ACP conventions: camelCase methods, absolute paths, 1-based lines (ACP-IN04).

## 4. Functional Requirements

**LANAACPB-FR-01: ACP Mode Activation and Transport**
- `lana --acp` starts the ACP server on stdio; mutually exclusive with `-p` and interactive REPL
- Messages are newline-delimited JSON-RPC 2.0, UTF-8; no embedded raw newlines (ACP-IN10)
- stdout carries only ACP messages; every diagnostic, warning, and log line goes to stderr
- Each outbound message is flushed immediately (same discipline as session JSONL writes, LANAAGNT-DD-20)
- stdout writes run on a dedicated writer thread fed by a bounded queue (LANAAGNT-IN03 BL-01): a client that stops draining stdout cannot freeze the event loop - cancel and EOF detection stay live; on queue overflow, messages are dropped with a stderr log line (backpressure fail-safe, wire bytes unchanged otherwise)
- EOF on stdin ends the process cleanly (exit 0) after finishing any active turn cancellation and terminating live tool child processes (LANAAGNT-IN03 BL-06)

**LANAACPB-FR-02: Initialization Handshake**
- Respond to `initialize` with `protocolVersion: 1`, `agentInfo` (name `lana`, version from package metadata), and agent capabilities (LANAACPB-IN01, official v1 shape)
- Declared capabilities: `loadSession: true`, `promptCapabilities: {image: false, audio: false, embeddedContext: false}`; nothing else (no `mcpCapabilities`, no `auth`, no `sessionCapabilities` markers in MVP-2)
- If the client requests `protocolVersion: 2`, respond with `1` (client decides to continue or disconnect, ACP-IN05 version negotiation)
- Before `initialize`: send nothing. Before the `initialized` notification: reject session methods with a JSON-RPC error (ACP-IN05 gotchas)

**LANAACPB-FR-03: Session Creation**
- `session/new` creates a Lana session: workspace = `cwd` param; prompt system, config, and system prompt assembled per LANAAGNT-FR-01..03; `session_started` environment record written as first JSONL line (LANAAGNT-FR-08)
- Runtime construction runs off the event loop in the default executor (LANAAGNT-IN03 BL-04): message processing (cancel, ping, second request) stays live during config/prompt-system load; applies to `session/load` identically
- Response carries `sessionId` (= session file stem)
- `mcpServers` param: ignored with one stderr warning (Lana has no MCP client, LANAAGNT-DD-18); `additionalDirectories`: ignored with stderr warning (single-workspace model, LANAAGNT-SP01 workspace definition)
- After the response, send `available_commands_update` listing workflows and built-ins (ACP-IN07 update types; source: loaded PromptSystem)

**LANAACPB-FR-04: Session Load**
- `session/load` resumes a session by id from its JSONL under recorded-environment authority (LANAAGNT-FR-08: recorded system prompt + tool definitions win; fingerprint and model-change warnings go to stderr)
- Conversation history is replayed to the client as `session/update` notifications (user_message_chunk, agent_message_chunk, tool_call + tool_call_update pairs) from the resume projection, then the response completes the load
- Unknown `sessionId` → JSON-RPC error with the id and the sessions directory in the message (self-contained per LANAAGNT-IG-05)
- Legacy session file without `session_started` → load proceeds with disk assembly + stderr warning (LANAAGNT-FR-08 fallback)

**LANAACPB-FR-05: Prompt Turn**
- `session/prompt` runs one Agent turn loop (LANAAGNT-FR-04) with the user input assembled from the prompt's content blocks
- Accepted blocks (v1 baseline, LANAACPB-IN01): `text` → verbatim; `resource_link` → inline reference line `[resource: <name>](<uri>)` appended to the user input (agents MUST accept both - clients send resource_link for file mentions)
- Capability-gated blocks we declared false (`image`, `audio`, `resource`) → reject the request with a JSON-RPC invalid-params error naming the unsupported type
- Streaming: every AgentEvent translates per LANAACPB-FR-06 while the turn runs
- Response carries `stopReason` only (official v1 shape - usage flows via `usage_update` notifications): `end_turn` (normal completion, including user-declined continue at the tool-call limit), `cancelled` (via session/cancel)
- Provider failure mid-turn → JSON-RPC error response on the `session/prompt` id with the self-contained provider message [ASSUMED - the 2026-08-30 INFO lists no `error` stop reason for v1; error response is the JSON-RPC-conformant channel]
- A second `session/prompt` for a session with an active turn → JSON-RPC error (one turn per session)

**LANAACPB-FR-06: Event Translation**
- `turn_started` → no notification; rotates the `messageId` (one logical message per turn)
- `text_delta` → `agent_message_chunk` with text content and the current turn's `messageId`
- `thinking_delta` → `agent_thought_chunk` with `messageId`
- `approval_required` → consumed by the PermissionBroker (LANAACPB-FR-08); never forwarded as a `session/update`
- `tool_call_requested` → `tool_call` (status `pending`, `title` = tool name + primary argument, `kind` per LANAACPB-FR-07)
- `tool_call_finished` → `tool_call_update` (status `completed`|`failed` from the event status, result text as content)
- `turn_finished` → `usage_update` with `used` (the turn's input+output tokens = current context consumption), `size` (generator context window from the pricing entry, 0 when unpriced), `cost` (`{amount, currency: "USD"}` cumulative session total from CostTracker) - official v1 shape per LANAACPB-IN01; mapping synced from implementation 2026-08-30 [TESTED: LANAACPB-IP01-TC-16]
- `todo_list` tool results additionally → `plan` update (entries content/priority/status map 1:1 to Lana todo items)
- `user_message` → not echoed (the client already owns the user's message) except during session/load replay
- `checkpoint_created` → no ACP mapping in v1 (Session Compaction RFD is Draft); one stderr log line documents the omission
- `error` → `agent_message_chunk` carrying the error text, so the client renders the failure inline [ASSUMED - v1 has no dedicated error update type]
- `session_started` → never sent to the client (session-file-only environment record)

**LANAACPB-FR-07: Tool Kind Mapping (16 tools → ACP kinds, ACP-IN08)**
- `read` - read_file, list_dir, view_content_chunk
- `search` - grep_search, find_by_name, trajectory_search
- `edit` - edit, multi_edit, write_to_file
- `execute` - run_command, command_status
- `fetch` - search_web, read_url_content
- `think` - todo_list
- `other` - skill, ask_user_question

**LANAACPB-FR-08: Permission Bridge**
- Every approval the CLI would prompt for (LANAAGNT-FR-12 dual consent under `manual` policy; denylist hits under every policy per LANAAGNT-IG-03) issues `session/request_permission` referencing the announced `toolCallId`, with options: allow_once, allow_always, reject_once, reject_always (ACP-IN08)
- `allow_once`/`reject_once` → single decision; `allow_always`/`reject_always` → remembered for identical action kind + first command token for the session's lifetime (in-memory, not persisted)
- Outcome `cancelled` → treat as rejection; the tool result records the denial (existing non-interactive denial path)
- ExecutionPolicy `auto`/`turbo` semantics unchanged: actions the policy auto-executes never ask the client; the startup risk warning goes to stderr
- The tool-call-limit continue prompt (LANAAGNT-FR-04) → `session/request_permission` with allow_once/reject_once on a synthetic `toolCallId` [ASSUMED - ACP has no dedicated continue mechanism in v1]

**LANAACPB-FR-09: Elicitation Bridge (ask_user_question)**
- Client advertised `elicitation.form` (present AND non-null - `{}` does not imply support, LANAACPB-IN01) → `ask_user_question` issues `elicitation/create` (form mode): question as `message`, options as a required string property with `enum` values in `requestedSchema`; `allowMultiple` → multi-select property; response `action: "accept"` → `content` values become the tool result; `decline`/`cancel` → the existing no-answer fallback
- Client did not advertise it → the tool returns "Client does not support structured questions - ask in plain text" (the Generator then asks inline; mirrors the image-refusal notice pattern of MVP-1)
- URL mode: not used in MVP-2

**LANAACPB-FR-10: Cancellation**
- `session/cancel` (notification) cancels the session's active turn using the existing cancellation machinery (LANAAGNT-FR-04: completed calls kept, cancellation note appended); the pending `session/prompt` response then carries `stopReason: "cancelled"` (ACP-IN07)
- Updates may still flow between `session/cancel` and the response (race by design); idempotent when no turn is active
- Pending `session/request_permission` or `elicitation/create` at cancel time → resolve as cancelled outcome; whether the denial record lands in the JSONL before the turn task's cancellation preempts it is a benign race - the guaranteed contract is the cancellation note plus the cancelled response (synced from implementation 2026-08-30)
- `$/cancel_request` (notification, either direction) on a cancellable outstanding request → same cancellation path, `-32800` Request Cancelled error response where no partial result exists (ACP-IN07)
- Cancellation terminates live tool child processes of the session (LANAAGNT-IN03 BL-02): abandoned executor-thread tools cannot keep mutating the workspace after the cancelled response, and process exit does not block on the `concurrent.futures` atexit join

**LANAACPB-FR-11: Wire Error Handling**
- Unparseable stdin line → error response `-32700` (Parse error) with null id, processing continues
- Unknown method → `-32601` (Method not found); requests carrying invalid params → `-32602`
- Session methods before `initialized`, unknown `sessionId`, second concurrent prompt → structured JSON-RPC errors with self-contained messages (LANAAGNT-IG-05 discipline)
- Errors never crash the connection; only stdin EOF or a fatal startup failure ends the process

## 5. Non-Functional Requirements

**LANAACPB-NFR-01: Compatibility - Protocol Conformance**
- Every wire shape matches the JSON examples in the 2026-08-30 ACP INFO docs byte-structurally (field names, nesting, discriminators)
- Verification: protocol fixtures transcribed verbatim from the INFO docs into the test suite; a fake ACP client drives the real executable (extends the LANAAGNT-FR-14 harness)

**LANAACPB-NFR-02: Security - Inherited Boundaries**
- LANAAGNT-NFR-01 holds in ACP mode: no network calls except the two provider APIs and approved `read_url_content`
- The ACP client is trusted (protocol trust model, ACP-IN09); the permission bridge is the control point, and denylist enforcement (LANAAGNT-IG-03) is agent-side and cannot be bypassed by any client response

**LANAACPB-NFR-03: Reliability - Crash-Safe Parity**
- A kill during an ACP-driven turn loses at most the in-flight turn; the session JSONL replays identically via `session/load` or CLI `--resume` (LANAAGNT-NFR-02 extended to the second frontend)

**LANAACPB-NFR-04: Performance - Streaming Latency**
- Text deltas forward as they arrive - no buffering beyond line assembly; notification write + flush per event (matches CLI rendering immediacy)

## 6. Design Decisions

**LANAACPB-DD-01:** Native in-process ACP module with hand-rolled JSON-RPC, no SDK (Option A of the 2026-08-30 analysis). Rationale: keeps the LANAAGNT-DD-17 closed dependency list; the needed v1 surface is small (3 baseline methods, 2 client-bound requests, notifications); consistent with the LANAAGNT-DD-03 philosophy of owning thin protocol layers; the official Python SDK is pre-1.0. Rejected: SDK (dependency + abstraction risk), bridge process (permission round-trip impossible, adapter tax per ACP-IN14).

**LANAACPB-DD-02:** Protocol v1 only; the version field in `initialize` is the v2 seam. Rationale: v2 is Draft (2026-07-20) and can change; v1-only peers stay common per official guidance; we avoid every surface v2 removes (session modes, client fs/terminal) so migration touches only the translator layer.

**LANAACPB-DD-03:** ACP session = Lana session; `sessionId` = session JSONL file stem. Rationale: the full-recall JSONL (LANAAGNT-DD-22) already IS the session state ACP expects agents to own; no second store, and CLI `--resume` and ACP `session/load` are the same code path.

**LANAACPB-DD-04:** `ask_user_question` maps to Elicitation form mode, not to permission requests. Rationale: elicitation was stabilized for exactly this (structured non-sensitive input, ACP-IN15); permissions are for action approval - the protocol distinguishes the two and so do we.

**LANAACPB-DD-05:** ExecutionPolicy stays agent-side; the client is only consulted where the CLI user would be. Rationale: policy is Lana configuration, not client preference; a client cannot loosen safety (denylist consultations always happen) and does not tighten it (auto policy auto-executes without asking) - behavior is frontend-invariant.

**LANAACPB-DD-06:** `messageId` on every streamed chunk from day one. Rationale: optional in v1, required in v2 (ACP-IN07) - zero-cost forward compatibility.

**LANAACPB-DD-07:** Capabilities declare only what MVP-2 implements: `loadSession`, text prompts. Rationale: "declare capabilities accurately - partial support causes silent failures" (ACP-IN14); resume/close/delete/list and image content are additive later.

**LANAACPB-DD-08:** `todo_list` state maps to ACP `plan` updates. Rationale: entry shape (content, priority, status) matches 1:1; the client gets live plan rendering for free; v1 `plan` replaces the whole plan per update, which matches Lana's whole-list todo semantics exactly.

**LANAACPB-DD-09:** One process serves either the CLI or ACP, never both. Rationale: two interactive frontends on one Agent create input-routing ambiguity; ACP clients spawn a dedicated subprocess per connection anyway (ACP-IN04).

## 7. Implementation Guarantees

**LANAACPB-IG-01:** In `--acp` mode, every byte on stdout belongs to a valid newline-delimited JSON-RPC message. No banner, no warning, no traceback - ever.

**LANAACPB-IG-02:** The session JSONL produced by an ACP-driven session is indistinguishable from a CLI-driven one: same event types, same full-recall first line, replayable by either frontend.

**LANAACPB-IG-03:** Every AgentEvent type has a defined ACP mapping or a documented omission (LANAACPB-FR-06 is exhaustive over the 11 event types).

**LANAACPB-IG-04:** No denylisted command executes on any client response path without an explicit allow outcome (LANAAGNT-IG-03 extended through the permission bridge).

**LANAACPB-IG-05:** A cancelled turn always terminates its pending `session/prompt` with `stopReason: "cancelled"`, and every pending client-bound request of that turn resolves.

## 8. Key Mechanisms

- **Two-frontend architecture**: the Agent yields AgentEvents; the CLI renderer and the ACP EventTranslator are sibling consumers. The Agent has no ACP knowledge
- **Blocking client round-trips inside tool dispatch**: `session/request_permission` and `elicitation/create` are agent-to-client REQUESTS. The tool dispatch awaits the response while the stdin reader keeps processing (bidirectional JSON-RPC, ACP-IN04) - cancellation can arrive during the wait
- **Request id spaces**: client-originated and agent-originated request ids are independent; the connection correlates responses by direction + id
- **Replay-on-load**: `session/load` reuses the resume projection (LANAAGNT-FR-08) both to rebuild Agent state and to stream history to the client - one projection, two consumers

## 9. Action Flow

```
Client sends session/prompt {sessionId, prompt:[{type:"text", ...}]}
├─> AcpSession starts Agent turn (LANAAGNT-FR-04 loop)
│   ├─> AgentEvent text_delta      -> notify session/update agent_message_chunk (messageId)
│   ├─> AgentEvent thinking_delta  -> notify session/update agent_thought_chunk
│   ├─> AgentEvent tool_call_requested -> notify session/update tool_call (pending, kind)
│   │   ├─> Policy requires approval?
│   │   │   └─> request session/request_permission (toolCallId, 4 options)
│   │   │       ├─> allow_once/allow_always -> execute tool
│   │   │       └─> reject_*/cancelled -> tool result records denial
│   │   ├─> Tool is ask_user_question? -> request elicitation/create (form) -> values -> tool result
│   │   └─> AgentEvent tool_call_finished -> notify session/update tool_call_update (completed|failed)
│   ├─> AgentEvent turn_finished   -> notify session/update usage_update
│   └─> Turn loop ends
└─> Respond to session/prompt {stopReason: "end_turn", usage}

Client sends session/cancel (notification, any time during the turn)
├─> Cancel active turn: keep completed calls, append cancellation note (LANAAGNT-FR-04)
├─> Resolve pending permission/elicitation requests as cancelled
└─> Respond to the pending session/prompt {stopReason: "cancelled"}
```

## 10. Data Structures

**Initialization exchange (agent response):**
```json
{"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentInfo": {"name": "lana", "version": "0.2.0"}, "agentCapabilities": {"loadSession": true, "promptCapabilities": {"image": false, "audio": false, "embeddedContext": false}}}}
```

**Tool call with permission round-trip (wire order, one line each):**
```json
{"jsonrpc": "2.0", "method": "session/update", "params": {"sessionId": "2026-08-30_120000_a1b2", "update": {"sessionUpdate": "tool_call", "toolCallId": "tc_001", "title": "run_command: git status", "kind": "execute", "status": "pending"}}}
{"jsonrpc": "2.0", "id": 100, "method": "session/request_permission", "params": {"sessionId": "2026-08-30_120000_a1b2", "toolCall": {"toolCallId": "tc_001"}, "options": [{"optionId": "allow-once", "name": "Allow once", "kind": "allow_once"}, {"optionId": "allow-always", "name": "Always allow", "kind": "allow_always"}, {"optionId": "reject-once", "name": "Reject", "kind": "reject_once"}, {"optionId": "reject-always", "name": "Always reject", "kind": "reject_always"}]}}
{"jsonrpc": "2.0", "id": 100, "result": {"outcome": {"outcome": "selected", "optionId": "allow-once"}}}
{"jsonrpc": "2.0", "method": "session/update", "params": {"sessionId": "2026-08-30_120000_a1b2", "update": {"sessionUpdate": "tool_call_update", "toolCallId": "tc_001", "status": "completed", "content": [{"type": "content", "content": {"type": "text", "text": "On branch master..."}}]}}}
```

**Prompt response and preceding usage notification (v1 shapes):**
```json
{"jsonrpc": "2.0", "method": "session/update", "params": {"sessionId": "2026-08-30_120000_a1b2", "update": {"sessionUpdate": "usage_update", "used": 2300, "size": 200000, "cost": {"amount": 0.045, "currency": "USD"}}}}
{"jsonrpc": "2.0", "id": 3, "result": {"stopReason": "end_turn"}}
```

## 11. Logging Requirements

**Applicable logging types:**
- [ ] User-Facing (UF) - N/A in ACP mode: the client owns the UI; stdout is protocol-only (LANAACPB-IG-01)
- [x] App-Level (AP) - `LOGGING-RULES-APP-LEVEL.md`

**App-Level logging (stderr):**
- **Audience**: Developers debugging an ACP client integration
- **Goal**: Trace method dispatch, capability decisions, and warning conditions without touching stdout
- **Key operations**: handshake, session create/load, permission round-trips, ignored params, translation omissions

**Expected stderr output for a session with one ignored param:**
```
2026-08-30 12:00:01 initialize: client 'Zed 0.175.0', negotiated protocolVersion 1.
2026-08-30 12:00:02 session/new: created '2026-08-30_120000_a1b2' in 'E:/proj'.
2026-08-30 12:00:02   WARNING: 'mcpServers' ignored - Lana has no MCP client.
2026-08-30 12:00:05 session/prompt: turn started.
2026-08-30 12:00:08   request_permission tc_001 (execute) -> allow-once.
2026-08-30 12:00:09 session/prompt: end_turn, 2300 tokens.
```

## 12. Technical Constraints

- The Agent core is reused with one seam: frontend callbacks (approve/continue/ask_user) may return awaitables, which the Agent awaits inside its async loop - CLI sync callbacks pass through unchanged (LANAACPB-IP01-IS-06)
- Single asyncio event loop coordinates stdin dispatch, turn execution, and client-bound requests; the blocking stdin readline itself runs in the default executor (Windows has no async console stdin)
- Windows stdio: UTF-8 encoding enforced on both pipes; line flushing per message (CRLF must not appear inside the JSON payload)
- The scripted replay adapter (LANAAGNT-FR-14) works unchanged under ACP mode - deterministic offline testing of full ACP exchanges
- Session files remain in `<workspace>/.lana-data/sessions/`; the `cwd` from `session/new` is the workspace for tool context and git-root detection
- `available_commands_update` sources the loaded PromptSystem; built-ins (`/help`, `/cost`, `/exit`) are CLI-only and not advertised

## 13. Document History

**[2026-08-30 16:55]**
- Added: hardening per LANAAGNT-IN03 - FR-01 stdout writer thread (BL-01) + process cleanup at EOF (BL-06), FR-03 off-loop runtime construction (BL-04), FR-10 child process termination on cancel (BL-02)

**[2026-08-30 15:10]**
- Changed (`/sync` Code→SPEC after implementation): FR-06 usage_update mapping made precise (per-turn used, pricing-derived size, cumulative cost); FR-10 denial-vs-cancellation race documented as benign

**[2026-08-30 14:00]**
- Fixed: 4 wire shapes corrected per live-doc verification (`/research` → LANAACPB-IN01): FR-02 capabilities (`promptCapabilities` object, top-level `loadSession` - `promptContentTypes` does not exist), FR-05 (accept baseline `resource_link`, response = `stopReason` only), FR-06 (`usage_update` = used/size/cost), FR-09 (elicitation = `message` + `requestedSchema` enum/multi-select), both Data Structures examples
- Changed: Depends-on - LANAACPB-IN01 added as wire-shape authority over the 2026-08-30 snapshot

**[2026-08-30 13:45]**
- Added: explicit protocol version scope statement in Context (user decision: v1 latest stable, v2 breaking changes postponed)
- Verified: `promptContentTypes` capability shape re-checked against ACP-IN05 [VERIFIED] examples - FR-02 shape confirmed correct; `resource_link` absent from v1 docs, FR-05 defensive rejection stands

**[2026-08-30 13:25]**
- Changed: Technical Constraints synced with LANAACPB-IP01 codebase analysis - awaitable callback seam in the Agent (sync CLI callbacks unaffected), stdin readline via default executor

**[2026-08-30 04:15]**
- Initial specification created: Option A (native module) per 2026-08-30 design discussion; wire shapes from ACP-AgentClientProtocol_2026-08-30 [ACP-IN04..08, IN10, IN15]; 11 FRs, 4 NFRs, 9 DDs, 5 IGs
