# Agent Client Protocol (ACP) - Summary

**Doc ID**: ACP-IN01
**Goal**: Cross-document synthesis and master index for ACP deep research
**Version scope**: ACP Protocol v1 (as of 2026-06-12), v2 draft proposal
**Research stats**: ~60m net | 12 topic files | 21 sources (15 T1 / 3 T2 / 3 T3) | 5 categories | 3 dimensions (technical / practical / historical)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Summary

The Agent Client Protocol (ACP) is an open JSON-RPC 2.0 standard created by Zed Industries (makers of the Zed code editor, founded by former Atom team members) in August 2025 that standardizes communication between code editors and AI coding agents, solving the same N x M fragmentation problem that the Language Server Protocol (LSP) solved for language tooling [VERIFIED] (ACP-SC-ACPORG-INTRO, ACP-SC-MRCNR-INTRO). ACP is explicitly complementary to Anthropic's Model Context Protocol (MCP): ACP handles the editor-to-agent layer (UI, sessions, permissions), while MCP handles the agent-to-tool layer, and the two wire up together at session creation time [VERIFIED] (ACP-SC-ACPORG-ARCH). The protocol's three-actor model (client/agent/MCP server) uses bidirectional JSON-RPC 2.0 over stdio as its primary transport, with Streamable HTTP under active development by a dedicated Transports Working Group [VERIFIED] (ACP-SC-ACPORG-TRNSP, ACP-SC-ACPORG-UPDTS).

As of June 2026, 35+ agents and 20+ clients implement ACP across editors (Zed, JetBrains, Neovim, Emacs), desktop/web apps, mobile clients, and messaging platforms [VERIFIED] (ACP-SC-ACPORG-AGNTS, ACP-SC-ACPORG-CLNTS). Official SDKs exist for five languages (Kotlin, Java, Python, Rust, TypeScript) with growing community libraries. Protocol v1 is stable with 10+ feature stabilizations including session resume, session close, logout, and the ACP Registry. A v2 proposal is in draft, introducing breaking changes: removal of session modes and client filesystem/terminal surface, unified tool call updates, plan variants, and restructured capability negotiation [VERIFIED] (ACP-SC-ACPORG-V2).

Key strengths include rapid multi-vendor adoption (Zed + JetBrains + Google within 5 months), clean separation of concerns from MCP, and a permission model giving users per-action control. Key weaknesses include no native VS Code support (Microsoft chose MCP), stdio-only practical transport limiting remote scenarios, adapter-only support for Claude Code and Codex CLI, and the pending v2 migration that will require implementation changes [SYNTHESIZED from all sources]. The most common gotcha is misattribution to Anthropic and confusion with two other protocols using the "ACP" acronym.

**Not in scope of ACP:** Skills, workflows, slash commands, and direct-call syntax are entirely outside the protocol. `session/prompt` accepts free-form text content blocks with no structured field for command name, skill reference, or procedure invocation. If a user types `/verify` in an ACP client, the editor passes that string as plain text; the agent interprets it. Cross-platform command portability comes from file conventions (SKILL.md format, `.agents/` standard), not from ACP. [VERIFIED]

## Topic Files

### Overview and Architecture (2 files)

- [`_INFO_ACP-03_ProblemAndSolution.md`](./_INFO_ACP-03_ProblemAndSolution.md) [ACP-IN03]
  - Why ACP exists, the N x M integration problem, LSP analogy, positioning vs MCP and A2A
- [`_INFO_ACP-04_Architecture.md`](./_INFO_ACP-04_Architecture.md) [ACP-IN04]
  - Three-actor model (client/agent/MCP server), design philosophy, communication model, message flow

### Protocol Specification (6 files)

- [`_INFO_ACP-05_Initialization.md`](./_INFO_ACP-05_Initialization.md) [ACP-IN05]
  - Protocol version negotiation, client/agent capabilities, implementation info
- [`_INFO_ACP-06_SessionLifecycle.md`](./_INFO_ACP-06_SessionLifecycle.md) [ACP-IN06]
  - Session create/load/resume/close/delete/list, workspace roots, MCP server config
- [`_INFO_ACP-07_PromptTurnAndStreaming.md`](./_INFO_ACP-07_PromptTurnAndStreaming.md) [ACP-IN07]
  - 6-step prompt turn lifecycle, streaming via notifications, message IDs, usage updates, stop reasons, cancellation
