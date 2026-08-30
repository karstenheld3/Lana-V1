# API Versioning and Beta Headers

**Doc ID**: ANTAPI-IN05
**Goal**: Document API version management, version history, and beta feature access
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL and general overview

## Summary

The Anthropic API uses the `anthropic-version` header for version control. The current (and only GA) version is `2023-06-01`. Within a version, Anthropic may add optional inputs, additional output values, new enum variants, and change error conditions, but will not break existing documented usage. Beta features are accessed via the `anthropic-beta` header with feature-specific identifiers following the `feature-name-YYYY-MM-DD` naming convention.

## Key Facts

- **Version Header**: `anthropic-version: 2023-06-01`
- **Current Version**: `2023-06-01`
- **Previous Version**: `2023-01-01` (deprecated)
- **Beta Header**: `anthropic-beta: feature-name-YYYY-MM-DD`
- **Multiple Betas**: Comma-separated in a single header
- **SDK Handling**: SDKs set version header automatically

## Stability Guarantees (within a version)

For any given API version, Anthropic preserves:

- Existing input parameters
- Existing output parameters

Anthropic may:

- Add additional optional inputs
- Add additional values to the output
- Change conditions for specific error types
- Add new variants to enum-like output values (e.g., streaming event types)

## Version History

### 2023-06-01 (current)

- New format for streaming SSE: completions are incremental (deltas, not cumulative)
- All events are named events (not data-only events)
- Removed `data: [DONE]` event
- Removed legacy `exception` and `truncated` values in responses

### 2023-01-01 (deprecated)

- Initial release

## Beta Headers

### Usage

Include the `anthropic-beta` header to access experimental features:

```python
import anthropic

client = anthropic.Anthropic()

# Using beta namespace in SDK
response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
    betas=["files-api-2025-04-14"],
)
```

### Raw HTTP

```
POST /v1/messages HTTP/1.1
Content-Type: application/json
X-API-Key: YOUR_API_KEY
anthropic-beta: files-api-2025-04-14
```

### Multiple Beta Features

Comma-separated in a single header:

```
anthropic-beta: feature1,feature2,feature3
```

### Version Naming Convention

Beta feature names follow `feature-name-YYYY-MM-DD` where the date indicates when the beta version was released. Always use the exact name as documented.

### Known Beta Feature Headers (as of 2026-07-26)

- **files-api-2025-04-14** - Files API for document/image uploads
- **managed-agents-2026-04-01** - Claude Managed Agents (non-memory endpoints)
- **agent-memory-2026-07-22** - Agent memory store endpoints (replaces managed-agents on memory calls)
- **advisor-tool-2026-03-01** - Advisor tool (executor + advisor model pairing)
- **cache-diagnosis-2026-04-07** - Cache diagnostics for debugging cache misses
- **output-300k-2026-03-24** - 300k output tokens on Batch API
- **fast-mode-2026-02-01** - Fast mode (Opus 5 and 4.8 only)
- **mcp-tunnels-2026-06-22** - MCP tunnels (moved from Admin API to Claude API)
- **server-side-fallback-2026-07-01** - Server-side fallback for refusals (fallbacks parameter)
- **mid-conversation-tool-changes-2026-07-01** - Add/remove tools between turns preserving cache
- **ce-user-management-2026-07-13** - Claude Enterprise Admin API user management
- **task-budgets-2026-03-13** - Task budgets for agentic loops (token budget countdown)
- **dreaming-2026-04-21** - Dreams for Managed Agents (research preview)
- **thinking-token-count-2026-05-13** - Thinking token count in usage details
- **user-profiles-2026-03-24** - User profiles for personalization
- **fallback-credit-2026-07-01** - Fallback credit (no-charge on refusals with fallback)
- **model-context-window-exceeded-2025-08-26** - model_context_window_exceeded stop reason (pre-Sonnet 4.5)

### Beta Feature Characteristics

Beta features are experimental and may:

- Have breaking changes with notice
- Be deprecated or removed
- Have different rate limits or pricing
- Not be available in all regions

## Error Codes

- **400** `invalid_request_error` - Invalid or unsupported beta header value (e.g., `"Unsupported beta header: invalid-beta-name"`)

## Gotchas and Quirks

- The `anthropic-version` value has been `2023-06-01` since June 2023; new features use beta headers instead of new API versions
- Always use the latest API version; previous versions are deprecated and may be unavailable for new users
- Beta features accessed via the `beta` namespace in SDKs (`client.beta.messages.create()`)
- Streaming changed significantly between 2023-01-01 and 2023-06-01: deltas became incremental rather than cumulative

## Related Endpoints

- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` - API overview
- `_INFO_ANTAPI-06_ERRORS.md [ANTAPI-IN06]` - Error handling for invalid beta headers
- `_INFO_ANTAPI-30_FILES_API.md [ANTAPI-IN30]` - Files API (beta feature)
- `_INFO_ANTAPI-31_SKILLS_API.md [ANTAPI-IN31]` - Skills API (beta feature)
- `_INFO_ANTAPI-40_MANAGED_AGENTS.md [ANTAPI-IN40]` - Managed Agents (beta)
- `_INFO_ANTAPI-41_ADVISOR_TOOL.md [ANTAPI-IN41]` - Advisor tool (beta)
- `_INFO_ANTAPI-42_CACHE_DIAGNOSTICS.md [ANTAPI-IN42]` - Cache diagnostics (beta)
- `_INFO_ANTAPI-45_MCP_TUNNELS.md [ANTAPI-IN45]` - MCP tunnels (research preview)
- `_INFO_ANTAPI-47_REFUSALS_AND_FALLBACKS.md [ANTAPI-IN47]` - Refusals and fallbacks (beta)
- `_INFO_ANTAPI-49_AGENT_MEMORY_STORES.md [ANTAPI-IN49]` - Agent memory stores (beta)

## Sources

- ANTAPI-SC-ANTH-VERSION - https://platform.claude.com/docs/en/api/versioning - Version history, stability guarantees
- ANTAPI-SC-ANTH-BETAHDR - https://platform.claude.com/docs/en/api/beta-headers - Beta header usage, naming, errors

## SDK Verification

1 Python example verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `resources/beta/beta.py` (line 43): `Beta.messages` -> `Messages` resource with `create()` method
- `_client.py` (line 137): `client.beta` property confirmed

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: 6 new beta headers (agent-memory, server-side-fallback, mid-conversation-tool-changes, ce-user-management, model-context-window-exceeded)
- Changed: mcp-tunnels header updated to 2026-06-22 (moved to Claude API)
- Changed: fast-mode now Opus 5/4.8 only
- Added: Related links for IN45, IN47

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Added: Known beta feature headers list (7 active betas)
- Added: Related endpoint links for new beta features (IN38-IN43)

**[2026-03-20 06:45]**
- Added: SDK verification section (anthropic 0.120.0, 1 example valid)

**[2026-03-20 02:18]**
- Initial documentation created from versioning and beta headers pages
