# MCP: Problem Statement and Architecture

**Doc ID**: MCP-IN03
**Goal**: Document the problem MCP solves and its architectural approach
**Version scope**: Spec 2025-11-25 (current)

**Depends on:**
- `_INFO_MCP-02_Sources.md [MCP-IN02]` for source references

## Summary

MCP solves the N x M integration problem between AI applications and external tools by defining a standard client-host-server protocol over JSON-RPC 2.0. Hosts manage multiple isolated clients, each connecting 1:1 to a server. Eight design principles guide the protocol: easy to build, composable, isolated, progressive, standardized, well-defined, extensible, and transport-agnostic. MCP draws from the Language Server Protocol (LSP) for its architecture but targets LLM-to-tool context exchange rather than IDE language intelligence.

## Problem Statement

### The N x M Integration Problem

Before MCP, connecting AI applications to external data sources and tools required custom integrations for each combination. [VERIFIED] Each AI application (Claude, ChatGPT, VS Code Copilot) needed bespoke connector code for each tool or data source (GitHub, Slack, databases, file systems). With N applications and M tools, this produced N x M individual integrations - fragile, duplicated, and non-portable.

Earlier attempts to solve this:
- **OpenAI function calling** (2023): Vendor-specific API for tools. Required per-vendor implementation. [VERIFIED, Wikipedia]
- **ChatGPT plugins** (2023): Plugin framework for ChatGPT only. Discontinued. Required vendor-specific connectors. [VERIFIED, Wikipedia]
- **Custom REST integrations**: Per-application adapter code. No standard schema, no interoperability.

### What MCP Solves

MCP reduces N x M to N + M: each application implements one MCP client, each tool implements one MCP server. Any client connects to any server. [VERIFIED, official docs: "USB-C for AI applications"]

**Core value proposition**:
- Developers: Reduced development time and complexity
- AI applications: Access to ecosystem of data sources and tools
- End users: More capable AI applications that access data and take actions

## Architectural Approach

### Inspiration: Language Server Protocol (LSP)

MCP reuses the message-flow ideas of the Language Server Protocol (LSP), which solved the analogous N x M problem for IDE language support. [VERIFIED, Wikipedia] Like LSP, MCP uses JSON-RPC 2.0 as its wire protocol. The key difference: LSP standardizes language intelligence (completions, diagnostics), while MCP standardizes context exchange and tool invocation for LLMs.

### Client-Host-Server Architecture

MCP follows a client-host-server architecture where each host can run multiple client instances. [VERIFIED, spec: Architecture section]

**Three participants:**

- **Host**: The AI application (e.g., Claude Desktop, VS Code, Cursor) that coordinates and manages one or multiple MCP clients
  - Creates and manages multiple client instances
  - Controls client connection permissions and lifecycle
  - Enforces security policies and consent requirements
  - Handles user authorization decisions
  - Coordinates AI/LLM integration and sampling
  - Manages context aggregation across clients

- **Client**: A component within the host that maintains a 1:1 connection to a single MCP server
  - Establishes one stateful session per server
  - Handles protocol negotiation and capability exchange
  - Routes protocol messages bidirectionally
  - Manages subscriptions and notifications
  - Maintains security boundaries between servers

- **Server**: A program that provides context and capabilities
  - Exposes resources, tools, and prompts via MCP primitives
  - Operates independently with focused responsibilities
  - Requests sampling through client interfaces
  - Must respect security constraints
  - Can be local processes (stdio) or remote services (Streamable HTTP)

**Architecture diagram** (from spec):
```
Application Host Process
  Host
  ├── Client 1 ──── Server 1 (Files & Git) ──── Local Resource A
  ├── Client 2 ──── Server 2 (Database) ──── Local Resource B
  └── Client 3 ──── Server 3 (External APIs) ──── Remote Resource C
```

**Key relationship**: A host creates and manages multiple clients, with each client having a 1:1 relationship with a particular server. Local servers (stdio) typically serve a single client; remote servers (Streamable HTTP) can serve many clients.

### Two-Layer Design

MCP consists of two layers: [VERIFIED, official docs]

