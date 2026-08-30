# Organization Users and Invites

**Doc ID**: OAIAPI-IN48
**Goal**: Document organization user management and invite operations
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

Organization Users API manages members of an OpenAI organization. List users (GET /v1/organization/users), retrieve user details, update roles (POST), and remove users (DELETE). Each user has a role (owner, admin, member) and associated email. Invites API manages pending invitations: create invites with email and role, list, retrieve, and delete. Users identified by user IDs (`user-xxx`). Role assignments define permissions at organization level. Only owners and admins can manage users and invites. Removed users lose access immediately. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-ADMORG)

## Key Facts

- **User roles**: owner, admin, member [VERIFIED] (OAIAPI-SC-OAI-ADMORG)
- **Invite flow**: Create invite -> user accepts via email -> becomes org member [VERIFIED] (OAIAPI-SC-OAI-ADMORG)
- **Removal**: Immediate access revocation [VERIFIED] (OAIAPI-SC-OAI-ADMORG)
- **Admin key required**: All endpoints require admin API key [VERIFIED] (OAIAPI-SC-OAI-ADMOVW)

## Quick Reference

```
Users:
  GET    /v1/organization/users              # List users
  GET    /v1/organization/users/{user_id}    # Retrieve user
  POST   /v1/organization/users/{user_id}    # Update user role
  DELETE /v1/organization/users/{user_id}    # Remove user

Invites:
  GET    /v1/organization/invites            # List invites
  POST   /v1/organization/invites            # Create invite
  GET    /v1/organization/invites/{invite_id}# Retrieve invite
  DELETE /v1/organization/invites/{invite_id}# Delete invite
```

## User Object

```json
{
  "object": "organization.user",
  "id": "user-abc123",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "role": "admin",
  "added_at": 1711471533
}
```

## Invite Object

```json
{
  "object": "organization.invite",
  "id": "invite-abc123",
  "email": "bob@example.com",
  "role": "member",
  "status": "pending",
  "invited_at": 1711471533,
  "expires_at": 1712081133
}
```

## SDK Examples (Python)

### User and Invite Management

```python
from openai import OpenAI

client = OpenAI(api_key="sk-admin-...")

def invite_user(email: str, role: str = "member"):
    """Invite a user to the organization"""
    try:
        invite = client.organization.invites.create(
            email=email,
            role=role
        )
        print(f"Invited {email} as {role}: {invite.id}")
        return invite
    except Exception as e:
        print(f"Error inviting {email}: {e}")
        return None

def list_users():
    """List all organization users"""
    users = client.organization.users.list(limit=100)
    for user in users.data:
        print(f"  {user.name} ({user.email}) - {user.role}")
    return users.data

def remove_user(user_id: str):
    """Remove user from organization"""
    try:
        client.organization.users.delete(user_id)
        print(f"Removed user: {user_id}")
    except Exception as e:
        print(f"Error: {e}")

invite_user("newdev@example.com", "member")
list_users()
```

### User and Invite Management (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/invites.py, users/users.py
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

def invite_user(email: str, role: str = "member"):
    """Invite a user to the organization"""
    try:
        invite = client.admin.organization.invites.create(
            email=email,
            role=role
        )
        print(f"Invited {email} as {role}: {invite.id}")
        return invite
    except Exception as e:
        print(f"Error inviting {email}: {e}")
        return None

def list_users():
    """List all organization users"""
    users = client.admin.organization.users.list(limit=100)
    for user in users.data:
        print(f"  {user.name} ({user.email}) - {user.role}")
    return users.data

def remove_user(user_id: str):
    """Remove user from organization"""
    try:
        client.admin.organization.users.delete(user_id)
        print(f"Removed user: {user_id}")
    except Exception as e:
        print(f"Error: {e}")

invite_user("newdev@example.com", "member")
list_users()
```

## Error Responses

- **400 Bad Request** - Invalid email or role
- **401 Unauthorized** - Invalid admin API key
- **403 Forbidden** - Insufficient permissions (must be owner/admin)
- **404 Not Found** - User or invite not found
- **409 Conflict** - User already exists or invite already pending

## Differences from Other APIs

- **vs Anthropic**: No programmatic user management API
- **vs Gemini**: Uses Google Cloud IAM for user management
- **vs Grok**: Limited user management API

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
- Enriched from 2026-03-20 IN48 (19 -> 120 lines)

**[2026-05-22 11:45]**
- Stub created
