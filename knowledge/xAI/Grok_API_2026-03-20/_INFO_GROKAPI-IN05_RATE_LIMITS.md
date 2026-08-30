# INFO: Consumption and Rate Limits

**Doc ID**: GROKAPI-IN05
**Goal**: Token consumption, rate limit tiers, checking usage, throttling strategies
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok API measures consumption in tokens - the basic unit for inference pricing. Tokens include text tokens, image prompt tokens, cached prompt tokens, and reasoning tokens. Rate limits are tier-based, determined by cumulative spend since January 1, 2026, with 7 tiers (Tier 1 at $0 default through Tier 6 at $5,000, plus Enterprise). Tiers unlock automatically and never downgrade. Each tier sets hard RPM (requests per minute) and TPM (tokens per minute) limits per model. Exceeding limits returns HTTP 429. Rate limit tiers only apply to text models; Voice and Imagine APIs require manual rate limit increase requests. Actual consumption is reflected in the `usage` object in API responses and in the Usage Explorer on xAI Console. A tokenizer is available both in the Console and via the `POST /v1/tokenize-text` API endpoint. Cached prompt tokens are automatically enabled and reduce costs on repeated prompts. [VERIFIED] (GROKAPI-SC-XAI-RATELIMITS | https://docs.x.ai/developers/rate-limits)

## Key Facts

- [VERIFIED] Tiers: 1 ($0), 2 ($50), 3 ($200), 4 ($500), 5 ($1,000), 6 ($5,000), Enterprise (on request) (GROKAPI-SC-XAI-RATELIMITS)
- [VERIFIED] Tiers based on cumulative spend since Jan 1, 2026 (prepaid credits or fulfilled invoices) (GROKAPI-SC-XAI-RATELIMITS)
- [VERIFIED] Tiers are permanent - never downgrade even if spending decreases (GROKAPI-SC-XAI-RATELIMITS)
- [VERIFIED] Rate limits are per-model RPM and TPM (GROKAPI-SC-XAI-RATELIMITS)
- [VERIFIED] Exceeding limits returns 429 Too Many Requests (GROKAPI-SC-XAI-RATELIMITS)
- [VERIFIED] Rate limit tiers only apply to text models (GROKAPI-SC-XAI-RATELIMITS)
- [VERIFIED] Voice and Imagine API rate limits require email request (GROKAPI-SC-XAI-RATELIMITS)
- [VERIFIED] Custom per-model or team-level overrides take precedence over automatic tier (GROKAPI-SC-XAI-RATELIMITS)
- [VERIFIED] Full availability not guaranteed during peak system load (GROKAPI-SC-XAI-RATELIMITS)

## Quick Reference

### Tier Thresholds

- **Tier 1**: $0 (default for all new accounts)
- **Tier 2**: $50 cumulative spend
- **Tier 3**: $200
- **Tier 4**: $500
- **Tier 5**: $1,000
- **Tier 6**: $5,000
- **Enterprise**: Available on request

### Token Types

- **Input tokens (prompt_tokens)**: Query and conversation history
- **Reasoning tokens**: Agent's internal thinking and planning
- **Completion tokens**: Final response
- **Image tokens (prompt_image_tokens)**: Visual content analysis
- **Cached prompt tokens**: Prompt tokens served from cache (discounted)

## Checking Consumption

### From API Response

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What is 2+2?"}],
)

usage = response.usage
print(f"Prompt tokens: {usage.prompt_tokens}")
print(f"Completion tokens: {usage.completion_tokens}")
print(f"Total tokens: {usage.total_tokens}")
print(f"Cached tokens: {usage.prompt_tokens_details.cached_tokens}")
print(f"Reasoning tokens: {usage.completion_tokens_details.reasoning_tokens}")
```

### Usage Object Schema

```json
{
  "usage": {
    "prompt_tokens": 32,
    "completion_tokens": 9,
    "total_tokens": 135,
    "prompt_tokens_details": {
      "text_tokens": 32,
      "audio_tokens": 0,
      "image_tokens": 0,
      "cached_tokens": 6
    },
    "completion_tokens_details": {
      "reasoning_tokens": 94,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    },
    "num_sources_used": 0
  }
}
```

### Tokenize Text Endpoint

```python
import os
import requests

response = requests.post(
    "https://api.x.ai/v1/tokenize-text",
    headers={
        "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}",
        "Content-Type": "application/json",
    },
    json={"text": "Hello world!", "model": "grok-4-0709"},
)

tokens = response.json()["token_ids"]
print(f"Token count: {len(tokens)}")
```

### Console Tools

- **Usage Explorer**: https://console.x.ai (filter by model, date, team)
- **Tokenizer**: https://console.x.ai/team/default/tokenizer
- **Rate Limits page**: https://console.x.ai/team/default/rate-limits

## Rate Limit Handling

```python
import time
import random
from openai import OpenAI, RateLimitError

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

def call_with_backoff(messages, max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.responses.create(
                model="grok-4.20-beta-latest-non-reasoning",
                input=messages,
            )
        except RateLimitError:
            wait = min(60, (2 ** attempt) + random.uniform(0, 1))
            print(f"Rate limited. Waiting {wait:.1f}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)
    raise Exception(f"Failed after {max_retries} retries")
```

## Differences from Other APIs

### vs OpenAI

- **Same tier concept**: Both use spend-based tiers with automatic upgrades
- **Same usage object**: Compatible `usage` response structure with `prompt_tokens`, `completion_tokens`
- **Permanent tiers**: xAI tiers never downgrade; OpenAI tiers can change
- **Additional fields**: xAI includes `num_sources_used` in usage (for tool-using requests)
- **Tokenize endpoint**: xAI has `POST /v1/tokenize-text`; OpenAI uses tiktoken library

### vs Anthropic

- **Different tier structure**: xAI uses spend-based ($0-$5000); Anthropic uses usage-based tiers
- **Rate limit units**: Both use RPM and TPM per model
- **Usage object**: Different format - xAI is OpenAI-compatible; Anthropic uses `input_tokens`/`output_tokens`

### vs Gemini

- **Different model**: Gemini uses per-model RPM/RPD/TPM; xAI uses tier-based per-model RPM/TPM
- **Free tier**: Gemini has generous free tier; xAI requires prepaid credits

## Limitations and Known Issues

- [VERIFIED] Full availability not guaranteed during peak system load even within tier limits (GROKAPI-SC-XAI-RATELIMITS)
- [VERIFIED] Voice and Imagine API limits not covered by automatic tier system (GROKAPI-SC-XAI-RATELIMITS)

## Sources

- GROKAPI-SC-XAI-RATELIMITS | https://docs.x.ai/developers/rate-limits | Accessed: 2026-03-20
- GROKAPI-SC-XAI-RESTREF | https://docs.x.ai/llms.txt | Accessed: 2026-03-20

## Document History

**[2026-03-20 03:25]**
- Initial document created with tier structure, consumption tracking, and rate limit handling
