# ACP: Architecture

**Doc ID**: ACP-IN04
**Goal**: Document the ACP architecture, communication model, and design philosophy
**Version scope**: ACP Protocol v1 (as of 2026-06-12)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references
- `_INFO_ACP-01_Summary.md [ACP-IN01]` for topic context

## Overview

ACP uses a three-actor architecture where the code editor (client) spawns and communicates with an AI coding agent (server) over JSON-RPC 2.0. The agent optionally connects to Model Context Protocol (MCP) servers for tool access. Communication is bidirectional: both sides can initiate requests and send notifications. [VERIFIED] (ACP-SC-ACPORG-OVRVW, ACP-SC-MRCNR-INTRO)

## Design Philosophy

Three principles guide ACP's design: [VERIFIED] (ACP-SC-ACPORG-ARCH)

- **MCP-friendly**: Built on JSON-RPC and re-uses MCP types where possible so integrators don't need yet another representation for common data types
- **UX-first**: Designed to solve the UX challenges of interacting with AI agents, ensuring enough flexibility to render the agent's intent clearly, but no more abstract than needed
- **Trusted**: ACP works when using a code editor to talk to a model you trust. The user retains controls over the agent's tool calls, but the editor gives the agent access to local files and MCP servers

## Three-Actor Model

An ACP deployment has three moving parts: [VERIFIED] (ACP-SC-MRCNR-INTRO, ACP-SC-ACPORG-ARCH)

- **ACP Client (Code Editor)**: Owns the UI and initiates the connection. Spawns the agent as a subprocess, manages sessions, visualizes responses (live diffs), and handles user permission prompts. Zed, JetBrains, Neovim, and Emacs are all clients today.

- **ACP Agent (AI Coding Tool)**: Runs the LLM inference loop, makes tool calls, and edits files. Operates as a standalone subprocess outside the editor environment. Is itself typically an MCP client.

- **MCP Servers (Tools and Data)**: The tools and data sources the agent calls out to. ACP does not replace MCP; it provides the editor-to-agent layer while MCP provides the agent-to-tool layer.

## Communication Model

ACP uses JSON-RPC 2.0 as its wire protocol with two message types: [VERIFIED] (ACP-SC-ACPORG-OVRVW)

- **Methods**: Request-response pairs that expect a result or error. Include an `id` field.
- **Notifications**: One-way messages that don't expect a response. Omit the `id` field.

Communication is bidirectional - both client and agent can initiate requests and send notifications. This is essential because the agent needs to request file access and permissions from the editor during execution.

## Message Flow

The protocol defines a three-phase message flow: [VERIFIED] (ACP-SC-ACPORG-OVRVW)

### Phase 1: Initialization

- Client sends `initialize` to establish the connection and negotiate capabilities
- Agent responds with its capabilities and protocol version
- Client sends `authenticate` if required by the agent

### Phase 2: Session Setup

Either:
- Client sends `session/new` to create a new session (with working directory and MCP servers)
- Client sends `session/load` to resume an existing session (if supported)

### Phase 3: Prompt Turn (repeats)

- Client sends `session/prompt` with the user's message
- Agent sends `session/update` notifications for streaming progress (text chunks, tool calls, plans)
- Agent may request file operations or permissions from the client
- Client may send `session/cancel` to interrupt processing
- Turn ends when the agent sends the `session/prompt` response with a stop reason

## Agent Methods and Notifications

### Baseline Methods (required)

- `initialize`: Negotiate versions and exchange capabilities
- `session/new`: Create a new conversation session
- `session/prompt`: Send user prompts and receive agent responses

### Optional Methods

- `session/load`: Load an existing session (requires `loadSession` capability)
- `logout`: End the current authenticated state (requires `agentCapabilities.auth.logout`)
- `session/set_mode`: Switch between agent operating modes

### Notifications (agent sends)

- `session/cancel`: Cancel ongoing operations

[VERIFIED] (ACP-SC-ACPORG-OVRVW)

## Client Methods and Notifications

### Baseline Methods (required)

- `session/request_permission`: Request user authorization for tool execution

### Optional Methods

- `fs/read_text_file`: Read file contents (requires `clientCapabilities.fs.readTextFile`)
- `fs/write_text_file`: Write file contents (requires `clientCapabilities.fs.writeTextFile`)
- `terminal/create`, `terminal/read`, `terminal/write`, `terminal/resize`, `terminal/wait`: Terminal management (requires `clientCapabilities.terminal`)

### Notifications (client sends)

- `session/update`: Send session updates (message chunks, tool calls, plans, mode changes, slash commands)

[VERIFIED] (ACP-SC-ACPORG-OVRVW)

## Conventions

- Method names use `camelCase`
- Fields in JSON objects use `snake_case` (exception: JSON-RPC standard fields like `jsonrpc`, `id`, `method`, `params`, `result`, `error`)
- All file paths MUST be absolute
- Line numbers are 1-based

[VERIFIED] (ACP-SC-ACPORG-OVRVW)

## Error Handling

ACP follows JSON-RPC 2.0 error handling conventions: [VERIFIED] (ACP-SC-ACPORG-OVRVW)

- Successful responses include a `result` field
- Errors include an `error` object with `code` and `message`
- Notifications never receive responses (success or error)

## Quick Reference

- **Wire protocol**: JSON-RPC 2.0
- **Transport**: stdio (primary), Streamable HTTP (roadmap)
- **Direction**: Bidirectional (both sides initiate)
- **Agent baseline**: `initialize`, `session/new`, `session/prompt`
- **Client baseline**: `session/request_permission`
- **Path convention**: Absolute paths, 1-based line numbers
- **Naming**: `camelCase` methods, `snake_case` fields

## Use Cases

### Basic Flow: User Asks Agent to Edit a File

1. Editor sends `session/prompt` with user's request
2. Agent streams thinking via `session/update` (agent_message_chunk)
3. Agent announces tool call via `session/update` (tool_call, kind: "edit")
4. Agent requests permission via `session/request_permission`
5. User approves; editor responds with `allow_once`
6. Agent reads file via `fs/read_text_file`, modifies, writes via `fs/write_text_file`
7. Agent sends `session/update` (tool_call_update, status: "completed") with diff content
8. Agent sends `session/prompt` response with `stopReason: "end_turn"`

## Limitations and Gotchas

- The bidirectional nature means both client and agent must handle incoming requests at any time, adding implementation complexity
- `session/cancel` is a notification (no response), so the client cannot confirm cancellation succeeded - it must watch for the `cancelled` stop reason on the pending `session/prompt`
- The client filesystem and terminal surface are optional capabilities - agents cannot assume they are available
- v2 proposes removing the client fs/terminal surface entirely, so implementations should not over-invest in this area

## Sources

- ACP-SC-ACPORG-ARCH - Official architecture page
- ACP-SC-ACPORG-OVRVW - Protocol v1 overview (methods, notifications, conventions)
- ACP-SC-MRCNR-INTRO - Marc Nuri blog (three-actor model, ecosystem analysis)

## Document History

**[2026-06-12 09:52]**
- Initial document created
