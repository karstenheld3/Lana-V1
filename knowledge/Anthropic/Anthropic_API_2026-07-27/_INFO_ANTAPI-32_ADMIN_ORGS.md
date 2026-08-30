# Admin API: Organizations and Invites

**Doc ID**: ANTAPI-IN32
**Goal**: Document Admin API for organization management and user invitations
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-04_AUTHENTICATION.md [ANTAPI-IN04]` for admin API key authentication

## Summary

The Admin API provides organization management endpoints. Organizations are the top-level entity; each contains workspaces, users, and API keys. The Organizations endpoint retrieves the current organization info. The Invites endpoints manage user invitations (create, retrieve, list, delete). Admin API keys with appropriate permissions are required. These endpoints use a separate base URL pattern under `/v1/organizations`.

## Key Facts

- **Organization Endpoint**: `GET /v1/organizations/me`
- **Invites Endpoints**: CRUD at `/v1/invites`
- **Auth**: Admin API key with organization-level permissions
- **Organization Model**: id, name, type="organization"
- **Invite Model**: id, email, role, status, expires_at, created_at, type="invite"
- **Status**: GA

## SDK Compatibility Note

**SDK 0.120.0**: The `client.admin` namespace does NOT exist in the Python SDK. Admin API endpoints require direct HTTP requests using `httpx` or similar. The examples below show the API documentation style; see HTTP examples for working code.

## Organizations

### GET /v1/organizations/me - Get Current Organization

**API Documentation Example** (illustrative - see HTTP below):

```python
import anthropic

client = anthropic.Anthropic()

org = client.admin.organizations.get()
print(f"Org ID: {org.id}")
print(f"Name: {org.name}")
```

**HTTP Example** (SDK 0.120.0 - no `client.admin` namespace):

```python
import httpx
import os

response = httpx.get(
    "https://api.anthropic.com/v1/organizations/me",
    headers={
        "x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"],
        "anthropic-version": "2023-06-01",
    },
)
org = response.json()
print(f"Org ID: {org['id']}")
print(f"Name: {org['name']}")
```

**Response:**

- **id** (`string`) - Organization ID
- **name** (`string`) - Organization name
- **type** (`string`) - Always `"organization"`

## Invites

### POST /v1/invites - Create Invite

**API Documentation Example** (illustrative):

```python
invite = client.admin.invites.create(
    email="newuser@example.com",
    role="user",
)
print(f"Invite ID: {invite.id}")
print(f"Expires: {invite.expires_at}")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.post(
    "https://api.anthropic.com/v1/invites",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
    json={"email": "newuser@example.com", "role": "user"},
)
invite = response.json()
```

### GET /v1/invites/{invite_id} - Get Invite

**API Documentation Example** (illustrative):

```python
invite = client.admin.invites.retrieve("invite-abc123")
print(f"Email: {invite.email}")
print(f"Status: {invite.status}")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.get(
    "https://api.anthropic.com/v1/invites/invite-abc123",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
invite = response.json()
```

### GET /v1/invites - List Invites

**API Documentation Example** (illustrative):

```python
invites = client.admin.invites.list()
for inv in invites:
    print(f"{inv.email}: {inv.status} (role: {inv.role})")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.get(
    "https://api.anthropic.com/v1/invites",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
for inv in response.json()["data"]:
    print(f"{inv['email']}: {inv['status']}")
```

### DELETE /v1/invites/{invite_id} - Delete Invite

**API Documentation Example** (illustrative):

```python
client.admin.invites.delete("invite-abc123")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.delete(
    "https://api.anthropic.com/v1/invites/invite-abc123",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
```

## Invite Model

- **id** (`string`) - Invite ID
- **email** (`string`) - Invitee email
- **role** (`string`) - Organization role assigned
- **status** (`string`) - Invite status (pending, accepted, expired)
- **expires_at** (`string`) - RFC 3339 expiration datetime
- **created_at** (`string`) - RFC 3339 creation datetime
- **type** (`string`) - Always `"invite"`

## Gotchas and Quirks

- Admin API requires organization-level admin API keys
- Organization endpoint only returns the current org (no list of all orgs)
- Invites have an expiration date; expired invites must be re-created

## Related Endpoints

- `_INFO_ANTAPI-33_ADMIN_USERS.md [ANTAPI-IN33]` - User management
- `_INFO_ANTAPI-34_ADMIN_WORKSPACES.md [ANTAPI-IN34]` - Workspace management

## Sources

- ANTAPI-SC-ANTH-ADMIN - https://platform.claude.com/docs/en/api/admin - Admin API reference

## SDK Verification

5 API doc examples re-verified against `anthropic` SDK 0.120.0. Previous HTTP workarounds confirmed correct.

**Confirmed**: `client.admin` namespace does NOT exist in SDK 0.120.0. HTTP examples using `httpx` are the correct approach.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5
- Changed: SDK version updated to 0.104.0 in verification section
- Confirmed: `client.admin` still not in SDK 0.120.0 (REST-only, 5 calls verified)

**[2026-03-20 07:10]**
- Added: SDK verification section (re-verified, HTTP workarounds confirmed)

**[2026-03-20 05:55]**
- Added: SDK compatibility note (`client.admin` not in SDK 0.120.0)
- Added: HTTP examples using httpx for all endpoints
- Kept original API doc examples as illustrative

**[2026-03-20 04:12]**
- Initial documentation created from Admin API reference
