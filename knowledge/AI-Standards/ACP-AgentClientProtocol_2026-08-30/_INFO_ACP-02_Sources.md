# ACP: Source Registry

**Doc ID**: ACP-IN02
**Goal**: Provide a comprehensive, tiered source registry for all ACP documentation
**Version scope**: As of 2026-08-30

## Source Tiers

- **Tier 1**: Official specification, protocol documentation, and governance documents
- **Tier 2**: Official repositories, SDK documentation, blog posts, stabilization announcements
- **Tier 3**: Community analysis, tutorials, and third-party documentation

## Tier 1: Official Specification (v1)

- **ACP-SC-ACPORG-OVRVW**: https://agentclientprotocol.com/protocol/v1/overview
  - Access date: 2026-08-30 | Protocol v1 overview and core concepts
- **ACP-SC-ACPORG-ARCH**: https://agentclientprotocol.com/protocol/v1/architecture
  - Access date: 2026-06-12 | Three-actor model, design philosophy
- **ACP-SC-ACPORG-INIT**: https://agentclientprotocol.com/protocol/v1/initialization
  - Access date: 2026-06-12 | Initialization handshake and capabilities
- **ACP-SC-ACPORG-SSSTP**: https://agentclientprotocol.com/protocol/v1/session-setup
  - Access date: 2026-06-12 | Session creation, MCP server config, workspace roots
- **ACP-SC-ACPORG-PRMPT**: https://agentclientprotocol.com/protocol/v1/prompt
  - Access date: 2026-06-12 | Prompt turn lifecycle
- **ACP-SC-ACPORG-STRMG**: https://agentclientprotocol.com/protocol/v1/streaming
  - Access date: 2026-06-12 | Real-time streaming mechanism
- **ACP-SC-ACPORG-TLCLL**: https://agentclientprotocol.com/protocol/v1/tool-calls
  - Access date: 2026-06-12 | Tool call lifecycle and permission model
- **ACP-SC-ACPORG-AUTH**: https://agentclientprotocol.com/protocol/v1/authentication
  - Access date: 2026-06-12 | Authentication flows
- **ACP-SC-ACPORG-TRNSP**: https://agentclientprotocol.com/protocol/v1/transports
  - Access date: 2026-06-12 | stdio and Streamable HTTP transports
- **ACP-SC-ACPORG-EXTNS**: https://agentclientprotocol.com/protocol/v1/extensibility
  - Access date: 2026-06-12 | Extension mechanisms (_meta, custom methods, capabilities)
- **ACP-SC-ACPORG-CNTNT**: https://agentclientprotocol.com/protocol/v1/content
  - Access date: 2026-06-12 | Content block types
- **ACP-SC-ACPORG-CNCL**: https://agentclientprotocol.com/protocol/v1/cancellation
  - Access date: 2026-08-30 | Request cancellation ($/cancel_request)
- **ACP-SC-ACPORG-ELCTN**: https://agentclientprotocol.com/protocol/v1/elicitation
  - Access date: 2026-08-30 | Structured elicitation (form mode, URL mode)

## Tier 1: Official Specification (v2 Draft)

- **ACP-SC-ACPORG-V2**: https://agentclientprotocol.com/rfds/v2/overview
  - Access date: 2026-08-30 | v2 RFD collection and tracking
- **ACP-SC-ACPORG-V2OVW**: https://agentclientprotocol.com/protocol/v2/overview
  - Access date: 2026-08-30 | v2 protocol documentation
- **ACP-SC-ACPORG-V2MIG**: https://agentclientprotocol.com/protocol/v2/migration
  - Access date: 2026-08-30 | v1 to v2 migration guide

## Tier 1: Ecosystem and Governance

- **ACP-SC-ACPORG-AGNTS**: https://agentclientprotocol.com/get-started/agents
  - Access date: 2026-08-30 | Official agents list
- **ACP-SC-ACPORG-CLNTS**: https://agentclientprotocol.com/get-started/clients
  - Access date: 2026-08-30 | Official clients list
- **ACP-SC-ACPORG-RGSTR**: https://agentclientprotocol.com/get-started/registry
  - Access date: 2026-08-30 | ACP Agent Registry and programmatic API
- **ACP-SC-ACPORG-UPDTS**: https://agentclientprotocol.com/updates
  - Access date: 2026-08-30 | Updates and stabilization announcements
- **ACP-SC-ACPORG-LLMS**: https://agentclientprotocol.com/llms-full.txt
  - Access date: 2026-06-12 | Full documentation index (for LLM consumption)

## Tier 2: Official Repositories

