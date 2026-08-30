# Errors

**Doc ID**: OAIAPI-IN04
**Goal**: Document HTTP status codes, error response format, debugging
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI API uses standard HTTP status codes. Error responses include a JSON body with `error` object containing `type`, `message`, `param`, and `code` fields. Key codes: 400 (bad request), 401 (invalid auth), 403 (forbidden), 404 (model/resource not found), 429 (rate limit), 500/503 (server errors). The `x-request-id` response header and `X-Client-Request-Id` request header aid debugging. Since 2026-05, DALL-E 2/3 and Realtime Beta requests return 404. [VERIFIED] (OAIAPI-SC-OAI-GERROR)

## Error Response Format

```json
{
  "error": {
    "message": "The model 'dall-e-3' has been decommissioned.",
    "type": "invalid_request_error",
    "param": "model",
    "code": "model_not_found"
  }
}
```

## Key Facts

- **Error format**: JSON with type, code, message fields [VERIFIED] (OAIAPI-SC-OAI-GERROR)
- **Request tracking**: `x-request-id` header in all responses [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **HTTP status codes**: 400 (client error), 401/403 (auth), 429 (rate limit), 500/503 (server) [VERIFIED] (OAIAPI-SC-OAI-GERROR)
- **Retry-safe**: 429, 500, 503 should retry with exponential backoff [VERIFIED] (OAIAPI-SC-OAI-GERROR)
- **Non-retry**: 400, 401, 403, 404 indicate client issues - fix request, don't retry [VERIFIED] (OAIAPI-SC-OAI-GERROR)

## HTTP Status Codes

### 400 Bad Request
- **Error type**: `invalid_request_error`
- **Meaning**: Malformed request or invalid parameters
- **Action**: Fix request parameters, do not retry
- **Common causes**: Invalid JSON, missing required fields, out-of-range values

### 401 Unauthorized
- **Error type**: `authentication_error`
- **Meaning**: Missing, invalid, or expired API key
- **Action**: Check API key, do not retry with same key
- **Common causes**: No Authorization header, invalid Bearer token, expired key

### 403 Forbidden
- **Error type**: `permission_error`
- **Meaning**: API key lacks permissions for requested resource
- **Action**: Check account permissions, do not retry
- **Common causes**: Model access restricted, organization access denied, feature not enabled, tier restriction

### 404 Not Found
- **Error type**: `not_found_error`
- **Meaning**: Requested resource does not exist
- **Action**: Verify resource ID, do not retry
- **Common causes**: Invalid model ID, deleted resource, wrong endpoint, deprecated models (DALL-E 2/3 since 2026-05)

### 413 Payload Too Large
- **Error type**: `invalid_request_error`
- **Meaning**: Request body exceeds size limits
- **Action**: Reduce payload size, do not retry without change

### 422 Unprocessable Entity
- **Error type**: `invalid_request_error`
- **Meaning**: Valid JSON but semantic errors
- **Action**: Fix logical errors in request, do not retry without change

### 429 Too Many Requests
- **Error type**: `rate_limit_error`
- **Meaning**: Rate limit exceeded (RPM or TPM)
- **Action**: Retry with exponential backoff
- **Headers**: Check `x-ratelimit-reset-*` for reset time
- **Common causes**: Too many concurrent requests, token limit exceeded, quota exhaustion

### 500 Internal Server Error
- **Error type**: `api_error`
- **Meaning**: OpenAI server error
- **Action**: Retry with exponential backoff
- **Common causes**: Temporary server issue, service degradation

### 503 Service Unavailable
- **Error type**: `overloaded_error`
- **Meaning**: Servers temporarily overloaded
- **Action**: Retry with exponential backoff
- **Common causes**: High traffic, temporary capacity issues

## Error Response Format

### Standard Error Structure

```json
{
  "error": {
    "type": "invalid_request_error",
    "code": "parameter_invalid",
    "message": "Invalid value for 'temperature': must be between 0 and 2",
    "param": "temperature",
    "request_id": "req_abc123"
  }
}
```

### Error Fields

- **type**: Error category (invalid_request_error, authentication_error, permission_error, not_found_error, rate_limit_error, api_error, overloaded_error)
- **code**: Specific error code (parameter_invalid, insufficient_quota, model_not_found, etc.)
- **message**: Human-readable error description
- **param**: Name of invalid parameter (if applicable, null otherwise)
- **request_id**: Unique request identifier (also in x-request-id header)

## Request Tracking

### x-request-id Header

Every API response includes `x-request-id` header:
```
x-request-id: req_1234567890abcdef
```

Best practice: Log x-request-id for all requests in production.

### X-Client-Request-Id Header

Optionally provide custom request ID:
```
X-Client-Request-Id: my-trace-id-12345
```

Benefits:
- Use own ID format (UUID, trace ID, etc.)
- Track requests when x-request-id unavailable (timeouts)
- Correlate with internal systems

## SDK Examples (Python)

### Basic Error Handling

```python
from openai import OpenAI, APIError, RateLimitError, AuthenticationError

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-5.6-sol",
        messages=[{"role": "user", "content": "Hello"}]
    )
except AuthenticationError as e:
    print(f"Auth error: {e}")
except RateLimitError as e:
    print(f"Rate limited: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
    print(f"Request ID: {e.request_id}")
```

### Production Error Handling with Retry

```python
from openai import OpenAI, APIError, RateLimitError
import logging
import time

client = OpenAI()
logger = logging.getLogger(__name__)

def call_api_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-5.6-sol",
                messages=messages
            )
            logger.info(f"Request successful: {response._request_id}")
            return response

        except RateLimitError as e:
            wait_time = 2 ** attempt
            logger.warning(f"Rate limit hit, retrying in {wait_time}s")
            time.sleep(wait_time)

        except APIError as e:
            if e.status_code in (500, 503) and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.error(f"Server error, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                logger.error(f"Non-retryable error: {e}")
                raise

    raise Exception("Max retries exceeded")
```

### Custom Request ID

```python
from openai import OpenAI
import uuid

client = OpenAI()

custom_id = str(uuid.uuid4())

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Hello"}],
    extra_headers={
        "X-Client-Request-Id": custom_id
    }
)

print(f"Custom request ID: {custom_id}")
print(f"Server request ID: {response._request_id}")
```

## Rate Limiting / Throttling

Rate limit errors (429) should trigger exponential backoff:
- First retry: 1-2 seconds
- Second retry: 2-4 seconds
- Third retry: 4-8 seconds
- Check `x-ratelimit-reset-*` headers for reset time

## Limitations and Known Issues

- **Request ID not always in error body**: Some errors may not include request_id in JSON body (always available in response header) [COMMUNITY]
- **Error messages may change**: Message text not guaranteed stable across versions [VERIFIED] (OAIAPI-SC-OAI-GERROR)
- **Deprecated models return 404**: DALL-E 2/3, Realtime Beta requests return 404 since 2026-05 [VERIFIED]

## Gotchas and Quirks

- **429 can mean quota OR rate**: Rate limit error covers both RPM/TPM limits AND quota exhaustion [VERIFIED] (OAIAPI-SC-OAI-GERROR)
- **param field optional**: Not all errors include param field [VERIFIED] (OAIAPI-SC-OAI-GERROR)
- **Error codes not fully documented**: Full list of error codes not publicly documented [COMMUNITY]

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

- OAIAPI-SC-OAI-OVERVIEW - API Overview (Debugging section)
- OAIAPI-SC-OAI-GERROR - Error codes guide
- OAIAPI-SC-GH-SDKPY - Python SDK error handling

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Full error type details, request tracking, production retry example, custom request IDs, gotchas

**[2026-05-22 11:05]**
- Updated from 2026-03-20 (minor: added DALL-E 404 note, X-Client-Request-Id)
