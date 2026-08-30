# MCP: Protocol Lifecycle

**Doc ID**: MCP-IN04
**Goal**: Document the MCP connection lifecycle, message format, and capability negotiation
**Version scope**: Spec 2025-11-25 (current)

**Depends on:**
- `_INFO_MCP-03_ProblemAndArchitecture.md [MCP-IN03]` for architecture context
- `_INFO_MCP-02_Sources.md [MCP-IN02]` for source references

## Summary

MCP uses JSON-RPC 2.0 as its wire format with three message types: requests, responses, and notifications. The connection lifecycle has three phases: initialization (capability and version negotiation via handshake), operation (normal message exchange), and shutdown (graceful termination). Capability negotiation during initialization determines which optional features are active per session. Version negotiation selects the newest mutually supported protocol version using YYYY-MM-DD format strings.

## JSON-RPC 2.0 Message Format

All messages MUST follow JSON-RPC 2.0 specification. Messages MUST be UTF-8 encoded. [VERIFIED, spec]

### Three Message Types

**Requests** (bidirectional, require response):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": { "name": "get_weather", "arguments": { "city": "Berlin" } }
}
```
- ID MUST be string or integer, MUST NOT be null
- ID MUST NOT be reused within the same session

**Responses** (success or error):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": { "content": [{ "type": "text", "text": "22C, sunny" }] }
}
```
Error response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": { "code": -32602, "message": "Invalid params", "data": {} }
}
```

**Notifications** (one-way, no response expected):
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```
- Notifications MUST NOT include an ID
- Receiver MUST NOT send a response

## Connection Lifecycle

Three phases: [VERIFIED, spec: Lifecycle section]

### Phase 1: Initialization

The initialization phase MUST be the first interaction. During this phase:
1. Client sends `initialize` request with protocol version, capabilities, and client info
2. Server responds with its capabilities, info, and optional instructions
3. Client sends `initialized` notification to signal readiness

**Initialize request** (client to server):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "roots": { "listChanged": true },
      "sampling": {},
      "elicitation": { "form": {}, "url": {} },
      "tasks": {
        "requests": {
          "elicitation": { "create": {} },
          "sampling": { "createMessage": {} }
        }
      }
    },
    "clientInfo": {
      "name": "ExampleClient",
      "version": "1.0.0"
    }
  }
}
```

**Initialize response** (server to client):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "logging": {},
      "prompts": { "listChanged": true },
      "resources": { "subscribe": true, "listChanged": true },
      "tools": { "listChanged": true },
      "tasks": {
        "list": {},
        "cancel": {},
        "requests": { "tools": { "call": {} } }
      }
    },
    "serverInfo": {
      "name": "ExampleServer",
      "version": "1.0.0"
    },
    "instructions": "Optional instructions for the client"
  }
}
```

**Initialized notification** (client to server):
```json
{ "jsonrpc": "2.0", "method": "notifications/initialized" }
```

**Constraints during initialization:**
- Client SHOULD NOT send requests other than pings before server responds to `initialize`
- Server SHOULD NOT send requests other than pings and logging before receiving `initialized`

### Phase 2: Operation

Normal protocol communication using negotiated capabilities. Both parties MUST:
- Respect the negotiated protocol version
- Only use capabilities that were successfully negotiated

### Phase 3: Shutdown

No specific shutdown messages defined. Transport mechanism signals termination:

**stdio**: Client closes stdin to server process, waits for exit, sends SIGTERM then SIGKILL if needed. Server MAY initiate by closing stdout and exiting.

**HTTP**: Shutdown indicated by closing associated HTTP connection(s).

## Version Negotiation

[VERIFIED, spec: Lifecycle/Initialization]

1. Client sends `protocolVersion` it supports (SHOULD be latest supported)
2. If server supports that version, it responds with the same version
3. Otherwise, server responds with another version it supports (SHOULD be latest)
4. If client does not support server's version, it SHOULD disconnect

**HTTP requirement**: After negotiation, client MUST include `MCP-Protocol-Version: <version>` header on all subsequent HTTP requests.

**Fallback**: If server receives no `MCP-Protocol-Version` header (no other way to identify version), it SHOULD assume protocol version `2025-03-26`. [VERIFIED, spec: Transports]

## Capability Negotiation

Capabilities determine which optional protocol features are available during a session. [VERIFIED, spec]

### Client Capabilities

- `roots` - Ability to provide filesystem roots
- `sampling` - Support for LLM sampling requests
- `elicitation` - Support for server elicitation requests (form and/or URL mode)
- `tasks` - Support for task-augmented client requests
- `experimental` - Non-standard experimental features

### Server Capabilities

- `prompts` - Offers prompt templates
- `resources` - Provides readable resources
- `tools` - Exposes callable tools
- `logging` - Emits structured log messages
- `completions` - Supports argument autocompletion
- `tasks` - Support for task-augmented server requests
- `experimental` - Non-standard experimental features

### Sub-capabilities

- `listChanged`: Support for list change notifications (prompts, resources, tools)
- `subscribe`: Support for subscribing to individual items' changes (resources only)

## Timeouts

[VERIFIED, spec]
- Implementations SHOULD establish timeouts for all sent requests
- When timeout expires without response, sender SHOULD issue cancellation notification and stop waiting
- SDKs SHOULD allow per-request timeout configuration
- Progress notifications MAY reset the timeout clock (implies work is happening)
- Implementations SHOULD always enforce a maximum timeout regardless of progress

## Error Handling

Standard error cases: [VERIFIED, spec]
- Protocol version mismatch
- Failure to negotiate required capabilities
- Request timeouts

Example initialization error:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Unsupported protocol version",
    "data": { "supported": ["2024-11-05"], "requested": "1.0.0" }
  }
}
```

## Limitations and Known Issues

- No built-in heartbeat mechanism beyond `ping` - connection liveness detection depends on transport
- Timeout values are implementation-defined, not standardized - interoperability risk between clients and servers with different timeout assumptions
- Capability negotiation is session-scoped; no mid-session capability renegotiation supported
- Error codes -32002 and -32001 are MCP extensions to JSON-RPC, not part of the base JSON-RPC 2.0 spec

## Sources

- MCP-SC-MCPIO-SPEC2511 (Lifecycle, Overview/Messages)
- MCP-SC-MCPIO-LLMSFULL (positions 203-204, 209-212)

## Document History

**[2026-06-12 09:45]**
- Initial topic file created with lifecycle phases, message format, capability and version negotiation