- **Data layer** (inner): JSON-RPC 2.0 based protocol defining message structure and semantics
  - Lifecycle management (init, capabilities, shutdown)
  - Server features: tools, resources, prompts
  - Client features: sampling, elicitation, logging
  - Utility features: notifications, progress tracking, tasks

- **Transport layer** (outer): Communication mechanisms and channels
  - stdio: standard input/output for local subprocess communication
  - Streamable HTTP: HTTP POST/GET with optional Server-Sent Events (SSE) for remote servers
  - Handles connection establishment, message framing, authorization

The transport layer abstracts communication details from the data layer, enabling the same JSON-RPC 2.0 message format across all transport mechanisms.

### Three Trust Boundaries

[VERIFIED, CSA Security Best Practices Guide] MCP creates three trust boundaries:

1. **LLM to MCP client**: The model reads tool descriptions and constructs invocations, but cannot verify that tool descriptions are accurate or unmodified
2. **MCP client to MCP servers**: The client must authenticate to servers and validate server responses
3. **MCP servers to downstream systems**: The server acts as an agent on behalf of the requesting model with potentially broad permissions

Attacks against any boundary can cascade throughout the agentic pipeline.

## Design Principles

Eight principles guide MCP protocol evolution: [VERIFIED, official docs: Design Principles]

1. **Convergence over choice**: One way to solve a problem. No fragmenting approaches.
2. **Composability over specificity**: Foundational primitives (resources, tools, prompts, tasks). No protocol features for use cases constructible from existing blocks.
3. **Interoperability over optimization**: Features that degrade gracefully. Capability negotiation makes this concrete.
4. **Stability over velocity**: Every addition is a permanent commitment. "No today leaves the door open, yes closes it forever."
5. **Capability over compensation**: Avoid permanent structure to work around temporary model limitations.
6. **Demonstration over deliberation**: Working implementations over theoretical debates. Prototype and demonstrate.
7. **Pragmatism over purity**: Practical tradeoffs in service of adoption. Accept some inconsistency.
8. **Standardization over innovation**: Standardize patterns already proven valuable. Extensions for experimentation.

## Protocol Scope

MCP focuses solely on the protocol for context exchange. [VERIFIED, official docs] It does NOT dictate:
- How AI applications use LLMs
- How provided context is managed or processed
- Which LLM model is used
- How the UI presents tools or resources

MCP includes:
- MCP Specification (authoritative protocol requirements)
- MCP SDKs (language-specific implementations)
- MCP Development Tools (Inspector, debugging)
- MCP Reference Server Implementations

## Comparison with Related Approaches

- **MCP** - LLM-to-tool context exchange. Protocol: JSON-RPC 2.0. Any client to any server. Active (spec 2025-11-25).
- **Language Server Protocol (LSP)** - IDE language intelligence. Protocol: JSON-RPC 2.0. Any IDE to any language server. Active, mature.
- **OpenAI function calling** - Tool invocation for OpenAI models. Protocol: OpenAI API (REST). OpenAI ecosystem only. Active, vendor-specific.
- **ChatGPT plugins** - Tool access for ChatGPT. Protocol: REST + manifest. ChatGPT only. Discontinued.
- **OpenAPI** - API description format. Protocol: REST. Any HTTP client. Active, complementary to MCP.

MCP and OpenAPI are complementary: OpenAPI describes API schemas, MCP provides the runtime protocol for LLMs to discover and invoke tools that may wrap those APIs.

## Limitations and Known Issues

- MCP solves N+M for protocol compatibility but not for semantic compatibility - each server still defines its own tool schemas
- No built-in service discovery mechanism - clients must know server endpoints in advance
- 1:1 client-server constraint prevents a single client from aggregating multiple servers natively (host must manage multiple clients)
- Protocol does not address multi-agent coordination - each client-server pair is independent

## Sources

- MCP-SC-MCPIO-LLMSFULL (positions 62-68, 180-183, 420-421)
- MCP-SC-WIKI-MCP (positions 4-5)
- MCP-SC-CSA-SECBP (position 3)

## Document History

**[2026-06-12 09:40]**
- Initial topic file created covering problem statement, architecture, design principles, and comparisons
