# Image Streaming

**Doc ID**: OAIAPI-IN22
**Goal**: Document SSE streaming for image generation - partial image events, progressive rendering
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Image streaming delivers image generation results incrementally via Server-Sent Events (SSE). When `stream: true` is set, the API sends partial image data as the image generates, enabling progressive rendering. Compatible with gpt-image-1 and gpt-image-1.5 models. GPT Image 2 does NOT support streaming. The Responses API also supports image streaming with the `image_generation` tool. Edit streaming events added 2026-03. [VERIFIED] (OAIAPI-SC-OAI-IMGSTR)

## Key Facts

- **Enable**: `stream: true` on image generation/editing requests [VERIFIED]
- **Protocol**: Server-Sent Events (SSE) [VERIFIED]
- **Progressive**: Partial images at increasing quality [VERIFIED]
- **Models**: gpt-image-1, gpt-image-1.5 (NOT GPT Image 2) [VERIFIED]
- **Responses API**: Streaming with image_generation tool [VERIFIED]

## SDK Examples (Python)

### Stream Image Generation

```python
from openai import OpenAI

client = OpenAI()

stream = client.images.generate(
    model="gpt-image-1",
    prompt="A serene mountain landscape at sunset with a lake reflection",
    size="1024x1024",
    stream=True
)

for event in stream:
    if event.type == "image.partial":
        partial_b64 = event.data
        print(f"Partial: {len(partial_b64)} bytes")
    elif event.type == "image.done":
        final_b64 = event.data
        print(f"Complete: {len(final_b64)} bytes")
```

### Stream via Responses API

```python
from openai import OpenAI

client = OpenAI()

stream = client.responses.create(
    model="gpt-5.6-sol",
    tools=[{"type": "image_generation"}],
    input="Generate an image of a futuristic city skyline",
    stream=True
)

for event in stream:
    if event.type == "response.image_generation.partial":
        print(f"Generating... {event.partial_image_index}")
    elif event.type == "response.image_generation.done":
        import base64
        img_bytes = base64.b64decode(event.result)
        with open("city.png", "wb") as f:
            f.write(img_bytes)
        print("Image saved")
```

## Error Responses

- **400 Bad Request** - Invalid prompt or parameters
- **429 Too Many Requests** - Rate limit exceeded
- **SSE error event** - Generation failed mid-stream

## Differences from Other APIs

- **vs Anthropic**: No image generation or streaming
- **vs Gemini Imagen**: Gemini supports image generation but streaming details differ
- **vs Non-streaming**: Streaming adds progressive rendering; non-streaming waits for complete image

## Limitations and Known Issues

- **Partial quality**: Early partial images are low resolution/quality [VERIFIED]
- **Stream interruption**: If connection drops, partial data is lost [ASSUMED]
- **GPT Image 2**: Does NOT support streaming [VERIFIED]

## TypeScript Examples

### Generate Image

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const result = await client.images.generate({
  model: "gpt-image-1",
  prompt: "A serene landscape with mountains",
  size: "1024x1024",
  n: 1,
});

console.log(result.data[0].b64_json ? "Got base64 image" : result.data[0].url);
```

## Sources

- OAIAPI-SC-OAI-IMGSTR - Image Streaming Reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 15:05]**
- Enriched: Full key facts, SDK examples, error responses, limitations from 2026-03-20
- Updated: Model refs to gpt-5.5 in Responses API example
- Added: GPT Image 2 non-support note

**[2026-05-22 11:40]**
- Stub created
