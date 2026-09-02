# TEST: Lana Eval Suite - Verification Plan

**Doc ID**: LANATEST-TP01
**Goal**: Verify the eval suite runner, evaluators, and judge meet all LANATEST-SP01 requirements -- offline via scripted drives, live via real agent runs with budget cap
**Timeline**: Created 2026-09-01

**Target file(s)**:
- Offline verification via scripted adapter drives (`--scripted` flag)
- Live verification via real `lana --prompt-file` runs (user-approved spend)
- Drive scripts persisted in `evals/suite/runner/drive-scripts/`

**Depends on:**
- `_SPEC_LANA_10-EvalSuite.md [LANATEST-SP01]` for requirements (FR, IG, NFR)
- `_IMPL_LANA_10-EvalSuite.md [LANATEST-IP01]` for implementation structure, edge cases, and TC definitions (TC-01..04)

## MUST-NOT-FORGET

- IP01 owns unit/integration cases (LANATEST-IP01-TC-01..04); this plan owns the verification contract and live scenarios
- Offline drives use `--scripted <script.jsonl>` - zero API calls, deterministic (DC-07)
- No API keys in run records (NFR-03): secret-leak scan after each test is mandatory
- Golden output is a rubric ANCHOR, never a diff target (CSRCMP-IN10)
- Tier 1 and Tier 2 evaluation MUST be deterministic: same run record -> same scores
- Live runs cost real money - run only with [ACTOR] approval

## Table of Contents

1. [Test Strategy](#1-test-strategy)
2. [Test Fixtures](#2-test-fixtures)
3. [Test Cases](#3-test-cases)
4. [Test Phases](#4-test-phases)
5. [Verification Checklist](#5-verification-checklist)
6. [Document History](#6-document-history)

## 1. Test Strategy

Two layers:

- **Layer 1 (offline)**: Scripted adapter drives - runner creates real run records, evaluators score them deterministically, no API keys needed. Validates PASS and FAIL detection paths. 4 core tests + 2 supplementary.
- **Layer 2 (live)**: Real agent runs with budget cap - validates end-to-end quality on actual LLM output, including Tier 3 judge. User-approved spend.

## 2. Test Fixtures

**Offline drives:**
```python
# Drive scripts in evals/suite/runner/drive-scripts/
# t01_pass.jsonl - scripted adapter that creates T01's expected file correctly
# t01_fail.jsonl - scripted adapter that creates wrong filename (sabotage)
# Runner invoked: python run_evals.py --scope 01-T01 --scripted drive-scripts/t01_pass.jsonl
```

**Live runs:**
- Real `lana` binary or dev install with API keys configured
- `LANA_CONFIG` pointing to workspace config (external to test workspace per IG-01)

## 3. Test Cases

IP01 test cases TC-01..04 are the authoritative definitions. This plan maps them to verification layers and adds live scenarios.

### Category 1: Offline scripted drives (4 core tests)

- **LANATEST-TP01-TC-01**: 01-T01 scripted PASS drive -> exit 0, Tier 1 = 1.0, Tier 2 = 1.0, status `pass` in results.json (IP01-TC-01, FR-05/FR-06)
- **LANATEST-TP01-TC-02**: 01-T01 sabotaged script (wrong filename) -> Tier 1 < 1.0, status `fail`, violated expectation named in REPORT.md (IP01-TC-02, FR-05/FR-06)
- **LANATEST-TP01-TC-03**: Record immutability - re-running same scope creates NEW timestamped folder, previous untouched (IP01-TC-03, IG-03)
- **LANATEST-TP01-TC-04**: Secret-leak scan - fake key value planted in scaffold output -> run aborts with CRITICAL (IP01-TC-04, EC-06, NFR-03)

### Category 2: Offline supplementary (2 tests)

- **LANATEST-TP01-TC-05**: Determinism check: run same PASS drive twice -> Tier 1 and Tier 2 scores identical to 2 decimal places (LANATEST-IG-02)
- **LANATEST-TP01-TC-06**: Missing manifest.yaml -> status INVALID, no agent spawned (EC-03, FR-02)

### Category 3: Live end-to-end (3 manual tests, user-approved spend)

- **LANATEST-TP01-TC-07**: Full suite live run (all 10 tests, real LLM) -> results.json with all tier scores, REPORT.md summary, cost totals reported (FR-05..08, NFR-02)
- **LANATEST-TP01-TC-08**: Single test with Tier 3 judge (03-T01 TranscribeLocal) -> judge/ audit trail complete (input.md, prompt.md, response.json, call.log), dimension scores in results.json (FR-08)
- **LANATEST-TP01-TC-09**: Run with `--skip-judge` flag -> Tier 3 scores null, Tier 1/2 still evaluated, no judge API call (runner flag behavior)

## 4. Test Phases

1. **Phase 1: Offline core** - TC-01..04 -- scripted drives, zero API calls
2. **Phase 2: Offline supplementary** - TC-05..06 -- determinism and validation edge cases
   - Gate: Phase 1 green
3. **Phase 3: Live single** - TC-08, TC-09 -- single test with judge, verify audit trail
   - Gate: Phase 2 green AND [ACTOR] approves spend (~$0.05 estimated per test)
4. **Phase 4: Live full** - TC-07 -- full suite
   - Gate: Phase 3 green AND [ACTOR] approves spend (~$1.00 estimated)

## 5. Verification Checklist

### Offline
- [x] **LANATEST-TP01-VC-01**: TC-01..04 verified via drive scripts (PASS + sabotage FAIL paths proven)
- [x] **LANATEST-TP01-VC-02**: TC-05 determinism check passed
- [x] **LANATEST-TP01-VC-03**: TC-06 INVALID path verified
- [x] **LANATEST-TP01-VC-04**: No key material in any offline run record (NFR-03 scan)

### Live (user-approved)
- [ ] **LANATEST-TP01-VC-05**: TC-07 full live run completed, results reviewed
- [ ] **LANATEST-TP01-VC-06**: TC-08 Tier 3 judge audit trail complete and reviewed
- [ ] **LANATEST-TP01-VC-07**: TC-09 --skip-judge behavior confirmed

### Coverage cross-check
- [x] **LANATEST-TP01-VC-08**: Every SP01 FR has at least one TC (FR-01..09 -> TC map above)
- [x] **LANATEST-TP01-VC-09**: Every SP01 IG has at least one TC (IG-01..04 -> TC-01/03/04/05)

## 6. Document History

**[2026-09-01 23:30]**
- Fixed: TC-07 test count 9 -> 10 (02-T04_SessionLoad added post-IMPL)
- Source: `/fact-check` + `/sync` against `evals/suite/` filesystem

**[2026-09-01 21:55]**
- Initial test plan created (spec restructure step 9)
