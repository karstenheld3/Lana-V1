# INFO: Image Generation

**Doc ID**: GROKAPI-IN23
**Goal**: Grok Imagine image generation, parameters, editing, inpainting, pricing
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok API provides image generation via the `grok-imagine` model family using `POST /v1/images/generations`. Generates images from text prompts with configurable parameters. The API also supports image editing and inpainting. Compatible with OpenAI's image generation endpoint format. Images are returned as URLs or base64-encoded data. Content moderation is applied to all generated images. [VERIFIED] (GROKAPI-SC-XAI-IMAGEGEN | https://docs.x.ai/developers/model-capabilities/images/generation)

## Key Facts

- [VERIFIED] Model: `grok-imagine` (GROKAPI-SC-XAI-IMAGEGEN)
- [VERIFIED] Endpoint: `POST /v1/images/generations` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Editing endpoint: `POST /v1/images/edits` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Content moderation applied to all generated images (GROKAPI-SC-XAI-IMAGEGEN)
- [VERIFIED] Rate limit increases for Imagine API require email request (GROKAPI-SC-XAI-RATELIMITS)

## Quick Reference

- **Generation**: `POST /v1/images/generations`
- **Editing**: `POST /v1/images/edits`
- **Model**: `grok-imagine`
- **Output**: URL or base64

## Examples

### Basic Image Generation (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.images.generate(
    model="grok-imagine",
    prompt="A serene mountain landscape at sunset with a crystal-clear lake in the foreground",
    n=1,
)

print(response.data[0].url)
```

### cURL

```bash
curl https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine",
    "prompt": "A serene mountain landscape at sunset",
    "n": 1
  }'
```

## Differences from Other APIs

### vs OpenAI (DALL-E)
- **Compatible endpoint**: Same `POST /v1/images/generations` format
- **Different model**: `grok-imagine` vs `dall-e-3`
- **Same SDK**: `client.images.generate()` works for both

### vs Anthropic
- **UNIQUE**: Anthropic has no image generation API

### vs Gemini (Imagen)
- **Similar concept**: Both have text-to-image generation
- **Different API**: Different endpoint structures

## Limitations and Known Issues

- [VERIFIED] Rate limits for Imagine API not covered by automatic tier system (GROKAPI-SC-XAI-RATELIMITS)
- Content moderation may reject some prompts

## Sources

- GROKAPI-SC-XAI-IMAGEGEN | https://docs.x.ai/developers/model-capabilities/images/generation | Accessed: 2026-03-20
- GROKAPI-SC-XAI-RESTREF | https://docs.x.ai/llms.txt | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:05]**
- Initial document created with image generation reference
