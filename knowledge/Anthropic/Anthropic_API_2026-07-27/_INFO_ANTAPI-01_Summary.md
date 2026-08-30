# Anthropic API - Table of Contents

**Doc ID**: ANTAPI-IN01
**Goal**: Master index for all Anthropic API documentation files
**Version scope**: API v1, anthropic-version 2023-06-01, Documentation date 2026-07-27
**Research stats**: 49 topics, 51 INFO files, 13 categories, 95+ sources collected, Python + TypeScript examples
**Updated from**: Anthropic_API_2026-07-26 (47 topics)

**Depends on:**
- `_INFO_ANTAPI-02_Sources.md [ANTAPI-IN02]` for source references

## Summary

The Anthropic API is a RESTful API at `https://api.anthropic.com` providing programmatic access to Claude models (Opus 5, Fable 5, Mythos 5, Sonnet 5, Opus 4.8, and legacy models). The primary interface is the Messages API (`POST /v1/messages`) for conversational interactions supporting text, images, PDFs, and tool use. Authentication uses the `x-api-key` header (with optional expiration) and API versioning via `anthropic-version: 2023-06-01`. The API supports streaming via SSE, prompt caching with configurable TTL (5m/1h), extended thinking with effort levels (low/medium/high/xhigh/max), adaptive thinking, and structured outputs. Built-in tools include web search, web fetch, code execution, computer use, bash, text editor, and memory. The Message Batches API offers 50% cost reduction for async bulk processing. New features since May 2026 include: refusal stop_details with categories, server-side fallbacks (beta), mid-conversation system messages, agent memory stores (beta), mid-conversation tool changes (beta), and Dreams (research preview). Rate limits use three tiers (Start/Build/Scale) with unified limits across Opus/Sonnet/Haiku. Claude Platform on AWS provides Anthropic-managed infrastructure with AWS billing. Admin APIs manage organizations, workspaces, users, invites, API keys, and rate limits. Official SDKs exist for Python (0.120.0), TypeScript, Java, Go, C#, Ruby, PHP, Swift (beta), and the `ant` CLI.

## Topic Files

### Core API (5 files)

- [`_INFO_ANTAPI-03_INTRODUCTION.md`](./_INFO_ANTAPI-03_INTRODUCTION.md) [ANTAPI-IN03]
  - API overview, base URL, protocol, content type, request/response format
  - Sources: ANTAPI-SC-ANTH-APIOVW, ANTAPI-SC-ANTH-INTRO

- [`_INFO_ANTAPI-04_AUTHENTICATION.md`](./_INFO_ANTAPI-04_AUTHENTICATION.md) [ANTAPI-IN04]
  - API keys, x-api-key header, workspaces, console setup
  - Sources: ANTAPI-SC-ANTH-APIOVW, ANTAPI-SC-ANTH-QKSTART

- [`_INFO_ANTAPI-05_VERSIONING.md`](./_INFO_ANTAPI-05_VERSIONING.md) [ANTAPI-IN05]
  - API versions, anthropic-version header, beta headers, changelog
  - Sources: ANTAPI-SC-ANTH-VERSION, ANTAPI-SC-ANTH-BETAHDR

- [`_INFO_ANTAPI-06_ERRORS.md`](./_INFO_ANTAPI-06_ERRORS.md) [ANTAPI-IN06]
  - HTTP status codes, error types, error response format, retry strategies
  - Sources: ANTAPI-SC-ANTH-ERRORS

- [`_INFO_ANTAPI-07_SDKS.md`](./_INFO_ANTAPI-07_SDKS.md) [ANTAPI-IN07]
  - Python SDK installation, configuration, usage patterns, other SDKs overview
  - Sources: ANTAPI-SC-ANTH-SDKOVW, ANTAPI-SC-ANTH-SDKPY, ANTAPI-SC-GH-SDKPY

### Messages API (5 files)

- [`_INFO_ANTAPI-08_MESSAGES.md`](./_INFO_ANTAPI-08_MESSAGES.md) [ANTAPI-IN08]
  - POST /v1/messages - full request/response schema, parameters, content blocks
  - Sources: ANTAPI-SC-ANTH-MSGCRT, ANTAPI-SC-ANTH-MSGGUIDE

- [`_INFO_ANTAPI-09_STREAMING.md`](./_INFO_ANTAPI-09_STREAMING.md) [ANTAPI-IN09]
  - SSE streaming, event types, stream manager, partial responses
  - Sources: ANTAPI-SC-ANTH-STREAM

- [`_INFO_ANTAPI-10_TOKEN_COUNTING.md`](./_INFO_ANTAPI-10_TOKEN_COUNTING.md) [ANTAPI-IN10]
  - POST /v1/messages/count_tokens - request/response, cost estimation
  - Sources: ANTAPI-SC-ANTH-MSGCNT, ANTAPI-SC-ANTH-TOKCNT