- [`_INFO_ACP-08_ToolCallsAndPermissions.md`](./_INFO_ACP-08_ToolCallsAndPermissions.md) [ACP-IN08]
  - Tool call creation/updating, permission model (4 options), diffs, terminals, content types
- [`_INFO_ACP-09_AuthenticationAndSecurity.md`](./_INFO_ACP-09_AuthenticationAndSecurity.md) [ACP-IN09]
  - Auth method advertising, authenticate/logout flow, security model, trust assumptions
- [`_INFO_ACP-10_TransportsAndExtensibility.md`](./_INFO_ACP-10_TransportsAndExtensibility.md) [ACP-IN10]
  - stdio transport, Streamable HTTP, custom transports, _meta fields, extension methods, custom capabilities

### Ecosystem (2 files)

- [`_INFO_ACP-11_AgentsAndClients.md`](./_INFO_ACP-11_AgentsAndClients.md) [ACP-IN11]
  - Agent implementations (native vs adapter), client implementations (editors, CLI, desktop, mobile, messaging), frameworks
- [`_INFO_ACP-12_SDKsAndLibraries.md`](./_INFO_ACP-12_SDKsAndLibraries.md) [ACP-IN12]
  - Official SDKs (Kotlin, Java, Python, Rust, TypeScript), community libraries, implementation examples

### Evolution and Roadmap (1 file)

- [`_INFO_ACP-13_VersionHistoryAndRoadmap.md`](./_INFO_ACP-13_VersionHistoryAndRoadmap.md) [ACP-IN13]
  - Timeline (Aug 2025 to present), v1 stabilization milestones, v2 proposal changes, RFD process, governance

### Best Practices and Limitations (1 file)

- [`_INFO_ACP-14_GotchasAndBestPractices.md`](./_INFO_ACP-14_GotchasAndBestPractices.md) [ACP-IN14]
  - Known limitations, security concerns, interoperability issues, production patterns, common pitfalls, recommendations

## Topic Count

- **Total Topics**: 12
- **Overview and Architecture**: 2
- **Protocol Specification**: 6
- **Ecosystem**: 2
- **Evolution and Roadmap**: 1
- **Best Practices and Limitations**: 1

## Topic Details

### Topic: ProblemAndSolution
**Scope**: Why ACP was created and what problem it solves
**Contents**:
- The N x M integration problem (every editor needs custom integration for every agent)
- LSP analogy: one standard, N editors, M agents
- ACP vs MCP vs A2A positioning (complementary layers)
- Design goals: portability, no vendor lock-in, shared UX
**Sources**: ACP-SC-ACPORG-INTRO, ACP-SC-MRCNR-INTRO, ACP-SC-MRPH-EXPL

### Topic: Architecture
**Scope**: Protocol architecture and communication model
**Contents**:
- Three-actor model: Client (editor), Agent (AI), MCP Server (tools)
- Design philosophy: MCP-friendly, UX-first, trusted
- JSON-RPC 2.0 communication, methods vs notifications
- Message flow: initialization, session setup, prompt turns
**Sources**: ACP-SC-ACPORG-ARCH, ACP-SC-ACPORG-OVRVW, ACP-SC-MRCNR-INTRO

### Topic: Initialization
**Scope**: How ACP connections begin
**Contents**:
- Protocol version negotiation (integer version, currently 1)
- Client capabilities (fs, terminal)
- Agent capabilities (loadSession, prompt types, MCP, auth, session features)
- Implementation information exchange
**Sources**: ACP-SC-ACPORG-INIT, ACP-SC-ACPORG-OVRVW

### Topic: SessionLifecycle
**Scope**: Full session management
**Contents**:
- session/new, session/load, session/resume, session/close, session/delete, session/list
- Working directory and additional workspace roots
- MCP server configuration (stdio, HTTP, SSE transports)
- Session ID management
**Sources**: ACP-SC-ACPORG-SSSTP, ACP-SC-ACPORG-OVRVW

### Topic: PromptTurnAndStreaming
**Scope**: Core conversation flow and real-time streaming
**Contents**:
- 6-step lifecycle: user message, agent processing, output, completion check, tool invocation, continue
- session/update notifications for streaming (agent_message_chunk, plan, tool_call, usage_update)
- Message IDs for chunk correlation
- Stop reasons (end_turn, cancelled, etc.), session/cancel
**Sources**: ACP-SC-ACPORG-PRMPT, ACP-SC-MRPH-EXPL

