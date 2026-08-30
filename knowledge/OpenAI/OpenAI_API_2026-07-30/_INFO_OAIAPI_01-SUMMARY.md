# OpenAI API - Summary

**Doc ID**: OAIAPI-IN01
**Goal**: Cross-document synthesis and master index for OpenAI API research
**Version scope**: API v1, Documentation date 2026-07-30
**Research stats**: 97 topic files, 19 categories, 5 new (IN93-IN97), SDK v2.45.0

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The OpenAI API is a RESTful API (v1) at `https://api.openai.com` providing programmatic access to OpenAI's language models. As of 2026-07, GPT-5.6 is the flagship model family (Sol/Terra/Luna tiers, 1M token context, GA 2026-07-09), replacing GPT-5.5 which is now deprecated (removal 2026-12-11). GPT-5.6 introduces Programmatic Tool Calling (model-written JavaScript orchestration in V8 sandbox), Multi-Agent orchestration beta, Pro mode, persisted reasoning across turns, 6 effort levels (none through max), and explicit prompt caching controls with TTL. Two primary text generation interfaces exist: the Responses API (recommended, all new features ship here) and the Chat Completions API (stable legacy). GPT-Realtime-2.1 adds improved alphanumeric recognition and interruption handling. Major changes since 2026-05 include: 2026-06 deprecation wave (Evals platform, Agent Builder, Reusable Prompts, older GPT Image models); inline moderation in Responses/Chat Completions requests; web search image results; Amazon Bedrock integration; Safety Usage Dashboard; Workload Identity Federation for keyless auth; and per-minute container billing. Python SDK at v2.45.0.

## Topic Files

### Core Documentation (5 files)

- [`_INFO_OAIAPI-IN01_INTRODUCTION.md`](./_INFO_OAIAPI-IN01_INTRODUCTION.md) OAIAPI-IN01
  - API overview, base URL, versioning, backwards compatibility, X-Client-Request-Id
- [`_INFO_OAIAPI-IN02_AUTHENTICATION.md`](./_INFO_OAIAPI-IN02_AUTHENTICATION.md) OAIAPI-IN02
  - API keys, Bearer auth, OpenAI-Organization, OpenAI-Project headers, key management
- [`_INFO_OAIAPI-IN03_MODELS.md`](./_INFO_OAIAPI-IN03_MODELS.md) OAIAPI-IN03
  - Model families (GPT-5.6 Sol/Terra/Luna, GPT-5.5 deprecated, GPT-5.4, image, audio, embedding, moderation), capabilities, pricing, context windows, deprecations
- [`_INFO_OAIAPI-IN04_ERRORS.md`](./_INFO_OAIAPI-IN04_ERRORS.md) OAIAPI-IN04
  - HTTP status codes, error response format, error types, debugging, x-request-id
- [`_INFO_OAIAPI-IN05_RATE_LIMITS.md`](./_INFO_OAIAPI-IN05_RATE_LIMITS.md) OAIAPI-IN05
  - Rate limit tiers, RPM/TPM, x-ratelimit-* headers, usage tiers, project-level rate limits

### Responses API (6 files)

- [`_INFO_OAIAPI-IN06_RESPONSES_API.md`](./_INFO_OAIAPI-IN06_RESPONSES_API.md) OAIAPI-IN06
  - POST /v1/responses - create, retrieve, delete, cancel, compact; full request/response schema, parameters, tools configuration, reasoning, background mode
- [`_INFO_OAIAPI-IN07_RESPONSES_STREAMING.md`](./_INFO_OAIAPI-IN07_RESPONSES_STREAMING.md) OAIAPI-IN07
  - SSE streaming events for Responses API, event types, partial responses, stream manager
- [`_INFO_OAIAPI-IN08_CONVERSATIONS.md`](./_INFO_OAIAPI-IN08_CONVERSATIONS.md) OAIAPI-IN08
  - Conversations API - create, retrieve, update, delete conversations; items CRUD; persistent multi-turn state
