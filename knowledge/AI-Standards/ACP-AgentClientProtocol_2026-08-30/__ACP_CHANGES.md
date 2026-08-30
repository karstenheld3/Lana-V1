# ACP Documentation: Version Comparison

**Doc ID**: ACP-CHANGES
**Goal**: Compare ACP-AgentClientProtocol_2026-06-12 against ACP-AgentClientProtocol_2026-08-30
**Created**: 2026-08-30

## 1. Executive Summary

- **Old version**: 2026-06-12, 14 INFO files, 91,392 bytes total
- **New version**: 2026-08-30, 16 INFO files, 97,490 bytes total (+6,098 bytes, +6.7%)
- **New topics**: 2 (IN15 Elicitation, IN16 v2 Migration Overview)
- **Removed topics**: 0
- **SDK verification**: Python (27 tests, 0 fail) + TypeScript (38 tests, 0 fail)
- **Documentation bugs fixed**: 3 (all in IN12 TypeScript examples)

**Headline changes**:
- ACP v2 Draft published July 20, 2026 (breaking changes to prompt lifecycle, tool calls, capabilities)
- 8 new v1 stabilizations (elicitation, request cancellation, message IDs, usage updates, session delete, boolean config, model config, SDK 1.0)
- Ecosystem grew from 35+ agents / 20+ clients to 40+ agents / 50+ clients
- Rust and TypeScript SDKs reached v1.0.0 (June 25, 2026)
- Python SDK at v0.12.1 with HTTP/WS transport and schema v1.19.0

## 2. Complete Topic Mapping

All 14 original topics map 1:1 to the new version. No renumbering or restructuring.

- IN01 Summary -> IN01 Summary (updated ecosystem counts, v2 overview added)
- IN02 Sources -> IN02 Sources (new v2, SDK, stabilization sources added)
- IN03 ProblemAndSolution -> IN03 ProblemAndSolution (updated counts, clarified vs MCP/A2A)
- IN04 Architecture -> IN04 Architecture (v2 method changes, updated method inventory)
- IN05 Initialization -> IN05 Initialization (elicitation capability, boolean config, dual-lang examples)
- IN06 SessionLifecycle -> IN06 SessionLifecycle (session/delete, usage_update, v2 changes)
- IN07 PromptTurnAndStreaming -> IN07 PromptTurnAndStreaming ($/cancel_request, messageId, v2 lifecycle)
- IN08 ToolCallsAndPermissions -> IN08 ToolCallsAndPermissions (v2 unified upsert, diff overhaul)
- IN09 AuthenticationAndSecurity -> IN09 AuthenticationAndSecurity (v2 auth/login rename)
- IN10 TransportsAndExtensibility -> IN10 TransportsAndExtensibility (HTTP transport progress, v2 changes)
- IN11 AgentsAndClients -> IN11 AgentsAndClients (40+ agents, 50+ clients, new Connectors category)
- IN12 SDKsAndLibraries -> IN12 SDKsAndLibraries (SDK versions, TS examples fixed, dual-lang)
- IN13 VersionHistoryAndRoadmap -> IN13 VersionHistoryAndRoadmap (8 new stabilizations, v2 RFD timeline)
- IN14 GotchasAndBestPractices -> IN14 GotchasAndBestPractices (v2 migration advice, elicitation best practices)

## 3. New Topics

### IN15: Elicitation (5,017 bytes)

Completely new v1 feature stabilized July 24, 2026. Allows agents to request structured user input via form mode or redirect to external URLs. Two methods: `elicitation/create` (request) and `elicitation/complete` (notification). Client advertises support via `clientCapabilities.elicitation.form` and/or `.url`.

**Developer action**: Implement elicitation support in clients if you need structured input beyond the binary permission model.

### IN16: v2 Migration Overview (6,989 bytes)

Comprehensive guide to ACP v2 breaking changes published in draft on July 20, 2026. Covers: prompt lifecycle redesign (response = acknowledgment), unified tool call upserts, structured diffs, capability reorganization, auth method renames, and removals (client fs/terminal, session/load, session modes).

**Developer action**: Read this topic first if you plan to support v2. Gate v2 behind version negotiation AND feature flags until stabilized.

## 4. Removed/Consolidated Topics

None. All 14 original topics retained. No merges or deprecations.

## 5. Changed Topics (Major)

### IN01 Summary (-4,529 bytes, -39%)

Significantly condensed. Removed verbose descriptions, added v2 overview section, updated ecosystem snapshot. Size reduction is editorial, not content loss.

### IN02 Sources (+1,731 bytes, +30%)

Added 15+ new sources: v2 draft docs, SDK documentation hubs, stabilization announcements, DeepWiki analysis, community analysis articles.

### IN05 Initialization (+1,830 bytes, +30%)