### Topic: ToolCallsAndPermissions
**Scope**: Tool execution and permission model
**Contents**:
- Tool call lifecycle: create (pending), update (in_progress), complete
- 9 tool kinds: read, edit, delete, move, search, execute, think, fetch, other
- Permission request/response: allow_once, allow_always, reject_once, reject_always
- Tool content types: regular content, diffs (oldText/newText), terminal references
**Sources**: ACP-SC-ACPORG-TLCLL, ACP-SC-MRPH-EXPL

### Topic: AuthenticationAndSecurity
**Scope**: Authentication flows and security model
**Contents**:
- Auth method advertising in initialize response
- authenticate request with methodId
- logout capability and flow
- Trust model: editor controls permissions, agent is trusted subprocess
**Sources**: ACP-SC-ACPORG-AUTH, ACP-SC-MRPH-EXPL

### Topic: TransportsAndExtensibility
**Scope**: Communication transports and protocol extension mechanisms
**Contents**:
- stdio transport (primary): newline-delimited JSON-RPC over stdin/stdout
- Streamable HTTP (roadmap)
- _meta fields for custom data, W3C trace context support
- Underscore-prefixed extension methods (requests and notifications)
- Custom capabilities advertising
**Sources**: ACP-SC-ACPORG-TRNSP, ACP-SC-ACPORG-EXTNS

### Topic: AgentsAndClients
**Scope**: Ecosystem of ACP implementations
**Contents**:
- 35+ agents (native: Gemini CLI, Goose, Cline; via adapter: Claude Code, Codex CLI)
- Editors: Zed (reference), JetBrains, Neovim, Emacs, VSCode (community extension)
- CLI/TUI, desktop/web, mobile, messaging (Discord, Slack, Telegram), notebooks
- Frameworks: LangChain, Mastra, LlamaIndex, Koog
**Sources**: ACP-SC-ACPORG-AGNTS, ACP-SC-ACPORG-CLNTS, ACP-SC-MRCNR-INTRO

### Topic: SDKsAndLibraries
**Scope**: Official and community SDK implementations
**Contents**:
- Official: Kotlin (acp-kotlin), Java (java-sdk), Python (python-sdk), Rust (agent-client-protocol crate), TypeScript (@agentclientprotocol/sdk)
- Python example: EchoAgent with stream_text
- TypeScript example: createAcpAgent with readFile and streamText
- Community libraries and AI SDK integration
**Sources**: ACP-SC-GH-REPO, ACP-SC-MRPH-EXPL, ACP-SC-AISDK-PRVDR

### Topic: VersionHistoryAndRoadmap
**Scope**: Protocol evolution from inception to future
**Contents**:
- Timeline: Zed intro (Aug 2025), JetBrains (Oct 2025), Registry (Jan 2026), stabilizations (2025-2026)
- v1 stabilization milestones (session config, session list, session info update, registry, session resume, session close, logout)
- v2 proposal: remove session modes, remove client fs/terminal surface, plan variants, unified tool_call updates, capability reorganization
- RFD process, governance (Sergey Ignatov as Lead Maintainer), Transports Working Group
**Sources**: ACP-SC-ACPORG-UPDTS, ACP-SC-ACPORG-V2, ACP-SC-MRCNR-INTRO

### Topic: GotchasAndBestPractices
**Scope**: Known limitations, pitfalls, and recommendations
**Contents**:
- No native VS Code support (Microsoft chose MCP for agent mode)
- ACP acronym confusion (3 different protocols use "ACP")
- Claude Code requires Zed adapter bridge, not native
- stdio-only transport limits remote deployment scenarios
- v2 breaking changes require migration planning
- Security: trusted agent model, permission model per tool call
**Sources**: ACP-SC-MRPH-EXPL, ACP-SC-MRCNR-INTRO, ACP-SC-ACPORG-V2

## Document History

**[2026-08-04 17:10]**
- Added: Explicit note that skills/workflows/commands are outside ACP scope (referenced from SKLWRKFL-IN01)

**[2026-06-12 10:20]**
- Summary finalized with full cross-document synthesis and research stats

**[2026-06-12 09:40]**
- Initial skeletal Summary created with 12 topics in 5 categories
