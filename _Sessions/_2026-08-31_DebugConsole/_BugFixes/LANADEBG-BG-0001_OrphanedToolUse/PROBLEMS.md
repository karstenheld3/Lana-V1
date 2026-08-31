# Bug: LANADEBG-BG-0001

**Status**: Resolved
**Reported**: 2026-08-31 14:15

## Verbatim Error

````
Provider error: Anthropic API error: Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'messages.4: tool_use ids were found without tool_result blocks immediately after: toolu_019jLYCvpsJ9bxMDeu6ifvD, toolu_01Ccg5zWLJN24wNi2TNsVTKw. Each tool_use block must have a corresponding tool_result block in the next message.'}, 'request_id': 'req_011CeaopwKiTs3oFJUjNdx3D'}
````

## Root Cause

Two interacting defects:

**Defect 1: Orphaned tool_use blocks** (`agent.py`)
- `CancelledError` (Python 3.12: `BaseException`, not caught by `dispatch_call`'s `except Exception`) interrupts mid-tool-dispatch
- Assistant message with N `tool_use` blocks already in `self.messages` (line 183)
- Only M < N `tool_result` messages appended before cancellation (line 211)
- `note_cancellation()` does not repair the gap

**Defect 2: Consecutive user messages** (`anthropic_adapter.py`)
- `note_cancellation()` appends `Message(role="user", ...)` cancellation note
- Next `run_prompt` appends another `Message(role="user", ...)` via `build_user_message`
- `build_messages()` creates separate Anthropic messages for each, violating alternation rule

## Impact

Both CLI and ACP modes affected. Any cancellation during a multi-tool turn permanently breaks the session.

## Fix Plan

1. `agent.py`: Add `_patch_orphaned_tool_results()` called from `note_cancellation()` - synthesize error `tool_result` for each missing tool_call_id
2. `session.py`: `_Projector` synthesizes missing tool_results during resume/replay (same orphan pattern from JSONL events)
3. `anthropic_adapter.py`: Fix `build_messages()` to merge consecutive user messages into one (safety net for all edge cases)
4. Tests: in-memory patch test, JSONL resume test with orphaned events, `build_messages` merge test

## Verification Note (GLOB-FL-0002)

Initial fix (agent.py only) missed the resume path. The `_Projector` independently reconstructs messages from JSONL events and had the same orphan problem. `/verify` caught this before it shipped.
