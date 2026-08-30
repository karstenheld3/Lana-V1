# INFO: Image Understanding

**Doc ID**: GROKAPI-IN22
**Goal**: Vision capabilities, multimodal input, base64/URL images, detail levels, chat with files
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Grok supports image understanding (vision) through multimodal input in both Chat Completions and Responses APIs. Images can be passed as base64-encoded data or URLs in content arrays with `image_url` type. Supports `detail` parameter ("high"/"low"/"auto") for controlling analysis depth. Multiple images can be included in a single message. Vision is supported by models with vision capability (e.g., grok-2-vision-1212, grok-4.20). The `view_image` tool enables automatic image analysis from web/X search results without direct user input. Image tokens are billed based on resolution and detail level. Compatible with OpenAI's vision input format. [VERIFIED] (GROKAPI-SC-XAI-IMAGEUND | https://docs.x.ai/developers/model-capabilities/images/understanding)

## Key Facts

- [VERIFIED] Input format: `image_url` content part with `url` field (base64 or URL) (GROKAPI-SC-XAI-IMAGEUND)
- [VERIFIED] Detail levels: "high", "low", "auto" (GROKAPI-SC-XAI-IMAGEUND)
- [VERIFIED] Multiple images per message supported (GROKAPI-SC-XAI-IMAGEUND)
- [VERIFIED] `view_image` tool for search result images (no invocation fee, token-based) (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Image tokens tracked in `usage.prompt_tokens_details.image_tokens` (GROKAPI-SC-XAI-RESTREF)

## Quick Reference

- **Input type**: `image_url` in content array
- **URL formats**: `https://...` or `data:image/jpeg;base64,...`
- **Detail**: `"high"` (detailed), `"low"` (fast), `"auto"` (model decides)
- **Token tracking**: `prompt_tokens_details.image_tokens`

## Examples

### Image from URL (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": "https://example.com/photo.jpg", "detail": "high"}},
            {"type": "text", "text": "Describe what you see in this image."},
        ],
    }],
)
print(response.output_text)
```

### Image from Base64

```python
import base64

with open("photo.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": "What is in this image?"},
        ],
    }],
)
```

### Multiple Images

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": "https://example.com/img1.jpg"}},
            {"type": "image_url", "image_url": {"url": "https://example.com/img2.jpg"}},
            {"type": "text", "text": "Compare these two images."},
        ],
    }],
)
```

## Differences from Other APIs

### vs OpenAI
- **Compatible format**: Same `image_url` content part structure
- **Same detail levels**: high, low, auto
- **Same SDK**: `content` array with mixed types

### vs Anthropic
- **Different format**: Anthropic uses `image` content block with `source.type: "base64"` or `source.type: "url"`
- **Different detail**: Anthropic has no explicit detail parameter

### vs Gemini
- **Different format**: Gemini uses `inlineData` with `mimeType` and `data` fields

## Sources

- GROKAPI-SC-XAI-IMAGEUND | https://docs.x.ai/developers/model-capabilities/images/understanding | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:10]**
- Initial document created with image understanding reference and examples
