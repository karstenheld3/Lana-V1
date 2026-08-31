# Failure Log

Lessons learned from past mistakes. Never delete entries unconfirmed; only append or mark as resolved.
ID format: `GLOB-FL-[NNNN]`

## Failures

- **GLOB-FL-0001** [CRITICAL] 2026-08-31: Hallucinated protocol step shipped to production
  - **What**: ACP knowledge docs (`ACP-IN04`, `ACP-IN05`) documented an `initialized` client notification with [VERIFIED] tags. The notification does not exist in ACP - it is an MCP/LSP concept. The error propagated: knowledge → SPEC (LANAACPB-FR-02) → IMPL (EC-06) → `server.py` state machine gating `session/new` on a notification no compliant client sends. Windsurf's ACP client was rejected with "handshake incomplete (state 'awaiting_initialized')".
  - **Why it slipped**: 1) [VERIFIED] tag applied without checking the official sequence diagram (which ends "Ready for session setup" after the `initialize` response); 2) tests were written from the same contaminated knowledge - the test harness sent the phantom notification, so the suite could not catch it; 3) a "Devin Desktop compatibility auto-promote" workaround was patched on top instead of questioning the state machine (symptom fix, root cause missed).
  - **Lesson**: When documenting protocol X while knowing similar protocol Y, explicitly check each handshake step against X's official schema/SDK method inventory - LLM knowledge of one protocol contaminates another. A client "violating" the spec (Devin Desktop, then Windsurf) is a signal the spec understanding may be wrong, not the clients.
  - **Fix**: `server.py` two-state machine (`uninitialized → initialized`, complete on `initialize` response), harness/tests, knowledge docs, SPEC/IMPL/TEST synced. Verified against https://agentclientprotocol.com/protocol/v1/initialization and the official TypeScript SDK (only `initialize` exists).

- **GLOB-FL-0002** [HIGH] 2026-08-31: Bugfix missed resume path - fix only worked in memory
  - **What**: BG-0001 initial fix patched orphaned `tool_use` blocks in `agent.py` (`_patch_orphaned_tool_results`) but did not patch the session `_Projector` in `session.py`. The fix worked for the current session but the same Anthropic 400 error recurred on `session/load` (ACP) or `--resume` (CLI) because the JSONL replay reconstructed the broken conversation state.
  - **Why it slipped**: 1) The `collect_until` test helper simulates cancellation by closing the generator cleanly between yields - this never creates orphaned events in the JSONL (the 3rd tool was never requested). 2) The test verified in-memory state (correct) but not the resumed state from JSONL (broken). 3) Fix was applied only where the bug was observed (agent runtime) without tracing all consumers of the event log.
  - **Lesson**: When fixing state corruption bugs in event-sourced systems, trace EVERY path that reconstructs state from the event log. The runtime path and the replay path are independent implementations that can diverge. Always write a resume/replay test that exercises the exact event sequence a real crash produces - not a clean simulation.
