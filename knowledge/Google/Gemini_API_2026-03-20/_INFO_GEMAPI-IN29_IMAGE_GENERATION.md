# INFO: Gemini API Image Generation

**Doc ID**: GEMAPI-IN29
**Goal**: Document Nano Banana (native image gen), Imagen 4, image editing, and generation parameters
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini API offers multiple image generation approaches. **Nano Banana** models (`gemini-2.5-flash-image`, `gemini-3.1-flash-image-preview`, `gemini-3-pro-image-preview`) provide native image generation integrated into the `generateContent` endpoint - the model generates images as part of its response alongside text. **Imagen 4** is a dedicated standalone image generation model accessed via a separate endpoint. Nano Banana supports text-to-image, image editing (inpainting, outpainting), and style transfer within a conversational context. Output images are returned as inline base64 data in response parts with `inlineData` type. The `responseModalities` config parameter controls whether text, image, or both are returned. Nano Banana 2 (`gemini-3.1-flash-image-preview`) optimizes for speed and high-volume use; Nano Banana Pro (`gemini-3-pro-image-preview`) optimizes for quality. Native image generation within the conversational model is unique to Gemini - OpenAI separates DALL-E from GPT, and Anthropic has no image generation.

## Key Facts

- [VERIFIED] Nano Banana: native image gen in generateContent (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] Models: gemini-2.5-flash-image, gemini-3.1-flash-image-preview, gemini-3-pro-image-preview (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Imagen 4: dedicated standalone image generation (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] responseModalities: ["TEXT", "IMAGE"] controls output types (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] Output as inlineData in response parts (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] Supports: text-to-image, editing, inpainting, style transfer (GEMAPI-SC-GOOG-IMGGEN)

## Quick Reference

**Native Generation Model**: `gemini-2.5-flash-image` (or Nano Banana 2/Pro previews)
**Standalone Model**: Imagen 4
**Config**: `responseModalities: ["IMAGE"]` or `["TEXT", "IMAGE"]`
**Output**: `parts[].inlineData` with base64 image

## Python Examples

### Example 1: Text-to-Image with Nano Banana

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
    ),
    contents="Generate a watercolor painting of a sunset over a mountain lake"
)

# Save generated image
for part in response.candidates[0].content.parts:
    if part.inline_data:
        image_bytes = base64.b64decode(part.inline_data.data)
        with open("generated_sunset.png", "wb") as f:
            f.write(image_bytes)
        print(f"Image saved ({len(image_bytes)} bytes)")
```

### Example 2: Image Editing (Provide Input + Instructions)

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open("photo.jpg", "rb") as f:
    input_image = base64.b64encode(f.read()).decode("utf-8")

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
    ),
    contents=[
        types.Content(role="user", parts=[
            types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=input_image)),
            types.Part(text="Remove the background and replace it with a tropical beach"),
        ])
    ]
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("edited_photo.png", "wb") as f:
            f.write(base64.b64decode(part.inline_data.data))
```

### Example 3: Text and Image Combined Response

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
    ),
    contents="Create an infographic about the water cycle with a brief explanation"
)

for part in response.candidates[0].content.parts:
    if part.text:
        print(f"Text: {part.text}")
    elif part.inline_data:
        with open("infographic.png", "wb") as f:
            f.write(base64.b64decode(part.inline_data.data))
        print("Image saved")
```

### Example 4: Imagen 4 Standalone

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_images(
    model="imagen-4.0-generate-preview",
    prompt="A photorealistic image of a futuristic city at night",
    config=types.GenerateImagesConfig(
        number_of_images=1,
    )
)

for i, image in enumerate(response.generated_images):
    with open(f"imagen_output_{i}.png", "wb") as f:
        f.write(image.image.image_bytes)
    print(f"Imagen image saved")
```

## Comparison with Other APIs

### vs OpenAI

- **Architecture**: Gemini: native image gen in conversation model | OpenAI: separate DALL-E model
- **Endpoint**: Gemini: generateContent (same endpoint) | OpenAI: /v1/images/generations (separate)
- **Conversation**: Gemini: images within chat context | OpenAI: standalone generation
- **Editing**: Gemini: conversational editing instructions | OpenAI: DALL-E edit endpoint with masks
- **Text+Image output**: Gemini: both in one response | OpenAI: separate API calls
- **UNIQUE to Gemini**: Native image generation within the conversational model

### vs Anthropic

- **Image generation**: Gemini: yes (Nano Banana + Imagen) | Anthropic: **no image generation**
- **UNIQUE advantage**: Anthropic has no image generation capability at all

## Error Responses

- **400**: Invalid image generation parameters, unsupported responseModalities combination
- Safety filters may block generated images (finishReason: SAFETY)

## Rate Limiting / Throttling

Image generation models have IPM (Images Per Minute) rate limits in addition to RPM/TPM. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Image output may be blocked by safety filters (GEMAPI-SC-GOOG-SAFETY)
- [VERIFIED] All generated images include SynthID watermark - invisible but detectable (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] Supported languages: EN, ar-EG, de-DE, es-MX, fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA, vi-VN, zh-CN (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] Image gen does NOT support audio or video inputs (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] Model may not follow exact number of requested output images (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] Input image limits: gemini-2.5-flash-image: up to 3; gemini-3-pro-image: 5 high-fidelity + 14 total; gemini-3.1-flash-image: 4 characters + 10 objects (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] Gemini 3.1 Flash Image: Grounding with Google Search does not support real-world images of people from web search (GEMAPI-SC-GOOG-IMGGEN)

## Gotchas and Quirks

- Must set `responseModalities` to include "IMAGE" - without it, model returns text only
- Nano Banana is a brand name for Gemini's native image capability, not a separate model family
- SynthID watermarking is invisible but detectable - cannot be removed
- Image editing uses conversational instructions, not mask-based editing like DALL-E
- Imagen 4 uses a different SDK method (`generate_images`) vs Nano Banana (`generate_content`)
- Gemini 3 image models support 1K, 2K, and 4K resolution output; Gemini 3.1 Flash Image adds 512 (0.5K)
- Gemini 3.1 Flash Image adds new aspect ratios: 1:4, 4:1, 1:8, 8:1
- Gemini 3 image models have a "thinking mode" - generates interim "thought images" (not charged) before final output
- Grounding with Google Search available for image generation (verify facts before generating)
- Advanced text rendering in images is a Gemini 3 feature (infographics, menus, diagrams)
- Up to 14 reference images supported in Gemini 3 for multi-reference composition
- For best text in images: generate the text first, then ask for an image containing that text

## Sources

- GEMAPI-SC-GOOG-IMGGEN: https://ai.google.dev/gemini-api/docs/image-generation [VERIFIED]
- GEMAPI-SC-GOOG-MODELS: https://ai.google.dev/gemini-api/docs/models [VERIFIED]

## Document History

**[2026-03-20 06:35]**
- Added: language support list, per-model input image limits, 4K resolution, search grounding
- Added: thinking mode for images, text rendering, aspect ratios, reference image limits
- Added: Google Search grounding people image restriction

**[2026-03-20 05:05]**
- Initial document created with native and standalone image generation
