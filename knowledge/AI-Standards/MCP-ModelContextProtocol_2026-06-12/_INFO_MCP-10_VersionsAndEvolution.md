# MCP: Versions and Evolution

**Doc ID**: MCP-IN10
**Goal**: Document all protocol versions, governance evolution, ecosystem adoption, and roadmap
**Version scope**: Spec 2025-11-25 (current), governance and roadmap as of 2026-03-05

**Depends on:**
- `_INFO_MCP-02_Sources.md [MCP-IN02]` for source references

## Summary

MCP has gone through 4 specification versions from Nov 2024 to Nov 2025. The initial release (2024-11-05) established stdio and HTTP+Server-Sent Events (SSE) transports with tools, resources, prompts, and sampling. Version 2025-06-18 replaced HTTP+SSE with Streamable HTTP, added elicitation and the OAuth 2.1 authorization framework. The current version (2025-11-25) introduced experimental Tasks, URL elicitation, Client ID Metadata Documents, and SDK tiering. In Dec 2025, MCP was donated to the Agentic AI Foundation (AAIF) under the Linux Foundation. Governance uses a BDFL-led steering group with Specification Enhancement Proposals (SEPs) and 6 working groups.

## Version Timeline

### 2024-11-05 (Initial Release)

[VERIFIED, spec + Wikipedia] Announced by Anthropic in November 2024. Created by David Soria Parra and Justin Spahr-Summers.

**Core features**:
- JSON-RPC 2.0 message format
- Client-host-server architecture
- Transports: stdio + HTTP+SSE
- Server primitives: tools, resources, prompts
- Client features: sampling, roots
- Lifecycle: initialization with capability negotiation, operation, shutdown
- Cancellation, progress tracking, ping, logging, pagination

**First hosts**: Claude Desktop, Zed editor, Sourcegraph Cody

### 2025-03-26 (Second Revision)

[PARTIALLY VERIFIED - changelog not individually read, referenced by 2025-06-18 changelog as prior version]

Interim revision between initial launch and major 2025-06-18 update. HTTP+SSE transport still active. OpenAI adopted MCP in March 2025, integrating into ChatGPT desktop app and Agents SDK. [VERIFIED, Wikipedia]

### 2025-06-18 (Third Revision)

[VERIFIED, changelog at modelcontextprotocol.io/specification/2025-06-18/changelog]

