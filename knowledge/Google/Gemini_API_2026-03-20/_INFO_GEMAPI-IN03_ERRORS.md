# INFO: Gemini API Errors and Troubleshooting

**Doc ID**: GEMAPI-IN03
**Goal**: Document HTTP error codes, error response format, safety blocks, and troubleshooting strategies
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini API returns standard HTTP status codes for errors with structured JSON error responses. Common errors include 400 (invalid parameters), 401/403 (authentication), 404 (model not found), 429 (rate limit), and 500/503 (server errors). Unique to Gemini are safety-related response blocks where the API returns 200 OK but with blocked content indicated by `finishReason` values like `SAFETY`, `RECITATION`, or `OTHER`. The `BlockedReason.OTHER` indicates terms of service violations. API version mismatches between `/v1` and `/v1beta` are a frequent source of 404 errors when using beta features. Thinking-enabled models (2.5+) may cause unexpected latency and token usage. The troubleshooting guide recommends verifying model parameters against `get_model`, checking API version compatibility, and reviewing safety settings.

## Key Facts

- [VERIFIED] Standard HTTP status codes used (400, 401, 403, 404, 429, 500, 503) (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] Safety blocks return 200 OK with blocked `finishReason`, not HTTP errors (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] `finishReason` values: STOP, MAX_TOKENS, SAFETY, RECITATION, OTHER (GEMAPI-SC-GOOG-GENCNT)
- [VERIFIED] `BlockedReason.OTHER` = terms of service violation (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] API version mismatch causes 404 for beta features on `/v1` (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] Thinking models increase latency/tokens by default (GEMAPI-SC-GOOG-TROUBL)

## Use Cases

- **Error handling**: Implement retry logic based on error codes
- **Safety monitoring**: Detect and handle content blocks
- **Debugging**: Diagnose parameter and version issues

## Quick Reference

**Error Response Format:**
```json
{
  "error": {
    "code": 429,
    "message": "Resource exhausted",
    "status": "RESOURCE_EXHAUSTED"
  }
}
```

## HTTP Error Codes

- **400 INVALID_ARGUMENT**: Invalid request body, unsupported parameter values, model parameter out of range
  - Resolution: Verify parameters against `get_model` response, check JSON syntax
- **401 UNAUTHENTICATED**: Missing or invalid API key
  - Resolution: Verify API key in `x-goog-api-key` header, check key in Google AI Studio
- **403 PERMISSION_DENIED**: API key lacks permissions, restricted by IP/referrer, API not enabled
  - Resolution: Check key restrictions in Google Cloud Console, enable Generative Language API
- **404 NOT_FOUND**: Invalid model name, wrong API version for feature
  - Resolution: Verify model exists via GET /v1beta/models, check `/v1beta` vs `/v1`
- **429 RESOURCE_EXHAUSTED**: Rate limit exceeded (RPM, TPM, or RPD)
  - Resolution: Implement exponential backoff, request quota increase, upgrade tier
- **500 INTERNAL**: Server-side error
  - Resolution: Retry with exponential backoff
- **503 UNAVAILABLE**: Service temporarily unavailable or overloaded
  - Resolution: Retry with exponential backoff, check status page

## Safety-Related Blocks

Safety blocks are NOT HTTP errors - the API returns 200 OK with modified response content.

### finishReason Values

- **STOP**: Normal completion
- **MAX_TOKENS**: Output truncated at maxOutputTokens limit
- **SAFETY**: Content blocked by safety settings
- **RECITATION**: Output resembles training data too closely
- **OTHER**: Content violates terms of service or is otherwise unsupported

### Safety Block Response

```json
{
  "candidates": [
    {
      "content": {
        "parts": [],
        "role": "model"
      },
      "finishReason": "SAFETY",
      "safetyRatings": [
        {
          "category": "HARM_CATEGORY_HARASSMENT",
          "probability": "HIGH",
          "blocked": true
        }
      ]
    }
  ]
}
```

### Handling Safety Blocks

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your prompt here"
)

