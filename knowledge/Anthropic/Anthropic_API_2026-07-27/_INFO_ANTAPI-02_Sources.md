# Anthropic API - Sources

**Doc ID**: ANTAPI-IN02
**Goal**: Master source index for all Anthropic API documentation
**Version scope**: API v1, anthropic-version 2023-06-01, Documentation date 2026-03-20
**Preflight accuracy**: [pending - to be filled after P1-S5]

## Pre-Research Assumptions

1. [VERIFIED] Base URL is `https://api.anthropic.com/v1/` (ANTAPI-SC-ANTH-APIOVW)
2. [VERIFIED] Authentication via `x-api-key` header (ANTAPI-SC-ANTH-APIOVW)
3. [VERIFIED] API versioning via `anthropic-version` header, current value `2023-06-01` (ANTAPI-SC-ANTH-APIOVW)
4. [VERIFIED] Primary endpoint is `POST /v1/messages` for all text generation (ANTAPI-SC-ANTH-APIOVW)
5. [ASSUMED] Streaming uses Server-Sent Events (SSE) with `stream: true`
6. [ASSUMED] Tool use supports sequential calls only (not parallel like OpenAI) - SDK shows DirectCaller + ServerToolCaller, needs deeper verification
7. [VERIFIED] System prompt is a separate `system` parameter, not in messages array (ANTAPI-SC-ANTH-MSGCRT)
8. **[PARTIAL]** Messages alternate user/assistant - but consecutive same-role turns are auto-combined, not rejected (ANTAPI-SC-ANTH-MSGCRT)
9. [ASSUMED] Extended thinking adds `thinking` blocks to response content
10. [VERIFIED] Prompt caching uses `cache_control` parameter with TTL 5m/1h (ANTAPI-SC-ANTH-MSGCRT)

**Preflight accuracy**: 5/10 verified, 1/10 partial, 4/10 still assumed = 60% verified (above 30% wrong threshold, no re-run needed)

## Official Documentation (Tier 1)

### API Reference

