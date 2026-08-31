# Session Problems

**Doc ID**: LANADEBG-PROBLEMS

## Open

(none)

## Resolved

**LANADEBG-PR-0006: Anthropic 400 after cancellation - orphaned tool_use blocks**
- **History**: Added 2026-08-31 14:15 | Resolved 2026-08-31 14:30
- **Solution**: Tracked as LANADEBG-BG-0001. Two fixes: `_patch_orphaned_tool_results()` in `agent.py` synthesizes missing `tool_result` messages; `build_messages()` in `anthropic_adapter.py` merges consecutive user messages.

**LANADEBG-PR-0001: No second console for debug/logging output**
- **History**: Added 2026-08-31 12:58 | Resolved 2026-08-31 13:38
- **Solution**: `--debug-console` flag spawns a pipe-connected viewer window (LANADEBG-DD-01). Committed c0163ab.

**LANADEBG-PR-0002: CLI flag design for second console**
- **History**: Added 2026-08-31 12:58 | Resolved 2026-08-31 13:38
- **Solution**: `--debug-console` in `build_arg_parser()`, `enable_debug_console()` in `main()` before any instrumented operation.

**LANADEBG-PR-0003: Performance requirement - logging must be super-fast**
- **History**: Added 2026-08-31 12:58 | Resolved 2026-08-31 13:38
- **Solution**: Synchronous pipe write + flush at 13.6 us/line [TESTED]. Known hazard: pipe blocks after 23 lines if viewer stalls (LANADEBG-IN01). Async queue mitigation proposed but not yet implemented.

**LANADEBG-PR-0004: ACP mode compatibility**
- **History**: Added 2026-08-31 12:58 | Resolved 2026-08-31 13:38
- **Solution**: Debug console uses a separate pipe, never touches stdout/stdin. ACP mode verified with 2x session/prompt + debug console (P4-S2).

**LANADEBG-PR-0005: Viewer window blank - std handle inheritance**
- **History**: Added 2026-08-31 13:26 | Resolved 2026-08-31 13:30
- **Solution**: Viewer renders via its own console device (`CONOUT$`); spawn detaches child stdout/stderr to DEVNULL (LANADEBG-DD-08, EC-08)

## Deferred

(none)

## Problems Changes

**[2026-08-31 12:58]**
- Added: LANADEBG-PR-0001 (no second console)
- Added: LANADEBG-PR-0002 (CLI flag design)
- Added: LANADEBG-PR-0003 (performance requirement)
- Added: LANADEBG-PR-0004 (ACP mode compatibility)
