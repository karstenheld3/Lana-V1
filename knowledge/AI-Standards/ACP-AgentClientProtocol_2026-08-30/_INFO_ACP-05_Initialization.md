# ACP: Initialization

**Doc ID**: ACP-IN05
**Goal**: Document the ACP initialization handshake, capability negotiation, and version exchange
**Version scope**: ACP Protocol v1 (stable) + v2 changes noted

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

The initialization phase establishes the connection between client and agent by negotiating the protocol version and exchanging capabilities. The client sends `initialize` with its supported version and capabilities; the agent responds with its own. Once the client confirms with `initialized`, the handshake is complete and session operations can begin. [VERIFIED] (ACP-SC-ACPORG-INIT)

## Initialization Handshake

### Step 1: Client sends `initialize`

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "method": "initialize",
  "params": {
    "protocolVersion": 1,
    "clientInfo": {
      "name": "Zed",
      "version": "0.175.0"
    },
    "clientCapabilities": {
      "fs": {
        "readTextFile": {},
        "writeTextFile": {}
      },
      "terminal": {},
      "elicitation": {
        "form": {},
        "url": {}
      }
    }
  }
}
```

### Step 2: Agent responds

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocolVersion": 1,
    "agentInfo": {
      "name": "my-agent",
      "version": "1.0.0"
    },
    "agentCapabilities": {
      "loadSession": true,
      "promptCapabilities": {
        "image": true,
        "audio": false,
        "embeddedContext": true
      },
      "mcpCapabilities": {
        "http": true,
        "sse": false
      },
      "sessionCapabilities": {
        "resume": {},
        "close": {},
        "delete": {},
        "list": {},
        "configOptions": {
          "boolean": {}
        }
      },
      "auth": {
        "logout": {}
      }
    },
    "authMethods": [
      {
        "id": "agent-login",
        "name": "Sign in",
        "description": "Sign in using browser-based OAuth"
      }
    ]
  }
}
```

### Step 3: Client sends `initialized` notification

```json
{
  "jsonrpc": "2.0",
  "method": "initialized",
  "params": {}
}
```

[VERIFIED] (ACP-SC-ACPORG-INIT)

## Client Capabilities

All client capabilities are optional. The agent must check for their presence before using client methods: [VERIFIED] (ACP-SC-ACPORG-INIT)

- **`fs.readTextFile`**: Client supports `fs/read_text_file` requests
- **`fs.writeTextFile`**: Client supports `fs/write_text_file` requests
- **`terminal`**: Client supports terminal lifecycle methods (`terminal/create`, etc.)
- **`elicitation.form`**: Client supports structured form-based elicitation [VERIFIED] (ACP-SC-ANN-ELCTN)
- **`elicitation.url`**: Client supports URL-based elicitation (redirect to external page) [VERIFIED] (ACP-SC-ANN-ELCTN)

## Agent Capabilities

- **`loadSession`** (top-level boolean): Agent supports `session/load`. NOTE: intentionally NOT inside `sessionCapabilities` - the official schema keeps it top-level ("will be unified in future versions") [VERIFIED] (ACP-SC-ACPORG-INIT)
- **`promptCapabilities`**: Object gating OPTIONAL prompt content types [VERIFIED] (ACP-SC-ACPORG-INIT):
  - Baseline (not declared, always mandatory): all agents MUST accept `ContentBlock::Text` and `ContentBlock::ResourceLink` in `session/prompt`
  - `image`: Agent accepts `ContentBlock::Image`
  - `audio`: Agent accepts `ContentBlock::Audio`
  - `embeddedContext`: Agent accepts `ContentBlock::Resource`
- **`mcpCapabilities`**: MCP server transports the agent can connect to (`http`, `sse`); stdio transport is assumed by default [VERIFIED] (ACP-SC-ACPORG-INIT)
- **`sessionCapabilities`**: Optional session method markers - `resume`, `close`, `delete`, `list`, `additionalDirectories`, `configOptions` (omitted or `null` = unsupported; `{}` = supported) [VERIFIED] (ACP-SC-ACPORG-INIT)
- **`sessionCapabilities.configOptions.boolean`**: Agent supports boolean session config options [VERIFIED] (ACP-SC-ANN-BOOLC)
- **`auth.logout`**: Agent supports explicit logout

Baseline agent methods requiring no capability: `session/new`, `session/prompt`, `session/cancel`, `session/update` [VERIFIED] (ACP-SC-ACPORG-SCHM)

## Version Negotiation

The client sends the latest `protocolVersion` it supports. The agent responds with the same version if supported, or its own latest version otherwise. [VERIFIED] (ACP-SC-ACPORG-INIT)

- v1 client to v1 agent: Both send `protocolVersion: 1`. Normal operation.
- v2 client to v1 agent: Client sends `2`, agent responds `1`. Client decides to continue with v1 or disconnect.
- v2 client to v2 agent: Both negotiate `protocolVersion: 2`. v2 surfaces apply.

## Implementation Information

Optional `clientInfo` and `agentInfo` objects allow exchanging implementation metadata: [VERIFIED] (ACP-SC-ACPORG-UPDTS)

```json
{
  "clientInfo": {
    "name": "Zed",
    "version": "0.175.0"
  }
}
```

## v2 Initialization Changes (Draft)