- [`_INFO_ANTAPI-11_STOP_REASONS.md`](./_INFO_ANTAPI-11_STOP_REASONS.md) [ANTAPI-IN11]
  - Stop reason types, handling end_turn, max_tokens, stop_sequence, tool_use
  - Sources: ANTAPI-SC-ANTH-STOPREASON

- [`_INFO_ANTAPI-12_BATCHES.md`](./_INFO_ANTAPI-12_BATCHES.md) [ANTAPI-IN12]
  - Message Batches API - create, retrieve, list, cancel, delete, results
  - Sources: ANTAPI-SC-ANTH-BTCHCRT, ANTAPI-SC-ANTH-BTCHLST, ANTAPI-SC-ANTH-BATCH

### Models (2 files)

- [`_INFO_ANTAPI-13_MODELS.md`](./_INFO_ANTAPI-13_MODELS.md) [ANTAPI-IN13]
  - GET /v1/models, GET /v1/models/{id} - model list, capabilities, info
  - Sources: ANTAPI-SC-ANTH-MODLST, ANTAPI-SC-ANTH-MODGET, ANTAPI-SC-ANTH-MODOVW

- [`_INFO_ANTAPI-14_PRICING.md`](./_INFO_ANTAPI-14_PRICING.md) [ANTAPI-IN14]
  - Model pricing, token costs, choosing a model, deprecations
  - Sources: ANTAPI-SC-ANTH-PRICING, ANTAPI-SC-ANTH-MODCHSE, ANTAPI-SC-ANTH-MODDEP

### Model Capabilities (8 files)

- [`_INFO_ANTAPI-15_EXTENDED_THINKING.md`](./_INFO_ANTAPI-15_EXTENDED_THINKING.md) [ANTAPI-IN15]
  - Extended thinking, adaptive thinking, effort parameter, thinking blocks
  - Sources: ANTAPI-SC-ANTH-EXTTHINK, ANTAPI-SC-ANTH-ADAPTIVE, ANTAPI-SC-ANTH-EFFORT

- [`_INFO_ANTAPI-16_STRUCTURED_OUTPUTS.md`](./_INFO_ANTAPI-16_STRUCTURED_OUTPUTS.md) [ANTAPI-IN16]
  - JSON mode, constrained outputs, output schemas
  - Sources: ANTAPI-SC-ANTH-STRUCTOUT

- [`_INFO_ANTAPI-17_CITATIONS.md`](./_INFO_ANTAPI-17_CITATIONS.md) [ANTAPI-IN17]
  - Source attribution, citation types (char, page, content block, web search)
  - Sources: ANTAPI-SC-ANTH-CITATIONS

- [`_INFO_ANTAPI-18_VISION.md`](./_INFO_ANTAPI-18_VISION.md) [ANTAPI-IN18]
  - Image inputs (base64, URL), supported formats, image processing
  - Sources: ANTAPI-SC-ANTH-VISION

- [`_INFO_ANTAPI-19_PDF_SUPPORT.md`](./_INFO_ANTAPI-19_PDF_SUPPORT.md) [ANTAPI-IN19]
  - PDF inputs (base64, URL), document blocks, page limits
  - Sources: ANTAPI-SC-ANTH-PDF

- [`_INFO_ANTAPI-20_PROMPT_CACHING.md`](./_INFO_ANTAPI-20_PROMPT_CACHING.md) [ANTAPI-IN20]
  - cache_control parameter, TTL (5m/1h), cost savings, cache usage
  - Sources: ANTAPI-SC-ANTH-CACHE

- [`_INFO_ANTAPI-21_CONTEXT_MANAGEMENT.md`](./_INFO_ANTAPI-21_CONTEXT_MANAGEMENT.md) [ANTAPI-IN21]
  - Context windows, compaction, context editing, token limits
  - Sources: ANTAPI-SC-ANTH-CTXWIN, ANTAPI-SC-ANTH-COMPACT, ANTAPI-SC-ANTH-CTXEDIT

- [`_INFO_ANTAPI-22_SEARCH.md`](./_INFO_ANTAPI-22_SEARCH.md) [ANTAPI-IN22]
  - Search results content blocks, embeddings guidance
  - Sources: ANTAPI-SC-ANTH-SEARCH, ANTAPI-SC-ANTH-EMBED

### Tools (7 files)

- [`_INFO_ANTAPI-23_TOOL_USE.md`](./_INFO_ANTAPI-23_TOOL_USE.md) [ANTAPI-IN23]
  - Tool use overview, implementing tool use, tool schemas, tool_choice
  - Sources: ANTAPI-SC-ANTH-TOOLOVW, ANTAPI-SC-ANTH-TOOLIMPL

