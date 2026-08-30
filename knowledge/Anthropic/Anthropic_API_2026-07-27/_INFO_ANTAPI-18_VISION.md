# Vision (Image Inputs)

**Doc ID**: ANTAPI-IN18
**Goal**: Document image input support, formats, sources, and multimodal usage patterns
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` for Messages API content block types

## Summary

Claude supports image inputs via `image` content blocks in the Messages API. Images can be provided as base64-encoded data or via URL. Supported formats include JPEG, PNG, GIF, and WebP. Images are processed as tokens based on their dimensions. Multiple images can be included in a single message, and images can be mixed with text content blocks for multimodal analysis.

## Key Facts

- **Content Block**: `{"type": "image", "source": {...}}`
- **Source Types**: `base64`, `url`
- **Formats**: JPEG, PNG, GIF, WebP
- **Max Size**: ~20 MB per image (varies by platform)
- **Token Cost**: Based on image dimensions
- **Multiple Images**: Supported in a single message
- **Status**: GA

## Image Sources

### URL Source

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://example.com/photo.jpg",
                    },
                },
                {"type": "text", "text": "Describe this image in detail."},
            ],
        }
    ],
)
print(message.content[0].text)
```

### Base64 Source

```python
import anthropic
import base64
import httpx

client = anthropic.Anthropic()

# From file
with open("photo.jpg", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {"type": "text", "text": "What's in this image?"},
            ],
        }
    ],
)
```

### Multiple Images

```python
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "url", "url": "https://example.com/before.jpg"},
                },
                {
                    "type": "image",
                    "source": {"type": "url", "url": "https://example.com/after.jpg"},
                },
                {"type": "text", "text": "Compare these two images. What changed?"},
            ],
        }
    ],
)
```

## Supported Media Types

- `image/jpeg` - JPEG images
- `image/png` - PNG images
- `image/gif` - GIF images (first frame for animated)
- `image/webp` - WebP images

## Image Limits

- **Max images per request**: 600 (API), 100 (for 200K-context models), 20 (claude.ai)
- **Max single image size**: 8000x8000 px (rejected above this)
- **Max image size when >20 images**: 2000x2000 px
- **Request payload limit**: 32 MB for standard endpoints (lower on some third-party platforms)
- **Optimal dimensions**: Resize long edge to max 1568 px, ~1.15 megapixels to avoid latency from server-side resizing
- **Minimum useful size**: Images under 200 px on any edge may degrade output quality
- For many images, use Files API with `file_id` references to keep payloads small

## Token Calculation

```
tokens = (width_px * height_px) / 750
```

Example costs at $3/million input tokens (Sonnet 4.6):
- 1568x1568 image: ~3,283 tokens (~$0.0098)
- 800x600 image: ~640 tokens (~$0.0019)
- Images exceeding 1568 px on either edge are auto-resized (preserving aspect ratio) before processing, adding latency with no quality benefit

## Vision Limitations

- **No people identification**: Claude cannot and will not name people in images (per Acceptable Use Policy)
- **Accuracy**: May hallucinate or make mistakes on low-quality, rotated, or very small (<200 px) images
- **Spatial reasoning**: Limited; struggles with precise localization, layouts, analog clock faces, exact chess positions
- **Counting**: Approximate only, especially for large numbers of small objects
- **AI-generated images**: Cannot reliably detect fake or synthetic images
- **Inappropriate content**: Refuses to process images violating Acceptable Use Policy
- **Healthcare**: Can analyze general medical images but not designed for diagnostic scans (CT, MRI); not a substitute for professional diagnosis

## Gotchas and Quirks

- Token cost formula: `(width * height) / 750`
- URL images must be publicly accessible
- Base64 encoding increases data size by ~33%
- Third-party platforms (Bedrock, Vertex) may have different size limits
- GIF animations: only the first frame is analyzed
- Images auto-resized server-side if over 1568 px long edge; adds latency, no quality gain
- Requests with many large images can fail before reaching the 600-image count due to 32 MB payload limit

## Related Endpoints

- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` - Messages API (image content blocks)
- `_INFO_ANTAPI-19_PDF_SUPPORT.md [ANTAPI-IN19]` - PDF support (also visual)
- `_INFO_ANTAPI-10_TOKEN_COUNTING.md [ANTAPI-IN10]` - Count image tokens

## Sources

- ANTAPI-SC-ANTH-VISION - https://platform.claude.com/docs/en/build-with-claude/vision - Vision guide
- ANTAPI-SC-ANTH-MSGCRT - https://platform.claude.com/docs/en/api/messages/create - Image block schema

## SDK Verification

All 3 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `types/url_image_source_param.py`: `UrlImageSourceParam(type="url", url=str)`
- `types/base64_image_source_param.py`: `Base64ImageSourceParam(type="base64", media_type=str, data=str)`
- Image content block `{"type": "image", "source": {...}}` accepted in message content arrays

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:55]**
- Added: SDK verification section (anthropic 0.120.0, all 3 examples valid)

**[2026-03-20 05:00]**
- Added: Concrete image limits (8000x8000 max, 600 images/request, 32 MB payload)
- Added: Token calculation formula (width*height/750)
- Added: Vision limitations (no people ID, spatial reasoning, counting, AI detection)
- Added: Optimization guidance (1568 px, 1.15 MP)

**[2026-03-20 03:22]**
- Initial documentation created from vision guide and Messages API reference