Key changes in v2: [VERIFIED] (ACP-SC-ACPORG-V2MIG)

- `clientInfo`/`agentInfo` replaced by role-agnostic `info` field
- `clientCapabilities`/`agentCapabilities` replaced by single `capabilities` field
- Support markers become objects (`{}`) instead of booleans (`true`)
- `session` capability becomes optional (for non-session agents)
- `fs` and `terminal` capabilities removed
- `elicitation` modes explicitly advertised

### Python: Initialization Example

```python
import asyncio
from acp import Agent, Session

class MyAgent(Agent):
    """Minimal ACP agent with capability declaration."""

    @property
    def capabilities(self):
        return {
            "loadSession": True,
            "promptCapabilities": {"image": False, "audio": False, "embeddedContext": False},
            "sessionCapabilities": {"resume": {}, "close": {}},
        }

    async def on_prompt(self, session: Session, prompt: str) -> str:
        await session.stream_text(f"Echo: {prompt}")
        return "done"

if __name__ == "__main__":
    asyncio.run(MyAgent().run_stdio())
```

[VERIFIED] (ACP-SC-MRPH-EXPL, ACP-SC-GH-PYSD) - Simplified from SDK examples; verify exact API against `agent-client-protocol` v0.12.1 docs.

## Quick Reference

- **Handshake**: `initialize` (request) -> response -> `initialized` (notification)
- **Version**: `protocolVersion: 1` (v1 stable), `protocolVersion: 2` (v2 draft)
- **Client capabilities**: fs, terminal, elicitation (all optional)
- **Agent capabilities**: loadSession, promptCapabilities, mcpCapabilities, sessionCapabilities, auth
- **Prompt baseline**: text + resource_link always accepted; image/audio/embeddedContext capability-gated
- **Implementation info**: `clientInfo`/`agentInfo` with name and version

## Limitations and Gotchas

- The agent MUST NOT send any messages before receiving `initialize`
- The client MUST NOT send any session methods before `initialized` completes
- Capability negotiation is all-or-nothing per feature; there is no partial support negotiation
- `promptCapabilities` gates only the OPTIONAL content types; `text` and `resource_link` are a mandatory baseline every agent must accept - rejecting a `resource_link` block breaks clients that send file mentions
- The client decides what to send regardless of declared capabilities - agents should reject undeclared optional types defensively
- v2 changes `clientInfo`/`agentInfo` to a single `info` field - implementations must handle both versions if supporting v1 and v2

## TypeScript Examples

### Agent with Capability Declaration

```typescript
import { createAcpAgent } from "@agentclientprotocol/sdk";

const agent = createAcpAgent({
  name: "my-agent",
  version: "1.0.0",
  capabilities: {
    loadSession: true,
    promptCapabilities: { image: true, audio: false, embeddedContext: false },
    sessionCapabilities: { resume: {}, close: {} },
  },
  onPrompt: async (session, prompt) => {
    await session.streamText(`Echo: ${prompt}`);
    return "done";
  },
});

agent.run(); // starts stdio transport
```

[VERIFIED] (ACP-SC-MRPH-EXPL, ACP-SC-TSSD-DOCS) - Simplified from SDK examples; verify exact API against `@agentclientprotocol/sdk` v1.4.0 docs.

### v2 Experimental Import

```typescript
// v2 requires explicit experimental import
import * as acp from "@agentclientprotocol/sdk/experimental/v2";

// v2 uses role-agnostic 'info' and unified 'capabilities'
```

[VERIFIED] (ACP-SC-TSSD-DOCS)

## Sources

- ACP-SC-ACPORG-INIT - Official initialization documentation
- ACP-SC-ACPORG-SCHM - Official v1 schema reference (https://agentclientprotocol.com/protocol/v1/schema) - AgentCapabilities default, baseline methods
- ACP-SC-ACPORG-UPDTS - Implementation information stabilization
- ACP-SC-ACPORG-V2MIG - v2 initialization changes
- ACP-SC-ANN-ELCTN - Elicitation capability advertising
- ACP-SC-ANN-BOOLC - Boolean config options capability
- ACP-SC-MRPH-EXPL - Python and TypeScript SDK examples
- ACP-SC-GH-PYSD - Python SDK repository and examples
- ACP-SC-TSSD-DOCS - TypeScript SDK API reference

## Document History

**[2026-08-30 14:20]**
- Fixed: agent capability shape corrected against live official docs (https://agentclientprotocol.com/protocol/v1/initialization + /schema) - `promptContentTypes` array DOES NOT EXIST (real: `promptCapabilities` object), session markers are top-level `loadSession` + separate `sessionCapabilities` (not nested `session.*`), `mcp` is `mcpCapabilities` {http, sse} with stdio assumed
- Added: mandatory text + resource_link prompt baseline; baseline agent methods; capability marker semantics (omitted/null vs {})
- Fixed: Python and TypeScript examples, Quick Reference, gotchas to match

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: Elicitation capabilities (form, url) in client capabilities
- Added: Boolean config options in agent capabilities
- Added: v2 initialization changes section
- Added: TypeScript Examples section (dual-language format)
- Updated: JSON examples to include elicitation and config options
- Updated: Python example with capabilities declaration

**[2026-06-12 09:25]**
- Initial document created