- [`_INFO_OAIAPI-IN09_TOKEN_COUNTING.md`](./_INFO_OAIAPI-IN09_TOKEN_COUNTING.md) OAIAPI-IN09
  - POST /v1/responses/input_tokens/count - pre-request token estimation, cost calculation
- [`_INFO_OAIAPI-IN10_RESPONSE_INPUT_ITEMS.md`](./_INFO_OAIAPI-IN10_RESPONSE_INPUT_ITEMS.md) OAIAPI-IN10
  - GET list input items for a response, pagination
- [`_INFO_OAIAPI-IN11_MIGRATE_TO_RESPONSES.md`](./_INFO_OAIAPI-IN11_MIGRATE_TO_RESPONSES.md) OAIAPI-IN11
  - Migration guide from Chat Completions to Responses API, parameter mapping, structured outputs changes

### Tools and Function Calling (6 files)

- [`_INFO_OAIAPI-IN12_TOOLS_OVERVIEW.md`](./_INFO_OAIAPI-IN12_TOOLS_OVERVIEW.md) OAIAPI-IN12
  - Tool types overview: built-in tools vs function calling, tool_choice, parallel tool calls
- [`_INFO_OAIAPI-IN13_FUNCTION_CALLING.md`](./_INFO_OAIAPI-IN13_FUNCTION_CALLING.md) OAIAPI-IN13
  - Function definitions, JSON schema, strict mode, tool_choice, parallel function calls
- [`_INFO_OAIAPI-IN14_WEB_SEARCH.md`](./_INFO_OAIAPI-IN14_WEB_SEARCH.md) OAIAPI-IN14
  - Web search tool configuration, search context size, user location, return_token_budget, deep research
- [`_INFO_OAIAPI-IN15_STRUCTURED_OUTPUTS.md`](./_INFO_OAIAPI-IN15_STRUCTURED_OUTPUTS.md) OAIAPI-IN15
  - JSON schema response formatting, text.format (Responses) vs response_format (Chat), strict mode
- [`_INFO_OAIAPI-IN16_REASONING.md`](./_INFO_OAIAPI-IN16_REASONING.md) OAIAPI-IN16
  - Reasoning models (GPT-5.6, GPT-5.5), Pro mode, persisted reasoning (`reasoning.context`), 6 effort levels (none-max), reasoning summaries
- [`_INFO_OAIAPI-IN17_SKILLS.md`](./_INFO_OAIAPI-IN17_SKILLS.md) OAIAPI-IN17
  - Skills API - CRUD, versions, content retrieval; tool search; reusable tool packages

### Audio (3 files)

- [`_INFO_OAIAPI-IN18_AUDIO_TRANSCRIPTION.md`](./_INFO_OAIAPI-IN18_AUDIO_TRANSCRIPTION.md) OAIAPI-IN18
  - POST /v1/audio/transcriptions, POST /v1/audio/translations; Whisper, gpt-4o-mini-transcribe; supported formats
- [`_INFO_OAIAPI-IN19_TEXT_TO_SPEECH.md`](./_INFO_OAIAPI-IN19_TEXT_TO_SPEECH.md) OAIAPI-IN19
  - POST /v1/audio/speech; TTS models, voices, formats, speed; custom voices with consent management
- [`_INFO_OAIAPI-IN20_REALTIME_AUDIO.md`](./_INFO_OAIAPI-IN20_REALTIME_AUDIO.md) OAIAPI-IN20
  - Realtime audio streaming, voice agents, realtime transcription overview

### Media Generation (4 files)

- [`_INFO_OAIAPI-IN21_IMAGE_GENERATION.md`](./_INFO_OAIAPI-IN21_IMAGE_GENERATION.md) OAIAPI-IN21
  - POST /v1/images/generations, /v1/images/edits, /v1/images/variations; gpt-image-2, gpt-image-1, gpt-image-1-mini; sizes, formats, quality
- [`_INFO_OAIAPI-IN22_IMAGE_STREAMING.md`](./_INFO_OAIAPI-IN22_IMAGE_STREAMING.md) OAIAPI-IN22
  - SSE streaming for image generation and editing, partial image events
