# ACP: Prompt Turn and Streaming

**Doc ID**: ACP-IN07
**Goal**: Document the core conversation flow and real-time streaming mechanism
**Version scope**: ACP Protocol v1 (as of 2026-06-12)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

The prompt turn is ACP's core interaction loop: the client sends a user message, the agent processes it (streaming progress in real time), optionally invokes tools, and eventually returns a response with a stop reason. This cycle repeats for each user interaction within a session. Streaming happens via JSON-RPC notifications, allowing the editor to update its UI in real time without waiting for a complete response. [VERIFIED] (ACP-SC-ACPORG-PRMPT, ACP-SC-MRPH-EXPL)

## The 6-Step Prompt Turn Lifecycle

### Step 1: User Message

The client sends `session/prompt` with the user's message as an array of content blocks. `session/prompt` is a baseline client method - every ACP client must support it. [VERIFIED] (ACP-SC-ACPORG-PRMPT, ACP-SC-ACPORG-OVRVW)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_abc123def456",
    "prompt": [
      {
        "type": "text",
        "text": "Can you analyze this code for potential issues?"
      },
      {
        "type": "resource",
        "resource": {
          "uri": "file:///home/user/project/main.py",
          "mimeType": "text/x-python",
          "text": "def process_data(items):\n    for item in items:\n        print(item)"
        }
      }
    ]
  }
}
```

The `sessionId` links the prompt to a specific session. Content types include text, image, audio, embedded resource, and resource link - the latter two reuse Model Context Protocol (MCP) content types. Which types the agent accepts depends on its prompt capabilities declared during initialization. [VERIFIED] (ACP-SC-ACPORG-CNTNT, ACP-SC-ACPORG-PRMPT)

### Step 2: Agent Processing

The agent receives the prompt and begins its inference loop. During processing, it can stream progress back to the client.

### Step 3: Agent Reports Output

The agent sends `session/update` notifications to stream its response. Several update types are available: [VERIFIED] (ACP-SC-ACPORG-PRMPT)

**Agent Message Chunks** (text streaming):
```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "agent_message_chunk",
      "messageId": "msg_agent_c42b9",
      "content": {
        "type": "text",
        "text": "I'll analyze your code for potential issues..."
      }
    }
  }
}
```

**Plan Updates** (execution plan):
```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "plan",
      "entries": [
        { "content": "Check for syntax errors", "priority": "high", "status": "pending" },
        { "content": "Identify potential type issues", "priority": "medium", "status": "pending" },
        { "content": "Review error handling patterns", "priority": "medium", "status": "pending" },
        { "content": "Suggest improvements", "priority": "low", "status": "pending" }
      ]
    }
  }
}
```

**Tool Call Announcements** (see `_INFO_ACP-08_ToolCallsAndPermissions.md [ACP-IN08]`):
```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "tool_call",
      "toolCallId": "call_001",
      "title": "Analyzing Python code",
      "kind": "other",
      "status": "pending"
    }
  }
}
```

### Message IDs

Message chunks include a `messageId` field to correlate multiple chunks belonging to the same logical message. Clients use this to append chunks to the correct message in the UI. [VERIFIED] (ACP-SC-ACPORG-PRMPT)

### Session Usage Updates

Agents can report token usage and cost information during the turn: [VERIFIED] (ACP-SC-ACPORG-PRMPT)

```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "usage_update",
      "used": 53000,
      "size": 200000,
      "cost": {
        "amount": 0.045,
        "currency": "USD"
      }
    }
  }
}
```

Fields: `used` (tokens consumed), `size` (context window size), `cost.amount` + `cost.currency` (monetary cost, currency defaults to `"USD"`).

### Step 4: Check for Completion

The turn ends when the agent sends the `session/prompt` response with a `StopReason`: [VERIFIED] (ACP-SC-ACPORG-PRMPT)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "stopReason": "end_turn"
  }
}
```

### Step 5: Tool Invocation and Status Reporting

