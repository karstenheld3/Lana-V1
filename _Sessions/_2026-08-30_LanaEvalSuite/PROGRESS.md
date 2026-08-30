# Session Progress

**Doc ID**: LANATEST-PROGRESS

## Phase Plan

- [x] **EXPLORE** - done: read IPPS concept docs + CSRCMP-IN10 research, inventoried 46 workflows / 23 skills, proposed 3 alternatives, user chose B
- [x] **DESIGN** - done: `_SPEC_LANA_EVAL_SUITE.md [LANATEST-SP01]` + `_IMPL_LANA_EVAL_SUITE.md [LANATEST-IP01]` (user chose B, prompt queue format, llm-evaluation judge)
- [ ] **IMPLEMENT** - in_progress: MVP done and offline-proven (runner, 3 tiers, 4 tests); pending: prompt catalogs, golden production
- [ ] **VERIFY** - pending: produce golden outputs with Cascade + IPPS, validate evaluation harness
- [ ] **RELEASE** - pending: integrate into CI or manual test run process

## To Do

- [ ] Inventory all workflows and skills in `.lana/` and `.devin/`
- [ ] Categorize workflows into Bucket 2 (basic IPPS) vs. Bucket 3 (special Lana)
- [ ] Research evaluation approaches for non-deterministic LLM outputs
- [ ] Extend Bucket 1 prompt catalog (more difficulty levels)
- [ ] Extend Bucket 2 prompt catalog (verify → improve, critique → reconcile → implement, drift-detect → drift-correct sequences)
- [ ] Extend Bucket 3 (full deep-research test with unambiguous question)
- [ ] Produce golden reference outputs using Cascade + IPPS (per-test instructions in TEST.md files)
- [ ] Live test-drive with real models (user): `.venv\Scripts\python.exe evals\suite\runner\run_evals.py All`

## In Progress

- (none yet)

## Done

- [x] 2026-08-30: Eval suite MVP implemented and offline-proven (`LANATEST-IP01` STRUT P1-P5): runner + Tier 1-3 evaluators (judge via @skills:llm-evaluation call-llm.py) + 4 tests (01-T01/T02, 02-T01, 03-T01); drives: PASS 1.00/1.00, sabotage FAIL 0.00/0.50 with named checks
- [x] 2026-08-30: Lana prompt queue implemented (LANAACPB-SP01 FR-12, IP01 Phase 7 IS-14/15) - parser, --prompt-file, prompt_step event; 15 new tests, full suite 265 offline green (VC-13, TP01-VC-07)
- [x] Session initialized (2026-08-30)

## Tried But Not Used

- (none yet)
