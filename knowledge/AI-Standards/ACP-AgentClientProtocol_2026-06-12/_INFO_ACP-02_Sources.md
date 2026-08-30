# ACP Agent Client Protocol - Sources

**Doc ID**: ACP-IN02
**Goal**: Source registry for ACP deep research
**Version scope**: ACP Protocol v1 (as of 2026-06-12)
**Preflight accuracy**: 2/8 verified (25% - significant corrections applied)

## Source Registry

### Tier 1: Official Specification and Documentation

- **ACP-SC-ACPORG-INTRO** - Introduction to ACP
  - URL: https://agentclientprotocol.com/get-started/introduction
  - Accessed: 2026-06-12
  - Content: Why ACP exists, overview of local/remote agent models

- **ACP-SC-ACPORG-ARCH** - Architecture
  - URL: https://agentclientprotocol.com/get-started/architecture
  - Accessed: 2026-06-12
  - Content: Design philosophy (MCP-friendly, UX-first, trusted), setup, MCP integration

- **ACP-SC-ACPORG-OVRVW** - Protocol v1 Overview
  - URL: https://agentclientprotocol.com/protocol/v1/overview
  - Accessed: 2026-06-12
  - Content: Communication model, message flow, agent/client baseline/optional methods, error handling, conventions, extensibility

- **ACP-SC-ACPORG-INIT** - Initialization
  - URL: https://agentclientprotocol.com/protocol/v1/initialization
  - Accessed: 2026-06-12
  - Content: Protocol version negotiation, client/agent capabilities, implementation info

- **ACP-SC-ACPORG-SSSTP** - Session Setup
  - URL: https://agentclientprotocol.com/protocol/v1/session-setup
  - Accessed: 2026-06-12
  - Content: Creating/loading/resuming/closing sessions, workspace roots, MCP server config, transport types

- **ACP-SC-ACPORG-PRMPT** - Prompt Turn
  - URL: https://agentclientprotocol.com/protocol/v1/prompt-turn
  - Accessed: 2026-06-12
  - Content: 6-step prompt turn lifecycle, message IDs, usage updates, stop reasons, cancellation

- **ACP-SC-ACPORG-TLCLL** - Tool Calls
  - URL: https://agentclientprotocol.com/protocol/v1/tool-calls
  - Accessed: 2026-06-12
  - Content: Tool call creation/updating, permission model (allow_once/always, reject_once/always), diffs, terminals

- **ACP-SC-ACPORG-AUTH** - Authentication
  - URL: https://agentclientprotocol.com/protocol/v1/authentication
  - Accessed: 2026-06-12
  - Content: Auth method advertising, authenticate/logout flow, active sessions

- **ACP-SC-ACPORG-CNTNT** - Content
  - URL: https://agentclientprotocol.com/protocol/v1/content
  - Accessed: 2026-06-12
  - Content: Content block types (text, image, audio, embedded resource, resource link), MCP type reuse

- **ACP-SC-ACPORG-TRNSP** - Transports
  - URL: https://agentclientprotocol.com/protocol/v1/transports
  - Accessed: 2026-06-12
  - Content: stdio transport (primary), Streamable HTTP (roadmap), custom transports

- **ACP-SC-ACPORG-EXTNS** - Extensibility
  - URL: https://agentclientprotocol.com/protocol/v1/extensibility
  - Accessed: 2026-06-12
  - Content: _meta fields, underscore-prefixed extension methods, custom capabilities advertising

- **ACP-SC-ACPORG-LLMS** - llms.txt Documentation Index
  - URL: https://agentclientprotocol.com/llms.txt
  - Accessed: 2026-06-12
  - Content: Full documentation index including all protocol pages, RFDs, announcements, libraries

- **ACP-SC-ACPORG-UPDTS** - Updates and Announcements
  - URL: https://agentclientprotocol.com/updates
  - Accessed: 2026-06-12
  - Content: Stabilization timeline (session config, session list, session info update, registry, transports WG, session resume, session close, logout)

- **ACP-SC-ACPORG-V2** - ACP v2 Proposal
  - URL: https://agentclientprotocol.com/rfds/v2/overview
  - Accessed: 2026-06-12
  - Content: v2 breaking changes (remove session modes API, remove client fs/terminal surface, plan variants, unified tool_call updates, message updates, capability reorganization, MCP transport alignment)

### Tier 2: Official Repositories and Blog Posts

- **ACP-SC-GH-REPO** - GitHub Repository (agentclientprotocol/agent-client-protocol)
  - URL: https://github.com/agentclientprotocol/agent-client-protocol
  - Accessed: 2026-06-12
  - Content: README, versioning model, integrations list, official SDK links (Kotlin, Java, Python, Rust, TypeScript), Apache 2.0 license

- **ACP-SC-ACPORG-AGNTS** - Agents List
  - URL: https://agentclientprotocol.com/get-started/agents
  - Accessed: 2026-06-12
  - Content: 35+ agents implementing ACP (Claude Code via adapter, Gemini CLI native, Copilot CLI preview, Goose, Cline, Cursor, OpenHands, etc.)

- **ACP-SC-ACPORG-CLNTS** - Clients List
  - URL: https://agentclientprotocol.com/get-started/clients
  - Accessed: 2026-06-12
  - Content: Editors (Zed, JetBrains, Neovim, Emacs, VSCode extension), CLI/TUI, desktop/web, notebooks, mobile, messaging (Discord, Slack, Telegram), frameworks (LangChain, Mastra, LlamaIndex)

### Tier 3: Community Analysis and Tutorials

- **ACP-SC-MRCNR-INTRO** - Marc Nuri: ACP Introduction Blog
  - URL: https://blog.marcnuri.com/agent-client-protocol-acp-introduction
  - Accessed: 2026-06-12
  - Content: LSP analogy, ACP disambiguation (3 different "ACP" protocols), ACP vs MCP comparison, ecosystem overview, timeline (Zed Aug 2025, JetBrains Oct 2025, Registry Jan 2026)

- **ACP-SC-MRPH-EXPL** - Morph LLM: ACP Explained
  - URL: https://www.morphllm.com/agent-client-protocol
  - Accessed: 2026-06-12
  - Content: 5 core message types, permission model, MCP integration at session start, protocol version/extensibility, Python/TypeScript SDK examples, FAQ (VS Code no native support, Claude Code via bridge)

- **ACP-SC-AISDK-PRVDR** - AI SDK: ACP Community Provider
  - URL: https://ai-sdk.dev/providers/community-providers/acp
  - Accessed: 2026-06-12
  - Content: AI SDK integration pattern for ACP agents

## Document History

**[2026-06-12 09:30]**
- Initial sources collected: 15 Tier 1, 3 Tier 2, 3 Tier 3
- Preflight accuracy: 2/8 verified (25%)
