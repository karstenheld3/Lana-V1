# ACP: Tool Calls and Permissions

**Doc ID**: ACP-IN08
**Goal**: Document tool call lifecycle and the permission model
**Version scope**: ACP Protocol v1 (stable) + v2 changes noted

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP's tool call system provides structured reporting of agent actions with a human-in-the-loop permission model. Agents announce tool calls, optionally request permission, and report status through a defined lifecycle. The permission system gives users four choices per tool invocation. [VERIFIED] (ACP-SC-ACPORG-TLCLL, ACP-SC-MRPH-EXPL)

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
      "status": "completed",
      "content": [
        {
          "type": "content",
          "content": { "type": "text", "text": "Found 3 configuration files..." }
        }
      ]
    }
  }
}
```

### Status Progression

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
    "toolCall": { "toolCallId": "call_001" },
    "options": [
      { "optionId": "allow-once", "name": "Allow once", "kind": "allow_once" },
      { "optionId": "reject-once", "name": "Reject", "kind": "reject_once" }
    ]
  }
}
```

### Permission Kinds

- `allow_once` - Allow this operation only this time
- `allow_always` - Allow this operation and remember the choice
- `reject_once` - Reject this operation only this time
- `reject_always` - Reject this operation and remember the choice

### Permission Response

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "outcome": { "outcome": "selected", "optionId": "allow-once" }
  }
}
```

If cancelled: `{ "outcome": { "outcome": "cancelled" } }`

## Tool Call Content Types

Tool calls produce three content types: [VERIFIED] (ACP-SC-ACPORG-TLCLL, ACP-SC-ACPORG-CNTNT)

- **Content**: Standard text/image blocks
- **Diffs**: File modifications with `oldText` and `newText` (v1) or structured `changes` (v2)
- **Terminal references**: References to terminal sessions

## v2 Tool Call Changes (Draft)

Key changes in v2: [VERIFIED] (ACP-SC-ACPORG-V2MIG)

### Unified Upsert
The split between `tool_call` (create) and `tool_call_update` (update) is replaced by a single `tool_call_update` upsert. The first `tool_call_update` for a `toolCallId` creates the tool call; subsequent ones update it. Omitted fields stay unchanged, `null` clears, values replace.

### Streaming Tool Call Content
New `tool_call_content_chunk` allows streaming individual content items that append to a tool call, eliminating the need to resend entire content arrays.

### Agent-Owned Terminal Display
New `terminal_update` and `terminal_output_chunk` for agent-owned display terminals, separate from the client terminal surface (which is removed in v2).

### Diff Overhaul
The `oldText`/`newText` diff is replaced by structured file changes:
```json
{
  "type": "diff",
  "changes": [
    { "operation": "modify", "path": "/home/user/project/config.json", "fileType": "text" }
  ],
  "patch": {
    "format": "git_patch",
    "text": "diff --git ..."
  }
}
```

Operations: `add`, `delete`, `modify`, `move`, `copy`. Optional `git_patch` for rendering.

### Permission Restructuring
`session/request_permission` gains required `title`, optional `description`, and extensible `subject` (instead of hard-wired `toolCall`). Subject types include `tool_call` and `command`.

## Quick Reference

- **Announce**: `session/update` with `sessionUpdate: "tool_call"` (v1) or `tool_call_update` upsert (v2)
- **Update**: `session/update` with `sessionUpdate: "tool_call_update"`
- **Permission**: `session/request_permission` (agent to client, request)
- **Kinds**: read, edit, delete, move, search, execute, think, fetch, other
- **Statuses**: pending, in_progress, completed, failed
- **Permission kinds**: allow_once, allow_always, reject_once, reject_always

## Limitations and Gotchas

- `session/request_permission` is the ONLY baseline client method in v1 [VERIFIED] (ACP-SC-ACPORG-OVRVW)
- The `kind` field is informational for UI categorization; it does NOT enforce security policy
- No standard mechanism for revoking `allow_always`/`reject_always` within a session
- v2 replaces split tool_call/tool_call_update with single upsert
- v2 replaces oldText/newText diffs with structured changes + optional git_patch

## Sources

- ACP-SC-ACPORG-TLCLL - Official tool calls page
- ACP-SC-ACPORG-OVRVW - Protocol v1 overview (request_permission as baseline)
- ACP-SC-ACPORG-CNTNT - Content block types
- ACP-SC-ACPORG-V2MIG - v2 tool call changes, diff overhaul, permission restructuring
- ACP-SC-MRPH-EXPL - Permission model description

## Document History

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: v2 tool call changes (unified upsert, content chunks, terminal display)
- Added: v2 diff overhaul (structured changes, git_patch)
- Added: v2 permission restructuring (title, description, subject)

**[2026-06-12 09:30]**
- Initial document created
