# ACP: Gotchas, Limitations, and Best Practices

**Doc ID**: ACP-IN14
**Goal**: Document known limitations, common pitfalls, and production recommendations
**Version scope**: ACP Protocol v1 (stable) + v2 (draft, as of 2026-08-30)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP is a rapidly maturing protocol with strong adoption but several important limitations. This document consolidates cross-cutting concerns into actionable guidance for agent and client developers. Updated with v2 migration considerations and new v1 features. [SYNTHESIZED from all sources]

## Known Limitations

### No Native VS Code Support

Microsoft chose MCP for VS Code's agent mode. A community extension (vscode-acp) provides partial support, but there is no official integration. This is the single largest gap in ACP's client coverage given VS Code's market dominance. [VERIFIED] (ACP-SC-MRPH-EXPL)

**Recommendation**: If your user base is primarily VS Code, ACP alone is insufficient. Consider supporting both ACP and direct VS Code extension integration.

### stdio-Only Transport (Practical)

While the spec describes Streamable HTTP and the Python SDK (v0.12.0+) has an early HTTP/WS implementation, stdio remains the only widely adopted transport. This limits ACP to local subprocess scenarios. [VERIFIED] (ACP-SC-ACPORG-TRNSP, ACP-SC-GH-PYSD)

**Recommendation**: Design agents to work over stdio first. Monitor the Transports Working Group progress and Python SDK HTTP transport maturity before investing in remote solutions.

### Adapter Tax for Major Agents

Claude Code and Codex CLI require Zed-maintained adapter bridges rather than native ACP support. [VERIFIED] (ACP-SC-MRCNR-INTRO, ACP-SC-MRPH-EXPL)

**Recommendation**: Prefer agents with native ACP support (Gemini CLI, Goose, Cline, Cursor) when adapter reliability is a concern.

### v2 Breaking Changes Ahead

The v2 draft (July 2026) removes the client fs/terminal surface, restructures capabilities, and redesigns the prompt lifecycle. While still in draft, implementations should plan for migration. [VERIFIED] (ACP-SC-ACPORG-V2DFT)

**Recommendation**: Avoid deep investment in features marked for removal in v2 (session modes, client fs/terminal methods). Use Session Config Options instead of session modes. Gate v2 support behind version negotiation AND feature flags until stabilization.

## Common Pitfalls

### ACP Acronym Confusion

Three different protocols use "ACP": Agent Client Protocol (Zed), Agent Communication Protocol (IBM/BeeAI), and Agentic Commerce Protocol (OpenAI/Stripe). [VERIFIED] (ACP-SC-MRCNR-INTRO)

**Recommendation**: Always verify the source domain (agentclientprotocol.com).

### Misattribution to Anthropic

ACP is frequently attributed to Anthropic. Anthropic created MCP, not ACP. ACP was created by Zed Industries. [VERIFIED from research]

### Permission Model is Informational, Not Enforcement

The `kind` field on tool calls is for UI categorization only. It does not enforce any security policy. [VERIFIED] (ACP-SC-ACPORG-TLCLL)

**Recommendation**: Do not rely on `kind` for security decisions. `session/request_permission` is the actual control point.

### Cancellation Race Conditions

`session/cancel` is a notification with no confirmation. The agent may send additional `session/update` notifications after cancellation. [VERIFIED] (ACP-SC-ACPORG-PRMPT)

**Recommendation**: After sending `session/cancel`, continue processing incoming notifications until the `session/prompt` response arrives with `stopReason: "cancelled"`. For general-purpose cancellation, `$/cancel_request` is also available. [VERIFIED] (ACP-SC-ANN-RQCNL)

### Additional Directories Not Persistent

`additionalDirectories` in session setup are not preserved across reconnections. Clients must re-send on every `session/load` and `session/resume`. [VERIFIED] (ACP-SC-ACPORG-SSSTP)

### Rejecting Baseline Content Blocks Breaks File Mentions

`text` and `resource_link` are a MANDATORY baseline - every agent must accept them in `session/prompt` regardless of declared `promptCapabilities`. Clients (e.g., Zed) send `resource_link` blocks for @-mentioned files; an agent that rejects them fails on most real-world prompts. Only `image`, `audio`, and `resource` (embedded context) are capability-gated. [VERIFIED] (ACP-SC-ACPORG-INIT)

### Embedded Newlines Forbidden on stdio

JSON-RPC messages on stdio are newline-delimited. Multi-line content must be JSON-escaped. [VERIFIED] (ACP-SC-ACPORG-TRNSP)

### v1/v2 Dual Version Support

Supporting both protocol versions simultaneously is recommended but adds complexity. Use version negotiation per connection and keep shared application logic behind thin protocol surfaces. [VERIFIED] (ACP-SC-ACPORG-V2MIG)

