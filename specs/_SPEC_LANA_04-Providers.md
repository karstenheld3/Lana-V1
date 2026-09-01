# SPEC: Lana Provider Adapters

**Doc ID**: LANAPRVD-SP01
**Goal**: Specify the provider adapter layer translating canonical messages to OpenAI and Anthropic APIs
**Timeline**: Created 2026-08-29, Extracted from _SPEC_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `src/lana/providers/base.py` (adapter protocol)
- `src/lana/providers/openai_adapter.py` (OpenAI Responses API)
- `src/lana/providers/anthropic_adapter.py` (Anthropic Messages API)

**Depends on:**
- `_SPEC_LANA_03-PromptAndConfig.md [LANAPRCF-SP01]` for role/model configuration (DD-02, DD-16)
- `_SPEC_LANA_01-ProductOverview.md [LANAAGNT-SP01]` for domain objects (ProviderAdapter, ModelRole, ThinkingBlock)

**Does not depend on:**
- `_SPEC_LANA_02-AgentCore.md [LANACORE-SP01]` (AgentCore dispatches through adapters; adapters are stateless translators)

## Table of Contents

1. [Functional Requirements](#1-functional-requirements)
2. [Design Decisions](#2-design-decisions)
3. [Document History](#3-document-history)

## 1. Functional Requirements

**LANAAGNT-FR-06: Provider Adapters**
- Canonical internal message model covering: system prompt, user/assistant messages, tool calls, tool results, thinking blocks
- OpenAI adapter: Responses API, `reasoning_effort` for reasoning models, `temperature` for temperature models (per `model_id_startswith` method in the registry); reasoning items carried across turns within a tool loop (OQ-04; RV01 RF-01)
- Anthropic adapter: Messages API, `thinking` budget from effort mapping, thinking blocks resent in multi-turn tool use, `cache_control` breakpoints on the tool definitions block and the system prompt block (provider-defined prefix order applies) plus top-level automatic caching so growing conversation history is cache-read too (OQ-13; RV01 RF-07)
- Adapter selection by `provider` field of the resolved model in `model-registry.json` (OQ-03)

## 2. Design Decisions

**LANAAGNT-DD-01:** Single-model loop, no Brain (OQ-01). Rationale: the Brain/Generator interplay is [ASSUMED] even in the wire capture and cannot be copied; modern generators plan and call tools natively; a second model doubles latency and cost for unproven benefit. The ModelRole abstraction keeps the door open.

**LANAAGNT-DD-03:** Own thin adapter layer over the official `openai` and `anthropic` Python SDKs; no LiteLLM (OQ-03). Rationale: two providers is small N; a third-party abstraction adds a dependency, lags provider features, and obscures cache control.

**LANAAGNT-DD-04:** OpenAI adapter uses the Responses API (OQ-04, matches the INFO leaning; revised per `LANAAGNT-SP01-RV01` RF-01) [PROVEN - live round trips TC-40/TC-42 green 2026-08-30]. Rationale: gpt-5.4+ models do not support tool calling with `reasoning_effort` above `none` on Chat Completions (all are enabled generator candidates in the registry); reasoning items persist across turns only on Responses; 40-80% better cache utilization. Source: OpenAI migration guide, checked 2026-08-29.

## 3. Document History

**[2026-09-01 21:45]**
- Extracted from `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]`: FR-06, DD-01, DD-03, DD-04
- Content is verbatim from source with section renumbering and header block update only
