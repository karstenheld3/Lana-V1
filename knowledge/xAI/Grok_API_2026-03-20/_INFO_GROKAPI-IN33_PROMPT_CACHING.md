# INFO: Prompt Caching

**Doc ID**: GROKAPI-IN33
**Goal**: How caching works, maximizing cache hits, conv-id header, cache key, what breaks caching
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Prompt caching automatically reduces costs by reusing previously computed prompt tokens. Cached prompt tokens are billed at a discounted rate. Caching is enabled by default - no opt-in required. Cache hits require the prompt prefix to be identical to a previous request. Two mechanisms to maximize cache hits: `x-grok-conv-id` header (Chat Completions API) and `prompt_cache_key` parameter (Responses API). Cache is broken by editing, removing, or reordering messages in the conversation prefix. For Chat Completions, use a consistent conversation ID via `x-grok-conv-id` header to ensure requests route to the same cache. For Responses API, use `prompt_cache_key` string. Cached tokens tracked in `usage.prompt_tokens_details.cached_tokens`. Multi-turn conversations benefit heavily from caching since earlier messages are identical across turns. [VERIFIED] (GROKAPI-SC-XAI-CACHING | https://docs.x.ai/developers/advanced-api-usage/prompt-caching/how-it-works)

## Key Facts

- [VERIFIED] Automatic - no opt-in required (GROKAPI-SC-XAI-CACHING)
- [VERIFIED] Cached tokens at discounted rate (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Chat Completions: `x-grok-conv-id` header for cache routing (GROKAPI-SC-XAI-CACHING)
- [VERIFIED] Responses API: `prompt_cache_key` parameter (GROKAPI-SC-XAI-CACHING)
- [VERIFIED] Cache broken by editing/removing/reordering messages (GROKAPI-SC-XAI-CACHINGBREAKS)
- [VERIFIED] Prompt prefix must be identical for cache hit (GROKAPI-SC-XAI-CACHINGBREAKS)
- [VERIFIED] Tracked in `usage.prompt_tokens_details.cached_tokens` (GROKAPI-SC-XAI-RESTREF)

## Quick Reference

- **Chat Completions**: Set `x-grok-conv-id` header to consistent conversation ID
- **Responses API**: Set `prompt_cache_key` parameter
- **Tracking**: `usage.prompt_tokens_details.cached_tokens`
- **Pricing**: Cached tokens at ~25% of regular input token rate (model-dependent)

## What Breaks Caching

- Editing any message in the conversation prefix
- Removing a message from the prefix
- Reordering messages
- Changing system prompt
- Different model
- Different conversation ID / cache key

## Examples

### Chat Completions with Conversation ID

```python
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

conv_id = "my-session-12345"

# Turn 1
r1 = client.chat.completions.create(
    model="grok-4.20-beta-latest-non-reasoning",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
    ],
    extra_headers={"x-grok-conv-id": conv_id},
)
print(f"Cached tokens: {r1.usage.prompt_tokens_details.cached_tokens}")

# Turn 2 - prefix is identical, should get cache hit
r2 = client.chat.completions.create(
    model="grok-4.20-beta-latest-non-reasoning",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": r1.choices[0].message.content},
        {"role": "user", "content": "What about JavaScript?"},
    ],
    extra_headers={"x-grok-conv-id": conv_id},
)
print(f"Cached tokens: {r2.usage.prompt_tokens_details.cached_tokens}")
```

### Responses API with Cache Key

```python
r1 = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What is Python?"}],
    extra_body={"prompt_cache_key": "my-cache-key-123"},
)
```

## Differences from Other APIs

### vs OpenAI
- **Similar concept**: Both have automatic prompt caching
- **Different mechanism**: xAI uses `x-grok-conv-id` header and `prompt_cache_key`; OpenAI caches automatically by prefix
- **Cache key**: xAI has explicit cache key control; OpenAI is purely automatic

### vs Anthropic
- **Similar concept**: Anthropic has `cache_control` blocks for explicit caching
- **Different approach**: xAI caches automatically; Anthropic requires explicit `cache_control` markers
- **Pricing**: Both discount cached tokens

### vs Gemini
- **Similar**: Gemini has context caching with explicit cache creation
- **Different**: Gemini requires creating a cache object; xAI is automatic

## Sources

- GROKAPI-SC-XAI-CACHING | https://docs.x.ai/developers/advanced-api-usage/prompt-caching/how-it-works | Accessed: 2026-03-20
- GROKAPI-SC-XAI-CACHINGBREAKS | https://docs.x.ai/developers/advanced-api-usage/prompt-caching/multi-turn | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:35]**
- Initial document created with prompt caching reference, cache key mechanisms, and what breaks caching
