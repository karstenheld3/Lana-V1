# TEST: Lana Provider Adapters - Verification Plan

**Doc ID**: LANAPRVD-TP01
**Goal**: Define live smoke tests proving the OpenAI and Anthropic provider adapters satisfy LANAPRVD-SP01
**Timeline**: Created 2026-08-29, Extracted from _TEST_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `tests/test_adapters.py` (live-key smoke tests)

**Depends on:**
- `_SPEC_LANA_04-Providers.md [LANAPRVD-SP01]` for FR-06
- `_IMPL_LANA_04-Providers.md [LANAPRVD-IP01]` for IS-11, IS-12 and edge cases
- `_TEST_LANA_01-ProductOverview.md [LANAAGNT-TP01]` for test strategy (Layer 4 live smoke)

**Does not depend on:**
- `_TEST_LANA_02-AgentCore.md [LANACORE-TP01]` (AgentCore tests use scripted adapters, not live providers)

## MUST-NOT-FORGET

- Live-key tests auto-skipped when keys absent (pytest marker `live`)
- Budget cap: under $1 per full run [ASSUMED]

## Table of Contents

1. [Test Cases](#1-test-cases)
2. [Verification Checklist](#2-verification-checklist)
3. [Document History](#3-document-history)

## 1. Test Cases

Provider adapter tests are Layer 4 (live smoke). No black-box CLI scenarios -- adapters are verified via direct API round trips.

### Live Smoke (3 tests, auto-skipped when keys absent)

- **LANAAGNT-IP01-TC-40**: OpenAI Responses: 1 function call round trip on gpt-4.1-mini
- **LANAAGNT-IP01-TC-41**: Anthropic: tool round trip + `cache_read_input_tokens > 0` on call 2 (NFR-03)
- **LANAAGNT-IP01-TC-42**: OpenAI reasoning model (gpt-5.x, effort medium): tool call works on Responses (RF-01 regression)

## 2. Verification Checklist

- [x] **LANAPRVD-TP01-VC-01**: T3 live smoke green with keys; spend under budget cap
- [x] **LANAPRVD-TP01-VC-02**: Coverage contract - FR-06 cited by TC-40, TC-41, TC-42; NFR-03 cache hit by TC-41

## 3. Document History

**[2026-09-01 21:45]**
- Extracted from `_TEST_LANA_MVP-1.md [LANAAGNT-TP01]`: Provider adapter smoke tests from Category 7
- Content is verbatim from source with section renumbering and header block update only
