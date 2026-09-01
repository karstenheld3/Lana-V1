# TEST: Lana Tool System - Verification Plan

**Doc ID**: LANATOOL-TP01
**Goal**: Define black-box CLI scenarios proving tool behavior, edit enforcement, web research, and trajectory search satisfy LANATOOL-SP01
**Timeline**: Created 2026-08-29, Extracted from _TEST_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `tests/test_tools.py` (file/edit/shell/state tool tests)
- `tests/test_web_tools.py` (web research tools)
- `tests/test_trajectory.py` (trajectory search)

**Depends on:**
- `_SPEC_LANA_05-Tools.md [LANATOOL-SP01]` for FR-10, FR-11, FR-13, FR-15
- `_IMPL_LANA_05-Tools.md [LANATOOL-IP01]` for IS-06..10, IS-18, IS-23 and edge cases
- `_TEST_LANA_01-ProductOverview.md [LANAAGNT-TP01]` for test strategy, harness, and fixtures

**Does not depend on:**
- `_TEST_LANA_02-AgentCore.md [LANACORE-TP01]` (AgentCore tests drive tools indirectly; tool tests verify tool behavior directly)

## MUST-NOT-FORGET

- Tool definition diff test: every tool definition must match `LANAAGNT-IN02` verbatim outside substitution points
- All scenario fixtures use generic content (Privacy Gate)

## Table of Contents

1. [Test Cases](#1-test-cases)
2. [Verification Checklist](#2-verification-checklist)
3. [Document History](#3-document-history)

## 1. Test Cases

Black-box scenarios (Layer 3) proving Tool System requirements. Unit/integration inventory in `_IMPL_LANA_05-Tools.md [LANATOOL-IP01]` section 3.

### Category 5: Diagnostics Scenario (1 test)

- **LANAAGNT-TP01-TC-09**: `--debug` round trip - single-prompt session with `--debug` -> `.lana-data/logs/` contains request/response JSON; keys redacted (NFR-04); grep for key patterns returns zero matches (NFR-01)

### Category 5b: Web Research Scenario (1 test)

- **LANAAGNT-TP01-TC-10**: Web search end-to-end (skip if keys absent) - script triggers `search_web` -> 5-result format in `tool_call_finished` event; then `read_url_content` on first URL (auto-approved via `--policy turbo` for this benign read) -> chunk text non-empty; `view_content_chunk` on same `document_id` position 1 -> same text (FR-13, DD-19)

## 2. Verification Checklist

- [x] **LANATOOL-TP01-VC-01**: TP01-TC-09 and TC-10 pass (TC-10 skip if keys absent)
- [x] **LANATOOL-TP01-VC-02**: Coverage contract - FR-10 (via IP01 TC-16..25), FR-11 (via IP01 TC-19..22), FR-13 (via TP01-TC-10 + IP01 TC-43..45), FR-15 (via IP01 TC-61..63) each cited by passing TCs

## 3. Document History

**[2026-09-01 21:45]**
- Extracted from `_TEST_LANA_MVP-1.md [LANAAGNT-TP01]`: Categories 5 (Diagnostics) and 5b (Web Research)
- Content is verbatim from source with section renumbering and header block update only
