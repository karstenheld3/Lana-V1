# Session Problems

**Doc ID**: LANADEBG-PROBLEMS

## Open

**LANADEBG-PR-0001: No second console for debug/logging output**
- **History**: Added 2026-08-31 12:58
- **Description**: Lana has no mechanism to display debug/logging output in a separate console window. All output goes to the main console via `print()`. In ACP mode, stdout is the JSON-RPC transport, so debug output has nowhere to go.
- **Impact**: Debugging requires reading log files after the fact; no real-time visibility into agent internals
- **Next Steps**: Design a second-console mechanism with a CLI flag

**LANADEBG-PR-0002: CLI flag design for second console**
- **History**: Added 2026-08-31 12:58
- **Description**: Need a new CLI flag (e.g. `--debug-console`) that spawns a second console window on startup. Must coexist with existing `--debug` (file-based API traffic logging) and work in both interactive and ACP modes.
- **Impact**: User experience - single flag to enable real-time debug view
- **Next Steps**: Design flag, integrate into `build_arg_parser()` and `build_runtime()`

**LANADEBG-PR-0003: Performance requirement - logging must be super-fast**
- **History**: Added 2026-08-31 12:58
- **Description**: User requires minimal overhead from debug logging. Writing to a second console must not slow down the main agent loop.
- **Impact**: Architecture choice - async writes, buffered I/O, or fire-and-forget pattern needed
- **Next Steps**: Evaluate approaches (named pipe, socket, async queue, subprocess stdin)

**LANADEBG-PR-0004: ACP mode compatibility**
- **History**: Added 2026-08-31 12:58
- **Description**: In ACP mode (`--acp`), stdout/stdin are reserved for JSON-RPC 2.0 protocol. The second console must work without touching stdout. Current `print()` calls in `cli.py` already go to stdout - need to understand if those are suppressed in ACP mode.
- **Impact**: Blocking - must verify ACP stdio handling before designing the second console output path
- **Next Steps**: Read `server.py` (ACP entry point) to understand how stdout is managed

## Resolved

**LANADEBG-PR-0005: Viewer window blank - std handle inheritance**
- **History**: Added 2026-08-31 13:26 | Resolved 2026-08-31 13:30
- **Description**: First smoke test showed an empty viewer window. Cause: `stdin=PIPE` makes Windows spawn use STARTF_USESTDHANDLES, so the child's stdout/stderr pointed at the PARENT's streams, not the new console - viewer output went to the parent (would corrupt ACP stdout).
- **Solution**: Viewer renders via its own console device (`CONOUT$`); spawn detaches child stdout/stderr to DEVNULL (LANADEBG-DD-08, EC-08)
- **Verification**: Second smoke test shows rendered lines in the viewer window

## Deferred

(none)

## Problems Changes

**[2026-08-31 12:58]**
- Added: LANADEBG-PR-0001 (no second console)
- Added: LANADEBG-PR-0002 (CLI flag design)
- Added: LANADEBG-PR-0003 (performance requirement)
- Added: LANADEBG-PR-0004 (ACP mode compatibility)
