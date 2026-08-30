# ACP: Summary and Overview

**Doc ID**: ACP-IN01
**Goal**: Provide a high-level summary of the Agent Client Protocol, its purpose, ecosystem, and documentation structure
**Version scope**: ACP Protocol v1 (stable) + v2 (draft, as of 2026-08-30)

## What is ACP?

The Agent Client Protocol (ACP) is a JSON-RPC 2.0 standard for bidirectional communication between code editors (clients) and AI-powered coding agents. Created by Zed Industries in August 2025, ACP solves the N x M integration problem: without a standard protocol, every editor must build custom integrations for every agent. ACP is the "LSP for AI agents." [VERIFIED] (ACP-SC-ACPORG-OVRVW, ACP-SC-MRCNR-INTRO)

**Not to be confused with**: Agent Communication Protocol (IBM/BeeAI) or Agentic Commerce Protocol (OpenAI/Stripe). The canonical ACP references agentclientprotocol.com. [VERIFIED] (ACP-SC-MRCNR-INTRO)

## Three-Actor Model

ACP defines three actors: [VERIFIED] (ACP-SC-ACPORG-ARCH)

- **Client** (Editor/IDE): Hosts the UI, manages files, mediates permissions. Examples: Zed, JetBrains, Neovim
- **Agent**: AI-powered program that processes prompts and performs actions. Examples: Gemini CLI, Goose, Cline, Cursor
- **MCP Servers**: Tool providers connected via Model Context Protocol. ACP handles editor-to-agent; MCP handles agent-to-tool

## Current Status (August 2026)

- **Protocol v1**: Stable, with 17+ feature stabilizations via RFD process
- **Protocol v2**: Draft published July 20, 2026. Breaking changes to prompt lifecycle, tool calls, capabilities. Not yet stabilized. [VERIFIED] (ACP-SC-ACPORG-V2DFT)
- **Agents**: 40+ implementations (native and adapter-based) [VERIFIED] (ACP-SC-ACPORG-AGNTS)
- **Clients**: 50+ implementations across 8 categories (editors, CLI/TUI, desktop/web, mobile, messaging, notebooks, frameworks, connectors) [VERIFIED] (ACP-SC-ACPORG-CLNTS)
- **SDKs**: 5 official (Kotlin, Java, Python, Rust, TypeScript). Rust and TypeScript reached 1.0 in June 2026. [VERIFIED] (ACP-SC-ANN-SDK10)
- **Registry**: Curated agent discovery at cdn.agentclientprotocol.com [VERIFIED] (ACP-SC-ACPORG-RGSTR)
- **Governance**: Open RFD process, Lead Maintainer Sergey Ignatov, Transports Working Group [VERIFIED] (ACP-SC-ACPORG-UPDTS)

## Key Strengths

- **Rapid adoption**: From single-vendor (Zed) to 40+ agents and 50+ clients in under a year
- **MCP-complementary**: ACP + MCP together cover the full editor-agent-tool chain
- **Extensible**: `_meta` fields, extension methods, custom capabilities without breaking compatibility
- **Human-in-the-loop**: Built-in permission system for user control over agent actions
- **Elicitation**: Agents can request structured user input via forms or URL-based flows [VERIFIED] (ACP-SC-ANN-ELCTN)

## Key Weaknesses

- **No native VS Code support**: Microsoft chose MCP for VS Code agent mode. Community extension only. [VERIFIED] (ACP-SC-MRPH-EXPL)
- **stdio-only transport** (practical): Streamable HTTP described but not yet widely implemented
- **Adapter tax**: Claude Code and Codex CLI require Zed-maintained bridges
- **v2 migration ahead**: Breaking changes will require effort from all implementations

## v1 Stabilizations Since June 2026

Features stabilized after the previous documentation version (2026-06-12): [VERIFIED] (ACP-SC-ACPORG-UPDTS)

