# Workspace Problems

**Doc ID**: GLOB-PROBLEMS

Track problems using ID format: `GLOB-PR-[NNNN]`

## Open

- (none yet)

## Resolved

**GLOB-PR-0001: Anthropic 400 after cancellation - orphaned tool_use blocks (LANADEBG-BG-0001)**
- **History**: Added 2026-08-31 | Resolved 2026-08-31
- **Impact**: Any cancellation during multi-tool turns broke the session permanently - no further prompts could succeed
- **Solution**: `_patch_orphaned_tool_results()` in `agent.py`, projector fix in `session.py`, user message merge in `anthropic_adapter.py`. Committed 5cc2dfc.

## Deferred

- (none yet)
