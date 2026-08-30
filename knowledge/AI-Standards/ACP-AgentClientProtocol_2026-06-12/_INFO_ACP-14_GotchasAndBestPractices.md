# ACP: Gotchas, Limitations, and Best Practices

**Doc ID**: ACP-IN14
**Goal**: Document known limitations, common pitfalls, and production recommendations
**Version scope**: ACP Protocol v1 (as of 2026-06-12)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP is a rapidly maturing protocol with strong adoption but several important limitations and gotchas that implementers should be aware of. This document consolidates cross-cutting concerns from all other topic files into actionable guidance for both agent and client developers. [SYNTHESIZED from all sources]

## Known Limitations

### No Native VS Code Support

Microsoft chose Model Context Protocol (MCP) for VS Code's agent mode and has not adopted ACP. A community extension (vscode-acp) provides partial support, but there is no official integration. An open GitHub issue (#265496) tracks the request. This is the single largest gap in ACP's client coverage given VS Code's market dominance. [VERIFIED] (ACP-SC-MRPH-EXPL)

**Recommendation**: If your user base is primarily VS Code, ACP alone is insufficient. Consider supporting both ACP and direct VS Code extension integration.

### stdio-Only Transport (Practical)

While the spec describes Streamable HTTP, stdio remains the only widely implemented transport. This limits ACP to local subprocess scenarios and prevents remote agent hosting without tunneling. [VERIFIED] (ACP-SC-ACPORG-TRNSP)

**Recommendation**: Design agents to work over stdio first. The Transports Working Group is actively developing HTTP transport; monitor their progress before investing in custom remote solutions.

### Adapter Tax for Major Agents

Claude Code and Codex CLI require Zed-maintained adapter bridges rather than native ACP support. Adapters may lag behind protocol updates and introduce additional failure modes. [VERIFIED] (ACP-SC-MRCNR-INTRO, ACP-SC-MRPH-EXPL)

**Recommendation**: Prefer agents with native ACP support (Gemini CLI, Goose, Cline) when adapter reliability is a concern.

### v2 Breaking Changes Ahead

The v2 proposal removes the client fs/terminal surface, session modes API, and restructures capabilities. Implementations built on v1-specific features will need migration. [VERIFIED] (ACP-SC-ACPORG-V2)

**Recommendation**: Avoid deep investment in features marked for removal in v2 (session modes, client fs/terminal methods). Use Session Config Options instead of session modes. Watch the RFD process for stabilization dates.

## Common Pitfalls

### ACP Acronym Confusion

Three different protocols use "ACP": Agent Client Protocol (this one, by Zed), Agent Communication Protocol (IBM/BeeAI), and Agentic Commerce Protocol (OpenAI/Stripe). Search results and LLM responses frequently confuse them. [VERIFIED] (ACP-SC-MRCNR-INTRO)

**Recommendation**: Always verify the source. The canonical Agent Client Protocol references agentclientprotocol.com and github.com/agentclientprotocol.

### Misattribution to Anthropic

ACP is frequently attributed to Anthropic in search results and AI-generated content. Anthropic created MCP, not ACP. ACP was created by Zed Industries. Anthropic's Claude Code participates only via an adapter maintained by Zed. [VERIFIED from research - multiple sources corrected this assumption]

### Permission Model is Informational, Not Enforcement

The `kind` field on tool calls (read, edit, delete, etc.) is for UI categorization only. It does not enforce any security policy. An agent declaring `kind: "read"` could still perform destructive operations if the underlying tool allows it. [VERIFIED] (ACP-SC-ACPORG-TLCLL)

**Recommendation**: Do not rely on `kind` for security decisions. The permission system (`session/request_permission`) is the actual control point.

### Cancellation Race Conditions

`session/cancel` is a notification with no confirmation. The agent may send additional `session/update` notifications after cancellation. Clients must handle this gracefully. [VERIFIED] (ACP-SC-ACPORG-PRMPT)

**Recommendation**: After sending `session/cancel`, continue processing incoming notifications until the `session/prompt` response arrives with `stopReason: "cancelled"`.

### Additional Directories Not Persistent