if response.candidates:
    candidate = response.candidates[0]
    if candidate.finish_reason == "SAFETY":
        print("Content blocked by safety filter")
        for rating in candidate.safety_ratings:
            if rating.blocked:
                print(f"  Blocked by: {rating.category}")
    elif candidate.finish_reason == "RECITATION":
        print("Content blocked due to recitation - try higher temperature")
    elif candidate.finish_reason == "STOP":
        print(response.text)
    elif candidate.finish_reason == "MAX_TOKENS":
        print(f"Truncated: {response.text}")
```

## Python Examples

### Example 1: Retry with Exponential Backoff

```python
# SOURCE: Google API docs (may use google.api_core.exceptions)
import time
from google import genai
from google.api_core import exceptions
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except exceptions.ResourceExhausted:
            wait = 2 ** attempt
            print(f"Rate limited. Retrying in {wait}s...")
            time.sleep(wait)
        except exceptions.InvalidArgument as e:
            print(f"Invalid request: {e}")
            raise
        except exceptions.NotFound as e:
            print(f"Model not found: {e}")
            raise
    raise Exception("Max retries exceeded")

result = generate_with_retry("Explain quantum computing")
print(result)
```

**SDK-verified correction** (google-genai v1.68.0, `google/genai/errors.py`):

`google.api_core` is NOT a dependency of `google-genai`. The SDK raises
`google.genai.errors.ClientError` (4xx) and `google.genai.errors.ServerError` (5xx),
both subclasses of `google.genai.errors.APIError`. Use `error.code` for HTTP status.

```python
import time
from google import genai
from google.genai.errors import APIError, ClientError, ServerError
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except ClientError as e:
            if e.code == 429:
                wait = 2 ** attempt
                print(f"Rate limited. Retrying in {wait}s...")
                time.sleep(wait)
            elif e.code == 400:
                print(f"Invalid request: {e.message}")
                raise
            elif e.code == 404:
                print(f"Model not found: {e.message}")
                raise
            else:
                raise
        except ServerError as e:
            wait = 2 ** attempt
            print(f"Server error ({e.code}). Retrying in {wait}s...")
            time.sleep(wait)
    raise Exception("Max retries exceeded")

result = generate_with_retry("Explain quantum computing")
print(result)
```

### Example 2: Comprehensive Error Handling

```python
# SOURCE: Google API docs (may use google.api_core.exceptions)
from google import genai
from google.api_core import exceptions
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Write a story"
    )

    if response.candidates:
        candidate = response.candidates[0]
        finish = candidate.finish_reason

        if finish == "STOP":
            print(response.text)
        elif finish == "MAX_TOKENS":
            print(f"Truncated output: {response.text}")
        elif finish == "SAFETY":
            blocked = [r.category for r in candidate.safety_ratings if r.blocked]
            print(f"Blocked by safety: {blocked}")
        elif finish == "RECITATION":
            print("Blocked: output resembles training data")
        elif finish == "OTHER":
            print("Blocked: possible ToS violation")
    else:
        print("No candidates returned")

except exceptions.InvalidArgument as e:
    print(f"400 Bad Request: {e}")
except exceptions.Unauthenticated as e:
    print(f"401 Unauthorized: {e}")
except exceptions.PermissionDenied as e:
    print(f"403 Forbidden: {e}")
except exceptions.NotFound as e:
    print(f"404 Not Found: {e}")
except exceptions.ResourceExhausted as e:
    print(f"429 Rate Limited: {e}")
except exceptions.InternalServerError as e:
    print(f"500 Server Error: {e}")
except exceptions.ServiceUnavailable as e:
    print(f"503 Unavailable: {e}")
```

**SDK-verified correction** (google-genai v1.68.0, `google/genai/errors.py`):

The SDK error hierarchy: `APIError` > `ClientError` (4xx), `ServerError` (5xx).
Use `error.code` for HTTP status, `error.message` for detail, `error.status` for gRPC status.
FinishReason is an enum but supports string comparison (`== 'SAFETY'` works).

```python
from google import genai
from google.genai.errors import APIError, ClientError, ServerError
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Write a story"
    )

    if response.candidates:
        candidate = response.candidates[0]
        finish = candidate.finish_reason

        if finish == "STOP":
            print(response.text)
        elif finish == "MAX_TOKENS":
            print(f"Truncated output: {response.text}")
        elif finish == "SAFETY":
            blocked = [r.category for r in candidate.safety_ratings if r.blocked]
            print(f"Blocked by safety: {blocked}")
        elif finish == "RECITATION":
            print("Blocked: output resembles training data")
        elif finish == "OTHER":
            print("Blocked: possible ToS violation")
    else:
        print("No candidates returned")

