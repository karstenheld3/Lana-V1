# ACP: Prompt Turn and Streaming

**Doc ID**: ACP-IN07
**Goal**: Document the prompt turn lifecycle, streaming mechanism, and cancellation
**Version scope**: ACP Protocol v1 (stable) + v2 changes noted

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

The prompt turn is ACP's core interaction loop: the client sends a user message, and the agent processes it while streaming real-time updates. In v1, the `session/prompt` response carries the `stopReason` that ends the turn - nothing else; usage data flows separately via `usage_update` notifications. In v2, the response is merely an acknowledgment; all output flows through `session/update` notifications, and session state is tracked via `state_update`. [VERIFIED] (ACP-SC-ACPORG-PRMPT, ACP-SC-ACPORG-V2MIG)

## v1 Prompt Turn Lifecycle

### 1. Client sends prompt

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_abc123def456",
    "prompt": [
      { "type": "text", "text": "Fix the authentication bug in login.py" },
      { "type": "resource_link", "uri": "file:///home/user/project/login.py", "name": "login.py" }
    ]
  }
}
```

Prompt content blocks: `text` and `resource_link` MUST be accepted by every agent (baseline); `image`, `audio`, and `resource` (embedded context) only when the agent declared the matching `promptCapabilities` flag (ACP-IN05). [VERIFIED] (ACP-SC-ACPORG-INIT)

### 2. Agent streams updates via `session/update` notifications

Text chunks:
```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "agent_message_chunk",
      "messageId": "msg_001",
      "content": { "type": "text", "text": "I'll analyze the login.py file..." }
    }
  }
}
```

### 3. Agent responds with the stop reason

The response carries ONLY `stopReason` - there is no usage field in the prompt response (usage flows via `usage_update` notifications, see Usage Tracking):

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "stopReason": "end_turn"
  }
}
```

[VERIFIED] (ACP-SC-ACPORG-PRMPT, ACP-SC-ACPORG-STRMG)

## Session Update Types (v1)

All streaming happens via `session/update` notifications with different `sessionUpdate` discriminators: [VERIFIED] (ACP-SC-ACPORG-STRMG)

- **`user_message_chunk`**: Echoed user message content (with optional `messageId`)
- **`agent_message_chunk`**: Agent response text (with optional `messageId`)
- **`agent_thought_chunk`**: Agent reasoning/thinking content (with optional `messageId`)
- **`tool_call`**: Tool call announcement
- **`tool_call_update`**: Tool call progress/completion
- **`plan`**: Agent's execution plan (each update replaces the whole plan)
- **`usage_update`**: Context/cost consumption updates (`used`, `size`, `cost`) [VERIFIED] (ACP-SC-ANN-USAGE, ACP-SC-ACPORG-PRMPT)
- **`current_mode_update`**: Active session mode change
- **`config_option_update`**: Session configuration changes
- **`session_info_update`**: Session metadata changes
- **`available_commands_update`**: Available slash commands

### Message IDs

Optional `messageId` fields correlate streamed chunks with their parent message. Stabilized as a v1 feature. [VERIFIED] (ACP-SC-ANN-MSGID)

## Stop Reasons

The `stopReason` field in the prompt response indicates why the agent stopped. The complete v1 enum (explicitly confirmed unchanged by the v2 migration guide): [VERIFIED] (ACP-SC-ACPORG-PRMPT, ACP-SC-ACPORG-V2MIG)

- **`end_turn`**: The language model finishes responding without requesting more tools
- **`max_tokens`**: The maximum token limit is reached
- **`max_turn_requests`**: The maximum number of model requests in a single turn is exceeded
- **`refusal`**: The agent refuses to continue
- **`cancelled`**: The client cancelled the turn via `session/cancel`

There are NO `auth_required` or `paused` stop reasons in v1.

## Cancellation

### Method-specific: `session/cancel`

The client sends `session/cancel` to interrupt an ongoing prompt turn: [VERIFIED] (ACP-SC-ACPORG-PRMPT)

```json
{
  "jsonrpc": "2.0",
  "method": "session/cancel",
  "params": {
    "sessionId": "sess_abc123def456"
  }
}
```

**Gotcha**: `session/cancel` is a notification with no confirmation. The agent may send additional `session/update` notifications after cancellation (but MUST send them before the prompt response). Wait for the `session/prompt` response with `stopReason: "cancelled"`.

Cancellation obligations: [VERIFIED] (ACP-SC-ACPORG-PRMPT)
- The client MUST respond to all pending `session/request_permission` requests with the `cancelled` outcome
- The client SHOULD preemptively mark non-finished tool calls of the turn as `cancelled`
- The agent MUST respond to the original `session/prompt` with the `cancelled` stop reason after aborting operations

