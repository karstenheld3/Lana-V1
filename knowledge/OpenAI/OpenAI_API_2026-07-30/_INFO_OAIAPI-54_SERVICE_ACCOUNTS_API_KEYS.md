# Service Accounts and API Keys

**Doc ID**: OAIAPI-IN54
**Goal**: Document project service accounts and API key management
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN50_PROJECTS.md [OAIAPI-IN50]` for project context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Service Accounts API manages programmatic identities within projects. Create service accounts to get an associated API key. Service accounts are non-human identities for CI/CD pipelines, backend services, and automated systems. Each has a role (owner, member) and receives an API key on creation. API Keys API manages project-scoped keys: list, retrieve, delete. Keys are project-scoped. Key creation returns the secret value only once. Prefixes: `svc_acct_` (service accounts), `sk-` (keys), `sk-admin-` (admin keys). API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)

## Key Facts

- **Service accounts**: Non-human identities for programmatic access [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **Key on creation**: API key returned only at service account creation time [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **One-time secret**: Key value shown only once, cannot be retrieved later [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **Project-scoped**: Keys only access their project's resources [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **Prefixes**: `svc_acct_` (service accounts), `sk-` (keys), `sk-admin-` (admin keys) [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)

## Quick Reference

```
Service Accounts:
  POST   /v1/organization/projects/{id}/service_accounts                  # Create
  GET    /v1/organization/projects/{id}/service_accounts                  # List
  GET    /v1/organization/projects/{id}/service_accounts/{sa_id}          # Retrieve
  DELETE /v1/organization/projects/{id}/service_accounts/{sa_id}          # Delete

API Keys:
  GET    /v1/organization/projects/{id}/api_keys                          # List keys
  GET    /v1/organization/projects/{id}/api_keys/{key_id}                 # Retrieve key
  DELETE /v1/organization/projects/{id}/api_keys/{key_id}                 # Delete key

Admin API Keys:
  POST   /v1/organization/audit_logs/admin_api_keys                       # Create admin key
  GET    /v1/organization/audit_logs/admin_api_keys                       # List admin keys
  GET    /v1/organization/audit_logs/admin_api_keys/{key_id}              # Retrieve
  DELETE /v1/organization/audit_logs/admin_api_keys/{key_id}              # Delete
```

## Service Account Object

```json
{
  "object": "organization.project.service_account",
  "id": "svc_acct_abc",
  "name": "Production App",
  "role": "member",
  "created_at": 1711471533,
  "api_key": {
    "object": "organization.project.service_account.api_key",
    "value": "sk-abcdefghijklmnop123",
    "name": "Secret Key",
    "created_at": 1711471533,
    "id": "key_abc123"
  }
}
```

Note: `api_key.value` is only present in the creation response.

## API Key Object

```json
{
  "object": "organization.project.api_key",
  "id": "key_abc123",
  "name": "My API Key",
  "redacted_value": "sk-...abc123",
  "created_at": 1711471533,
  "owner": {
    "type": "service_account",
    "service_account": {
      "id": "svc_acct_abc",
      "name": "Production App"
    }
  }
}
```

## SDK Examples (Python)

### Service Account Lifecycle

```python
from openai import OpenAI

client = OpenAI(api_key="sk-admin-...")

project_id = "proj_abc123"

# Create service account
svc = client.organization.projects.service_accounts.create(
    project_id=project_id,
    name="CI/CD Pipeline"
)

# IMPORTANT: Store the key now - it won't be shown again
api_key_value = svc.api_key.value
print(f"Service Account: {svc.id}")
print(f"API Key (SAVE THIS): {api_key_value}")

# List service accounts
accounts = client.organization.projects.service_accounts.list(
    project_id=project_id
)
for sa in accounts.data:
    print(f"  {sa.name} ({sa.id}) - {sa.role}")
```

### Key Rotation

```python
from openai import OpenAI
import time

client = OpenAI(api_key="sk-admin-...")

def rotate_service_account_key(project_id: str, old_sa_id: str, name: str):
    """Rotate a service account by creating new and deleting old"""
    new_svc = client.organization.projects.service_accounts.create(
        project_id=project_id,
        name=f"{name} (rotated {time.strftime('%Y-%m-%d')})"
    )
    
    new_key = new_svc.api_key.value
    print(f"New service account: {new_svc.id}")
    print(f"New API key: {new_key[:10]}...")
    
    # Deploy new key to your services here
    
    try:
        client.organization.projects.service_accounts.delete(
            project_id=project_id,
            service_account_id=old_sa_id
        )
        print(f"Deleted old service account: {old_sa_id}")
    except Exception as e:
        print(f"Warning: Could not delete old account: {e}")
    
    return {"new_sa_id": new_svc.id, "new_key": new_key}

try:
    result = rotate_service_account_key(
        project_id="proj_abc123",
        old_sa_id="svc_acct_old",
        name="Production API"
    )
except Exception as e:
    print(f"Rotation failed: {e}")
