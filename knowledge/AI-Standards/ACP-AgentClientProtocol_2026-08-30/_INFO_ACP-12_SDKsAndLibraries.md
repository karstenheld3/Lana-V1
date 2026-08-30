# ACP: SDKs and Libraries

**Doc ID**: ACP-IN12
**Goal**: Document official SDKs, community libraries, and implementation examples
**Version scope**: As of 2026-08-30

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP provides official SDKs in five languages (Kotlin, Java, Python, Rust, TypeScript) maintained under the `agentclientprotocol` GitHub organization. The Rust and TypeScript SDKs reached v1.0 in June 2026. Each SDK handles the JSON-RPC 2.0 wire protocol, initialization handshake, and session management. Community libraries extend coverage to additional frameworks. [VERIFIED] (ACP-SC-GH-REPO, ACP-SC-ANN-SDK10)

## Official SDKs

### Python SDK

- **Package**: `agent-client-protocol` (pip / uv)
- **Version**: 0.12.1 (August 16, 2026) [VERIFIED] (ACP-SC-PYPI-ACP)
- **Repository**: https://github.com/agentclientprotocol/python-sdk (307 stars) [VERIFIED] (ACP-SC-GH-PYSD)
- **Docs**: https://agentclientprotocol.github.io/python-sdk/ [VERIFIED] (ACP-SC-PYSD-DOCS)
- **Requires**: Python 3.10+ (< 3.15)
- **Features**: Async base classes, stdio JSON-RPC transport, helper builders (`acp.helpers`), contrib utilities (session accumulators, tool call trackers, permission brokers), Pydantic schema models (`acp.schema`)
- **Examples**: Streaming, permissions, Gemini bridge, duet demos under `examples/`
- **Recent changes**: v0.12.0 added ACP schema v1.19.0 (extensible unions + lenient deserialization), RFD-based HTTP and WS web transport implementation

### TypeScript SDK

- **Package**: `@agentclientprotocol/sdk` (npm)
- **Version**: 1.4.0 (stable v1 API) [VERIFIED] (ACP-SC-TSSD-DOCS)
- **Repository**: https://github.com/agentclientprotocol/typescript-sdk
- **Docs**: https://agentclientprotocol.github.io/typescript-sdk/ [VERIFIED] (ACP-SC-TSSD-DOCS)
- **v2 support**: Experimental import via `@agentclientprotocol/sdk/experimental/v2`
- **1.0 milestone**: Reached June 25, 2026 [VERIFIED] (ACP-SC-ANN-SDK10)

### Rust SDK

- **Crate**: `agent-client-protocol` (crates.io)
- **Version**: 1.0.0+ [VERIFIED] (ACP-SC-ANN-SDK10)
- **Repository**: https://github.com/agentclientprotocol/rust-sdk
- **Architecture**: Component-based with explicit message ordering and composable handlers
- **1.0 milestone**: Reached June 25, 2026

### Kotlin SDK

- **Package**: `acp-kotlin`
- **Repository**: https://github.com/agentclientprotocol/kotlin-sdk
- **Platform**: JVM (other Kotlin targets in progress)
- **Examples**: `samples/` directory [VERIFIED] (ACP-SC-GH-REPO)

### Java SDK

- **Package**: `java-sdk`
- **Repository**: https://github.com/agentclientprotocol/java-sdk
- **Examples**: `examples/` directory [VERIFIED] (ACP-SC-GH-REPO)

## SDK Examples

### Python: Minimal Echo Agent

```python
import asyncio
from acp import Agent, Session

class EchoAgent(Agent):
    async def on_prompt(self, session: Session, prompt: str) -> str:
        await session.stream_text(f"You said: {prompt}")
        return "done"

if __name__ == "__main__":
    asyncio.run(EchoAgent().run_stdio())
```

[VERIFIED] (ACP-SC-MRPH-EXPL, ACP-SC-GH-PYSD) - Simplified; verify exact API against v0.12.1 docs.

### Python: Agent with File Access and Permissions

```python
import asyncio
from acp import Agent, Session

class FileAgent(Agent):
    async def on_prompt(self, session: Session, prompt: str) -> str:
        # Request permission before file operations
        allowed = await session.request_permission(
            tool_call_id="call_001",
            title="Read source file",
            kind="read",
            options=["allow_once", "reject_once"],
        )
        if allowed:
            content = await session.read_file("/src/main.py")
            await session.stream_text(f"File contents: {content[:200]}...")
        else:
            await session.stream_text("Permission denied.")
        return "done"

if __name__ == "__main__":
    asyncio.run(FileAgent().run_stdio())
```

[SYNTHESIZED from SDK patterns] - Verify exact API against `agent-client-protocol` v0.12.1 docs.

### Zed Configuration: Adding a Custom Agent

```json
{
  "agent": {
    "profiles": {
      "my-goose-agent": {
        "provider": "acp",
        "command": "goose",
        "args": ["run", "--acp"]
      }
    }
  }
}
```

[VERIFIED] (ACP-SC-MRPH-EXPL)

### Neovim Configuration: agentic.nvim

```lua
{
  "carlos-algms/agentic.nvim",
  config = function()
    require("agentic").setup({
      default_agent = "claude-code",
      agents = {
        ["claude-code"] = {
          command = "claude",
          args = { "--acp" },
        },
        ["gemini"] = {
          command = "gemini",
          args = { "--acp" },
        },
      },
    })
  end,
}
```

