# Projects API

**Doc ID**: OAIAPI-IN50
**Goal**: Document project management - create, retrieve, update, list, archive projects and sub-resources
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN47_ADMIN_OVERVIEW.md [OAIAPI-IN47]` for admin context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Projects API manages isolated environments within an organization. Each project has its own API keys, service accounts, rate limits, and usage tracking. Create, retrieve, update, list, and archive projects. Projects contain sub-resources: users, groups, service accounts, API keys, and rate limits. **NEW 2026-05**: model_permissions, hosted_tool_permissions, data_retention, spend_alerts sub-resources (see IN80). Project-scoped API keys only access resources within their project. Archiving revokes all keys and service accounts. The `OpenAI-Project` header routes API calls to a specific project. [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)

## Key Facts

- **Isolation**: Each project has own keys, accounts, limits, usage [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **Scoped keys**: Project API keys only access that project's resources [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **Archive**: Revokes all keys and service accounts [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **Header routing**: `OpenAI-Project: proj_xxx` header for API calls [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)
- **Cost tracking**: Usage tracked per project [VERIFIED] (OAIAPI-SC-OAI-ADMPRJ)

## Quick Reference

```
Projects:
  POST   /v1/organization/projects                           # Create
  GET    /v1/organization/projects                           # List
  GET    /v1/organization/projects/{project_id}              # Retrieve
  POST   /v1/organization/projects/{project_id}              # Update
  POST   /v1/organization/projects/{project_id}/archive      # Archive

Sub-resources:
  /v1/organization/projects/{id}/users                       # Project users
  /v1/organization/projects/{id}/groups                      # Project groups
  /v1/organization/projects/{id}/service_accounts            # Service accounts
  /v1/organization/projects/{id}/api_keys                    # API keys
  /v1/organization/projects/{id}/rate_limits                 # Rate limits
  /v1/organization/projects/{id}/model_permissions           # NEW 2026-05
  /v1/organization/projects/{id}/hosted_tool_permissions     # NEW 2026-05
  /v1/organization/projects/{id}/data_retention              # NEW 2026-05
  /v1/organization/projects/{id}/spend_alerts                # NEW 2026-05
```

## Project Object

```json
{
  "object": "organization.project",
  "id": "proj_abc123",
  "name": "Production App",
  "status": "active",
  "created_at": 1711471533,
  "archived_at": null
}
```

### Status Values

- **active**: Project is operational
- **archived**: Project is archived, all keys revoked

## SDK Examples (Python)

### Project Lifecycle Management

```python
from openai import OpenAI

client = OpenAI(api_key="sk-admin-...")

# Create project
project = client.organization.projects.create(
    name="Production API",
    description="Production environment for customer-facing API"
)
print(f"Project: {project.id}")

# Add user to project
client.organization.projects.users.create(
    project_id=project.id,
    user_id="user-abc123",
    role="member"
)

# Create service account
svc = client.organization.projects.service_accounts.create(
    project_id=project.id,
    name="CI/CD Pipeline"
)
print(f"Service Account: {svc.id}")
print(f"API Key: {svc.api_key.value}")

# Set rate limits
client.organization.projects.rate_limits.update(
    project_id=project.id,
    model="gpt-5.6-sol",
    max_requests_per_minute=100,
    max_tokens_per_minute=50000
)

# List all projects
projects = client.organization.projects.list(limit=100)
for p in projects.data:
    print(f"  {p.name} ({p.id}) - {p.status}")
```

### Project Lifecycle Management (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/projects/
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

# Create project
project = client.admin.organization.projects.create(
    name="Production API"
)
print(f"Project: {project.id}")

# Add user to project
client.admin.organization.projects.users.create(
    project_id=project.id,
    user_id="user-abc123",
    role="member"
)

# Create service account
svc = client.admin.organization.projects.service_accounts.create(
    project_id=project.id,
    name="CI/CD Pipeline"
)
print(f"Service Account: {svc.id}")
print(f"API Key: {svc.api_key.value}")

# Set rate limits (SDK uses update_rate_limit, not update)
# Note: requires rate_limit_id, not model name
limits = client.admin.organization.projects.rate_limits.list_rate_limits(
    project_id=project.id
)
for rl in limits.data:
    if rl.model == "gpt-5.5":
        client.admin.organization.projects.rate_limits.update_rate_limit(
            rate_limit_id=rl.id,
            project_id=project.id,
            max_requests_per_1_minute=100,
            max_tokens_per_1_minute=50000
        )

# List all projects
projects = client.admin.organization.projects.list(limit=100)
for p in projects.data:
    print(f"  {p.name} ({p.id}) - {p.status}")
```

## Error Responses

- **400 Bad Request** - Invalid project parameters
- **401 Unauthorized** - Invalid admin API key
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Project not found

## Differences from Other APIs

- **vs Anthropic**: Anthropic has workspaces (similar concept) but limited API management
- **vs Gemini**: Google Cloud projects with IAM (different abstraction level)
- **vs Grok**: No project isolation API

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

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:15]**
- Enriched from 2026-03-20 IN50 (19 -> 125 lines)
- Added new 2026-05 sub-resources, updated model refs to gpt-5.5

**[2026-05-22 11:45]**
- Stub created
