# Failure Log

Lessons learned from past mistakes. Never delete entries unconfirmed; only append or mark as resolved.
ID format: `GLOB-FL-[NNNN]`

## Failures

- **GLOB-FL-0001** [CRITICAL] 2026-08-31: Hallucinated protocol step shipped to production
  - **What**: ACP knowledge docs (`ACP-IN04`, `ACP-IN05`) documented an `initialized` client notification with [VERIFIED] tags. The notification does not exist in ACP - it is an MCP/LSP concept. The error propagated: knowledge → SPEC (LANAACPB-FR-02) → IMPL (EC-06) → `server.py` state machine gating `session/new` on a notification no compliant client sends. Windsurf's ACP client was rejected with "handshake incomplete (state 'awaiting_initialized')".
  - **Why it slipped**: 1) [VERIFIED] tag applied without checking the official sequence diagram (which ends "Ready for session setup" after the `initialize` response); 2) tests were written from the same contaminated knowledge - the test harness sent the phantom notification, so the suite could not catch it; 3) a "Devin Desktop compatibility auto-promote" workaround was patched on top instead of questioning the state machine (symptom fix, root cause missed).
  - **Lesson**: When documenting protocol X while knowing similar protocol Y, explicitly check each handshake step against X's official schema/SDK method inventory - LLM knowledge of one protocol contaminates another. A client "violating" the spec (Devin Desktop, then Windsurf) is a signal the spec understanding may be wrong, not the clients.
  - **Fix**: `server.py` two-state machine (`uninitialized → initialized`, complete on `initialize` response), harness/tests, knowledge docs, SPEC/IMPL/TEST synced. Verified against https://agentclientprotocol.com/protocol/v1/initialization and the official TypeScript SDK (only `initialize` exists).
