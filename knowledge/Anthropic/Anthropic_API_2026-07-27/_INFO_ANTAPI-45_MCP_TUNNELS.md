# MCP Tunnels

**Doc ID**: ANTAPI-IN45
**Goal**: Document MCP tunnels for connecting Claude to private MCP servers
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-40_MANAGED_AGENTS.md [ANTAPI-IN40]` for Managed Agents context
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` for beta header usage

## Summary

MCP tunnels (research preview) allow Claude Managed Agents to connect to MCP (Model Context Protocol) servers running on private networks. This enables agents to access internal tools, databases, and services that are not publicly accessible. Tunnels create a secure connection between the managed agent's cloud container and your private infrastructure. As of June 22, 2026, the tunnels endpoint moved from Admin API (`/v1/organizations/tunnels`) to Claude API (`/v1/tunnels`). Requires the `mcp-tunnels-2026-06-22` beta header and separate research preview access.

## Key Facts

- **Beta Header**: `mcp-tunnels-2026-06-22` (was `mcp-tunnels-2026-05-01`)
- **Endpoint**: `POST /v1/tunnels` (moved from `/v1/organizations/tunnels` on Jun 22)
- **Access**: Research preview (requires separate access request)
- **Purpose**: Connect managed agents to private MCP servers
- **Security**: Secure tunnel between cloud container and private network
- **Prerequisite**: Claude Managed Agents
- **Status**: Research Preview

## Use Cases

- Connect agents to internal databases via MCP
- Access private APIs and tools from managed agent sessions
- Enterprise workflows requiring access to on-premise systems
- Compliance scenarios where tools must run inside private networks

## Limitations

- Research preview; may change significantly
- Requires separate access request via form
- Only available with Claude Managed Agents
- Not eligible for ZDR or HIPAA BAA (same as Managed Agents)

## Gotchas and Quirks

- MCP tunnels require both the MCP tunnels beta header and Managed Agents beta header
- Endpoint moved from Admin API to Claude API on Jun 22; old path returns 404
- Old header `mcp-tunnels-2026-05-01` no longer works; use `mcp-tunnels-2026-06-22`
- Tunnel setup adds latency to initial connection
- Private MCP servers must implement the standard MCP protocol

## Related Endpoints

- `_INFO_ANTAPI-40_MANAGED_AGENTS.md [ANTAPI-IN40]` - Managed Agents (required for tunnels)
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` - Beta header configuration

## Sources

- ANTAPI-SC-ANTH-MCPTNL - https://platform.claude.com/docs/en/managed-agents/mcp-tunnels - MCP tunnels documentation
- ANTAPI-SC-ANTH-RLNTS - https://platform.claude.com/docs/en/about-claude/release-notes - Release notes (May 19, 2026)

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Endpoint moved from /v1/organizations/tunnels to /v1/tunnels
- Changed: Beta header updated to mcp-tunnels-2026-06-22

**[2026-05-22]**
- Initial documentation created from release notes and MCP tunnels references
