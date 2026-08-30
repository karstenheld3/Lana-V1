# Authentication

**Doc ID**: ANTAPI-IN04
**Goal**: Document API key authentication, header format, and security practices
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL and general overview

## Summary

The Anthropic API authenticates requests using the `x-api-key` header containing an API key generated from the Anthropic Console. Unlike OpenAI's Bearer token scheme, Anthropic uses a custom header. API keys are scoped to workspaces for access control and spend management. The official SDKs read the `ANTHROPIC_API_KEY` environment variable by default. Since July 8, 2026, API keys support an optional `expires_at` field for automatic expiration.

## Key Facts

- **Auth Header**: `x-api-key: sk-ant-...`
- **Key Format**: Starts with `sk-ant-`
- **Key Source**: Anthropic Console (platform.claude.com/settings/keys)
- **Env Variable**: `ANTHROPIC_API_KEY` (SDK default)
- **Scope**: Keys are scoped to workspaces
- **Expiration**: Optional `expires_at` field on keys (since Jul 8, 2026)
- **Status**: GA

## Authentication Flow

1. Create an account at https://platform.claude.com
2. Generate an API key at https://platform.claude.com/settings/keys
3. Include the key in every request via the `x-api-key` header
4. Optionally scope keys to specific workspaces for access control

## Required Headers

Every API request requires these three headers:

- **`x-api-key`** - Your API key
- **`anthropic-version`** - API version (current: `2023-06-01`)
- **`content-type`** - Must be `application/json`

## Quick Reference

```python
import anthropic

# Option 1: Environment variable (recommended)
# Set ANTHROPIC_API_KEY in your environment
client = anthropic.Anthropic()

# Option 2: Explicit key
client = anthropic.Anthropic(api_key="sk-ant-your-key-here")

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

### Raw HTTP

```
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{"model": "claude-opus-5", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hello"}]}'
```

## Workspace Scoping

API keys can be associated with specific workspaces to:

- Segment usage tracking per use case
- Control spend limits per workspace
- Restrict access to specific resources

Use the Console to create workspace-scoped keys under Account Settings.

## Error Codes

- **401** `authentication_error` - Invalid or missing API key
- **402** `billing_error` - Payment issue on the account
- **403** `permission_error` - API key lacks permission for the resource

## Gotchas and Quirks

- Unlike OpenAI (`Authorization: Bearer sk-...`), Anthropic uses `x-api-key` header directly
- The SDK reads `ANTHROPIC_API_KEY` environment variable by default; no explicit key needed if set
- Third-party platforms (Bedrock, Vertex AI) use their own authentication (SigV4, OAuth2), not x-api-key
- API keys start with `sk-ant-` prefix
- API keys can have an `expires_at` timestamp (since Jul 8, 2026); expired keys return 401
- Key expiration is optional; keys without `expires_at` never expire

## Related Endpoints

- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` - API overview
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` - Versioning and beta headers
- `_INFO_ANTAPI-34_ADMIN_WORKSPACES.md [ANTAPI-IN34]` - Workspace and API key management

## Sources

- ANTAPI-SC-ANTH-APIOVW - https://platform.claude.com/docs/en/api/overview - Auth headers, key management
- ANTAPI-SC-ANTH-QKSTART - https://platform.claude.com/docs/en/get-started - Setup instructions

## SDK Verification

1 Python example verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `_client.py` (lines 53-94): `Anthropic(api_key=None)` reads `ANTHROPIC_API_KEY` env var; explicit `api_key` param supported

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: API key expiration (expires_at field, Jul 8, 2026)

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:45]**
- Added: SDK verification section (anthropic 0.120.0, 1 example valid)

**[2026-03-20 02:15]**
- Initial documentation created from API overview and quickstart pages
