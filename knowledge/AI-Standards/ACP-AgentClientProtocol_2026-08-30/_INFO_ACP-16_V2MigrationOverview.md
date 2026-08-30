# ACP: v2 Migration Overview

**Doc ID**: ACP-IN16
**Goal**: Summarize ACP v2 breaking changes and provide migration guidance
**Version scope**: ACP v2 Draft (published July 20, 2026)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP v2 is a consolidation release published in draft form on July 20, 2026. It redesigns the prompt lifecycle, unifies streaming and non-streaming updates, makes the schema forward-compatible by default, and removes protocol surface the ecosystem had already moved away from. v2 is NOT yet stabilized; implementations should gate support behind version negotiation AND feature flags. [VERIFIED] (ACP-SC-ACPORG-V2DFT, ACP-SC-ACPORG-V2MIG)

## Status

- **Published**: July 20, 2026
- **Status**: Draft (not stabilized)
- **Schema**: `schema/v2/schema.json` (stable baseline), `schema/v2/schema.unstable.json` (draft features)
- **SDK support**: TypeScript via `@agentclientprotocol/sdk/experimental/v2`, Python and Rust in progress

## Version Negotiation

Unchanged mechanism: client sends latest supported `protocolVersion`, agent responds with same or its own latest. [VERIFIED] (ACP-SC-ACPORG-V2MIG)

- v2 client to v1 agent: Client sends `2`, agent responds `1`. Client continues with v1 or disconnects.
- Both sides should support v1 AND v2 simultaneously. v1-only peers will remain common.

## Breaking Changes Summary

### Prompt Lifecycle Redesigned

**v1**: `session/prompt` stays pending for the whole turn; the response carries the `stopReason` (only). The response IS the turn. Stop reasons themselves are unchanged in v2 (`end_turn`, `max_tokens`, `max_turn_requests`, `refusal`, `cancelled`) - they move into the idle `state_update`.

**v2**: `session/prompt` response is `{}` (acknowledgment only). All output and state changes flow through `session/update`:

- `state_update` with `state: "running"` - Agent is processing
- `state_update` with `state: "idle"` + `stopReason` - Agent finished
- `state_update` with `state: "requires_action"` - Agent needs user input

This enables queueing, multi-client observation, and background work. [VERIFIED] (ACP-SC-ACPORG-V2MIG)

### Initialization Restructured

- `clientInfo`/`agentInfo` replaced by role-agnostic `info` field (required in both params and result)
- `clientCapabilities`/`agentCapabilities` replaced by single `capabilities` field
- Support markers become objects (`{}`) instead of booleans (`true`)
- `session` capability becomes optional (for non-session agents like NES-only agents)
- `fs` and `terminal` capabilities removed

### Authentication Renamed

- `authenticate` becomes `auth/login`
- `logout` becomes `auth/logout`
- When `authMethods` is non-empty: agent MUST implement both `auth/login` and `auth/logout`
- When `authMethods` is empty/omitted: clients MUST NOT call either method

### Tool Calls Unified

- `tool_call` session update removed
- First `tool_call_update` for a `toolCallId` creates the tool call
- `tool_call_update` is an explicit upsert: omitted fields stay unchanged, `null` clears, values replace
- New `tool_call_content_chunk` streams individual content items appending to a tool call

### Diff Content Overhauled

v1 `oldText`/`newText` replaced by structured diff:

```json
{
  "type": "diff",
  "changes": [
    { "operation": "modify", "path": "/src/config.json", "fileType": "text", "mimeType": "application/json" },
    { "operation": "delete", "path": "/src/old_file.txt", "fileType": "text" },
    { "operation": "add", "path": "/src/new_file.txt", "fileType": "text" }
  ],
  "patch": {
    "format": "git_patch",
    "text": "diff --git ..."
  }
}
```

Operations: `add`, `delete`, `modify`, `move` (has `oldPath`), `copy` (has `oldPath`). `patch` is optional but recommended when feasible.

### Permission Requests Restructured

- Required `title` field (human-readable permission prompt text)
- Optional `description` field
- Extensible `subject` replaces hard-wired `toolCall`:
  - `type: "tool_call"` with `toolCall` payload (same ToolCallUpdate upsert shape)
  - `type: "command"` with `command`, `cwd`, optional `toolCallId`, `terminalId`
  - Unknown subject types should be preserved when proxying

### Plans Restructured

- `plan` replaced by `plan_update` with `planId` and `type` discriminator
- Supports `type: "items"` with entries array
- `planId` enables multiple concurrent plans

### Session Lifecycle Changes

- `session/load` removed; use `session/resume` with optional `replayFrom` cursors
- `session/list`, `session/resume`, `session/close` become baseline (required) when `session` is present
- `session/delete` remains optional via `session.delete` capability
- `mcpServers` becomes optional in `session/new`

### Removals

- Client fs surface: `fs/read_text_file`, `fs/write_text_file` removed
- Client terminal surface: `terminal/create`, `terminal/output`, `terminal/release`, `terminal/wait_for_exit`, `terminal/kill` removed
- Session modes: `session/set_mode`, `current_mode_update` removed (use config options)
- SSE MCP transport removed (HTTP retained)

### Additions

- `terminal_update` and `terminal_output_chunk` for agent-owned display terminals
- Whole-message upserts: `user_message`, `agent_message`, `agent_thought`
- `state_update` foreground notification (running/idle/requires_action)
- Forward-compatible schema (unknown fields preserved, not rejected)
- `messageId` required on all message chunks

## Migration Checklists

### Agent Migration

1. Negotiation: Support both `protocolVersion` 1 and 2
2. Initialization: Use role-agnostic `info` and unified `capabilities`
3. Prompt: Return `{}` from `session/prompt`; emit `state_update` for lifecycle
4. Tool calls: Switch to upsert pattern; stream content via `tool_call_content_chunk`
5. Diffs: Use structured `changes` + optional `git_patch`
6. Auth: Rename methods to `auth/login` and `auth/logout`
7. Sessions: Support `session/resume` with `replayFrom`; make list/resume/close baseline

### Client Migration

1. Negotiation: Send `protocolVersion: 2`; handle v1 fallback
2. Initialization: Send `info` and `capabilities`; drop `fs`/`terminal`
3. Prompt: Handle `session/prompt` returning `{}`; consume `state_update`
4. Tool calls: Handle upsert pattern and `tool_call_content_chunk`
5. Permissions: Handle required `title` and extensible `subject`
6. Diffs: Render structured `changes` and optional `git_patch`

## Quick Reference

- **v2 status**: Draft (not stabilized)
- **Published**: July 20, 2026
- **Key philosophy**: Response is acknowledgment, all output via notifications
- **Biggest changes**: Prompt lifecycle, tool call unification, diff overhaul
- **Biggest removals**: Client fs/terminal, session/load, session modes
- **Recommendation**: Support both v1 and v2 side by side

## Sources

- ACP-SC-ACPORG-V2DFT - v2 draft announcement (July 20, 2026)
- ACP-SC-ACPORG-V2MIG - Complete v1 to v2 migration guide
- ACP-SC-ACPORG-V2OVW - v2 protocol documentation
- ACP-SC-ACPORG-V2 - v2 RFD collection and tracking
- ACP-SC-DPWK-V2 - DeepWiki v2 protocol analysis

## Document History

**[2026-08-30 14:20]**
- Fixed: v1 prompt response carries `stopReason` only (usage claim was hallucinated); added unchanged StopReason enum note

**[2026-08-30 03:50]**
- Initial document created (new topic for v2 draft coverage)