During processing, the agent may invoke tools. It requests permission via `session/request_permission`, then reports progress via `tool_call_update` notifications. See `_INFO_ACP-08_ToolCallsAndPermissions.md [ACP-IN08]` for full details.

### Step 6: Continue Conversation

After the turn completes, the client can send another `session/prompt` to continue the conversation. The agent retains context from previous turns within the session.

## Stop Reasons

The `StopReason` in the `session/prompt` response indicates why the turn ended: [VERIFIED] (ACP-SC-ACPORG-PRMPT)

- `end_turn`: Agent completed its response normally
- `cancelled`: Turn was cancelled by the client via `session/cancel`
- `auth_required`: Agent needs authentication before continuing
- `max_turns`: Agent reached its configured maximum turn limit
- `error`: An error occurred during processing

## Cancellation

The client can interrupt a running turn by sending `session/cancel`: [VERIFIED] (ACP-SC-ACPORG-PRMPT)

```json
{
  "jsonrpc": "2.0",
  "method": "session/cancel",
  "params": {
    "sessionId": "sess_abc123def456"
  }
}
```

Important behavior:
- `session/cancel` is a **notification** (no `id`, no response)
- After cancellation, any pending `session/request_permission` receives `outcome: "cancelled"`
- The `session/prompt` response will have `stopReason: "cancelled"`
- The agent may still send `session/update` notifications between `session/cancel` and the `session/prompt` response
- `session/cancel` is idempotent: sending it when no prompt is active has no effect

## Quick Reference

- **Send prompt**: `session/prompt` (client to agent, request)
- **Stream response**: `session/update` (agent to client, notification)
- **Cancel**: `session/cancel` (client to agent, notification)
- **Update types**: `agent_message_chunk`, `plan`, `tool_call`, `tool_call_update`, `usage_update`
- **Completion**: `session/prompt` response with `stopReason`

## Use Cases

### Streaming Code Analysis

1. User asks "review this file for bugs"
2. Agent streams thinking text via `agent_message_chunk`
3. Agent sends `plan` update with analysis steps
4. Agent reads file, streams findings one by one
5. Agent sends `end_turn` stop reason

### Long-Running Task with Cancellation

1. User asks "refactor the entire codebase"
2. Agent begins processing, streams progress
3. User realizes the scope is too large, clicks cancel
4. Client sends `session/cancel`
5. Agent stops processing, sends `session/prompt` response with `cancelled`

## Limitations and Gotchas

- `session/cancel` has no confirmation mechanism - the client must watch for `stopReason: "cancelled"` to verify it took effect
- Multiple `session/update` notifications may arrive after `session/cancel` (race condition by design)
- The `usage_update` mechanism only tracks the current turn, not cumulative session usage
- Plan updates replace the entire plan; there is no incremental plan update in v1 (v2 proposes `plan_update` with item-based updates) [VERIFIED] (ACP-SC-ACPORG-V2)
- v2 will require `messageId` on all streamed chunks and introduce whole-message upserts (`user_message`, `agent_message`, `agent_thought`) keyed by `messageId` [VERIFIED] (ACP-SC-ACPORG-V2)
- Message IDs are agent-assigned; clients should not assume a particular format

## Sources

- ACP-SC-ACPORG-PRMPT - Official prompt turn lifecycle page
- ACP-SC-ACPORG-OVRVW - Protocol v1 overview (session/prompt as baseline method)
- ACP-SC-ACPORG-CNTNT - Content block types used in prompt messages
- ACP-SC-ACPORG-V2 - v2 proposal (plan_update, required messageId, whole-message upserts)
- ACP-SC-MRPH-EXPL - Five core message types, streaming description

## Document History

**[2026-06-12 09:30]**
- [IMPROVED] Added 3 source citations (ACP-SC-ACPORG-OVRVW, ACP-SC-ACPORG-CNTNT, ACP-SC-ACPORG-V2)
- Added: Content block type details with MCP type reuse reference
- Added: v2 messageId and whole-message upsert changes to Limitations
- Added: Baseline method clarification for session/prompt

**[2026-06-12 10:00]**
- Initial document created
