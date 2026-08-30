# INFO: Models and Pricing

**Doc ID**: GROKAPI-IN03
**Goal**: Complete model list, capabilities, pricing, aliases, context windows, and modalities
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

xAI offers multiple model families accessed via the Grok API: language models (Grok 4.20, Grok 4, Grok 3, Grok 3 Mini, Grok 2 Vision), an image generation model (grok-imagine-image), a video generation model (grok-imagine-video), a coding model (grok-code-fast-1), and voice models. The flagship Grok 4.20 has a 2M token context window with function calling, structured outputs, and reasoning. Grok 4 is a pure reasoning model with no non-reasoning mode; it does not support presencePenalty, frequencyPenalty, stop, or reasoning_effort parameters. Pricing uses per-token billing with separate costs for input, output, cached, and reasoning tokens. Server-side tools (web_search, x_search, code_execution, collections_search) have additional per-invocation costs beyond token costs. Batch API provides 50% discount on text/language model tokens. Voice Agent API is billed per minute of connection time. Models use aliases for version management: `<model>` for latest stable, `<model>-latest` for bleeding edge, `<model>-<date>` for pinned versions. Knowledge cutoff for Grok 3 and 4 is November 2024. [VERIFIED] (GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models)

## Key Facts

- [VERIFIED] Grok 4.20: 2M context window, function calling, structured outputs, reasoning, fastest model (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Grok 4: Pure reasoning model, no non-reasoning mode, no presencePenalty/frequencyPenalty/stop/reasoning_effort params (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Grok 4.20 does not support logprobs field (silently ignored) (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Model aliases: `<model>` = latest stable, `<model>-latest` = bleeding edge, `<model>-<date>` = pinned (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Knowledge cutoff: November 2024 for Grok 3 and Grok 4 (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Image input: max 20MiB, jpg/jpeg/png only, no image count limit (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] No role order limitation: system/user/assistant roles in any sequence (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Tool invocation costs are separate from token costs (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Batch API: 50% discount on text/language model tokens only (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Usage guidelines violation fee: $0.05 per request (Responses API) (GROKAPI-SC-XAI-MODELS)

## Quick Reference

### Language Models

- **grok-4.20** (aliases: grok-4.20-beta-latest)
  - Context: 2,000,000 tokens
  - Input: text, image
  - Output: text
  - Features: Function calling, structured outputs, reasoning, non-reasoning variant available
  - Note: Does not support logprobs

- **grok-4** (aliases: grok-4-latest, grok-4-0709)
  - Context: [standard]
  - Input: text
  - Output: text
  - Features: Reasoning (always on)
  - Note: No presencePenalty, frequencyPenalty, stop, reasoning_effort

- **grok-3** (aliases: grok-3-latest, grok-3-beta)
  - Context: [standard]
  - Input: text
  - Output: text
  - Pricing: $3/M input, $15/M output

- **grok-3-mini** (aliases: grok-3-mini-latest, grok-3-mini-beta)
  - Context: [standard]
  - Input: text
  - Output: text
  - Pricing: $0.30/M input, $0.50/M output

- **grok-2-vision-1212**
  - Input: text, image
  - Output: text
  - Pricing: $2/M input (text+image), $10/M output

- **grok-code-fast-1**
  - Input: text
  - Output: text
  - Optimized for coding tasks

### Multi-Agent Models

- **grok-4.20-multi-agent** (aliases: grok-4.20-multi-agent-latest)
  - Orchestrates 4-16 parallel AI agents
  - Built-in tools: web_search, x_search, code_execution, collections_search

### Image Generation Models

- **grok-imagine-image**
  - Input: text, image
  - Output: image
  - Pricing: per generated image token

### Video Generation Models

- **grok-imagine-video**
  - Input: text, image
  - Output: video
  - Pricing: per generated video

### Voice Models

- **Voice Agent API**: Billed per minute of connection time
- **Text to Speech API**: Billed per input character

## Model Endpoints

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")

# List all models (OpenAI-compatible)
models = client.models.list()
for model in models.data:
    print(f"{model.id} (owned by: {model.owned_by})")
```

### Extended Model Info (xAI-specific endpoints)

```bash
# Language models with pricing info
curl https://api.x.ai/v1/language-models \
  -H "Authorization: Bearer $XAI_API_KEY"

# Image generation models
curl https://api.x.ai/v1/image-generation-models \
  -H "Authorization: Bearer $XAI_API_KEY"

# Video generation models
curl https://api.x.ai/v1/video-generation-models \
  -H "Authorization: Bearer $XAI_API_KEY"

# Specific model details
curl https://api.x.ai/v1/language-models/grok-4-0709 \
  -H "Authorization: Bearer $XAI_API_KEY"
```

### Language Model Response Schema

```json
{
  "id": "grok-4-0709",
  "fingerprint": "fp_156d35dcaa",
  "created": 1743724800,
  "object": "model",
  "owned_by": "xai",
  "version": "1.0.0",
  "input_modalities": ["text"],
  "output_modalities": ["text"],
  "prompt_text_token_price": 20000,
  "cached_prompt_text_token_price": 0,
  "prompt_image_token_price": 0,
  "completion_text_token_price": 100000,
  "aliases": ["grok-4", "grok-4-latest"]
}
```

## Tool Invocation Pricing

Server-side tools have per-invocation costs beyond token costs:

- **web_search**: Per-invocation fee
- **x_search**: Per-invocation fee
- **code_execution** / **code_interpreter**: Per-invocation fee
- **attachment_search**: Per-invocation fee (file attachments)
- **collections_search** / **file_search**: Per-invocation fee (RAG)
- **view_image**: No invocation fee, billed for image tokens only
- **view_x_video**: No invocation fee, billed for image tokens only
- **Remote MCP tools**: No invocation fee, billed for tokens only

Note: In gRPC API (Python xAI SDK), `code_interpreter` and `file_search` names are not supported.

## Tokenization

```python
import os
import requests

response = requests.post(
    "https://api.x.ai/v1/tokenize-text",
    headers={
        "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}",
        "Content-Type": "application/json",
    },
    json={"text": "Hello world!", "model": "grok-4-0709"},
)
tokens = response.json()
print(f"Token count: {len(tokens['token_ids'])}")
for t in tokens["token_ids"]:
    print(f"  {t['string_token']} -> {t['token_id']}")
```

Also available via xAI Console Tokenizer: https://console.x.ai/team/default/tokenizer

## Differences from Other APIs

### vs OpenAI

- **Additional model endpoints**: `/v1/language-models`, `/v1/image-generation-models`, `/v1/video-generation-models` (not in OpenAI)
- **Tokenize endpoint**: `/v1/tokenize-text` (OpenAI has tiktoken library instead)
- **No embeddings models**: No text-embedding-* equivalent
- **No fine-tuning**: Cannot create custom models
- **Pricing in model response**: Language model response includes per-token prices
- **Tool invocation costs**: Separate from token costs (OpenAI bundles tool costs into token pricing)

### vs Anthropic

- **Model listing**: REST endpoint vs documentation-only model list
- **No usage tiers**: xAI uses tier-based rate limits, not usage-based pricing tiers
- **Model aliases**: xAI uses `<model>-latest` pattern (Anthropic uses `claude-sonnet-4-*`)

### vs Gemini

- **OpenAI-compatible format**: Model list uses OpenAI schema
- **Separate model endpoints**: Per-modality model listing (language, image, video)
- **Pricing in API**: Model response includes pricing (Gemini pricing is docs-only)

## Limitations and Known Issues

- [VERIFIED] Grok 4 always reasons - no way to disable reasoning (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Grok 4.20 silently ignores logprobs parameter (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] No knowledge of current events without search tools (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Image generation models: max 1024 character prompt (GROKAPI-SC-XAI-RESTREF)

## Sources

- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20
- GROKAPI-SC-XAI-RESTREF | https://docs.x.ai/llms.txt (API ref section) | Accessed: 2026-03-20

## Document History

**[2026-03-20 03:10]**
- Initial document created with model list, pricing, aliases, and tool costs