- [`_INFO_OAIAPI-IN23_VIDEO_GENERATION.md`](./_INFO_OAIAPI-IN23_VIDEO_GENERATION.md) OAIAPI-IN23
  - POST /v1/videos, POST /v1/videos/edits; Sora, sora-2, sora-2-pro (deprecated 2026-09); characters, edit, extend, remix
- [`_INFO_OAIAPI-IN24_PROMPT_ENGINEERING.md`](./_INFO_OAIAPI-IN24_PROMPT_ENGINEERING.md) OAIAPI-IN24
  - Prompt engineering best practices, system prompts, few-shot, chain-of-thought, reusable prompts

### AI Core (3 files)

- [`_INFO_OAIAPI-IN25_EMBEDDINGS.md`](./_INFO_OAIAPI-IN25_EMBEDDINGS.md) OAIAPI-IN25
  - POST /v1/embeddings; text-embedding-3-small/large; dimensions, encoding formats
- [`_INFO_OAIAPI-IN26_MODERATIONS.md`](./_INFO_OAIAPI-IN26_MODERATIONS.md) OAIAPI-IN26
  - POST /v1/moderations; omni-moderation-latest; category scores, multi-modal input
- [`_INFO_OAIAPI-IN27_MODELS_API.md`](./_INFO_OAIAPI-IN27_MODELS_API.md) OAIAPI-IN27
  - GET /v1/models, GET /v1/models/{model}, DELETE /v1/models/{model}; model listing, fine-tuned model deletion

### Evaluation and Training (4 files)

- [`_INFO_OAIAPI-IN28_EVALS.md`](./_INFO_OAIAPI-IN28_EVALS.md) OAIAPI-IN28
  - **[DEPRECATED 2026-06-03]** Evals API - CRUD evals, runs, output items; migrate to Promptfoo
- [`_INFO_OAIAPI-IN29_FINE_TUNING.md`](./_INFO_OAIAPI-IN29_FINE_TUNING.md) OAIAPI-IN29
  - Fine-tuning jobs - create, retrieve, list, cancel, pause, resume; events; checkpoints; permissions; supported models
- [`_INFO_OAIAPI-IN30_REINFORCEMENT_FINE_TUNING.md`](./_INFO_OAIAPI-IN30_REINFORCEMENT_FINE_TUNING.md) OAIAPI-IN30
  - DPO, reinforcement fine-tuning, graders (run, validate), training metrics
- [`_INFO_OAIAPI-IN31_GRADERS.md`](./_INFO_OAIAPI-IN31_GRADERS.md) OAIAPI-IN31
  - **[ALPHA]** Graders API - run, validate; grader types; eval integration

### Processing (4 files)

- [`_INFO_OAIAPI-IN32_BATCH_API.md`](./_INFO_OAIAPI-IN32_BATCH_API.md) OAIAPI-IN32
  - POST /v1/batches; create, retrieve, list, cancel; 50% cost reduction; JSONL input/output; supported endpoints
- [`_INFO_OAIAPI-IN33_FILES.md`](./_INFO_OAIAPI-IN33_FILES.md) OAIAPI-IN33
  - Files API - list, create, retrieve, delete, content; purpose types; supported formats
- [`_INFO_OAIAPI-IN34_UPLOADS.md`](./_INFO_OAIAPI-IN34_UPLOADS.md) OAIAPI-IN34
  - Uploads API - create, cancel, complete, create parts; multipart uploads for large files (>100MB)
- [`_INFO_OAIAPI-IN35_WEBHOOKS.md`](./_INFO_OAIAPI-IN35_WEBHOOKS.md) OAIAPI-IN35
  - Webhook events, event types, signature verification, retry behavior

### Vector Stores (3 files)

- [`_INFO_OAIAPI-IN36_VECTOR_STORES.md`](./_INFO_OAIAPI-IN36_VECTOR_STORES.md) OAIAPI-IN36
  - Vector stores - create, retrieve, update, delete, list, search; expiration policies; file search integration