- [`_INFO_ANTAPI-24_WEB_TOOLS.md`](./_INFO_ANTAPI-24_WEB_TOOLS.md) [ANTAPI-IN24]
  - Web search tool, web fetch tool, server-side tools
  - Sources: ANTAPI-SC-ANTH-TOOLWEB, ANTAPI-SC-ANTH-TOOLFETCH

- [`_INFO_ANTAPI-25_CODE_EXECUTION.md`](./_INFO_ANTAPI-25_CODE_EXECUTION.md) [ANTAPI-IN25]
  - Code execution tool, sandboxed environment, result blocks
  - Sources: ANTAPI-SC-ANTH-TOOLCODE

- [`_INFO_ANTAPI-26_COMPUTER_USE.md`](./_INFO_ANTAPI-26_COMPUTER_USE.md) [ANTAPI-IN26]
  - Computer use tool, bash tool, text editor tool
  - Sources: ANTAPI-SC-ANTH-TOOLCOMP, ANTAPI-SC-ANTH-TOOLBASH, ANTAPI-SC-ANTH-TOOLTEXT

- [`_INFO_ANTAPI-27_MEMORY_TOOL.md`](./_INFO_ANTAPI-27_MEMORY_TOOL.md) [ANTAPI-IN27]
  - Memory tool for persistent context across conversations
  - Sources: ANTAPI-SC-ANTH-TOOLMEM

- [`_INFO_ANTAPI-28_TOOL_INFRASTRUCTURE.md`](./_INFO_ANTAPI-28_TOOL_INFRASTRUCTURE.md) [ANTAPI-IN28]
  - Tool search, programmatic tool calling, fine-grained tool streaming
  - Sources: ANTAPI-SC-ANTH-TOOLSRCH, ANTAPI-SC-ANTH-TOOLPROG, ANTAPI-SC-ANTH-TOOLSTRM

- [`_INFO_ANTAPI-29_TOOL_STREAMING.md`](./_INFO_ANTAPI-29_TOOL_STREAMING.md) [ANTAPI-IN29]
  - Fine-grained streaming with tool use, partial JSON, event handling
  - Sources: ANTAPI-SC-ANTH-TOOLSTRM

### Files and Skills - Beta (2 files)

- [`_INFO_ANTAPI-30_FILES_API.md`](./_INFO_ANTAPI-30_FILES_API.md) [ANTAPI-IN30]
  - Files API (beta) - upload, list, download, metadata, delete
  - Sources: ANTAPI-SC-ANTH-BFILUP, ANTAPI-SC-ANTH-BFILLST, ANTAPI-SC-ANTH-FILES

- [`_INFO_ANTAPI-31_SKILLS_API.md`](./_INFO_ANTAPI-31_SKILLS_API.md) [ANTAPI-IN31]
  - Agent Skills API (beta) - create, list, get, delete, versions
  - Sources: ANTAPI-SC-ANTH-BSKLCRT, ANTAPI-SC-ANTH-AGSKOVW, ANTAPI-SC-ANTH-AGSKAPI

### Admin API (4 files)

- [`_INFO_ANTAPI-32_ADMIN_ORGS.md`](./_INFO_ANTAPI-32_ADMIN_ORGS.md) [ANTAPI-IN32]
  - Organizations - get current org; Invites - create, get, list, delete
  - Sources: ANTAPI-SC-ANTH-ADMORG, ANTAPI-SC-ANTH-ADMIVCRT, ANTAPI-SC-ANTH-ADMIVLST

- [`_INFO_ANTAPI-33_ADMIN_USERS.md`](./_INFO_ANTAPI-33_ADMIN_USERS.md) [ANTAPI-IN33]
  - Users - get, list, update, remove
  - Sources: ANTAPI-SC-ANTH-ADMUSRGET, ANTAPI-SC-ANTH-ADMUSRLST

- [`_INFO_ANTAPI-34_ADMIN_WORKSPACES.md`](./_INFO_ANTAPI-34_ADMIN_WORKSPACES.md) [ANTAPI-IN34]
  - Workspaces - create, get, list, update, archive, members; API Keys - get, list, update
  - Sources: ANTAPI-SC-ANTH-ADMWSCRT, ANTAPI-SC-ANTH-ADMKELST

- [`_INFO_ANTAPI-35_USAGE_API.md`](./_INFO_ANTAPI-35_USAGE_API.md) [ANTAPI-IN35]
  - Usage reports (messages, Claude Code), token consumption and cost tracking
  - Sources: ANTAPI-SC-ANTH-ADMIN

### Support and Configuration (4 files)

