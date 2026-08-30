# ACP: Version History and Roadmap

**Doc ID**: ACP-IN13
**Goal**: Document ACP's timeline, v1 milestones, v2 proposal, and governance
**Version scope**: Inception (Aug 2025) through August 2026

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP was introduced by Zed Industries in August 2025 and grew from a Zed-specific integration mechanism to a multi-vendor standard within months. Protocol v1 is stable with 17+ feature stabilizations. v2 was published in draft form on July 20, 2026, introducing breaking changes to the prompt lifecycle, tool calls, capabilities, and session management. Governance follows an open RFD process with working groups. [VERIFIED] (ACP-SC-MRCNR-INTRO, ACP-SC-ACPORG-UPDTS, ACP-SC-ACPORG-V2DFT)

## Timeline

### 2025

- **August 2025**: Zed introduces ACP in "Bring Your Own Agent to Zed" blog post [VERIFIED] (ACP-SC-MRCNR-INTRO)
- **September 2025**: "Claude Code via ACP" blog post by Zed, establishing adapter pattern [VERIFIED] (ACP-SC-MRCNR-INTRO)
- **October 2025**: JetBrains announces ACP interoperability, transforming ACP to multi-vendor standard [VERIFIED] (ACP-SC-MRCNR-INTRO)
- **December 2025**: "Bring your own AI agent to JetBrains IDEs" blog post [VERIFIED] (ACP-SC-MRCNR-INTRO)

### 2026 (January - June 12)

- **January 2026**: ACP Registry launched. GitHub Copilot CLI ACP support enters public preview [VERIFIED] (ACP-SC-MRCNR-INTRO, ACP-SC-ACPORG-AGNTS)
- **2026 (early)**: Session Config Options, Implementation Information, Session List, Session Info Update, Session Resume, Session Close, Logout Method, Transports Working Group formed, Additional Workspace Roots stabilized. Sergey Ignatov joins as Lead Maintainer. [VERIFIED] (ACP-SC-ACPORG-UPDTS)

### 2026 (June 12 - August 30) - Changes since previous docs

- **June 25, 2026**: Rust and TypeScript SDKs reach v1.0.0 [VERIFIED] (ACP-SC-ANN-SDK10)
- **June 29, 2026**: Request Cancellation (`$/cancel_request`) stabilized [VERIFIED] (ACP-SC-ANN-RQCNL)
- **2026 (June-July)**: Message IDs, Session Usage Updates (`usage_update`), Session Delete (`session/delete`), Model Config Category, Boolean Config Options stabilized [VERIFIED] (ACP-SC-ACPORG-UPDTS)
- **July 2, 2026**: v2 RFD collection moved to Active status [VERIFIED] (ACP-SC-ACPORG-V2)
- **July 20, 2026**: **ACP v2 Draft published** - First draft of protocol v2 documentation and schema [VERIFIED] (ACP-SC-ACPORG-V2DFT)
- **July 24, 2026**: Elicitation (`elicitation/create`, `elicitation/complete`) stabilized [VERIFIED] (ACP-SC-ANN-ELCTN)
- **August 2026**: Python SDK reaches v0.12.1 with ACP schema v1.19.0 and HTTP/WS transport [VERIFIED] (ACP-SC-PYPI-ACP)

## v1 Stabilization Milestones (Complete List)

All features stabilized through the RFD process as of August 2026: [VERIFIED] (ACP-SC-ACPORG-UPDTS)

1. Implementation Information - Optional metadata exchange during initialization
2. Session Config Options - Flexible configuration selectors
3. Session List - `session/list` method
4. Session Info Update - `session_info_update` notification
5. ACP Registry - Agent registry specification
6. Transports Working Group - Formed for new transport formats
7. Session Resume - `session/resume` method
8. Session Close - `session/close` method
9. Logout Method - `logout` method
10. Additional Workspace Roots - `additionalDirectories` stabilized
11. Session Delete - `session/delete` method
12. Session Usage Updates - `usage_update` notifications
13. Message IDs - Optional `messageId` fields
14. Model Config Category - `model_config` configuration options
15. Rust and TypeScript SDKs 1.0 - Stable SDK foundation
16. Request Cancellation - `$/cancel_request` notification
17. Boolean Config Options - `session.configOptions.boolean`
18. Elicitation - `elicitation/create` and `elicitation/complete`