- `ANTAPI-SC-ANTH-APIOVW` - https://platform.claude.com/docs/en/api/overview - API Overview
- `ANTAPI-SC-ANTH-BETAHDR` - https://platform.claude.com/docs/en/api/beta-headers - Beta Headers
- `ANTAPI-SC-ANTH-ERRORS` - https://platform.claude.com/docs/en/api/errors - Errors
- `ANTAPI-SC-ANTH-SDKOVW` - https://platform.claude.com/docs/en/api/client-sdks - Client SDKs Overview
- `ANTAPI-SC-ANTH-SDKPY` - https://platform.claude.com/docs/en/api/sdks/python - Python SDK
- `ANTAPI-SC-ANTH-SDKTS` - https://platform.claude.com/docs/en/api/sdks/typescript - TypeScript SDK
- `ANTAPI-SC-ANTH-SDKJAVA` - https://platform.claude.com/docs/en/api/sdks/java - Java SDK
- `ANTAPI-SC-ANTH-SDKGO` - https://platform.claude.com/docs/en/api/sdks/go - Go SDK
- `ANTAPI-SC-ANTH-MSGCRT` - https://platform.claude.com/docs/en/api/messages/create - Create a Message
- `ANTAPI-SC-ANTH-MSGCNT` - https://platform.claude.com/docs/en/api/messages/count_tokens - Count Tokens
- `ANTAPI-SC-ANTH-BTCHCRT` - https://platform.claude.com/docs/en/api/messages/batches/create - Create Message Batch
- `ANTAPI-SC-ANTH-BTCHGET` - https://platform.claude.com/docs/en/api/messages/batches/retrieve - Retrieve Message Batch
- `ANTAPI-SC-ANTH-BTCHLST` - https://platform.claude.com/docs/en/api/messages/batches/list - List Message Batches
- `ANTAPI-SC-ANTH-BTCHCNL` - https://platform.claude.com/docs/en/api/messages/batches/cancel - Cancel Message Batch
- `ANTAPI-SC-ANTH-BTCHDEL` - https://platform.claude.com/docs/en/api/messages/batches/delete - Delete Message Batch
- `ANTAPI-SC-ANTH-BTCHRES` - https://platform.claude.com/docs/en/api/messages/batches/results - Retrieve Batch Results
- `ANTAPI-SC-ANTH-MODLST` - https://platform.claude.com/docs/en/api/models/list - List Models
- `ANTAPI-SC-ANTH-MODGET` - https://platform.claude.com/docs/en/api/models/retrieve - Get a Model
- `ANTAPI-SC-ANTH-BETA` - https://platform.claude.com/docs/en/api/beta - Beta API
- `ANTAPI-SC-ANTH-BFILUP` - https://platform.claude.com/docs/en/api/beta/files/upload - Upload File (beta)
- `ANTAPI-SC-ANTH-BFILLST` - https://platform.claude.com/docs/en/api/beta/files/list - List Files (beta)
- `ANTAPI-SC-ANTH-BFILDL` - https://platform.claude.com/docs/en/api/beta/files/download - Download File (beta)
- `ANTAPI-SC-ANTH-BFILMET` - https://platform.claude.com/docs/en/api/beta/files/retrieve_metadata - File Metadata (beta)
- `ANTAPI-SC-ANTH-BFILDEL` - https://platform.claude.com/docs/en/api/beta/files/delete - Delete File (beta)
- `ANTAPI-SC-ANTH-BSKLCRT` - https://platform.claude.com/docs/en/api/beta/skills/create - Create Skill (beta)
- `ANTAPI-SC-ANTH-BSKLLST` - https://platform.claude.com/docs/en/api/beta/skills/list - List Skills (beta)
- `ANTAPI-SC-ANTH-BSKLGET` - https://platform.claude.com/docs/en/api/beta/skills/retrieve - Get Skill (beta)
- `ANTAPI-SC-ANTH-BSKLDEL` - https://platform.claude.com/docs/en/api/beta/skills/delete - Delete Skill (beta)
- `ANTAPI-SC-ANTH-ADMORG` - https://platform.claude.com/docs/en/api/admin/organizations/me - Get Current Organization
- `ANTAPI-SC-ANTH-ADMIVCRT` - https://platform.claude.com/docs/en/api/admin/invites/create - Create Invite
- `ANTAPI-SC-ANTH-ADMIVGET` - https://platform.claude.com/docs/en/api/admin/invites/retrieve - Get Invite
- `ANTAPI-SC-ANTH-ADMIVLST` - https://platform.claude.com/docs/en/api/admin/invites/list - List Invites
- `ANTAPI-SC-ANTH-ADMIVDEL` - https://platform.claude.com/docs/en/api/admin/invites/delete - Delete Invite
- `ANTAPI-SC-ANTH-ADMUSRGET` - https://platform.claude.com/docs/en/api/admin/users/retrieve - Get User
- `ANTAPI-SC-ANTH-ADMUSRLST` - https://platform.claude.com/docs/en/api/admin/users/list - List Users
- `ANTAPI-SC-ANTH-ADMUSRUPD` - https://platform.claude.com/docs/en/api/admin/users/update - Update User
- `ANTAPI-SC-ANTH-ADMUSRDEL` - https://platform.claude.com/docs/en/api/admin/users/delete - Remove User
- `ANTAPI-SC-ANTH-ADMWSCRT` - https://platform.claude.com/docs/en/api/admin/workspaces/create - Create Workspace
- `ANTAPI-SC-ANTH-ADMWSGET` - https://platform.claude.com/docs/en/api/admin/workspaces/retrieve - Get Workspace
- `ANTAPI-SC-ANTH-ADMWSLST` - https://platform.claude.com/docs/en/api/admin/workspaces/list - List Workspaces
- `ANTAPI-SC-ANTH-ADMWSUPD` - https://platform.claude.com/docs/en/api/admin/workspaces/update - Update Workspace
- `ANTAPI-SC-ANTH-ADMWSARC` - https://platform.claude.com/docs/en/api/admin/workspaces/archive - Archive Workspace
- `ANTAPI-SC-ANTH-ADMKEGET` - https://platform.claude.com/docs/en/api/admin/api_keys/retrieve - Get API Key
- `ANTAPI-SC-ANTH-ADMKELST` - https://platform.claude.com/docs/en/api/admin/api_keys/list - List API Keys
- `ANTAPI-SC-ANTH-ADMKEUPD` - https://platform.claude.com/docs/en/api/admin/api_keys/update - Update API Key
- `ANTAPI-SC-ANTH-ADMUSGMSG` - https://platform.claude.com/docs/en/api/admin/usage_report/retrieve_messages - Messages Usage Report
- `ANTAPI-SC-ANTH-ADMUSGCC` - https://platform.claude.com/docs/en/api/admin/usage_report/retrieve_claude_code - Claude Code Usage Report
- `ANTAPI-SC-ANTH-ADMCOST` - https://platform.claude.com/docs/en/api/admin/cost_report/retrieve - Cost Report
- `ANTAPI-SC-ANTH-COMPLCRT` - https://platform.claude.com/docs/en/api/completions/create - Create Text Completion (legacy)
- `ANTAPI-SC-ANTH-RATELIM` - https://platform.claude.com/docs/en/api/rate-limits - Rate Limits
- `ANTAPI-SC-ANTH-SVCTIER` - https://platform.claude.com/docs/en/api/service-tiers - Service Tiers
- `ANTAPI-SC-ANTH-VERSION` - https://platform.claude.com/docs/en/api/versioning - Versions
- `ANTAPI-SC-ANTH-IPADDR` - https://platform.claude.com/docs/en/api/ip-addresses - IP Addresses
- `ANTAPI-SC-ANTH-REGIONS` - https://platform.claude.com/docs/en/api/supported-regions - Supported Regions
- `ANTAPI-SC-ANTH-OAISDK` - https://platform.claude.com/docs/en/api/openai-sdk - OpenAI SDK Compatibility

