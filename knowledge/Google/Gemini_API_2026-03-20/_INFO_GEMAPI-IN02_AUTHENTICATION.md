# INFO: Gemini API Authentication

**Doc ID**: GEMAPI-IN02
**Goal**: Document API key management, authentication headers, ephemeral tokens, and security best practices
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini API authenticates requests using API keys passed via the `x-goog-api-key` HTTP header. API keys are created and managed through Google AI Studio, which provides a lightweight interface to Google Cloud projects. Each key is associated with a Google Cloud project that controls billing and permissions. For client-side Live API access, ephemeral tokens provide short-lived authentication (default 1 minute for session start, 30 minutes for connection) to avoid exposing long-lived API keys. Ephemeral tokens are created server-side via the `auth_tokens.create` endpoint and can be locked to specific model configurations. Unlike OpenAI (Bearer token) and Anthropic (x-api-key), Gemini uses the `x-goog-api-key` header format. There is no organization/project header system like OpenAI's `OpenAI-Organization`. The Python SDK reads the `GEMINI_API_KEY` environment variable automatically when no explicit key is provided.

## Key Facts

- [VERIFIED] Auth header: `x-goog-api-key: YOUR_API_KEY` (GEMAPI-SC-GOOG-APIKEY)
- [VERIFIED] API keys created via Google AI Studio (https://aistudio.google.com/app/apikey) (GEMAPI-SC-GOOG-APIKEY)
- [VERIFIED] Keys associated with Google Cloud projects for billing/permissions (GEMAPI-SC-GOOG-APIKEY)
- [VERIFIED] Python SDK env var: `GEMINI_API_KEY` (auto-detected) (GEMAPI-SC-GOOG-APIKEY)
- [VERIFIED] Ephemeral tokens: short-lived, Live API only (GEMAPI-SC-GOOG-EPHTKN)
- [VERIFIED] Ephemeral token defaults: 1 min newSessionExpireTime, 30 min expireTime (GEMAPI-SC-GOOG-EPHTKN)
- [VERIFIED] Ephemeral tokens can be locked to specific model/config (GEMAPI-SC-GOOG-EPHTKN)

## Use Cases

- **Server-side API calls**: Standard API key in environment variable or explicit parameter
- **Client-side Live API**: Ephemeral tokens for WebSocket connections from browser/mobile
- **Multi-project management**: Separate API keys per Google Cloud project for billing isolation

## Quick Reference

**Auth Header**: `x-goog-api-key: YOUR_API_KEY`
**Key Management**: https://aistudio.google.com/app/apikey
**Environment Variable**: `GEMINI_API_KEY`
**Ephemeral Tokens**: `POST /v1alpha/authTokens` (Live API only)

## API Key Authentication

### Header Format

```
x-goog-api-key: YOUR_API_KEY
```

All requests to the Gemini API must include this header. The key is a string obtained from Google AI Studio.

### Google Cloud Projects

API keys are tied to Google Cloud projects which control:
- **Billing**: Usage charges billed to the project's billing account
- **Permissions**: IAM controls for key management
- **Rate limits**: Applied per project, not per key

Google AI Studio provides a lightweight interface to manage projects. If no project exists, create one in AI Studio or import from Google Cloud.

### Environment Variable Setup

**Linux/macOS (Bash):**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**macOS (Zsh):**
```bash
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

### Security Best Practices

- **Never commit** API keys to source control (Git, etc.)
- **Never expose** keys in client-side code (JavaScript, mobile apps) in production
- **Restrict access**: Limit key usage to specific IP addresses, HTTP referrers, or apps
- **Restrict APIs**: Enable only necessary APIs for each key
- **Regular audits**: Rotate keys periodically
- **Use ephemeral tokens** for any client-side Live API access

## Ephemeral Tokens

### Overview

Ephemeral tokens are short-lived authentication tokens for client-to-server Live API WebSocket connections. They prevent long-lived API key exposure on clients.

**Flow:**
1. Client authenticates with your backend
2. Backend requests ephemeral token from Gemini API (v1alpha)
3. Gemini API issues short-lived token
4. Backend sends token to client
5. Client uses token as API key for WebSocket connection

### REST API

**Create Ephemeral Token:**

```
POST https://generativelanguage.googleapis.com/v1alpha/authTokens
```

**Request Body:**

```json
{
  "uses": 1,
  "expireTime": "2026-03-20T03:00:00Z",
  "newSessionExpireTime": "2026-03-20T02:31:00Z"
}
```

**Parameters:**
- **uses** (integer): Number of sessions this token can start (default: 1)
- **expireTime** (string, ISO 8601): When token expires for sending messages (default: 30 min)
- **newSessionExpireTime** (string, ISO 8601): When token expires for starting new sessions (default: 1 min)
- **liveConnectConstraints** (object, optional): Lock token to specific model/config

**Response:**

```json
{
  "name": "ephemeral-token-string-here"
}
```

### Locked Tokens

Tokens can be constrained to specific configurations for additional security:

```json
{
  "uses": 1,
  "liveConnectConstraints": {
    "model": "gemini-2.5-flash-native-audio-preview",
    "config": {
      "sessionResumption": {},
      "temperature": 0.7,
      "responseModalities": ["AUDIO"]
    }
  }
}
```

### Limitations

- Ephemeral tokens are **Live API only** - not supported for REST endpoints
- Requires `v1alpha` API version for token creation
- Session resumption needed every 10 minutes within the expireTime window

## Python Examples

### Example 1: Environment Variable (Recommended)

```python
from google import genai
import os

# SDK auto-detects GEMINI_API_KEY environment variable
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello, world!"
)
print(response.text)
```

### Example 2: Explicit API Key

```python
from google import genai
import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello, world!"
)
print(response.text)
```

### Example 3: Create Ephemeral Token (Server-Side)

```python
import datetime
from google import genai

