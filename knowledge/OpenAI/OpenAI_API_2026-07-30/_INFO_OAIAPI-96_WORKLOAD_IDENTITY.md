# Workload Identity Federation

**Doc ID**: OAIAPI-IN96
**Goal**: Document Workload Identity Federation for keyless authentication via external identity tokens
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN02_AUTHENTICATION.md [OAIAPI-IN02]` for authentication context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Overview

Workload Identity Federation (released 2026-05) allows trusted workloads to exchange externally issued identity tokens (e.g., from AWS, GCP, Azure, GitHub Actions) for short-lived OpenAI access tokens. This eliminates the need to store long-lived API keys in application environments.

## How It Works

1. Workload obtains an identity token from its native identity provider (AWS IAM, GCP Service Account, Azure Managed Identity, GitHub OIDC)
2. Workload sends the external token to OpenAI's token exchange endpoint
3. OpenAI validates the token against the configured trust relationship
4. OpenAI issues a short-lived access token scoped to the configured project
5. Workload uses the short-lived token for API requests

## REST API

### Token Exchange

**Endpoint**: `POST /v1/auth/token-exchange`

**Request**:

```json
{
  "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
  "subject_token": "<external-identity-token>",
  "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
  "audience": "openai-api"
}
```

**Response** (`200 OK`):

```json
{
  "access_token": "oai_live_abc123...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## SDK Examples

### Python

```python
from openai import OpenAI

# Using workload identity - SDK handles token exchange automatically
# when configured with identity provider credentials
client = OpenAI(
    # No api_key needed - uses workload identity
    organization="org-abc123",
    project="proj-xyz789",
)

# Token exchange happens transparently
response = client.responses.create(
    model="gpt-5.6-terra",
    input="Hello, world!",
)
print(response.output_text)
```

### AWS Integration

```python
import boto3
from openai import OpenAI

# Get AWS identity token
sts = boto3.client("sts")
identity = sts.get_caller_identity()

# OpenAI SDK with AWS workload identity
client = OpenAI(
    # Configured via environment or explicit identity provider config
)

response = client.responses.create(
    model="gpt-5.6-terra",
    input="Summarize today's key metrics.",
)
print(response.output_text)
```

## Configuration

Trust relationships are configured in the OpenAI platform:

1. Navigate to Settings > Security > Workload Identity
2. Add a trust relationship specifying:
   - Identity provider (AWS, GCP, Azure, GitHub, custom OIDC)
   - Allowed subjects/audiences
   - Project scope
3. Assign permissions to the federated identity

## Security Benefits

- No long-lived API keys to rotate or leak
- Short-lived tokens (default 1 hour) limit blast radius
- Audit logs show workload identity in addition to token usage
- Tokens scoped to specific projects

## Gotchas and Quirks

- Token exchange adds ~100ms latency on first request (subsequent requests use cached token until expiry)
- External identity provider must be OIDC-compliant
- Trust relationship changes take up to 5 minutes to propagate
- SDK v2.39.0+ required for workload identity audit log support

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

- https://developers.openai.com/api/docs/guides/workload-identity-federation
- SDK changelog v2.39.0 (workload identity in audit logs)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Initial documentation for Workload Identity Federation
