# INFO: Gemini API Vision (Image Input)

**Doc ID**: GEMAPI-IN12
**Goal**: Document image input methods, supported formats, and image understanding capabilities
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini models natively process images as part of multimodal prompts through two input methods: inline base64 data via `inlineData` parts and File API references via `fileData` parts. Supported image formats include JPEG, PNG, GIF (including animated), WebP, and BMP. Multiple images can be included in a single request. Images are processed as visual tokens counting toward the context window. The File API is recommended for images over 20MB or when reusing images across requests. Gemini can perform image understanding tasks including object recognition, text extraction (OCR), visual question answering, image comparison, diagram interpretation, and spatial reasoning. All Gemini models support vision input natively within the `generateContent` endpoint - no separate vision API exists.

## Key Facts

- [VERIFIED] Two input methods: inlineData (base64) and fileData (File API URI) (GEMAPI-SC-GOOG-FILINP)
- [VERIFIED] Supported formats: JPEG, PNG, GIF, WebP, BMP (GEMAPI-SC-GOOG-FILINP)
- [VERIFIED] Multiple images per request supported (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Images processed as visual tokens in context window (GEMAPI-SC-GOOG-FILPRM)
- [VERIFIED] File API recommended for large files (>20MB) (GEMAPI-SC-GOOG-FILAPI)

## Quick Reference

**Inline**: `{"inlineData": {"mimeType": "image/jpeg", "data": "base64..."}}`
**File API**: `{"fileData": {"mimeType": "image/jpeg", "fileUri": "https://generativelanguage.googleapis.com/v1beta/files/abc123"}}`

## Input Methods

### Inline Data (Base64)

Best for small images (<20MB). Encode image as base64 string:

```json
{
  "parts": [
    {"inlineData": {"mimeType": "image/jpeg", "data": "/9j/4AAQ..."}},
    {"text": "Describe this image"}
  ]
}
```

### File API Reference

Best for large images or reuse across requests. Upload first, then reference:

```json
{
  "parts": [
    {"fileData": {"mimeType": "image/png", "fileUri": "https://generativelanguage.googleapis.com/v1beta/files/abc123"}},
    {"text": "What objects are in this image?"}
  ]
}
```

## Python Examples

### Example 1: Inline Image from File

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open("photo.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[
            types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=image_data)),
            types.Part(text="Describe this image in detail"),
        ])
    ]
)
print(response.text)
```

### Example 2: Multiple Images Comparison

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def load_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[
            types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=load_image("before.jpg"))),
            types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=load_image("after.jpg"))),
            types.Part(text="Compare these two images. What changed?"),
        ])
    ]
)
print(response.text)
```

### Example 3: Image via File API

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Upload image
uploaded = client.files.upload(file="large_photo.png")

# Wait for processing
import time
while uploaded.state == "PROCESSING":
    time.sleep(2)
    uploaded = client.files.get(name=uploaded.name)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[
            types.Part(file_data=types.FileData(mime_type=uploaded.mime_type, file_uri=uploaded.uri)),
            types.Part(text="Extract all text visible in this image"),
        ])
    ]
)
print(response.text)
```

## Comparison with Other APIs

### vs OpenAI

- **Input format**: Gemini: `inlineData`/`fileData` parts | OpenAI: `image_url` in content array
- **URL support**: Gemini: File API URIs only | OpenAI: arbitrary URLs and base64
- **Formats**: Gemini: JPEG, PNG, GIF, WebP, BMP | OpenAI: JPEG, PNG, GIF, WebP
- **Multiple images**: Both support multiple images per request

### vs Anthropic

- **Input format**: Gemini: `inlineData`/`fileData` | Anthropic: `image` blocks with base64 or URL
- **URL support**: Gemini: File API URIs | Anthropic: arbitrary URLs and base64
- **Formats**: Similar support across both APIs

## Error Responses

- **400**: Unsupported MIME type, invalid base64 encoding, file too large for inline
- **404**: Invalid fileUri reference

## Rate Limiting / Throttling

Standard rate limits apply. Large images consume more tokens. See GEMAPI-IN04.

## Limitations and Known Issues

- Inline data has practical size limits (~20MB) - use File API for larger images
- Animated GIF frames may not all be processed depending on model

## Gotchas and Quirks

- No direct URL image input (unlike OpenAI) - must use base64 or File API
- Image token cost depends on resolution - higher resolution = more tokens
- Text after image in parts array is treated as the question about the image

## Sources

- GEMAPI-SC-GOOG-FILINP: https://ai.google.dev/gemini-api/docs/file-input-methods [VERIFIED]
- GEMAPI-SC-GOOG-FILPRM: https://ai.google.dev/gemini-api/docs/file-prompting-strategies [VERIFIED]
- GEMAPI-SC-GOOG-FILAPI: https://ai.google.dev/gemini-api/docs/files [VERIFIED]

## Document History

**[2026-03-20 03:45]**
- Initial document created with image input methods and examples