- [`_INFO_ANTAPI-36_RATE_LIMITS.md`](./_INFO_ANTAPI-36_RATE_LIMITS.md) [ANTAPI-IN36]
  - Rate limits (RPM, TPM), tiers, headers, retry strategies
  - Sources: ANTAPI-SC-ANTH-RTLMT

- [`_INFO_ANTAPI-37_DATA_RESIDENCY.md`](./_INFO_ANTAPI-37_DATA_RESIDENCY.md) [ANTAPI-IN37]
  - Data residency, inference_geo parameter, regional routing, US-only inference
  - Sources: ANTAPI-SC-ANTH-DATARES, ANTAPI-SC-ANTH-PRICING

- [`_INFO_ANTAPI-38_PLATFORM_COMPAT.md`](./_INFO_ANTAPI-38_PLATFORM_COMPAT.md) [ANTAPI-IN38]
  - Platform compatibility: AWS Bedrock, Google Vertex AI, Microsoft Foundry
  - Sources: ANTAPI-SC-ANTH-BEDROCK, ANTAPI-SC-ANTH-VERTEX, ANTAPI-SC-ANTH-FOUNDRY

- [`_INFO_ANTAPI-39_LEGACY.md`](./_INFO_ANTAPI-39_LEGACY.md) [ANTAPI-IN39]
  - Legacy APIs, model deprecations, Text Completions migration, Workbench sunset
  - Sources: ANTAPI-SC-ANTH-DEPR, ANTAPI-SC-ANTH-LEGACY

### Managed Agents and Agent Features (4 files)

- [`_INFO_ANTAPI-40_MANAGED_AGENTS.md`](./_INFO_ANTAPI-40_MANAGED_AGENTS.md) [ANTAPI-IN40]
  - Claude Managed Agents - agents, environments, sessions, events, Dreams
  - Sources: ANTAPI-SC-ANTH-MAOVW, ANTAPI-SC-ANTH-MAQS, ANTAPI-SC-ANTH-MATOOL

- [`_INFO_ANTAPI-41_ADVISOR_TOOL.md`](./_INFO_ANTAPI-41_ADVISOR_TOOL.md) [ANTAPI-IN41]
  - Advisor tool (beta) - executor/advisor model pairing, max_tokens on advisor
  - Sources: ANTAPI-SC-ANTH-ADVSR

- [`_INFO_ANTAPI-45_MCP_TUNNELS.md`](./_INFO_ANTAPI-45_MCP_TUNNELS.md) [ANTAPI-IN45]
  - MCP tunnels (research preview) - private MCP server access from managed agents
  - Sources: ANTAPI-SC-ANTH-MCPTNL

- [`_INFO_ANTAPI-49_AGENT_MEMORY_STORES.md`](./_INFO_ANTAPI-49_AGENT_MEMORY_STORES.md) [ANTAPI-IN49]
  - Agent memory stores (beta) - persistent memory CRUD for managed agents
  - Sources: ANTAPI-SC-ANTH-AGMEM

### Diagnostics and Operational (3 files)

- [`_INFO_ANTAPI-42_CACHE_DIAGNOSTICS.md`](./_INFO_ANTAPI-42_CACHE_DIAGNOSTICS.md) [ANTAPI-IN42]
  - Cache diagnostics (beta) - debug cache misses, diagnose caching issues
  - Sources: ANTAPI-SC-ANTH-CACHEDIAG

- [`_INFO_ANTAPI-43_RATE_LIMITS_API.md`](./_INFO_ANTAPI-43_RATE_LIMITS_API.md) [ANTAPI-IN43]
  - Rate Limits API - programmatic rate limit querying
  - Sources: ANTAPI-SC-ANTH-RTLMTAPI

- [`_INFO_ANTAPI-46_CLI.md`](./_INFO_ANTAPI-46_CLI.md) [ANTAPI-IN46]
  - ant CLI - command-line interface for API access
  - Sources: ANTAPI-SC-ANTH-CLI

### Platform Integration (1 file)

- [`_INFO_ANTAPI-44_CLAUDE_PLATFORM_ON_AWS.md`](./_INFO_ANTAPI-44_CLAUDE_PLATFORM_ON_AWS.md) [ANTAPI-IN44]
  - Claude Platform on AWS - CCU billing, feature availability
  - Sources: ANTAPI-SC-ANTH-CPAWS

### New Features (2 files)

- [`_INFO_ANTAPI-47_REFUSALS_AND_FALLBACKS.md`](./_INFO_ANTAPI-47_REFUSALS_AND_FALLBACKS.md) [ANTAPI-IN47]
  - Refusal stop_details, categories (cyber/bio/reasoning_extraction), server-side fallbacks (beta)
  - Sources: ANTAPI-SC-ANTH-REFUSAL