### Developer Guide (Feature Documentation)

- `ANTAPI-SC-ANTH-INTRO` - https://platform.claude.com/docs/en/intro - Intro to Claude
- `ANTAPI-SC-ANTH-QKSTART` - https://platform.claude.com/docs/en/get-started - Quickstart
- `ANTAPI-SC-ANTH-MODOVW` - https://platform.claude.com/docs/en/about-claude/models/overview - Models Overview
- `ANTAPI-SC-ANTH-MODCHSE` - https://platform.claude.com/docs/en/about-claude/models/choosing-a-model - Choosing a Model
- `ANTAPI-SC-ANTH-MODDEP` - https://platform.claude.com/docs/en/about-claude/model-deprecations - Model Deprecations
- `ANTAPI-SC-ANTH-PRICING` - https://platform.claude.com/docs/en/about-claude/pricing - Pricing
- `ANTAPI-SC-ANTH-FEATOVW` - https://platform.claude.com/docs/en/build-with-claude/overview - Features Overview
- `ANTAPI-SC-ANTH-MSGGUIDE` - https://platform.claude.com/docs/en/build-with-claude/working-with-messages - Using the Messages API
- `ANTAPI-SC-ANTH-STOPREASON` - https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons - Handling Stop Reasons
- `ANTAPI-SC-ANTH-EXTTHINK` - https://platform.claude.com/docs/en/build-with-claude/extended-thinking - Extended Thinking
- `ANTAPI-SC-ANTH-ADAPTIVE` - https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking - Adaptive Thinking
- `ANTAPI-SC-ANTH-EFFORT` - https://platform.claude.com/docs/en/build-with-claude/effort - Effort
- `ANTAPI-SC-ANTH-FASTMODE` - https://platform.claude.com/docs/en/build-with-claude/fast-mode - Fast Mode (beta)
- `ANTAPI-SC-ANTH-STRUCTOUT` - https://platform.claude.com/docs/en/build-with-claude/structured-outputs - Structured Outputs
- `ANTAPI-SC-ANTH-CITATIONS` - https://platform.claude.com/docs/en/build-with-claude/citations - Citations
- `ANTAPI-SC-ANTH-STREAM` - https://platform.claude.com/docs/en/build-with-claude/streaming - Streaming Messages
- `ANTAPI-SC-ANTH-BATCH` - https://platform.claude.com/docs/en/build-with-claude/batch-processing - Batch Processing
- `ANTAPI-SC-ANTH-PDF` - https://platform.claude.com/docs/en/build-with-claude/pdf-support - PDF Support
- `ANTAPI-SC-ANTH-SEARCH` - https://platform.claude.com/docs/en/build-with-claude/search-results - Search Results
- `ANTAPI-SC-ANTH-VISION` - https://platform.claude.com/docs/en/build-with-claude/vision - Vision
- `ANTAPI-SC-ANTH-EMBED` - https://platform.claude.com/docs/en/build-with-claude/embeddings - Embeddings
- `ANTAPI-SC-ANTH-CTXWIN` - https://platform.claude.com/docs/en/build-with-claude/context-windows - Context Windows
- `ANTAPI-SC-ANTH-COMPACT` - https://platform.claude.com/docs/en/build-with-claude/compaction - Compaction
- `ANTAPI-SC-ANTH-CTXEDIT` - https://platform.claude.com/docs/en/build-with-claude/context-editing - Context Editing
- `ANTAPI-SC-ANTH-CACHE` - https://platform.claude.com/docs/en/build-with-claude/prompt-caching - Prompt Caching
- `ANTAPI-SC-ANTH-TOKCNT` - https://platform.claude.com/docs/en/build-with-claude/token-counting - Token Counting
- `ANTAPI-SC-ANTH-FILES` - https://platform.claude.com/docs/en/build-with-claude/files - Files API Guide

