# Model Context Protocol (MCP) - Summary

**Doc ID**: MCP-IN01
**Goal**: Cross-document synthesis and master index for MCP research
**Version scope**: Spec 2025-11-25 (current), documentation as of 2026-06-12
**Research stats**: ~68m net | 9 docs (IN03-IN11) | 11 sources (7 Tier 1, 2 Tier 2, 2 Tier 3) | 4 phases completed

**Depends on:**
- `_INFO_MCP-02_Sources.md [MCP-IN02]` for source references

## Summary

MCP (Model Context Protocol) is an open standard by Anthropic (Nov 2024) that solves the N x M integration problem between AI applications and external tools by standardizing context exchange via JSON-RPC 2.0. [VERIFIED] Its client-host-server architecture enforces security isolation: hosts manage multiple clients, each maintaining a dedicated 1:1 connection to a server with independent capability negotiation. The protocol's two-layer design separates data semantics (primitives, lifecycle) from transport mechanics (stdio for local, Streamable HTTP for remote), enabling the same message format across all communication channels.

The specification defines a clear control hierarchy: user-controlled prompts, application-controlled resources, and model-controlled tools, with three client features (sampling, roots, elicitation) enabling servers to request LLM completions, filesystem boundaries, and user input without direct API access. [VERIFIED] Through 4 revisions (2024-11-05 to 2025-11-25), the protocol has added Streamable HTTP transport, OAuth 2.1 authorization with three client registration approaches, elicitation (form + URL modes), tool calling in sampling, and experimental Tasks for durable execution. [VERIFIED]

Ten official SDKs span 4 tiers with conformance testing and formal maintenance commitments - TypeScript, Python, C#, and Go at Tier 1. [VERIFIED] The protocol was donated to the Agentic AI Foundation (Linux Foundation) in Dec 2025, establishing formal governance via SEPs, working groups, and a BDFL-led steering group. [VERIFIED]

Security remains the primary challenge. Six attack categories are documented in the spec: tool poisoning via hidden instructions, rug pulls (description mutation), confused deputy attacks on proxy servers, SSRF via OAuth discovery, session hijacking, and token passthrough. [VERIFIED] The CSA reported 30+ CVEs in early 2026, and published a 4-level security maturity model. [VERIFIED] The roadmap prioritizes transport scalability, agent communication improvements, governance maturation, and enterprise readiness (audit trails, gateway patterns, SSO integration). [VERIFIED]

Design patterns reinforce across topics: 1:1 client-server isolation (IN03) prevents confused deputy cross-server data leakage (IN11), while per-session capability negotiation (IN04) constrains the attack surface - a session without `tools` capability cannot suffer tool poisoning. Transport choice determines the threat model: stdio has no remote attack surface, while Streamable HTTP necessitated OAuth 2.1 (IN09), which created the SSRF and session hijacking vectors dominating the CVE landscape (IN11). Protocol evolution shows a reactive security pattern - each version added features then security mechanisms (2025-06-18: Streamable HTTP + OAuth 2.1; 2025-11-25: Client ID metadata + scope minimization). AAIF governance formalization (IN10) enabled the SDK tiering system (IN08) with conformance testing, creating a quality pipeline absent during MCP's first year. [VERIFIED, cross-reference synthesis from IN03-IN11]

## Topic Files

### Architecture and Design (2 files)

- [`_INFO_MCP-03_ProblemAndArchitecture.md`](./_INFO_MCP-03_ProblemAndArchitecture.md) [MCP-IN03]
  - Problem statement MCP solves, client-host-server architecture, design principles, comparison with LSP and prior approaches
- [`_INFO_MCP-04_ProtocolLifecycle.md`](./_INFO_MCP-04_ProtocolLifecycle.md) [MCP-IN04]
  - Initialization handshake, capability negotiation, operation phase, shutdown, version negotiation, JSON-RPC message format

