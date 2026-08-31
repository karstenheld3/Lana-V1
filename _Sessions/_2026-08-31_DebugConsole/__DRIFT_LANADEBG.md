<DevSystem MarkdownTablesAllowed=true />
# Drift: LANADEBG

**Target workflow**: /go (STRUT execution P1-P5)
**Context**: Code Implementation
**Directive**: against STRUT
**Status**: COMPLETE

## Criteria

| ID | Criterion                                                        | Cat | Priority | Status | Source            |
|----|------------------------------------------------------------------|-----|----------|--------|-------------------|
| 01 | FR-01 flag works in REPL, headless, ACP                           | 1   | HIGH     | PASS   | SPEC FR-01        |
| 02 | FR-02 generator turns: request/TTFT/response/retry/error          | 1   | HIGH     | PASS   | SPEC FR-02        |
| 03 | FR-02 ALL backend calls covered (summarizer, websearch side-call) | 1   | HIGH     | PASS   | summarizer request/response in compaction.py; websearch `sidecall` line in web_tools.py |
| 04 | FR-03 tool end line carries error text (first 300 chars)          | 1   | HIGH     | PASS   | agent.py err field on failed calls; unit-tested |
| 05 | FR-03 approval line: action, resolution, wait duration            | 1   | MEDIUM   | PASS   | SPEC FR-03        |
| 06 | FR-04 ACP: recv/send/turn/roundtrip/lifecycle/EOF                 | 1   | HIGH     | PASS   | SPEC FR-04, live ACP driver |
| 07 | FR-05 roles banner logged (dedicated `roles` line at runtime build)| 1   | MEDIUM   | PASS   | cli.py build_runtime; SPEC FR-05 synced |
| 08 | FR-05 session + compaction lines                                  | 1   | MEDIUM   | PASS   | SPEC FR-05 (session live; compaction code-verified only) |
| 09 | FR-06 viewer rendering: colors, alignment, EOF notice             | 1   | HIGH     | PASS   | SPEC FR-06, user screenshot |
| 10 | IG-01 no stdout/stdin writes in debug paths                       | 1   | HIGH     | PASS   | DEVNULL spawn + CONOUT$, ACP live exit 0 |
| 11 | IG-02 pipe failure never raises into call sites                   | 1   | HIGH     | PASS   | unit test + live viewer kill |
| 12 | IG-03 durations from monotonic clocks                             | 1   | HIGH     | PASS   | perf_counter at all boundaries |
| 13 | IG-04 zero overhead when disabled                                 | 1   | HIGH     | PASS   | None-check fast path, unit test |
| 14 | IG-05 no payloads/keys in lines                                   | 1   | HIGH     | PASS   | args_summary identifiers only; tool err field capped at 300 chars |
| 15 | EC-01/02/04/06 handled (EC-03/05/07 N/A)                          | 1   | MEDIUM   | PASS   | EC-01 live, EC-02/06 code+unit; EC-04 keypress-wait itself unconfirmed |
| 16 | DD-03 PyApp binary viewer spawn verified or labeled [ASSUMED]     | 1   | HIGH     | PASS   | [ASSUMED] label added to DD-03; binary verification deferred to next rebuild |
| 17 | NFR-01 stated verification method executed (timing comparison)    | 1   | MEDIUM   | PASS   | measured 3x each: without 686 ms avg, with 633 ms avg - within noise; SPEC updated [TESTED] |
| 18 | STRUT deliverables P1-D1..P5-D3 exist and are checked             | 1   | HIGH     | PASS   | PROGRESS.md STRUT |
| 19 | STRUT step sequence followed (P1 → P5, gates respected)           | 2   | HIGH     | PASS   | conversation flow |
| 20 | STRUT steps not rewritten to match outcome without decision log   | 2   | MEDIUM   | MISSED | P4-S1 "interactive CLI" reworded to "headless CLI" while marking done - not logged as DECISION |
| 21 | Interactive REPL live test with --debug-console (original P4-S1)  | 2   | MEDIUM   | PASS   | piped REPL run: prompt cycle + /exit, exit 0 |
| 22 | /verify run after implementation (significant change)             | 2   | MEDIUM   | PASS   | focused verify vs PYTHON-RULES: 1 violation (IM-03 rich import) found and fixed |
| 23 | Tracking files updated (NOTES, PROBLEMS, PROGRESS)                | 2   | HIGH     | PASS   | session folder     |
| 24 | Tests actually run, not just written                              | 2   | HIGH     | PASS   | 293 passed live (includes 9 debuglog tests) |
| 25 | Commit created for completed work                                 | 2   | HIGH     | PASS   | c0163ab            |
| 26 | Scope reductions logged as decisions (summarizer/websearch exclusion) | 2 | MEDIUM | MISSED | /go Decision Logging - exclusion decided silently |
| 27 | P5-S2 docs/ checked for applicable doc targets                    | 2   | LOW      | PASS   | docs/README.md has no CLI reference - root README was the only target |

## TODOs

FAIL items in priority order:

- [x] 04: Add error text (first 300 chars, from `call.result`) to the tool `end` debug line and viewer rendering (FR-03, respect IG-05 truncation)
- [x] 03: Instrument summarizer compaction call; websearch side-call gets a `sidecall` line (usage not surfaced by provider wrappers - documented in SPEC FR-02)
- [x] 16: Add `[ASSUMED]` label to DD-03 PyApp claim in SPEC; verify after user rebuilds the binary
- [x] 07: Roles banner as dedicated `roles` line at runtime build (config not loaded at startup - SPEC FR-05 synced)
- [x] 21: Run interactive REPL live test with `--debug-console` (piped stdin exercised the REPL loop, exit 0)
- [x] 17: NFR-01 measured (3x each: 686 ms vs 633 ms avg - within noise); SPEC verification line carries [TESTED] evidence
- [x] 22: Focused verify vs @skills:coding-conventions PYTHON-RULES - fixed IM-03 (rich import moved to module top)

## MISSED

- 20: STRUT step P4-S1 reworded from "interactive CLI" to "headless CLI live run" while marking it done - DoD weakening without a [DECISION] entry (Category 2)
- 26: Summarizer/websearch instrumentation exclusion decided silently during P3 - never logged as [DECISION] per /go protocol (Category 2)

## Meta-Criteria Observations

- Prompt Decomposition: present (3-option analysis before design)
- Current/Target Comparison: present (full codebase scan before SPEC)
- Self-Correction: present (LANADEBG-PR-0005 blank-window bug found and fixed during smoke test)
- Strategy Justification: present (Decision Log in PROGRESS.md)
- Quantitative Completeness: ABSENT - SPEC FR fields were not cross-checked item-by-item against code before marking P3 complete (caused 03, 04, 07)
- Constraint Re-reading: partial - SPEC re-read for sync edits but not as a completion checklist
