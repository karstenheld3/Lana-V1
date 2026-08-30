# Image Generation

**Doc ID**: OAIAPI-IN21
**Goal**: Document image generation and editing via GPT Image 2, gpt-image-1, gpt-image-1-mini
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Image generation is available via `POST /v1/images/generations` (generate) and `POST /v1/images/edits` (edit). GPT Image 2 is the current state-of-the-art model (released 2026-04-21) with 2K resolution, token-based pricing, flexible sizes, high-fidelity image inputs, multilingual text rendering, and Batch API support (50% discount). **DEPRECATED (2026-06-02)**: `gpt-image-1-mini`, `gpt-image-1.5`, and `chatgpt-image-latest` deprecated with removal scheduled 2026-12-01. Migrate to `gpt-image-2` (recommended) or `gpt-image-1`. DALL-E 2 and DALL-E 3 were **removed from the API on 2026-05-12** - any code referencing them will fail with 404 errors. GPT-5.6 adds `original_image_detail` parameter for controlling input image quality. Image generation also supports streaming events for progressive rendering. [VERIFIED] (OAIAPI-SC-OAI-IMGGEN, OAIAPI-SC-OAI-GIMAGE, OAIAPI-SC-OAI-MGIMG2, OAIAPI-SC-OAI-GCHLOG)

## REST API

### Generate an Image

**Endpoint**: `POST /v1/images/generations`

**Request**:

```json
{
  "model": "gpt-image-2",
  "prompt": "A photorealistic landscape of mountains at sunset with a lake reflection",
  "n": 1,
  "size": "1536x1024",
  "quality": "high",
  "output_format": "png"
}
```

**Parameters**:

- **model** (string, required) - `gpt-image-2`, `gpt-image-1`, or `gpt-image-1-mini`
- **prompt** (string, required) - Text description of the image to generate
- **n** (integer, optional) - Number of images to generate. Default: 1
- **size** (string, optional) - Image size. Options vary by model:
  - gpt-image-2: `1024x1024`, `1536x1024`, `1024x1536`, `2048x2048` (and more flexible sizes)
  - gpt-image-1: `1024x1024`, `1024x1536`, `1536x1024`
- **quality** (string, optional) - `standard` or `high`. Default: `standard`
- **output_format** (string, optional) - `png`, `jpeg`, `webp`. Default: `png`

**Response** (`200 OK`):

```json
{
  "created": 1716393600,
  "data": [
    {
      "url": "https://...",
      "revised_prompt": "A photorealistic landscape..."
    }
  ]
}
```

### Edit an Image

**Endpoint**: `POST /v1/images/edits`

**Request**: Multipart form data with:

- **model** (string, required) - Model to use
- **image** (file, required) - Source image to edit (PNG, max 4MB)
- **prompt** (string, required) - Edit instruction
- **mask** (file, optional) - Mask indicating regions to edit (PNG with transparent areas)
- **n** (integer, optional) - Number of outputs
- **size** (string, optional) - Output size

### Create Variation

**Endpoint**: `POST /v1/images/variations`

**Note**: Limited model support. Legacy endpoint from DALL-E era.

## SDK Examples (Python)

### Basic Image Generation

```python
from openai import OpenAI

client = OpenAI()

result = client.images.generate(
    model="gpt-image-2",
    prompt="A modern minimalist logo for a tech startup called 'NeuralFlow'",
    size="1024x1024",
    quality="high",
    n=1,
)
print(result.data[0].url)
```

### Image Editing with Mask

```python
from openai import OpenAI

client = OpenAI()

result = client.images.edit(
    model="gpt-image-2",
    image=open("original.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="Replace the sky with a dramatic sunset",
    size="1024x1024",
)
print(result.data[0].url)
```

### Image Generation via Responses API

```python
from openai import OpenAI

client = OpenAI()

# GPT-5.5 with image_generation tool
response = client.responses.create(
    model="gpt-5.6-sol",
    input="Generate a professional headshot photo of a friendly software engineer",
    tools=[{"type": "image_generation"}],
)
# Output contains image data in response items
for item in response.output:
    if hasattr(item, "image_url"):
        print(item.image_url)
```

