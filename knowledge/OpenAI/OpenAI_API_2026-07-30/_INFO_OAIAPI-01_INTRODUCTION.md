# Introduction

**Doc ID**: OAIAPI-IN01
**Goal**: Document API overview, base URL, versioning, backwards compatibility
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The OpenAI API is a RESTful interface at `https://api.openai.com/v1` providing access to AI models for text generation, image/video creation, audio processing, embeddings, moderation, and real-time voice interactions. Authentication uses Bearer tokens via `Authorization` header. The API follows semantic versioning with the current REST version `2020-10-01`. Backwards-compatible changes (new resources, optional parameters, new response properties, new event types) do not require client updates. The API supports per-request debugging via `x-request-id` header (server-generated) and `X-Client-Request-Id` header (client-supplied, up to 512 ASCII chars). Rate limiting information is returned in `x-ratelimit-*` response headers. [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)

## Base URL

```
https://api.openai.com/v1
```

## Authentication

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

For multi-org/project setups:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Organization: $ORGANIZATION_ID" \
  -H "OpenAI-Project: $PROJECT_ID"
```

## Debugging Headers

**Response headers**:
- `x-request-id` - Unique request identifier (for support troubleshooting)
- `openai-organization` - Organization associated with request
- `openai-processing-ms` - Server processing time
- `openai-version` - REST API version (`2020-10-01`)

**Client-supplied request ID**:
- `X-Client-Request-Id` - Custom trace ID (ASCII, max 512 chars)
- Logged by OpenAI for supported endpoints (chat/completions, embeddings, responses)
- Useful when server `x-request-id` is unavailable (timeouts, network issues)

## Rate Limiting Headers

- `x-ratelimit-limit-requests` / `x-ratelimit-remaining-requests`
- `x-ratelimit-limit-tokens` / `x-ratelimit-remaining-tokens`
- `x-ratelimit-reset-requests` / `x-ratelimit-reset-tokens`

## Backwards Compatibility

Backwards-compatible changes (no client update needed):
- Adding new resources (URLs)
- Adding new optional parameters
- Adding new JSON response properties or event types
- Changing order of JSON properties
- Changing length/format of opaque strings (IDs, UUIDs)

## Key Facts

- **Base URL**: `https://api.openai.com/v1/` [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **Current API version**: `v1` (returned as `2020-10-01` in `openai-version` header) [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **Authentication**: Bearer token in `Authorization` header [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **Multi-org support**: `OpenAI-Organization` and `OpenAI-Project` headers [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **Custom request IDs**: `X-Client-Request-Id` header (max 512 ASCII chars) [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **Debug headers**: `x-request-id`, `openai-processing-ms`, rate limit headers [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)

## Use Cases

- **API integration**: Building applications that use OpenAI models
- **Multi-org routing**: Managing API usage across multiple organizations and projects
- **Request tracking**: Logging request IDs for production troubleshooting
- **Rate limit monitoring**: Tracking usage via response headers

## API Overview

### Request Structure

API requests are RESTful HTTP requests with JSON payloads. Most endpoints use POST method with JSON request bodies. The API provides access to:

- Text generation (GPT-5.5, GPT-5.4, o4-mini, o3-pro)
- Image generation (gpt-image-1, gpt-image-1.5)
- Video generation (Sora)
- Audio (Whisper, TTS, Realtime)
- Embeddings (text-embedding-3-small/large)
- Moderation (omni-moderation)
- Real-time voice interactions (Realtime API)

### Model Behavior Changes

Model prompting behavior between snapshots is subject to change. Model outputs are variable by nature - expect changes between snapshots. Best practices:
- Use pinned model versions for consistent behavior
- Implement evals for applications

## SDK Examples (Python)

### Basic Request

```python
from openai import OpenAI

client = OpenAI()  # API key loaded from OPENAI_API_KEY env var

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
# Access request ID for debugging
print(f"Request ID: {response._request_id}")
```

### Multi-Organization Request

```python
from openai import OpenAI

client = OpenAI(
    organization="org-123456",
    project="proj-abc123"
)

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Request ID Logging (Production)

```python
from openai import OpenAI
import logging

client = OpenAI()
logger = logging.getLogger(__name__)

try:
    response = client.chat.completions.create(
        model="gpt-5.6-sol",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    # Log request ID for troubleshooting
    logger.info(f"Request completed: {response.id}, x-request-id: {response._request_id}")
except Exception as e:
    logger.error(f"Request failed: {e}")
```

## Error Responses

- **400 Bad Request** - Invalid request format or parameters
- **401 Unauthorized** - Missing or invalid API key
- **403 Forbidden** - API key lacks required permissions
- **429 Too Many Requests** - Rate limit exceeded, retry with backoff
- **500 Internal Server Error** - OpenAI server error, retry with exponential backoff

## Differences from Other APIs

- **vs Anthropic**: Anthropic uses `x-api-key` header instead of `Authorization: Bearer`; no multi-org routing headers
- **vs Gemini**: Gemini uses `x-goog-api-key` header; no organization/project routing
- **vs Grok**: Grok is OpenAI-compatible (uses same authentication and base URL pattern)

## Limitations and Known Issues

- **Custom request IDs limited**: Max 512 ASCII characters, request fails with 400 if exceeded [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **Model behavior variability**: Model outputs change between snapshots even with identical prompts [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)

## Gotchas and Quirks

- **Organization/Project headers optional**: Only needed for multi-org access or legacy user API keys [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **API version in header**: The `openai-version` header returns `2020-10-01`, not `v1` [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)

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

- OAIAPI-SC-OAI-OVERVIEW - API Overview (Introduction, Authentication, Debugging, Backwards compatibility)
- OAIAPI-SC-OAI-GOVRVW - Official guides overview

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Added Key Facts, Use Cases, API Overview, detailed SDK examples, error responses, gotchas

**[2026-05-22 10:25]**
- Updated from 2026-03-20 version
- Changed: SDK example uses gpt-5.5
- Added: X-Client-Request-Id documentation
