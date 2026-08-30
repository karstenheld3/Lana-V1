# ACP: Transports and Extensibility

**Doc ID**: ACP-IN10
**Goal**: Document ACP transport mechanisms and protocol extension patterns
**Version scope**: ACP Protocol v1 (stable) + v2 changes noted

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP currently supports stdio as its primary transport (the client spawns the agent as a subprocess) with Streamable HTTP described but not yet widely adopted. The protocol provides three extension mechanisms: `_meta` fields for custom data, underscore-prefixed methods for custom operations, and custom capability advertising during initialization. [VERIFIED] (ACP-SC-ACPORG-TRNSP, ACP-SC-ACPORG-EXTNS)

## Transports

### stdio (Primary)

The standard transport for local agent integration: [VERIFIED] (ACP-SC-ACPORG-TRNSP)

- The client launches the agent as a subprocess
- The agent reads JSON-RPC messages from `stdin` and sends messages to `stdout`
- Messages are delimited by newlines (`\n`) and MUST NOT contain embedded newlines
- The agent MAY write UTF-8 strings to `stderr` for logging
- The agent MUST NOT write anything to `stdout` that is not a valid ACP message

### Streamable HTTP

Described in the spec and under active development by the Transports Working Group. Intended for remote agent scenarios. The Python SDK (v0.12.0+) added RFD-based HTTP and WebSocket transport implementation. [VERIFIED] (ACP-SC-ACPORG-TRNSP, ACP-SC-ACPORG-UPDTS, ACP-SC-GH-PYSD)

### Custom Transports

Implementations may define additional transports beyond stdio and HTTP, following the same JSON-RPC 2.0 message format.

## Extensibility

Three mechanisms for extending the protocol: [VERIFIED] (ACP-SC-ACPORG-EXTNS)

### The `_meta` Field

Any ACP message can include a `_meta` field for custom data (`{ [key: string]: unknown }`):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_abc123def456",
    "prompt": [{ "type": "text", "text": "Hello" }],
    "_meta": {
      "traceparent": "00-80e1afed08e019fc1110464cfa66635c-7a085853722dc6d2-01",
      "zed.dev/debugMode": true
    }
  }
}
```

Supports W3C trace context fields: `traceparent`, `tracestate`, `baggage`.

### Extension Methods

Custom methods use underscore (`_`) prefix: [VERIFIED] (ACP-SC-ACPORG-EXTNS)

**Requests** (include `id`, expect response):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "_zed.dev/workspace/buffers",
  "params": { "language": "rust" }
}
```

**Notifications** (no `id`, no response):
```json
{
  "jsonrpc": "2.0",
  "method": "_zed.dev/file_opened",
  "params": { "path": "/home/user/project/src/editor.rs" }
}
```

Unrecognized methods return `-32601` (Method not found). Naming convention: reverse domain notation (e.g., `zed.dev/`).

### Custom Capabilities

Custom capabilities use `_meta` within capabilities during initialization:

```json
{
  "agentCapabilities": {
    "loadSession": true,
    "_meta": {
      "zed.dev": { "workspace": true, "fileNotifications": true }
    }
  }
}
```

## v2 Extensibility Changes (Draft)

- v2 schema is forward-compatible by default (unknown fields preserved, not rejected) [VERIFIED] (ACP-SC-ACPORG-V2MIG)
- Enum variant extensions allow adding new discriminated union members
- SSE MCP transport removed; only stdio and HTTP retained for MCP servers
- `session.mcp.stdio` becomes explicit capability

## Quick Reference

- **Primary transport**: stdio (JSON-RPC over stdin/stdout, newline-delimited)
- **Future transport**: Streamable HTTP (Transports Working Group, Python SDK has early implementation)
- **Custom data**: `_meta` field on any message
- **Custom methods**: Underscore prefix (e.g., `_zed.dev/workspace/buffers`)
- **Custom capabilities**: `_meta` within capabilities during initialization
- **Naming**: Reverse domain notation for vendor extensions

## Limitations and Gotchas

- stdio is inherently local; cannot be used for remote agents without tunneling
- stderr logging has no standard format; clients handle it inconsistently
- Embedded newlines in JSON-RPC messages are forbidden on stdio
- Extension methods may silently fail (custom notifications have no error path)
- No versioning mechanism for custom capabilities
- v2 removes SSE MCP transport; HTTP is the only remote MCP option

## Sources

- ACP-SC-ACPORG-TRNSP - Official transports page
- ACP-SC-ACPORG-EXTNS - Official extensibility page
- ACP-SC-ACPORG-UPDTS - Transports Working Group announcement
- ACP-SC-ACPORG-V2MIG - v2 forward compatibility and transport changes
- ACP-SC-GH-PYSD - Python SDK HTTP/WS transport implementation

## Document History

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: Python SDK HTTP/WebSocket transport implementation reference
- Added: v2 extensibility changes (forward-compatible schema, enum extensions)
- Added: v2 SSE removal, explicit stdio capability

**[2026-06-12 10:08]**
- Initial document created
