# INFO: Authentication and API Key Management

**Doc ID**: GROKAPI-IN02
**Goal**: API key creation, Bearer auth, teams, ACLs, management key operations
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok API uses Bearer token authentication with API keys created via the xAI Console or Management API. Keys are scoped to teams, with Access Control Lists (ACLs) controlling which models and endpoints each key can access. Two key types exist: standard API keys for inference requests and Management API keys for administrative operations (key CRUD, ACL management, audit logs). The Management API runs on a separate host (`management-api.x.ai`). ACLs use a path-based format (`api-key:model:*`, `api-key:endpoint:chat`) for granular access control. Keys can have per-key rate limits (QPS, QPM, TPM). Key propagation across clusters may have slight delay after creation. Teams support automatic domain-based membership. [VERIFIED] (GROKAPI-SC-XAI-MGMTAPI | https://docs.x.ai/developers/management-api)

## Key Facts

- [VERIFIED] Auth header: `Authorization: Bearer <XAI_API_KEY>` (GROKAPI-SC-XAI-QUICKSTART)
- [VERIFIED] API key env var: `XAI_API_KEY` (auto-read by SDKs) (GROKAPI-SC-XAI-QUICKSTART)
- [VERIFIED] Console key management: https://console.x.ai/team/default/api-keys (GROKAPI-SC-XAI-QUICKSTART)
- [VERIFIED] Management API host: `management-api.x.ai` (separate from inference API) (GROKAPI-SC-XAI-MGMTAPI)
- [VERIFIED] ACL types: `api-key:model` and `api-key:endpoint` (GROKAPI-SC-XAI-MGMTAPI)
- [VERIFIED] Wildcard ACL: `api-key:model:*` and `api-key:endpoint:*` for full access (GROKAPI-SC-XAI-MGMTAPI)
- [VERIFIED] Endpoint ACLs: `api-key:endpoint:chat`, `api-key:endpoint:image` (GROKAPI-SC-XAI-MGMTAPI)
- [VERIFIED] Per-key rate limits: QPS, QPM, TPM configurable at creation (GROKAPI-SC-XAI-MGMTAPI)
- [VERIFIED] Key propagation delay: slight delay between creation and availability across clusters (GROKAPI-SC-XAI-MGMTAPI)

## Quick Reference

- **Auth header**: `Authorization: Bearer <API_KEY>`
- **Inference API**: `https://api.x.ai/v1/`
- **Management API**: `https://management-api.x.ai/auth/`
- **Key info endpoint**: `GET /v1/api-key` (returns key metadata without exposing full key)
- **Console**: https://console.x.ai/team/default/api-keys

## Authentication Flow

### Standard API Request

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Hello"}],
)
```

### Check Current API Key Info

```bash
curl https://api.x.ai/v1/api-key \
  -H "Authorization: Bearer $XAI_API_KEY"
```

Response:
```json
{
  "redacted_api_key": "xai-...b14o",
  "user_id": "59fbe5f2-...",
  "name": "My API Key",
  "team_id": "5ea6f6bd-...",
  "acls": ["api-key:model:*", "api-key:endpoint:*"],
  "api_key_id": "ae1e1841-...",
  "team_blocked": false,
  "api_key_blocked": false,
  "api_key_disabled": false
}
```

## Management API Operations

### Create API Key

```bash
curl https://management-api.x.ai/auth/teams/{teamId}/api-keys \
  -X POST \
  -H "Authorization: Bearer <MANAGEMENT_KEY>" \
  -d '{
    "name": "Production Key",
    "acls": ["api-key:model:*", "api-key:endpoint:*"],
    "qps": 5,
    "qpm": 100,
    "tpm": null
  }'
```

### List API Keys

```bash
curl "https://management-api.x.ai/auth/teams/{teamId}/api-keys?pageSize=10&paginationToken=" \
  -H "Authorization: Bearer <MANAGEMENT_KEY>"
```

### Update API Key

```bash
curl https://management-api.x.ai/auth/api-keys/{apiKeyId} \
  -X PUT \
  -H "Authorization: Bearer <MANAGEMENT_KEY>" \
  -d '{
    "apiKey": {"qpm": 200},
    "fieldMask": "qpm"
  }'
```

### Delete API Key

```bash
curl https://management-api.x.ai/auth/api-keys/{apiKeyId} \
  -X DELETE \
  -H "Authorization: Bearer <MANAGEMENT_KEY>"
```

### Check Key Propagation

```bash
curl https://management-api.x.ai/auth/api-keys/{apiKeyId}/propagation \
  -H "Authorization: Bearer <MANAGEMENT_KEY>"
```

### List Available ACLs

```bash
curl https://management-api.x.ai/auth/teams/{teamId}/endpoints \
  -H "Authorization: Bearer <MANAGEMENT_KEY>"
```

### Validate Management Key

```bash
curl https://management-api.x.ai/auth/management-keys/validation \
  -H "Authorization: Bearer <MANAGEMENT_KEY>"
```

## ACL Reference

- `api-key:model:*` - Access to all models
- `api-key:model:<model-name>` - Access to specific model (e.g., `api-key:model:grok-4.20-beta-latest-non-reasoning`)
- `api-key:endpoint:*` - Access to all endpoints
- `api-key:endpoint:chat` - Chat and vision models only
- `api-key:endpoint:image` - Image generation only

## Differences from Other APIs

### vs OpenAI

- **Same auth header**: Both use `Authorization: Bearer`
- **Management API**: xAI has separate management host (`management-api.x.ai`); OpenAI manages via platform dashboard or Admin API
- **ACLs**: xAI has path-based ACLs on keys; OpenAI uses project-scoped keys
- **Per-key rate limits**: xAI allows QPS/QPM/TPM per key; OpenAI sets limits at org/project level
- **Key info endpoint**: `GET /v1/api-key` returns metadata (OpenAI has no equivalent)

### vs Anthropic

- **Auth header**: xAI uses `Authorization: Bearer` vs Anthropic `x-api-key` header
- **Key management**: xAI Management API vs Anthropic Console-only
- **ACLs**: xAI has model/endpoint ACLs; Anthropic has workspace-level keys

### vs Gemini

- **Auth header**: xAI uses `Authorization: Bearer` vs Gemini `x-goog-api-key` query param or header
- **Management**: xAI has programmatic Management API; Gemini uses Google Cloud IAM

## Error Responses

- **401 Unauthorized**: No authorization header or invalid token - supply valid `Authorization: Bearer <key>`
- **403 Forbidden**: Key/team lacks permission or is blocked - contact team admin

## Limitations and Known Issues

- [VERIFIED] Key propagation across clusters has slight delay after creation (GROKAPI-SC-XAI-MGMTAPI)
- [VERIFIED] Management API is on separate host from inference API (GROKAPI-SC-XAI-MGMTAPI)

## Sources

- GROKAPI-SC-XAI-QUICKSTART | https://docs.x.ai/developers/quickstart | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MGMTAPI | https://docs.x.ai/developers/management-api | Accessed: 2026-03-20
- GROKAPI-SC-XAI-RESTREF | https://docs.x.ai/llms.txt | Accessed: 2026-03-20

## Document History

**[2026-03-20 03:15]**
- Initial document created with auth flow, Management API operations, ACL reference