- [`_INFO_ANTAPI-48_MID_CONVERSATION_SYSTEM_MESSAGES.md`](./_INFO_ANTAPI-48_MID_CONVERSATION_SYSTEM_MESSAGES.md) [ANTAPI-IN48]
  - Mid-conversation system messages - dynamic instruction injection, cache preservation
  - Sources: ANTAPI-SC-ANTH-MIDSYS

### SDK Implementation (2 files)

- [`_INFO_ANTAPI-50_SDK_Model_Methods.md`](./_INFO_ANTAPI-50_SDK_Model_Methods.md) [ANTAPI-IN50]
  - Verified parameter combinations per model, live API test results (Python 0.120.0, TypeScript 0.115.0)
  - Sources: ANTAPI-SC-GH-SDKPY, ANTAPI-SC-ANTH-EFFORT

- [`_INFO_ANTAPI-51_Effort_Adaptive_Params.md`](./_INFO_ANTAPI-51_Effort_Adaptive_Params.md) [ANTAPI-IN51]
  - Effort-based and adaptive reasoning parameters - Python + TypeScript examples, model routing, error matrix
  - Sources: ANTAPI-SC-ANTH-THINK, ANTAPI-SC-ANTH-ADAPT, ANTAPI-SC-ANTH-EFFORT

## Topic Count

- **Total Topics**: 49
- **Core API**: 5
- **Messages API**: 5
- **Models**: 2
- **Model Capabilities**: 8
- **Tools**: 7
- **Files and Skills (Beta)**: 2
- **Admin API**: 4
- **Support and Configuration**: 4
- **Managed Agents and Agent Features**: 4
- **Diagnostics and Operational**: 3
- **Platform Integration**: 1
- **New Features**: 2
- **SDK Implementation**: 2

## Topic Details

### Topic: Introduction
**Scope**: API overview, base URL, protocol, request/response format, basic example
**Contents**:
- Base URL `https://api.anthropic.com`
- RESTful JSON API
- Required headers (x-api-key, anthropic-version, content-type)
- Request size limits
- Response headers (request-id, anthropic-organization-id)
- Basic cURL and Python examples
**Sources**: ANTAPI-SC-ANTH-APIOVW

### Topic: Authentication
**Scope**: API key management, authentication headers
**Contents**:
- x-api-key header authentication
- Console account setup
- API key creation and workspace segmentation
- Security best practices
**Sources**: ANTAPI-SC-ANTH-APIOVW, ANTAPI-SC-ANTH-QKSTART

### Topic: Versioning
**Scope**: API version management, beta features
**Contents**:
- anthropic-version header (current: 2023-06-01)
- Version changelog
- Beta headers for feature access
- anthropic-beta header format
**Sources**: ANTAPI-SC-ANTH-VERSION, ANTAPI-SC-ANTH-BETAHDR

### Topic: Errors
**Scope**: Error response format, HTTP status codes
**Contents**:
- Error type taxonomy (authentication_error, invalid_request_error, etc.)
- HTTP status codes (400, 401, 403, 404, 413, 429, 500, 529)
- Error response JSON schema
- Retry strategies for transient errors
**Sources**: ANTAPI-SC-ANTH-ERRORS

### Topic: SDKs
**Scope**: Official client libraries
**Contents**:
- Python SDK (anthropic package) - installation, configuration, usage
- TypeScript, Java, Go, C#, Ruby, PHP SDKs overview
- Environment variable configuration (ANTHROPIC_API_KEY)
- SDK vs raw HTTP comparison
**Sources**: ANTAPI-SC-ANTH-SDKOVW, ANTAPI-SC-ANTH-SDKPY, ANTAPI-SC-GH-SDKPY

### Topic: Messages (Create)
**Scope**: Primary message creation endpoint
**Contents**:
- POST /v1/messages full request body schema
- Required params: model, max_tokens, messages
- Optional params: system, temperature, top_p, top_k, tools, stream, metadata
- Content block types (text, image, tool_use, tool_result, document)
- Response schema with usage, stop_reason, content blocks
- Multi-turn conversation patterns
**Sources**: ANTAPI-SC-ANTH-MSGCRT, ANTAPI-SC-ANTH-MSGGUIDE

### Topic: Streaming
**Scope**: Server-Sent Events streaming interface
**Contents**:
- stream: true parameter
- SSE event types (message_start, content_block_start, content_block_delta, etc.)
- Python SDK StreamManager
- Partial response handling
**Sources**: ANTAPI-SC-ANTH-STREAM

### Topic: Token Counting
**Scope**: Pre-request token estimation
**Contents**:
- POST /v1/messages/count_tokens
- Request/response schema
- Cost estimation before sending
**Sources**: ANTAPI-SC-ANTH-MSGCNT, ANTAPI-SC-ANTH-TOKCNT