Added elicitation capability advertising, boolean config options, dual-language SDK examples (Python + TypeScript).

### IN08 ToolCallsAndPermissions (-1,048 bytes, -14%)

Condensed existing content while adding v2 unified upsert pattern, tool_call_content_chunk streaming, and structured diff overhaul.

### IN11 AgentsAndClients (+1,936 bytes, +37%)

Major expansion: 40+ agents (was 35+), 50+ clients across 8 categories (was 20+ / 7 categories). New Connectors category. Added: Gold Band, Jockey, Kepler, Kronos, ACP Inspector, Newio, VACP, many messaging platform integrations.

### IN12 SDKsAndLibraries (+3,672 bytes, +63%)

Largest growth. Added: Python SDK v0.12.1 details, TypeScript SDK v1.4.0 with correct class names (AgentApp, ActiveSession, RequestError), v2 experimental import, JSON schema references, dual-language examples. **3 documentation bugs fixed** during SDK verification (createAcpAgent -> AgentApp pattern).

### IN13 VersionHistoryAndRoadmap (+178 bytes, +2%)

Added 8 new stabilization milestones, v2 RFD timeline (June-July 2026), v2 draft publication entry.

## 6. Deprecations

### v1 Features Deprecated by v2 Draft

These v1 features are marked for removal in v2. They still work in v1 but should not receive new investment:

- **Session modes** (`session/set_mode`, `current_mode_update`): Use Session Config Options instead
- **Client fs surface** (`fs/read_text_file`, `fs/write_text_file`): No replacement; agents must handle file I/O directly
- **Client terminal surface** (5 methods): Replaced by agent-owned `terminal_update` / `terminal_output_chunk`
- **`session/load`**: Use `session/resume` with optional `replayFrom` cursors
- **SSE MCP transport**: Use HTTP transport instead

**Timeline**: v2 is draft (July 2026), not yet stabilized. No hard sunset date for v1.

### SDK-Level Deprecations

- Python SDK: `acp.schema` attribute naming uses camelCase (`protocolVersion`) but serialization is snake_case (`protocol_version`). This is by design, not a bug.
- TypeScript SDK: `createAcpAgent` (if it ever existed in earlier versions) replaced by `AgentApp` class with `onRequest`/`onNotification` pattern.

## 7. Recommended Actions

### Immediate (Before Next Release)

- **Read IN16** (v2 Migration Overview) to understand upcoming breaking changes
- **Implement `elicitation/create`** support if your client needs structured user input (IN15)
- **Update `$/cancel_request`** handling as a companion to `session/cancel` (IN07)
- **Track `usage_update`** notifications for cost monitoring (IN07)

### Short-Term (Next Quarter)

- **Add `messageId` support** to message chunks - optional in v1 but required in v2
- **Support `session/delete`** for session cleanup (IN06)
- **Plan v2 migration**: Audit use of session modes, client fs/terminal, session/load
- **Update SDK dependencies**: Python to v0.12.1, TypeScript to v1.4.0

### Evaluate

- **Elicitation URL mode**: Consider for OAuth and external auth flows (IN15)
- **HTTP/WS transport**: Python SDK v0.12.0+ has early implementation; monitor maturity (IN10)
- **v2 experimental import**: TypeScript SDK offers `@agentclientprotocol/sdk/experimental/v2` for early testing
- **ACP Registry**: Use programmatic API for agent discovery if building multi-agent orchestration (IN11)

## Size Comparison

```
File (INxx)          Old (bytes)  New (bytes)  Delta    %
IN01 Summary             11,627       7,098   -4,529  -39%
IN02 Sources              5,723       7,454   +1,731  +30%
IN03 ProblemAndSolution   6,701       4,911   -1,790  -27%
IN04 Architecture         7,315       6,694     -621   -8%
IN05 Initialization       6,177       8,007   +1,830  +30%
IN06 SessionLifecycle     6,675       6,425     -250   -4%
IN07 PromptTurn           8,809       7,209   -1,600  -18%
IN08 ToolCalls            7,618       6,570   -1,048  -14%
IN09 Authentication       5,280       4,968     -312   -6%
IN10 Transports           6,064       4,963   -1,101  -18%
IN11 AgentsClients        5,241       7,177   +1,936  +37%
IN12 SDKsLibraries        5,872       9,544   +3,672  +63%
IN13 VersionHistory       7,418       7,596     +178   +2%
IN14 Gotchas              8,672       8,865     +193   +2%
IN15 Elicitation              -       5,017   +5,017  NEW
IN16 V2Migration              -       6,989   +6,989  NEW
------------------------------------------------------------
TOTAL (INFO only)        91,192      97,490   +6,298   +7%
```

## Document History

**[2026-08-30 04:15]**
- Initial version comparison created