```

### Audit API Keys

```python
from openai import OpenAI

client = OpenAI(api_key="sk-admin-...")

def audit_project_keys(project_id: str):
    """List all API keys in a project for security audit"""
    keys = client.organization.projects.api_keys.list(
        project_id=project_id,
        limit=100
    )
    
    print(f"Project {project_id}: {len(keys.data)} API keys")
    for key in keys.data:
        owner_type = key.owner.type
        if owner_type == "service_account":
            owner_name = key.owner.service_account.name
        elif owner_type == "user":
            owner_name = key.owner.user.email
        else:
            owner_name = "unknown"
        
        print(f"  {key.redacted_value} | Owner: {owner_name} ({owner_type}) | Created: {key.created_at}")

try:
    audit_project_keys("proj_abc123")
except Exception as e:
    print(f"Error: {e}")
```

### Service Account Lifecycle (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/projects/service_accounts.py
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

project_id = "proj_abc123"

# Create service account
svc = client.admin.organization.projects.service_accounts.create(
    project_id=project_id,
    name="CI/CD Pipeline"
)

api_key_value = svc.api_key.value
print(f"Service Account: {svc.id}")
print(f"API Key (SAVE THIS): {api_key_value}")

# List service accounts
accounts = client.admin.organization.projects.service_accounts.list(
    project_id=project_id
)
for sa in accounts.data:
    print(f"  {sa.name} ({sa.id}) - {sa.role}")
```

### Key Rotation (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/projects/service_accounts.py
from openai import OpenAI
import time

client = OpenAI(admin_api_key="sk-admin-...")

def rotate_service_account_key(project_id: str, old_sa_id: str, name: str):
    """Rotate a service account by creating new and deleting old"""
    new_svc = client.admin.organization.projects.service_accounts.create(
        project_id=project_id,
        name=f"{name} (rotated {time.strftime('%Y-%m-%d')})"
    )
    
    new_key = new_svc.api_key.value
    print(f"New service account: {new_svc.id}")
    print(f"New API key: {new_key[:10]}...")
    
    try:
        client.admin.organization.projects.service_accounts.delete(
            project_id=project_id,
            service_account_id=old_sa_id
        )
        print(f"Deleted old service account: {old_sa_id}")
    except Exception as e:
        print(f"Warning: Could not delete old account: {e}")
    
    return {"new_sa_id": new_svc.id, "new_key": new_key}

try:
    result = rotate_service_account_key(
        project_id="proj_abc123",
        old_sa_id="svc_acct_old",
        name="Production API"
    )
except Exception as e:
    print(f"Rotation failed: {e}")
```

### Audit API Keys (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/projects/api_keys.py
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

def audit_project_keys(project_id: str):
    """List all API keys in a project for security audit"""
    keys = client.admin.organization.projects.api_keys.list(
        project_id=project_id,
        limit=100
    )
    
    print(f"Project {project_id}: {len(keys.data)} API keys")
    for key in keys.data:
        owner_type = key.owner.type
        if owner_type == "service_account":
            owner_name = key.owner.service_account.name
        elif owner_type == "user":
            owner_name = key.owner.user.email
        else:
            owner_name = "unknown"
        
        print(f"  {key.redacted_value} | Owner: {owner_name} ({owner_type}) | Created: {key.created_at}")

try:
    audit_project_keys("proj_abc123")
except Exception as e:
    print(f"Error: {e}")
```

## Error Responses

- **400 Bad Request** - Invalid parameters
- **401 Unauthorized** - Invalid admin API key
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Service account, key, or project not found
- **409 Conflict** - Name conflict

## Differences from Other APIs

- **vs Anthropic**: Anthropic has API keys via console; no programmatic service account API
- **vs Gemini**: Google Cloud Service Accounts via IAM API (different paradigm)
- **vs Grok**: Limited API key management

## Limitations and Known Issues

- **One-time key visibility**: API key value only shown at creation; cannot be retrieved later [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **No key update**: Cannot rename or change permissions on existing keys; must rotate [ASSUMED]
- **Admin key separation**: Admin keys cannot be used as regular API keys [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)

## Gotchas and Quirks

- **Store key immediately**: The API key secret is in the creation response ONLY [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **Redacted in list**: List/retrieve endpoints show only redacted key values [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **Rotation pattern**: Create new -> deploy -> delete old (no atomic rotation) [ASSUMED]
- **Service account roles**: Can be `owner` or `member` at project level [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)

## TypeScript Examples

### Admin API

```typescript
import OpenAI from "openai";

// Admin API requires admin API key
const client = new OpenAI();

// List organization members
for await (const user of await client.admin.users.list()) {
  console.log(`${user.email}: ${user.role}`);
}
```

## Sources

- OAIAPI-SC-OAI-ADMPRJ - Projects Administration API
- OAIAPI-SC-OAI-ADMOVW - Administration Overview

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:25]**
- Enriched from 2026-03-20 IN54 (19 -> 225 lines)

**[2026-05-22 11:50]**
- Stub created
