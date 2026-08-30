# ACP: Session Lifecycle

**Doc ID**: ACP-IN06
**Goal**: Document ACP session management methods and lifecycle
**Version scope**: ACP Protocol v1 (stable) + v2 changes noted

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP sessions encapsulate a conversation between a client and an agent. The session lifecycle includes creating new sessions, loading/resuming existing ones, configuring workspace roots, closing sessions gracefully, deleting them permanently, and listing available sessions. MCP server configurations are passed at session creation time. [VERIFIED] (ACP-SC-ACPORG-SSSTP)

## Creating a Session

`session/new` creates a fresh session with a working directory and optional MCP configurations: [VERIFIED] (ACP-SC-ACPORG-SSSTP)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "session/new",
  "params": {
    "cwd": "/home/user/project",
    "additionalDirectories": ["/home/user/shared-lib"],
    "mcpServers": [
      {
        "name": "filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"],
        "env": []
      }
    ]
  }
}
```

`mcpServers` is an ARRAY of server objects (stdio: `name`/`command`/`args`/`env`; http and sse variants carry a URL instead). [VERIFIED] (ACP-SC-ACPORG-SSSTP)

Response carries the session ID (plus session-mode state when the agent uses session modes; the `modes` field is removed in v2):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "sessionId": "sess_abc123def456"
  }
}
```

## Loading a Session

`session/load` restores a previously created session by ID (requires the TOP-LEVEL `agentCapabilities.loadSession` - not a `sessionCapabilities` marker). The agent MUST replay the entire conversation to the client as `session/update` notifications before responding: [VERIFIED] (ACP-SC-ACPORG-SSSTP)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "session/load",
  "params": {
    "sessionId": "sess_abc123def456",
    "cwd": "/home/user/project",
    "mcpServers": [],
    "additionalDirectories": ["/home/user/shared-lib"]
  }
}
```

**Note**: `session/load` is removed in v2. Use `session/resume` with `"replayFrom": { "type": "start" }` instead.

## Resuming a Session

`session/resume` reconnects to an existing session WITHOUT replaying conversation history - it restores context, reconnects MCP servers, and returns when ready (requires `agentCapabilities.sessionCapabilities.resume`): [VERIFIED] (ACP-SC-ACPORG-SSSTP)

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "session/resume",
  "params": {
    "sessionId": "sess_abc123def456",
    "cwd": "/home/user/project"
  }
}
```

## Closing a Session

`session/close` gracefully terminates a session (requires `agentCapabilities.sessionCapabilities.close`): [VERIFIED] (ACP-SC-ACPORG-UPDTS)

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "session/close",
  "params": {
    "sessionId": "sess_abc123def456"
  }
}
```

## Deleting a Session

`session/delete` permanently removes a session and its data (requires `agentCapabilities.sessionCapabilities.delete`): [VERIFIED] (ACP-SC-ANN-SSDEL)

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "session/delete",
  "params": {
    "sessionId": "sess_abc123def456"
  }
}
```

## Listing Sessions

`session/list` returns available sessions (requires `agentCapabilities.sessionCapabilities.list`): [VERIFIED] (ACP-SC-ACPORG-UPDTS)

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "session/list",
  "params": {}
}
```

## Working Directory and Additional Roots

- `cwd`: The primary working directory for the session
- `additionalDirectories`: Extra workspace roots the agent should be aware of [VERIFIED] (ACP-SC-ACPORG-UPDTS)

**Gotcha**: `additionalDirectories` are NOT persistent across reconnections. Clients must re-send the full root list on every `session/load` and `session/resume`. [VERIFIED] (ACP-SC-ACPORG-SSSTP)

## MCP Server Configuration

MCP servers are configured at session creation via the `mcpServers` object. Three transport types are supported: [VERIFIED] (ACP-SC-ACPORG-SSSTP)

- **stdio**: Local subprocess with command, args, and optional env variables
- **http**: Remote HTTP endpoint with URL
- **sse**: Server-Sent Events endpoint (deprecated in v2)

## Session Config Options

Agents can expose session-level configuration options: [VERIFIED] (ACP-SC-ACPORG-UPDTS)

- **Boolean config options**: On/off toggles for agent features [VERIFIED] (ACP-SC-ANN-BOOLC)
- **Model config category**: Model-related configuration options [VERIFIED] (ACP-SC-ANN-MDLCF)
- Set via `session/set_config_option`, updates via `config_option_update` notification

## Session Info Updates

Agents send `session_info_update` notifications when session metadata changes (e.g., title): [VERIFIED] (ACP-SC-ACPORG-UPDTS)

## v2 Session Changes (Draft)

Key changes in v2: [VERIFIED] (ACP-SC-ACPORG-V2MIG)

- `session/load` removed; `session/resume` with optional `replayFrom` handles both use cases
- `session/list`, `session/resume`, `session/close` become baseline (required) when `session` capability is present
- `session/delete` remains optional via `session.delete` capability
- `mcpServers` becomes optional in `session/new`
- SSE MCP transport type removed; only stdio and HTTP retained
- Session modes API removed; replaced by `session/set_config_option` and `config_option_update`

## Quick Reference

- **Create**: `session/new` (always available)
- **Load**: `session/load` (optional, removed in v2)
- **Resume**: `session/resume` (optional in v1, baseline in v2)
- **Close**: `session/close` (optional in v1, baseline in v2)
- **Delete**: `session/delete` (optional)
- **List**: `session/list` (optional in v1, baseline in v2)
- **Config**: `session/set_config_option` (requires `sessionCapabilities.configOptions`)

## Limitations and Gotchas

- `additionalDirectories` not persistent across reconnections
- `session/load` and `session/resume` are distinct in v1; merged in v2
- MCP credentials (API keys, tokens) are passed in cleartext via env variables or HTTP headers
- The agent decides session ID format and persistence strategy
- `session/close` does not guarantee cleanup of agent-side resources

## Sources

- ACP-SC-ACPORG-SSSTP - Session setup, MCP configuration, workspace roots
- ACP-SC-ACPORG-UPDTS - Session list, close, resume, info update, config options stabilizations
- ACP-SC-ANN-SSDEL - Session delete stabilization
- ACP-SC-ANN-BOOLC - Boolean config options
- ACP-SC-ANN-MDLCF - Model config category
- ACP-SC-ACPORG-V2MIG - v2 session changes

## Document History

**[2026-08-30 14:20]**
- Fixed: capability gates corrected against official docs - `session/load` gated by TOP-LEVEL `loadSession`; resume/close/delete/list gated by `sessionCapabilities.*` markers (the `agentCapabilities.session.*` paths were hallucinated)
- Fixed: `mcpServers` is an array of server objects, not a name-keyed map; `session/new` response example reduced to `sessionId` (unverified `title` removed)
- Added: session/load full-replay obligation; session/resume no-replay semantics; config options capability gate

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: session/delete method (stabilized)
- Added: Session config options (boolean, model_config)
- Added: v2 session changes section
- Updated: Quick reference with v1/v2 baseline status

**[2026-06-12 09:30]**
- Initial document created
