# TEST: Selftest Framework

**Doc ID**: LANATEST-TP01
**Goal**: Verify the selftest framework meets all LANATEST-SP01 requirements -- offline via pytest, live via controlled selftest runs
**Timeline**: Created 2026-08-30

**Target file(s)**:
- `tests/test_selftest_script.py` (offline pytest)
- Live verification via `selftest.py` runs (manual phases, user-approved spend)

**Depends on:**
- `_SPEC_SELFTEST.md [LANATEST-SP01]` for requirements
- `_IMPL_SELFTEST.md [LANATEST-IP01]` for implementation structure and edge cases

## MUST-NOT-FORGET

- Offline tests never make API calls and never require keys
- Live phases cost real money -- run only with [ACTOR] approval, budget-capped
- Test the script as a module (importlib from skill path), not by shelling out where avoidable
- Never weaken existing tests -- `tests/test_adapters.py` live smokes stay untouched

## Table of Contents

1. [Overview](#1-overview)
2. [Scenario](#2-scenario)
3. [Test Strategy](#3-test-strategy)
4. [Test Priority Matrix](#4-test-priority-matrix)
5. [Test Data](#5-test-data)
6. [Test Cases](#6-test-cases)
7. [Test Phases](#7-test-phases)
8. [Helper Functions](#8-helper-functions)
9. [Cleanup](#9-cleanup)
10. [Verification Checklist](#10-verification-checklist)
11. [Document History](#11-document-history)

## 1. Overview

Two-layer verification of the selftest framework:
- **Layer 1 (offline, pytest)**: script logic -- menu, selection, discovery, offline categories, results, budget, exit codes. Runs in CI, no keys, no cost.
- **Layer 2 (live, manual)**: the selftest itself run against real APIs -- validates categories 04-06 end-to-end and doubles as the first real model validation (session goal).

## 2. Scenario

**Problem:** The selftest validates Lana installations -- if the selftest itself is broken (wrong filtering, silent crashes, corrupt results), it reports wrong health status or burns budget.

**Solution:** Offline pytest covers all decision logic deterministically; two controlled live runs prove the API-facing paths and produce the first full model validation report.

**What we don't want:**
- Live API calls inside pytest (existing `@pytest.mark.live` in `test_adapters.py` covers adapter smoke -- no duplication)
- Mock-heavy tests of `stream_turn` internals -- adapter correctness is owned by `test_adapters.py`
- Testing Lana's workflow-following behavior here -- that belongs in `evals/` (02_WorkflowsSkills bucket)

## 3. Test Strategy

**Approach**: unit + integration (offline), scripted end-to-end (live)

- Offline: import `selftest.py` via importlib, call functions directly with tmp-workspace fixtures from `tests/conftest.py`
- Offline integration: run `main(argv)` in-process against a tmp workspace for full-run behavior (results.json, exit codes)
- Live: run `selftest.py` as subprocess in the real workspace, small scope first (`--model gpt-5-nano`), then full `live`

## 4. Test Priority Matrix

### MUST TEST (Critical Business Logic)

- **`select_categories()`** - selftest.py
  - Testability: EASY, Effort: Low
  - Code parsing, `all|offline|live` groups, invalid code exit 2 (FR-02)
- **`discover_models()`** - selftest.py
  - Testability: EASY, Effort: Low
  - enabled/available/prefix/key filters, provider and model filters (FR-06, FR-11)
- **Budget precheck** - selftest.py
  - Testability: EASY, Effort: Low
  - Skip with `budget_exceeded` before overspend (FR-10, IG-01)
- **`write_results()` + exit codes** - selftest.py
  - Testability: EASY, Effort: Low
  - Valid JSON always, summary counts, exit 0/1 rule (FR-12, IG-03..05)
- **Offline categories 01-03** - selftest.py
  - Testability: Medium, Effort: Medium
  - Pass/fail per check, resilience to broken config (FR-03..05, EC-14)

### SHOULD TEST (Important Workflows)

- **Effort matrix selection** - selftest.py
  - Testability: Medium, Effort: Low
  - Cheapest-per-method choice, effort level derivation (FR-08)
- **Menu output** - selftest.py
  - Testability: EASY, Effort: Low
  - All categories with cost class (FR-01)
- **KeyboardInterrupt handling** - selftest.py
  - Testability: Medium, Effort: Medium
  - results.json written on interrupt (EC-06)

### DROP (Not Worth Testing Offline)

- **`run_model_turn()` against real APIs** - Reason: live-only by nature, covered by Layer 2 and existing TC-40..42
- **TLS endpoint reachability check** - Reason: network-dependent, flaky in CI; covered by Layer 2
- **Interpreter discovery in workflow** - Reason: agent-side markdown instruction, covered by evals-style manual check (Phase 4)

## 5. Test Data

**Required Fixtures:**
- Tmp workspace with config trio: reuse `write_config_dir()` from `tests/conftest.py`
- Registry fixture variants: model disabled, status untested, no prefix match, provider without key
- Prompt system fixture: `.lana/` with rules/workflows/skills, one workflow file, one skill folder (with and without SKILL.md)
- Env fixture: `monkeypatch` clears `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` for no-key scenarios

**Setup:**
```python
# Import once per session via importlib from .lana/skills/selftest/selftest.py
# Per test: tmp_path workspace + write_config_dir() + monkeypatch env
```

**Teardown:**
- pytest `tmp_path` auto-cleanup; no global state (script uses function-local context)

## 6. Test Cases

Offline cases TC-01..13 correspond 1:1 to `LANATEST-IP01-TC-01..13`; TC-17..19 supplement coverage gaps found during /verify. All offline cases implemented in `tests/test_selftest_script.py`:

### Category 1: Selection and menu (4 tests)

- **LANATEST-TP01-TC-01**: `--menu` lists codes 01-06 with cost class and estimates -> ok=true (FR-01)
- **LANATEST-TP01-TC-02**: codes `["04","01"]` -> selected `[01, 04]` ascending -> ok=true (FR-02)
- **LANATEST-TP01-TC-03**: `offline` -> 01-03, `live` -> 04-06, `all` -> 01-06 -> ok=true (FR-02)
- **LANATEST-TP01-TC-04**: code `99` -> ok=false, exit 2, message lists valid codes (EC-02)

### Category 2: Model discovery (3 tests)

- **LANATEST-TP01-TC-05**: fixture registry with disabled + untested models -> only enabled+available returned (FR-06)
- **LANATEST-TP01-TC-06**: model without prefix entry -> excluded with warning (EC-08)
- **LANATEST-TP01-TC-07**: no ANTHROPIC_API_KEY -> anthropic models status skip, openai unaffected (EC-01, IG-02)

### Category 3: Offline categories (3 tests)

- **LANATEST-TP01-TC-08**: valid tmp workspace -> category 02 all checks pass (FR-04)
- **LANATEST-TP01-TC-09**: pricing file deleted -> category 02 check fails, no exception, run continues (EC-14)
- **LANATEST-TP01-TC-10**: skill folder without SKILL.md -> category 03 fails naming the folder (FR-05)

### Category 4: Results, budget, exit codes (3 tests)

- **LANATEST-TP01-TC-11**: full offline run -> results.json valid JSON, summary counts match tests array (IG-04, IG-05)
- **LANATEST-TP01-TC-12**: budget precheck with remaining < $0.01 -> `budget_exceeded`, no API attempt (FR-10, IG-01)
- **LANATEST-TP01-TC-13**: one fail -> exit 1; only pass+skip -> exit 0 (IG-03)

### Category 5: Live end-to-end (3 manual cases, user-approved spend)

- **LANATEST-TP01-TC-14**: `selftest.py 04 --model gpt-5-nano --budget 0.10` -> pass, cost < $0.01, results.json entry complete (FR-07)
- **LANATEST-TP01-TC-15**: `selftest.py live --budget 1.00` -> categories 04-06 complete, all 20 models attempted, effort matrix covers 5 methods, tool calls pass (FR-07..09; validates NFR-02 estimates and closes LANATEST-PR-0001/PR-0002)
- **LANATEST-TP01-TC-16**: `/selftest` in Lana (menu flow) -> menu presented, selection executed, summary reported (FR-14)

### Category 6: Supplementary unit tests (3 tests)

- **LANATEST-TP01-TC-17**: category 01 offline checks (python version, lana version, data dir writable) pass in tmp workspace; endpoint checks excluded via injectable check list (FR-03)
- **LANATEST-TP01-TC-18**: `run_model_turn()` with stub adapter that stalls -> status fail with timeout message after configured 1s, next test proceeds (FR-13, EC-07)
- **LANATEST-TP01-TC-19**: effort matrix selection on fixture registry + pricing -> cheapest model per method chosen, effort levels derived from prefix array or low/medium/high default (FR-08)

## 7. Test Phases

1. **Phase 1: Offline unit** - TC-01..07 (selection, menu, discovery) -- pure functions, no filesystem beyond fixtures
2. **Phase 2: Offline integration** - TC-08..13, TC-17..19 (categories, results, exit codes, timeout stub, matrix selection) -- tmp workspace `main(argv)` runs
3. **Phase 3: Live smoke** - TC-14 single cheap model, verifies API path before spending on full run
4. **Phase 4: Live full + workflow** - TC-15 full live run, TC-16 `/selftest` menu flow in Lana
   - Gate: Phase 3 green AND [ACTOR] approves spend (~$0.35 estimated)

## 8. Helper Functions

```python
# tests/test_selftest_script.py
def load_selftest_module(): ...          # importlib from .lana/skills/selftest/selftest.py
def make_workspace(tmp_path, **mods): ...  # config trio + .lana skeleton, per-test variants
def run_main(module, argv, cwd): ...     # main(argv) with cwd switch, returns (exit_code, results_dict)
```

## 9. Cleanup

- pytest `tmp_path` fixtures: automatic
- Live runs: `.lana-data/selftest/<timestamp>/` folders are runtime artifacts -- keep latest, older removable via `/cleanup`
- `.tmp_verify_registry.py` (session temp script): delete after implementation verified

## 10. Verification Checklist

### Offline (pytest)
- [ ] **LANATEST-TP01-VC-01**: TC-01..13 and TC-17..19 implemented in `tests/test_selftest_script.py`
- [ ] **LANATEST-TP01-VC-02**: `pytest tests/test_selftest_script.py -q` green without API keys in env
- [ ] **LANATEST-TP01-VC-03**: Full offline suite `pytest -m "not live"` -- no new failures beyond deferred PR-0005

### Live (user-approved)
- [ ] **LANATEST-TP01-VC-04**: TC-14 live smoke green, cost reported
- [ ] **LANATEST-TP01-VC-05**: TC-15 full live run -- results reviewed, failing models recorded in PROBLEMS.md
- [ ] **LANATEST-TP01-VC-06**: TC-16 `/selftest` menu flow works in Lana
- [ ] **LANATEST-TP01-VC-07**: NFR-02 cost estimates compared against actuals, spec updated if off

### Coverage cross-check
- [ ] **LANATEST-TP01-VC-08**: Every SP01 FR has at least one TC (FR-01..14 -> TC map in sections 6)
- [ ] **LANATEST-TP01-VC-09**: Session goal met -- all available models tested, effort variants covered (PR-0001, PR-0002 closable)

## 11. Document History

**[2026-08-30 22:38]**
- Added: TC-17..19 closing coverage gaps found during /verify (FR-03 category 01, FR-13 timeout, FR-08 matrix selection)

**[2026-08-30 22:36]**
- Initial test plan created

