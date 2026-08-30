# MCP: Client Features - Sampling, Roots, Elicitation

**Doc ID**: MCP-IN06
**Goal**: Document client-exposed features that servers can request
**Version scope**: Spec 2025-11-25 (current)

**Depends on:**
- `_INFO_MCP-05_ServerPrimitives.md [MCP-IN05]` for server-side context
- `_INFO_MCP-02_Sources.md [MCP-IN02]` for source references

## Summary

Client features enable servers to request actions from the host application. Unlike server primitives (which servers expose), these are capabilities the client declares and the server invokes. [VERIFIED, spec] Three client features exist: sampling (server requests Large Language Model completions through the client), roots (server queries filesystem/URI boundaries), and elicitation (server requests user input via forms or URLs). All three require explicit user approval and are subject to human-in-the-loop controls.

- **Sampling** - Server requests client. LLM completions without server needing API keys.
- **Roots** - Server requests client. Filesystem/URI boundaries for operation scope.
- **Elicitation** - Server requests client. User input via forms or URLs.

## Sampling

Allows servers to request LLM completions ("generations") from the host's language model. Servers leverage AI capabilities without needing their own API keys. Clients maintain control over model access, selection, and permissions. [VERIFIED, spec]

### Capability Declaration

```json
{ "capabilities": { "sampling": {} } }
```

With tool use support (added 2025-11-25): [VERIFIED, changelog]
```json
{ "capabilities": { "sampling": { "tools": {} } } }
```

### Protocol: `sampling/createMessage`

**Request** (server to client):
```json
{
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      { "role": "user", "content": { "type": "text", "text": "What is the capital of France?" } }
    ],
    "modelPreferences": {
      "hints": [{ "name": "claude-3-sonnet" }],
      "intelligencePriority": 0.8,
      "speedPriority": 0.5
    },
    "systemPrompt": "You are a helpful assistant.",
    "maxTokens": 100
  }
}
```

**Response** (client to server):
```json
{
  "result": {
    "role": "assistant",
    "content": { "type": "text", "text": "The capital of France is Paris." },
    "model": "claude-3-sonnet-20240307",
    "stopReason": "endTurn"
  }
}
```

### Sampling with Tools (2025-11-25)

Servers can include `tools` array and `toolChoice` in sampling requests. [VERIFIED, spec: SEP-1577]

Flow: Server sends tools + messages -> Client asks LLM -> LLM returns `tool_use` -> Client returns to server -> Server executes tools -> Server sends results back for continuation.

`toolChoice` modes: `auto`, `any`, `tool` (specific tool), `none`.

**Human-in-the-loop**: Applications SHOULD present sampling requests for user review, allow editing prompts, and present responses before delivery.

### Model Preferences

- `hints`: Array of model name hints (e.g., `[{ "name": "claude-3-sonnet" }]`)
- `intelligencePriority`: 0.0-1.0 weight for intelligence
- `speedPriority`: 0.0-1.0 weight for speed
- `costPriority`: 0.0-1.0 weight for cost

Client is free to choose any model - preferences are hints, not mandates. Server deliberately has limited visibility into actual prompt and model used.

### Soft-Deprecated: `includeContext`

Values `"thisServer"` and `"allServers"` are soft-deprecated. Servers SHOULD omit or use `"none"` (default). May be removed in future spec releases.

## Roots

Roots define URI or filesystem boundaries within which the server should operate. [VERIFIED, spec]

### Capability Declaration

```json
{ "capabilities": { "roots": { "listChanged": true } } }
```

### Protocol: `roots/list`

**Request** (server to client):
```json
{ "method": "roots/list" }
```

**Response**:
```json
{
  "result": {
    "roots": [
      { "uri": "file:///home/user/projects/myproject", "name": "My Project" }
    ]
  }
}
```

### Root List Changes

Client sends `notifications/roots/list_changed` when roots change (if `listChanged` capability declared).

### Use Case

Typically exposed through workspace/project configuration. Allows servers to know their operational boundaries (e.g., which directories a filesystem server should access). Can be combined with automatic workspace detection from version control.

## Elicitation

Allows servers to request additional information from users. Added in spec version 2025-06-18. [VERIFIED, spec]

### Capability Declaration

```json
{ "capabilities": { "elicitation": { "form": {}, "url": {} } } }
```

Two modes: `form` (in-band structured data) and `url` (out-of-band URL navigation).

### Form Mode

Server collects structured data through the MCP client using a restricted JSON Schema.

**Protocol**: `elicitation/create` with `mode: "form"` (or omitted for backwards compat).

**Request**:
```json
{
  "method": "elicitation/create",
  "params": {
    "mode": "form",
    "message": "Please provide your GitHub username",
    "requestedSchema": {
      "type": "object",
      "properties": {
        "name": { "type": "string" }
      },
      "required": ["name"]
    }
  }
}
```

**Response**:
```json
{ "result": { "action": "accept", "content": { "name": "octocat" } } }
```

**Supported schema types** (flat objects with primitive properties only):
- `string`: With optional minLength, maxLength, pattern, format (email, uri, date, date-time), default
- `number`/`integer`: With optional minimum, maximum, default
- `boolean`: With optional default
- `enum`: Single-select (type: string + enum array, or oneOf with const/title), multi-select (type: array + items with enum)

Complex nested structures intentionally not supported for simplified client UX.

### URL Mode (2025-11-25)

Server directs user to a URL for out-of-band interaction. Data (other than the URL) is NOT exposed to the client. [VERIFIED, spec: SEP-1036]

Useful for: OAuth flows, sensitive data entry, external service interactions.

### Response Actions

- `accept`: User provided data
- `decline`: User declined the request
- `cancel`: User cancelled the interaction

## Security Considerations

**Sampling**: Users MUST explicitly approve sampling requests. Users control whether sampling occurs, the actual prompt, and what results the server sees. Protocol intentionally limits server visibility into prompts.

**Roots**: Servers MUST respect root boundaries. Hosts enforce access controls.

**Elicitation**: Clients validate schemas, prevent injection. URL mode requires safe URL handling. Identifying the actual user is client's responsibility.

## Limitations and Known Issues

- Sampling gives servers no control over which model the client selects - server preferences are advisory only
- Elicitation URL mode relies on out-of-band browser interaction with no guaranteed completion signal
- Roots are informational only - servers are not required to restrict operations to declared roots
- No client feature for server-to-server delegation (all features route through the host)

## Sources

- MCP-SC-MCPIO-SPEC2511 (Sampling, Roots, Elicitation sections)
- MCP-SC-MCPIO-LLMSFULL (positions 243-272)

## Document History

**[2026-06-12 10:00]**
- Initial topic file with sampling (including tools), roots, and elicitation (form + URL modes)
