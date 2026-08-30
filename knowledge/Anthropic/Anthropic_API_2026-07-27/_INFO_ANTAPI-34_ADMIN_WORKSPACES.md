# Admin API: Workspaces and Members

**Doc ID**: ANTAPI-IN34
**Goal**: Document Admin API for workspace management and workspace membership
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-32_ADMIN_ORGS.md [ANTAPI-IN32]` for organization context

## Summary

Workspaces are organizational units within an Anthropic organization. Each workspace has its own API keys, rate limits, and spend limits. The Admin Workspaces endpoints manage workspace lifecycle (create, retrieve, list, update, archive). Workspace Members endpoints manage user membership within workspaces (add, retrieve, list, update role, remove). API keys and batches are scoped to workspaces.

## Key Facts

- **Workspaces Base**: `/v1/workspaces`
- **Members Base**: `/v1/workspaces/{workspace_id}/members`
- **Workspace Operations**: create, retrieve, list, update, archive
- **Member Operations**: create, retrieve, list, update, delete
- **Workspace Member Model**: user_id, workspace_id, role, type="workspace_member"
- **Status**: GA

## SDK Compatibility Note

**SDK 0.120.0**: The `client.admin` namespace does NOT exist in the Python SDK. Admin API endpoints require direct HTTP requests using `httpx` or similar. Examples below show API documentation style; HTTP examples provide working code.

## Workspaces

### POST /v1/workspaces - Create Workspace

**API Documentation Example** (illustrative):

```python
import anthropic

client = anthropic.Anthropic()

workspace = client.admin.workspaces.create(name="Production")
print(f"Workspace ID: {workspace.id}")
```

**HTTP Example** (SDK 0.120.0):

```python
import httpx, os
response = httpx.post(
    "https://api.anthropic.com/v1/workspaces",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
    json={"name": "Production"},
)
workspace = response.json()
```

### GET /v1/workspaces/{workspace_id} - Get Workspace

**API Documentation Example** (illustrative):

```python
workspace = client.admin.workspaces.retrieve("wrkspc-abc123")
print(f"Name: {workspace.name}")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.get(
    "https://api.anthropic.com/v1/workspaces/wrkspc-abc123",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
```

### GET /v1/workspaces - List Workspaces

**API Documentation Example** (illustrative):

```python
workspaces = client.admin.workspaces.list()
for ws in workspaces:
    print(f"{ws.id}: {ws.name}")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.get(
    "https://api.anthropic.com/v1/workspaces",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
```

### POST /v1/workspaces/{workspace_id} - Update Workspace

**API Documentation Example** (illustrative):

```python
workspace = client.admin.workspaces.update("wrkspc-abc123", name="Production v2")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.post(
    "https://api.anthropic.com/v1/workspaces/wrkspc-abc123",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
    json={"name": "Production v2"},
)
```

### POST /v1/workspaces/{workspace_id}/archive - Archive Workspace

**API Documentation Example** (illustrative):

```python
workspace = client.admin.workspaces.archive("wrkspc-abc123")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.post(
    "https://api.anthropic.com/v1/workspaces/wrkspc-abc123/archive",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
```

## Workspace Members

### POST /v1/workspaces/{workspace_id}/members - Add Member

**API Documentation Example** (illustrative):

```python
member = client.admin.workspaces.members.create(
    workspace_id="wrkspc-abc123", user_id="user-def456", role="developer",
)
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.post(
    "https://api.anthropic.com/v1/workspaces/wrkspc-abc123/members",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
    json={"user_id": "user-def456", "role": "developer"},
)
```

### GET /v1/workspaces/{workspace_id}/members/{user_id} - Get Member

**API Documentation Example** (illustrative):

```python
member = client.admin.workspaces.members.retrieve(
    workspace_id="wrkspc-abc123", user_id="user-def456",
)
print(f"Role: {member.workspace_role}")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.get(
    "https://api.anthropic.com/v1/workspaces/wrkspc-abc123/members/user-def456",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
```

### GET /v1/workspaces/{workspace_id}/members - List Members

**API Documentation Example** (illustrative):

```python
members = client.admin.workspaces.members.list(workspace_id="wrkspc-abc123")
for m in members:
    print(f"{m.user_id}: {m.workspace_role}")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.get(
    "https://api.anthropic.com/v1/workspaces/wrkspc-abc123/members",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
```

### POST /v1/workspaces/{workspace_id}/members/{user_id} - Update Member

**API Documentation Example** (illustrative):

```python
member = client.admin.workspaces.members.update(
    workspace_id="wrkspc-abc123", user_id="user-def456", role="admin",
)
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.post(
    "https://api.anthropic.com/v1/workspaces/wrkspc-abc123/members/user-def456",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
    json={"role": "admin"},
)
```

### DELETE /v1/workspaces/{workspace_id}/members/{user_id} - Remove Member

**API Documentation Example** (illustrative):

```python
client.admin.workspaces.members.delete(
    workspace_id="wrkspc-abc123", user_id="user-def456",
)
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.delete(
    "https://api.anthropic.com/v1/workspaces/wrkspc-abc123/members/user-def456",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
)
```

## Workspace Member Model

- **user_id** (`string`) - User ID
- **workspace_id** (`string`) - Workspace ID
- **workspace_role** (`string`) - Role within workspace
- **type** (`string`) - Always `"workspace_member"`

## Gotchas and Quirks

- Archiving a workspace is soft-delete; archived workspaces cannot be used but may be viewable
- API keys are created per-workspace via the Console, not the Admin API
- Rate limits and spend limits are configured per-workspace
- Batches are scoped to the workspace of the API key used

## Related Endpoints

- `_INFO_ANTAPI-32_ADMIN_ORGS.md [ANTAPI-IN32]` - Organizations and invites
- `_INFO_ANTAPI-33_ADMIN_USERS.md [ANTAPI-IN33]` - Users and API keys
- `_INFO_ANTAPI-35_USAGE_API.md [ANTAPI-IN35]` - Usage reports per workspace

## Sources

- ANTAPI-SC-ANTH-ADMIN - https://platform.claude.com/docs/en/api/admin - Admin API reference

## SDK Verification

10 API doc examples re-verified against `anthropic` SDK 0.120.0. Previous HTTP workarounds confirmed correct.

**Confirmed**: `client.admin` namespace does NOT exist in SDK 0.120.0. HTTP examples using `httpx` are the correct approach.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5
- Changed: SDK version updated to 0.104.0 in verification section
- Confirmed: `client.admin` still not in SDK 0.120.0 (REST-only, 10 calls verified)

**[2026-03-20 07:10]**
- Added: SDK verification section (re-verified, HTTP workarounds confirmed)

**[2026-03-20 05:55]**
- Added: SDK compatibility note (`client.admin` not in SDK 0.86.0)
- Added: HTTP examples using httpx for all endpoints
- Kept original API doc examples as illustrative

**[2026-03-20 04:18]**
- Initial documentation created from Admin API reference