### Specification Primitives (3 files)

- [`_INFO_MCP-05_ServerPrimitives.md`](./_INFO_MCP-05_ServerPrimitives.md) [MCP-IN05]
  - Tools, resources, prompts: schemas, capabilities, protocol messages, message flows, data types
- [`_INFO_MCP-06_ClientFeatures.md`](./_INFO_MCP-06_ClientFeatures.md) [MCP-IN06]
  - Sampling, roots, elicitation: user interaction models, protocol messages, security considerations
- [`_INFO_MCP-07_TransportsAndUtilities.md`](./_INFO_MCP-07_TransportsAndUtilities.md) [MCP-IN07]
  - stdio, Streamable HTTP, custom transports. Utilities: cancellation, progress, ping, logging, pagination, tasks

### Implementation (2 files)

- [`_INFO_MCP-08_SDKsAndExamples.md`](./_INFO_MCP-08_SDKsAndExamples.md) [MCP-IN08]
  - SDK tiering system, TypeScript and Python SDK examples (server and client), setup and configuration
- [`_INFO_MCP-09_AuthorizationAndOAuth.md`](./_INFO_MCP-09_AuthorizationAndOAuth.md) [MCP-IN09]
  - OAuth 2.1 authorization framework, discovery, client registration, token usage, enterprise-managed auth, client credentials

### Evolution and Ecosystem (1 file)

- [`_INFO_MCP-10_VersionsAndEvolution.md`](./_INFO_MCP-10_VersionsAndEvolution.md) [MCP-IN10]
  - All 4 spec versions (2024-11-05 through 2025-11-25), changelogs, governance (AAIF, SEPs, working groups), ecosystem adoption timeline, roadmap

### Security and Best Practices (1 file)

- [`_INFO_MCP-11_SecurityAndBestPractices.md`](./_INFO_MCP-11_SecurityAndBestPractices.md) [MCP-IN11]
  - Attack vectors (tool poisoning, rug pulls, confused deputy, SSRF, session hijacking), CVEs, CSA maturity model, official security best practices, production deployment guidance

## Topic Count

- **Total Topics**: 9
- **Architecture and Design**: 2
- **Specification Primitives**: 3
- **Implementation**: 2
- **Evolution and Ecosystem**: 1
- **Security and Best Practices**: 1

## Topic Details

### Topic: ProblemAndArchitecture
**Scope**: Why MCP exists, what it replaces, how it is structured
**Contents**:
- N x M integration problem before MCP
- USB-C analogy and LSP inspiration
- Client-host-server architecture with security boundaries
- Core design principles (easy to build, composable, isolated, progressive)
- Comparison: MCP vs function calling, vs OpenAPI, vs ChatGPT plugins
**Sources**: MCP-SC-MCPIO-LLMSFULL, MCP-SC-WIKI-MCP

### Topic: ProtocolLifecycle
**Scope**: Connection lifecycle from initialization through shutdown
**Contents**:
- Initialize request/response with capability and version negotiation
- Capability table (client and server capabilities)
- Operation phase: request/response, notifications
- Shutdown and disconnect behavior
- JSON-RPC 2.0 message format, error codes
- MCP-Protocol-Version header for HTTP transport
**Sources**: MCP-SC-MCPIO-SPEC2511

### Topic: ServerPrimitives
**Scope**: Tools, resources, and prompts as server-exposed capabilities
**Contents**:
- Tools: model-controlled, inputSchema (JSON Schema 2020-12), tool annotations, structured output
- Resources: URI-identified, read-only, subscriptions, resource templates
- Prompts: user-controlled templates, arguments, multi-step workflows
- Control hierarchy: user-controlled (prompts) -> app-controlled (resources) -> model-controlled (tools)
**Sources**: MCP-SC-MCPIO-SPEC2511