### Topic: Stop Reasons
**Scope**: Understanding why model stopped generating
**Contents**:
- end_turn, max_tokens, stop_sequence, tool_use
- Handling each stop reason type
- Agentic loop patterns with tool_use
**Sources**: ANTAPI-SC-ANTH-STOPREASON

### Topic: Batches
**Scope**: Async bulk message processing
**Contents**:
- POST /v1/messages/batches - create batch
- GET /v1/messages/batches - list batches
- GET /v1/messages/batches/{id} - retrieve batch
- POST /v1/messages/batches/{id}/cancel - cancel
- DELETE /v1/messages/batches/{id} - delete
- GET /v1/messages/batches/{id}/results - get results
- 50% cost reduction, 24h processing window
**Sources**: ANTAPI-SC-ANTH-BTCHCRT, ANTAPI-SC-ANTH-BATCH

### Topic: Models API
**Scope**: Model discovery and information
**Contents**:
- GET /v1/models - list all models
- GET /v1/models/{model_id} - get model details
- ModelInfo schema (capabilities, context window, pricing)
**Sources**: ANTAPI-SC-ANTH-MODLST, ANTAPI-SC-ANTH-MODGET

### Topic: Pricing
**Scope**: Cost structure and model selection
**Contents**:
- Per-model token pricing (input/output)
- Choosing between Claude models
- Model deprecation schedule
- Migration guide
**Sources**: ANTAPI-SC-ANTH-PRICING, ANTAPI-SC-ANTH-MODCHSE, ANTAPI-SC-ANTH-MODDEP

### Topic: Extended Thinking
**Scope**: Reasoning capabilities
**Contents**:
- thinking parameter configuration
- Adaptive thinking
- Effort levels (low, medium, high)
- ThinkingBlock and RedactedThinkingBlock in responses
- Budget tokens
**Sources**: ANTAPI-SC-ANTH-EXTTHINK, ANTAPI-SC-ANTH-ADAPTIVE, ANTAPI-SC-ANTH-EFFORT

### Topic: Structured Outputs
**Scope**: Constrained output formats
**Contents**:
- JSON mode
- Output schema constraints
- Prefill technique for format control
**Sources**: ANTAPI-SC-ANTH-STRUCTOUT

### Topic: Citations
**Scope**: Source attribution in responses
**Contents**:
- CitationsConfig parameter
- Citation types: char location, page location, content block, web search
- Enabling/disabling citations
**Sources**: ANTAPI-SC-ANTH-CITATIONS

### Topic: Vision
**Scope**: Image understanding
**Contents**:
- Base64 and URL image sources
- Supported formats (JPEG, PNG, GIF, WebP)
- Image content blocks in messages
- Multi-image support
**Sources**: ANTAPI-SC-ANTH-VISION

### Topic: PDF Support
**Scope**: Document processing
**Contents**:
- Base64 and URL PDF sources
- Document content blocks
- Page limits and processing
**Sources**: ANTAPI-SC-ANTH-PDF

### Topic: Prompt Caching
**Scope**: Cost optimization via caching
**Contents**:
- cache_control parameter on content blocks
- TTL options (5m, 1h)
- Cache creation and usage in response
- Cost savings calculation
**Sources**: ANTAPI-SC-ANTH-CACHE

### Topic: Context Management
**Scope**: Managing conversation context
**Contents**:
- Context window sizes per model
- Compaction for long conversations
- Context editing for precise control
- Token counting for context budget
**Sources**: ANTAPI-SC-ANTH-CTXWIN, ANTAPI-SC-ANTH-COMPACT, ANTAPI-SC-ANTH-CTXEDIT

### Topic: Search
**Scope**: Search results and embeddings
**Contents**:
- Search result content blocks
- Embeddings guidance (third-party)
**Sources**: ANTAPI-SC-ANTH-SEARCH, ANTAPI-SC-ANTH-EMBED

### Topic: Tool Use
**Scope**: Function calling fundamentals
**Contents**:
- tools parameter schema
- tool_choice (auto, any, none, specific tool)
- Tool use request/response flow
- tool_use and tool_result content blocks
**Sources**: ANTAPI-SC-ANTH-TOOLOVW, ANTAPI-SC-ANTH-TOOLIMPL

### Topic: Web Tools
**Scope**: Built-in web search and fetch
**Contents**:
- Web search tool (server-side)
- Web fetch tool (server-side)
- Search result blocks
- ServerToolCaller pattern
**Sources**: ANTAPI-SC-ANTH-TOOLWEB, ANTAPI-SC-ANTH-TOOLFETCH

### Topic: Code Execution
**Scope**: Sandboxed code execution
**Contents**:
- Code execution tool configuration
- Execution result blocks
- Error handling
**Sources**: ANTAPI-SC-ANTH-TOOLCODE

