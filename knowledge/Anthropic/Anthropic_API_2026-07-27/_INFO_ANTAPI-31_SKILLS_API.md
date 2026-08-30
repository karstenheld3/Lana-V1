# Skills API (Beta)

**Doc ID**: ANTAPI-IN31
**Goal**: Document beta Skills API - create, retrieve, list, delete operations
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL, auth headers
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` for beta header usage

## Summary

The Skills API (beta) enables creating and managing reusable agent skills. Skills encapsulate specific capabilities (instructions, tools, configurations) that can be attached to Claude for consistent behavior across conversations. The API provides CRUD operations: create, retrieve, list, and delete. Skills are accessed via the `client.beta.skills` namespace.

## Key Facts

- **Base Endpoint**: `/v1/skills`
- **SDK Namespace**: `client.beta.skills`
- **Operations**: create, retrieve, list, delete
- **Pagination**: Cursor-based (`SyncPageCursor`)
- **Status**: Beta

## Endpoints

### POST /v1/skills - Create Skill

**API Documentation Example:**

```python
import anthropic

client = anthropic.Anthropic()

skill = client.beta.skills.create(
    name="data_analyst",
    description="A skill for analyzing datasets and generating insights",
)
print(f"Skill ID: {skill.id}")
```

**SDK-Verified Example** (anthropic 0.120.0, `resources/beta/skills/skills.py`):

```python
import anthropic

client = anthropic.Anthropic()

# SDK signature: create(display_title, files, betas, extra_headers, ...)
# Note: API docs show name/description; SDK uses display_title/files
skill = client.beta.skills.create(
    display_title="Data Analyst",
    files=["file-abc123"],  # File IDs from Files API
)
print(f"Skill ID: {skill.id}")
```

### GET /v1/skills/{skill_id} - Retrieve Skill

```python
skill = client.beta.skills.retrieve("skill-abc123")
print(f"Name: {skill.name}")
print(f"Description: {skill.description}")
```

### GET /v1/skills - List Skills

```python
skills = client.beta.skills.list()
for skill in skills:
    print(f"{skill.id}: {skill.name}")
```

### DELETE /v1/skills/{skill_id} - Delete Skill

```python
result = client.beta.skills.delete("skill-abc123")
print(f"Deleted: {result.id}")
```

## SDK Types

- **SkillCreateResponse** - Response from skill creation
- **SkillRetrieveResponse** - Response from skill retrieval
- **SkillListResponse** - Response from skill listing (cursor-paginated)
- **SkillDeleteResponse** - Response from skill deletion

## Gotchas and Quirks

- Skills API is in beta; the interface may change
- Use `client.beta.skills` namespace in SDK
- Skills list uses cursor-based pagination (`SyncPageCursor`), different from standard `SyncPage`
- Skill configuration parameters are still evolving; check latest documentation

## Related Endpoints

- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` - Tool use (skills can define tools)
- `_INFO_ANTAPI-30_FILES_API.md [ANTAPI-IN30]` - Files API (another beta feature)

## Sources

- ANTAPI-SC-GH-SDKAPI - https://github.com/anthropics/anthropic-sdk-python/blob/main/api.md - Skill types and methods

## SDK Verification

4 Python examples re-verified against `anthropic` SDK 0.120.0. Previous fix confirmed correct.

**SDK source files checked**:
- `resources/beta/skills/skills.py`: `create(display_title, files)`, `retrieve(skill_id)`, `list()`, `delete(skill_id)`

**Previous fix (still correct)**: SDK-verified example uses `display_title`/`files` instead of API docs' `name`/`description`.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 07:10]**
- Added: SDK verification section (re-verified, previous fix confirmed)

**[2026-03-20 05:55]**
- Added: SDK-verified example (anthropic 0.120.0, `resources/beta/skills/skills.py`)
- Fixed: SDK uses `display_title`/`files` params, not `name`/`description`
- Kept original API doc example for reference

**[2026-03-20 04:08]**
- Initial documentation created from SDK API types
