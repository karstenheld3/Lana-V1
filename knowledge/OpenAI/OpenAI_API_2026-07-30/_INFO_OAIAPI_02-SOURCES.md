# OpenAI API Documentation Sources

**Doc ID**: OAIAPI-IN02
**Goal**: Master source list for OpenAI API documentation research
**Version scope**: API v1, Documentation date 2026-07-30
**Preflight accuracy**: 8/10 assumptions verified (1 WRONG: GPT-5.5 is new flagship, 1 PARTIAL: computer-use-preview deprecated)

**Depends on:**
- `_INFO_OAIAPI_01-SUMMARY.md [OAIAPI-IN01]` for topic mapping

## Discovery Platforms

- **developers.openai.com** (official API reference) - FREE - primary source
- **platform.openai.com/docs/guides** (official guides) - FREE - primary source (redirects to developers.openai.com)
- **github.com/openai/openai-python** (Python SDK) - FREE - tier 2
- **github.com/openai/openai-agents-python** (Agents SDK) - FREE - tier 2
- **github.com/openai/openai-cookbook** (examples) - FREE - tier 2
- **community.openai.com** (official forum) - FREE - tier 3
- **stackoverflow.com** (community Q&A) - FREE - tier 3

**Access notes**: `read_url_content` returns Forbidden for platform.openai.com/developers.openai.com. Must use Playwright MCP for scraping. `search_web` works for discovery.

## Tier 1: Official API Reference (developers.openai.com)

### Core Reference

- **OAIAPI-SC-OAI-OVERVIEW**: API Overview (Introduction, Authentication, Debugging, Backwards compatibility)
  - URL: https://developers.openai.com/api/reference/overview
  - Accessed: 2026-05-22

### Responses API

- **OAIAPI-SC-OAI-RESOVW**: Responses API Overview
  - URL: https://developers.openai.com/api/reference/responses/overview
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RESCRT**: POST Create a response
  - URL: https://developers.openai.com/api/reference/resources/responses/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RESGET**: GET Retrieve a response
  - URL: https://developers.openai.com/api/reference/resources/responses/methods/retrieve
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RESDEL**: DELETE Delete a response
  - URL: https://developers.openai.com/api/reference/resources/responses/methods/delete
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RESINP**: GET List input items
  - URL: https://developers.openai.com/api/reference/resources/responses/subresources/input_items/methods/list
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RESTOK**: POST Count input tokens
  - URL: https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RESCAN**: POST Cancel a response
  - URL: https://developers.openai.com/api/reference/resources/responses/methods/cancel
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RESCMP**: POST Compact a response
  - URL: https://developers.openai.com/api/reference/resources/responses/methods/compact
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RESSTR**: Streaming events
  - URL: https://developers.openai.com/api/reference/resources/responses/streaming-events
  - Accessed: 2026-05-22

### Conversations API

- **OAIAPI-SC-OAI-CNVCRT**: POST Create a conversation
  - URL: https://developers.openai.com/api/reference/resources/conversations/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-CNVGET**: GET Retrieve a conversation
  - URL: https://developers.openai.com/api/reference/resources/conversations/methods/retrieve
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-CNVUPD**: POST Update a conversation
  - URL: https://developers.openai.com/api/reference/resources/conversations/methods/update
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-CNVDEL**: DELETE Delete a conversation
  - URL: https://developers.openai.com/api/reference/resources/conversations/methods/delete
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-CNVITM**: Conversation Items (CRUD + List)
  - URL: https://developers.openai.com/api/reference/resources/conversations/subresources/items/methods/create
  - Accessed: 2026-05-22

### Webhooks

- **OAIAPI-SC-OAI-WBHEVT**: Webhook Events
  - URL: https://developers.openai.com/api/reference/resources/webhooks
  - Accessed: 2026-05-22

### Audio