**Major changes**:
- **Streamable HTTP transport** replaces HTTP+SSE (backwards-compatible fallback defined)
- **Elicitation** added as client feature (form mode for structured data collection)
- **OAuth 2.1 authorization framework** with Protected Resource Metadata (RFC 9728)
- **Tool annotations** for behavior hints (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
- **Structured tool output** with `outputSchema` and `structuredContent`
- **Audio content type** added to messages
- **Incremental scope consent** via step-up authorization

**Minor changes**:
- JSON Schema dialect standardized (2020-12 default)
- Clarified stdio stderr logging
- HTTP 403 for invalid Origin headers
- Security best practices expanded

### 2025-11-25 (Current Version)

[VERIFIED, changelog at modelcontextprotocol.io/specification/2025-11-25/changelog]

**Major changes** (9):
1. OpenID Connect Discovery 1.0 support for authorization server discovery
2. Icons as metadata for tools, resources, resource templates, prompts (SEP-973)
3. Incremental scope consent via `WWW-Authenticate` (SEP-835)
4. Tool name guidance (1-128 chars, case-sensitive, restricted charset) (SEP-986)
5. Updated elicitation: standards-based enums, titled/untitled, single/multi-select (SEP-1330)
6. URL mode elicitation for out-of-band interactions (SEP-1036)
7. Tool calling in sampling via `tools` and `toolChoice` (SEP-1577)
8. OAuth Client ID Metadata Documents for client registration (SEP-991)
9. Experimental Tasks for durable request tracking with polling (SEP-1686)

**Minor changes** (10):
1. stderr logging clarification for stdio
2. Optional `description` in `Implementation` interface
3. HTTP 403 for invalid Origin headers
4. Updated security best practices
5. Input validation errors as Tool Execution Errors (SEP-1303)
6. Polling SSE streams (SEP-1699)
7. GET stream resumption clarifications
8. RFC 9728 alignment for Protected Resource Metadata discovery (SEP-985)
9. Default values in elicitation schemas (SEP-1034)
10. JSON Schema 2020-12 as default dialect (SEP-1613)

## Governance

### Agentic AI Foundation (AAIF) Donation (December 2025)

[VERIFIED, Wikipedia] MCP donated to AAIF under the Linux Foundation. Established as "Model Context Protocol a Series of LF Projects, LLC."

**Licensing**:
- Code and specifications: Apache License 2.0
- Documentation (non-spec): Creative Commons Attribution 4.0 International

### Technical Governance Structure

[VERIFIED, official docs: community/governance]

- **Lead Maintainers** (Benevolent Dictator for Life / BDFL) - Final decision authority
- **Core Maintainers** - Overall project direction
- **Maintainers** - Working Groups, SDKs, components
- **Contributors** - Issues, PRs, discussions

Together: Maintainers + Core Maintainers + Lead Maintainers = **MCP Steering Group**

Membership is individual, not company-based. No reserved seats for specific companies.

### SEP Process

[VERIFIED, official docs: community/sep-guidelines]

Specification Enhancement Proposals (SEPs) are the mechanism for proposing protocol changes. SEPs aligned with roadmap priority areas receive expedited review. SEPs with Working Group backing move fastest.

### Working Groups and Interest Groups

[VERIFIED, official docs] Formalized via SEP-1302.

**Working Groups** (deliverable-focused):
- Transports WG - transport and session evolution
- Server Card WG - server metadata discovery
- Agents WG - Tasks primitive lifecycle
- Governance WG - contributor ladder, delegation
- SDK WG - SDK tiering and conformance
- Conformance Testing WG - automated protocol tests

**Interest Groups** (discussion-focused): Enterprise IG, Security IG, others.

## Ecosystem Adoption Timeline

- **Nov 2024** - Anthropic announces MCP. Claude Desktop, Zed, Sourcegraph Cody adopt.
- **Mar 2025** - OpenAI adopts MCP in ChatGPT desktop app and Agents SDK.
- **Mar 2025** - Google DeepMind announces MCP support.
- **Sep 2025** - ChatGPT apps integrate MCP for interactive UIs.
- **Dec 2025** - MCP donated to AAIF (Linux Foundation).
- **Jan 2026** - Conformance tests available.
- **Feb 2026** - Official SDK tiering published.

[VERIFIED, Wikipedia + official docs]

**Notable hosts**: Claude Desktop, Claude Code, VS Code, Cursor, Windsurf, ChatGPT apps, Zed

**Ecosystem scale**: 97M+ SDK downloads reported by enterprise adoption guides. [COMMUNITY, not officially verified]

## Roadmap (as of 2026-03-05)

[VERIFIED, official docs: development/roadmap]

Four priority areas:

### 1. Transport Evolution and Scalability

- Evolve Streamable HTTP for stateless operation across multiple server instances
- Scalable session handling (creation, resumption, migration)
- MCP Server Cards: structured metadata via `.well-known` URL for discovery
- No additional official transports this cycle

### 2. Agent Communication

- Tasks primitive lifecycle improvements (retry semantics, expiry policies)
- Collect operational issues from production deployments
- Owned by Agents WG

### 3. Governance Maturation

- Contributor Ladder SEP (participant -> contributor -> facilitator -> maintainer -> core)
- Delegation model for WGs to accept SEPs within their domain
- Charter template for WGs/IGs (scope, deliverables, success criteria, retirement)

### 4. Enterprise Readiness

- Audit trails and observability (end-to-end logging, compliance)
- Enterprise-managed auth (SSO integration, Cross-App Access)
- Gateway and proxy patterns (auth propagation, session semantics)
- Configuration portability (configure once, use across clients)
- Expected Enterprise WG to form; output likely as extensions, not core spec

## Versioning Mechanism

[VERIFIED, spec]
- Format: `YYYY-MM-DD` string (date of last backward-incompatible change)
- Negotiated during initialization handshake
- Revision states: Draft, Current, Final
- Feature states: Experimental, Deprecated (with removal timeline), Removed
- Backward compatibility maintained via capability negotiation

## Limitations and Known Issues

- Changelog for version 2025-03-26 was not individually read - changes inferred from the 2025-06-18 changelog's "from" baseline [PARTIALLY VERIFIED]
- Roadmap priorities are aspirational, not committed - timelines may shift
- Governance is still maturing; contributor ladder and delegation policies are being formalized via the Governance Working Group
- No formal backward-compatibility guarantee across major versions beyond capability negotiation

## Sources

- MCP-SC-MCPIO-CHLOG2511, MCP-SC-MCPIO-CHLOG0618 (changelogs)
- MCP-SC-MCPIO-LLMSFULL (positions 85-86, 240-242, 427-433, 438-451, 895-898)
- MCP-SC-WIKI-MCP (adoption timeline)

## Document History

**[2026-06-12 10:15]**
- Initial topic file with 4 version changelogs, governance, adoption timeline, and roadmap