- [`_INFO_OAIAPI-IN37_VECTOR_STORE_FILES.md`](./_INFO_OAIAPI-IN37_VECTOR_STORE_FILES.md) OAIAPI-IN37
  - Vector store files - create, retrieve, update, delete, list, content; chunking strategies; status tracking
- [`_INFO_OAIAPI-IN38_VECTOR_STORE_FILE_BATCHES.md`](./_INFO_OAIAPI-IN38_VECTOR_STORE_FILE_BATCHES.md) OAIAPI-IN38
  - File batches - create, retrieve, list files, cancel; bulk file operations

### Realtime API (5 files)

- [`_INFO_OAIAPI-IN39_REALTIME_OVERVIEW.md`](./_INFO_OAIAPI-IN39_REALTIME_OVERVIEW.md) OAIAPI-IN39
  - Realtime API overview, WebSocket connection, sessions, transcription sessions, calls, client secrets
- [`_INFO_OAIAPI-IN40_REALTIME_CLIENT_EVENTS.md`](./_INFO_OAIAPI-IN40_REALTIME_CLIENT_EVENTS.md) OAIAPI-IN40
  - Client-to-server event types, session configuration, audio input, conversation management
- [`_INFO_OAIAPI-IN41_REALTIME_SERVER_EVENTS.md`](./_INFO_OAIAPI-IN41_REALTIME_SERVER_EVENTS.md) OAIAPI-IN41
  - Server-to-client event types, audio output, function calls, error events
- [`_INFO_OAIAPI-IN42_REALTIME_CALLS.md`](./_INFO_OAIAPI-IN42_REALTIME_CALLS.md) OAIAPI-IN42
  - Calls API - create, retrieve, list; call lifecycle management
- [`_INFO_OAIAPI-IN77_REALTIME_TRANSLATE_WHISPER.md`](./_INFO_OAIAPI-IN77_REALTIME_TRANSLATE_WHISPER.md) OAIAPI-IN77
  - **[NEW]** Realtime 2, Realtime Translate (70+ input, 13 output languages), Realtime Whisper (streaming STT), translation CRUD endpoints

### Infrastructure (4 files)

- [`_INFO_OAIAPI-IN43_CONTAINERS.md`](./_INFO_OAIAPI-IN43_CONTAINERS.md) OAIAPI-IN43
  - Containers API - create, retrieve, delete, list; sandboxed execution environments
- [`_INFO_OAIAPI-IN44_CONTAINER_FILES.md`](./_INFO_OAIAPI-IN44_CONTAINER_FILES.md) OAIAPI-IN44
  - Container files - create, retrieve, delete, list, content; file management in containers
- [`_INFO_OAIAPI-IN45_CHATKIT.md`](./_INFO_OAIAPI-IN45_CHATKIT.md) OAIAPI-IN45
  - **[BETA]** ChatKit - sessions, threads, list items; embeddable chat UI; widgets; developer mode
- [`_INFO_OAIAPI-IN46_SDKS.md`](./_INFO_OAIAPI-IN46_SDKS.md) OAIAPI-IN46
  - Official SDKs (Python, TypeScript, .NET, Java, Go, Ruby), Agents SDK, Admin API SDK support, installation

### Administration (9 files)

- [`_INFO_OAIAPI-IN47_ADMIN_OVERVIEW.md`](./_INFO_OAIAPI-IN47_ADMIN_OVERVIEW.md) OAIAPI-IN47
  - Administration overview, org/project hierarchy, RBAC model, Admin APIs guide
- [`_INFO_OAIAPI-IN48_ORG_USERS_INVITES.md`](./_INFO_OAIAPI-IN48_ORG_USERS_INVITES.md) OAIAPI-IN48
  - Organization users, invites, roles, role assignments; user management
- [`_INFO_OAIAPI-IN49_ORG_GROUPS_ROLES.md`](./_INFO_OAIAPI-IN49_ORG_GROUPS_ROLES.md) OAIAPI-IN49
  - Organization groups, custom roles, role CRUD; group-based access control