### Tools Documentation

- `ANTAPI-SC-ANTH-TOOLOVW` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview - Tool Use Overview
- `ANTAPI-SC-ANTH-TOOLIMPL` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use - How to Implement Tool Use
- `ANTAPI-SC-ANTH-TOOLWEB` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool - Web Search Tool
- `ANTAPI-SC-ANTH-TOOLFETCH` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool - Web Fetch Tool
- `ANTAPI-SC-ANTH-TOOLCODE` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool - Code Execution Tool
- `ANTAPI-SC-ANTH-TOOLMEM` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool - Memory Tool
- `ANTAPI-SC-ANTH-TOOLBASH` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool - Bash Tool
- `ANTAPI-SC-ANTH-TOOLCOMP` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool - Computer Use Tool
- `ANTAPI-SC-ANTH-TOOLTEXT` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool - Text Editor Tool
- `ANTAPI-SC-ANTH-TOOLSRCH` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool - Tool Search
- `ANTAPI-SC-ANTH-TOOLPROG` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling - Programmatic Tool Calling
- `ANTAPI-SC-ANTH-TOOLSTRM` - https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming - Fine-grained Tool Streaming

### Agent Skills and SDK

- `ANTAPI-SC-ANTH-AGSKOVW` - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview - Agent Skills Overview
- `ANTAPI-SC-ANTH-AGSKQS` - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart - Agent Skills Quickstart
- `ANTAPI-SC-ANTH-AGSKAPI` - https://platform.claude.com/docs/en/build-with-claude/skills-guide - Using Skills with the API
- `ANTAPI-SC-ANTH-AGSDKOVW` - https://platform.claude.com/docs/en/agent-sdk/overview - Agent SDK Overview

## Vendor/Issuer Content (Tier 2)

