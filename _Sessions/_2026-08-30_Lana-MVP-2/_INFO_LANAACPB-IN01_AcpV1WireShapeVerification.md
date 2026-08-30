# INFO: ACP v1 Wire Shape Verification

**Doc ID**: LANAACPB-IN01
**Goal**: Resolve discrepancies between the two local ACP doc snapshots (2026-06-12 vs 2026-08-30) against the live official protocol docs, and determine the correct v1 wire shapes for LANAACPB-SP01
**Timeline**: Created 2026-08-30, Updated 0 times

**Depends on:**
- `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` - consumer of these corrections

## Summary

- **Verdict**: the 2026-08-30 INFO refresh contains hallucinated wire shapes; the 2026-06-12 snapshot was correct on every disputed point [VERIFIED]
- `agentCapabilities` v1 shape: `{loadSession: bool, promptCapabilities: {image, audio, embeddedContext}, mcpCapabilities: {http, sse}, sessionCapabilities: {...}, auth: {...}}` - `promptContentTypes` DOES NOT EXIST [VERIFIED]
- Baseline: agents MUST accept `ContentBlock::Text` AND `ContentBlock::ResourceLink` in `session/prompt`; image/audio/embeddedContext are capability-gated [VERIFIED]
- `session/prompt` response carries `{stopReason}` only - no usage field [VERIFIED]
- `usage_update` notification shape: `{used, size, cost: {amount, currency}}` - NOT inputTokens/outputTokens/totalTokens [VERIFIED]
- `elicitation/create` params: `{sessionId|requestId, mode: "form", message, requestedSchema}` (restricted flat JSON Schema; enum + MultiSelectPropertySchema exist) - not "title/select fields" [VERIFIED]
- `$/cancel_request` with `requestId`, `-32800` Cancelled error - as spec'd [VERIFIED]
- `session/update` kinds in v1: user_message_chunk, agent_message_chunk, agent_thought_chunk, tool_call, tool_call_update, plan, available_commands_update, current_mode_update, config_option_update, session_info_update, usage_update [VERIFIED]
- SPEC corrections required: FR-02 (capability shape), FR-05 (accept resource_link; response shape), FR-06 (usage_update mapping), FR-09 (elicitation field names), Data Structures examples

## Table of Contents