- [`_INFO_OAIAPI-IN50_PROJECTS.md`](./_INFO_OAIAPI-IN50_PROJECTS.md) OAIAPI-IN50
  - Projects - create, retrieve, update, list, archive; project users, groups, service accounts, API keys, rate limits
- [`_INFO_OAIAPI-IN51_CERTIFICATES.md`](./_INFO_OAIAPI-IN51_CERTIFICATES.md) OAIAPI-IN51
  - mTLS certificates - CRUD, activate, deactivate; org-level and project-level certificates
- [`_INFO_OAIAPI-IN52_AUDIT_LOGS.md`](./_INFO_OAIAPI-IN52_AUDIT_LOGS.md) OAIAPI-IN52
  - Audit logs - list, filtering; compliance and security logging
- [`_INFO_OAIAPI-IN53_USAGE_COSTS.md`](./_INFO_OAIAPI-IN53_USAGE_COSTS.md) OAIAPI-IN53
  - Usage tracking (completions, embeddings, images, audio, moderations, vector stores), cost reporting
- [`_INFO_OAIAPI-IN54_SERVICE_ACCOUNTS_API_KEYS.md`](./_INFO_OAIAPI-IN54_SERVICE_ACCOUNTS_API_KEYS.md) OAIAPI-IN54
  - Project service accounts, project API keys; programmatic access management
- [`_INFO_OAIAPI-IN80_ADMIN_PERMISSIONS_RETENTION.md`](./_INFO_OAIAPI-IN80_ADMIN_PERMISSIONS_RETENTION.md) OAIAPI-IN80
  - **[NEW]** Admin API Keys, Model Permissions, Hosted Tool Permissions, Data Retention, Spend Alerts

### Chat Completions (3 files)

- [`_INFO_OAIAPI-IN55_CHAT_COMPLETIONS.md`](./_INFO_OAIAPI-IN55_CHAT_COMPLETIONS.md) OAIAPI-IN55
  - POST /v1/chat/completions - create, retrieve, update, delete, list; full request/response schema; messages format
- [`_INFO_OAIAPI-IN56_CHAT_STREAMING.md`](./_INFO_OAIAPI-IN56_CHAT_STREAMING.md) OAIAPI-IN56
  - SSE streaming for Chat Completions, chunk format, delta objects
- [`_INFO_OAIAPI-IN57_CHAT_MESSAGES.md`](./_INFO_OAIAPI-IN57_CHAT_MESSAGES.md) OAIAPI-IN57
  - List messages for a chat completion; conversation history retrieval

### Legacy APIs (3 files)

- [`_INFO_OAIAPI-IN58_LEGACY_ASSISTANTS.md`](./_INFO_OAIAPI-IN58_LEGACY_ASSISTANTS.md) OAIAPI-IN58
  - **[DEPRECATED sunset 2026-08-26]** Assistants API - assistants, threads, messages, runs, run steps, streaming; migration path
- [`_INFO_OAIAPI-IN59_LEGACY_COMPLETIONS.md`](./_INFO_OAIAPI-IN59_LEGACY_COMPLETIONS.md) OAIAPI-IN59
  - Legacy Completions API (POST /v1/completions); freeform prompt interface
- [`_INFO_OAIAPI-IN60_LEGACY_REALTIME_BETA.md`](./_INFO_OAIAPI-IN60_LEGACY_REALTIME_BETA.md) OAIAPI-IN60
  - **[REMOVED 2026-05-12]** Realtime Beta - removed from API, migration to GA Realtime

### Agents and Automation (4 files)

- [`_INFO_OAIAPI-IN63_CODE_GENERATION_CODEX.md`](./_INFO_OAIAPI-IN63_CODE_GENERATION_CODEX.md) OAIAPI-IN63
  - Code generation, Codex coding agent, GPT-5.3-Codex/gpt-5.4/gpt-5.5 models, shell tool, apply patch, IDE/CLI/CI-CD integration