[VERIFIED] (ACP-SC-MRPH-EXPL)

## Community Libraries

Additional language bindings and integrations: [VERIFIED] (ACP-SC-ACPORG-CLNTS)

- **AI SDK Provider**: `@mcpc/acp-ai-provider` - ACP integration for the AI SDK
- **Pydantic AI**: `pydantic-acp` - Adapter for Pydantic AI runtimes
- **LangChain**: `langchain-acp` - ACP integration for LangChain agents
- **ACP Kit**: `acpkit` - Adapter toolkit for multiple Python agent frameworks

## JSON Schema

The protocol is formally defined via JSON Schema: [VERIFIED] (ACP-SC-GH-REPO)

- **v1**: `schema/v1/schema.json` (stable)
- **v2**: `schema/v2/schema.json` (draft baseline), `schema/v2/schema.unstable.json` (draft features)
- **v2 alpha releases**: Published as `v2.0.0-alphaX` alongside v1 releases
- **Usage**: SDK code generation, validation, documentation

## Quick Reference

- **Python**: `pip install agent-client-protocol` (v0.12.1, Python 3.10+)
- **TypeScript**: `npm install @agentclientprotocol/sdk` (v1.4.0)
- **Rust**: `cargo add agent-client-protocol` (v1.0.0+)
- **Kotlin**: `acp-kotlin` (Maven/Gradle)
- **Java**: `java-sdk` (Maven/Gradle)
- **v1 Schema**: `schema/v1/schema.json`
- **v2 Schema**: `schema/v2/schema.json` (draft)
- **Agent CLI flag**: Most agents use `--acp` to enable ACP mode

## Limitations and Gotchas

- SDK examples from blog posts may be simplified or outdated; always verify against official SDK docs
- The Python SDK requires Python 3.10+ (< 3.15) for async features
- Community libraries vary in maturity and may lag behind protocol updates
- The `--acp` flag convention is common but not universal
- SDK artifact versioning follows its own semver, separate from protocol version
- v2 SDK support is experimental; use `@agentclientprotocol/sdk/experimental/v2` for TypeScript

## TypeScript Examples

### Minimal Echo Agent

```typescript
import { AgentApp, agent } from "@agentclientprotocol/sdk";

const app = new AgentApp();

// Register request handler for session/prompt
app.onRequest("session/prompt", async (params, session) => {
  // session is an ActiveSession
  await session.streamText(`You said: ${params.prompt[0].text}`);
  return { stopReason: "end_turn" };
});

// Connect via stdio
app.connect(agent.stdio());
```

[SDK-VERIFIED] v1.4.0 - AgentApp uses onRequest/onNotification pattern, not createAcpAgent.

### Agent with Session Builder

```typescript
import { AgentApp, SessionBuilder, agent } from "@agentclientprotocol/sdk";

const app = new AgentApp();

// Initialize handler
app.onRequest("initialize", async (params) => {
  return {
    protocolVersion: 1,
    agentInfo: { name: "file-agent", version: "1.0.0" },
    agentCapabilities: { session: {} },
  };
});

// Session creation
app.onRequest("session/new", async (params) => {
  return { sessionId: "sess_" + Date.now(), title: "New Session" };
});

// Prompt handling
app.onRequest("session/prompt", async (params, session) => {
  await session.streamText("Processing your request...");
  return { stopReason: "end_turn" };
});

app.connect(agent.stdio());
```

[SDK-VERIFIED] v1.4.0 - Core classes: AgentApp, ClientApp, ActiveSession, SessionBuilder, AgentContext, RequestError.

### v2 Experimental Usage

```typescript
// v2 requires explicit experimental import
import { AgentApp } from "@agentclientprotocol/sdk/experimental/v2";

// v2 AgentApp has additional exports: AgentProtocolRouter, StateUpdate,
// SessionUpdate, ContentBlock, DiffChange, PlanUpdateContent, ReplayFrom
// v2 API may change; gate behind feature flags
```

[SDK-VERIFIED] v1.4.0 - v2 experimental available at @agentclientprotocol/sdk/experimental/v2

## Sources

- ACP-SC-GH-REPO - GitHub repository, schema versioning
- ACP-SC-GH-PYSD - Python SDK repository, features, recent changes
- ACP-SC-GH-TSSD - TypeScript SDK repository
- ACP-SC-PYPI-ACP - Python SDK on PyPI (version history)
- ACP-SC-NPM-ACP - TypeScript SDK on npm
- ACP-SC-PYSD-DOCS - Python SDK documentation hub
- ACP-SC-TSSD-DOCS - TypeScript SDK API reference (v1.4.0 + experimental v2)
- ACP-SC-ANN-SDK10 - Rust + TypeScript SDK 1.0 announcement
- ACP-SC-MRPH-EXPL - SDK examples (Python, TypeScript, Zed config, Neovim config)
- ACP-SC-ACPORG-CLNTS - Community libraries and framework integrations

## Document History

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Updated: Python SDK version to 0.12.1 (was unversioned), added features list and recent changes
- Updated: TypeScript SDK version to 1.4.0 with experimental v2 import
- Added: Rust SDK 1.0 milestone and architecture description
- Added: v2 JSON Schema references (draft baseline + unstable)
- Added: Python file access/permissions example
- Added: TypeScript Examples section (dual-language format)
- Added: SDK documentation links (PYSD-DOCS, TSSD-DOCS)

**[2026-06-12 10:12]**
- Initial document created
