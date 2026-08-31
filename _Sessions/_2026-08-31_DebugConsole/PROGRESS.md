# Session Progress

**Doc ID**: LANADEBG-PROGRESS

## STRUT Plan

[x] P1 [DESIGN]: Design debug console system
├─ Objectives:
│   ├─ [x] Log line schema covers all 3 domains (ACP, LLM, tool) ← P1-D1
│   ├─ [x] All instrumentation points identified with pre-computable values ← P1-D2
│   └─ [x] SPEC reviewed and approved by user ← P1-D3
├─ Strategy: Write SPEC from findings in NOTES.md. Cover: DebugLog class API, JSONL line schema, CLI flag, viewer subprocess design, instrumentation points. User reviews before P2.
├─ [x] P1-S1 [ANALYZE](existing `--debug` / `dump_debug` to decide reuse vs replace)
├─ [x] P1-S2 [DESIGN](JSONL log line schema: ts, domain, op, duration_ms, tokens, cost, detail, error)
├─ [x] P1-S3 [DESIGN](DebugLog class: pipe writer, subprocess spawner, graceful degradation, frozen-exe spawn)
├─ [x] P1-S4 [DESIGN](viewer subprocess: stdin reader, colorizer, domain filter)
├─ [x] P1-S5 [DESIGN](CLI integration: --debug-console flag, AppConfig field, wire-up in build_runtime)
├─ [x] P1-S6 [DESIGN](instrumentation map: every call site, what values to pre-compute)
├─ [x] P1-S7 [WRITE-SPEC](_SPEC_LANADEBG.md)
├─ Deliverables:
│   ├─ [x] P1-D1: JSONL schema definition
│   ├─ [x] P1-D2: Instrumentation map (call site -> log line -> pre-computed values)
│   └─ [x] P1-D3: _SPEC_LANADEBG.md approved (self-confirmed per /go autonomous protocol)
└─> Transitions:
    - P1-D1 - P1-D3 checked → P2 [IMPLEMENT-CORE]
    - User requests changes → P1-S7

[x] P2 [IMPLEMENT-CORE]: Build debug infrastructure
├─ Objectives:
│   ├─ [x] Debug console opens in a new window and displays log lines ← P2-D1, P2-D2
│   └─ [x] --debug-console flag wired end-to-end ← P2-D3
├─ Strategy: Build bottom-up: DebugLog writer first, then viewer subprocess, then CLI wiring. Test each layer before moving up.
├─ [x] P2-S1 [IMPLEMENT](DebugLog class: pipe write + flush, subprocess spawn with CREATE_NEW_CONSOLE)
├─ [x] P2-S2 [IMPLEMENT](viewer subprocess entry point: stdin reader, colorized pretty-printer)
├─ [x] P2-S3 [IMPLEMENT](--debug-console CLI flag; module singleton instead of AppConfig field, see LANADEBG-DD-02)
├─ [x] P2-S4 [IMPLEMENT](wire debuglog.enable() in main() - covers CLI and ACP paths before any instrumented operation)
├─ [2] P2-S5 [TEST](manual smoke: --debug-console opens window, receives lines, closes cleanly)
├─ Deliverables:
│   ├─ [x] P2-D1: DebugLog writer in src/lana/debuglog.py
│   ├─ [x] P2-D2: Viewer subprocess in src/lana/debug_viewer.py
│   └─ [x] P2-D3: --debug-console flag functional in CLI and ACP modes
└─> Transitions:
    - P2-D1 - P2-D3 checked → P3 [IMPLEMENT-INSTRUMENTATION]
    - Smoke test fails → P2-S1

[x] P3 [IMPLEMENT-INSTRUMENTATION]: Add logging at all instrumentation points
├─ Objectives:
│   ├─ [x] LLM domain: latency, TTFT, tokens, cost, cache, retries, errors ← P3-D1
│   ├─ [x] Tool domain: latency per tool, success/failure, approval, errors ← P3-D2
│   └─ [x] ACP domain: method timing, message flow, round-trip latency ← P3-D3
├─ Strategy: Instrument one domain at a time. Each domain: add timing + log calls, verify output in viewer. Pre-compute all values (duration, cost) before calling dlog().
├─ [x] P3-S1 [IMPLEMENT](LLM instrumentation: agent turn loop only - adapters need no changes, retry notices arrive as stream deltas)
├─ [x] P3-S2 [TEST](LLM domain: latency, tokens, cost verified in tests/test_debuglog.py + live smoke)
├─ [x] P3-S3 [IMPLEMENT](tool instrumentation: dispatch loop, approval gate)
├─ [x] P3-S4 [TEST](tool domain: latency, success/failure, denial verified in tests + live smoke)
├─ [x] P3-S5 [IMPLEMENT](ACP instrumentation: server router, run_prompt_turn, jsonrpc round-trips, EOF)
├─ [x] P3-S6 [TEST](ACP domain: verified live via ACP driver - recv/send/turn lines, exit 0)
├─ Deliverables:
│   ├─ [x] P3-D1: LLM domain fully instrumented
│   ├─ [x] P3-D2: Tool domain fully instrumented
│   └─ [x] P3-D3: ACP domain fully instrumented
└─> Transitions:
    - P3-D1 - P3-D3 checked → P4 [VERIFY]
    - Domain test fails → fix and re-test same domain

