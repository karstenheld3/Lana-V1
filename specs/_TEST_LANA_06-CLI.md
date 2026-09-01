# TEST: Lana CLI Frontend - Verification Plan

**Doc ID**: LANACLI-TP01
**Goal**: Define black-box CLI scenarios proving the CLI frontend, headless mode, prompt queue, cost tracking, and zero-setup satisfy LANACLI-SP01
**Timeline**: Created 2026-08-29, Extracted from _TEST_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `tests/test_cli.py` (CLI harness scenarios)
- `tests/test_cost.py` (cost engine)
- `tests/test_hardening.py` (zero-setup and resilience)

**Depends on:**
- `_SPEC_LANA_06-CLI.md [LANACLI-SP01]` for FR-09, FR-14, FR-16, LANAACPB-FR-12, DD-20, DD-24
- `_IMPL_LANA_06-CLI.md [LANACLI-IP01]` for IS-15, IS-16, IS-21, IS-22 and hardening steps
- `_TEST_LANA_01-ProductOverview.md [LANAAGNT-TP01]` for test strategy, harness, and fixtures

**Does not depend on:**
- `_TEST_LANA_11-Selftest.md [LANASTST-TP01]` (selftest is a separate component)

## MUST-NOT-FORGET

- Every black-box scenario runs the REAL `lana` executable via `tests/harness.py` - no in-process shortcuts
- `assert_no_secret_leak` wired into every black-box scenario (NFR-01)
- All scenario fixtures use generic content (Privacy Gate)

## Table of Contents

1. [Test Cases](#1-test-cases)
2. [Verification Checklist](#2-verification-checklist)
3. [Document History](#3-document-history)

## 1. Test Cases

Black-box scenarios (Layer 3) proving CLI Frontend requirements. Unit/integration inventory in `_IMPL_LANA_06-CLI.md [LANACLI-IP01]` section 2.

### Category 5c: Headless Provider Failure Scenario (1 test)

- **LANAAGNT-TP01-TC-10b**: Provider failure headless - scripted adapter with `{"error": "simulated 500"}` -> exit 3, stderr contains self-contained error, session file survives for --resume (FR-14, FR-16 resilience)

### Category 7: Prompt Queue Scenario (1 test)

- **LANAAGNT-TP01-TC-PQ-01**: Prompt queue end-to-end - `lana --prompt-file <test_queue.md>` with 2-prompt queue and scripted adapter -> 2 `prompt_step` events in session JSONL (index 1/2, total 2), 2 `turn_finished` events, exit 0; malformed file (unclosed fence) -> exit 2 with rule-naming stderr message (LANAACPB-FR-12)

## 2. Verification Checklist

- [x] **LANACLI-TP01-VC-01**: TP01 scenarios pass (TC-10b, TC-PQ-01)
- [x] **LANACLI-TP01-VC-02**: Coverage contract - FR-09 (via IP01 TC-48..49), FR-14 (via IP01 TC-50..55 + TP01-TC-10b), FR-16 (via IP02 TC-01..16), LANAACPB-FR-12 (via TP01-TC-PQ-01) each cited by passing TCs
- [x] **LANACLI-TP01-VC-03**: `assert_no_secret_leak` wired into every black-box scenario (NFR-01)

## 3. Document History

**[2026-09-01 21:45]**
- Extracted from `_TEST_LANA_MVP-1.md [LANAAGNT-TP01]`: Provider failure scenario
- Added: Prompt queue scenario for LANAACPB-FR-12 (absorbed from MVP-2)
- Content is verbatim from source with section renumbering and header block update only