- **OAIAPI-SC-OAI-AUDTRN**: POST Create a transcription
  - URL: https://developers.openai.com/api/reference/resources/audio/subresources/transcriptions/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-AUDTRL**: POST Create a translation
  - URL: https://developers.openai.com/api/reference/resources/audio/subresources/translations/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-AUDSPK**: POST Create a speech
  - URL: https://developers.openai.com/api/reference/resources/audio/subresources/speech/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-AUDVOI**: POST Create a voice
  - URL: https://developers.openai.com/api/reference/resources/audio/subresources/voices/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-AUDVCS**: Voice Consents (CRUD + List)
  - URL: https://developers.openai.com/api/reference/resources/audio/subresources/voice_consents/methods/create
  - Accessed: 2026-05-22

### Videos

- **OAIAPI-SC-OAI-VIDCRT**: POST Create a video
  - URL: https://developers.openai.com/api/reference/resources/videos/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-VIDCHR**: Video Characters (Create, Get)
  - URL: https://developers.openai.com/api/reference/resources/videos/methods/create_character
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-VIDGET**: GET Retrieve / DELETE Delete / GET List / Download Content
  - URL: https://developers.openai.com/api/reference/resources/videos/methods/retrieve
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-VIDEDT**: Edit / Extend / Remix
  - URL: https://developers.openai.com/api/reference/resources/videos/methods/edit
  - Accessed: 2026-05-22

### Images

- **OAIAPI-SC-OAI-IMGGEN**: POST Generate an Image
  - URL: https://developers.openai.com/api/reference/resources/images/methods/generate
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-IMGEDT**: POST Edit an Image
  - URL: https://developers.openai.com/api/reference/resources/images/methods/edit
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-IMGVAR**: POST Create Variation
  - URL: https://developers.openai.com/api/reference/resources/images/methods/create_variation
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-IMGSTR**: Image generation/edit streaming events
  - URL: https://developers.openai.com/api/reference/resources/images/generation-streaming-events
  - Accessed: 2026-05-22

### Embeddings

- **OAIAPI-SC-OAI-EMBCRT**: POST Create an embedding
  - URL: https://developers.openai.com/api/reference/resources/embeddings/methods/create
  - Accessed: 2026-05-22

### Evals

- **OAIAPI-SC-OAI-EVLAPI**: Evals API (CRUD + List, Runs, Output Items)
  - URL: https://developers.openai.com/api/reference/resources/evals/methods/create
  - Accessed: 2026-05-22

### Fine Tuning

- **OAIAPI-SC-OAI-FTJOBS**: Fine-tuning Jobs (CRUD + List + Events + Cancel + Pause + Resume)
  - URL: https://developers.openai.com/api/reference/resources/fine_tuning/subresources/jobs/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-FTCKPT**: Fine-tuning Checkpoints + Permissions
  - URL: https://developers.openai.com/api/reference/resources/fine_tuning/subresources/jobs/subresources/checkpoints/methods/list
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-FTGRAD**: Graders (Run, Validate)
  - URL: https://developers.openai.com/api/reference/resources/fine_tuning/subresources/alpha/subresources/graders/methods/run
  - Accessed: 2026-05-22

### Batch

- **OAIAPI-SC-OAI-BTCAPI**: Batch API (CRUD + List + Cancel)
  - URL: https://developers.openai.com/api/reference/resources/batches/methods/create
  - Accessed: 2026-05-22

### Files

- **OAIAPI-SC-OAI-FILAPI**: Files API (CRUD + List + Content)
  - URL: https://developers.openai.com/api/reference/resources/files/methods/list
  - Accessed: 2026-05-22

### Uploads

- **OAIAPI-SC-OAI-UPLAPI**: Uploads API (Create, Cancel, Complete, Parts)
  - URL: https://developers.openai.com/api/reference/resources/uploads/methods/create
  - Accessed: 2026-05-22

### Models

- **OAIAPI-SC-OAI-MODAPI**: Models API (Retrieve, Delete, List)
  - URL: https://developers.openai.com/api/reference/resources/models/methods/list
  - Accessed: 2026-05-22

### Moderations

- **OAIAPI-SC-OAI-MODRT**: POST Create a moderation
  - URL: https://developers.openai.com/api/reference/resources/moderations/methods/create
  - Accessed: 2026-05-22

### Vector Stores

