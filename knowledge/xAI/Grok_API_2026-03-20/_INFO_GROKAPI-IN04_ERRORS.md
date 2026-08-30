# INFO: Debugging Errors

**Doc ID**: GROKAPI-IN04
**Goal**: Status codes, error response format, debugging guidance, bug reports
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok API returns standard HTTP status codes with structured error messages. Normal responses return `200 OK`. Client errors use 4XX codes (400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 405 Method Not Allowed, 415 Unsupported Media Type, 422 Unprocessable Entity, 429 Too Many Requests). A special 2XX code exists: `202 Accepted` for deferred chat completion requests that are queued but not yet ready. Error messages are self-explanatory and accompany most error responses. Service disruptions are tracked at https://status.x.ai with RSS feed available at https://status.x.ai/feed.xml. [VERIFIED] (GROKAPI-SC-XAI-ERRORS | https://docs.x.ai/developers/debugging-errors)

## Key Facts

- [VERIFIED] Status page: https://status.x.ai (RSS: https://status.x.ai/feed.xml) (GROKAPI-SC-XAI-ERRORS)
- [VERIFIED] 202 Accepted is used for deferred completions (not an error, request is queued) (GROKAPI-SC-XAI-ERRORS)
- [VERIFIED] 429 Too Many Requests applies only to inference endpoints (GROKAPI-SC-XAI-ERRORS)
- [VERIFIED] 415 requires Content-Type: application/json header on POST requests (GROKAPI-SC-XAI-ERRORS)

## Quick Reference

### 4XX Status Codes

- **400 Bad Request**: Invalid argument in POST body, invalid URL param, or incorrect API key
  - Fix: Check request body or URL against API Reference
- **401 Unauthorized**: Missing or invalid authorization header
  - Fix: Add `Authorization: Bearer <XAI_API_KEY>` header
- **403 Forbidden**: Key/team lacks permission or is blocked
  - Fix: Contact team admin for permission
- **404 Not Found**: Model not found or invalid endpoint URL
  - Fix: Verify model name and endpoint URL
- **405 Method Not Allowed**: Wrong HTTP method (e.g., POST to GET-only endpoint)
  - Fix: Check correct method in API Reference
- **415 Unsupported Media Type**: Empty POST body or missing Content-Type header
  - Fix: Add valid body and `Content-Type: application/json` header
- **422 Unprocessable Entity**: Invalid field format in POST body
  - Fix: Validate request body against API Reference
- **429 Too Many Requests**: Rate limit exceeded (inference endpoints only)
  - Fix: Reduce request rate or increase rate limit tier

### 2XX Special Codes

- **202 Accepted**: Deferred completion queued but response not yet available
  - Fix: Poll `GET /v1/chat/deferred-completion/{request_id}` until response ready

## Error Handling Example (Python)

```python
import os
import httpx
from openai import OpenAI, APIError, RateLimitError, AuthenticationError

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

try:
    response = client.responses.create(
        model="grok-4.20-beta-latest-non-reasoning",
        input=[{"role": "user", "content": "Hello"}],
    )
    print(response.output_text)
except AuthenticationError as e:
    print(f"Auth failed (401): {e.message}")
except RateLimitError as e:
    print(f"Rate limited (429): {e.message}")
    # Implement exponential backoff
except APIError as e:
    print(f"API error ({e.status_code}): {e.message}")
```

### Retry with Exponential Backoff

```python
import time
import random
from openai import OpenAI, RateLimitError, APIError

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

def call_with_retry(max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.responses.create(
                model="grok-4.20-beta-latest-non-reasoning",
                input=[{"role": "user", "content": "Hello"}],
            )
        except RateLimitError:
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited. Retrying in {wait:.1f}s (attempt {attempt + 1})")
            time.sleep(wait)
        except APIError as e:
            if e.status_code >= 500:
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"Server error {e.status_code}. Retrying in {wait:.1f}s")
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")
```

## Differences from Other APIs

### vs OpenAI

- **Same status codes**: Both follow standard HTTP error patterns
- **202 Accepted**: xAI uses for deferred completions (OpenAI has no equivalent for standard API)
- **Status page**: status.x.ai vs status.openai.com
- **Error format**: Compatible structure (OpenAI SDK handles xAI errors natively)

### vs Anthropic

- **Same HTTP codes**: Both use standard 4XX/5XX patterns
- **Error body format**: xAI uses OpenAI-compatible format; Anthropic uses `{"type": "error", "error": {"type": "...", "message": "..."}}`
- **Overloaded errors**: Anthropic has 529 Overloaded; xAI uses 429 for all rate-limiting

### vs Gemini

- **Different error format**: xAI uses OpenAI-compatible; Gemini uses Google API error format with `status` and `details` arrays

## Sources

- GROKAPI-SC-XAI-ERRORS | https://docs.x.ai/developers/debugging-errors | Accessed: 2026-03-20

## Document History

**[2026-03-20 03:20]**
- Initial document created with all status codes and error handling examples