[x] P4 [VERIFY]: End-to-end testing and edge cases
├─ Objectives:
│   ├─ [x] Works in interactive CLI mode ← P4-D1
│   ├─ [x] Works in ACP mode ← P4-D2
│   ├─ [x] No performance regression ← P4-D3
│   └─ [x] Graceful degradation on viewer crash ← P4-D4
├─ Strategy: Run Lana with --debug-console in both modes. Verify all 3 domains visible. Kill viewer mid-session to test graceful handling. Run eval suite to check no regressions.
├─ [x] P4-S1 [TEST](headless CLI live run: llm + tool + app lines rendered in viewer, user-confirmed via screenshot)
├─ [x] P4-S2 [TEST](ACP mode live: initialize + session/new + 2x session/prompt with debug console, exit 0)
├─ [x] P4-S3 [TEST](viewer kill mid-session: one pipe-broken warning, Lana completed second prompt, clean shutdown)
├─ [x] P4-S4 [TEST](no flag: full pytest suite runs flag-less; dlog no-op path unit-tested, IG-04)
├─ [x] P4-S5 [TEST](pytest: 293 existing + 8 new debuglog tests passed, 0 regressions)
├─ Deliverables:
│   ├─ [x] P4-D1: Interactive mode verified
│   ├─ [x] P4-D2: ACP mode verified
│   ├─ [x] P4-D3: No performance regression
│   └─ [x] P4-D4: Graceful degradation confirmed
└─> Transitions:
    - P4-D1 - P4-D4 checked → P5 [DELIVER]
    - Failures found → fix in P3 or P2, re-verify

[x] P5 [DELIVER]: Polish, document, commit
├─ Objectives:
│   └─ [x] Feature complete, documented, committed ← P5-D1, P5-D2, P5-D3
├─ Strategy: Update README and docs, commit with conventional message, tell user to rebuild.
├─ [x] P5-S1 [REFINE](viewer formatting confirmed good in live run - colors, alignment, title)
├─ [x] P5-S2 [DOCUMENT](README.md: CLI reference line + spec list entry)
├─ [x] P5-S3 [COMMIT](c0163ab "feat: add --debug-console second console for real-time debug/timing output")
├─ [x] P5-S4 [NOTIFY](user to rebuild via _build.bat - in final report)
├─ Deliverables:
│   ├─ [x] P5-D1: Viewer output polished
│   ├─ [x] P5-D2: Documentation updated
│   └─ [x] P5-D3: Changes committed (c0163ab; README.md left uncommitted - contains unrelated pre-existing Quick Start rework)
└─> Transitions:
    - P5-D1 - P5-D3 checked → [END]

## Done

- [x] Scanned codebase: `cli.py`, `config.py`, `agent.py`, `render.py`, `events.py`, `session.py`, `server.py`, `jsonrpc.py`, `openai_adapter.py`, `anthropic_adapter.py`, `cost.py`
- [x] Identified 3 options, user chose Option B (pipe-connected spawned console)

## Tried But Not Used

- Option A (JSONL file + tail viewer) - viable but file I/O not needed when pipe is available
- Option C (background thread + queue + dual sink) - over-engineered for event volumes

## Decision Log (/go autonomous)

- [DECISION] Keep `--debug` unchanged, debug console is a separate mechanism - different concerns (payload dumps vs flow/timing); existing tests depend on it - LANADEBG-DD-06
- [DECISION] Module-level singleton instead of AppConfig field - ACP needs console before AppConfig exists; adapters/jsonrpc have no AppConfig access; precedent `_ADAPTER_CACHE` - LANADEBG-DD-02
- [DECISION] No adapter instrumentation needed - retry notices already arrive as stream deltas; request/TTFT/response measured in agent loop - fewer touch points - LANADEBG-DD-04
- [DECISION] P1-D3 SPEC approval self-confirmed - /go protocol, evidence: SPEC follows template, covers all NOTES.md requirements
- [DECISION] acp `turn` line consolidates send + turn_updates for session/prompt - less noise, honest semantics (router only creates the task) - APAPALAN

## Progress Changes

**[2026-08-31 14:15]**
- /improve vs logging rules (all 5 rule files re-read) driven by user questions on compaction visibility and exact timing
- Compaction now fully observable: compaction_start (projected/threshold trigger), compaction report (+checkpoint_chars), compaction_failed (silent-continue path)
- Exact timing: ts carries full date (LOG-AP-01), resume dur_ms, prompt_system load line
- Viewer: LOG-GN-04 durations (245 ms / 1.5 secs / 2 mins 30 secs), LOG-GN-02 quoting, date stripped for display
- Tests: 295 passed (+2: format_duration, compaction debug lines integration)

**[2026-08-31 14:00]**
- /drift-detect + /drift-correct executed: 7 FAIL closed, 2 MISSED recorded (__DRIFT_LANADEBG.md COMPLETE)
- Corrections: tool end err text (FR-03), summarizer + websearch sidecall instrumentation (FR-02), roles line (FR-05), DD-03 [ASSUMED], NFR-01 measured [TESTED], REPL live test, PYTHON-IM-03 fix
- Correction note: test total is 293 (earlier "301" was a miscount - the 293 already included the new debuglog tests)

**[2026-08-31 13:38]**
- P5 complete: committed c0163ab - STRUT reached [END]
- README.md NOT committed: contains my --debug-console docs plus unrelated pre-existing Quick Start rework - user decides

**[2026-08-31 13:35]**
- P1-P4 complete, P5 docs done - commit pending
- Fixed LANADEBG-PR-0005 (blank viewer window - std handle inheritance, DD-08/EC-08)
- Tests: 301 passed (293 existing + 8 new), 0 regressions
- Live verified: headless CLI with viewer (user screenshot), ACP mode + viewer kill resilience

**[2026-08-31 13:08]**
- STRUT plan created (P1-P5)
- User chose Option B (LANADEBG-DD-01)
- EXPLORE phase complete, entering DESIGN

**[2026-08-31 12:58]**
- Initial progress tracking created
- Scanned `cli.py` and `config.py` for current state
