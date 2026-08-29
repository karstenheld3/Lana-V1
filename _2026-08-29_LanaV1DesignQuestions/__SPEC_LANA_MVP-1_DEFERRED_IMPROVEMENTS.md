# Deferred Improvements: _SPEC_LANA_MVP-1

**Doc ID**: LANAAGNT-DF01
**Goal**: Track improvement candidates deferred from `/improve` runs
**Target file(s)**:
- `_2026-08-29_LanaV1DesignQuestions/_SPEC_LANA_MVP-1.md`
**Timeline**: Created 2026-08-29, Updated 0 times

**Depends on:**
- `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` for improvement context

## Candidates

### D-01: `trajectory_search` support for the `/remove` workflow (scan evidence)
- **Issue**: `/remove` (conversation-content removal) references `trajectory_search` 3 times; MVP-1 has no trajectory index, so the workflow cannot complete those steps (capability notice covers the failure mode)
- **Fix**: MVP-2+ candidate - implement `trajectory_search` over Lana's own session JSONL files (they ARE the trajectories; a local search over `.lana/sessions/` would satisfy the tool contract)
- **Effort**: Medium
- **Value**: LOW (1 workflow of 46; niche use)

### D-02: Fake-adapter scripting format unspecified (Walkthrough finding, LANAAGNT-IP01)
- **Issue**: `tests/conftest.py` promises "fake adapters" but no format exists for scripting their turn sequences (which tool calls, which text, per test)
- **Fix**: Define a small scripted-turn fixture format (list of AdapterDelta sequences) in conftest during Phase A; document in IP01 IS-13 note
- **Effort**: Low
- **Value**: MEDIUM (blocks nothing - conftest authorship covers it - but a defined format keeps 14 test modules consistent)
- **Status**: SUPERSEDED by LANAAGNT-IP01-IS-22 (2026-08-29 22:20) - the scripted adapter JSONL format and `LanaProc` harness specify this fully

### D-03: Key-free execution order recommendation (LANAAGNT-TK01)
- **Issue**: Document order (Phase D before E) suggests API keys are needed mid-way; the dependency graph already permits deferring TK-016/017/033 until after all scripted-path work
- **Fix**: Add a one-paragraph "recommended execution order" note to TK01 making the fully key-free corridor explicit (A, B, C, TK-015, TK-018, E, F, G, then D live, H, scenarios)
- **Effort**: Minimal
- **Value**: LOW (Task 0 note + dependency graph already carry the information; pure convenience)

## Log

- **Run 1** (2026-08-29): Added web research tools (`search_web`, `read_url_content`, `view_content_chunk`) to LANAAGNT-SP01 based on DevSystemV4.2 full-text tool demand scan
- **Run 2** (2026-08-29): Created `_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02]` (15 verbatim tool definitions from live session); repointed LANAAGNT-IP01 IS-06/VC-01/Depends-on and the LANAAGNT-SP01 authority constraint
- **Run 3** (2026-08-29): Added Task Execution Protocol to LANAAGNT-TK01 (context-reset-safe execution rules)

## Document History

**[2026-08-29 22:46]**
- Added: D-03 (key-free execution order note) and Run 3 log entry

**[2026-08-29 22:14]**
- Added: D-02 (fake-adapter scripting format) and Run 2 log entry

**[2026-08-29 21:48]**
- Initial deferred improvements file created from `/improve` run 1
- Added: D-01 (trajectory_search over session JSONL)