- **OAIAPI-SC-OAI-VSAPI**: Vector Stores API (CRUD + List + Search)
  - URL: https://developers.openai.com/api/reference/resources/vector_stores/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-VSFIL**: Vector Store Files (CRUD + List + Content)
  - URL: https://developers.openai.com/api/reference/resources/vector_stores/subresources/files/methods/list
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-VSFBT**: Vector Store File Batches (Create, Retrieve, List Files, Cancel)
  - URL: https://developers.openai.com/api/reference/resources/vector_stores/subresources/file_batches/methods/create
  - Accessed: 2026-05-22

### ChatKit (Beta)

- **OAIAPI-SC-OAI-CKSESS**: ChatKit Sessions (Create, Cancel)
  - URL: https://developers.openai.com/api/reference/resources/beta/subresources/chatkit/subresources/sessions/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-CKTHR**: ChatKit Threads (Retrieve, Delete, List Items, List)
  - URL: https://developers.openai.com/api/reference/resources/beta/subresources/chatkit/subresources/threads/methods/list
  - Accessed: 2026-05-22

### Containers

- **OAIAPI-SC-OAI-CNTAPI**: Containers API (CRUD + List)
  - URL: https://developers.openai.com/api/reference/resources/containers/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-CNTFIL**: Container Files (CRUD + List + Content)
  - URL: https://developers.openai.com/api/reference/resources/containers/subresources/files/methods/list
  - Accessed: 2026-05-22

### Skills

- **OAIAPI-SC-OAI-SKLAPI**: Skills API (CRUD + List + Content + Versions)
  - URL: https://developers.openai.com/api/reference/resources/skills/methods/create
  - Accessed: 2026-05-22

### Realtime