- [`_INFO_OAIAPI-IN64_AGENTS_FRAMEWORK.md`](./_INFO_OAIAPI-IN64_AGENTS_FRAMEWORK.md) OAIAPI-IN64
  - Agents overview, building agents, Agents SDK (Python/TypeScript), sandbox agents, harness, memory control
- [`_INFO_OAIAPI-IN65_COMPUTER_USE.md`](./_INFO_OAIAPI-IN65_COMPUTER_USE.md) OAIAPI-IN65
  - Computer Use built-in tool (GPT-5.4/5.5), browser automation, screenshot-action loop
- [`_INFO_OAIAPI-IN66_MCP_AND_CONNECTORS.md`](./_INFO_OAIAPI-IN66_MCP_AND_CONNECTORS.md) OAIAPI-IN66
  - Remote MCP server integration, Secure MCP Tunnels (enterprise), connector setup, authentication

### Specialized Capabilities (4 files)

- [`_INFO_OAIAPI-IN67_DEEP_RESEARCH.md`](./_INFO_OAIAPI-IN67_DEEP_RESEARCH.md) OAIAPI-IN67
  - Deep research (GPT-5.6 Sol with Pro mode), background mode, webhook integration
- [`_INFO_OAIAPI-IN68_FILE_INPUTS_VISION.md`](./_INFO_OAIAPI-IN68_FILE_INPUTS_VISION.md) OAIAPI-IN68
  - File inputs (PDF, images, documents), vision capabilities, multimodal input processing
- [`_INFO_OAIAPI-IN69_VOICE_AGENTS.md`](./_INFO_OAIAPI-IN69_VOICE_AGENTS.md) OAIAPI-IN69
  - Voice agent patterns, Realtime 2 with reasoning, SIP integration, dedicated IP ranges
- [`_INFO_OAIAPI-IN70_WEBSOCKET_MODE.md`](./_INFO_OAIAPI-IN70_WEBSOCKET_MODE.md) OAIAPI-IN70
  - WebSocket mode for Responses API (alternative to SSE streaming), persistent connections

### Cross-Cutting Guides (8 files)

- [`_INFO_OAIAPI-IN61_PRODUCTION_BEST_PRACTICES.md`](./_INFO_OAIAPI-IN61_PRODUCTION_BEST_PRACTICES.md) OAIAPI-IN61
  - Production readiness, retry strategies, backoff, monitoring, organization setup, safety
- [`_INFO_OAIAPI-IN62_CHANGELOG_DEPRECATIONS.md`](./_INFO_OAIAPI-IN62_CHANGELOG_DEPRECATIONS.md) OAIAPI-IN62
  - API changelog, model deprecation schedule, version history, breaking changes, 2026-05 deprecation wave
- [`_INFO_OAIAPI-IN71_PROMPT_CACHING.md`](./_INFO_OAIAPI-IN71_PROMPT_CACHING.md) OAIAPI-IN71
  - Automatic prompt caching, explicit caching with breakpoints/TTL (GPT-5.6), cached_tokens in usage, 90% pricing discount
- [`_INFO_OAIAPI-IN72_BACKGROUND_FLEX_PROCESSING.md`](./_INFO_OAIAPI-IN72_BACKGROUND_FLEX_PROCESSING.md) OAIAPI-IN72
  - Background mode, flex processing, comparison with batch API
- [`_INFO_OAIAPI-IN73_SAFETY_DATA_PRIVACY.md`](./_INFO_OAIAPI-IN73_SAFETY_DATA_PRIVACY.md) OAIAPI-IN73
  - Safety best practices, content policies, data usage policies, API data retention, opt-out
- [`_INFO_OAIAPI-IN74_OPTIMIZATION_GUIDES.md`](./_INFO_OAIAPI-IN74_OPTIMIZATION_GUIDES.md) OAIAPI-IN74
  - Latency optimization, cost optimization, accuracy optimization, model selection
