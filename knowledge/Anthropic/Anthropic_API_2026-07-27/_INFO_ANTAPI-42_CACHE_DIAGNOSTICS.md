# Cache Diagnostics

**Doc ID**: ANTAPI-IN42
**Goal**: Document cache diagnostics for debugging prompt caching misses
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-20_PROMPT_CACHING.md [ANTAPI-IN20]` for prompt caching mechanisms
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` for beta header usage

## Summary

Cache diagnostics (beta) helps debug why prompt caching misses occur. When enabled via the `cache-diagnosis-2026-04-07` beta header, the API response includes diagnostic information about cache hit/miss status for each cacheable block, including reasons for misses (e.g., content changed, TTL expired, token count below minimum). This complements the existing `cache_creation_input_tokens` and `cache_read_input_tokens` usage fields.

## Key Facts

- **Beta Header**: `cache-diagnosis-2026-04-07`
- **Purpose**: Diagnose why cache misses occur
- **Request Field**: `diagnostics.previous_message_id` - ID of previous message to compare against
- **Response Field**: `cache_miss_reason` explaining where cache prefix diverged
- **Prerequisite**: Prompt caching must be configured (cache_control blocks)
- **Status**: Beta

## Quick Reference

```python
import anthropic

client = anthropic.Anthropic()

# First request - establishes cache
first_response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are an expert assistant...",
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[{"role": "user", "content": "Hello"}],
    betas=["cache-diagnosis-2026-04-07"],
)

# Second request - diagnose cache behavior by referencing previous message
response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are an expert assistant...",
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[{"role": "user", "content": "Follow up question"}],
    diagnostics={"previous_message_id": first_response.id},
    betas=["cache-diagnosis-2026-04-07"],
)

# Check cache diagnostics in response
print(f"Cache creation tokens: {response.usage.cache_creation_input_tokens}")
print(f"Cache read tokens: {response.usage.cache_read_input_tokens}")
# cache_miss_reason explains where prefix diverged if cache missed
```

## Use Cases

- Debug unexpected cache misses in production
- Optimize cache breakpoint placement
- Verify caching is working as expected during development
- Identify content changes that invalidate cache

## Common Miss Reasons

- Content in cached prefix changed between requests
- TTL expired (5m or 1h)
- Token count below minimum cacheable threshold (1,024 for Opus/Sonnet, 2,048 for Haiku)
- Different model used between requests
- Thinking budget change invalidated cache for message blocks

## Gotchas and Quirks

- Cache diagnostics add minimal overhead to response
- Only useful when prompt caching is already configured
- Opus 4.7 uses a different tokenizer than 4.6; same text produces different token counts, affecting cache keys

## Related Endpoints

- `_INFO_ANTAPI-20_PROMPT_CACHING.md [ANTAPI-IN20]` - Prompt caching configuration
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` - Beta header configuration

## Sources

- ANTAPI-SC-ANTH-CACHDIAG - https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics - Cache diagnostics guide

## SDK Verification

2 client calls verified against `anthropic` SDK 0.120.0:
- `client.beta.messages.create` - OK (params: model, max_tokens, system, messages)

Note: `diagnostics` param and `betas` param are passed as keyword arguments. The `diagnostics={"previous_message_id": ...}` parameter may require `extra_body` if not yet in the SDK typed interface.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Initial documentation created from cache diagnostics guide and release notes
- Added: SDK verification section (2 calls verified against 0.104.0)