- **OAIAPI-SC-OAI-RTTRNSL**: Realtime Translations (CRUD + List) [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/reference/resources/realtime/subresources/translations/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RTCLNT**: Client Secrets (Create)
  - URL: https://developers.openai.com/api/reference/resources/realtime/subresources/client_secrets/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RTCALL**: Calls (Create, Retrieve, List)
  - URL: https://developers.openai.com/api/reference/resources/realtime/subresources/calls/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RTCLEV**: Client events
  - URL: https://developers.openai.com/api/reference/resources/realtime/client-events
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-RTSREV**: Server events
  - URL: https://developers.openai.com/api/reference/resources/realtime/server-events
  - Accessed: 2026-05-22

### Administration

- **OAIAPI-SC-OAI-ADMOVW**: Administration Overview
  - URL: https://developers.openai.com/api/reference/administration/overview
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-ADMKEY**: Admin API Keys (CRUD + List) [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/admin_api_keys/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-ADMORG**: Organization (Invites, Audit Logs, Usage, Costs, Users, Groups, Roles, Certificates)
  - URL: https://developers.openai.com/api/reference/resources/admin/subresources/organization
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-ADMPRJ**: Projects (CRUD + Archive + Users + Service Accounts + API Keys + Rate Limits + Groups + Certificates + Roles)
  - URL: https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/projects/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-ADMMDL**: Projects > Model Permissions (Retrieve, Update, Delete) [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/projects/subresources/model_permissions/methods/retrieve
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-ADMHTL**: Projects > Hosted Tool Permissions (Retrieve, Update) [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/projects/subresources/hosted_tool_permissions/methods/retrieve
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-ADMDRT**: Projects > Data Retention (Retrieve, Update) [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/projects/subresources/data_retention/methods/retrieve
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-ADMSPN**: Projects > Spend Alerts (CRUD + List) [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/projects/subresources/spend_alerts/methods/create
  - Accessed: 2026-05-22

### Chat Completions

- **OAIAPI-SC-OAI-CHTCRT**: POST Create a chat completion
  - URL: https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-CHTLST**: GET List / GET Retrieve / POST Update / DELETE Delete chat completions
  - URL: https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/list
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-CHTSTR**: Streaming events
  - URL: https://developers.openai.com/api/reference/resources/chat/subresources/completions/streaming-events
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-CHTMSG**: List messages
  - URL: https://developers.openai.com/api/reference/resources/chat/subresources/completions/subresources/messages/methods/list
  - Accessed: 2026-05-22

### Legacy

- **OAIAPI-SC-OAI-LGRTBM**: Realtime Beta (removed 2026-05-12)
  - URL: https://developers.openai.com/api/reference/realtime-beta/overview
  - Accessed: 2026-05-22
  - Status: REMOVED

- **OAIAPI-SC-OAI-LGASST**: Assistants API (Beta - deprecated, sunset 2026-08-26)
  - URL: https://developers.openai.com/api/reference/resources/beta/subresources/assistants/methods/create
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-LGCOMP**: Legacy Completions
  - URL: https://developers.openai.com/api/reference/resources/completions/methods/create
  - Accessed: 2026-05-22

## Tier 2: Official Guides (developers.openai.com/api/docs)

- **OAIAPI-SC-OAI-GFNCAL**: Function Calling Guide
  - URL: https://developers.openai.com/api/docs/guides/function-calling
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GSTRCT**: Structured Outputs Guide
  - URL: https://developers.openai.com/api/docs/guides/structured-outputs
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GTOOLS**: Using Tools Guide
  - URL: https://developers.openai.com/api/docs/guides/tools
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GWBSRC**: Web Search Guide
  - URL: https://developers.openai.com/api/docs/guides/tools-web-search
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GDEEP**: Deep Research Guide
  - URL: https://developers.openai.com/api/docs/guides/deep-research
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GREASN**: Reasoning Models Guide
  - URL: https://developers.openai.com/api/docs/guides/reasoning
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GMIGRR**: Migrate to Responses API Guide
  - URL: https://developers.openai.com/api/docs/guides/migrate-to-responses
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GVIDEO**: Video Generation Guide (Sora)
  - URL: https://developers.openai.com/api/docs/guides/video-generation
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GIMAGE**: Image Generation Guide (GPT Image, DALL-E)
  - URL: https://developers.openai.com/api/docs/guides/image-generation
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GAUDIO**: Audio and Speech Guide
  - URL: https://developers.openai.com/api/docs/guides/audio
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GRTAPI**: Realtime API Guide
  - URL: https://developers.openai.com/api/docs/guides/realtime
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GRTTRL**: Realtime Translation Guide [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/guides/realtime-translation
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GRTMDL**: Realtime Models Prompting Guide [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/guides/realtime-models-prompting
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GBATCH**: Batch API Guide
  - URL: https://developers.openai.com/api/docs/guides/batch
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GFNTN**: Fine-tuning Guide
  - URL: https://developers.openai.com/api/docs/guides/fine-tuning
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GRFT**: Reinforcement Fine-tuning Guide
  - URL: https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GMODR**: Moderation Guide
  - URL: https://developers.openai.com/api/docs/guides/moderation
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GRLMT**: Rate Limits Guide
  - URL: https://developers.openai.com/api/docs/guides/rate-limits
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GERROR**: Error Codes Guide
  - URL: https://developers.openai.com/api/docs/guides/error-codes
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GPRMPT**: Prompt Engineering Guide
  - URL: https://developers.openai.com/api/docs/guides/prompt-engineering
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GCHATK**: ChatKit Guide
  - URL: https://developers.openai.com/api/docs/guides/chatkit
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GCKWDG**: ChatKit Widgets Guide
  - URL: https://developers.openai.com/api/docs/guides/chatkit-widgets
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GLATEST**: Using GPT-5.5 Guide (updated from GPT-5.2) [UPDATED 2026-05-22]
  - URL: https://developers.openai.com/api/docs/guides/latest-model
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GMODLS**: Models Overview
  - URL: https://developers.openai.com/api/docs/models
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GPRICE**: Pricing
  - URL: https://developers.openai.com/api/docs/pricing
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GCHLOG**: Changelog
  - URL: https://developers.openai.com/api/docs/changelog
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GDEPR**: Deprecations
  - URL: https://developers.openai.com/api/docs/deprecations
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GOVRVW**: Platform Overview
  - URL: https://developers.openai.com/api/docs/overview
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GCODGN**: Code Generation Guide
  - URL: https://developers.openai.com/api/docs/guides/code-generation
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GSHELL**: Shell Tool Guide
  - URL: https://developers.openai.com/api/docs/guides/tools-shell
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GAGENT**: Agents Overview Guide
  - URL: https://developers.openai.com/api/docs/guides/agents
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GCMPTU**: Computer Use Guide
  - URL: https://developers.openai.com/api/docs/guides/tools-computer-use
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GMCP**: MCP and Connectors Guide
  - URL: https://developers.openai.com/api/docs/guides/tools-connectors-mcp
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GFILIN**: File Inputs Guide
  - URL: https://developers.openai.com/api/docs/guides/file-inputs
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GVOICE**: Voice Agents Guide
  - URL: https://developers.openai.com/api/docs/guides/voice-agents
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GWSMOD**: WebSocket Mode Guide
  - URL: https://developers.openai.com/api/docs/guides/websocket-mode
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GPCACH**: Prompt Caching Guide
  - URL: https://developers.openai.com/api/docs/guides/prompt-caching
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GBKGND**: Background Mode Guide
  - URL: https://developers.openai.com/api/docs/guides/background
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GFLEX**: Flex Processing Guide
  - URL: https://developers.openai.com/api/docs/guides/flex-processing
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GSAFTY**: Safety Best Practices Guide
  - URL: https://developers.openai.com/api/docs/guides/safety-best-practices
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GYDATA**: Your Data Guide
  - URL: https://developers.openai.com/api/docs/guides/your-data
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GOPTIM**: Model Optimization Guide
  - URL: https://developers.openai.com/api/docs/guides/model-optimization
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GPRMGD**: Prompt Guidance
  - URL: https://developers.openai.com/api/docs/guides/prompt-guidance
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GEVLBP**: Evaluation Best Practices Guide
  - URL: https://developers.openai.com/api/docs/guides/evaluation-best-practices
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GCNVST**: Conversation State Guide
  - URL: https://developers.openai.com/api/docs/guides/conversation-state
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GCMPCT**: Compaction Guide [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/guides/compaction
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GSCMCP**: Secure MCP Tunnels Guide [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/guides/secure-mcp-tunnels
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-GADMSK**: Admin APIs Guide [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/guides/admin-apis
  - Accessed: 2026-05-22

### Tier 2: Model Pages

- **OAIAPI-SC-OAI-MGP55**: GPT-5.5 Model Page [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/models/gpt-5.5
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-MGP55P**: GPT-5.5 Pro Model Page [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/models/gpt-5.5-pro
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-MGIMG2**: GPT Image 2 Model Page [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/models/gpt-image-2
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-MGRT2**: GPT Realtime 2 Model Info [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/models
  - Note: Model info within models overview page
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-MGRTW**: GPT Realtime Whisper Model Page [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/models/gpt-realtime-whisper
  - Accessed: 2026-05-22

- **OAIAPI-SC-OAI-MGCHAT**: chat-latest Model Page [NEW 2026-05-22]
  - URL: https://developers.openai.com/api/docs/models/chat-latest
  - Accessed: 2026-05-22

## Tier 2: GitHub Repositories

- **OAIAPI-SC-GH-SDKPY**: openai-python (Official Python SDK)
  - URL: https://github.com/openai/openai-python
  - Accessed: 2026-05-22

- **OAIAPI-SC-GH-AGNTPY**: openai-agents-python (Agents SDK)
  - URL: https://github.com/openai/openai-agents-python
  - Accessed: 2026-05-22

- **OAIAPI-SC-GH-SDKREL**: openai-python Releases
  - URL: https://github.com/openai/openai-python/releases
  - Accessed: 2026-05-22

## Tier 3: Community Sources

[pending - to be collected during Phase 3 as needed per topic]

## Related APIs/Technologies

- **Anthropic API** - Primary competitor, Messages API pattern
  - URL: https://docs.anthropic.com/en/docs/
  - Relation: Direct alternative for LLM API access, different auth pattern (x-api-key)

- **Google Gemini API** - Primary competitor, generateContent pattern
  - URL: https://ai.google.dev/api
  - Relation: Direct alternative, OpenAI-compatible layer available

- **Grok API (xAI)** - Competitor, OpenAI SDK-compatible
  - URL: https://docs.x.ai
  - Relation: Uses OpenAI-compatible endpoints (/v1/chat/completions, /v1/responses)

- **Azure OpenAI** - Microsoft-hosted OpenAI models
  - URL: https://learn.microsoft.com/en-us/azure/ai-services/openai/
  - Relation: Same models, different hosting/auth/endpoints, enterprise features

## Sources Added During /improve Review

- **OAIAPI-SC-OAI-GPROUT**: Predicted Outputs guide
  - URL: https://developers.openai.com/api/docs/guides/predicted-outputs
- **OAIAPI-SC-OAI-GAGTBL**: Agent Builder guide
  - URL: https://developers.openai.com/api/docs/guides/agent-builder
- **OAIAPI-SC-OAI-GACTN**: Actions (GPT Actions) guide
  - URL: https://developers.openai.com/api/docs/actions/introduction
- **OAIAPI-SC-OAI-GPRIO**: Priority Processing guide
  - URL: https://developers.openai.com/api/docs/guides/priority-processing
- **OAIAPI-SC-OAI-GDEPLC**: Deployment Checklist guide
  - URL: https://developers.openai.com/api/docs/guides/deployment-checklist
- **OAIAPI-SC-OAI-GCITN**: Citation Formatting guide
  - URL: https://developers.openai.com/api/docs/guides/citation-formatting
- **OAIAPI-SC-OAI-GDEVMD**: Developer Mode guide
  - URL: https://developers.openai.com/api/docs/guides/developer-mode
- **OAIAPI-SC-OAI-GLSHLL**: Local Shell tool guide
  - URL: https://developers.openai.com/api/docs/guides/tools-local-shell
- **OAIAPI-SC-OAI-GAPTCH**: Apply Patch tool guide
  - URL: https://developers.openai.com/api/docs/guides/tools-apply-patch
- **OAIAPI-SC-OAI-GVFT**: Vision Fine-Tuning guide
  - URL: https://developers.openai.com/api/docs/guides/vision-fine-tuning
- **OAIAPI-SC-OAI-GSAFCK**: Safety Checks guide
  - URL: https://developers.openai.com/api/docs/guides/safety-checks
- **OAIAPI-SC-OAI-GAGEVAL**: Evaluate Agent Workflows guide
  - URL: https://developers.openai.com/api/docs/guides/agent-evals
- **OAIAPI-SC-OAI-GMCPDR**: MCP for Deep Research
  - URL: https://developers.openai.com/api/docs/mcp
- **OAIAPI-SC-OAI-GRTVAD**: Realtime Voice Activity Detection guide
  - URL: https://developers.openai.com/api/docs/guides/realtime-vad
- **OAIAPI-SC-OAI-GRTCST**: Realtime Managing Costs guide
  - URL: https://developers.openai.com/api/docs/guides/realtime-costs
- **OAIAPI-SC-OAI-GRTMCP**: Realtime with Tools/MCP guide
  - URL: https://developers.openai.com/api/docs/guides/realtime-mcp
- **OAIAPI-SC-OAI-GRTSCR**: Realtime Server Controls guide
  - URL: https://developers.openai.com/api/docs/guides/realtime-server-controls
- **OAIAPI-SC-OAI-GRTCNV**: Realtime Managing Conversations guide
  - URL: https://developers.openai.com/api/docs/guides/realtime-conversations

## Source Count

- **Tier 1 (Official API Reference)**: 49 source entries (+7 new)
- **Tier 2 (Official Guides)**: 69 source entries (+24 new, includes 18 from /improve review)
- **Tier 2 (Model Pages)**: 6 source entries (+6 new)
- **Tier 2 (GitHub)**: 3 source entries
- **Tier 3 (Community)**: pending
- **Total**: 127 sources (+37 new vs 2026-03-20)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 13:15]**
- Added: 18 new guide sources from /improve sidebar review
- Updated: Source count from 109 to 127

**[2026-05-22 09:20]**
- Initial source collection for 2026-05-22 update
- Based on 90 sources from 2026-03-20 baseline
- Added: 19 new sources across Tier 1/2
- Total: 109 sources
