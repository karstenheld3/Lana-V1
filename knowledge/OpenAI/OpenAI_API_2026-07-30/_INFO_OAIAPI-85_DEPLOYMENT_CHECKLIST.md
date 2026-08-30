# Deployment Checklist

**Doc ID**: OAIAPI-IN85
**Goal**: Document deployment checklist for production API integrations
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Step-by-step checklist for deploying OpenAI API integrations to production. Covers authentication setup, rate limit configuration, error handling, monitoring, safety checks, and compliance requirements. Separate from production best practices guide which covers patterns and strategies. [VERIFIED] (OAIAPI-SC-OAI-GDEPLC (https://developers.openai.com/api/docs/guides/deployment-checklist))

## Pre-Deployment Checklist

### Authentication and Security

- [ ] API keys stored in environment variables or secret manager (not hardcoded)
- [ ] Using project-scoped API keys (not legacy user keys)
- [ ] Service account keys for production (not personal keys)
- [ ] Keys rotated on schedule
- [ ] No keys in client-side code or version control

### Rate Limiting and Scaling

- [ ] Exponential backoff implemented for 429 responses
- [ ] Rate limit headers monitored (`x-ratelimit-*`)
- [ ] Appropriate usage tier for expected load
- [ ] Batch API used for non-urgent bulk processing
- [ ] Project-level rate limits configured via Admin API

### Error Handling

- [ ] All HTTP error codes handled (400, 401, 403, 404, 429, 500, 503)
- [ ] Retry logic for transient errors (429, 500, 503)
- [ ] Max retry limits to prevent infinite loops
- [ ] `x-request-id` logged for all requests
- [ ] `X-Client-Request-Id` set for request correlation

### Monitoring and Observability

- [ ] Request latency tracking
- [ ] Error rate monitoring with alerting
- [ ] Token usage tracking for cost control
- [ ] Rate limit remaining monitoring
- [ ] Model performance metrics (quality, latency per model)

### Safety and Content

- [ ] Content moderation applied to user inputs
- [ ] Output validation for sensitive use cases
- [ ] System prompts secured against injection
- [ ] PII handling compliant with policy
- [ ] Age-appropriate content controls (if applicable)

### Model Configuration

- [ ] Pinned model version (not floating alias) for consistency
- [ ] `max_completion_tokens` set to prevent runaway costs
- [ ] Temperature and parameters tuned via evaluation
- [ ] Fallback model configured for outages

### Cost Management

- [ ] Usage alerts configured in dashboard
- [ ] Budget caps set per project
- [ ] Batch API used where possible (50% savings)
- [ ] Token usage optimized (prompt engineering, caching)

## SDK Examples (Python)

### Production-Ready Client Setup

```python
import os
import logging
from openai import OpenAI, APIError, RateLimitError

logger = logging.getLogger(__name__)

# Checklist: env var, not hardcoded
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not set")

client = OpenAI(
    api_key=api_key,
    max_retries=3,  # Built-in retry with backoff
    timeout=30.0,   # Request timeout
)

def production_call(messages, model="gpt-5.6-sol"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_completion_tokens=4096,
            extra_headers={"X-Client-Request-Id": generate_trace_id()},
        )
        logger.info(f"Success: {response._request_id}")
        return response
    except RateLimitError as e:
        logger.warning(f"Rate limited: {e}")
        raise
    except APIError as e:
        logger.error(f"API error {e.status_code}: {e.message}, req_id={e.request_id}")
        raise
```

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

- OAIAPI-SC-OAI-GDEPLC - Deployment checklist (https://developers.openai.com/api/docs/guides/deployment-checklist)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Full checklist categories, production client example

**[2026-05-22 13:05]**
- Initial documentation (gap found during /improve review)
