# ACP: Tool Calls and Permissions

**Doc ID**: ACP-IN08
**Goal**: Document tool call lifecycle and the permission model
**Version scope**: ACP Protocol v1 (as of 2026-06-12)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP's tool call system provides structured reporting of agent actions with a human-in-the-loop permission model. Agents cannot execute arbitrary commands; they must announce tool calls, optionally request permission, and report status through a defined lifecycle. The permission system gives users four choices per tool invocation, balancing control with workflow efficiency. [VERIFIED] (ACP-SC-ACPORG-TLCLL, ACP-SC-MRPH-EXPL)

## Tool Call Lifecycle

### Creating a Tool Call

Agents announce tool calls via `session/update` with `sessionUpdate: "tool_call"`: [VERIFIED] (ACP-SC-ACPORG-TLCLL)

```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "tool_call",
      "toolCallId": "call_001",
      "title": "Reading configuration file",
      "kind": "read",
      "status": "pending"
    }
  }
}
```

Fields:
- `toolCallId`: Unique identifier for this tool call
- `title`: Human-readable description
- `kind`: Category of operation (see Tool Kinds)
- `status`: Initial status (always `pending`)

### Tool Kinds

Nine predefined kinds categorize tool operations: [VERIFIED] (ACP-SC-ACPORG-TLCLL)

- `read` - Reading files or data
- `edit` - Modifying files or content
- `delete` - Removing files or data
- `move` - Moving or renaming files
- `search` - Searching for information
- `execute` - Running commands or code
- `think` - Internal reasoning or planning
- `fetch` - Retrieving external data
- `other` - Other tool types (default)

### Updating a Tool Call

Progress updates use `tool_call_update`: [VERIFIED] (ACP-SC-ACPORG-TLCLL)

```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "tool_call_update",
      "toolCallId": "call_001",
      "status": "in_progress",
      "content": [
        {
          "type": "content",
          "content": {
            "type": "text",
            "text": "Found 3 configuration files..."
          }
        }
      ]
    }
  }
}
```

### Tool Call Status Progression

- `pending` - Tool call announced, not yet started
- `in_progress` - Tool call is executing
- `completed` - Tool call finished successfully
- `failed` - Tool call encountered an error

## Permission Model

### Requesting Permission

Before executing sensitive operations, agents send `session/request_permission`: [VERIFIED] (ACP-SC-ACPORG-TLCLL)

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "session/request_permission",
  "params": {
    "sessionId": "sess_abc123def456",
    "toolCall": {
      "toolCallId": "call_001"
    },
    "options": [
      { "optionId": "allow-once", "name": "Allow once", "kind": "allow_once" },
      { "optionId": "reject-once", "name": "Reject", "kind": "reject_once" }
    ]
  }
}
```

### Permission Options

Four permission kinds are defined: [VERIFIED] (ACP-SC-ACPORG-TLCLL)

- `allow_once` - Allow this operation only this time
- `allow_always` - Allow this operation and remember the choice
- `reject_once` - Reject this operation only this time
- `reject_always` - Reject this operation and remember the choice

### Permission Response

The client responds with the user's choice:

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "outcome": {
      "outcome": "selected",
      "optionId": "allow-once"
    }
  }
}
```

If the prompt turn was cancelled while a permission request is pending, the client responds with `outcome: "cancelled"`:

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "outcome": {
      "outcome": "cancelled"
    }
  }
}
```

## Tool Call Content Types

Tool calls can produce three types of content. Regular content reuses the standard ACP content block types (text, image, etc.) defined in the protocol's content specification. [VERIFIED] (ACP-SC-ACPORG-TLCLL, ACP-SC-ACPORG-CNTNT)

### Regular Content

Standard content blocks (text, images, etc.):
```json
{
  "type": "content",
  "content": {
    "type": "text",
    "text": "Analysis complete. Found 3 issues."
  }
}
```

### Diffs

File modification diffs with old and new text:
```json
{
  "type": "diff",
  "path": "/home/user/project/src/config.json",
  "oldText": "{\n  \"debug\": false\n}",
  "newText": "{\n  \"debug\": true\n}"
}
```

Fields: `path` (absolute file path), `oldText`, `newText`.

### Terminal References

References to terminal sessions created via `terminal/create`:
```json
{
  "type": "terminal",
  "terminalId": "term_xyz789"
}
```

## Quick Reference

- **Announce**: `session/update` with `sessionUpdate: "tool_call"`
- **Update**: `session/update` with `sessionUpdate: "tool_call_update"`
- **Permission**: `session/request_permission` (agent to client, request)
- **Kinds**: read, edit, delete, move, search, execute, think, fetch, other
- **Statuses**: pending, in_progress, completed, failed
- **Permission kinds**: allow_once, allow_always, reject_once, reject_always

## Use Cases

### File Edit with Permission

1. Agent announces tool call (kind: "edit", status: "pending")
2. Agent requests permission with allow_once and reject_once options
3. User clicks "Allow once" in editor UI
4. Editor responds with selected optionId
5. Agent reads file, modifies it, writes back
6. Agent sends tool_call_update with status: "completed" and diff content
7. Editor renders the diff inline

### Autonomous Execution with Always-Allow

1. User previously selected "Allow always" for read operations
2. Agent announces read tool call
3. Agent skips permission request (or editor auto-approves)
4. Agent reads file and reports results
5. No user interruption needed

## Limitations and Gotchas

- `session/request_permission` is the ONLY baseline client method - everything else (fs, terminal) is optional [VERIFIED] (ACP-SC-ACPORG-OVRVW)
- The agent decides which options to present in permission requests; not all four kinds must be offered
- There is no standard mechanism for revoking `allow_always` or `reject_always` choices within a session
- v2 proposes replacing the split between `tool_call` and `tool_call_update` with a single upsert shape keyed by `toolCallId` [VERIFIED] (ACP-SC-ACPORG-V2)
- v2 introduces tool-call content chunks that stream individual `ToolCallContent` items appending to a tool call [VERIFIED] (ACP-SC-ACPORG-V2)
- Diffs use raw `oldText`/`newText` strings; v2 proposes expanding diff types to include delete and move operations [VERIFIED] (ACP-SC-ACPORG-V2)
- The `kind` field is informational for UI categorization; it does not enforce any security policy

## Sources

- ACP-SC-ACPORG-TLCLL - Official tool calls page
- ACP-SC-ACPORG-OVRVW - Protocol v1 overview (request_permission as baseline client method)
- ACP-SC-ACPORG-CNTNT - Content block types reused in tool call content
- ACP-SC-ACPORG-V2 - v2 proposal (unified tool_call upsert, content chunks, expanded diffs)
- ACP-SC-MRPH-EXPL - Permission model description and five core message types

## Document History

**[2026-06-12 09:30]**
- [IMPROVED] Added 3 source citations (ACP-SC-ACPORG-OVRVW, ACP-SC-ACPORG-CNTNT, ACP-SC-ACPORG-V2)
- Added: Content block type reuse reference for tool call content
- Added: v2 tool-call content chunks to Limitations
- Added: Baseline method verification for request_permission

**[2026-06-12 10:03]**
- Initial document created
