# ACP: Transports and Extensibility

**Doc ID**: ACP-IN10
**Goal**: Document ACP transport mechanisms and protocol extension patterns
**Version scope**: ACP Protocol v1 (as of 2026-06-12)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP currently supports stdio as its primary transport (the client spawns the agent as a subprocess) with Streamable HTTP described but not yet widely adopted. The protocol provides three extension mechanisms: `_meta` fields for custom data, underscore-prefixed methods for custom operations, and custom capability advertising during initialization. [VERIFIED] (ACP-SC-ACPORG-TRNSP, ACP-SC-ACPORG-EXTNS)

## Transports

### stdio (Primary)

The standard transport for local agent integration: [VERIFIED] (ACP-SC-ACPORG-TRNSP)

- The client launches the agent as a subprocess
- The agent reads JSON-RPC messages from `stdin` and sends messages to `stdout`
- Messages are individual JSON-RPC requests, notifications, or responses
- Messages are delimited by newlines (`\n`) and MUST NOT contain embedded newlines
- The agent MAY write UTF-8 strings to `stderr` for logging (clients may capture, forward, or ignore)
- The agent MUST NOT write anything to `stdout` that is not a valid ACP message
- The client MUST NOT write anything to the agent's `stdin` that is not a valid ACP message

### Streamable HTTP

Described in the spec and under active development by the Transports Working Group. Intended for remote agent scenarios where the agent runs on a separate server. Currently not widely implemented. [VERIFIED] (ACP-SC-ACPORG-TRNSP, ACP-SC-ACPORG-UPDTS)

### Custom Transports

Implementations may define additional transports beyond stdio and HTTP, following the same JSON-RPC 2.0 message format.

## Extensibility

ACP provides three mechanisms for extending the protocol without breaking compatibility: [VERIFIED] (ACP-SC-ACPORG-EXTNS)

### The `_meta` Field

Any ACP message can include a `_meta` field for custom data. This is a free-form object (`{ [key: string]: unknown }`) that implementations can use to pass additional context: [VERIFIED] (ACP-SC-ACPORG-EXTNS)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_abc123def456",
    "prompt": [
      { "type": "text", "text": "Hello, world!" }
    ],
    "_meta": {
      "traceparent": "00-80e1afed08e019fc1110464cfa66635c-7a085853722dc6d2-01",
      "zed.dev/debugMode": true
    }
  }
}
```

The `_meta` field supports W3C trace context fields for distributed tracing:
- `traceparent`
- `tracestate`
- `baggage`

### Extension Methods

Custom methods use an underscore (`_`) prefix to distinguish them from standard protocol methods. They follow standard JSON-RPC 2.0 patterns: [VERIFIED] (ACP-SC-ACPORG-EXTNS)

**Custom Requests** (include `id`, expect response):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "_zed.dev/workspace/buffers",
  "params": { "language": "rust" }
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "buffers": [
      { "id": 0, "path": "/home/user/project/src/main.rs" },
      { "id": 1, "path": "/home/user/project/src/editor.rs" }
    ]
  }
}
```

If the other side does not recognize the method, it returns a standard JSON-RPC "Method not found" error:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": { "code": -32601, "message": "Method not found" }
}
```

**Custom Notifications** (no `id`, no response):
```json
{
  "jsonrpc": "2.0",
  "method": "_zed.dev/file_opened",
  "params": { "path": "/home/user/project/src/editor.rs" }
}
```

### Custom Capabilities

Custom capabilities are advertised during initialization using the `_meta` field within capabilities: [VERIFIED] (ACP-SC-ACPORG-EXTNS)

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocolVersion": 1,
    "agentCapabilities": {
      "loadSession": true,
      "_meta": {
        "zed.dev": {
          "workspace": true,
          "fileNotifications": true
        }
      }
    }
  }
}
```

This allows implementations to negotiate vendor-specific features without polluting the standard capability namespace.

## Quick Reference

- **Primary transport**: stdio (JSON-RPC over stdin/stdout, newline-delimited)
- **Future transport**: Streamable HTTP (in development)
- **Custom data**: `_meta` field on any message
- **Custom methods**: Underscore prefix (e.g., `_zed.dev/workspace/buffers`)
- **Custom capabilities**: `_meta` within capabilities during initialization
- **Naming convention**: Use reverse domain notation for vendor extensions (e.g., `zed.dev/`)

## Use Cases

### Distributed Tracing

An editor passes W3C `traceparent` headers in `_meta` on every prompt, enabling end-to-end trace correlation from the editor through the agent to Model Context Protocol (MCP) server calls.

### Zed-Specific Workspace Features

Zed uses custom methods like `_zed.dev/workspace/buffers` to expose editor-specific workspace state to agents, enhancing the agent's context without requiring protocol changes.

## Limitations and Gotchas

- stdio is inherently local - it cannot be used for remote agent deployments without a tunneling layer
- The agent's `stderr` logging has no standard format; clients handle it inconsistently
- Embedded newlines in JSON-RPC messages are forbidden on stdio, requiring careful serialization of multi-line content
- Extension methods may silently fail if the other side doesn't recognize them (custom notifications have no error path)
- No versioning mechanism for custom capabilities - vendors must handle backward compatibility themselves
- The Transports Working Group is actively developing HTTP transport, but details are not yet stabilized
- v2 proposes more structured extension patterns including enum variant extensions

## Sources

- ACP-SC-ACPORG-TRNSP - Official transports page
- ACP-SC-ACPORG-EXTNS - Official extensibility page
- ACP-SC-ACPORG-UPDTS - Transports Working Group announcement

## Document History

**[2026-06-12 10:08]**
- Initial document created
