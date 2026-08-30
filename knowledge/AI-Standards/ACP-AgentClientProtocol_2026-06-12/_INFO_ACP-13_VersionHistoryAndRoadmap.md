# ACP: Version History and Roadmap

**Doc ID**: ACP-IN13
**Goal**: Document ACP's timeline, v1 milestones, v2 proposal, and governance
**Version scope**: Inception (Aug 2025) through June 2026

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP was introduced by Zed Industries in August 2025 and grew from a Zed-specific integration mechanism to a multi-vendor standard within months. Protocol v1 is stable with 10+ feature stabilizations. A v2 proposal is in draft, introducing breaking changes to capability negotiation, tool call updates, and plan variants. Governance follows an open RFD (Requests for Dialog) process with working groups and interest groups. [VERIFIED] (ACP-SC-MRCNR-INTRO, ACP-SC-ACPORG-UPDTS, ACP-SC-ACPORG-V2)

## Timeline

### 2025

- **August 2025**: Zed introduces ACP in "Bring Your Own Agent to Zed" blog post. Initial protocol design as a Zed-specific integration mechanism. [VERIFIED] (ACP-SC-MRCNR-INTRO)

- **September 2025**: "Claude Code via ACP" blog post by Zed, establishing the adapter pattern for non-native agents. [VERIFIED] (ACP-SC-MRCNR-INTRO)

- **October 2025**: JetBrains announces interoperability with Zed on ACP, transforming it from a single-vendor to multi-vendor standard. [VERIFIED] (ACP-SC-MRCNR-INTRO)

- **December 2025**: "Bring your own AI agent to JetBrains IDEs" blog post, formalizing JetBrains' ACP support. [VERIFIED] (ACP-SC-MRCNR-INTRO)

### 2026

- **January 2026**: ACP Registry launched, providing curated agent discovery and installation. GitHub Copilot CLI ACP support enters public preview. [VERIFIED] (ACP-SC-MRCNR-INTRO, ACP-SC-ACPORG-AGNTS)

- **2026 (ongoing)**: Multiple protocol features stabilized (see Stabilization Milestones below). Sergey Ignatov joins as Lead Maintainer. Transports Working Group formed.

## v1 Stabilization Milestones

Features move from draft/RFD to stable protocol through the following stabilizations: [VERIFIED] (ACP-SC-ACPORG-UPDTS)

- **Implementation information**: Optional metadata exchange during initialization
- **Session Config Options**: Flexible configuration selectors for agent sessions
- **Session List**: `session/list` method for discovering existing sessions
- **Session Info Update**: `session_info_update` notification
- **ACP Registry**: Agent registry specification stabilized
- **Transports Working Group**: Formed to stabilize new transport formats
- **Session Resume**: `session/resume` method (complement to `session/load`)
- **Session Close**: `session/close` method for graceful session termination
- **Logout Method**: `logout` method for ending authenticated state

## v2 Proposal (Draft)

The v2 proposal introduces breaking protocol changes. Key changes: [VERIFIED] (ACP-SC-ACPORG-V2)

### Removals

- **Session modes API removed**: `session/set_mode`, `current_mode_update`, `SessionMode*` types. Replaced by Session Config Options.
- **Client filesystem and terminal surface removed**: `clientCapabilities.fs`, `clientCapabilities.terminal`, `fs/*` methods, `terminal/*` methods. Terminal authentication remains under `clientCapabilities.auth.terminal`.
- **Deprecated SSE Model Context Protocol (MCP) transport removed**: Only HTTP retained for remote MCP servers.

### Changes

- **Plan variants**: Replace `plan` session update with item-based `plan_update`
- **Unified tool calls**: Replace split `tool_call`/`tool_call_update` with single upsert shape keyed by `toolCallId`
- **Tool-call content chunks**: Stream individual `ToolCallContent` items that append to a tool call
- **Whole-message updates**: `user_message`, `agent_message`, `agent_thought` upserts keyed by `messageId`
- **Required message IDs**: Streamed message chunks must include `messageId`
- **JSON-RPC 2.0 batch support**: Follow batch request and notification behavior

### Capability Reorganization

- Single `capabilities` field replaces `clientCapabilities`/`agentCapabilities`
- Concise group names (`session`, `auth` instead of `sessionCapabilities`)
- `session` becomes optional (for non-session agents like NES-only agents)
- Session-scoped groups move under `session` (e.g., `session.prompt`, `session.mcp`, `session.load`)
- Support markers as capability objects (`{}` = supported) instead of booleans

### MCP Transport Alignment

- stdio becomes explicit `session.mcp.stdio` capability
- MCP server configs require `type` discriminator (including `type: "stdio"`)
- HTTP retained as remote MCP transport

### RFDs to be Written

Outstanding items for v2 include: terminal output streaming, expanded diff types (delete, move), starting message history in `session/new`, MCP tool timeouts, and getting config options outside a session.

## Governance

### RFD Process

Changes to the protocol follow the Requests for Dialog (RFD) process. Each RFD goes through lifecycle stages: Draft, Preview, Completed. This ensures changes are well-considered before stabilization. [VERIFIED] (ACP-SC-ACPORG-LLMS)

### Maintainers

- **Sergey Ignatov**: Joined as Lead Maintainer (announced in protocol updates) [VERIFIED] (ACP-SC-ACPORG-UPDTS)

### Working and Interest Groups

- **Transports Working Group**: Focused on stabilizing new transport formats (HTTP, WebSocket) [VERIFIED] (ACP-SC-ACPORG-UPDTS)
- Other working groups and interest groups defined in governance documentation

### Contributing

Contributions are accepted under Apache License 2.0 without a CLA requirement. Contributors affirm they have legal right to submit their work. [VERIFIED] (ACP-SC-GH-REPO)

## Versioning Model

ACP uses a two-level versioning approach: [VERIFIED] (ACP-SC-GH-REPO)

- **Protocol version**: Single integer (currently 1), only increments for breaking wire changes. Negotiated during `initialize` via `protocolVersion`.
- **Artifact version**: SDK crate/package versions follow their own semver. Two artifact versions can describe the same wire-compatible protocol.
- **Compatibility rule**: Use negotiated `protocolVersion` for wire compatibility; use exchanged capabilities for optional features; use artifact versions for SDK compatibility.

## Quick Reference

- **Created**: August 2025 by Zed Industries
- **Protocol v1**: Stable, 10+ feature stabilizations
- **Protocol v2**: Draft proposal with breaking changes
- **License**: Apache 2.0
- **Governance**: RFD process, working groups, interest groups
- **Lead Maintainer**: Sergey Ignatov
- **48 releases**: On GitHub as of 2026-06-12

## Limitations and Gotchas

- v2 breaking changes will require migration effort for all existing implementations
- The removal of client fs/terminal surface in v2 means current implementations using these features will need alternative approaches
- Session modes API is deprecated; implementations should use Session Config Options instead
- The two-level versioning (protocol vs artifact) causes confusion; always check `protocolVersion`, not package version
- RFD process means changes can take time to stabilize; check the status of specific features before relying on them

## Sources

- ACP-SC-ACPORG-UPDTS - Official updates and stabilization announcements
- ACP-SC-ACPORG-V2 - v2 proposal RFD
- ACP-SC-MRCNR-INTRO - Timeline and ecosystem evolution
- ACP-SC-GH-REPO - Versioning model, contributing policy, release count
- ACP-SC-ACPORG-LLMS - Full documentation index including all RFDs

## Document History

**[2026-06-12 10:15]**
- Initial document created
