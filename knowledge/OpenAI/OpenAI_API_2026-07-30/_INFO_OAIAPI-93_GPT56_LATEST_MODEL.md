# GPT-5.6 Latest Model Guide

**Doc ID**: OAIAPI-IN93
**Goal**: Document GPT-5.6 model family (Sol, Terra, Luna) capabilities, pricing, reasoning modes, and migration from GPT-5.5
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Overview

GPT-5.6 is OpenAI's flagship model family released 2026-07-09. It replaces GPT-5.5 as the recommended production model and introduces a three-tier architecture: Sol (frontier capability), Terra (balanced intelligence/cost), and Luna (efficient high-volume). The `gpt-5.6` alias routes to `gpt-5.6-sol`. All tiers support 1M token context windows.

GPT-5.6 introduces Programmatic Tool Calling (see IN94), Multi-Agent orchestration beta (see IN95), persisted reasoning across turns, Pro mode, and explicit prompt caching controls.

## Model Tiers

- **gpt-5.6-sol** - Deepest reasoning, frontier capability. Default for `gpt-5.6` alias.
- **gpt-5.6-terra** - Strong performance at lower price. Balanced everyday workloads.
- **gpt-5.6-luna** - Fastest and cheapest. Efficient, high-volume tasks.

All three tiers are self-serve via the API with no plan gating.

## Reasoning Effort

GPT-5.6 supports 6 reasoning effort levels:

- `none` - No reasoning, fastest
- `low` - Minimal reasoning
- `medium` - Default for standard and pro modes
- `high` - Extended reasoning
- `xhigh` - Deep exploration
- `max` - Maximum reasoning time, explores alternatives

Set via `reasoning.effort` in the Responses API:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-terra",
    input="Summarize the trade-offs between webhooks and polling.",
    reasoning={"effort": "low"},
)
print(response.output_text)
```

## Pro Mode

Pro mode applies more model work before returning a single final answer. Increases reliability on difficult tasks at the cost of latency. Tokens from that work are billed at standard rates.

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Analyze the implications of quantum error correction on cryptographic protocols.",
    reasoning={"mode": "pro", "effort": "high"},
)
print(response.output_text)
```

Pro mode is a setting (`reasoning.mode: "pro"`) on all three models, not a separate model slug.

## Persisted Reasoning

Reasoning context carries across turns via `reasoning.context`, so multi-turn agents do not rebuild their chain of thought from zero on every call:

```python
from openai import OpenAI

client = OpenAI()

# First turn
response1 = client.responses.create(
    model="gpt-5.6-sol",
    input="Design a REST API for a task management system.",
    reasoning={"effort": "high"},
)

# Second turn - reasoning persists via previous_response_id
response2 = client.responses.create(
    model="gpt-5.6-sol",
    input="Now add authentication to the design.",
    previous_response_id=response1.id,
    reasoning={"effort": "high", "context": "all_turns"},
)
print(response2.output_text)
```

## Explicit Prompt Caching

GPT-5.6 introduces explicit cache breakpoints and configurable TTL:

- `prompt_cache_retention: "explicit"` with `ttl` parameter
- Cache writes billed at 1.25x standard input rate
- Cache reads retain the 90% discount
- Cached content lives at least 30 minutes (minimum guarantee)

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"type": "message", "role": "developer", "content": [
            {"type": "input_text", "text": "You are a helpful assistant.", "prompt_cache_breakpoint": True}
        ]},
        {"type": "message", "role": "user", "content": "What is quantum computing?"},
    ],
    prompt_cache_options={"mode": "explicit", "ttl": "30m"},
    reasoning={"effort": "medium"},
)
print(response.output_text)
```

## Image Detail

GPT-5.6 accepts images at their original dimensions with `detail: "original"` or `detail: "auto"`:

- `original` - Process at native resolution
- `auto` - Model decides optimal resolution (default)
- `low` / `high` - Legacy fixed options still supported

## Migration from GPT-5.5

1. Replace model ID: `gpt-5.5` -> `gpt-5.6` (routes to Sol) or choose tier explicitly
2. Reasoning effort: GPT-5.6 defaults to `medium` (same as GPT-5.5)
3. Chat Completions: Code works with model ID swap, no forced rewrite
4. Responses API: Recommended for new builds (Programmatic Tool Calling, Multi-Agent, persisted reasoning all ship here)
5. GPT-5.5 deprecated 2026-06-11 with removal 2026-12-11 - migrate before then

## Gotchas and Quirks

- The `gpt-5.6` alias always routes to `gpt-5.6-sol` - use explicit tier IDs for cost control
- Pro mode increases latency significantly - benchmark before deploying in latency-sensitive paths
- Persisted reasoning (`reasoning.context`) is opaque - cannot inspect or modify between turns
- Explicit caching TTL minimum is 30 minutes regardless of configured value

## TypeScript Examples

### Basic Response

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Explain this concept briefly.",
});

console.log(response.output_text);
```

### With Instructions

```typescript
const response = await client.responses.create({
  model: "gpt-4o-mini",
  instructions: "You are a helpful assistant.",
  input: "What is 2+2?",
});

console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-GLATEST (Model guidance page, updated 2026-07)
- https://openai.com/index/gpt-5-6/ (Launch announcement)
- https://developers.openai.com/api/docs/guides/latest-model

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Initial documentation for GPT-5.6 model family