- **Elicitation**: `elicitation/create` and `elicitation/complete` for structured user input (July 24, 2026)
- **Boolean Config Options**: `sessionCapabilities.configOptions.boolean` for native on/off controls
- **Request Cancellation**: `$/cancel_request` notification for protocol-level request cancellation (June 29, 2026)
- **Model Config Category**: `model_config` category for session configuration
- **Message IDs**: Optional `messageId` fields on streamed message chunks
- **Session Usage Updates**: `usage_update` notifications for token/cost tracking
- **Session Delete**: `session/delete` method for removing sessions
- **SDK 1.0 Releases**: Rust and TypeScript SDKs reached v1.0.0 (June 25, 2026)

## v2 Proposal (Draft, July 2026)

ACP v2 is a consolidation release. Key breaking changes: [VERIFIED] (ACP-SC-ACPORG-V2DFT, ACP-SC-ACPORG-V2MIG)

- **Prompt lifecycle redesigned**: `session/prompt` response is acknowledgment only; all output via `session/update`. New `state_update` (running/idle/requires_action) carries the stop reason on idle (the StopReason enum itself is unchanged).
- **Unified tool calls**: Single `tool_call_update` upsert replaces split `tool_call`/`tool_call_update`. Streaming via `tool_call_content_chunk`.
- **Diff overhaul**: Structured `changes` array (add/delete/modify/move/copy) + optional `git_patch` replaces `oldText`/`newText`.
- **Capability reorganization**: Single `capabilities` field, object support markers (`{}` = supported).
- **Client fs/terminal removed**: Replaced by MCP-based alternatives.
- **session/load removed**: `session/resume` with `replayFrom` handles both use cases.
- **Authentication renamed**: `authenticate` becomes `auth/login`, `logout` becomes `auth/logout`.

See `_INFO_ACP-16_V2MigrationOverview.md [ACP-IN16]` for full migration details.

## Documentation Structure

This documentation set contains 16 INFO files organized into 6 categories:

### Overview (2)
- **IN01** (this file): Summary and overview
- **IN02**: Source registry

### Architecture and Problem (2)
- **IN03**: Problem and solution (N x M, ACP vs MCP vs A2A)
- **IN04**: Architecture (three-actor model, JSON-RPC 2.0)

### Protocol Specification (7)
- **IN05**: Initialization and capability negotiation
- **IN06**: Session lifecycle (create, load, resume, close, delete, list)
- **IN07**: Prompt turn and streaming
- **IN08**: Tool calls and permissions
- **IN09**: Authentication and security
- **IN10**: Transports and extensibility
- **IN15**: Elicitation (structured user input) [NEW]

### Ecosystem (2)
- **IN11**: Agents and clients ecosystem
- **IN12**: SDKs and libraries

### Evolution (2)
- **IN13**: Version history and roadmap
- **IN16**: v2 migration overview [NEW]

### Best Practices (1)
- **IN14**: Gotchas, limitations, and best practices

## Sources

- ACP-SC-ACPORG-OVRVW - Protocol v1 overview
- ACP-SC-ACPORG-ARCH - Architecture and design philosophy
- ACP-SC-ACPORG-UPDTS - Updates and stabilization announcements
- ACP-SC-ACPORG-V2DFT - v2 draft announcement (July 20, 2026)
- ACP-SC-ACPORG-V2MIG - v2 migration guide
- ACP-SC-ACPORG-AGNTS - Agent ecosystem list
- ACP-SC-ACPORG-CLNTS - Client ecosystem list
- ACP-SC-ANN-ELCTN - Elicitation stabilization announcement
- ACP-SC-ANN-SDK10 - SDK 1.0 release announcement
- ACP-SC-MRCNR-INTRO - Ecosystem analysis and ACP introduction
- ACP-SC-MRPH-EXPL - FAQ, VS Code status, SDK examples

## Document History

**[2026-08-30 14:20]**
- Fixed: boolean config options capability path (`sessionCapabilities.configOptions.boolean`); v2 state_update wording (stop reasons unchanged, moved to idle state_update)

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: v1 stabilizations since June 2026 (7 features + SDK 1.0)
- Added: v2 proposal summary (published July 20, 2026)
- Updated: Ecosystem counts (40+ agents, 50+ clients, up from 35+/20+)
- Updated: Documentation structure (16 files, up from 14; added IN15, IN16)
- Added: Elicitation as key strength

**[2026-06-12 09:00]**
- Initial document created
