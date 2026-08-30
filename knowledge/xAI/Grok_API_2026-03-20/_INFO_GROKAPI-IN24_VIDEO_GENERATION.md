# INFO: Video Generation

**Doc ID**: GROKAPI-IN24
**Goal**: Video generation, image-to-video, editing, polling, configuration, pricing
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Video generation is a **UNIQUE Grok feature** (no equivalent endpoint in OpenAI or Anthropic APIs). The `grok-imagine-video` model generates videos from text prompts or from image+text input. Videos can be up to 15 seconds for generation and 8.7 seconds for editing input videos. Available resolutions: 480p and 720p. The xAI SDK provides a synchronous `client.video.generate()` method that handles polling internally. For the REST API, generation is asynchronous: POST to create the job, then poll until completion. Generated URLs are ephemeral and should not be used for long-term storage. Videos are subject to content moderation - check `response.respect_moderation` to verify. Per-second pricing applies; longer videos cost more. Error handling via `VideoGenerationError` exception with code and message. [VERIFIED] (GROKAPI-SC-XAI-VIDEOGEN | https://docs.x.ai/developers/model-capabilities/video/generation)

## Key Facts

- [VERIFIED] Model: `grok-imagine-video` (GROKAPI-SC-XAI-VIDEOGEN)
- [VERIFIED] Max duration: 15 seconds (generation), 8.7 seconds (editing input) (GROKAPI-SC-XAI-VIDEOGEN)
- [VERIFIED] Resolutions: 480p or 720p (GROKAPI-SC-XAI-VIDEOGEN)
- [VERIFIED] Generated URLs are ephemeral - not for long-term storage (GROKAPI-SC-XAI-VIDEOGEN)
- [VERIFIED] Content moderation applied to all generated videos (GROKAPI-SC-XAI-VIDEOGEN)
- [VERIFIED] Per-second pricing (GROKAPI-SC-XAI-VIDEOGEN)
- [VERIFIED] xAI SDK: `client.video.generate()` with automatic polling (GROKAPI-SC-XAI-VIDEOGEN)
- [VERIFIED] REST API: asynchronous with polling (GROKAPI-SC-XAI-VIDEOGEN)

## Quick Reference

- **Model**: `grok-imagine-video`
- **Endpoint**: `POST /v1/videos/generations`
- **Max generation duration**: 15 seconds
- **Max editing input duration**: 8.7 seconds
- **Resolutions**: 480p, 720p
- **Pricing**: Per-second
- **URL lifetime**: Ephemeral (download immediately)

## Examples

### Text-to-Video (xAI SDK)

```python
import os
import xai_sdk

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

response = client.video.generate(
    prompt="A cat lounging in a sunbeam, tail gently swishing",
    model="grok-imagine-video",
    duration=5,
)

print(f"Video URL: {response.url}")
print(f"Duration: {response.duration} seconds")
print(f"Model: {response.model}")

if response.respect_moderation:
    print("Video passed moderation")
else:
    print("Video filtered by moderation")
```

### Error Handling

```python
import os
import xai_sdk
from xai_sdk.video import VideoGenerationError

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

try:
    response = client.video.generate(
        prompt="A serene mountain landscape at sunset",
        model="grok-imagine-video",
        duration=5,
    )
    print(response.url)
except VideoGenerationError as e:
    print(f"Generation failed [{e.code}]: {e.message}")
except TimeoutError:
    print("Generation timed out")
```

### cURL (Async with Polling)

```bash
# Step 1: Start generation
curl https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "A cat lounging in a sunbeam",
    "duration": 5
  }'

# Step 2: Poll for result using returned job ID
# curl https://api.x.ai/v1/videos/generations/{job_id} \
#   -H "Authorization: Bearer $XAI_API_KEY"
```

## Response Object

- **`url`** (string): Ephemeral URL to download the generated video
- **`duration`** (number): Actual duration in seconds
- **`model`** (string): Resolved model ID
- **`respect_moderation`** (boolean): Whether the video passed content moderation

## Differences from Other APIs

### vs OpenAI

- **UNIQUE endpoint**: OpenAI has Sora but as a separate product, not integrated into the main API
- **No OpenAI equivalent**: No `POST /v1/videos/generations` in OpenAI API

### vs Anthropic

- **UNIQUE**: No video generation capability in Anthropic API

### vs Gemini

- **Similar concept**: Gemini has Veo for video generation, but with different API patterns
- **xAI advantage**: Integrated into same API with consistent auth and billing

## Limitations and Known Issues

- [VERIFIED] Max duration: 15s generation, 8.7s editing input (GROKAPI-SC-XAI-VIDEOGEN)
- [VERIFIED] URLs are ephemeral - must download immediately (GROKAPI-SC-XAI-VIDEOGEN)
- [VERIFIED] Limited to 480p/720p resolution (GROKAPI-SC-XAI-VIDEOGEN)
- [VERIFIED] Content moderation may reject some prompts (GROKAPI-SC-XAI-VIDEOGEN)

## Sources

- GROKAPI-SC-XAI-VIDEOGEN | https://docs.x.ai/developers/model-capabilities/video/generation | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:25]**
- Initial document created with full video generation reference
