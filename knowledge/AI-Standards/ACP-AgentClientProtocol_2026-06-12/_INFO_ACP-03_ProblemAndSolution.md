# ACP: Problem Statement and Solution Approach

**Doc ID**: ACP-IN03
**Goal**: Document why ACP exists and what problem it solves
**Version scope**: ACP Protocol v1 (as of 2026-06-12)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references
- `_INFO_ACP-01_Summary.md [ACP-IN01]` for topic context

## Overview

The Agent Client Protocol (ACP) was created to solve the N x M integration problem between code editors and AI coding agents. Before ACP, every editor needed a custom integration for every agent, creating fragmentation and vendor lock-in. ACP standardizes this communication layer using JSON-RPC 2.0, allowing any ACP-compatible agent to work in any ACP-compatible editor. [VERIFIED] (ACP-SC-ACPORG-INTRO)

## The Problem: Siloed Integrations

Before ACP, the AI coding agent landscape suffered from three core issues:

- **Integration overhead**: Every new agent-editor combination required custom development work. Adding a new agent to an existing editor, or supporting a new editor from an existing agent, meant building bespoke integrations from scratch. [VERIFIED] (ACP-SC-ACPORG-INTRO)

- **Limited compatibility**: Agents worked with only a subset of available editors. Users of niche or specialized editors were often excluded from using the best AI agents. [VERIFIED] (ACP-SC-ACPORG-INTRO)

- **Developer lock-in**: Choosing an agent often meant accepting their available interfaces. If a developer preferred a particular editor but the best agent only supported a different one, they faced an unpleasant tradeoff. [VERIFIED] (ACP-SC-ACPORG-INTRO)

The combinatorial explosion was the fundamental driver: with N editors and M agents, the ecosystem needed N x M custom integrations. Each integration reimplemented the same patterns - chat rendering, diff display, permission prompts, session management - independently and incompatibly. [VERIFIED] (ACP-SC-MRCNR-INTRO)

## The Solution: The LSP Analogy

ACP solves this the same way the Language Server Protocol (LSP) solved language tooling fragmentation. [VERIFIED] (ACP-SC-MRCNR-INTRO)

Before LSP, every editor needed its own TypeScript parser, Python linter, and Go formatter. After LSP, one language server worked everywhere. ACP applies the same pattern to AI agents:

- **One standard**: A single open JSON-RPC protocol that both editors and agents implement
- **N editors, M agents**: Instead of N x M bespoke integrations, each side implements the protocol once
- **Independent shipping**: Editors and agents evolve independently without breaking compatibility

As Zed framed it: "Just as the Language Server Protocol unbundled language intelligence from monolithic IDEs, the goal with the Agent Client Protocol is to enable you to switch between multiple agents without switching your editor." [VERIFIED] (ACP-SC-MRCNR-INTRO)

## ACP vs MCP vs A2A: Complementary Layers

Three protocols are commonly discussed in the AI agent ecosystem. They solve different problems at different layers and are designed to work together:

- **ACP (Agent Client Protocol)**: Editor-to-agent layer. How the editor drives the agent - rendering chat, diffs, permission prompts. "ACP gives the agent an editor." [VERIFIED] (ACP-SC-MRCNR-INTRO)

- **MCP (Model Context Protocol)**: Agent-to-tool layer. How the agent accesses external tools and data sources (databases, APIs, file systems). "MCP gives the agent tools." Created by Anthropic. [VERIFIED] (ACP-SC-MRCNR-INTRO)

- **A2A (Agent-to-Agent Protocol)**: Agent-to-agent layer. How autonomous agents communicate with each other for task delegation. Created by Google.

ACP and MCP are explicitly complementary: when an ACP session starts, the editor passes MCP server endpoints to the agent so it can use both protocols simultaneously. The agent is both an ACP server (receiving prompts from the editor) and an MCP client (calling tools). [VERIFIED] (ACP-SC-ACPORG-ARCH, ACP-SC-MRCNR-INTRO)

**Role reversal note**: The direction is subtly reversed between ACP and MCP. In MCP, the AI application is the "host/client" and tools are "servers." In ACP, the editor is the client and the AI agent is the subprocess. The terminology repeats but the roles flip. [VERIFIED] (ACP-SC-MRCNR-INTRO)

## ACP Disambiguation

Over the last two years, three different protocols have used the "ACP" acronym, and search results still mix them:

- **Agent Client Protocol**: The editor-to-agent protocol covered here (by Zed Industries)
- **Agent Communication Protocol**: An agent-to-agent interoperability protocol associated with IBM Research / BeeAI
- **Agentic Commerce Protocol**: A commerce protocol from OpenAI and Stripe for AI-driven checkout flows

[VERIFIED] (ACP-SC-MRCNR-INTRO)

## Design Goals

ACP's stated design goals reflect its LSP heritage:

- **Editor-agent portability**: Switch between Claude Code, Gemini CLI, Codex, or Goose without switching editors [VERIFIED] (ACP-SC-MRCNR-INTRO)
- **No vendor lock-in**: Adopting a new agent no longer forces an editor migration, and vice versa [VERIFIED] (ACP-SC-MRCNR-INTRO)
- **Shared UX surface**: Chat, diffs, and permission prompts live in the editor instead of being reimplemented per agent [VERIFIED] (ACP-SC-MRCNR-INTRO)
- **Open and multi-vendor**: Zed, JetBrains, and Google ship against the spec directly; Claude Code and Codex CLI plug in via adapters [VERIFIED] (ACP-SC-MRCNR-INTRO)
- **MCP-friendly**: Natural fit with MCP - ACP handles editor-to-agent, MCP handles agent-to-tool [VERIFIED] (ACP-SC-ACPORG-ARCH)

## Quick Reference

- **Created by**: Zed Industries (August 2025)
- **Protocol**: JSON-RPC 2.0 over stdio (primary), Streamable HTTP (roadmap)
- **License**: Apache 2.0
- **Current stable version**: Protocol v1
- **Spec repository**: github.com/agentclientprotocol/agent-client-protocol
- **Website**: agentclientprotocol.com

## Limitations and Gotchas

- ACP is NOT by Anthropic - a common misconception. Anthropic created MCP; Zed Industries created ACP
- The "ACP" acronym is overloaded - always verify which "ACP" a source refers to
- ACP is specifically for code editors and coding agents, not general-purpose agent orchestration
- The LSP analogy is useful but imperfect: ACP handles much more state (sessions, permissions, streaming) than LSP's stateless request-response model

## Sources

- ACP-SC-ACPORG-INTRO - Official ACP introduction (agentclientprotocol.com)
- ACP-SC-ACPORG-ARCH - Official ACP architecture page
- ACP-SC-MRCNR-INTRO - Marc Nuri blog: comprehensive ACP introduction with timeline and ecosystem analysis
- ACP-SC-MRPH-EXPL - Morph LLM: ACP explained with FAQ and implementation details

## Document History

**[2026-06-12 09:50]**
- Initial document created
