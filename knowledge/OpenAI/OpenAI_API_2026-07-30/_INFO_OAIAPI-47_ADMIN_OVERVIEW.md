# Administration Overview

**Doc ID**: OAIAPI-IN47
**Goal**: Document the Administration API hierarchy - organizations, projects, RBAC model, and admin API keys
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Administration API provides programmatic management of OpenAI organizations. The hierarchy is Organization -> Projects -> Resources (API keys, service accounts, rate limits). Access requires Admin API Keys - these keys cannot be used for non-admin endpoints. Organization-level resources include users, invites, groups, custom roles, certificates, and audit logs. Project-level resources include users, groups, service accounts, API keys, and rate limits. The RBAC model supports built-in roles (owner, admin, member) and custom roles with granular permissions. All admin endpoints use the `/v1/organization/` base path. **NEW 2026-05**: Admin APIs now supported in all official SDKs (Python, Node, Go, Ruby, Java). See IN80 for new permissions and retention endpoints. [VERIFIED] (OAIAPI-SC-OAI-ADMOVW, OAIAPI-SC-OAI-GADMSK)

## Key Facts

- **Hierarchy**: Organization -> Projects -> Resources [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **Admin API Keys**: Required for all admin endpoints; cannot be used for regular API calls [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **Base path**: `/v1/organization/` for all admin endpoints [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **RBAC**: Built-in roles (owner, admin, member) + custom roles [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **Audit logs**: Complete action history for compliance [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **SDK support**: Admin APIs in all SDKs since 2026-05 [VERIFIED] (OAIAPI-SC-OAI-GADMSK)

## Quick Reference

```
Admin API Key Creation:
  POST /v1/organization/audit_logs/admin_api_keys   # Create admin API key

Organization Level:
  /v1/organization/users          # Users management
  /v1/organization/invites        # Invite management
  /v1/organization/groups         # Groups management
  /v1/organization/roles          # Custom roles
  /v1/organization/certificates   # mTLS certificates
  /v1/organization/audit_logs     # Audit logs
  /v1/organization/usage          # Usage tracking
  /v1/organization/costs          # Cost reporting

Project Level:
  /v1/organization/projects                          # Project CRUD
  /v1/organization/projects/{id}/users               # Project users
  /v1/organization/projects/{id}/groups              # Project groups
  /v1/organization/projects/{id}/service_accounts    # Service accounts
  /v1/organization/projects/{id}/api_keys            # API keys
  /v1/organization/projects/{id}/rate_limits         # Rate limits

Headers:
  Authorization: Bearer $ADMIN_API_KEY
  Content-Type: application/json
```

## Organization Hierarchy

```
Organization (org-xxx)
├─> Users (members with roles)
├─> Groups (collections of users)
├─> Custom Roles (permission sets)
├─> Certificates (mTLS)
├─> Audit Logs (action history)
├─> Usage / Costs (billing)
└─> Projects (proj-xxx)
    ├─> Project Users (with project roles)
    ├─> Project Groups
    ├─> Service Accounts (svc_acct-xxx)
    ├─> API Keys (sk-xxx)
    └─> Rate Limits (per-model limits)
```

## Built-in Roles

- **Owner**: Full organization access including billing and admin management
- **Admin**: Manage users, projects, and settings (no billing)
- **Member**: Access assigned projects, use API within project scope

## Admin API Keys

Admin API keys are separate from regular API keys:
- Created via POST /v1/organization/audit_logs/admin_api_keys
- Can only call admin endpoints (not Responses, Chat, etc.)
- Should be treated as highly sensitive credentials
- Use for automation, CI/CD, and programmatic org management

## SDK Examples (Python)

### Create Admin API Key

```python
from openai import OpenAI

client = OpenAI(api_key="sk-admin-...")

admin_key = client.organization.admin_api_keys.create(
    name="CI/CD Admin Key"
)

print(f"Admin Key: {admin_key.value}")
print(f"Key ID: {admin_key.id}")
```

### Organization Overview

```python
from openai import OpenAI

client = OpenAI(api_key="sk-admin-...")

def get_org_overview():
    """Get complete organization overview"""
    users = client.organization.users.list(limit=100)
    projects = client.organization.projects.list(limit=100)
    groups = client.organization.groups.list(limit=100)
    
    overview = {
        "users": len(users.data),
        "projects": len(projects.data),
        "groups": len(groups.data),
    }
    
    print(f"Users: {overview['users']}")
    print(f"Projects: {overview['projects']}")
    print(f"Groups: {overview['groups']}")
    
    for proj in projects.data:
        print(f"  Project: {proj.name} ({proj.id}) - {proj.status}")
    
    return overview

try:
    get_org_overview()
except Exception as e:
    print(f"Error: {e}")
```

### Create Admin API Key (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/admin_api_keys.py
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

admin_key = client.admin.organization.admin_api_keys.create(
    name="CI/CD Admin Key"
)

print(f"Admin Key: {admin_key.value}")
print(f"Key ID: {admin_key.id}")
```

### Organization Overview (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

def get_org_overview():
    """Get complete organization overview"""
    users = client.admin.organization.users.list(limit=100)
    projects = client.admin.organization.projects.list(limit=100)
    groups = client.admin.organization.groups.list(limit=100)
    
    overview = {
        "users": len(users.data),
        "projects": len(projects.data),
        "groups": len(groups.data),
    }
    
    print(f"Users: {overview['users']}")
    print(f"Projects: {overview['projects']}")
    print(f"Groups: {overview['groups']}")
    
    for proj in projects.data:
        print(f"  Project: {proj.name} ({proj.id}) - {proj.status}")
    
    return overview

try:
    get_org_overview()
except Exception as e:
    print(f"Error: {e}")
```

## Error Responses

- **401 Unauthorized** - Invalid or non-admin API key
- **403 Forbidden** - Insufficient admin permissions
- **404 Not Found** - Resource not found
- **429 Too Many Requests** - Rate limit exceeded

## Differences from Other APIs

- **vs Anthropic**: Anthropic has organization management via console only, no programmatic admin API
- **vs Gemini**: Google Cloud IAM handles access control; no API-level admin endpoints
- **vs Grok**: Limited organization management API

## Limitations and Known Issues

- **Admin key separation**: Admin keys cannot call regular API endpoints [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **No cross-org management**: Each admin key scoped to one organization [ASSUMED]

## Gotchas and Quirks

- **Admin key prefix**: Admin API keys use `sk-admin-` prefix, distinct from regular `sk-` keys [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)
- **SDK access**: Use `client.admin.organization.*` namespace in SDKs since 2026-05 [VERIFIED] (OAIAPI-SC-OAI-GADMSK)

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

- OAIAPI-SC-OAI-ADMOVW - Administration Overview
- OAIAPI-SC-OAI-GADMSK - Admin API SDK support guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:05]**
- Enriched from 2026-03-20 IN47 (19 -> 165 lines)
- Added SDK support note for 2026-05

**[2026-05-22 11:45]**
- Stub created
