# Introduction and API Overview

**Doc ID**: ANTAPI-IN03
**Goal**: Document the Anthropic API fundamentals - base URL, protocol, request/response format, available APIs
**API version**: anthropic-version 2023-06-01

## Summary

The Claude API is a RESTful JSON API at `https://api.anthropic.com` providing programmatic access to Claude models. The primary interface is the Messages API (`POST /v1/messages`) for conversational interactions. Authentication uses the `x-api-key` header, API versioning uses the `anthropic-version` header, and all requests use `application/json` content type. Official SDKs are available for Python, TypeScript, Java, Go, C#, Ruby, and PHP.

## Key Facts

- **Base URL**: `https://api.anthropic.com`
- **Protocol**: HTTPS, RESTful
- **Content-Type**: `application/json`
- **Primary Endpoint**: `POST /v1/messages`
- **Auth Header**: `x-api-key`
- **Version Header**: `anthropic-version: 2023-06-01`
- **Status**: GA (General Availability)
- **SDKs**: Python, TypeScript, Java, Go, C#, Ruby, PHP

## Available APIs

### General Availability

- **Messages API** (`POST /v1/messages`) - Send messages to Claude for conversational interactions
- **Message Batches API** (`POST /v1/messages/batches`) - Async bulk processing with 50% cost reduction
- **Token Counting API** (`POST /v1/messages/count_tokens`) - Count tokens before sending to manage costs
- **Models API** (`GET /v1/models`) - List available Claude models and details

### Beta

- **Files API** (`POST /v1/files`, `GET /v1/files`) - Upload and manage files across API calls
- **Skills API** (`POST /v1/skills`, `GET /v1/skills`) - Create and manage custom agent skills

### Admin

- **Organizations API** - Organization management
- **Users API** - User management within organizations
- **Workspaces API** - Workspace CRUD and membership
- **API Keys API** - Key management
- **Usage/Cost Reports** - Token consumption and spend tracking

### Legacy

- **Text Completions API** (`POST /v1/complete`) - Deprecated, use Messages API instead

## Required Headers

Every request must include these three headers:

- **`x-api-key`** - Your API key from the Anthropic Console
- **`anthropic-version`** - API version string (current: `2023-06-01`)
- **`content-type`** - Must be `application/json`

The official SDKs send these headers automatically.

## Request and Response Format

### Request Size Limits

The API enforces maximum request sizes per endpoint. Exceeding limits returns a `413 request_too_large` error. Third-party platforms have their own limits: Vertex AI limits requests to 30 MB, Amazon Bedrock to 20 MB.

### Response Headers

Every response includes:

- **`request-id`** - Globally unique identifier for the request (use for debugging and support)
- **`anthropic-organization-id`** - Organization ID associated with the API key

## Quick Reference

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
print(message.content[0].text)
```

### Equivalent cURL

```
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "Hello, Claude"}
    ]
  }'
```

### Response Example

```json
{
  "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Hello! How can I assist you today?"
    }
  ],
  "model": "claude-opus-5",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 12,
    "output_tokens": 8
  }
}
```

## Claude API vs Third-Party Platforms

### Direct API (api.anthropic.com)

- Direct access to latest models and features first
- Anthropic billing and support
- Best for: new integrations, full feature access, direct relationship with Anthropic

### Third-Party Platform APIs

Access Claude through AWS (Bedrock), Google Cloud (Vertex AI), or Microsoft Azure:

- Integrated with cloud provider billing and IAM
- May have feature delays or differences from the direct API
- Best for: existing cloud commitments, compliance requirements, consolidated billing

## Gotchas and Quirks

- The `anthropic-version` header value has not changed since `2023-06-01` despite many API updates; new features use beta headers instead
- The `request-id` response header is essential for Anthropic support; log it for production systems
- Third-party platforms (Bedrock, Vertex AI) use different authentication mechanisms (SigV4, OAuth2) and may lag behind the direct API in feature availability
- The `inference_geo` parameter on the Messages API enables data residency controls for specifying where model inference runs

## Related Endpoints

- `_INFO_ANTAPI-04_AUTHENTICATION.md [ANTAPI-IN04]` - Detailed authentication guide
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` - API versioning and beta headers
- `_INFO_ANTAPI-06_ERRORS.md [ANTAPI-IN06]` - Error types and handling
- `_INFO_ANTAPI-07_SDKS.md [ANTAPI-IN07]` - SDK installation and usage
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` - Full Messages API reference

## Sources

- ANTAPI-SC-ANTH-APIOVW - https://platform.claude.com/docs/en/api/overview - API overview, auth, format, examples
- ANTAPI-SC-ANTH-INTRO - https://platform.claude.com/docs/en/intro - Intro page, capabilities overview

## SDK Verification

1 Python example verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `_client.py` (line 53): `Anthropic()` constructor, ANTHROPIC_API_KEY env var
- `resources/messages/messages.py`: `create(model, max_tokens, messages)` signature

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:45]**
- Added: SDK verification section (anthropic 0.120.0, 1 example valid)

**[2026-03-20 02:10]**
- Initial documentation created from API overview page
