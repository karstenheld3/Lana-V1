# TEST: Lana Prompt and Configuration - Verification Plan

**Doc ID**: LANAPRCF-TP01
**Goal**: Define black-box CLI scenarios proving configuration loading, prompt system loading, and system prompt assembly satisfy LANAPRCF-SP01
**Timeline**: Created 2026-08-29, Extracted from _TEST_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `tests/test_config.py` (configuration unit tests)
- `tests/test_loader.py` (prompt system loading)
- `tests/test_prompt.py` (system prompt assembly)

**Depends on:**
- `_SPEC_LANA_03-PromptAndConfig.md [LANAPRCF-SP01]` for FR-01, FR-02, FR-03, IG-01
- `_IMPL_LANA_03-PromptAndConfig.md [LANAPRCF-IP01]` for IS-03, IS-04, IS-05, IS-25 and edge cases
- `_TEST_LANA_01-ProductOverview.md [LANAAGNT-TP01]` for test strategy, harness, and fixtures

**Does not depend on:**
- `_TEST_LANA_02-AgentCore.md [LANACORE-TP01]` (AgentCore tests consume config/prompt outputs but don't test them)

## MUST-NOT-FORGET

- Test workspaces are temp folders with their own `--config` - the real `config/lana-config.json` and IPPS are never written
- All scenario fixtures use generic content (Privacy Gate)

## Table of Contents

1. [Test Cases](#1-test-cases)
2. [Verification Checklist](#2-verification-checklist)
3. [Document History](#3-document-history)

## 1. Test Cases

Black-box scenarios (Layer 3) proving PromptAndConfig requirements. Unit/integration inventory in `_IMPL_LANA_03-PromptAndConfig.md [LANAPRCF-IP01]` section 3.

### Category 4: Real Prompt System Scenario (1 test)

- **LANAAGNT-TP01-TC-08**: IPPS startup + `/help` via pipe (skip if folder absent) -> banner reports filesystem-derived counts (8/46/21 at analysis; the folder evolves - counts computed at test time), `Keys:` line shows source per provider (`Environment variable:` or key file path with var name, FR-01), workflow list contains `prime` and `verify`, startup under 2 s (FR-02, NFR-03)

## 2. Verification Checklist

- [x] **LANAPRCF-TP01-VC-01**: TP01-TC-08 passes against real IPPS (skip if absent)
- [x] **LANAPRCF-TP01-VC-02**: Coverage contract - FR-01, FR-02, FR-03, IG-01 each cited by at least one passing TC across IP01 Categories 1-3 and TP01-TC-08

## 3. Document History

**[2026-09-01 21:45]**
- Extracted from `_TEST_LANA_MVP-1.md [LANAAGNT-TP01]`: Category 4 (Real Prompt System Scenario)
- Content is verbatim from source with section renumbering and header block update only