### Protocol-level: `$/cancel_request`

General-purpose request cancellation, not limited to prompt turns: [VERIFIED] (ACP-SC-ANN-RQCNL)

```json
{
  "jsonrpc": "2.0",
  "method": "$/cancel_request",
  "params": {
    "id": 3
  }
}
```

Either side can send `$/cancel_request` for any outstanding JSON-RPC request. The receiver may return a valid partial result or the `-32800` Request Cancelled error.

## Usage Tracking

`usage_update` notifications provide real-time context consumption and cost data. Fields are `used`, `size`, and `cost` - NOT a token triple: [VERIFIED] (ACP-SC-ANN-USAGE, ACP-SC-ACPORG-PRMPT)

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
      "cost": { "amount": 0.045, "currency": "USD" }
    }
  }
}
```

- **`used`**: Tokens consumed in the context window (minimum 0)
- **`size`**: Context window size in tokens (minimum 0)
- **`cost`**: `{amount, currency}` - accumulated cost (currency e.g. `"USD"`)

## v2 Prompt Lifecycle Changes (Draft)

The v2 prompt lifecycle is fundamentally redesigned: [VERIFIED] (ACP-SC-ACPORG-V2MIG)

### v1: Response is the turn
In v1, `session/prompt` stays pending for the entire turn; the eventual response carries the `stopReason` that ends the turn. The response marks the end of the turn.

### v2: Response is an acknowledgment
In v2, `session/prompt` response is `{}` (empty). All output and turn completion flow through `session/update`:

- **`state_update`** with `state: "running"`: Agent is processing
- **`state_update`** with `state: "idle"` + `stopReason`: Agent finished (replaces stopReason in prompt response)
- **`state_update`** with `state: "requires_action"`: Agent needs user input (e.g., permission)

This decouples output from the request-response cycle, enabling queueing, multi-client observation, and background work.

### v2 session/update changes
- `messageId` becomes required (was optional in v1)
- New whole-message upserts: `user_message`, `agent_message`, `agent_thought`
- `tool_call` removed; first `tool_call_update` for a `toolCallId` creates the tool call
- New `tool_call_content_chunk` for streaming tool call content
- `plan` replaced by `plan_update` with `planId` and `type` discriminator
- `current_mode_update` removed (use `config_option_update`)
- New `terminal_update` and `terminal_output_chunk` for agent-owned terminals

## Quick Reference

- **Send prompt**: `session/prompt` (client to agent, request)
- **Stream output**: `session/update` (agent to client, notification)
- **Cancel turn**: `session/cancel` (client to agent, notification)
- **Cancel request**: `$/cancel_request` (either direction, notification)
- **Stop reasons**: end_turn, max_tokens, max_turn_requests, refusal, cancelled
- **v2 states**: running, idle, requires_action

## Limitations and Gotchas

- `session/cancel` has no confirmation; additional updates may arrive after cancellation
- `usage_update` may be sent multiple times during a turn; use the latest values
- `messageId` is optional in v1 but required in v2 - implement it now for forward compatibility
- v2 changes the fundamental response semantics; implementations must handle both if supporting dual versions

## Sources

- ACP-SC-ACPORG-PRMPT - Prompt turn lifecycle
- ACP-SC-ACPORG-STRMG - Streaming mechanism
- ACP-SC-ANN-RQCNL - $/cancel_request stabilization
- ACP-SC-ANN-MSGID - Message ID stabilization
- ACP-SC-ANN-USAGE - usage_update stabilization
- ACP-SC-ACPORG-V2MIG - v2 prompt lifecycle redesign

## Document History

**[2026-08-30 14:20]**
- Fixed: prompt response carries `stopReason` ONLY (usage field in the response was hallucinated) - verified against https://agentclientprotocol.com/protocol/v1/prompt-turn
- Fixed: `usage_update` shape is `used`/`size`/`cost` (token triple was hallucinated)
- Fixed: StopReason enum is end_turn/max_tokens/max_turn_requests/refusal/cancelled (`auth_required` and `paused` do not exist)
- Added: `current_mode_update` to the session update list (was missing); prompt content block baseline (text + resource_link mandatory); cancellation obligations

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: $/cancel_request protocol-level cancellation
- Added: usage_update notifications
- Added: Message IDs (messageId) as stabilized feature
- Added: v2 prompt lifecycle redesign (state_update, acknowledgment-only response)
- Added: v2 session/update variant changes

**[2026-06-12 09:35]**
- Initial document created
