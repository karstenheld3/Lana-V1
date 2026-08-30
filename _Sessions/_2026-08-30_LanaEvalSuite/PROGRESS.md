# Session Progress

**Doc ID**: LANATEST-PROGRESS

## Phase Plan

- [x] **EXPLORE** - done: read IPPS concept docs + CSRCMP-IN10 research, inventoried 46 workflows / 23 skills, proposed 3 alternatives, user chose B
- [x] **DESIGN** - done: `_SPEC_LANA_EVAL_SUITE.md [LANATEST-SP01]` + `_IMPL_LANA_EVAL_SUITE.md [LANATEST-IP01]` (user chose B, prompt queue format, llm-evaluation judge)
- [x] **IMPLEMENT** - done: runner, 3 tiers, 9 tests across 3 buckets, goldens 8/9, all offline drives green, cost tracking (STRUT P1-P11 → [END])
- [ ] **VERIFY** - in_progress: harness validated offline (PASS/FAIL/leak/immutability paths); pending: live run with real models (user), 03-T02 golden
- [ ] **RELEASE** - pending: integrate into CI or manual test run process

## To Do

- [ ] Live test-drive with real models (user): `.venv\Scripts\python.exe evals\suite\runner\run_evals.py All`
- [ ] Golden for 03-T02 DeepResearch (requires live Cascade deep-research run)
- [ ] Future catalog growth: drift-detect → drift-correct sequence test (needs __DRIFT_ scaffold design), more Bucket 1 difficulty levels

## In Progress

- (none yet)

## Decision Log

- [DECISION] Bucket 2 sequence tests use verify-fix and critique-reconcile-implement chains; drift-detect → drift-correct deferred - rationale: drift workflows need conversation-log evidence that headless runs structure differently; needs its own scaffold design - rules consulted: LANATEST-SP01 FR-12, drift-detect.md
- [DECISION] 03-T02 goldens NOT self-produced - rationale: honest golden requires real web research; fabricating a researched-looking INFO doc would poison the rubric anchor - rules consulted: LANATEST-SP01 DD-02, AUDITCITE-IN01
- [DECISION] cp1252 crash fixed upstream in cli.py (force UTF-8 stdio) instead of runner-side workaround - rationale: any consumer piping jsonl on Windows would hit it - rules consulted: bugfix discipline (root cause over symptom)

## Done

- [x] 2026-08-30: STRUT P6-P10 complete → [END]: workflow categorization (NOTES.md), Bucket 1 T03 SearchAndRefactor + T04 ShellExecution, Bucket 2 T02 VerifyFix + T03 CritiqueSequence, Bucket 3 T02 DeepResearch, goldens 8/9 tests; all offline drives green; found + fixed real Lana bug (cp1252 jsonl crash), suite 266 offline green
- [x] 2026-08-30: Inventory + categorization of 46 workflows into buckets (NOTES.md); evaluation-approach research (CSRCMP-IN10 + GRUC)
- [x] 2026-08-30: Eval suite MVP implemented and offline-proven (`LANATEST-IP01` STRUT P1-P5): runner + Tier 1-3 evaluators (judge via @skills:llm-evaluation call-llm.py) + 4 tests (01-T01/T02, 02-T01, 03-T01); drives: PASS 1.00/1.00, sabotage FAIL 0.00/0.50 with named checks
- [x] 2026-08-30: Lana prompt queue implemented (LANAACPB-SP01 FR-12, IP01 Phase 7 IS-14/15) - parser, --prompt-file, prompt_step event; 15 new tests, full suite 265 offline green (VC-13, TP01-VC-07)
- [x] Session initialized (2026-08-30)

## Tried But Not Used

- (none yet)