- [`_INFO_OAIAPI-IN75_GPT55_LATEST_MODEL.md`](./_INFO_OAIAPI-IN75_GPT55_LATEST_MODEL.md) OAIAPI-IN75
  - **[DEPRECATED]** GPT-5.5 guide (deprecated 2026-06-11, removal 2026-12-11). Migrate to IN93 (GPT-5.6)
- [`_INFO_OAIAPI-IN78_COMPACTION.md`](./_INFO_OAIAPI-IN78_COMPACTION.md) OAIAPI-IN78
  - **[NEW]** Compaction for long-running agent workflows, context management, POST /v1/responses/{id}/compact

### New Topics IN93+ (5 files)

- [`_INFO_OAIAPI-IN93_GPT56_LATEST_MODEL.md`](./_INFO_OAIAPI-IN93_GPT56_LATEST_MODEL.md) OAIAPI-IN93
  - GPT-5.6 Sol/Terra/Luna tiers, Pro mode, persisted reasoning, explicit caching, migration from GPT-5.5
- [`_INFO_OAIAPI-IN94_PROGRAMMATIC_TOOL_CALLING.md`](./_INFO_OAIAPI-IN94_PROGRAMMATIC_TOOL_CALLING.md) OAIAPI-IN94
  - Programmatic Tool Calling - model-written JS in V8 sandbox, multi-tool orchestration, GPT-5.6 only
- [`_INFO_OAIAPI-IN95_MULTI_AGENT.md`](./_INFO_OAIAPI-IN95_MULTI_AGENT.md) OAIAPI-IN95
  - **[BETA]** Multi-Agent Orchestration - parallel subagent coordination via Responses API
- [`_INFO_OAIAPI-IN96_WORKLOAD_IDENTITY_FEDERATION.md`](./_INFO_OAIAPI-IN96_WORKLOAD_IDENTITY_FEDERATION.md) OAIAPI-IN96
  - Workload Identity Federation - keyless auth via AWS STS, GCP, Azure AD tokens
- [`_INFO_OAIAPI-IN97_AMAZON_BEDROCK.md`](./_INFO_OAIAPI-IN97_AMAZON_BEDROCK.md) OAIAPI-IN97
  - Amazon Bedrock Integration - OpenAI models via AWS Bedrock endpoint, IAM auth

## Topic Count

- **Total Topics**: 97 (85 content + 12 gap)
- **Core Documentation**: 5
- **Responses API**: 6
- **Tools and Function Calling**: 6
- **Audio**: 3
- **Media Generation**: 4
- **AI Core**: 3
- **Evaluation and Training**: 4
- **Processing**: 4
- **Vector Stores**: 3
- **Realtime API**: 5
- **Infrastructure**: 4
- **Administration**: 9
- **Chat Completions**: 3
- **Legacy APIs**: 3
- **Agents and Automation**: 4
- **Specialized Capabilities**: 4
- **Cross-Cutting Guides**: 8
- **Gap Topics**: 12
- **New Topics (IN93+)**: 5

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 13:10]**
- Fixed: Date formats to YYYY-MM/YYYY-MM-DD throughout
- Fixed: Stale descriptions (IN16, IN67, IN71, IN75, IN28)
- Added: New Topics IN93+ section (5 files)
- Fixed: Topic Count (80 → 97)
- Removed: "[Skeletal]" placeholder

**[2026-07-13 12:00]**
- Updated: Summary for GPT-5.6 flagship (replaces GPT-5.5)
- Updated: Topic count to 85 (19 categories) + 12 gap topics = 97 files total
- Added: SDK v2.45.0 reference
- Added: June-2026-07 changes in summary paragraph
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 09:30]**
- Initial skeletal Summary created with 80 topics in 18 categories
- Based on 74-topic structure from 2026-03-20, added 6 new topics:
  - IN75: GPT-5.5 / Latest Model Guide
  - IN77: Realtime Translate / Whisper
  - IN78: Compaction
  - IN80: Admin Permissions / Retention / Spend Alerts
- Updated existing topic descriptions for GPT-5.5, GPT Image 2, deprecations
- Summary section is skeletal, to be finalized in Phase 4