except ClientError as e:
    print(f"Client error {e.code} {e.status}: {e.message}")
except ServerError as e:
    print(f"Server error {e.code}: {e.message}")
except APIError as e:
    print(f"API error {e.code}: {e.message}")
```

## cURL Examples

### Example: Check Error Response

```bash
# Intentionally invalid model to see error format
curl "https://generativelanguage.googleapis.com/v1beta/models/nonexistent-model:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{"contents": [{"parts": [{"text": "hello"}]}]}'
```

## Comparison with Other APIs

### vs OpenAI

- **Error format**: Gemini: `{error: {code, message, status}}` | OpenAI: `{error: {message, type, code}}`
- **Safety handling**: Gemini: finishReason in 200 response | OpenAI: separate Moderations API
- **Rate limit info**: Gemini: check AI Studio | OpenAI: rate limit headers in response

### vs Anthropic

- **Error format**: Gemini: `{error: {code, message, status}}` | Anthropic: `{type: "error", error: {type, message}}`
- **Safety handling**: Gemini: configurable per-request | Anthropic: stop_reason with content policy
- **Recitation blocking**: Gemini-specific concept (RECITATION finishReason)

## Rate Limiting / Throttling

429 errors indicate rate limit exceeded. Implement exponential backoff. See GEMAPI-IN04 for tier details.

## Limitations and Known Issues

- [VERIFIED] Only a number of select languages supported; unsupported languages may produce unexpected or blocked responses (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] Thinking models (2.5+) have thinking enabled by default, causing higher latency/tokens (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] RECITATION finish reason: model stops if output resembles training data - use higher temperature and more unique prompts (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] `BlockedReason.OTHER`: query or response violates ToS or is otherwise unsupported (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] Beta features only available on `/v1beta` API version, not `/v1` (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] API keys can be blocked by Google security if leaked publicly (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] Leaked keys may cause unexpected charges from vulnerability exploitation (GEMAPI-SC-GOOG-TROUBL)
- [COMMUNITY] Empty responses reported alongside errors during peak usage (GEMAPI-SC-FORUM-ERRS)

## Gotchas and Quirks

- Safety blocks return HTTP 200, not 4xx - must check `finishReason` in response body
- `BlockedReason.OTHER` is different from safety blocks - indicates ToS violation, not content filter
- Using `/v1` with beta features gives 404, not a helpful "use v1beta" error
- RECITATION blocks can be mitigated by using higher temperature and more unique prompts
- API keys leaked in public repos/websites will be automatically blocked by Google security
- Verify model parameter values using `get_model` before troubleshooting errors
- Ensure correct API version (`/v1` vs `/v1beta`) matches the features you need

## Sources

- GEMAPI-SC-GOOG-TROUBL: https://ai.google.dev/gemini-api/docs/troubleshooting [VERIFIED]
- GEMAPI-SC-GOOG-GENCNT: https://ai.google.dev/api/generate-content [VERIFIED]
- GEMAPI-SC-FORUM-ERRS: https://discuss.ai.google.dev/t/finishreason-http-code-and-json-response/52608 [COMMUNITY]

## Document History

**[2026-03-20 07:15]**
- Fixed: Error handling examples used google.api_core.exceptions (not installed with google-genai)
- Added: SDK-verified corrections using google.genai.errors (ClientError, ServerError, APIError)
- Source: google-genai v1.68.0, google/genai/errors.py

**[2026-03-20 06:45]**
- Added: RECITATION finish reason, BlockedReason.OTHER, leaked API key blocking
- Added: v1beta feature requirement, parameter validation via get_model

**[2026-03-20 02:55]**
- Initial document created with error codes, safety blocks, and Python examples
