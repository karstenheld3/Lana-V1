# Rate Limits

**Doc ID**: ANTAPI-IN36
**Goal**: Document rate limit types, tiers, headers, and handling strategies
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL, auth headers

## Summary

Anthropic enforces rate limits at three levels: requests per minute (RPM), input tokens per minute (ITPM), and output tokens per minute (OTPM). Limits are set per-model and per-workspace. As of June 26, 2026, usage tiers are consolidated into three named tiers: **Start**, **Build**, and **Scale**. Sonnet and Haiku limits now match Opus at every tier. Cache reads do not count toward ITPM. Fable 5 has lower limits than other models. Rate limit information is returned in response headers. When limits are exceeded, the API returns HTTP 429 with a `rate_limit_error`. The Rate Limits API (`GET /v1/organizations/rate_limits`) allows programmatic querying of configured limits (see `_INFO_ANTAPI-43_RATE_LIMITS_API.md [ANTAPI-IN43]`).

## Key Facts

- **Limit Types**: RPM, ITPM, OTPM
- **Scope**: Per-model, per-workspace (limits per model are independent)
- **HTTP Status**: 429 Too Many Requests
- **Error Type**: `rate_limit_error`
- **Headers**: `anthropic-ratelimit-*` in every response
- **Tiers**: Start ($500/mo cap), Build ($1K/mo cap), Scale ($200K/mo cap)
- **Cache reads**: Do not count toward ITPM (only uncached + cache writes count)
- **Status**: GA

## Rate Limit Headers

Every API response includes rate limit headers:

- **anthropic-ratelimit-requests-limit** - Max RPM for this model
- **anthropic-ratelimit-requests-remaining** - Remaining requests in current window
- **anthropic-ratelimit-requests-reset** - ISO 8601 time when request limit resets
- **anthropic-ratelimit-input-tokens-limit** - Max input TPM
- **anthropic-ratelimit-input-tokens-remaining** - Remaining input tokens
- **anthropic-ratelimit-input-tokens-reset** - Input token limit reset time
- **anthropic-ratelimit-output-tokens-limit** - Max output TPM
- **anthropic-ratelimit-output-tokens-remaining** - Remaining output tokens
- **anthropic-ratelimit-output-tokens-reset** - Output token limit reset time
- **retry-after** - Seconds to wait before retrying (on 429 responses)

## Handling Rate Limits

### Basic Retry with Backoff

```python
import anthropic
import time

client = anthropic.Anthropic()

def make_request_with_retry(messages, max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.messages.create(
                model="claude-opus-5",
                max_tokens=1024,
                messages=messages,
            )
        except anthropic.RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            retry_after = int(e.response.headers.get("retry-after", 30))
            print(f"Rate limited. Retrying in {retry_after}s...")
            time.sleep(retry_after)
```

### SDK Built-in Retry

The Python SDK automatically retries on 429 errors with exponential backoff:

```python
import anthropic

# SDK retries rate limit errors automatically (default: 2 retries)
client = anthropic.Anthropic(max_retries=3)

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

### Checking Remaining Capacity

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.with_raw_response.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)

headers = response.headers
print(f"RPM remaining: {headers.get('anthropic-ratelimit-requests-remaining')}")
print(f"Input TPM remaining: {headers.get('anthropic-ratelimit-input-tokens-remaining')}")
print(f"Output TPM remaining: {headers.get('anthropic-ratelimit-output-tokens-remaining')}")

message = response.parse()
```

## Usage Tiers (as of June 26, 2026)

Three named tiers with unified limits across Opus, Sonnet, and Haiku:

### Start (monthly spend cap: $500)

- **RPM**: 1,000
- **ITPM**: 2,000,000
- **OTPM**: 400,000

### Build (monthly spend cap: $1,000)

- **RPM**: 5,000
- **ITPM**: 5,000,000
- **OTPM**: 1,000,000

### Scale (monthly spend cap: $200,000)

- **RPM**: 10,000
- **ITPM**: 10,000,000
- **OTPM**: 2,000,000

### Fable 5 Limits (lower than other models)

