# ACP: Problem and Solution

**Doc ID**: ACP-IN03
**Goal**: Document the problem ACP solves and how it differs from related protocols
**Version scope**: ACP Protocol v1 (stable) + v2 (draft, as of 2026-08-30)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## The N x M Integration Problem

Without a standard protocol, every code editor must build custom integrations for every AI coding agent. With E editors and A agents, this requires E x A integrations. ACP reduces this to E + A: each editor implements the ACP client side, each agent implements the ACP agent side, and all combinations work. [VERIFIED] (ACP-SC-ACPORG-OVRVW)

This mirrors the Language Server Protocol (LSP) pattern: LSP solved the same N x M problem for language features (syntax highlighting, code completion). ACP is "LSP for AI agents." [VERIFIED] (ACP-SC-MRCNR-INTRO)

### Scale of the Problem (August 2026)

- 40+ agents listed on agentclientprotocol.com [VERIFIED] (ACP-SC-ACPORG-AGNTS)
- 50+ clients across 8 categories [VERIFIED] (ACP-SC-ACPORG-CLNTS)
- Without ACP: 40 x 50 = 2000 custom integrations
- With ACP: 40 + 50 = 90 implementations

## ACP vs MCP vs A2A

Three protocols serve different communication channels in the AI agent ecosystem: [VERIFIED] (ACP-SC-ACPORG-OVRVW, ACP-SC-MRCNR-INTRO)

- **ACP (Agent Client Protocol)**: Editor-to-Agent communication. Created by Zed Industries (Aug 2025). JSON-RPC 2.0 over stdio. Handles UI interaction, permissions, session management, prompt turns.
- **MCP (Model Context Protocol)**: Agent-to-Tool communication. Created by Anthropic (Nov 2024). Provides tools, resources, and prompts to agents from external services.
- **A2A (Agent-to-Agent Protocol)**: Agent-to-Agent communication. Created by Google (Apr 2025). Enables agents to discover and collaborate with other agents.

These protocols are complementary, not competing:
```
Editor/IDE <--ACP--> Agent <--MCP--> Tool Servers
                       |
                      A2A
                       |
                   Other Agents
```

## ACP Acronym Confusion

Three different protocols use the "ACP" acronym: [VERIFIED] (ACP-SC-MRCNR-INTRO)

- **Agent Client Protocol** (Zed Industries): This documentation. Editor-to-agent. agentclientprotocol.com
- **Agent Communication Protocol** (IBM/BeeAI): Agent-to-agent orchestration. Different domain.
- **Agentic Commerce Protocol** (OpenAI/Stripe): Payment and commerce for AI agents. Different domain.

Search results and LLM responses frequently confuse these. Always verify the source domain.

## Common Misattribution

ACP is frequently attributed to Anthropic. This is incorrect: [VERIFIED] (ACP-SC-MRCNR-INTRO, ACP-SC-MRPH-EXPL)

- **Anthropic created MCP** (Model Context Protocol), not ACP
- **Zed Industries created ACP** (Agent Client Protocol)
- Anthropic's Claude Code participates in ACP only via an adapter maintained by Zed

## ACP Design Goals

- **MCP-friendly**: Agents can proxy MCP server configurations from the editor [VERIFIED] (ACP-SC-ACPORG-ARCH)
- **UX-first**: Rich streaming, permission UI, progress reporting [VERIFIED] (ACP-SC-ACPORG-ARCH)
- **Trusted**: Agent runs as local subprocess; editor mediates destructive actions [VERIFIED] (ACP-SC-ACPORG-ARCH)
- **Extensible**: `_meta` fields, extension methods, custom capabilities [VERIFIED] (ACP-SC-ACPORG-EXTNS)
- **Elicitable**: Agents can request structured user input via forms or URL flows [VERIFIED] (ACP-SC-ANN-ELCTN)

## Limitations of ACP's Approach

- **Local subprocess model**: ACP assumes the agent runs as a trusted local subprocess. Remote agents need additional security layers. v2's Transports Working Group is addressing remote scenarios. [VERIFIED] (ACP-SC-ACPORG-TRNSP)
- **No enforcement**: The permission system is cooperative. The `kind` field on tool calls is informational, not a security boundary. [VERIFIED] (ACP-SC-ACPORG-TLCLL)
- **VS Code gap**: Microsoft chose MCP for VS Code agent mode. ACP has no native VS Code support. [VERIFIED] (ACP-SC-MRPH-EXPL)

## Sources

- ACP-SC-ACPORG-OVRVW - Protocol v1 overview (N x M problem statement)
- ACP-SC-ACPORG-ARCH - Design philosophy and goals
- ACP-SC-ACPORG-EXTNS - Extension mechanisms
- ACP-SC-ACPORG-TRNSP - Transport limitations
- ACP-SC-ACPORG-TLCLL - Tool call kind field (informational only)
- ACP-SC-ACPORG-AGNTS - Agent count (40+)
- ACP-SC-ACPORG-CLNTS - Client count (50+)
- ACP-SC-ANN-ELCTN - Elicitation stabilization
- ACP-SC-MRCNR-INTRO - Ecosystem analysis, acronym disambiguation, LSP analogy
- ACP-SC-MRPH-EXPL - VS Code status, Anthropic misattribution

## Document History

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Updated: Ecosystem counts (40+ agents, 50+ clients)
- Added: Elicitation as design goal
- Added: v2 Transports Working Group context for remote agent limitation

**[2026-06-12 09:15]**
- Initial document created
