# Deferred Improvements: src/lana (Code)

**Doc ID**: LANAAGNT-DF02
**Goal**: Track code improvement candidates deferred from `/improve` runs on the Lana implementation
**Target file(s)**:
- `src/lana/` (22 modules), `tests/`
**Timeline**: Created 2026-08-30, Updated 0 times

**Depends on:**
- `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` for implementation context

## Candidates

### D-01: Close SessionStore file handle on CLI exit
- **Issue**: `cli.main()` never calls `session.close()`; the handle closes only at interpreter exit
- **Fix**: try/finally around repl/run_headless calling `agent.session.close()`
- **Effort**: Minimal
- **Value**: LOW - fails pragmatic Q2 (theoretical): every line is flushed at write (FR-08), the process exits right after, and Python closes handles at exit; no observed lock or loss scenario

### D-02: Garbage-collect `.lana/chunks/*.json`
- **Issue**: `read_url_content` chunk files accumulate indefinitely per workspace
- **Fix**: Age-based cleanup at startup or a `/cleanup`-style built-in
- **Effort**: Low
- **Value**: LOW - fails pragmatic Q2 (theoretical): ~5 KB per chunk, research sessions produce dozens at most; no observed pressure

### D-03: File-count cap for grep_search file-list mode
- **Issue**: File-mode output (one line per matching file) has no own cap; only MatchPerLine has GREP_LINE_CAP
- **Fix**: Cap file list at 50 entries like find_by_name
- **Effort**: Minimal
- **Value**: LOW - fails pragmatic Q1 (already addressed): `cap_result()` bounds every tool result at `tool_result_max_chars` (EC-04)

### D-04: Recovery actions in all ToolError messages (MC-PR-05)
- **Issue**: Some errors state what failed but not the recovery action (e.g., "Search path not found: 'x'")
- **Fix**: Sweep all `raise ToolError` sites, append recovery hints
- **Effort**: Low
- **Value**: LOW - fails pragmatic Q3 (proportionality): the Generator self-corrects from what+why alone; the gate errors (FR-11/FR-12) that matter already include recovery actions

### D-05: `--show-thinking` CLI flag
- **Issue**: `Renderer.show_thinking` exists but no flag exposes it; thinking deltas are emitted yet invisible interactively
- **Fix**: argparse flag wired to Renderer
- **Effort**: Minimal
- **Value**: MEDIUM but out of `/improve` scope - new user-facing feature, belongs in SPEC first (FR change, not refactoring)

## Log

- **Run 1** (2026-08-30): APPLIED - rg/fd ignore-directory parity for grep_search/find_by_name (IGNORED_DIRECTORIES skip set + exclusion tests; commit 68da12c). Violations fixed: `check_read_gate` -> `enforce_read_gate` (MC-PR-03), unused import; brittle DevSystemV4.2 count assertions de-hardcoded after external system evolved 21 -> 23 skills (SOCAS-10, commit 6138f5e)
- **Run 2** (2026-08-30): No APPLY-able candidate remained - D-01..D-05 deferred with per-question rationale; loop terminated

## Document History

**[2026-08-30 03:30]**
- Initial deferred improvements file created from `/improve` runs 1-2 on the Lana code
