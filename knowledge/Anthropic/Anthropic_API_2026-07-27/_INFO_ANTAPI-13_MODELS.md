# Models API

**Doc ID**: ANTAPI-IN13
**Goal**: Document GET /v1/models endpoints for model discovery and capability information
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL, auth headers

## Summary

The Models API provides two endpoints for discovering available Claude models and their capabilities. `GET /v1/models` lists all models (most recent first) with pagination support. `GET /v1/models/{model_id}` retrieves detailed information including `max_input_tokens`, `max_tokens` (output limit), and a `capabilities` object covering thinking, vision, PDF, citations, batch, code execution, structured output, and effort levels. As of March 2026, capability fields are returned directly on the model response. The model lineup now includes five tiers: Mythos-class (Fable 5, Mythos 5), Opus-class (Opus 5, 4.8, 4.7, 4.6), Sonnet-class (Sonnet 5, 4.6), and Haiku-class (Haiku 4.5). Fast mode is available on Opus 5 and Opus 4.8 at 2x base pricing.

## Key Facts

- **List Endpoint**: `GET /v1/models`
- **Get Endpoint**: `GET /v1/models/{model_id}`
- **SDK Methods**: `client.models.list()`, `client.models.retrieve(model_id)`
- **Pagination**: Cursor-based (after_id, before_id, limit)
- **Default Limit**: 20 items per page (range: 1-1000)
- **Sort Order**: Most recently released first
- **Status**: GA

## Endpoints

### GET /v1/models - List Models

**Query Parameters:**

- **after_id** (`string`, optional) - Cursor for forward pagination
- **before_id** (`string`, optional) - Cursor for backward pagination
- **limit** (`integer`, default: `20`, range: 1-1000) - Items per page

```python
import anthropic

client = anthropic.Anthropic()

# List all models
models = client.models.list()
for model in models:
    print(f"{model.id}: {model.display_name}")
    print(f"  Context: {model.max_input_tokens} tokens")
    print(f"  Max output: {model.max_output_tokens} tokens")
```

### GET /v1/models/{model_id} - Get Model

```python
import anthropic

client = anthropic.Anthropic()

model = client.models.retrieve("claude-opus-5")
print(f"Name: {model.display_name}")
print(f"Context window: {model.max_input_tokens}")
print(f"Max output: {model.max_output_tokens}")
print(f"Released: {model.created_at}")

# Check capabilities
caps = model.capabilities
print(f"Thinking: {caps.thinking.supported}")
print(f"Vision: {caps.vision.supported}")
print(f"PDF: {caps.pdf.supported}")
print(f"Citations: {caps.citations.supported}")
print(f"Batch: {caps.batch.supported}")
print(f"Code execution: {caps.code_execution.supported}")
print(f"Structured output: {caps.structured_output.supported}")
```

## ModelInfo Response

- **id** (`string`) - Model identifier (e.g., `"claude-opus-5"`)
- **type** (`string`) - Object type
- **display_name** (`string`) - Human-readable name
- **created_at** (`string`) - RFC 3339 release datetime
- **max_input_tokens** (`integer`) - Maximum input context window in tokens
- **max_output_tokens** (`integer`) - Maximum value for `max_tokens` parameter
- **capabilities** (`ModelCapabilities`) - Model capability information:
  - **batch** (`CapabilitySupport`) - Batch API support
  - **citations** (`CapabilitySupport`) - Citation generation support
  - **code_execution** (`CapabilitySupport`) - Code execution tool support
  - **context_management** (`ContextManagementCapability`) - Compaction/editing strategies
  - **vision** (`CapabilitySupport`) - Image content block support
  - **pdf** (`CapabilitySupport`) - PDF content block support
  - **structured_output** (`CapabilitySupport`) - JSON mode / strict schemas
  - **thinking** (`ThinkingCapability`) - Extended thinking support
    - **types** (`ThinkingTypes`) - Supported configs (adaptive, enabled)
  - **effort** (`EffortCapability`) - Effort levels (low, medium, high, xhigh, max)

## Available Models (as of 2026-07-26)

**Mythos-class (frontier):**
- **claude-fable-5** - Mythos-class with safety classifiers, $10/$50 MTok, 1M context, 128k output, adaptive thinking only, 30-day data retention required. Refusals fall back to Opus 4.8 via `fallbacks` parameter.
- **claude-mythos-5** - Same model as Fable 5 without safeguards, restricted to Project Glasswing partners

