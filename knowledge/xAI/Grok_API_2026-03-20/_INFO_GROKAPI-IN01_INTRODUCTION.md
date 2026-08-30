# INFO: Grok API Introduction

**Doc ID**: GROKAPI-IN01
**Goal**: API overview, base URL, versioning, OpenAI SDK compatibility, and getting started
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok API is a RESTful API by xAI providing access to the Grok family of language models, image generation models, and video generation models. The base URL is `https://api.x.ai` with all inference routes under `/v1/`. Authentication uses `Authorization: Bearer <API_KEY>` headers. The API is explicitly designed to be OpenAI SDK compatible - developers can use the OpenAI Python or JavaScript SDK by pointing `base_url` to `https://api.x.ai/v1`. xAI also provides a native Python SDK (`xai-sdk`) with additional features like built-in server-side tools. Two primary text generation interfaces exist: the legacy Chat Completions API (`POST /v1/chat/completions`) and the newer Responses API (`POST /v1/responses`). The Responses API stores responses for 30 days, supports retrieval by ID, and enables multi-turn conversations without repeating context. The API launched in public beta November 2024 with Grok-2 models, progressed through Grok 3 (April 2025) and Grok 4 (July 2025) to the current flagship Grok 4.20 (March 2026). [VERIFIED] (GROKAPI-SC-XAI-OVERVIEW | https://docs.x.ai/overview)

## Key Facts

- [VERIFIED] Base URL: `https://api.x.ai`, all routes under `/v1/` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Authentication: `Authorization: Bearer <xAI API key>` header (GROKAPI-SC-XAI-QUICKSTART)
- [VERIFIED] OpenAI SDK compatible: use `base_url="https://api.x.ai/v1"` with OpenAI Python/JS SDK (GROKAPI-SC-XAI-QUICKSTART)
- [VERIFIED] Native SDK: `pip install xai-sdk` (Python), `npm install ai @ai-sdk/xai` (JS/TS) (GROKAPI-SC-XAI-QUICKSTART)
- [VERIFIED] API key env var: `XAI_API_KEY` (auto-read by SDKs) (GROKAPI-SC-XAI-QUICKSTART)
- [VERIFIED] Two API styles: Chat Completions (legacy) and Responses API (new) (GROKAPI-SC-XAI-GENTEXT)
- [VERIFIED] Responses stored 30 days, retrievable by ID (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Knowledge cutoff: November 2024 for Grok 3 and Grok 4 (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Real-time data requires server-side search tools (web_search, x_search) (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Status page: https://status.x.ai (GROKAPI-SC-XAI-ERRORS)

## Use Cases

- **Chat applications**: Text generation with multi-turn conversation support
- **Agentic workflows**: Tool calling with server-side and client-side tools
- **Real-time information**: Web and X (Twitter) search integration
- **Media generation**: Image and video generation from text prompts
- **Voice applications**: Real-time voice agents via WebSocket API
- **Document analysis**: File upload and chat with document collections

## Quick Reference

- **Base URL**: `https://api.x.ai`
- **Auth header**: `Authorization: Bearer <XAI_API_KEY>`
- **Content-Type**: `application/json`
- **Primary endpoints**:
  - `POST /v1/responses` - Create text response (recommended)
  - `POST /v1/chat/completions` - Legacy chat completion
  - `POST /v1/images/generations` - Generate images
  - `POST /v1/videos/generations` - Generate videos
  - `GET /v1/models` - List available models
- **SDKs**:
  - Python (native): `pip install xai-sdk`
  - Python (OpenAI compat): `pip install openai`
  - JavaScript (native): `npm install ai @ai-sdk/xai`
  - JavaScript (OpenAI compat): `npm install openai`
- **Console**: https://console.x.ai

## Getting Started

### 1. Create Account and API Key

Sign up at https://accounts.x.ai, load credits, then create an API key at https://console.x.ai/team/default/api-keys.

### 2. Set Environment Variable

```bash
export XAI_API_KEY="your_api_key"
```

### 3. Install SDK

```bash
pip install xai-sdk
```

### 4. First Request (xAI SDK)

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(model="grok-4.20-beta-latest-non-reasoning")
chat.append(system("You are a helpful assistant."))
chat.append(user("What is the capital of France?"))

response = chat.sample()
print(response.content)
```

### 5. First Request (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

completion = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
)
print(completion.output_text)
```

### 6. First Request (cURL)

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-4.20-beta-latest-non-reasoning",
    "input": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```

## API Architecture

### Endpoint Categories

- **Inference API** (`/v1/`): Chat, responses, images, videos, models, tokenization
- **Files API** (`/v1/files/`): Upload, manage, download files
- **Collections API** (`/v1/collections/`): Document collections for RAG
- **Batches API** (`/v1/batches/`): Async batch processing
- **Management API** (`/auth/`): API keys, ACLs, audit logs
- **Billing API** (`/v1/billing/`): Billing info, invoices, usage
- **Voice API** (`wss://api.x.ai/v1/realtime`): WebSocket for voice agents

### OpenAI Compatibility

The Grok API implements OpenAI-compatible endpoints. To migrate from OpenAI:

```python
# Change only base_url and api_key
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),  # was OPENAI_API_KEY
    base_url="https://api.x.ai/v1",    # was https://api.openai.com/v1
)
# All existing code works with Grok models
```

**Notable differences from OpenAI**:
- No embeddings endpoint
- No fine-tuning API
- No moderations endpoint
- Server-side tools (web_search, x_search, code_execution) execute on xAI servers
- Additional endpoints: `/v1/language-models`, `/v1/image-generation-models`, `/v1/video-generation-models`, `/v1/tokenize-text`, `/v1/api-key`

## Differences from Other APIs

### vs OpenAI

- **Compatibility**: Explicitly OpenAI SDK compatible; same Chat Completions and Responses API patterns
- **Server-side tools**: web_search, x_search, code_execution run on xAI servers (OpenAI tools are all client-side except built-in file_search/code_interpreter in Assistants)
- **No Assistants API**: Use Responses API with stored context instead
- **No embeddings**: No text embedding endpoint
- **No fine-tuning**: No custom model training
- **X Search**: Unique access to X (Twitter) data
- **Multi-Agent**: Built-in multi-agent orchestration (no OpenAI equivalent)

### vs Anthropic

- **Auth**: Bearer token (not x-api-key header)
- **Message format**: OpenAI-compatible messages array (not Anthropic message format)
- **System prompt**: In messages array as system role (not separate parameter)
- **No extended thinking**: Reasoning tokens are encrypted, not exposed as thinking blocks
- **Caching**: Uses conv-id/prompt_cache_key (not cache_control blocks)

### vs Gemini

- **Base URL**: REST at api.x.ai (not generativelanguage.googleapis.com)
- **Auth**: Bearer token (not x-goog-api-key)
- **Endpoint style**: OpenAI-compatible paths (not model:generateContent)
- **Code execution**: Similar built-in Python sandbox
- **Web search**: Similar grounding capability via web_search tool

## Limitations and Known Issues

- [VERIFIED] Knowledge cutoff November 2024 without search tools enabled (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Image input: max 20MiB per image, jpg/jpeg/png only (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Usage guidelines violations incur $0.05 fee per request (Responses API) (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Model availability varies by geography and account type (GROKAPI-SC-XAI-MODELS)

## Sources

- GROKAPI-SC-XAI-OVERVIEW | https://docs.x.ai/overview | Accessed: 2026-03-20
- GROKAPI-SC-XAI-QUICKSTART | https://docs.x.ai/developers/quickstart | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20
- GROKAPI-SC-XAI-ERRORS | https://docs.x.ai/developers/debugging-errors | Accessed: 2026-03-20
- GROKAPI-SC-XAI-RESTREF | https://docs.x.ai/docs/api-reference | Accessed: 2026-03-20

## Document History

**[2026-03-20 03:05]**
- Initial document created with full API overview and getting started guide
