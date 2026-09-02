# IMPL: Lana Provider Adapters

**Doc ID**: LANAPRVD-IP01
**Goal**: Implement the OpenAI and Anthropic provider adapters per LANAPRVD-SP01
**Timeline**: Created 2026-08-29, Extracted from _IMPL_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `src/lana/providers/__init__.py` (get_adapter via registry provider field)
- `src/lana/providers/base.py` (ProviderAdapter protocol)
- `src/lana/providers/openai_adapter.py` (Responses API adapter)
- `src/lana/providers/anthropic_adapter.py` (Messages API adapter)

**Depends on:**
- `_SPEC_LANA_04-Providers.md [LANAPRVD-SP01]` for FR-06, DD-01, DD-03, DD-04
- `_IMPL_LANA_01-ProductOverview.md [LANAAGNT-IP01]` for IS-02 (canonical models/events)
- `_IMPL_LANA_03-PromptAndConfig.md [LANAPRCF-IP01]` for IS-03 (config loading provides role/model resolution)

**Does not depend on:**
- `_IMPL_LANA_02-AgentCore.md [LANACORE-IP01]` (AgentCore consumes adapter protocol)

## MUST-NOT-FORGET

- OpenAI = Responses API only (LANAAGNT-DD-04); Anthropic = Messages + cache_control + top-level automatic caching (LANAAGNT-FR-06)
- Small cycles: implement -> test -> green -> commit per phase; never proceed on red

## Table of Contents

1. [Edge Cases](#1-edge-cases)
2. [Implementation Steps](#2-implementation-steps)
3. [Test Cases](#3-test-cases)
4. [Verification Checklist](#4-verification-checklist)
5. [Document History](#5-document-history)

## 1. Edge Cases

- **LANAAGNT-IP01-EC-16**: Provider API error (429/5xx) -> SDK retries disabled (`max_retries=0`), Lana-owned retries (up to 2, delays 2s/8s, each announced as notice delta, FR-16 UX-03); final failure surfaces as `error` event with provider message, turn discarded like cancellation
- **LANAAGNT-IP01-EC-19**: `search_web` role model's provider tool unavailable -> tool error advising a different `websearch` model

## 2. Implementation Steps

### Phase D: Provider Adapters

### LANAAGNT-IP01-IS-11: Adapter protocol and OpenAI Responses adapter

**Location**: `providers/base.py`, `providers/openai_adapter.py`

**Action**: `base.py`: `stream_turn(system, tools, messages, role_params) -> AsyncIterator[AdapterDelta]` (text/thinking/tool_call/usage deltas) + `supports_web_search()`. OpenAI: canonical messages -> Responses `input` items; function tools; `reasoning_effort`/`temperature` per registry method; reasoning items stored as ThinkingBlock and resent next call; parse typed `output` array (message | reasoning | function_call)

**Note**: Never read only the first output item (typed array parsing per migration guide); `store: false`

### LANAAGNT-IP01-IS-12: Anthropic Messages adapter with caching

**Location**: `providers/anthropic_adapter.py`

**Action**: Canonical -> Messages: `tools` array with `cache_control` on last tool, `system` block with `cache_control`, top-level automatic caching for history (FR-06); `thinking` budget from effort mapping; thinking blocks resent in tool-use turns; usage fields captured incl. `cache_read_input_tokens`

**Note**: Deterministic tool serialization (IS-06) is a cache-hit precondition; smoke test asserts `cache_read_input_tokens > 0` on call 2 (NFR-03)

## 3. Test Cases

### Category 7: Adapters (3 tests, live-key smoke, skipped in CI)

- **LANAAGNT-IP01-TC-40**: OpenAI Responses: 1 function call round trip on gpt-4.1-mini
- **LANAAGNT-IP01-TC-41**: Anthropic: tool round trip + `cache_read_input_tokens > 0` on call 2 (NFR-03)
- **LANAAGNT-IP01-TC-42**: OpenAI reasoning model (gpt-5.x, effort medium): tool call works on Responses (RF-01 regression)

## 4. Verification Checklist

- [x] **LANAPRVD-IP01-VC-01**: LANAPRVD-SP01 re-read; 1 FR, 3 DDs accounted for
- [x] **LANAPRVD-IP01-VC-02**: Phase D green (TC-40..42 with live keys)
- [x] **LANAPRVD-IP01-VC-03**: Anthropic cache-read tokens verified on call 2 (NFR-03)

## 5. Document History

**[2026-09-01 22:00]**
- Fixed: EC-16 "SDK default retries" -> "SDK retries disabled, Lana-owned retries" (synced from `base.py` `RETRY_DELAYS_SECONDS` and adapters `max_retries=0`)
- Source: `/fact-check` + `/sync` against source code

**[2026-09-01 21:45]**
- Extracted from `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]`: IS-11 (OpenAI adapter), IS-12 (Anthropic adapter)
- Edge cases: EC-16, EC-19
- Test cases: Category 7 adapter tests (TC-40..42)
- Content is verbatim from source with section renumbering and header block update only