### Topic: Computer Use
**Scope**: Desktop automation tools
**Contents**:
- Computer use tool
- Bash tool (shell commands)
- Text editor tool (file operations)
- Tool versions and compatibility
**Sources**: ANTAPI-SC-ANTH-TOOLCOMP, ANTAPI-SC-ANTH-TOOLBASH, ANTAPI-SC-ANTH-TOOLTEXT

### Topic: Memory Tool
**Scope**: Persistent memory across conversations
**Contents**:
- Memory tool configuration
- Storing and retrieving memories
**Sources**: ANTAPI-SC-ANTH-TOOLMEM

### Topic: Tool Infrastructure
**Scope**: Advanced tool patterns
**Contents**:
- Tool search for dynamic tool selection
- Programmatic tool calling
- Fine-grained tool streaming
**Sources**: ANTAPI-SC-ANTH-TOOLSRCH, ANTAPI-SC-ANTH-TOOLPROG

### Topic: Tool Streaming
**Scope**: Streaming with tool use
**Contents**:
- Fine-grained streaming during tool interactions
- Partial JSON handling
- Event ordering with tools
**Sources**: ANTAPI-SC-ANTH-TOOLSTRM

### Topic: Files API
**Scope**: File management (beta)
**Contents**:
- POST /v1/files - upload
- GET /v1/files - list
- GET /v1/files/{id}/content - download
- GET /v1/files/{id} - metadata
- DELETE /v1/files/{id} - delete
**Sources**: ANTAPI-SC-ANTH-BFILUP, ANTAPI-SC-ANTH-FILES

### Topic: Skills API
**Scope**: Agent Skills management (beta)
**Contents**:
- POST /v1/skills - create
- GET /v1/skills - list
- GET /v1/skills/{id} - retrieve
- DELETE /v1/skills/{id} - delete
- Skill versions
**Sources**: ANTAPI-SC-ANTH-BSKLCRT, ANTAPI-SC-ANTH-AGSKOVW

### Topic: Admin Organizations
**Scope**: Organization and invite management
**Contents**:
- GET /v1/organizations/me - current organization
- Invites CRUD (create, get, list, delete)
**Sources**: ANTAPI-SC-ANTH-ADMORG, ANTAPI-SC-ANTH-ADMIVCRT

### Topic: Admin Users
**Scope**: User management
**Contents**:
- GET /v1/organizations/users/{id} - get user
- GET /v1/organizations/users - list users
- POST /v1/organizations/users/{id} - update
- DELETE /v1/organizations/users/{id} - remove
**Sources**: ANTAPI-SC-ANTH-ADMUSRGET, ANTAPI-SC-ANTH-ADMUSRLST

### Topic: Admin Workspaces
**Scope**: Workspace and API key management
**Contents**:
- Workspaces CRUD + archive + members
- API Keys management (get, list, update)
**Sources**: ANTAPI-SC-ANTH-ADMWSCRT, ANTAPI-SC-ANTH-ADMKELST

### Topic: Usage Reports
**Scope**: Usage tracking and cost reporting
**Contents**:
- Messages usage report (tokens by model, workspace, API key, geo)
- Claude Code usage report (sessions, commits, code changes)
- Grouping dimensions and cursor pagination
**Sources**: ANTAPI-SC-ANTH-ADMIN

### Topic: Rate Limits
**Scope**: API usage limits and tiers
**Contents**:
- Rate limit types (RPM, input TPM, output TPM)
- Per-model, per-workspace scope
- Rate limit headers (anthropic-ratelimit-*)
- SDK auto-retry with exponential backoff
- Batch API separate rate limits
**Sources**: ANTAPI-SC-ANTH-RTLMT

### Topic: Data Residency
**Scope**: Geographic inference routing
**Contents**:
- inference_geo parameter ("us" for US-only)
- 1.1x pricing multiplier for US-only (Opus 4.6+)
- Workspace default_inference_geo
- Third-party platform regional vs global endpoints
**Sources**: ANTAPI-SC-ANTH-DATARES, ANTAPI-SC-ANTH-PRICING

### Topic: Platform Compatibility
**Scope**: Third-party cloud platform support
**Contents**:
- AWS Bedrock (AnthropicBedrock client, IAM auth)
- Google Vertex AI (AnthropicVertex client, GCP auth)
- Microsoft Azure AI Foundry
- Platform-specific model IDs, pricing, feature availability
**Sources**: ANTAPI-SC-ANTH-BEDROCK, ANTAPI-SC-ANTH-VERTEX, ANTAPI-SC-ANTH-FOUNDRY