- **ACP-SC-GH-REPO**: https://github.com/agentclientprotocol/agent-client-protocol
  - Access date: 2026-08-30 | Main protocol repository (schema, docs, RFDs)
- **ACP-SC-GH-PYSD**: https://github.com/agentclientprotocol/python-sdk
  - Access date: 2026-08-30 | Python SDK repository (307 stars)
- **ACP-SC-GH-TSSD**: https://github.com/agentclientprotocol/typescript-sdk
  - Access date: 2026-08-30 | TypeScript SDK repository

## Tier 2: SDK Documentation and Packages

- **ACP-SC-PYPI-ACP**: https://pypi.org/project/agent-client-protocol/
  - Access date: 2026-08-30 | Python SDK on PyPI (v0.12.1, Aug 16 2026)
- **ACP-SC-NPM-ACP**: https://www.npmjs.com/package/@agentclientprotocol/sdk
  - Access date: 2026-08-30 | TypeScript SDK on npm (v1.4.0)
- **ACP-SC-PYSD-DOCS**: https://agentclientprotocol.github.io/python-sdk/
  - Access date: 2026-08-30 | Python SDK documentation hub
- **ACP-SC-TSSD-DOCS**: https://agentclientprotocol.github.io/typescript-sdk/
  - Access date: 2026-08-30 | TypeScript SDK API reference (v1.4.0)

## Tier 2: Stabilization Announcements (since 2026-06-12)

- **ACP-SC-ANN-ELCTN**: https://agentclientprotocol.com/announcements/elicitation-stabilized
  - Access date: 2026-08-30 | Elicitation stabilized (July 24, 2026)
- **ACP-SC-ANN-SDK10**: https://agentclientprotocol.com/announcements/sdk-1-0-releases
  - Access date: 2026-08-30 | Rust + TypeScript SDKs reach 1.0 (June 25, 2026)
- **ACP-SC-ACPORG-V2DFT**: https://agentclientprotocol.com/announcements/acp-v2-draft
  - Access date: 2026-08-30 | v2 draft announcement (July 20, 2026)
- **ACP-SC-ANN-RQCNL**: https://agentclientprotocol.com/announcements/request-cancellation-stabilized
  - Access date: 2026-08-30 | Request cancellation stabilized (June 29, 2026)
- **ACP-SC-ANN-MSGID**: https://agentclientprotocol.com/announcements/message-id-stabilized
  - Access date: 2026-08-30 | Message IDs stabilized
- **ACP-SC-ANN-BOOLC**: https://agentclientprotocol.com/announcements/boolean-config-option-stabilized
  - Access date: 2026-08-30 | Boolean config options stabilized
- **ACP-SC-ANN-MDLCF**: https://agentclientprotocol.com/announcements/model-config-category-stabilized
  - Access date: 2026-08-30 | Model config category stabilized
- **ACP-SC-ANN-USAGE**: https://agentclientprotocol.com/announcements/session-usage-stabilized
  - Access date: 2026-08-30 | Session usage updates stabilized
- **ACP-SC-ANN-SSDEL**: https://agentclientprotocol.com/announcements/session-delete-stabilized
  - Access date: 2026-08-30 | Session delete stabilized

## Tier 3: Community Analysis and Tutorials

- **ACP-SC-MRCNR-INTRO**: Marc Nearon's ACP introduction and ecosystem analysis
  - Access date: 2026-06-12 | Ecosystem overview, adapter details, acronym disambiguation
- **ACP-SC-MRPH-EXPL**: Morph LLM's ACP explainer with SDK examples
  - Access date: 2026-06-12 | FAQ, VS Code status, Python/TypeScript examples
- **ACP-SC-AISDK-PRVDR**: AI SDK community ACP provider documentation
  - Access date: 2026-06-12 | @mcpc/acp-ai-provider integration
- **ACP-SC-DPWK-V2**: https://deepwiki.com/agentclientprotocol/agent-client-protocol/3-protocol-specification-v2-(draft)
  - Access date: 2026-08-30 | DeepWiki v2 protocol analysis (indexed Aug 20, 2026)

## Document History

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: Tier 1 v2 sources (V2OVW, V2MIG, V2DFT, CNCL, ELCTN)
- Added: Tier 2 SDK documentation sources (PYPI, NPM, PYSD-DOCS, TSSD-DOCS, GH-PYSD, GH-TSSD)
- Added: Tier 2 stabilization announcement sources (8 new announcements)
- Added: Tier 3 DeepWiki v2 analysis
- Restructured: Separated v1 spec, v2 spec, ecosystem/governance into distinct Tier 1 sections
- Updated: Access dates for re-verified sources

**[2026-06-12 09:00]**
- Initial source registry created
