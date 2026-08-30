# INFO: Gemini API Video Generation

**Doc ID**: GEMAPI-IN30
**Goal**: Document Veo models for video generation, parameters, and output handling
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini API offers video generation through Veo models. **Veo 3.1** (`veo-3.1-generate-preview`) generates cinematic 4K video with native synchronized audio from text prompts or image inputs. **Veo 2.0** (`veo-2.0-generate-001`) generates 1080p production-ready video. Video generation is asynchronous - a generation request returns an operation ID that is polled for completion. Generated videos are returned as downloadable URLs. Generation supports text-to-video and image-to-video (using a reference image as the first frame). Parameters include aspect ratio, duration, and number of videos. This is unique to Gemini - neither OpenAI nor Anthropic offer video generation through their APIs.

## Key Facts

- [VERIFIED] Veo 3.1: 4K video with synchronized audio (GEMAPI-SC-GOOG-VEOGEN)
- [VERIFIED] Veo 2.0: 1080p production video (GEMAPI-SC-GOOG-VEOGEN)
- [VERIFIED] Async generation via operations (poll for completion) (GEMAPI-SC-GOOG-VEOGEN)
- [VERIFIED] Text-to-video and image-to-video supported (GEMAPI-SC-GOOG-VEOGEN)
- [VERIFIED] UNIQUE to Gemini - no video gen in OpenAI or Anthropic APIs (GEMAPI-SC-GOOG-VEOGEN)

## Quick Reference

**Models**: `veo-3.1-generate-preview`, `veo-2.0-generate-001`
**Method**: `generate_videos()` (async operation)
**Output**: Downloadable video URL

## Python Examples

### Example 1: Text-to-Video

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

operation = client.models.generate_videos(
    model="veo-2.0-generate-001",
    prompt="A drone shot flying over a tropical island at sunset, cinematic quality",
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        aspect_ratio="16:9",
        duration_seconds=8,
    )
)

# Poll for completion
while not operation.done:
    time.sleep(10)
    operation = client.operations.get(name=operation.name)

# Download result
if operation.result:
    for i, video in enumerate(operation.result.generated_videos):
        print(f"Video URL: {video.video.uri}")
```

### Example 2: Veo 3.1 with Audio

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="A busy coffee shop with jazz music playing, people chatting, espresso machine sounds",
    config=types.GenerateVideosConfig(
        number_of_videos=1,
    )
)

while not operation.done:
    time.sleep(15)
    operation = client.operations.get(name=operation.name)

if operation.result:
    for video in operation.result.generated_videos:
        print(f"4K Video with audio: {video.video.uri}")
```

## Comparison with Other APIs

### vs OpenAI

- **Video generation**: Gemini: Veo 3.1/2.0 | OpenAI: **no video generation API**
- **UNIQUE to Gemini**: Video generation is not available in OpenAI's API

### vs Anthropic

- **Video generation**: Gemini: Veo 3.1/2.0 | Anthropic: **no video generation**
- **UNIQUE to Gemini**: Major differentiator

## Error Responses

- **400**: Invalid parameters (duration, aspect ratio)
- Operation may fail with error details in `operation.error`
- Safety filters may block generated content

## Rate Limiting / Throttling

Video generation has separate rate limits. Generation is resource-intensive and slower than text/image. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Veo 3.1 is preview status (GEMAPI-SC-GOOG-MODELS)
- Generation can take minutes per video
- SynthID watermarking applied to generated videos

## Gotchas and Quirks

- Async operation model - must poll for completion (can take minutes)
- Video URLs are temporary - download promptly
- Veo 3.1 native audio is a major differentiator (synchronized to visual content)
- SynthID watermarking is invisible but detectable
- Duration and resolution options vary by model

## Sources

- GEMAPI-SC-GOOG-VEOGEN: https://ai.google.dev/gemini-api/docs/video-generation [VERIFIED]
- GEMAPI-SC-GOOG-MODELS: https://ai.google.dev/gemini-api/docs/models [VERIFIED]

## Document History

**[2026-03-20 05:10]**
- Initial document created
