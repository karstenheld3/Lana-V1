# Errors

**Doc ID**: ANTAPI-IN06
**Goal**: Document all error types, HTTP status codes, error response format, and retry strategies
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL and general overview

## Summary

The Anthropic API uses standard HTTP status codes with a consistent JSON error response format. All errors include a top-level `error` object with `type` and `message` fields, plus a `request_id` for support. Transient errors (429, 500, 529) should be retried with exponential backoff. The SDKs provide the request ID as `message._request_id`.

## Key Facts

- **Error Format**: JSON with `type`, `error.type`, `error.message`, `request_id`
- **Retryable**: 429 (rate limit), 500 (internal), 529 (overloaded)
- **Non-Retryable**: 400, 401, 402, 403, 404, 413
- **Max Request Size**: 32 MB for standard endpoints
- **SDK Feature**: Built-in retry logic for transient errors

## HTTP Status Codes

- **400** `invalid_request_error` - Issue with request format or content. Also used for other 4XX codes not listed below
- **401** `authentication_error` - Issue with API key
- **402** `billing_error` - Issue with billing or payment. Check payment details in Console
- **403** `permission_error` - API key lacks permission for the resource
- **404** `not_found_error` - Requested resource not found
- **413** `request_too_large` - Request exceeds 32 MB max. Returned by Cloudflare before reaching API servers
- **429** `rate_limit_error` - Account hit a rate limit. May also occur due to acceleration limits on sharp usage increases
- **500** `api_error` - Unexpected internal error at Anthropic
- **529** `overloaded_error` - API temporarily overloaded due to high traffic across all users

## Error Response Format

```json
{
  "type": "error",
  "error": {
    "type": "not_found_error",
    "message": "The requested resource could not be found."
  },
  "request_id": "req_011CSHoEeqs5C35K2UUqR7Fy"
}
```

**Fields:**

- **type** (`string`) - Always `"error"`
- **error.type** (`string`) - Error type identifier (see HTTP Status Codes above)
- **error.message** (`string`) - Human-readable error description
- **request_id** (`string`) - Unique request identifier for debugging and support

## Common Validation Errors

### Prefill Not Supported

Claude Opus 4.6 does not support prefilling assistant messages. Sending a prefilled last assistant message returns:

```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "Prefilling assistant messages is not supported for this model."
  }
}
```

Use structured outputs, system prompt instructions, or `output_config.format` instead.

## Request ID Access

### Python SDK

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
print(f"Request ID: {message._request_id}")
```

### Response Header

Every API response includes the `request-id` header (e.g., `req_018EeWyXxfu5pfWkrYcMdjWG`). Log this for production systems to facilitate support debugging.

## Retry Strategy

```python
import anthropic
import time

def call_with_retry(client, max_retries=3, base_delay=1.0):
    """Call API with exponential backoff for transient errors."""
    for attempt in range(max_retries):
        try:
            return client.messages.create(
                model="claude-opus-5",
                max_tokens=1024,
                messages=[{"role": "user", "content": "Hello"}],
            )
        except anthropic.RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"Rate limited. Retrying in {delay}s...")
            time.sleep(delay)
        except anthropic.InternalServerError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
        except anthropic.APIStatusError as e:
            # Non-retryable errors (400, 401, 403, etc.)
            raise
```

The official SDKs include built-in retry logic with exponential backoff for transient errors, so manual retry is usually unnecessary.

## Long Request Handling

For requests over 10 minutes:

- Use the streaming Messages API to avoid idle connection timeouts
- Use the Message Batches API for requests that do not need real-time responses
- SDKs validate non-streaming requests against a 10-minute timeout
- SDKs set TCP socket keep-alive to reduce idle connection drops

```python
import anthropic

client = anthropic.Anthropic()

# Use streaming for long requests
with client.messages.stream(
    max_tokens=128000,
    messages=[{"role": "user", "content": "Write a detailed analysis..."}],
    model="claude-opus-5",
) as stream:
    message = stream.get_final_message()
```

## Gotchas and Quirks

- SSE streaming responses return HTTP 200 initially; errors during streaming do not follow standard error format
- 529 errors affect all users during high traffic, not just your account
- 429 errors can occur from acceleration limits even if steady-state rate limits are not exceeded; ramp up traffic gradually
- The `request_id` format is `req_` followed by a unique string
- Error `type` values may expand over time per the versioning policy

## Related Endpoints

- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` - Request/response format
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` - Version stability guarantees
- `_INFO_ANTAPI-36_RATE_LIMITS.md [ANTAPI-IN36]` - Rate limit details and tiers

## Sources

- ANTAPI-SC-ANTH-ERRORS - https://platform.claude.com/docs/en/api/errors - All error types, shapes, request ID, long requests, validation errors

## SDK Verification

All 3 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `_models.py`: `_request_id` injected via `add_request_id()` at runtime
- `_exceptions.py` (lines 84-130): `RateLimitError` (429), `InternalServerError` (pass-through), `APIStatusError` base class
- `lib/streaming/_messages.py`: `stream.get_final_message()` for long requests

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:45]**
- Added: SDK verification section (anthropic 0.120.0, all 3 examples valid)

**[2026-03-20 02:20]**
- Initial documentation created from errors page
