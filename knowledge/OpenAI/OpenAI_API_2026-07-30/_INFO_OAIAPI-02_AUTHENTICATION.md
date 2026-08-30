# Authentication

**Doc ID**: OAIAPI-IN02
**Goal**: Document API key types, Bearer auth, organization/project headers
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02-SRC]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI API authentication uses Bearer tokens in the `Authorization` header. API keys are generated in the API dashboard and can be scoped to projects. Organization and project membership can be specified via `OpenAI-Organization` and `OpenAI-Project` headers for multi-org accounts. Admin API keys provide elevated access for organization management endpoints. Key types: project API keys (standard access), legacy user API keys (org-wide), admin API keys (administration). **NEW (2026-06)**: Workload Identity Federation enables keyless authentication by exchanging external identity tokens (AWS STS, GCP, Azure AD) for short-lived OpenAI tokens (see IN96). Amazon Bedrock integration uses AWS IAM auth directly (see IN97). The Python SDK reads the `OPENAI_API_KEY` environment variable automatically. [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW, OAIAPI-SC-OAI-GCHLOG)

## Authentication Methods

### Bearer Token

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Multi-Organization / Multi-Project

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Organization: org_abc123" \
  -H "OpenAI-Project: proj_xyz456"
```

### Admin API Key (for Administration endpoints)

Admin API keys are required for all `/v1/organization/*` administration endpoints. Create via API dashboard or programmatically.

### Workload Identity Federation (NEW - 2026-06)

Exchange external identity tokens for short-lived OpenAI API tokens. Eliminates stored API keys. Supported providers: AWS STS, Google Cloud, Azure AD. See IN96 for full details.

### Amazon Bedrock Auth (NEW - 2026-06)

Access OpenAI models via AWS Bedrock endpoint using AWS IAM credentials (no OpenAI API key needed). See IN97 for setup.

## Key Facts

- **Authentication method**: Bearer token via `Authorization` header [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **Key types**: Project API keys (recommended), legacy user API keys, service account keys, admin API keys [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **Multi-org routing**: `OpenAI-Organization` and `OpenAI-Project` headers [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **Key management**: API Dashboard at platform.openai.com [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **Security**: Keys grant full access to account - store securely [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)

## API Key Types

### Project API Keys (Recommended)

- **Scope**: Single project only
- **Use case**: New applications, project-scoped access control
- **Benefit**: Usage tracked per project, better isolation
- **Location**: API keys page in project settings

### Legacy User API Keys

- **Scope**: Organization-wide access
- **Use case**: Personal development, legacy applications
- **Limitation**: Access to all projects in organization
- **Status**: Legacy - project API keys recommended for new applications

### Service Account API Keys

- **Scope**: Project-level, no user association
- **Use case**: Production deployments, CI/CD pipelines
- **Benefit**: Not tied to individual user account
- **Management**: Created through Administration API

### Admin API Keys (NEW)

- **Scope**: Organization administration endpoints
- **Use case**: Model permissions, data retention, spend alerts, org management
- **Required for**: All `/v1/organization/*` endpoints
- **Creation**: API dashboard or programmatically

## API Key Management

### Creating API Keys

1. Navigate to API Dashboard (platform.openai.com)
2. Select organization and project
3. Go to API keys page
4. Click "Create new secret key"
5. Name the key (for identification)
6. Copy key immediately (shown only once)

### Key Security Best Practices

- **Never hardcode keys**: Use environment variables or secret management
- **Rotate keys regularly**: Especially for production environments
- **Delete unused keys**: Remove keys from old projects/environments
- **Use project keys**: Prefer project API keys over user API keys
- **Service accounts for prod**: Use service account keys in production

### Key Storage

Recommended storage methods:
- Environment variables (`OPENAI_API_KEY`)
- Secret management systems (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
- CI/CD secret stores (GitHub Secrets, GitLab CI/CD variables)

Never:
- Commit to version control
- Include in client-side code
- Share via unsecured channels

## SDK Examples (Python)

### Basic Authentication

```python
from openai import OpenAI

# API key loaded from OPENAI_API_KEY environment variable
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Explicit API Key

```python
from openai import OpenAI

# Explicitly provide API key (not recommended for production)
client = OpenAI(api_key="sk-proj-...")

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Multi-Organization Routing

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    organization="org-123456",
    project="proj-abc123"
)

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Admin Client for Administration Endpoints

```python
from openai import OpenAI

# Admin API key required for /v1/organization/* endpoints
admin_client = OpenAI(admin_api_key="sk-admin-...")

# Example: list organization members
members = admin_client.admin.organization.users.list()
```

### Production Setup with Environment Variables

```python
import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-5.6-sol",
        messages=[{"role": "user", "content": "Hello!"}]
    )
except Exception as e:
    print(f"Authentication error: {e}")
```

## Error Responses

- **401 Unauthorized** - Missing or invalid API key
- **403 Forbidden** - API key lacks required permissions for endpoint
- **429 Too Many Requests** - Rate limit exceeded (check project rate limits)

## Rate Limiting

- **Rate limits are project-scoped**: Each project has separate RPM/TPM limits
- **Headers indicate limits**: See `x-ratelimit-*` headers in responses
- **Retry strategy**: Implement exponential backoff on 429 responses

## Differences from Other APIs

- **vs Anthropic**: Uses `x-api-key` header instead of `Authorization: Bearer`
- **vs Gemini**: Uses `x-goog-api-key` query parameter or header
- **vs Grok**: OpenAI-compatible - uses same Bearer authentication

## Limitations and Known Issues

- **User API keys organization-wide**: Cannot scope user API keys to single project [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **Key shown once**: API keys displayed only at creation - must copy immediately [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **No key rotation API**: Must manually create and delete keys for rotation [COMMUNITY]

## Gotchas and Quirks

- **Environment variable name**: Python SDK defaults to `OPENAI_API_KEY` (not `OPENAI_KEY`) [VERIFIED] (OAIAPI-SC-GH-SDKPY)
- **Organization header optional**: Only required for multi-org access or legacy user keys [VERIFIED] (OAIAPI-SC-OAI-OVERVIEW)
- **Service account keys admin only**: Require admin API access to create [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **Admin API key constructor**: Use `OpenAI(admin_api_key=...)` not `OpenAI(api_key=...)` for admin endpoints [TESTED] (SDK v2.45.0)

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

- OAIAPI-SC-OAI-OVERVIEW - API Overview (Authentication section)
- OAIAPI-SC-OAI-ADMOVW - Administration Overview
- OAIAPI-SC-OAI-GADMSK - Admin APIs guide
- OAIAPI-SC-GH-SDKPY - Python SDK documentation

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: Workload Identity Federation (keyless auth via external identity tokens)
- Added: Amazon Bedrock authentication (AWS IAM)
- Added: Cross-references to IN96, IN97
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 22:00]**
- Enriched: Full key types detail, management, security, production examples, gotchas

**[2026-05-22 10:30]**
- Updated from 2026-03-20 version
- Added: Admin API key type documentation