### Topic: Legacy APIs and Deprecations
**Scope**: Deprecated models and APIs
**Contents**:
- Text Completions API (POST /v1/complete) - fully deprecated
- Model deprecation lifecycle (Active, Legacy, Deprecated, Retired)
- Claude Sonnet 4 + Opus 4 deprecated (retiring June 15, 2026)
- Claude Haiku 3 retired (April 20, 2026)
- Migration guidance and auditing model usage
**Sources**: ANTAPI-SC-ANTH-DEPR, ANTAPI-SC-ANTH-LEGACY

### New in 2026-05-22: Agents and Platform (7 files)

- [`_INFO_ANTAPI-40_MANAGED_AGENTS.md`](./_INFO_ANTAPI-40_MANAGED_AGENTS.md) [ANTAPI-IN40]
  - Claude Managed Agents - autonomous agent harness, sessions, tools, environments
  - Sources: ANTAPI-SC-ANTH-MAOVW, ANTAPI-SC-ANTH-MAQS, ANTAPI-SC-ANTH-MATOOL, ANTAPI-SC-ANTH-MASESS

- [`_INFO_ANTAPI-41_ADVISOR_TOOL.md`](./_INFO_ANTAPI-41_ADVISOR_TOOL.md) [ANTAPI-IN41]
  - Advisor tool - pair executor + advisor models for cost-effective reasoning
  - Sources: ANTAPI-SC-ANTH-ADVSR

- [`_INFO_ANTAPI-42_CACHE_DIAGNOSTICS.md`](./_INFO_ANTAPI-42_CACHE_DIAGNOSTICS.md) [ANTAPI-IN42]
  - Cache diagnostics - debug prompt caching misses
  - Sources: ANTAPI-SC-ANTH-CACHDIAG

- [`_INFO_ANTAPI-43_RATE_LIMITS_API.md`](./_INFO_ANTAPI-43_RATE_LIMITS_API.md) [ANTAPI-IN43]
  - Rate Limits API - programmatic rate limit querying
  - Sources: ANTAPI-SC-ANTH-RTLMTAPI

- [`_INFO_ANTAPI-44_CLAUDE_PLATFORM_ON_AWS.md`](./_INFO_ANTAPI-44_CLAUDE_PLATFORM_ON_AWS.md) [ANTAPI-IN44]
  - Claude Platform on AWS - Anthropic-managed infra, CCU billing, PrivateLink
  - Sources: ANTAPI-SC-ANTH-CPAWS

- [`_INFO_ANTAPI-45_MCP_TUNNELS.md`](./_INFO_ANTAPI-45_MCP_TUNNELS.md) [ANTAPI-IN45]
  - MCP tunnels - connect managed agents to private MCP servers
  - Sources: ANTAPI-SC-ANTH-MCPTNL

- [`_INFO_ANTAPI-46_CLI.md`](./_INFO_ANTAPI-46_CLI.md) [ANTAPI-IN46]
  - `ant` CLI - command-line interface for the Anthropic API
  - Sources: ANTAPI-SC-ANTH-CLI

## Related APIs/Technologies

- **OpenAI API**
  - URL: https://platform.openai.com/docs
  - Relation: Primary competitor with similar REST API structure, SDK patterns
- **Google Gemini API**
  - URL: https://ai.google.dev/docs
  - Relation: Competing LLM API with different auth and endpoint structure
- **Amazon Bedrock (Claude)**
  - URL: https://docs.aws.amazon.com/bedrock/
  - Relation: Hosted Claude access via AWS, different auth (SigV4), different endpoints
- **Google Vertex AI (Claude)**
  - URL: https://cloud.google.com/vertex-ai/docs
  - Relation: Hosted Claude access via GCP, different auth (OAuth2), different endpoints

## Document History

**[2026-07-27]**
- Changed: Migrated to deep-research output format (01_Summary, 02_Sources, 03+ topic files)
- Added: 2 new topics (IN50 SDK Model Methods, IN51 Effort/Adaptive Params) with Python + TypeScript examples
- Added: SDK Implementation category (2 files)
- Changed: All files renumbered (+2 shift), Doc IDs and cross-references updated (647 replacements)
- Changed: Stats updated to 49 topics, 51 INFO files, 13 categories

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Added: 7 new topics (IN38-IN44): Managed Agents, Advisor Tool, Cache Diagnostics, Rate Limits API, Claude Platform on AWS, MCP Tunnels, CLI
- Changed: Stats updated to 44 topics, 10 categories
- Changed: Summary updated with new features (Managed Agents, advisor, cache diagnostics, MCP tunnels, ant CLI, Platform on AWS)
- Changed: Legacy topic updated with current deprecation/retirement status

**[2026-03-20 04:35]**
- Fixed: TOC filenames synced with actual files (IN33, IN35, IN36, IN37)
- Changed: Support/Config section expanded from 3 to 4 files
- Added: Research stats to header (37 topics, 37 files, 89 sources)

**[2026-03-20 02:00]**
- Initial TOC created with 37 topics in 9 categories