client = genai.Client(
    http_options={"api_version": "v1alpha"}
)

now = datetime.datetime.now(tz=datetime.timezone.utc)

token = client.auth_tokens.create(
    config={
        "uses": 1,
        "expire_time": now + datetime.timedelta(minutes=30),
        "new_session_expire_time": now + datetime.timedelta(minutes=1),
        "http_options": {"api_version": "v1alpha"},
    }
)

# Send token.name to client for WebSocket connection
print(f"Ephemeral token: {token.name}")
```

### Example 4: Locked Ephemeral Token

```python
import datetime
from google import genai

client = genai.Client(
    http_options={"api_version": "v1alpha"}
)

token = client.auth_tokens.create(
    config={
        "uses": 1,
        "live_connect_constraints": {
            "model": "gemini-2.5-flash-native-audio-preview",
            "config": {
                "session_resumption": {},
                "temperature": 0.7,
                "response_modalities": ["AUDIO"],
            },
        },
        "http_options": {"api_version": "v1alpha"},
    }
)
print(f"Locked token: {token.name}")
```

## cURL Examples

### Example: Basic Authenticated Request

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "contents": [{"parts": [{"text": "Hello"}]}]
  }'
```

## Comparison with Other APIs

### vs OpenAI

- **Header**: Gemini: `x-goog-api-key: KEY` | OpenAI: `Authorization: Bearer KEY`
- **Key management**: Gemini: Google AI Studio | OpenAI: platform.openai.com
- **Organization**: Gemini: via Google Cloud projects | OpenAI: `OpenAI-Organization` header
- **Client tokens**: Gemini: ephemeral tokens (Live API) | OpenAI: no equivalent
- **Env var**: Gemini: `GEMINI_API_KEY` | OpenAI: `OPENAI_API_KEY`

### vs Anthropic

- **Header**: Gemini: `x-goog-api-key: KEY` | Anthropic: `x-api-key: KEY`
- **Version header**: Gemini: none (URL path) | Anthropic: `anthropic-version: 2023-06-01`
- **Key management**: Gemini: Google AI Studio | Anthropic: console.anthropic.com
- **Client tokens**: Gemini: ephemeral tokens | Anthropic: no equivalent

## Error Responses

- **401 Unauthorized**: Missing or invalid API key
- **403 Forbidden**: API key restricted (IP, referrer, API not enabled)
- **429 Too Many Requests**: Rate limit exceeded for project

## Rate Limiting / Throttling

Rate limits are per-project, not per-key. Multiple keys in the same project share limits. See GEMAPI-IN04 for details.

## Limitations and Known Issues

- [VERIFIED] Ephemeral tokens only work with Live API, not REST endpoints (GEMAPI-SC-GOOG-EPHTKN)
- [VERIFIED] Token creation requires v1alpha API version (GEMAPI-SC-GOOG-EPHTKN)
- [COMMUNITY] Leaked API keys may be automatically blocked by Google's security measures (GEMAPI-SC-GOOG-TROUBL)

## Gotchas and Quirks

- SDK auto-detects `GEMINI_API_KEY` env var - no explicit configuration needed if set
- API keys are project-scoped, not user-scoped - all keys in a project share rate limits
- No `Authorization: Bearer` support - migrating from OpenAI requires header change
- Ephemeral tokens use `v1alpha` version, not `v1beta`

## Sources

- GEMAPI-SC-GOOG-APIKEY: https://ai.google.dev/gemini-api/docs/api-key [VERIFIED]
- GEMAPI-SC-GOOG-EPHTKN: https://ai.google.dev/gemini-api/docs/ephemeral-tokens [VERIFIED]
- GEMAPI-SC-GOOG-APIOVW: https://ai.google.dev/gemini-api/docs/api-overview [VERIFIED]

## Document History

**[2026-03-20 02:50]**
- Initial document created with full auth and ephemeral token documentation