## v2 Draft (Published July 20, 2026)

The v2 draft introduces breaking changes. Status: **Draft** (not yet stabilized). [VERIFIED] (ACP-SC-ACPORG-V2DFT)

Key changes:
- Prompt lifecycle redesigned (response = acknowledgment, output via session/update)
- Unified tool call upsert pattern
- Structured diff content (changes array + git_patch)
- Capability reorganization (single capabilities field)
- Client fs/terminal removed
- session/load removed (session/resume covers both)
- Authentication method renames (auth/login, auth/logout)
- Forward-compatible schema (unknown fields preserved)
- Agent-owned terminal display

See `_INFO_ACP-16_V2MigrationOverview.md [ACP-IN16]` for full details.

### v2 RFD Timeline

- 2026-06-05: Capability cleanup recorded [VERIFIED] (ACP-SC-ACPORG-V2)
- 2026-06-08: Tool Call Updates RFD added
- 2026-06-09: Message Updates and Chunks RFD added
- 2026-06-25: Initialize information cleanup, auth method cleanup
- 2026-07-02: v2 RFD collection moved to Active; Permission Requests, Session Resume Replay, Required Session Methods, File States RFDs added
- 2026-07-14: Terminal Output RFD added
- 2026-07-20: v2 draft published; git_patch clarified, auth surface scoped

## Governance

### RFD Process

Changes follow Requests for Dialog (RFD) lifecycle: Draft -> Preview -> Completed. [VERIFIED] (ACP-SC-ACPORG-LLMS)

### Maintainers

- **Sergey Ignatov**: Lead Maintainer [VERIFIED] (ACP-SC-ACPORG-UPDTS)

### Working Groups

- **Transports Working Group**: Standardizing remote agent transports (HTTP, WebSocket) [VERIFIED] (ACP-SC-ACPORG-UPDTS)

### Contributing

Apache License 2.0 without CLA requirement. [VERIFIED] (ACP-SC-GH-REPO)

## Versioning Model

Two-level approach: [VERIFIED] (ACP-SC-GH-REPO)

- **Protocol version**: Single integer (1 stable, 2 draft). Negotiated during `initialize`.
- **Artifact version**: SDK crate/package versions follow their own semver.
- **Compatibility rule**: Use `protocolVersion` for wire compatibility; capabilities for optional features; artifact versions for SDK compatibility.

## Quick Reference

- **Created**: August 2025 by Zed Industries
- **Protocol v1**: Stable, 18 feature stabilizations
- **Protocol v2**: Draft (published July 20, 2026)
- **License**: Apache 2.0
- **Governance**: RFD process, working groups
- **Lead Maintainer**: Sergey Ignatov

## Limitations and Gotchas

- v2 breaking changes will require migration effort for all implementations
- Client fs/terminal removal in v2 means current implementations need alternatives
- Session modes API deprecated; use Session Config Options
- Two-level versioning (protocol vs artifact) causes confusion
- v2 is draft; gate implementations behind version negotiation AND feature flags
- RFD process means changes take time to stabilize

## Sources

- ACP-SC-ACPORG-UPDTS - Official updates and stabilization announcements
- ACP-SC-ACPORG-V2 - v2 RFD collection and timeline
- ACP-SC-ACPORG-V2DFT - v2 draft announcement
- ACP-SC-ACPORG-V2MIG - v2 migration guide
- ACP-SC-MRCNR-INTRO - Timeline and ecosystem evolution
- ACP-SC-GH-REPO - Versioning model, contributing policy
- ACP-SC-ACPORG-LLMS - RFD process documentation
- ACP-SC-ANN-SDK10 - SDK 1.0 releases
- ACP-SC-ANN-RQCNL - Request cancellation stabilization
- ACP-SC-ANN-ELCTN - Elicitation stabilization
- ACP-SC-PYPI-ACP - Python SDK version history

## Document History

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: Complete timeline from June 12 to August 30, 2026
- Added: 8 new stabilization milestones (items 11-18)
- Added: v2 draft publication details and RFD timeline
- Updated: Total stabilizations from 10+ to 18
- Added: Python SDK v0.12.1 timeline entry

**[2026-06-12 10:15]**
- Initial document created