**Opus-class:**
- **claude-opus-5** - State-of-the-art for coding/knowledge work, $5/$25 MTok, 1M context, 128k output, thinking on by default, effort is primary control (low/medium/high/xhigh/max), fast mode at 2.5x speed
- **claude-opus-4-8** - Previous frontier, $5/$25 MTok, 1M context, 128k output, mid-conversation system messages, fast mode available
- **claude-opus-5** - 1M context, 128k output, fast mode removed Jul 24
- **claude-opus-4-6** - 1M context, fast mode removed Jun 29

**Sonnet-class:**
- **claude-sonnet-5** - Most agentic Sonnet, $2/$10 intro thru Aug 31 then $3/$15, 1M context, 128k output, new tokenizer (~30% more tokens), adaptive thinking default. Priority Tier not available.
- **claude-sonnet-4-6** - Best speed/intelligence ratio, 1M context GA

**Haiku-class:**
- **claude-haiku-4-5-20251001** - Fastest model with near-frontier intelligence

**Deprecated:**
- **claude-opus-4-1-20250805** - Deprecated Jun 5, retiring Aug 5, 2026. Migrate to claude-opus-4-8
- **claude-mythos-preview** - Deprecated, migrate to claude-mythos-5

**Retired:**
- **claude-sonnet-4-20250514** - Retired Jun 15, 2026
- **claude-opus-4-20250514** - Retired Jun 15, 2026
- **claude-3-haiku-20240307** - Retired April 20, 2026

**1M Context Window:** GA on all active models (Fable 5, Mythos 5, Opus 5, 4.8, 4.7, 4.6, Sonnet 5, 4.6).

**300k Output Tokens:** On Batch API for Opus and Sonnet models via `output-300k-2026-03-24` beta header.

**Fast Mode:** Available on Opus 5 and Opus 4.8. Removed from Opus 4.7 (Jul 24) and Opus 4.6 (Jun 29).

## Gotchas and Quirks

- Model IDs use dateless format from 4.6+ (e.g., `claude-opus-5`, `claude-sonnet-5`); each maps to one fixed snapshot
- Pre-4.6 convenience aliases (`claude-opus-4`, `claude-sonnet-4`) now return errors (retired Jun 15)
- Fable 5 and Sonnet 5 use an updated tokenizer: same text produces ~30% more tokens than pre-4.7 models
- On Opus 4.7+ and Sonnet 5, setting `temperature`, `top_p`, or `top_k` to non-default values returns 400
- On Opus 5, disabling thinking at `xhigh` or `max` effort returns 400
- On Fable 5/Mythos 5, `thinking: {"type": "disabled"}` and manual budget are not supported (400 error)
- Fable 5 requires 30-day data retention; not available under zero data retention
- The `created_at` field may be set to epoch value if release date is unknown
- Models are listed most recent first; use pagination for older models
- Beta models are available via `client.beta.models.list()` with additional beta-specific capabilities

## Related Endpoints

- `_INFO_ANTAPI-14_PRICING.md [ANTAPI-IN14]` - Token pricing per model
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` - Messages API (model parameter)

## Sources

- ANTAPI-SC-ANTH-MODLST - https://platform.claude.com/docs/en/api/models/list - List models endpoint
- ANTAPI-SC-ANTH-MODGET - https://platform.claude.com/docs/en/api/models/retrieve - Get model endpoint
- ANTAPI-SC-ANTH-MODOVW - https://platform.claude.com/docs/en/about-claude/models/overview - Models overview

## SDK Verification

Examples updated for `anthropic` SDK 0.120.0. Pending re-verification in Prompt 3.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: Claude Opus 4.8 (May 28), Fable 5 (Jun 9), Mythos 5 (Jun 9), Sonnet 5 (Jun 30), Opus 5 (Jul 24)
- Added: Model tiers (Mythos-class, Opus-class, Sonnet-class, Haiku-class)
- Added: Fast mode availability (Opus 5, 4.8 only), effort xhigh level
- Changed: Deprecation/retirement status updated (Opus 4, Sonnet 4, Opus 4.1, Mythos Preview)
- Changed: Gotchas updated for breaking changes (sampling params, thinking restrictions, tokenizer)

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Available models list updated (Opus 4.7 as top, Mythos Preview, deprecations)
- Added: 300k output tokens on Batch API, 1M context GA status
- Added: Capability fields returned directly on model response (March 2026 update)

**[2026-03-20 06:50]**
- Added: SDK verification section (anthropic 0.120.0, all 2 examples valid)

**[2026-03-20 02:55]**
- Initial documentation created from Models API reference
