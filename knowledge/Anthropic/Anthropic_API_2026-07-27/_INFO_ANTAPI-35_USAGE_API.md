# Admin API: Usage Reports

**Doc ID**: ANTAPI-IN35
**Goal**: Document usage reporting endpoints for messages and Claude Code
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-32_ADMIN_ORGS.md [ANTAPI-IN32]` for organization context

## Summary

The Usage Report endpoints provide detailed token consumption and cost data. Two report types exist: Messages usage (API token consumption by model, workspace, API key, context window, inference geo, service tier) and Claude Code usage (developer productivity metrics including commits, code changes, sessions, PRs). Reports support time-based bucketing, grouping dimensions, and cursor pagination.

## Key Facts

- **Messages Report**: `GET /v1/usage/messages`
- **Claude Code Report**: `GET /v1/usage/claude_code`
- **Grouping**: model, workspace_id, api_key_id, context_window, inference_geo, service_tier, speed
- **Time Buckets**: start_time, end_time in RFC 3339 format
- **Pagination**: Cursor-based with `has_more` and `next_page` fields
- **Status**: GA

## SDK Compatibility Note

**SDK 0.120.0**: The `client.admin` namespace does NOT exist in the Python SDK. Usage API endpoints require direct HTTP requests using `httpx` or similar. Examples below show API documentation style; HTTP examples provide working code.

## Messages Usage Report

### GET /v1/usage/messages

**API Documentation Example** (illustrative):

```python
import anthropic

client = anthropic.Anthropic()

usage = client.admin.usage_report.retrieve_messages(
    start_time="2026-03-01T00:00:00Z",
    end_time="2026-03-20T00:00:00Z",
    group_by=["model"],
)
for bucket in usage.data:
    print(f"Model: {bucket.items[0].model}, Tokens: {bucket.items[0].input_tokens}")
```

**HTTP Example** (SDK 0.120.0):

```python
import httpx, os

response = httpx.get(
    "https://api.anthropic.com/v1/usage/messages",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
    params={
        "start_time": "2026-03-01T00:00:00Z",
        "end_time": "2026-03-20T00:00:00Z",
        "group_by": "model",
    },
)
usage = response.json()
for bucket in usage["data"]:
    for item in bucket["items"]:
        print(f"Model: {item['model']}, Input: {item['input_tokens']}")
```

### Usage Item Fields

- **input_tokens** (`integer`) - Uncached input tokens
- **output_tokens** (`integer`) - Output tokens generated
- **cache_read_input_tokens** (`integer`) - Tokens read from cache
- **cache_creation_input_tokens** (`integer`) - Tokens written to cache
- **cache_creation_input_tokens_5m** (`integer`) - 5-minute cache writes
- **cache_creation_input_tokens_1h** (`integer`) - 1-hour cache writes
- **model** (`string | null`) - Model used (if grouping by model)
- **workspace_id** (`string | null`) - Workspace (if grouping by workspace)
- **api_key_id** (`string | null`) - API key (if grouping by api_key)
- **context_window** (`string | null`) - Context window tier
- **inference_geo** (`string | null`) - Inference geography
- **service_tier** (`string | null`) - Service tier
- **speed** (`string | null`) - Speed tier (requires fast-mode beta header)
- **server_tool_usage** (`object`) - Server tool metrics:
  - **web_search_requests** (`integer`) - Web searches performed

## Claude Code Usage Report

### GET /v1/usage/claude_code

**API Documentation Example** (illustrative):

```python
usage = client.admin.usage_report.retrieve_claude_code(
    start_time="2026-03-01T00:00:00Z",
    end_time="2026-03-20T00:00:00Z",
)
for record in usage.data:
    print(f"Date: {record.date}, Sessions: {record.core_metrics.sessions}")
```

**HTTP Example** (SDK 0.120.0):

```python
response = httpx.get(
    "https://api.anthropic.com/v1/usage/claude_code",
    headers={"x-api-key": os.environ["ANTHROPIC_ADMIN_KEY"], "anthropic-version": "2023-06-01"},
    params={"start_time": "2026-03-01T00:00:00Z", "end_time": "2026-03-20T00:00:00Z"},
)
for record in response.json()["data"]:
    print(f"Date: {record['date']}, Sessions: {record['core_metrics']['sessions']}")
```

### Claude Code Usage Fields

- **date** (`string`) - UTC date (YYYY-MM-DD)
- **actor** - User or API key identity
  - **email** / **api_key_name** (`string`)
- **core_metrics** - Productivity metrics:
  - **sessions** (`integer`) - Distinct sessions
  - **git_commits** (`integer`) - Commits created
  - **pull_requests** (`integer`) - PRs created
  - **code_changes** - Code modification stats:
    - **lines_added** (`integer`)
    - **lines_removed** (`integer`)
- **model_usage** (`array`) - Per-model token breakdown:
  - **model** (`string`) - Model name
  - **tokens** - input, output, cache_read, cache_creation counts
  - **estimated_cost** - amount (minor units), currency
- **customer_type** (`string`) - "api" or "subscription"
- **terminal_type** (`string`) - Environment type
- **tool_actions** (`array`) - Acceptance/rejection rates by tool

## Gotchas and Quirks

- `group_by` parameters are passed as array query parameters (`group_by[]=model&group_by[]=workspace_id`)
- `speed` grouping requires the `fast-mode-2026-02-01` beta header
- `api_key_id` is null for Console usage (not via API key)
- `workspace_id` is null for default workspace usage
- Cost data in Claude Code report uses minor currency units (cents for USD)
- Pagination uses `has_more` boolean and `next_page` cursor token

## Related Endpoints

- `_INFO_ANTAPI-32_ADMIN_ORGS.md [ANTAPI-IN32]` - Organization context
- `_INFO_ANTAPI-34_ADMIN_WORKSPACES.md [ANTAPI-IN34]` - Workspace management
- `_INFO_ANTAPI-14_PRICING.md [ANTAPI-IN14]` - Token pricing rates

## Sources

- ANTAPI-SC-ANTH-ADMIN - https://platform.claude.com/docs/en/api/admin - Admin API reference (usage report section)

## SDK Verification

2 API doc examples re-verified against `anthropic` SDK 0.120.0. Previous HTTP workarounds confirmed correct.

**Confirmed**: `client.admin` namespace does NOT exist in SDK 0.120.0. HTTP examples using `httpx` are the correct approach.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5
- Changed: SDK version updated to 0.104.0 in verification section
- Confirmed: `client.admin` still not in SDK 0.120.0 (REST-only, 2 calls verified)

**[2026-03-20 07:10]**
- Added: SDK verification section (re-verified, HTTP workarounds confirmed)

**[2026-03-20 05:55]**
- Added: SDK compatibility note (`client.admin` not in SDK 0.86.0)
- Added: HTTP examples using httpx for all endpoints
- Kept original API doc examples as illustrative

**[2026-03-20 04:22]**
- Initial documentation created from Admin API reference
