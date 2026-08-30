# ACP: Agents and Clients Ecosystem

**Doc ID**: ACP-IN11
**Goal**: Document the ACP ecosystem of agent and client implementations
**Version scope**: As of 2026-06-12

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

The ACP ecosystem has grown rapidly since August 2025, with 35+ agents and 20+ clients as of June 2026. Agents range from native implementations (Gemini CLI, Goose) to adapter-based ones (Claude Code, Codex CLI). Clients span editors (Zed, JetBrains, Neovim), desktop/web apps, mobile clients, messaging platforms, and notebook tools. Framework integrations enable existing AI pipelines to expose or consume ACP. [VERIFIED] (ACP-SC-ACPORG-AGNTS, ACP-SC-ACPORG-CLNTS)

## Agents

### Native ACP Agents (selected)

Agents that implement ACP directly:

- **Gemini CLI** (Google): Supports ACP natively via the `--acp` flag [VERIFIED] (ACP-SC-MRCNR-INTRO)
- **Goose** (Block): Open-source agent with native ACP support
- **Cline**: AI coding assistant with ACP support
- **Cursor**: IDE with ACP agent mode
- **OpenHands**: Open-source agent with ACP integration
- **Mistral Vibe**: Mistral AI's coding agent
- **Augment Code**: Enterprise coding agent
- **Blackbox AI**: AI coding assistant
- **GitHub Copilot CLI**: In public preview for ACP support (announced Jan 2026) [VERIFIED] (ACP-SC-ACPORG-AGNTS)
- **Junie by JetBrains**: JetBrains' own agent
- **Kiro CLI** (AWS): Amazon's AI coding CLI
- **Qwen Code**: Alibaba's coding agent
- **Docker cagent**: Docker's containerized agent

### Adapter-Based Agents

Agents that require bridge adapters to speak ACP:

- **Claude Code** (Anthropic): Via Zed's `claude-agent-acp` adapter. Anthropic has not natively adopted ACP. [VERIFIED] (ACP-SC-MRCNR-INTRO, ACP-SC-MRPH-EXPL)
- **Codex CLI** (OpenAI): Via Zed's `codex-acp` adapter [VERIFIED] (ACP-SC-MRCNR-INTRO)

### Full Agent Count

35+ agents listed on agentclientprotocol.com/get-started/agents as of 2026-06-12. [VERIFIED] (ACP-SC-ACPORG-AGNTS)

## Clients

### Editors and IDEs

- **Zed**: Reference implementation, most complete ACP support [VERIFIED] (ACP-SC-MRPH-EXPL)
- **JetBrains**: Native ACP support added in partnership with Zed (Oct 2025) [VERIFIED] (ACP-SC-MRCNR-INTRO)
- **Neovim**: Via community plugins (CodeCompanion, agentic.nvim, avante.nvim, hermes.nvim) [VERIFIED] (ACP-SC-ACPORG-CLNTS)
- **Emacs**: Via agent-shell.el [VERIFIED] (ACP-SC-ACPORG-CLNTS)
- **VS Code**: Community extension only (vscode-acp), NO native support. Microsoft chose Model Context Protocol (MCP) for VS Code's agent mode. [VERIFIED] (ACP-SC-MRPH-EXPL)
- **Chrome ACP**: Chrome extension / PWA
- **Obsidian**: Via Agent Client plugin
- **Unity**: Two separate plugins (ACP Client, Agent Client)

### CLI and TUI

- acpx (CLI), Nori CLI, pool, Toad [VERIFIED] (ACP-SC-ACPORG-CLNTS)

### Desktop and Web

- ACP UI (cross-platform), Agent Studio, DeepChat, Devin Desktop, Jockey (multi-agent orchestrator), and 15+ more [VERIFIED] (ACP-SC-ACPORG-CLNTS)

### Mobile Clients

- Agmente (iOS), Ferngeist (Android), Happy (iOS/Android/Web), Mobvibe (iOS/Android/Web) [VERIFIED] (ACP-SC-ACPORG-CLNTS)

### Messaging Platforms

- Discord, Slack, Telegram, WeChat, Lark, Matrix via community bridges [VERIFIED] (ACP-SC-ACPORG-CLNTS)

### Notebook and Data Tools

- agent-client-kernel (Jupyter), DuckDB extension, marimo notebook [VERIFIED] (ACP-SC-ACPORG-CLNTS)

## Frameworks

Framework integrations allow existing AI pipelines to work with ACP: [VERIFIED] (ACP-SC-ACPORG-CLNTS)

- **LangChain / LangGraph**: Deep Agents ACP integration
- **Mastra**: `@mastra/acp` package for wrapping agents as tools or subagents
- **LlamaIndex**: workflows-acp adapter
- **Koog** (JetBrains): agents-features-acp integration
- **ACP Kit**: Adapter toolkit for Pydantic AI / LangChain runtimes
- **AgentPool**: Built-in ACP integration for IDEs

## ACP Registry

The ACP Registry (launched January 2026) provides a curated installation surface for discovering and wiring up agents. It is hosted as part of the agentclientprotocol.com website and backed by a GitHub repository. [VERIFIED] (ACP-SC-MRCNR-INTRO, ACP-SC-ACPORG-UPDTS)

## Quick Reference

- **Agents**: 35+ implementations (native and adapter-based)
- **Clients**: 20+ implementations across 7 categories
- **Reference client**: Zed
- **Reference adapter pattern**: claude-agent-acp, codex-acp (by Zed)
- **Registry**: agentclientprotocol.com/get-started/registry

## Limitations and Gotchas

- VS Code has NO native ACP support and likely will not get it (Microsoft invested in MCP instead)
- Claude Code and Codex CLI require Zed-maintained adapters, not official support from Anthropic/OpenAI
- Many community integrations are early-stage with varying quality and completeness
- Mobile and messaging clients are mostly community-driven with limited testing
- The ecosystem list is fast-moving; check the official website for current status

## Sources

- ACP-SC-ACPORG-AGNTS - Official agents list
- ACP-SC-ACPORG-CLNTS - Official clients list
- ACP-SC-MRCNR-INTRO - Ecosystem overview and adapter details
- ACP-SC-MRPH-EXPL - FAQ on editor support and agent compatibility

## Document History

**[2026-06-12 10:10]**
- Initial document created