**Recommendation**: Treat v2 as additive. Keep v1 support when adding v2. v1-only peers will remain common for some time.

## Security Concerns

### Trusted Agent Model

ACP assumes the agent is a trusted local subprocess. No sandboxing or agent identity verification. [VERIFIED] (ACP-SC-ACPORG-ARCH)

**Recommendation**: Only run agents you trust. For untrusted/remote agents, add application-level security outside the ACP layer.

### MCP Credential Exposure

MCP server credentials are passed in cleartext via env variables or HTTP headers at session creation. [VERIFIED] (ACP-SC-ACPORG-SSSTP)

**Recommendation**: Use short-lived tokens. Avoid passing long-lived secrets through ACP session setup.

### No Audit Trail

ACP does not define logging or audit trail requirements. [SYNTHESIZED from protocol review]

**Recommendation**: Implement application-level logging for all agent actions, especially in enterprise deployments.

## Best Practices

### For Agent Developers

- **Implement capabilities incrementally**: Start with baseline methods, add optional features based on client demand
- **Use `session/update` liberally**: Stream progress early and often
- **Request permission for destructive actions**: Always use `session/request_permission` for file writes and command execution
- **Support the `--acp` flag convention**: Most clients expect `--acp` to enable ACP mode
- **Handle `session/cancel` gracefully**: Stop work, clean up, return `stopReason: "cancelled"`
- **Declare capabilities accurately**: Only advertise capabilities you fully implement
- **Implement `messageId`**: Optional in v1 but required in v2. Adding it now eases migration.
- **Support elicitation**: Use `elicitation/create` for structured user input instead of unstructured prompts [VERIFIED] (ACP-SC-ANN-ELCTN)

### For Client Developers

- **Negotiate capabilities**: Always check agent capabilities before using optional features
- **Handle streaming interruptions**: Implement timeout and reconnection logic
- **Present permission requests clearly**: Include tool kind, title, and affected files
- **Support the ACP Registry**: Use registry metadata for agent discovery
- **Track `messageId`**: Correlate message chunks correctly
- **Advertise elicitation modes**: Declare `elicitation.form` and/or `elicitation.url` if supported

### For Production Deployments

- **Pin SDK versions**: SDK artifact versions change independently of protocol version
- **Monitor `usage_update`**: Track token consumption and costs per session [VERIFIED] (ACP-SC-ANN-USAGE)
- **Implement session persistence**: Use `session/load`/`session/resume` for long-running workflows
- **Plan for v2 migration**: Audit use of deprecated features (session modes, client fs/terminal)
- **Support dual versions**: Keep v1 working while adding v2 behind feature flags

## Quick Reference

- **Biggest gap**: No native VS Code support
- **Biggest confusion**: ACP acronym (3 protocols) and Anthropic misattribution
- **Security model**: Trusted subprocess + per-action permissions
- **Migration risk**: v2 removes session modes and client fs/terminal surface
- **CLI convention**: `--acp` flag to enable ACP mode
- **v2 status**: Draft (July 2026), not yet stabilized

## Sources

- ACP-SC-MRPH-EXPL - FAQ, VS Code status, Claude Code adapter details
- ACP-SC-MRCNR-INTRO - Acronym disambiguation, ecosystem analysis
- ACP-SC-ACPORG-V2DFT - v2 draft announcement
- ACP-SC-ACPORG-V2MIG - v2 migration guide, dual version support
- ACP-SC-ACPORG-TLCLL - Permission model details
- ACP-SC-ACPORG-PRMPT - Cancellation behavior
- ACP-SC-ACPORG-SSSTP - Session setup, additional directories, MCP credentials
- ACP-SC-ACPORG-TRNSP - Transport limitations
- ACP-SC-ACPORG-ARCH - Trust model and design philosophy
- ACP-SC-ANN-RQCNL - $/cancel_request as alternative cancellation
- ACP-SC-ANN-ELCTN - Elicitation best practices
- ACP-SC-ANN-USAGE - usage_update for cost tracking
- ACP-SC-GH-PYSD - Python SDK HTTP transport progress

## Document History

**[2026-08-30 14:20]**
- Added: baseline content block pitfall (mandatory text + resource_link acceptance) from live-doc verification

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: v1/v2 dual version support as new pitfall
- Added: Elicitation best practices for agents and clients
- Added: messageId implementation recommendation
- Added: usage_update monitoring for production
- Added: $/cancel_request as alternative cancellation mechanism
- Added: Python SDK HTTP transport reference in transport limitation
- Updated: v2 status from "proposal" to "draft (July 2026)"

**[2026-06-12 10:18]**
- Initial document created