1. [Trigger](#1-trigger)
2. [Discrepancies and Verdicts](#2-discrepancies-and-verdicts)
3. [Verified-Correct Shapes in Both Snapshots](#3-verified-correct-shapes-in-both-snapshots)
4. [Impact on LANAACPB-SP01](#4-impact-on-lanaacpb-sp01)
5. [Exclusions](#5-exclusions)
6. [Sources](#6-sources)
7. [Document History](#7-document-history)

## 1. Trigger

During `/write-impl-plan` review, the agent's training data conflicted with the 2026-08-30 INFO docs on the agent capability shape (`promptCapabilities` object vs `promptContentTypes` array). Folder comparison then showed the 2026-06-12 snapshot documenting a THIRD variant reading. User directed `/research` verification against live sources ([official protocol docs](https://agentclientprotocol.com/protocol/v1/overview)).

## 2. Discrepancies and Verdicts

### 2.1 Agent prompt capability declaration

- **2026-08-30 doc claims**: `agentCapabilities.promptContentTypes: ["text", "image"]` (array of type names)
- **2026-06-12 doc claims**: `promptCapabilities` with `image`/`audio`/`embeddedContext` flags; text + ResourceLink baseline
- **Official v1** ([initialization](https://agentclientprotocol.com/protocol/v1/initialization), [schema](https://agentclientprotocol.com/protocol/v1/schema) `AgentCapabilities` default): `"promptCapabilities": {"image": false, "audio": false, "embeddedContext": false}` - **2026-06-12 correct, `promptContentTypes` does not exist** [VERIFIED]
- Baseline rule (initialization page, verbatim): "As a baseline, all Agents MUST support `ContentBlock::Text` and `ContentBlock::ResourceLink` in `session/prompt` requests." [VERIFIED]

### 2.2 Session capability nesting

- **2026-08-30 doc claims**: `agentCapabilities.session.{loadSession, resumeSession, closeSession, deleteSession, listSessions, configOptions}`
- **Official v1**: top-level `loadSession: bool` PLUS separate `sessionCapabilities: {resume, close, delete, list, configOptions, additionalDirectories}` markers; schema note: "`session/load` is still handled by the top-level `load_session` capability. This will be unified in future versions." - **2026-08-30 nesting is wrong** [VERIFIED]

### 2.3 MCP capability shape

- **2026-08-30 doc claims**: `mcp: {stdio: true}`
- **Official v1**: `mcpCapabilities: {http, sse}`; stdio transport assumed by default (matches 2026-06-12) [VERIFIED]

### 2.4 usage_update shape

- **2026-08-30 doc claims**: `usage_update` with `inputTokens`, `outputTokens`, `totalTokens`
- **Official v1** ([prompt-turn](https://agentclientprotocol.com/protocol/v1/prompt-turn) Session Usage Updates + schema `UsageUpdate`): `{"sessionUpdate": "usage_update", "used": 53000, "size": 200000, "cost": {"amount": 0.045, "currency": "USD"}}` - `used` = tokens consumed in context, `size` = context window size, both min 0 - **token-triple shape is hallucinated** [VERIFIED]

### 2.5 session/prompt response shape

- **LANAACPB-SP01 assumed** (from 2026-08-30 doc): response carries `stopReason` + `usage` object
- **Official v1** (prompt-turn Check for Completion): `{"jsonrpc": "2.0", "id": 2, "result": {"stopReason": "end_turn"}}` - stopReason only; usage flows via `usage_update` notifications [VERIFIED]

### 2.6 Elicitation form request shape

- **2026-08-30 doc claims**: form definition with `title` and `select` fields
- **Official** ([elicitation RFD](https://agentclientprotocol.com/rfds/elicitation), [v2 elicitation page](https://agentclientprotocol.com/protocol/v2/elicitation) - data model shared with the stabilized v1 extension): `elicitation/create` params `{sessionId|requestId, mode: "form", message, requestedSchema}`; `requestedSchema` = restricted flat JSON Schema (primitive properties, `enum`, `MultiSelectPropertySchema` for multi-select); response `{action: accept|decline|cancel, content?}` [VERIFIED]
- Client capability rule: `elicitation.form`/`elicitation.url` must be present AND non-null; `{}` does NOT imply form support (unlike MCP) [VERIFIED]

## 3. Verified-Correct Shapes in Both Snapshots

Confirmed against live docs - no SPEC change needed:

- Handshake sequence `initialize` → response → `initialized` notification; nothing before `initialize` [VERIFIED]
- Version negotiation: agent responds with its own latest supported version when client requests higher [VERIFIED]
- `$/cancel_request` protocol-level notification with `requestId`; receiver MUST answer the original request (partial result or `-32800` Cancelled) [VERIFIED]
- `session/update` discriminator `sessionUpdate` with the 11 v1 kinds (Summary above); `messageId` on user/agent/thought chunks [VERIFIED]
- `tool_call`/`tool_call_update` with `toolCallId`, `title`, `kind` (ToolKind), `status` (ToolCallStatus) [VERIFIED]
- `plan` update with `entries[{content, priority, status}]` [VERIFIED]
- `session/load` replays the entire conversation via `session/update` notifications before responding; gated by `loadSession` capability [VERIFIED]
- `session/cancel` notification; turn must end with `stopReason: "cancelled"`; pending permission requests resolve as `cancelled` outcome [VERIFIED]
- `agentInfo` `{name, title?, version}` optional-but-SHOULD in v1 initialize response [VERIFIED]
- Stop reasons `end_turn` and `cancelled` valid v1 `StopReason` values [VERIFIED]; complete enum not extracted from the schema page render [ASSUMED - remaining values do not affect MVP-2, which emits only these two]

## 4. Impact on LANAACPB-SP01

Corrections applied to the SPEC (see SP01 Document History 2026-08-30):

- **FR-02**: capability declaration → `{loadSession: true, promptCapabilities: {image: false, audio: false, embeddedContext: false}}`; no `promptContentTypes`
- **FR-05**: MUST accept `resource_link` content blocks (baseline) - flattened to text for the Generator; `-32602` only for image/audio/resource blocks; response carries `stopReason` only
- **FR-06**: `turn_finished` → `usage_update {used, size, cost}` mapping; `used` = cumulative session input+output tokens, `size` = generator context window, `cost` from CostTracker [ASSUMED mapping - official docs define the fields, not the agent-side accounting]
- **FR-09**: elicitation via `message` + `requestedSchema` (enum select / multi-select), response `action`/`content`
- **Data Structures**: initialize and prompt response examples corrected

## 5. Exclusions

- **v2 Draft surfaces**: not verified beyond the migration table - v2 postponed per user decision 2026-08-30
- **Terminal/fs client capabilities**: Lana never consumes them (LANAACPB-SP01 scope)
- **auth methods**: Lana declares none in MVP-2
- **Full StopReason enum**: not needed for MVP-2 (only end_turn/cancelled emitted)
- **Session modes / config options**: v1 features Lana does not implement (ExecutionPolicy is not a session mode, DD-05)

## 6. Sources

- **LANAACPB-IN01-SC-ACPORG-INIT** - https://agentclientprotocol.com/protocol/v1/initialization - agentCapabilities shape, promptCapabilities, text+resource_link baseline, elicitation client capability rules
- **LANAACPB-IN01-SC-ACPORG-SCHM** - https://agentclientprotocol.com/protocol/v1/schema - AgentCapabilities default JSON, SessionUpdate kinds, UsageUpdate, ElicitationSchema, MultiSelectPropertySchema, $/cancel_request (-32800)
- **LANAACPB-IN01-SC-ACPORG-PRMPT** - https://agentclientprotocol.com/protocol/v1/prompt-turn - prompt request with resource block, session/update examples, usage_update shape, prompt response {stopReason}, cancellation
- **LANAACPB-IN01-SC-ACPORG-SESSU** - https://agentclientprotocol.com/protocol/v1/session-setup - loadSession gating, session/load replay contract, sessionCapabilities.resume
- **LANAACPB-IN01-SC-ACPORG-ELIC** - https://agentclientprotocol.com/rfds/elicitation - elicitation/create data model, form/url modes, accept/decline/cancel actions
- **LANAACPB-IN01-SC-ACPORG-V2MIG** - https://agentclientprotocol.com/protocol/v2/migration - v1 capability example (promptCapabilities confirmed), v1→v2 method table
- **LANAACPB-IN01-SC-LOCAL-D0612** - `docs/AI-Standards/ACP-AgentClientProtocol_2026-06-12/_INFO_ACP-05_Initialization.md` - correct promptCapabilities + baseline documentation
- **LANAACPB-IN01-SC-LOCAL-D0830** - `docs/AI-Standards/ACP-AgentClientProtocol_2026-08-30/_INFO_ACP-05_Initialization.md` - hallucinated promptContentTypes/session nesting (SOCAS: examples carry [VERIFIED] tags citing sources that contradict them - verification labels in that doc set are unreliable)

## 7. Document History

**[2026-08-30 13:55]**
- Initial document created via /research: 6 discrepancies resolved against live official docs, 2026-08-30 snapshot found hallucinated on 4 wire shapes, SPEC correction list compiled
