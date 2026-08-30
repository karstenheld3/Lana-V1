# Rate Limits

**Doc ID**: OAIAPI-IN05
**Goal**: Document rate limit tiers, RPM/TPM, headers, project-level limits
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Rate limits are usage tier-based (Free through Tier 5), applied per model and per project. Limits include RPM (requests per minute), TPM (tokens per minute), IPM (images per minute for image models), and Batch queue limits. GPT-5.6 Sol/Terra/Luna are NOT available on the Free tier. Rate info returned in `x-ratelimit-*` response headers. Project-level rate limits can be configured via Admin API. [VERIFIED] (OAIAPI-SC-OAI-GRLMT, OAIAPI-SC-OAI-GLATEST)

## GPT-5.6 Rate Limits (Sol/Terra/Luna)

- **Free**: Not supported
- **Tier 1**: 500 RPM, 500K TPM
- **Tier 2**: 5,000 RPM, 1M TPM
- **Tier 3**: 5,000 RPM, 2M TPM
- **Tier 4**: 10,000 RPM, 4M TPM
- **Tier 5**: 15,000 RPM, 40M TPM

All three GPT-5.6 tiers (Sol, Terra, Luna) share the same rate limit structure. Pro mode (`reasoning.mode: "pro"`) does not consume additional RPM but may use more tokens per request.

## GPT-5.5 Rate Limits (DEPRECATED - removal 2026-12-11)

- **Free**: Not supported
- **Tier 1**: 500 RPM, 500K TPM
- **Tier 2**: 5,000 RPM, 1M TPM
- **Tier 3**: 5,000 RPM, 2M TPM
- **Tier 4**: 10,000 RPM, 4M TPM
- **Tier 5**: 15,000 RPM, 40M TPM

## GPT Image 2 Rate Limits

- **Free**: Not supported
- **Tier 1**: 100K TPM, 5 IPM
- **Tier 5**: 8M TPM, 250 IPM

## Key Facts

