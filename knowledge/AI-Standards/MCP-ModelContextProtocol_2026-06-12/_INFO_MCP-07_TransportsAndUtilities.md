# MCP: Transports and Utilities

**Doc ID**: MCP-IN07
**Goal**: Document transport mechanisms and protocol utilities
**Version scope**: Spec 2025-11-25 (current)

**Depends on:**
- `_INFO_MCP-04_ProtocolLifecycle.md [MCP-IN04]` for lifecycle context
- `_INFO_MCP-02_Sources.md [MCP-IN02]` for source references

## Summary

MCP defines two standard transports: stdio (subprocess communication via stdin/stdout for local servers) and Streamable HTTP (HTTP POST for requests, optional Server-Sent Events for streaming, for remote servers). Custom transports are permitted if they preserve JSON-RPC framing. Protocol utilities include cancellation, progress tracking, ping for liveness, structured logging, cursor-based pagination, and experimental Tasks for durable request tracking. Origin header validation is required for HTTP transport to prevent DNS rebinding attacks.

## Transports

MCP uses JSON-RPC to encode messages. Messages MUST be UTF-8 encoded. [VERIFIED, spec]

Two standard transports. Clients SHOULD support stdio whenever possible.

### stdio Transport

Client launches MCP server as a subprocess. [VERIFIED, spec]

**Message flow**: Client writes to server's stdin, server writes to stdout. Messages delimited by newlines, MUST NOT contain embedded newlines.

**Rules**:
- Server MUST NOT write anything to stdout that is not a valid MCP message
- Client MUST NOT write anything to server's stdin that is not a valid MCP message
- Server MAY write UTF-8 strings to stderr for logging (informational, debug, error)
- Client MAY capture, forward, or ignore stderr output
- Client SHOULD NOT assume stderr output indicates error conditions

**Shutdown**: Client closes stdin, waits for server exit, sends SIGTERM then SIGKILL if needed.

**Use case**: Local subprocess servers with single client. Optimal performance, no network overhead.

### Streamable HTTP Transport

Replaces HTTP+SSE transport from protocol version 2024-11-05. [VERIFIED, spec]

Server operates as independent process handling multiple client connections. Uses HTTP POST and GET with optional Server-Sent Events (SSE).

**MCP endpoint**: Server provides a single HTTP endpoint path supporting both POST and GET (e.g., `https://example.com/mcp`).

#### Security Requirements

1. Servers MUST validate `Origin` header on all incoming connections (DNS rebinding prevention)
   - Invalid `Origin` -> HTTP 403 Forbidden
2. Local servers SHOULD bind only to localhost (127.0.0.1), not 0.0.0.0
3. Servers SHOULD implement proper authentication for all connections

#### Sending Messages (Client to Server)

Every JSON-RPC message from client is a new HTTP POST to the MCP endpoint.
- Client MUST include `Accept` header listing both `application/json` and `text/event-stream`
- POST body MUST be a single JSON-RPC request, notification, or response
- For notifications/responses: server returns 202 Accepted (no body)
- For requests: server returns either `Content-Type: application/json` (single response) or `Content-Type: text/event-stream` (SSE stream)

**SSE stream behavior**:
- Server SHOULD immediately send SSE event with event ID and empty data (priming for reconnection)
- Server MAY close connection at any time (client polls by reconnecting with Last-Event-ID)
- Server SHOULD send `retry` field before closing (client MUST respect it)
- Stream SHOULD eventually include the JSON-RPC response for the POST request
- Server MAY send requests and notifications before the response
- Disconnection SHOULD NOT be interpreted as cancellation (use CancelledNotification explicitly)

#### Listening for Messages (Server to Client)

Client MAY issue HTTP GET to MCP endpoint to open SSE stream for server-initiated communication.
- Server responds with `text/event-stream` or 405 Method Not Allowed
- Server MAY send requests and notifications on the stream
- Server MUST NOT send response on GET stream unless resuming a previous stream

#### Session Management

[VERIFIED, spec]
- Server MAY assign session ID via `MCP-Session-Id` header on initialize response
- Session ID MUST be globally unique and cryptographically secure (UUID, JWT, hash)
- Client MUST include `MCP-Session-Id` on all subsequent requests
- Server MAY terminate session at any time (responds 404 to subsequent requests)
- Client receiving 404 MUST start new session with fresh InitializeRequest
- Client SHOULD send HTTP DELETE to terminate session when no longer needed

