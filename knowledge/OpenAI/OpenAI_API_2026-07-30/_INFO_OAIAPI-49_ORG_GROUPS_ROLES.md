# Organization Groups and Custom Roles

**Doc ID**: OAIAPI-IN49
**Goal**: Document organization groups for bulk access control and custom roles for granular permissions
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

Organization Groups API manages collections of users for bulk access control. Create groups, add/remove members, and assign groups to projects. Groups simplify permission management - assign a group to a project instead of individual users. Custom Roles API enables granular permission definitions beyond built-in roles (owner, admin, member). Create roles with specific permission sets, then assign to users or groups. Group membership changes take effect immediately. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-ADMORG)

## Key Facts

- **Groups**: Collections of users for bulk access management [VERIFIED] (OAIAPI-SC-OAI-ADMORG)
- **Custom roles**: Granular permission sets beyond owner/admin/member [VERIFIED] (OAIAPI-SC-OAI-ADMORG)
- **Project assignment**: Groups can be assigned to projects with specific roles [VERIFIED] (OAIAPI-SC-OAI-ADMORG)
- **Immediate effect**: Membership and role changes take effect immediately [VERIFIED] (OAIAPI-SC-OAI-ADMORG)

## Quick Reference

```
Groups:
  POST   /v1/organization/groups                          # Create group
  GET    /v1/organization/groups                          # List groups
  GET    /v1/organization/groups/{group_id}               # Retrieve group
  POST   /v1/organization/groups/{group_id}               # Update group
  DELETE /v1/organization/groups/{group_id}               # Delete group

Roles:
  POST   /v1/organization/roles                           # Create custom role
  GET    /v1/organization/roles                           # List roles
  GET    /v1/organization/roles/{role_id}                 # Retrieve role
  POST   /v1/organization/roles/{role_id}                 # Update role
  DELETE /v1/organization/roles/{role_id}                 # Delete role
```

## Group Object

```json
{
  "object": "organization.group",
  "id": "group-abc123",
  "name": "Engineering Team",
  "description": "Backend and frontend engineers",
  "created_at": 1711471533,
  "metadata": {}
}
```

## Role Object

```json
{
  "object": "organization.role",
  "id": "role-abc123",
  "name": "Developer",
  "description": "Can create API keys and use API endpoints",
  "permissions": [
    "api_keys.create",
    "api_keys.read",
    "projects.read",
    "usage.read"
  ],
  "created_at": 1711471533,
  "is_builtin": false
}
```

## SDK Examples (Python)

### Group and Role Management

```python
from openai import OpenAI

client = OpenAI(api_key="sk-admin-...")

# Create a custom role
role = client.organization.roles.create(
    name="Developer",
    description="API access with usage visibility",
    permissions=["api_keys.create", "api_keys.read", "projects.read", "usage.read"]
)
print(f"Role: {role.id}")

# Create a group
group = client.organization.groups.create(
    name="Backend Team",
    description="Backend engineering team"
)
print(f"Group: {group.id}")

# List all roles
roles = client.organization.roles.list()
for r in roles.data:
    builtin = " (built-in)" if r.is_builtin else ""
    print(f"  {r.name}{builtin}: {len(r.permissions)} permissions")
```

### Group and Role Management (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/roles.py, groups/groups.py
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

# Create a custom role (SDK uses role_name, not name)
role = client.admin.organization.roles.create(
    role_name="Developer",
    description="API access with usage visibility",
    permissions=["api_keys.create", "api_keys.read", "projects.read", "usage.read"]
)
print(f"Role: {role.id}")

# Create a group (SDK only accepts name, not description)
group = client.admin.organization.groups.create(
    name="Backend Team"
)
print(f"Group: {group.id}")

# List all roles
roles = client.admin.organization.roles.list()
for r in roles.data:
    print(f"  {r.role_name}: {r.description}")
```

## Differences from Other APIs

- **vs Anthropic**: No groups or custom roles API
- **vs Gemini**: Google Cloud IAM provides similar RBAC but via Google Cloud APIs
- **vs Grok**: No custom roles API

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

- OAIAPI-SC-OAI-ADMORG - Organization Administration API

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:10]**
- Enriched from 2026-03-20 IN49 (19 -> 110 lines)

**[2026-05-22 11:45]**
- Stub created