- **Limit types**: RPM (requests per minute), TPM (tokens per minute), IPM (images per minute) [VERIFIED] (OAIAPI-SC-OAI-GRLMT)
- **Scope**: Project-level, model-specific [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **Tiers**: Free, Tier 1-5 based on cumulative spend [VERIFIED] (OAIAPI-SC-OAI-GRLMT)
- **Headers**: Six `x-ratelimit-*` headers in responses [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **Error**: 429 Too Many Requests when exceeded [VERIFIED] (OAIAPI-SC-OAI-GERROR)
- **Batch bypass**: Batch API bypasses rate limits with 50% cost reduction [VERIFIED] (OAIAPI-SC-OAI-GRLMT)

## Usage Tiers

- **Free** ($0 spend) - Lowest RPM/TPM, limited model access, GPT-5.5 NOT available
- **Tier 1** ($5+ cumulative) - Basic production limits
- **Tier 2** ($50+ cumulative) - Higher production limits
- **Tier 3** ($100+ cumulative) - Large-scale production
- **Tier 4** ($250+ cumulative) - Enterprise-scale
- **Tier 5** ($1,000+ cumulative) - Highest available limits

## Model-Specific Limits

Different models have different rate limits within same tier:
- **Flagship models** (GPT-5.5): Lower TPM due to cost
- **Mini models** (GPT-5.4-mini): Higher TPM limits
- **Nano models** (GPT-5.4-nano): Highest TPM limits
- **Image models** (gpt-image-2): IPM limits apply

## Project-Level Rate Limiting

- Each project has separate limits
- Multiple projects = multiple sets of limits
- Usage doesn't share across projects
- Manage limits in project settings or via Admin API

## Rate Limit Headers

### Response Headers

```
x-ratelimit-limit-requests: 5000
x-ratelimit-remaining-requests: 4999
x-ratelimit-limit-tokens: 1000000
x-ratelimit-remaining-tokens: 999500
x-ratelimit-reset-requests: 12ms
x-ratelimit-reset-tokens: 30ms
```

- **x-ratelimit-limit-requests**: Maximum requests allowed per minute
- **x-ratelimit-limit-tokens**: Maximum tokens allowed per minute
- **x-ratelimit-remaining-requests**: Requests remaining in current window
- **x-ratelimit-remaining-tokens**: Tokens remaining in current window
- **x-ratelimit-reset-requests**: Time until request limit resets
- **x-ratelimit-reset-tokens**: Time until token limit resets

Format: Duration string (e.g., "60s", "2m30s", "12ms")

## Exceeding Rate Limits

```json
{
  "error": {
    "type": "rate_limit_error",
    "code": "rate_limit_exceeded",
    "message": "Rate limit reached for requests"
  }
}
```

Retry strategy (exponential backoff):
1. First retry: 1-2 seconds
2. Second retry: 2-4 seconds
3. Third retry: 4-8 seconds
4. Check `x-ratelimit-reset-*` headers for exact reset time

## Rate Limit Bypass

### Batch API

- No RPM/TPM limits during batch processing
- 50% cost reduction
- 24-hour completion window
- Use for large-scale processing jobs

## SDK Examples (Python)

### Basic Retry Logic

```python
from openai import OpenAI, RateLimitError
import time

client = OpenAI()

def call_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.responses.create(
                model="gpt-5.6-sol",
                input=prompt,
            )
        except RateLimitError as e:
            wait = 2 ** attempt
            print(f"Rate limited, waiting {wait}s...")
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

### Rate Limit Aware Client (Production)

```python
from openai import OpenAI, RateLimitError
import time
import logging

logger = logging.getLogger(__name__)

class RateLimitAwareClient:
    def __init__(self):
        self.client = OpenAI()
        self.max_retries = 5

    def call_with_backoff(self, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return self.client.chat.completions.create(**kwargs)

            except RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise

                wait_time = min(2 ** attempt, 60)  # Cap at 60s
                logger.warning(f"Rate limit hit, waiting {wait_time}s (attempt {attempt+1})")
                time.sleep(wait_time)

        raise Exception("Max retries exceeded")

# Usage
client = RateLimitAwareClient()
response = client.call_with_backoff(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Batch API for Rate Limit Bypass

```python
from openai import OpenAI
import json

client = OpenAI()

# Create batch file
batch_requests = []
for i in range(1000):
    batch_requests.append({
        "custom_id": f"request-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-5.5",
            "messages": [{"role": "user", "content": f"Task {i}"}]
        }
    })

# Upload batch file
with open("batch.jsonl", "w") as f:
    for req in batch_requests:
        f.write(json.dumps(req) + "\n")

batch_file = client.files.create(
    file=open("batch.jsonl", "rb"),
    purpose="batch"
)

# Create batch job (bypasses rate limits, 50% cheaper)
batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"
)

print(f"Batch created: {batch.id}")
```

## Best Practices

- Monitor headers proactively before hitting limits
- Implement exponential backoff with jitter
- Use Batch API for large jobs (50% cost reduction + no rate limits)
- Consider tier upgrades for higher limits
- Distribute load across projects if needed

## Limitations and Known Issues

- **Tier upgrades not instant**: May take time to reflect after spend [COMMUNITY]
- **Model limits vary**: No single published table of all model limits [COMMUNITY]
- **Burst limits undocumented**: Short burst behavior not fully documented [COMMUNITY]

## Gotchas and Quirks

- **Tokens counted both ways**: Both input AND output tokens count toward TPM [VERIFIED] (OAIAPI-SC-OAI-GRLMT)
- **Reset time approximate**: Reset headers show approximate time, not exact [COMMUNITY]
- **Project limits independent**: Cannot pool limits across projects [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **429 means rate OR quota**: Rate limit error covers both RPM/TPM limits AND quota exhaustion [VERIFIED] (OAIAPI-SC-OAI-GERROR)

## TypeScript Examples

### Client Setup and Basic Usage

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  organization: process.env.OPENAI_ORG_ID,
});

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Hello!",
});
console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-GRLMT - Rate limits guide
- OAIAPI-SC-OAI-ADMPRJ - Project administration
- OAIAPI-SC-OAI-OVERVIEW - API overview (headers)
- OAIAPI-SC-OAI-MGP55 - GPT-5.5 model page

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: GPT-5.6 Sol/Terra/Luna rate limits section
- Changed: GPT-5.5 marked deprecated in rate limits context
- Changed: Summary updated for GPT-5.6 as primary model
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 22:00]**
- Enriched: Full tier detail, headers explanation, production client, batch bypass, gotchas

**[2026-05-22 11:05]**
- Updated: GPT-5.5 and GPT Image 2 rate limits added
