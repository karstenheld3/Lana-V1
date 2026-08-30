# ACP: Agents and Clients Ecosystem

**Doc ID**: ACP-IN11
**Goal**: Document the ACP ecosystem of agent and client implementations
**Version scope**: As of 2026-08-30

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

The ACP ecosystem has grown significantly since August 2025. As of August 2026, there are 40+ agents and 50+ clients listed on the official website. Agents range from native implementations (Gemini CLI, Goose, Cursor) to adapter-based ones (Claude Code, Codex CLI). Clients span editors, CLI/TUI tools, desktop/web apps, mobile clients, messaging platforms, notebook tools, frameworks, and connectors. The ACP Registry provides programmatic agent discovery. [VERIFIED] (ACP-SC-ACPORG-AGNTS, ACP-SC-ACPORG-CLNTS, ACP-SC-ACPORG-RGSTR)

## Agents

### Native ACP Agents (selected)

Agents that implement ACP directly: [VERIFIED] (ACP-SC-ACPORG-AGNTS)

- **Gemini CLI** (Google): Native ACP via `--acp` flag
- **Goose** (Block): Open-source agent with native ACP support
- **Cline**: AI coding assistant with ACP support
- **Cursor**: IDE with ACP agent mode
- **OpenHands**: Open-source agent with ACP integration
- **Mistral Vibe**: Mistral AI's coding agent
- **Augment Code**: Enterprise coding agent
- **Blackbox AI**: AI coding assistant
- **GitHub Copilot CLI**: Public preview for ACP support
- **Junie by JetBrains**: JetBrains' own agent
- **Kiro CLI** (AWS): Amazon's AI coding CLI
- **Qwen Code** (Alibaba): Alibaba's coding agent
- **Docker cagent**: Docker's containerized agent
- **Kimi CLI**: Moonshot AI's coding agent
- **fast-agent**: Code and build agents with multi-provider support
- **crow-cli**: Minimal ACP native coding agent
- **OpenCode**: Open-source coding agent
- **Devin CLI** (Cognition): Devin coding agent

### Adapter-Based Agents

Agents that require bridge adapters to speak ACP: [VERIFIED] (ACP-SC-ACPORG-AGNTS, ACP-SC-MRCNR-INTRO)

- **Claude Agent** (Anthropic): Via Zed's SDK adapter. Anthropic has not natively adopted ACP.
- **Codex CLI** (OpenAI): Via Zed's adapter

### Full Agent Count

40+ agents listed on agentclientprotocol.com/get-started/agents as of 2026-08-30. [VERIFIED] (ACP-SC-ACPORG-AGNTS)

## Clients

### Editors and IDEs

- **Zed**: Reference implementation, most complete ACP support [VERIFIED] (ACP-SC-MRPH-EXPL)
- **JetBrains**: Native ACP support (Oct 2025 partnership with Zed) [VERIFIED] (ACP-SC-MRCNR-INTRO)
- **Neovim**: Via community plugins (CodeCompanion, agentic.nvim, avante.nvim, hermes.nvim)
- **Emacs**: Via agent-shell.el
- **VS Code**: Community extension only (vscode-acp), NO native support [VERIFIED] (ACP-SC-MRPH-EXPL)
- **Obsidian**: Via Agent Client plugin
- **Unity**: Two separate plugins
- **Kangaroo**: Database IDE with ACP support

### CLI and TUI

- acpx, Hash (shell), Hydra, Nori CLI, pool, Toad [VERIFIED] (ACP-SC-ACPORG-CLNTS)

### Desktop and Web

Major additions since June 2026: [VERIFIED] (ACP-SC-ACPORG-CLNTS)

- **Gold Band**: Open-source, local-first ACP desktop client (Windows, macOS, Linux)
- **Jockey**: Open-source multi-agent orchestrator (Tauri + Rust + SolidJS)
- **Kepler** (GitKraken): Agentic development environment
- **Kronos**: Scheduler and orchestration dashboard for ACP agent tasks
- **ACP Inspector**: Desktop debugger/inspector for ACP protocol
- **Newio**: Multi-channel, multi-player agent native messaging app
- Devin Desktop, Poolside Desktop, RLM Code, Shellular, and 15+ more

