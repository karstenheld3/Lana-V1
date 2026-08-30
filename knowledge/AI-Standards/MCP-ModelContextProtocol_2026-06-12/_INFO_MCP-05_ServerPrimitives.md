# MCP: Server Primitives - Tools, Resources, Prompts

**Doc ID**: MCP-IN05
**Goal**: Document the three server-exposed primitives with schemas, protocol messages, and usage patterns
**Version scope**: Spec 2025-11-25 (current)

**Depends on:**
- `_INFO_MCP-03_ProblemAndArchitecture.md [MCP-IN03]` for architecture context
- `_INFO_MCP-02_Sources.md [MCP-IN02]` for source references

## Summary

MCP servers expose three primitives with distinct control models: tools (model-controlled functions for actions), resources (application-controlled contextual data), and prompts (user-controlled interactive templates). Tools use JSON Schema 2020-12 for input validation and support annotations for behavior hints (read-only, destructive, idempotent). Resources are URI-identified and support subscriptions for change notifications. Prompts accept arguments and return structured message sequences for multi-step workflows.

## Control Hierarchy

[VERIFIED, spec] Each primitive has a different control model:

- **Prompts** - User-controlled. Interactive templates invoked by user choice. Example: slash commands, menu options.
- **Resources** - Application-controlled. Contextual data attached and managed by the client. Example: file contents, git history.
- **Tools** - Model-controlled. Functions exposed to the LLM to take actions. Example: API POST requests, file writing.

## Tools

Tools enable models to interact with external systems (databases, APIs, computations). Each tool is uniquely identified by a name. [VERIFIED, spec]

### Tool Definition

```json
{
  "name": "get_weather",
  "title": "Weather Information Provider",
  "description": "Get current weather information for a location",
  "inputSchema": {
    "type": "object",
    "properties": {
      "location": { "type": "string", "description": "City name or zip code" }
    },
    "required": ["location"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "temperature": { "type": "number" },
      "conditions": { "type": "string" }
    },
    "required": ["temperature", "conditions"]
  },
  "annotations": {},
  "execution": { "taskSupport": "optional" }
}
```

**Fields**:
- `name`: Unique identifier (1-128 chars, case-sensitive, A-Z/a-z/0-9/_/-/. only)
- `title`: Optional human-readable display name
- `description`: Human-readable functionality description
- `inputSchema`: JSON Schema 2020-12 (default) defining parameters. MUST be valid JSON Schema object.
- `outputSchema`: Optional JSON Schema for structured output validation
- `annotations`: Optional behavior hints (UNTRUSTED unless from trusted server)
- `execution.taskSupport`: `"forbidden"` (default), `"optional"`, or `"required"`

**No-parameter tools**: Use `{ "type": "object", "additionalProperties": false }`

### Protocol Messages

**Discovery**: `tools/list` (supports pagination via cursor)
**Invocation**: `tools/call` with `name` and `arguments`
**Notification**: `notifications/tools/list_changed` (when tool list changes)

### Tool Results

Two result types:

**Unstructured** (in `content` field): Array of content items:
- `text`: Plain text (`{ "type": "text", "text": "..." }`)
- `image`: Base64-encoded (`{ "type": "image", "data": "...", "mimeType": "image/png" }`)
- `audio`: Base64-encoded (`{ "type": "audio", "data": "...", "mimeType": "audio/wav" }`)
- `resource_link`: URI to fetchable resource
- `resource`: Embedded resource with inline content

**Structured** (in `structuredContent` field): JSON object matching `outputSchema`. For backwards compatibility, also include serialized JSON in a TextContent block.

### Error Handling

Two error mechanisms: [VERIFIED, spec]
- **Protocol Errors**: JSON-RPC errors (unknown tool, malformed request). Code `-32602`.
- **Tool Execution Errors**: In result with `isError: true`. Input validation, API failures, business logic. Actionable for LLM self-correction.

Input validation errors SHOULD be Tool Execution Errors (not Protocol Errors) to enable model self-correction. [SEP-1303]

### Security

Servers MUST: validate inputs, implement access controls, rate limit invocations, sanitize outputs.
Clients SHOULD: prompt for user confirmation, show inputs before calling, validate results, implement timeouts, log for audit.

## Resources

Resources provide context data to language models (files, database schemas, application info). Each resource identified by a URI (RFC 3986). [VERIFIED, spec]

### Resource Definition

```json
{
  "uri": "file:///project/src/main.rs",
  "name": "main.rs",
  "title": "Rust Application Main File",
  "description": "Primary application entry point",
  "mimeType": "text/x-rust",
  "size": 1024
}
```

### Resource Contents

**Text**: `{ "uri": "...", "mimeType": "text/plain", "text": "content" }`
**Binary**: `{ "uri": "...", "mimeType": "image/png", "blob": "base64-data" }`

### Annotations

Resources, templates, and content blocks support annotations:
- `audience`: Array of `"user"` and/or `"assistant"`
- `priority`: 0.0 (least important) to 1.0 (most important/required)
- `lastModified`: ISO 8601 timestamp

### Protocol Messages

- `resources/list`: Discover available resources (paginated)
- `resources/read`: Retrieve resource contents by URI
- `resources/templates/list`: List parameterized resource templates (RFC 6570 URI templates)
- `resources/subscribe` / `resources/unsubscribe`: Subscribe to individual resource changes
- `notifications/resources/list_changed`: List of resources changed
- `notifications/resources/updated`: Specific resource updated

### Common URI Schemes

- `https://` - Web resources
- `file://` - Local filesystem resources
- `git://` - Git repository resources
- Custom schemes allowed

## Prompts

Prompts provide structured message templates for interacting with language models. Clients discover and retrieve prompts with arguments. [VERIFIED, spec]

### Prompt Definition

```json
{
  "name": "code_review",
  "title": "Request Code Review",
  "description": "Asks the LLM to analyze code quality",
  "arguments": [
    { "name": "code", "description": "The code to review", "required": true }
  ]
}
```

### PromptMessage

Messages contain `role` ("user" or "assistant") and `content` (text, image, audio, or embedded resource).

```json
{
  "role": "user",
  "content": { "type": "text", "text": "Please review this code: ..." }
}
```

Content types: text, image (base64), audio (base64), embedded resource (URI + inline data).

### Protocol Messages

- `prompts/list`: Discover available prompts (paginated)
- `prompts/get`: Retrieve specific prompt with arguments (arguments auto-completable via completion API)
- `notifications/prompts/list_changed`: Prompt list changed

## Discovery Pattern

All three primitives follow the same discovery pattern: [VERIFIED, spec]
1. Client calls `*/list` to discover available items
2. Client uses specific methods (`tools/call`, `resources/read`, `prompts/get`)
3. Server sends `notifications/*/list_changed` when available items change
4. Listings are dynamic and paginated

## Limitations and Known Issues

- Tool annotations (readOnlyHint, destructiveHint) are advisory only - no enforcement mechanism at protocol level
- Resource subscriptions lack delivery guarantees - missed notifications possible if connection drops
- Prompt arguments have no validation schema - servers must validate manually
- Tool names are case-sensitive with restricted charset, but no namespacing mechanism to prevent collisions across servers

## Sources

- MCP-SC-MCPIO-SPEC2511 (Tools, Resources, Prompts sections)
- MCP-SC-MCPIO-LLMSFULL (positions 352-373)

## Document History

**[2026-06-12 09:55]**
- Initial topic file with tools, resources, prompts including schemas, protocol messages, error handling