`additionalDirectories` in session setup are not preserved across reconnections. Clients must re-send the full intended root list on every `session/load` and `session/resume`. [VERIFIED] (ACP-SC-ACPORG-SSSTP)

### Embedded Newlines Forbidden on stdio

JSON-RPC messages on stdio are newline-delimited. Multi-line content must be JSON-escaped (e.g., `\n` within strings). A single newline in a raw message breaks the framing. [VERIFIED] (ACP-SC-ACPORG-TRNSP)

## Security Concerns

### Trusted Agent Model

ACP assumes the agent is a trusted local subprocess. The protocol has no mechanisms for sandboxing untrusted agents, verifying agent identity, or limiting agent capabilities beyond the permission system. [VERIFIED] (ACP-SC-ACPORG-ARCH)

**Recommendation**: Only run agents you trust. For untrusted or remote agents, add application-level security (container isolation, network policies) outside the ACP layer.

### MCP Credential Exposure

MCP server credentials (API keys, tokens) are passed in cleartext via `env` variables or HTTP headers at session creation. The agent receives these credentials to connect to MCP servers. [VERIFIED] (ACP-SC-ACPORG-SSSTP)

**Recommendation**: Use short-lived tokens where possible. Avoid passing long-lived secrets through ACP session setup.

### No Audit Trail

ACP does not define logging or audit trail requirements. Actions taken by the agent (file writes, command execution) are not centrally recorded by the protocol. [SYNTHESIZED from protocol review]

**Recommendation**: Implement application-level logging for all agent actions, especially in enterprise deployments.

## Best Practices

### For Agent Developers

- **Implement capabilities incrementally**: Start with baseline methods (`initialize`, `session/new`, `session/prompt`), then add optional features based on client demand
- **Use `session/update` liberally**: Stream progress early and often. Users prefer visible activity over long silences.
- **Request permission for destructive actions**: Even if the client might auto-approve, always use `session/request_permission` for file writes and command execution
- **Support the `--acp` flag convention**: Most clients expect agents to enable ACP mode via a `--acp` CLI flag
- **Handle `session/cancel` gracefully**: Stop work as soon as possible, clean up partial state, and return `stopReason: "cancelled"`
- **Declare capabilities accurately**: Only advertise capabilities you fully implement. Partial support causes silent failures.

### For Client Developers

- **Negotiate capabilities**: Always check the agent's declared capabilities before using optional features. Never assume fs/terminal support.
- **Handle streaming interruptions**: The agent may disconnect mid-stream. Implement timeout and reconnection logic.
- **Present permission requests clearly**: Users need enough context (tool kind, title, affected files) to make informed allow/reject decisions
- **Support the ACP Registry**: Use registry metadata for agent discovery and installation
- **Track `messageId`**: Correlate message chunks correctly, especially when multiple messages overlap

### For Production Deployments

- **Pin SDK versions**: SDK artifact versions change independently of protocol version. Use lockfiles.
- **Monitor `usage_update`**: Track token consumption and costs per session for budgeting
- **Implement session persistence**: Use `session/load`/`session/resume` for long-running workflows
- **Plan for v2 migration**: Audit your use of deprecated features (session modes, client fs/terminal)

## Quick Reference

- **Biggest gap**: No native VS Code support
- **Biggest confusion**: ACP acronym (3 protocols) and Anthropic misattribution
- **Security model**: Trusted subprocess + per-action permissions
- **Migration risk**: v2 removes session modes and client fs/terminal surface
- **CLI convention**: `--acp` flag to enable ACP mode

## Sources

- ACP-SC-MRPH-EXPL - FAQ, VS Code status, Claude Code adapter details
- ACP-SC-MRCNR-INTRO - Acronym disambiguation, ecosystem analysis
- ACP-SC-ACPORG-V2 - v2 breaking changes
- ACP-SC-ACPORG-TLCLL - Permission model details
- ACP-SC-ACPORG-PRMPT - Cancellation behavior
- ACP-SC-ACPORG-SSSTP - Session setup, additional directories, MCP credentials
- ACP-SC-ACPORG-TRNSP - Transport limitations
- ACP-SC-ACPORG-ARCH - Trust model and design philosophy

## Document History

**[2026-06-12 10:18]**
- Initial document created
