# ACP: Architecture

**Doc ID**: ACP-IN04
**Goal**: Document ACP's three-actor architecture, communication model, and method inventory
**Version scope**: ACP Protocol v1 (stable) + v2 changes noted where applicable

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP follows a bidirectional JSON-RPC 2.0 communication model between a Client (editor/IDE) and an Agent (AI program). Both sides can initiate requests and send notifications. The protocol uses three phases: Initialization, Session Setup, and Prompt Turn. Model Context Protocol (MCP) servers provide tools and resources to the agent, completing the three-actor model. [VERIFIED] (ACP-SC-ACPORG-ARCH)

## Three-Actor Model

```
Client (Editor/IDE) <--ACP (JSON-RPC 2.0)--> Agent <--MCP--> Tool Servers
```

- **Client**: Hosts the UI, manages files and terminals, mediates user permissions, and displays agent output. The client spawns the agent as a subprocess (stdio transport).
- **Agent**: Processes prompts, generates responses, invokes tools, and streams progress. The agent connects to MCP servers for tool access.
- **MCP Servers**: External tool providers (file systems, databases, APIs) connected via Model Context Protocol. Configurations are passed from client to agent at session creation.

[VERIFIED] (ACP-SC-ACPORG-ARCH)

## Design Philosophy

Three core principles: [VERIFIED] (ACP-SC-ACPORG-ARCH)

- **MCP-Friendly**: ACP is designed to complement MCP. Agents can proxy MCP server configurations received from the editor.
- **UX-First**: Rich streaming, structured permission prompts, progress reporting, and elicitation for user input. The protocol prioritizes responsive user experience.
- **Trusted**: The agent is a trusted subprocess. The editor mediates all destructive actions through the permission system. No sandboxing or agent identity verification is built into the protocol.

## Communication Model

ACP uses JSON-RPC 2.0 with three message types: [VERIFIED] (ACP-SC-ACPORG-ARCH)

- **Requests**: Include `id`, expect a response. Either side can send requests.
- **Responses**: Match a request by `id`. Contain `result` or `error`.
- **Notifications**: No `id`, no response expected. Used for streaming updates.

### Three-Phase Message Flow

**Phase 1: Initialization**
1. Client sends `initialize` with `protocolVersion` and `clientCapabilities`
2. Agent responds with `protocolVersion` and `agentCapabilities`
3. Client sends `initialized` notification (handshake complete)

**Phase 2: Session Setup**
4. Client sends `session/new` or `session/resume` with working directory and MCP configs
5. Agent responds with session ID and metadata

**Phase 3: Prompt Turn**
6. Client sends `session/prompt` with user message
7. Agent streams `session/update` notifications (text, tool calls, plans)
8. Agent responds to `session/prompt` with the stop reason (usage flows separately via `usage_update` notifications)

## v1 Method Inventory

### Agent Methods (agent implements, client calls)

**Baseline (required):**
- `initialize` - Protocol handshake and capability negotiation
- `session/new` - Create a new session
- `session/prompt` - Send a user prompt
- `session/cancel` - Cancel an ongoing prompt turn (notification)
- `$/cancel_request` - Cancel any outstanding JSON-RPC request (notification, either direction) [VERIFIED] (ACP-SC-ANN-RQCNL)

**Optional (gated by capabilities):**
- `authenticate` - Trigger authentication flow
- `logout` - End authenticated state (requires `agentCapabilities.auth.logout`)
- `session/load` - Load an existing session by ID, replaying full history (requires top-level `agentCapabilities.loadSession`)
- `session/resume` - Reconnect without history replay (requires `sessionCapabilities.resume`)
- `session/close` - Gracefully terminate a session (requires `sessionCapabilities.close`)
- `session/delete` - Remove a session permanently (requires `sessionCapabilities.delete`) [VERIFIED] (ACP-SC-ANN-SSDEL)
- `session/list` - List available sessions (requires `sessionCapabilities.list`)
- `session/set_config_option` - Set a session configuration option (requires `sessionCapabilities.configOptions`)

### Client Methods (client implements, agent calls)

**Baseline (required):**
- `session/request_permission` - Request user permission for an action

**Optional (gated by capabilities):**
- `fs/read_text_file` - Read a file from the workspace
- `fs/write_text_file` - Write a file to the workspace
- `terminal/create` - Create a terminal session
- `terminal/output` - Send output to a terminal
- `terminal/release` - Release a terminal
- `terminal/wait_for_exit` - Wait for terminal process to exit
- `terminal/kill` - Kill a terminal process
- `elicitation/create` - Request structured user input (requires `clientCapabilities.elicitation.form`/`.url`) [VERIFIED] (ACP-SC-ANN-ELCTN)
- `elicitation/complete` - Signal out-of-band elicitation completion (notification, agent to client) [VERIFIED] (ACP-SC-ANN-ELCTN)

### Notifications

- `session/update` (agent to client) - Stream session state changes (text, tool calls, plans, etc.)
- `initialized` (client to agent) - Handshake acknowledgment

## v2 Method Changes (Draft)

Key method changes in v2: [VERIFIED] (ACP-SC-ACPORG-V2MIG)

- `authenticate` renamed to `auth/login`
- `logout` renamed to `auth/logout`
- `session/load` removed; use `session/resume` with `replayFrom`
- `session/list`, `session/resume`, `session/close` become baseline (required) when `session` capability is present
- `fs/*` and `terminal/*` methods removed entirely
- `session/prompt` response becomes acknowledgment only; output via `session/update`
- New `state_update` variant in `session/update` (running/idle/requires_action)

See `_INFO_ACP-16_V2MigrationOverview.md [ACP-IN16]` for complete migration details.

## Conventions

- **Error codes**: Standard JSON-RPC 2.0 error codes (-32700, -32600, -32601, -32602, -32603) plus ACP-specific `-32800` (Request Cancelled) [VERIFIED] (ACP-SC-ACPORG-ARCH, ACP-SC-ANN-RQCNL)
- **Session IDs**: Opaque strings, agent-generated
- **Content types**: `text` and `resource_link` (mandatory baseline in prompts), `image`/`audio` (base64), `resource` (embedded context) - optional types capability-gated via `promptCapabilities`
- **Naming**: object property keys use camelCase; discriminator string values use snake_case
- **Newline framing**: stdio messages are newline-delimited, MUST NOT contain embedded newlines

## Sources

- ACP-SC-ACPORG-ARCH - Architecture, design philosophy, communication model
- ACP-SC-ACPORG-OVRVW - Protocol overview and method inventory
- ACP-SC-ACPORG-V2MIG - v2 method changes and migration guide
- ACP-SC-ANN-RQCNL - Request cancellation ($/cancel_request) stabilization
- ACP-SC-ANN-SSDEL - Session delete stabilization
- ACP-SC-ANN-ELCTN - Elicitation methods stabilization

## Document History

**[2026-08-30 14:20]**
- Fixed: prompt response carries stop reason only (usage was hallucinated); `session/set_config_option` is capability-gated, not baseline; `elicitation/complete` is a client-implemented notification (was listed as agent method); notifications section directions
- Added: capability gates per optional method; content type baseline; camelCase/snake_case naming convention

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: v1 methods stabilized since June 2026 ($/cancel_request, session/delete, elicitation/create, elicitation/complete)
- Added: v2 method changes section (method renames, removals, new requirements)
- Added: -32800 Request Cancelled error code
- Updated: Method inventory to include all stabilized features

**[2026-06-12 09:20]**
- Initial document created