### Topic: ClientFeatures
**Scope**: Sampling, roots, elicitation as client-provided capabilities
**Contents**:
- Sampling: server requests LLM completions through client, human-in-loop control
- Roots: filesystem/URI boundaries for server operation scope
- Elicitation: server requests user input via forms or URLs (added 2025-06-18)
- Tool calling support in sampling (added 2025-11-25)
**Sources**: MCP-SC-MCPIO-SPEC2511

### Topic: TransportsAndUtilities
**Scope**: Communication mechanisms and protocol utilities
**Contents**:
- stdio: subprocess model, stdin/stdout JSON-RPC, stderr logging
- Streamable HTTP: POST/GET, Server-Sent Events (SSE) streaming, session management, resumability
- Backwards compatibility with HTTP+SSE (2024-11-05)
- Utilities: cancellation, progress tracking, ping, logging, pagination
- Tasks: experimental durable request tracking (added 2025-11-25)
**Sources**: MCP-SC-MCPIO-SPEC2511

### Topic: SDKsAndExamples
**Scope**: Official SDKs and practical implementation guidance
**Contents**:
- SDK tiering: Tier 1 (TS, Python, C#, Go), Tier 2 (Java, Rust), Tier 3 (Swift, Ruby, PHP)
- Python FastMCP server example (weather tools)
- TypeScript server example
- Client implementation patterns
- MCP Inspector tool for debugging
**Sources**: MCP-SC-MCPIO-LLMSFULL, MCP-SC-GH-TSSDK, MCP-SC-GH-PYSDK

### Topic: AuthorizationAndOAuth
**Scope**: Authentication and authorization framework
**Contents**:
- OAuth 2.1 with PKCE flow for MCP servers
- Authorization server discovery (OIDC, RFC 9728)
- Client registration: Client ID Metadata Documents, dynamic registration, preregistration
- Token usage and error handling
- Enterprise-managed authorization
- OAuth client credentials for machine-to-machine
**Sources**: MCP-SC-MCPIO-SPEC2511

### Topic: VersionsAndEvolution
**Scope**: Protocol evolution from launch through current version
**Contents**:
- Version timeline: 2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25
- Key changes per version
- AAIF donation (Dec 2025), governance structure
- SEP process, working groups, interest groups
- Adoption: OpenAI (Mar 2025), VS Code, Cursor, ChatGPT apps (Sep 2025)
- Roadmap: transport evolution, agent communication, enterprise readiness
**Sources**: MCP-SC-MCPIO-CHLOG2511, MCP-SC-MCPIO-CHLOG0618, MCP-SC-WIKI-MCP

### Topic: SecurityAndBestPractices
**Scope**: Security threats, mitigations, and production guidance
**Contents**:
- Threat landscape: 6 attack categories (tool poisoning, rug pulls, confused deputy, SSRF, session hijacking, supply chain)
- CVE examples (CVE-2025-6514 pre-auth RCE, GitHub MCP prompt injection)
- CSA Security Maturity Model (4 levels)
- Official security best practices (trust boundaries, consent, data privacy)
- Production deployment checklist
**Sources**: MCP-SC-CSA-SECBP, MCP-SC-MCPIO-SPEC2511

## Document History

**[2026-06-12 12:00]**
- Fixed: Non-standard [IMPROVED] label changed to [VERIFIED] (QA-09)

**[2026-06-12 11:30]**
- Added: Cross-reference synthesis paragraph connecting IN03-IN11 findings (architecture→security, transport→threat model, governance→SDK quality)
- Fixed: SSE acronym expanded on first use (AP-NM-01)

**[2026-06-12 11:00]**
- Changed: Research stats format to `Xm net | Y docs | Z sources`
- Verified: All topic file links resolve, Doc IDs consistent

**[2026-06-12 10:30]**
- Summary finalized with cross-document synthesis, research stats added
- All 9 topic files verified for dimension coverage

**[2026-06-12 09:35]**
- Initial Summary skeleton created with 9 topics in 5 categories
