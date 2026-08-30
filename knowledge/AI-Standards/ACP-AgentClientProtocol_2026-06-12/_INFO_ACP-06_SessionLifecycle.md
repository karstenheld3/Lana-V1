# ACP: Session Lifecycle

**Doc ID**: ACP-IN06
**Goal**: Document the full session management lifecycle in ACP
**Version scope**: ACP Protocol v1 (as of 2026-06-12)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

Work in ACP is organized into sessions (a conversation with shared context) and turns (one prompt-to-response cycle within a session). Sessions persist across prompts so context accumulates. The protocol supports creating, loading, resuming, closing, deleting, and listing sessions. Model Context Protocol (MCP) server endpoints and workspace roots are configured at session creation time. [VERIFIED] (ACP-SC-ACPORG-SSSTP, ACP-SC-MRCNR-INTRO)

## Creating a Session

`session/new` creates a new conversation session. The client provides: [VERIFIED] (ACP-SC-ACPORG-SSSTP)

- **Working directory** (`cwd`): Absolute path, used as the base for relative-path resolution
- **MCP servers** (`mcpServers`): List of MCP server configurations the agent should connect to

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "session/new",
  "params": {
    "cwd": "/home/user/project",
    "mcpServers": [
      {
        "name": "filesystem",
        "command": "/path/to/mcp-server",
        "args": ["--stdio"],
        "env": []
      }
    ]
  }
}
```

The agent responds with a session ID:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "sessionId": "sess_abc123def456"
  }
}
```

## Loading Sessions

`session/load` resumes a previously created session by its ID. Requires `loadSession` capability. [VERIFIED] (ACP-SC-ACPORG-SSSTP)

## Resuming Sessions

`session/resume` provides an alternative to `session/load` that reconnects to an existing session. Requires `sessionCapabilities.resume` capability. This was stabilized as part of the protocol updates. [VERIFIED] (ACP-SC-ACPORG-UPDTS)

Key difference: `session/load` creates a new agent connection to an old session; `session/resume` reconnects to a session that may still be active.

## Closing Sessions

`session/close` gracefully terminates an active session. Requires `sessionCapabilities.close` capability. Stabilized as a protocol update. [VERIFIED] (ACP-SC-ACPORG-UPDTS)

## Deleting and Listing Sessions

- `session/delete`: Removes a session from history. Requires `sessionCapabilities.delete`.
- `session/list`: Discovers existing sessions. Requires `sessionCapabilities.list` to be advertised. Stabilized as a protocol update. [VERIFIED] (ACP-SC-ACPORG-UPDTS)

## Working Directory

The `cwd` field in session requests has strict semantics: [VERIFIED] (ACP-SC-ACPORG-SSSTP)

- MUST be an absolute path
- MUST be used for the session regardless of where the agent subprocess was spawned
- MUST remain the base for relative-path resolution
- MUST be part of the session's effective root set

## Additional Workspace Roots

Agents that advertise `sessionCapabilities.additionalDirectories` support extra workspace roots beyond the primary `cwd`: [VERIFIED] (ACP-SC-ACPORG-SSSTP)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "session/load",
  "params": {
    "sessionId": "sess_789xyz",
    "cwd": "/home/user/project",
    "additionalDirectories": [
      "/home/user/shared-lib",
      "/home/user/product-docs"
    ],
    "mcpServers": []
  }
}
```

Rules for additional directories:
- `cwd` remains the primary working directory and base for relative paths
- Each `additionalDirectories` entry MUST be an absolute path
- Omitting the field or providing an empty array activates no additional roots
- On `session/load` and `session/resume`, clients must send the full intended root list again; it may differ from previous lists

## MCP Server Configuration

ACP sessions wire up MCP integration at session creation time. The client passes MCP server configurations, and the agent connects to them. [VERIFIED] (ACP-SC-ACPORG-SSSTP, ACP-SC-MRCNR-INTRO)

### Transport Types

**Stdio Transport** (default):
```json
{
  "name": "filesystem",
  "command": "/path/to/mcp-server",
  "args": ["--stdio"],
  "env": [
    { "name": "API_KEY", "value": "secret123" }
  ]
}
```

**HTTP Transport** (requires `mcpCapabilities.http`):
```json
{
  "type": "http",
  "name": "api-server",
  "url": "https://api.example.com/mcp",
  "headers": [
    { "name": "Authorization", "value": "Bearer token123" }
  ]
}
```

**SSE Transport** (requires `mcpCapabilities.sse`):
```json
{
  "type": "sse",
  "name": "event-stream",
  "url": "https://events.example.com/mcp",
  "headers": [
    { "name": "X-API-Key", "value": "apikey456" }
  ]
}
```

### Checking Transport Support

The agent advertises MCP transport support in its capabilities:
```json
{
  "agentCapabilities": {
    "mcpCapabilities": {
      "http": true,
      "sse": true
    }
  }
}
```

If `mcpCapabilities.http` is `false` or absent, only stdio MCP servers are supported. [VERIFIED] (ACP-SC-ACPORG-SSSTP)

## Quick Reference

- **Create**: `session/new` (baseline, always available)
- **Load**: `session/load` (requires `loadSession`)
- **Resume**: `session/resume` (requires `sessionCapabilities.resume`)
- **Close**: `session/close` (requires `sessionCapabilities.close`)
- **Delete**: `session/delete` (requires `sessionCapabilities.delete`)
- **List**: `session/list` (requires `sessionCapabilities.list`)
- **Session ID**: Returned by `session/new`, used in all subsequent requests
- **cwd**: Always absolute, always required

## Use Cases

### Multi-Root Workspace

An editor with multiple open projects passes them as additional directories so the agent can access files across project boundaries during a single session.

### MCP-Integrated Session

An editor configures a database MCP server and a browser automation MCP server at session start. The agent can then query the database and interact with web pages without separate setup.

## Limitations and Gotchas

- `session/new` is the only baseline session method; all others require capability negotiation
- The agent cannot autonomously discover MCP servers - the editor must explicitly configure and pass them
- `additionalDirectories` is not preserved across reconnections: clients must re-send the full list on `session/load` and `session/resume`
- v2 proposes requiring MCP server configurations to include a `type` discriminator even for stdio, changing the current implicit default

## Sources

- ACP-SC-ACPORG-SSSTP - Official session setup page
- ACP-SC-ACPORG-OVRVW - Protocol overview (session methods)
- ACP-SC-ACPORG-UPDTS - Stabilization announcements for session resume, close, list
- ACP-SC-MRCNR-INTRO - MCP integration description

## Document History

**[2026-06-12 09:58]**
- Initial document created