- `ANTAPI-SC-GH-SDKPY` - https://github.com/anthropics/anthropic-sdk-python - Python SDK Repository
- `ANTAPI-SC-GH-SDKAPI` - https://github.com/anthropics/anthropic-sdk-python/blob/main/api.md - SDK API Reference (types and methods)
- `ANTAPI-SC-GH-AGENTSDK` - https://github.com/anthropics/claude-agent-sdk-python - Agent SDK Repository
- `ANTAPI-SC-ANTH-RELNOTES` - https://platform.claude.com/docs/en/release-notes/overview - Release Notes

## Community/Analyst Sources (Tier 3)

- `ANTAPI-SC-EESEL-COMPARE` - https://www.eesel.ai/blog/openai-api-vs-anthropic-api - OpenAI vs Anthropic API Comparison [COMMUNITY]
- `ANTAPI-SC-SO-RATELIMIT` - https://stackoverflow.com/questions/79590591 - Rate Limit Exceeded [COMMUNITY]
- `ANTAPI-SC-SO-BETAFLAG` - https://stackoverflow.com/questions/79632861 - Invalid Beta Flag Error [COMMUNITY]

## Related APIs/Technologies

- **OpenAI API** - https://platform.openai.com/docs - Primary competitor, similar REST API structure
- **Google Gemini API** - https://ai.google.dev/docs - Google's competing LLM API
- **Amazon Bedrock** - https://docs.aws.amazon.com/bedrock/ - AWS-hosted Claude access
- **Google Vertex AI** - https://cloud.google.com/vertex-ai/docs - GCP-hosted Claude access

## New Sources (2026-05-22 Update)

### Tier 1 - Official Documentation

- ANTAPI-SC-ANTH-MAOVW - https://platform.claude.com/docs/en/managed-agents/overview - Managed Agents overview
- ANTAPI-SC-ANTH-MAQS - https://platform.claude.com/docs/en/managed-agents/quickstart - Managed Agents quickstart
- ANTAPI-SC-ANTH-MATOOL - https://platform.claude.com/docs/en/managed-agents/tools - Managed Agents tools
- ANTAPI-SC-ANTH-MASESS - https://platform.claude.com/docs/en/managed-agents/sessions - Managed Agents sessions API
- ANTAPI-SC-ANTH-ADVSR - https://platform.claude.com/docs/en/build-with-claude/advisor - Advisor tool
- ANTAPI-SC-ANTH-CACHDIAG - https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics - Cache diagnostics
- ANTAPI-SC-ANTH-CPAWS - https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws - Claude Platform on AWS
- ANTAPI-SC-ANTH-BEDRM - https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock - Bedrock Messages API
- ANTAPI-SC-ANTH-MCPTNL - https://platform.claude.com/docs/en/managed-agents/mcp-tunnels - MCP tunnels
- ANTAPI-SC-ANTH-CLI - https://platform.claude.com/docs/en/api/sdks/cli - ant CLI
- ANTAPI-SC-ANTH-RLNTS - https://platform.claude.com/docs/en/about-claude/release-notes - Release notes
- ANTAPI-SC-ANTH-RTLMTAPI - https://platform.claude.com/docs/en/api/rate-limits - Rate Limits API

## Source Statistics

- **Total sources**: 101 (89 from 2026-03-20 + 12 new)
- **Tier 1 (Official)**: 95
- **Tier 2 (Vendor)**: 4
- **Tier 3 (Community)**: 3
- **Original access**: 2026-03-20
- **Updated access**: 2026-05-22

## Document History

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Added: 12 new Tier 1 sources for new topics (Managed Agents, Advisor, Cache Diagnostics, Platform on AWS, MCP Tunnels, CLI, Release Notes)
- Changed: Source statistics updated (89 -> 101 total)

**[2026-03-20 01:55]**
- Initial source collection from API Reference sidebar and Developer Guide sidebar
- 10 pre-research assumptions documented
- Discovery platforms tested and classified