- **Start**: 1,000 RPM / 500K ITPM / 100K OTPM
- **Build**: 2,000 RPM / 1.5M ITPM / 300K OTPM
- **Scale**: 4,000 RPM / 4M ITPM / 800K OTPM

Tier advancement is automatic and immediate based on cumulative API spend. No application needed. Spend caps reset monthly. Custom tier (negotiated) has no cap.

**Priority Tier**: No longer available for new purchase. Existing commitments run until contract end.

## Acceleration Limits

Sharp increases in usage can trigger 429 errors even within normal rate limits. Ramp up traffic gradually and maintain consistent usage patterns to avoid acceleration limit hits.

## Cache-Aware ITPM

Input token rate limits are cache-aware. Cached tokens consume less rate limit capacity than uncached tokens, allowing higher effective throughput when using prompt caching.

## Batch API Rate Limits

Message Batches API has separate limits (shared across all models):

- **HTTP request rate limits (RPM)** - For batch CRUD operations
- **Queued request limits** - Max batch requests in the processing queue simultaneously
- A batch request = one item within a Message Batch; a single batch with 1,000 items counts as 1,000 batch requests
- Processing may be slowed during high demand, causing more request expirations

## Fast Mode Rate Limits

Fast mode (`speed: "fast"` on Opus 5 and Opus 4.8) has dedicated rate limits separate from standard limits:

- Returns `anthropic-fast-*` headers indicating fast mode rate limit status
- 429 errors with `retry-after` header when exceeded
- Fast mode removed from Opus 4.7 (Jul 24) and Opus 4.6 (Jun 29)

## Gotchas and Quirks

- Rate limits are per-model AND per-workspace (not per-API-key); each model has independent buckets
- Cache reads do not count toward ITPM; only uncached input + cache write tokens count
- Sonnet/Haiku limits now match Opus at every tier (since Jun 26, 2026)
- The SDK auto-retries on 429 with exponential backoff by default
- `retry-after` header gives the recommended wait time in seconds
- Token limits apply to both input and output separately
- **Token bucket algorithm**: Capacity continuously replenishes up to max (not reset at fixed intervals)
- RPM may be enforced over shorter intervals (e.g., 60 RPM = 1 request/second; short bursts can trigger 429)
- Batch API can slightly exceed workspace spend limits due to concurrent processing
- Claude Platform on AWS organizations are placed on Start tier; no automatic tier advancement
- All limits are maximum allowed, not guaranteed minimums

## Related Endpoints

- `_INFO_ANTAPI-06_ERRORS.md [ANTAPI-IN06]` - Error types including rate_limit_error
- `_INFO_ANTAPI-12_BATCHES.md [ANTAPI-IN12]` - Batch API rate limits
- `_INFO_ANTAPI-14_PRICING.md [ANTAPI-IN14]` - Tier-based pricing and limits
- `_INFO_ANTAPI-43_RATE_LIMITS_API.md [ANTAPI-IN43]` - Programmatic rate limit querying

## Sources

- ANTAPI-SC-ANTH-RTLMT - https://platform.claude.com/docs/en/api/rate-limits - Rate limit documentation

## SDK Verification

Examples updated for `anthropic` SDK 0.120.0. Pending re-verification in Prompt 3.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Usage tiers consolidated to Start/Build/Scale with concrete RPM/ITPM/OTPM values
- Added: Unified limits across Opus/Sonnet/Haiku
- Added: Fable 5 separate (lower) limits
- Added: Cache reads excluded from ITPM
- Added: Priority Tier no longer available for new purchase
- Changed: Fast mode rate limits now Opus 5/4.8 only
- Changed: Model references to claude-opus-5

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references to claude-opus-5
- Added: Rate Limits API reference (IN41)
- Changed: Fast mode now also supports Opus 4.7

**[2026-03-20 07:00]**
- Added: SDK verification section (anthropic 0.120.0, all 3 examples valid)

**[2026-03-20 05:00]**
- Added: Spend limits and tiers, acceleration limits
- Added: Cache-aware ITPM, fast mode separate rate limits
- Added: Token bucket algorithm details, batch request counting clarification

**[2026-03-20 04:25]**
- Initial documentation created from rate limits guide
