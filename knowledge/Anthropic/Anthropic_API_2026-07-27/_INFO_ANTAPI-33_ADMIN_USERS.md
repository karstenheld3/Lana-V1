# Admin API: Users and API Keys

**Doc ID**: ANTAPI-IN33
**Goal**: Document Admin API for user management and API key administration
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-32_ADMIN_ORGS.md [ANTAPI-IN32]` for organization context

## Summary

The Admin Users endpoints manage organization members (retrieve, list, update role, remove). The Admin API Keys endpoints manage API keys (retrieve, list, update). Users have organization roles and can be members of multiple workspaces. API keys are scoped to workspaces and have configurable names and statuses.

## Key Facts

- **Users Base**: `/v1/users`
- **API Keys Base**: `/v1/api_keys`
- **User Operations**: retrieve, list, update, delete (remove)
- **API Key Operations**: retrieve, list, update
- **User Model**: id, email, name, role, created_at, type="user"
- **Status**: GA

## SDK Compatibility Note

**SDK 0.120.0**: The `client.admin` namespace does NOT exist in the Python SDK. Admin API endpoints require direct HTTP requests using `httpx` or similar. The examples below show API documentation style; HTTP examples provide working code.

## Users

### GET /v1/users/{user_id} - Get User

**API Documentation Example** (illustrative):

```python
import anthropic

client = anthropic.Anthropic()

user = client.admin.users.retrieve("user-abc123")
print(f"Name: {user.name}")
print(f"Email: {user.email}")
```

**HTTP Example** (SDK 0.120.0):

```python
import httpx, os
response = httpx.get(
    "https://api.anthropic.com/v1/users/user-abc123",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
user = response.json()
```

### GET /v1/users - List Users

**API Documentation Example** (illustrative):

```python
users = client.admin.users.list()
for user in users:
    print(f"{user.name} ({user.email}): {user.role}")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.get(
    "https://api.anthropic.com/v1/users",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
for user in response.json()["data"]:
    print(f"{user['name']}: {user['role']}")
```

### POST /v1/users/{user_id} - Update User

**API Documentation Example** (illustrative):

```python
user = client.admin.users.update("user-abc123", role="developer")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.post(
    "https://api.anthropic.com/v1/users/user-abc123",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
    json={"role": "developer"},
)
```

### DELETE /v1/users/{user_id} - Remove User

**API Documentation Example** (illustrative):

```python
client.admin.users.delete("user-abc123")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.delete(
    "https://api.anthropic.com/v1/users/user-abc123",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
```

## User Model

- **id** (`string`) - User ID
- **email** (`string`) - User email
- **name** (`string`) - User display name
- **role** (`string`) - Organization role
- **created_at** (`string`) - RFC 3339 join datetime
- **type** (`string`) - Always `"user"`

## API Keys

### GET /v1/api_keys/{api_key_id} - Get API Key

**API Documentation Example** (illustrative):

```python
key = client.admin.api_keys.retrieve("apikey-abc123")
print(f"Name: {key.name}")
print(f"Status: {key.status}")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.get(
    "https://api.anthropic.com/v1/api_keys/apikey-abc123",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
key = response.json()
```

### GET /v1/api_keys - List API Keys

**API Documentation Example** (illustrative):

```python
keys = client.admin.api_keys.list()
for key in keys:
    print(f"{key.name}: {key.status}")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.get(
    "https://api.anthropic.com/v1/api_keys",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
for key in response.json()["data"]:
    print(f"{key['name']}: {key['status']}")
```

### POST /v1/api_keys/{api_key_id} - Update API Key

**API Documentation Example** (illustrative):

```python
key = client.admin.api_keys.update("apikey-abc123", name="Production Key", status="active")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.post(
    "https://api.anthropic.com/v1/api_keys/apikey-abc123",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
    json={"name": "Production Key", "status": "active"},
)
```

## Gotchas and Quirks

- API keys cannot be created via Admin API; use the Console
- Removing a user is irreversible; they must be re-invited
- User roles affect permissions across all workspaces in the organization
- API keys are scoped to specific workspaces

## Related Endpoints

- `_INFO_ANTAPI-32_ADMIN_ORGS.md [ANTAPI-IN32]` - Organizations and invites
- `_INFO_ANTAPI-34_ADMIN_WORKSPACES.md [ANTAPI-IN34]` - Workspace management

## Sources

- ANTAPI-SC-ANTH-ADMIN - https://platform.claude.com/docs/en/api/admin - Admin API reference

## SDK Verification

7 API doc examples re-verified against `anthropic` SDK 0.120.0. Previous HTTP workarounds confirmed correct.

**Confirmed**: `client.admin` namespace does NOT exist in SDK 0.120.0. HTTP examples using `httpx` are the correct approach.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5
- Changed: SDK version updated to 0.104.0 in verification section
- Confirmed: `client.admin` still not in SDK 0.120.0 (REST-only, 7 calls verified)

**[2026-03-20 07:10]**
- Added: SDK verification section (re-verified, HTTP workarounds confirmed)

**[2026-03-20 05:55]**
- Added: SDK compatibility note (`client.admin` not in SDK 0.86.0)
- Added: HTTP examples using httpx for all endpoints
- Kept original API doc examples as illustrative

**[2026-03-20 04:15]**
- Initial documentation created from Admin API reference
