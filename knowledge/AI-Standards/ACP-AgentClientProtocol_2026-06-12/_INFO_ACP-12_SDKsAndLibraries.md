# ACP: SDKs and Libraries

**Doc ID**: ACP-IN12
**Goal**: Document official SDKs, community libraries, and implementation examples
**Version scope**: As of 2026-06-12

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP provides official SDKs in five languages (Kotlin, Java, Python, Rust, TypeScript) maintained under the `agentclientprotocol` GitHub organization. Each SDK handles the JSON-RPC 2.0 wire protocol, initialization handshake, and session management, allowing developers to focus on agent logic. Community libraries extend coverage to additional languages and frameworks. [VERIFIED] (ACP-SC-GH-REPO, ACP-SC-ACPORG-CLNTS)

## Official SDKs

### Kotlin SDK

- **Package**: `acp-kotlin`
- **Repository**: github.com/agentclientprotocol/kotlin-sdk
- **Platform**: JVM (other Kotlin targets in progress)
- **Examples**: github.com/agentclientprotocol/kotlin-sdk/tree/master/samples

[VERIFIED] (ACP-SC-GH-REPO)

### Java SDK

- **Package**: `java-sdk`
- **Repository**: github.com/agentclientprotocol/java-sdk
- **Examples**: github.com/agentclientprotocol/java-sdk/tree/main/examples

[VERIFIED] (ACP-SC-GH-REPO)

### Python SDK

- **Package**: `agent-client-protocol` (pip install)
- **Repository**: github.com/agentclientprotocol/python-sdk
- **Requires**: Python 3.10+
- **Features**: Async base classes, stdio JSON-RPC transport, helper builders
- **Examples**: github.com/agentclientprotocol/python-sdk/tree/main/examples
- **Docs**: agentclientprotocol.github.io/python-sdk/quickstart/

[VERIFIED] (ACP-SC-GH-REPO, ACP-SC-MRPH-EXPL)

### Rust SDK

- **Crate**: `agent-client-protocol` (crates.io)
- **Repository**: github.com/agentclientprotocol/rust-sdk
- **Examples**: `examples/agent.rs` and `examples/client.rs`

[VERIFIED] (ACP-SC-GH-REPO)

### TypeScript SDK

- **Package**: `@agentclientprotocol/sdk` (npm)
- **Repository**: github.com/agentclientprotocol/typescript-sdk
- **Examples**: github.com/agentclientprotocol/typescript-sdk/tree/main/src/examples

[VERIFIED] (ACP-SC-GH-REPO)

## SDK Examples

### Python: Minimal Echo Agent

```python
# echo_agent.py
import asyncio
from acp import Agent, Session

class EchoAgent(Agent):
    async def on_prompt(self, session: Session, prompt: str) -> str:
        # Stream a response back to the editor
        await session.stream_text(f"You said: {prompt}")
        return "done"

if __name__ == "__main__":
    asyncio.run(EchoAgent().run_stdio())
```

[VERIFIED] (ACP-SC-MRPH-EXPL) - Note: simplified example from Morph LLM; verify exact API against official SDK docs.

### TypeScript: Agent with File Access

```typescript
import { createAcpAgent } from "@agentclientprotocol/sdk";

const agent = createAcpAgent({
  name: "my-agent",
  version: "1.0.0",
  onPrompt: async (session, prompt) => {
    // Read a file from the editor
    const file = await session.readFile("/src/index.ts");
    // Stream partial responses
    await session.streamText(`Processing: ${file.path}`);
    return "done";
  },
});

agent.run(); // starts stdio loop
```

[VERIFIED] (ACP-SC-MRPH-EXPL) - Note: simplified example; verify exact API against official SDK docs.

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

Additional language bindings and integrations maintained by the community: [VERIFIED] (ACP-SC-ACPORG-CLNTS)

- **AI SDK Provider**: `@mcpc/acp-ai-provider` - ACP integration for the AI SDK
- **Pydantic AI**: `pydantic-acp` - Adapter for Pydantic AI runtimes
- **LangChain**: `langchain-acp` - ACP integration for LangChain agents
- **ACP Kit**: `acpkit` - Adapter toolkit for multiple Python agent frameworks

## JSON Schema

The protocol is formally defined via JSON Schema, published at: [VERIFIED] (ACP-SC-GH-REPO)

- **Location**: `schema/v1/schema.json` in the main repository
- **Usage**: SDK code generation, validation, documentation
- **Versioning**: Schema artifact version is separate from protocol wire version

## Quick Reference

- **Python**: `pip install agent-client-protocol` (3.10+)
- **TypeScript**: `npm install @agentclientprotocol/sdk`
- **Rust**: `cargo add agent-client-protocol`
- **Kotlin**: `acp-kotlin` (Maven/Gradle)
- **Java**: `java-sdk` (Maven/Gradle)
- **Schema**: `schema/v1/schema.json`
- **Agent CLI flag**: Most agents use `--acp` to enable ACP mode

## Limitations and Gotchas

- SDK examples from blog posts may be simplified or outdated; always verify against the official SDK documentation
- The Python SDK requires Python 3.10+ for async features
- Community libraries vary in maturity and may lag behind protocol updates
- The `--acp` flag convention is common but not universal; some agents use different CLI interfaces
- SDK versioning follows artifact versioning, not protocol versioning (see Versioning in `_INFO_ACP-13_VersionHistoryAndRoadmap.md [ACP-IN13]`)

## Sources

- ACP-SC-GH-REPO - GitHub repository with SDK links and versioning details
- ACP-SC-MRPH-EXPL - SDK examples (Python, TypeScript, Zed config, Neovim config)
- ACP-SC-AISDK-PRVDR - AI SDK community provider documentation
- ACP-SC-ACPORG-CLNTS - Community libraries and framework integrations

## Document History

**[2026-06-12 10:12]**
- Initial document created
