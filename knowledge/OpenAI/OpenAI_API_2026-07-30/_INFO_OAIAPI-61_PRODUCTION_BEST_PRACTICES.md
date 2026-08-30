# Production Best Practices

**Doc ID**: OAIAPI-IN61
**Goal**: Document production best practices for deploying OpenAI API applications - security, reliability, monitoring
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Production best practices cover security, reliability, cost management, and safety for OpenAI API deployments. Key areas: API key management (project-scoped keys, rotate regularly, never expose in client code), rate limit handling (exponential backoff with jitter), error handling (retry on 429, 500, 503), input sanitization, output validation, monitoring (track usage, latency, errors), cost control (spending limits, prompt caching, flex processing), safety (content moderation, structured outputs). API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-GBPRD)

## Key Facts

- **API key security**: Project-scoped keys, never in client code [VERIFIED] (OAIAPI-SC-OAI-GBPRD)
- **Rate limits**: Exponential backoff with jitter on 429 responses [VERIFIED] (OAIAPI-SC-OAI-GBPRD)
- **Error handling**: Retry on 429, 500, 503; don't retry 400, 401 [VERIFIED] (OAIAPI-SC-OAI-GBPRD)
- **Cost control**: max_completion_tokens, prompt caching, flex processing [VERIFIED] (OAIAPI-SC-OAI-GBPRD)
- **Safety**: Moderation API, input validation, output scope restriction [VERIFIED] (OAIAPI-SC-OAI-GBPRD)
- **Monitoring**: Track tokens, latency, errors, cost per request [VERIFIED] (OAIAPI-SC-OAI-GBPRD)

## Security Best Practices

- **Never expose API keys in client-side code** - use server-side proxy
- **Use project-scoped keys** - limit blast radius of key compromise
- **Rotate keys regularly** - create new, deploy, delete old
- **Use service accounts for automation** - not personal keys
- **Environment variables** - never hardcode keys in source code
- **mTLS** - enable for enterprise security requirements
- **Audit logs** - monitor key usage and administrative actions

## Reliability Patterns

### Exponential Backoff

```python
from openai import OpenAI, RateLimitError, APIError
import time
import random

client = OpenAI()

def call_with_retry(fn, max_retries=5, base_delay=1.0):
    """Call API with exponential backoff and jitter"""
    for attempt in range(max_retries):
        try:
            return fn()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            retry_after = e.response.headers.get("retry-after")
            if retry_after:
                delay = max(delay, float(retry_after))
            print(f"Rate limited. Retrying in {delay:.1f}s...")
            time.sleep(delay)
        except APIError as e:
            if e.status_code in (500, 503) and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
            else:
                raise

response = call_with_retry(
    lambda: client.chat.completions.create(
        model="gpt-5.6-sol",
        messages=[{"role": "user", "content": "Hello"}]
    )
)
```

### Rate Limit Headers

```python
def check_rate_limits(response):
    """Extract rate limit info from response headers"""
    headers = response.headers if hasattr(response, 'headers') else {}
    return {
        "requests_limit": headers.get("x-ratelimit-limit-requests"),
        "requests_remaining": headers.get("x-ratelimit-remaining-requests"),
        "tokens_limit": headers.get("x-ratelimit-limit-tokens"),
        "tokens_remaining": headers.get("x-ratelimit-remaining-tokens"),
        "reset": headers.get("x-ratelimit-reset-requests")
    }
```

## Cost Management

- **max_completion_tokens**: Always set to prevent runaway generation
- **Prompt caching**: Automatic 50-90% discount on repeated prompt prefixes
- **Flex processing**: 50% discount for latency-insensitive workloads (`service_tier: "flex"`)
- **Batch API**: 50% discount for async batch processing
- **Model selection**: Use smaller models (gpt-4.1-mini, gpt-4.1-nano) for simpler tasks
- **Usage API**: Monitor costs per project via admin endpoints

## Safety Practices

- **Moderation API**: Screen user inputs and model outputs
- **Input validation**: Sanitize, length-limit, and validate all user inputs
- **Output scope**: Use structured outputs to constrain response format
- **Content filtering**: Handle `finish_reason: "content_filter"` gracefully
- **Refusal handling**: Check `message.refusal` field for safety refusals
- **User identification**: Pass `user` parameter for abuse tracking

### Moderation Check

```python
from openai import OpenAI

client = OpenAI()

def moderate_input(text: str) -> bool:
    """Returns True if content is safe"""
    result = client.moderations.create(input=text)
    return not result.results[0].flagged

def safe_completion(user_input: str):
    if not moderate_input(user_input):
        return "I cannot process this request."
    
    response = client.chat.completions.create(
        model="gpt-5.6-sol",
        messages=[{"role": "user", "content": user_input}],
        max_completion_tokens=500
    )
    
    output = response.choices[0].message.content
    
    if not moderate_input(output):
        return "The response was filtered for safety."
    
    return output
```

## Monitoring Checklist

- **Token usage**: Track prompt_tokens, completion_tokens per request
- **Cached tokens**: Monitor prompt_tokens_details.cached_tokens for caching efficiency
- **Latency**: P50, P95, P99 response times
- **Error rates**: 4xx and 5xx error percentages
- **Cost per request**: Track spending via Usage/Cost API
- **Model performance**: Quality metrics specific to your use case
- **Rate limit proximity**: Alert when remaining requests/tokens < threshold

## Error Responses and Handling

- **400** - Bad request. Fix request parameters. Do not retry
- **401** - Invalid API key. Check key. Do not retry
- **403** - Forbidden. Check permissions. Do not retry
- **404** - Not found. Check resource ID. Do not retry
- **422** - Invalid schema (structured outputs). Fix schema. Do not retry
- **429** - Rate limited. Retry with exponential backoff
- **500** - Server error. Retry with backoff
- **503** - Service unavailable. Retry with backoff

## Differences from Other APIs

- **vs Anthropic**: Similar best practices. Anthropic has `anthropic-ratelimit-*` headers
- **vs Gemini**: Google Cloud quotas and IAM for access control
- **vs Grok**: Uses OpenAI-compatible API; same patterns apply

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

- OAIAPI-SC-OAI-GBPRD - Production Best Practices Guide
- OAIAPI-SC-OAI-GSAFE - Safety Best Practices Guide
- OAIAPI-SC-OAI-GRLIM - Rate Limits Guide
- OAIAPI-SC-OAI-GOVRVW - Governance Overview

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:45]**
- Enriched from 2026-03-20 IN61 (19 -> 170 lines)
- Updated model references to gpt-5.5

**[2026-05-22 11:50]**
- Stub created
