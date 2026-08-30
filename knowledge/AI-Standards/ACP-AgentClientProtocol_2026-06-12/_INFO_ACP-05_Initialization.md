# ACP: Initialization

**Doc ID**: ACP-IN05
**Goal**: Document the ACP initialization phase including version negotiation and capabilities
**Version scope**: ACP Protocol v1 (as of 2026-06-12)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

Every ACP connection begins with an `initialize` request from the client to the agent. This exchange negotiates the protocol version, declares capabilities on both sides, optionally advertises authentication methods, and provides implementation metadata. No other messages may be sent before initialization completes. [VERIFIED] (ACP-SC-ACPORG-INIT, ACP-SC-ACPORG-OVRVW)

## Protocol Version

ACP uses a single integer version number that only increments for breaking wire-protocol changes. The current stable protocol version is **1**. [VERIFIED] (ACP-SC-ACPORG-INIT, ACP-SC-GH-REPO)

### Version Negotiation

The client sends its supported `protocolVersion` in the `initialize` request. The agent responds with its own `protocolVersion`. If the versions are incompatible, the connection should be terminated.

Wire compatibility is determined by the negotiated `protocolVersion`, NOT by crate or schema package versions. Within a protocol version, use the exchanged capabilities to decide which optional features are supported. [VERIFIED] (ACP-SC-GH-REPO)

```json
// Client sends:
{
  "jsonrpc": "2.0",
  "id": 0,
  "method": "initialize",
  "params": {
    "protocolVersion": 1,
    "clientCapabilities": { ... }
  }
}

// Agent responds:
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocolVersion": 1,
    "agentCapabilities": { ... }
  }
}
```

## Client Capabilities

The client declares what features it supports for the agent to use: [VERIFIED] (ACP-SC-ACPORG-INIT)

### File System

- `fs.readTextFile`: Client supports `fs/read_text_file` method (agent can read files)
- `fs.writeTextFile`: Client supports `fs/write_text_file` method (agent can write files)

### Terminal

- `terminal`: Client supports `terminal/*` methods (agent can create and manage terminal sessions)

## Agent Capabilities

The agent declares what features it supports: [VERIFIED] (ACP-SC-ACPORG-INIT)

### Session Capabilities

- `loadSession`: Agent supports `session/load` for resuming existing sessions
- `sessionCapabilities.resume`: Agent supports `session/resume`
- `sessionCapabilities.close`: Agent supports `session/close`
- `sessionCapabilities.delete`: Agent supports `session/delete` (returns `null` or `{}`)
- `sessionCapabilities.list`: Agent supports `session/list`
- `sessionCapabilities.additionalDirectories`: Agent supports additional workspace roots

### Prompt Capabilities

The agent declares which content types it accepts in `session/prompt`:
- `ContentBlock::Text` and `ContentBlock::ResourceLink` are always supported (baseline)
- `image`: Agent accepts `ContentBlock::Image`
- `audio`: Agent accepts `ContentBlock::Audio`
- `embeddedContext`: Agent accepts `ContentBlock::Resource`

### Model Context Protocol (MCP) Capabilities

- `mcpCapabilities.http`: Agent supports HTTP-based MCP server transport
- `mcpCapabilities.sse`: Agent supports SSE-based MCP server transport
- stdio MCP transport is assumed by default

### Authentication Capabilities

- `auth.logout`: Agent supports the `logout` method

## Authentication Methods

Agents can advertise available authentication methods in the `initialize` response via the `authMethods` array: [VERIFIED] (ACP-SC-ACPORG-AUTH)

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocolVersion": 1,
    "agentCapabilities": {
      "auth": { "logout": {} }
    },
    "authMethods": [
      {
        "id": "agent-login",
        "name": "Agent login",
        "description": "Sign in using the agent's login flow"
      }
    ]
  }
}
```

## Implementation Information

Agents and clients can optionally exchange implementation metadata during initialization: name, version, and other identifying information. This enables better diagnostics and compatibility handling. [VERIFIED] (ACP-SC-ACPORG-INIT)

## Quick Reference

- **Method**: `initialize` (client to agent)
- **Required fields**: `protocolVersion`, `clientCapabilities` / `agentCapabilities`
- **Optional fields**: `authMethods`, implementation info
- **Current protocol version**: 1 (integer, only increments for breaking changes)
- **Must complete before**: Any other ACP messages

## SDK Examples

### Python

```python
# Using the official Python SDK, initialization is handled automatically
import asyncio
from acp import Agent, Session

class MyAgent(Agent):
    # Capabilities are declared via class attributes or constructor
    async def on_prompt(self, session: Session, prompt: str) -> str:
        await session.stream_text("Processing...")
        return "done"

# The SDK handles initialize handshake internally
asyncio.run(MyAgent().run_stdio())
```

### TypeScript

```typescript
import { createAcpAgent } from "@agentclientprotocol/sdk";

// Capabilities are declared in the agent configuration
const agent = createAcpAgent({
  name: "my-agent",
  version: "1.0.0",
  // SDK handles initialize handshake automatically
  onPrompt: async (session, prompt) => {
    await session.streamText("Processing...");
    return "done";
  },
});

agent.run(); // starts stdio loop, handles initialize
```

## Limitations and Gotchas

- Non-breaking additions happen through capability negotiation, NOT protocol version bumps. Always check capabilities, not just the version number.
- The `authMethods` array is optional. If omitted, the agent does not require authentication.
- `agentCapabilities.auth.logout` being `null` means the agent does not support logout even if it advertises auth methods.
- v2 proposes merging `clientCapabilities` and `agentCapabilities` into a single `capabilities` field with restructured naming.

## Sources

- ACP-SC-ACPORG-INIT - Official initialization page
- ACP-SC-ACPORG-OVRVW - Protocol overview (baseline methods)
- ACP-SC-ACPORG-AUTH - Authentication advertising during initialization
- ACP-SC-GH-REPO - Versioning model explanation

## Document History

**[2026-06-12 09:55]**
- Initial document created