### Mobile Clients

- Agmente (iOS), Ferngeist (Android), Happy (iOS/Android/Web), Mobvibe (iOS/Android/Web), Shellular (iOS/Android/Web), VACP (Android, voice control) [VERIFIED] (ACP-SC-ACPORG-CLNTS)

### Messaging Platforms

Significant expansion since June 2026: [VERIFIED] (ACP-SC-ACPORG-CLNTS)

- **Discord**: ACP Discord bot
- **Slack**: duckdb-claude-slack, Juan, Pomerium AgentOps
- **Telegram**: Telegram ACP Bot, Telegram-ACP, ACP Router (rich diffs, approvals)
- **WeChat**: WeChat ACP
- **QQ**: qq-ai-bot (OneBot 11)
- **Lark**: Lark ACP
- **Matrix**: Zooid
- **OpenACP**: Self-hosted bridge for Telegram, Discord, Slack
- **Snipt**: Team repository integration

### Notebook and Data Tools

- agent-client-kernel (Jupyter), DuckDB extension, marimo notebook [VERIFIED] (ACP-SC-ACPORG-CLNTS)

### Frameworks

Framework integrations for existing AI pipelines: [VERIFIED] (ACP-SC-ACPORG-CLNTS)

- **LangChain / LangGraph**: Deep Agents ACP integration
- **Mastra**: `@mastra/acp` package
- **LlamaIndex**: workflows-acp adapter
- **Koog** (JetBrains): agents-features-acp integration
- **ACP Kit**: Adapter toolkit for Pydantic AI / LangChain runtimes
- **AgentPool**: Built-in ACP integration for IDEs
- **fast-agent**: Through `fast-agent-acp`
- **LLMling-Agent**: Built-in ACP support

### Connectors (New Category)

Bridges connecting ACP to other environments: [VERIFIED] (ACP-SC-ACPORG-CLNTS)

- **AgentRQ**: Human-in-the-loop task collaboration
- **ACP Components**: Universal frontend component library for AI Agent interfaces
- Various protocol bridges and adapters

## ACP Registry

The ACP Registry provides curated agent discovery with programmatic API: [VERIFIED] (ACP-SC-ACPORG-RGSTR)

```bash
curl https://cdn.agentclientprotocol.com/registry/v1/latest/registry.json
```

The registry JSON contains agent metadata including distribution information for automatic installation. Agents in the registry must support authentication.

## Quick Reference

- **Agents**: 40+ implementations (native and adapter-based)
- **Clients**: 50+ implementations across 8 categories
- **Reference client**: Zed
- **Reference adapter pattern**: claude-agent-acp, codex-acp (by Zed)
- **Registry API**: `https://cdn.agentclientprotocol.com/registry/v1/latest/registry.json`

## Limitations and Gotchas

- VS Code has NO native ACP support and likely will not get it (Microsoft invested in MCP)
- Claude Code and Codex CLI require Zed-maintained adapters, not official support from Anthropic/OpenAI
- Many community integrations are early-stage with varying quality
- Mobile and messaging clients are mostly community-driven
- The ecosystem list is fast-moving; check the official website for current status

## Sources

- ACP-SC-ACPORG-AGNTS - Official agents list
- ACP-SC-ACPORG-CLNTS - Official clients list
- ACP-SC-ACPORG-RGSTR - ACP Registry and programmatic API
- ACP-SC-MRCNR-INTRO - Ecosystem overview and adapter details
- ACP-SC-MRPH-EXPL - FAQ on editor support and agent compatibility

## Document History

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Updated: Agent count from 35+ to 40+ with new entries (Kimi CLI, fast-agent, crow-cli, OpenCode, Devin CLI)
- Updated: Client count from 20+ to 50+ across 8 categories (was 7)
- Added: Connectors as new client category
- Added: Many new desktop/web clients (Gold Band, Jockey, Kepler, Kronos, ACP Inspector, Newio)
- Added: Expanded messaging platform coverage (QQ, Lark, Matrix, OpenACP, ACP Router)
- Added: New mobile clients (VACP for voice control)
- Added: Registry programmatic API endpoint
- Added: New framework integrations (fast-agent, LLMling-Agent)

**[2026-06-12 10:10]**
- Initial document created
