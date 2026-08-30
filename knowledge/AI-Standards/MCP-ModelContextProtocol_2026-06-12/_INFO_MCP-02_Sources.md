# MCP Model Context Protocol - Sources

**Doc ID**: MCP-IN02
**Goal**: Source registry for MCP MEPI Deep Research
**Version scope**: Spec 2025-11-25 (current), documentation as of 2026-06-12

## Source Tiers

### Tier 1: Official / Primary

- **MCP-SC-MCPIO-LLMSFULL** `modelcontextprotocol.io/llms-full.txt`
  - Complete official documentation including spec, tutorials, SDKs, security, governance, SEPs
  - 898 content chunks covering all aspects of MCP
  - Accessed: 2026-06-12
  - [VERIFIED] Primary authoritative source

- **MCP-SC-MCPIO-SPEC2511** `modelcontextprotocol.io/specification/2025-11-25/`
  - Current protocol specification (version 2025-11-25)
  - Authoritative TypeScript schema: `github.com/modelcontextprotocol/specification/blob/main/schema/2025-11-25/schema.ts`
  - Accessed: 2026-06-12
  - [VERIFIED] RFC 2119/8174 keyword compliance

- **MCP-SC-MCPIO-CHLOG2511** `modelcontextprotocol.io/specification/2025-11-25/changelog`
  - Changes from 2025-06-18 to 2025-11-25 (9 major, 10 minor changes)
  - Accessed: 2026-06-12
  - [VERIFIED] Lists tasks, URL elicitation, OAuth Client ID metadata docs as major additions

- **MCP-SC-MCPIO-CHLOG0618** `modelcontextprotocol.io/specification/2025-06-18/changelog`
  - Changes from 2025-03-26 to 2025-06-18
  - Accessed: 2026-06-12
  - [VERIFIED] Includes Streamable HTTP transport (replacing HTTP+SSE), elicitation, authorization framework

- **MCP-SC-GH-SPEC** `github.com/modelcontextprotocol/specification`
  - Official specification repository with schema definitions
  - Full git history for version evolution tracking
  - Accessed: 2026-06-12
  - [VERIFIED] Contains schema/ folders for each spec version

- **MCP-SC-GH-TSSDK** `github.com/modelcontextprotocol/typescript-sdk`
  - Official TypeScript SDK (Tier 1)
  - npm: `@modelcontextprotocol/sdk`
  - Accessed: 2026-06-12
  - [VERIFIED] Tier 1 per SDK tiering system

- **MCP-SC-GH-PYSDK** `github.com/modelcontextprotocol/python-sdk`
  - Official Python SDK (Tier 1)
  - PyPI: `mcp`
  - Accessed: 2026-06-12
  - [VERIFIED] Tier 1 per SDK tiering system

### Tier 2: Vendor / Issuer

- **MCP-SC-WIKI-MCP** `en.wikipedia.org/wiki/Model_Context_Protocol`
  - Background, adoption timeline, reception
  - Accessed: 2026-06-12
  - [VERIFIED] Confirms Nov 2024 launch, AAIF donation Dec 2025, OpenAI adoption Mar 2025

- **MCP-SC-CSA-SECBP** `labs.cloudsecurityalliance.org/agentic/agentic-mcp-security-best-practices-v1/`
  - Cloud Security Alliance (CSA): Agentic MCP Security Best Practices Guide
  - Threat landscape: 6 attack categories, 4-level maturity model
  - Accessed: 2026-06-12
  - [VERIFIED] Reports 30+ CVEs in Jan-Feb 2026, covers tool poisoning, rug pulls, session hijacking

### Tier 3: Community / Analyst

- **MCP-SC-WBFUSE-CHEAT** `webfuse.com/mcp-cheat-sheet`
  - MCP Cheat Sheet (2026) - quick reference for architecture, primitives, transports
  - Accessed: 2026-06-12
  - [COMMUNITY] Not yet read in full, identified via search_web

- **MCP-SC-GDEEP-ENTER** `guptadeepak.com/the-complete-guide-to-model-context-protocol-mcp-enterprise-adoption-market-trends-and-implementation-strategies/`
  - Enterprise adoption guide: 97M+ SDK downloads, Block & Bloomberg case studies
  - Accessed: 2026-06-12
  - [COMMUNITY] Not yet read in full, identified via search_web

## Version Timeline (from sources)

- **2024-11-05** (Nov 2024) - Initial release. stdio + HTTP+SSE transports. Tools, resources, prompts, sampling, roots.
- **2025-03-26** (Mar 2025) - Second revision. (Changelog not read; predates 2025-06-18 changelog reference.)
- **2025-06-18** (Jun 2025) - Streamable HTTP replaces HTTP+SSE. Elicitation added. OAuth 2.1 authorization framework. Tool annotations.
- **2025-11-25** (Nov 2025) - Current. Tasks (experimental). URL elicitation. OAuth Client ID metadata docs. Tool name guidance. SDK tiering. Governance formalized.

## Discovery Platforms Tested

- **Google (via Playwright)** - Tested. Yielded spec pages, GitHub repos, changelogs
- **search_web** - Tested. Yielded Wikipedia, CSA guide, community guides
- **modelcontextprotocol.io/llms-full.txt** - Read. 898 chunks - comprehensive single source

## Source Statistics

- **Tier 1 sources**: 7
- **Tier 2 sources**: 2
- **Tier 3 sources**: 2
- **Total sources**: 11
- **Sources read**: 9 (2 Tier 3 sources identified but not fully read)

## Document History

**[2026-06-12 11:00]**
- Added: Accessed dates on all 11 sources (SC-03)
- Changed: Tables converted to lists (QA-07)
- Fixed: CSA acronym expanded on first use (AP-PR-06)

**[2026-06-12 09:30]**
- Initial Sources file created from Phase 1 source collection
- 11 sources across 3 tiers identified and cataloged
- Version timeline verified across 4 spec revisions