### Batch Image Generation (50% Discount)

```python
import json
from openai import OpenAI

client = OpenAI()

# Prepare JSONL batch file
requests = [
    {
        "custom_id": f"img-{i}",
        "method": "POST",
        "url": "/v1/images/generations",
        "body": {
            "model": "gpt-image-2",
            "prompt": f"Product photo of item {i} on white background",
            "size": "1024x1024",
            "quality": "high",
        }
    }
    for i in range(10)
]

# Write batch file
with open("image_batch.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# Upload and create batch
batch_file = client.files.create(
    file=open("image_batch.jsonl", "rb"),
    purpose="batch",
)

batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/images/generations",
    completion_window="24h",
)
print(f"Batch ID: {batch.id}")  # 50% discount applied
```

### Download and Save Image

```python
import requests
from openai import OpenAI

client = OpenAI()

result = client.images.generate(
    model="gpt-image-2",
    prompt="An isometric illustration of a smart city",
    size="1536x1024",
)

# Download the image
image_url = result.data[0].url
response = requests.get(image_url)
with open("smart_city.png", "wb") as f:
    f.write(response.content)
print("Image saved to smart_city.png")
```

## Pricing

### GPT Image 2
- Token-based pricing (input text tokens + output image tokens)
- Batch API: 50% discount
- Estimated: $8/MTok input, $30/MTok output (varies by image size)

### gpt-image-1 / gpt-image-1-mini
- Lower-cost alternatives
- gpt-image-1-mini for high-volume, lower-quality needs

### Removed
- DALL-E 3, DALL-E 2: **Removed 2026-05-12** - no longer billable or accessible

## Rate Limits (GPT Image 2)

- **Tier 1**: 100K TPM, 5 IPM (images per minute)
- **Tier 2**: 250K TPM, 20 IPM
- **Tier 3**: 800K TPM, 50 IPM
- **Tier 4**: 3M TPM, 150 IPM
- **Tier 5**: 8M TPM, 250 IPM
- **Free tier**: Not supported

## Error Responses

- **400 Bad Request** - Invalid size, unsupported format, prompt too long
- **404 Not Found** - Model not found (DALL-E 2/3 removed)
- **413 Payload Too Large** - Image file exceeds size limit
- **429 Too Many Requests** - Rate limit exceeded (check IPM limit)

## Gotchas and Quirks

- **DALL-E gone**: `dall-e-2` and `dall-e-3` return 404 since 2026-05-12. Migrate to `gpt-image-2` [VERIFIED]
- **Token pricing**: GPT Image 2 uses token-based pricing unlike DALL-E's per-image pricing. Cost varies by output resolution [VERIFIED]
- **Batch API support**: 50% discount for batch image generation, 24h completion window [VERIFIED]
- **No fine-tuning**: GPT Image 2 does not support fine-tuning [VERIFIED] (OAIAPI-SC-OAI-MGIMG2)
- **No streaming**: GPT Image 2 does not support streaming (separate streaming events endpoint exists for other image models) [VERIFIED]

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

- OAIAPI-SC-OAI-IMGGEN - POST Generate an Image reference
- OAIAPI-SC-OAI-IMGEDT - POST Edit an Image reference
- OAIAPI-SC-OAI-IMGSTR - Image streaming events reference
- OAIAPI-SC-OAI-GIMAGE - Image Generation guide
- OAIAPI-SC-OAI-MGIMG2 - GPT Image 2 model page
- OAIAPI-SC-OAI-GPRICE - Pricing

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: gpt-image-1-mini/1.5/chatgpt-image-latest deprecation notice (2026-06-02, removal 2026-12-01)
- Added: `original_image_detail` parameter (GPT-5.6)
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 10:15]**
- Major update from 2026-03-20 version
- Added: GPT Image 2 as primary model (token pricing, 2K resolution, Batch)
- Added: Batch image generation example
- Added: Responses API image generation example
- Changed: DALL-E 2/3 marked as REMOVED (2026-05-12)
- Changed: Pricing section updated to token-based for GPT Image 2
- Changed: Rate limits section with GPT Image 2 tiers