#### Resumability

- Servers MAY attach `id` field to SSE events (globally unique within session)
- Event IDs SHOULD encode stream identity for correlation
- Client reconnects via GET with `Last-Event-ID` header
- Server replays messages for that specific stream only (MUST NOT cross-stream replay)
- Resumption always via GET regardless of original stream origin (POST or GET)

#### Protocol Version Header

Client MUST include `MCP-Protocol-Version: <version>` on all HTTP requests after initialization.
Fallback if header absent: server SHOULD assume `2025-03-26`.

#### Backwards Compatibility with HTTP+SSE (2024-11-05)

**Servers** supporting older clients: host both old SSE/POST endpoints alongside new MCP endpoint.

**Clients** supporting older servers:
1. POST InitializeRequest to server URL
2. If success -> new Streamable HTTP transport
3. If 400/404/405 -> GET to server URL expecting SSE stream with `endpoint` event -> old HTTP+SSE transport

### Custom Transports

Clients and servers MAY implement custom transports in a pluggable fashion. [VERIFIED, spec]

## Protocol Utilities

### Cancellation

[VERIFIED, spec] Optional cancellation of in-progress requests via `notifications/cancelled`.

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/cancelled",
  "params": { "requestId": "123", "reason": "User requested cancellation" }
}
```

**Rules**:
- MUST only reference previously issued, in-progress requests
- `initialize` request MUST NOT be cancelled
- For task-augmented requests, use `tasks/cancel` instead
- Receivers SHOULD stop processing and free resources
- Invalid cancellations SHOULD be silently ignored (fire-and-forget)

### Progress Tracking

[VERIFIED, spec] Optional progress notifications for long-running operations.

Request includes `progressToken` in `_meta`:
```json
{ "params": { "_meta": { "progressToken": "abc123" } } }
```

Progress notification:
```json
{
  "method": "notifications/progress",
  "params": { "progressToken": "abc123", "progress": 50, "total": 100, "message": "Processing..." }
}
```

- `progress` value MUST increase with each notification
- `total` MAY be omitted if unknown
- Progress and total MAY be floating point

### Ping

Connectivity check. Either side can send `ping` request, other side MUST respond.

### Logging

Server emits structured log messages to client via `notifications/message`. Client can set log level with `logging/setLevel`. Levels: debug, info, notice, warning, error, critical, alert, emergency.

### Pagination

Operations supporting pagination: `tools/list`, `resources/list`, `prompts/list`, `resources/templates/list`, `tasks/list`.
- Response includes optional `nextCursor` string
- Client sends `cursor` in next request to get next page

### Tasks (Experimental)

[VERIFIED, spec: 2025-11-25 addition] Durable execution wrappers for deferred result retrieval and status tracking.

**Participants**: Requestor (sender) and Receiver (executor). Either client or server can be either role.

**Task statuses**: `running`, `input_required`, `completed`, `failed`, `cancelled`

**Protocol messages**:
- Task creation: requestor includes `_meta.task` in request
- `tasks/get`: retrieve task status
- `tasks/result`: retrieve task result
- `tasks/list`: list all tasks
- `tasks/cancel`: cancel a task
- `notifications/tasks/status`: server notifies of task status changes

**Key design decisions**:
- Requestor-driven: requestors control polling and orchestration
- TTL-based lifecycle: tasks have time-to-live for resource management
- Progress token persists through task lifetime

## Limitations and Known Issues

- stdio transport cannot traverse network boundaries - requires the server to run as a local subprocess
- Streamable HTTP requires Server-Sent Events (SSE) support from HTTP infrastructure (some proxies and load balancers strip SSE)
- Tasks are experimental (2025-11-25) and may change or be removed in future spec versions
- No built-in message encryption at transport level - relies on TLS for confidentiality
- SSE stream resumability depends on server maintaining event history keyed by `Last-Event-ID` - no guaranteed retention period

## Sources

- MCP-SC-MCPIO-SPEC2511 (Transports, Cancellation, Progress, Tasks)
- MCP-SC-MCPIO-LLMSFULL (positions 213-218, 219-224, 225-239)

## Document History

**[2026-06-12 09:50]**
- Initial topic file with transports (stdio, Streamable HTTP, backwards compat) and utilities (cancellation, progress, ping, logging, pagination, tasks)
