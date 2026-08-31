# Session Problems

**Doc ID**: LANAUSRX-PROBLEMS

**Purpose**: All dead-air and status-signaling problems identified in the Lana interaction chain.

## Open

**LANAUSRX-PR-0001: ACP frontend sends zero updates between turn_started and first content delta**
- **History**: Added 2026-08-31 16:55
- **Description**: `EventTranslator.translate()` returns `[]` for `turn_started`. The Devin Desktop client has no signal that the LLM request is in flight. Duration: 2-30+ seconds.
- **Impact**: User sees no activity in Devin Desktop during model thinking. Indistinguishable from a crash.
- **Next Steps**: Emit a structured ACP update (e.g. `agent_thought_chunk` or a status indicator) on turn_started.

**LANAUSRX-PR-0002: CLI spinner stops when no thinking deltas arrive (pure dead air before first SSE event)**
- **History**: Added 2026-08-31 16:55
- **Description**: The Rich spinner in `render.py` ticks via `tick_status()` which is only called on `thinking_delta` events. If the model has no thinking (or thinking is disabled), the spinner says "generator thinking..." but never updates the elapsed counter until the first text/tool delta arrives.
- **Impact**: Spinner appears frozen during the network round-trip to the provider API.
- **Next Steps**: Add a background timer tick to the spinner independent of thinking deltas, OR show a periodic heartbeat.

**LANAUSRX-PR-0003: Long-running tool executions show zero progress**
- **History**: Added 2026-08-31 16:55
- **Description**: `run_command` (Blocking: up to 600s), `search_web` (2-15s), `read_url_content` (up to 120s) show only start/end markers. No intermediate progress.
- **Impact**: User cannot distinguish a slow command from a hung agent.
- **Next Steps**: For `run_command` Blocking, consider streaming partial output. For web tools, consider elapsed-time updates.

**LANAUSRX-PR-0004: Compaction/summarizer call (5-30s) shows no progress indicator**
- **History**: Added 2026-08-31 16:55
- **Description**: After the NOTICE "Compacting context...", the summarizer LLM call runs with zero output until it completes or fails.
- **Impact**: User sees "Compacting context..." and then nothing for up to 30 seconds.
- **Next Steps**: Show elapsed time during summarizer call, similar to the generator spinner.

**LANAUSRX-PR-0005: ACP session build (session/new) sends no progress to client**
- **History**: Added 2026-08-31 16:55
- **Description**: `build_session_runtime()` redirects all stdout to stderr. Client receives nothing until the session/new JSON-RPC response.
- **Impact**: Low severity (usually <2s). But on slow filesystems or large prompt systems, client shows no activity.
- **Next Steps**: Evaluate whether ACP v1 has a notification channel for session-build progress. May be deferred.

**LANAUSRX-PR-0006: Post-turn dead air between Turn stats and next event**
- **History**: Added 2026-08-31 16:55
- **Description**: After `turn_finished` renders the Turn stats line, the agent enters the next iteration of the while loop and calls `stream_turn()` again. Between the Turn line and the next `turn_started` (which starts the spinner), there is a gap where the messages list is being assembled, serialized, and sent to the provider.
- **Impact**: This is the dead air visible in the user's screenshot. The cursor blinks after the Turn line with no indication of what's happening.
- **Next Steps**: Minimize the gap by emitting `turn_started` BEFORE message serialization, or add a status indicator.

**LANAUSRX-PR-0007: CLI render.py spinner is model-text-only - no tool execution spinner**
- **History**: Added 2026-08-31 16:55
- **Description**: The Rich status spinner is started at `turn_started` and stopped at any visible output. But during tool execution (between `tool_call_requested` and `tool_call_finished`), there is no spinner. Only a static `[tool]` line.
- **Impact**: Multi-second tool calls (especially search_web, read_url_content) look frozen.
- **Next Steps**: Start a tool-specific spinner after the `[tool]` line, stopped by `tool_call_finished`.

## Resolved

(none)

## Deferred

(none)

## Problems Changes

**[2026-08-31 16:55]**
- Added: LANAUSRX-PR-0001 through LANAUSRX-PR-0007 (initial dead-air audit)
