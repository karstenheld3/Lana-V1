# INFO: Gemini API Video Understanding

**Doc ID**: GEMAPI-IN14
**Goal**: Document video input processing, File API uploads, frame extraction, and timestamps
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini models natively process video as multimodal input, a capability unique among major LLM APIs. Videos are uploaded via the File API and referenced using `fileData` parts. Supported formats include MP4, MPEG, MOV, AVI, FLV, MKV, and WebM. The API extracts frames at approximately 1 FPS and processes both visual frames and audio tracks. Videos up to approximately 1 hour at default resolution fit within the context window. Timestamp-based queries allow asking about specific moments in the video. Video is always uploaded via the File API (not inline base64) due to file size. Processing may take time - poll `files.get()` until state is "ACTIVE". Neither OpenAI nor Anthropic offer native video understanding through their REST APIs.

## Key Facts

- [VERIFIED] Video input via File API only (not inline base64) (GEMAPI-SC-GOOG-VIDUND)
- [VERIFIED] Supported: MP4, MPEG, MOV, AVI, FLV, MKV, WebM (GEMAPI-SC-GOOG-VIDUND)
- [VERIFIED] Frame extraction at ~1 FPS (GEMAPI-SC-GOOG-VIDUND)
- [VERIFIED] Audio track processed alongside visual frames (GEMAPI-SC-GOOG-VIDUND)
- [VERIFIED] Timestamp-based queries supported (GEMAPI-SC-GOOG-VIDUND)
- [VERIFIED] Up to ~1 hour at default resolution (GEMAPI-SC-GOOG-VIDUND)

## Quick Reference

**Input**: `{"fileData": {"mimeType": "video/mp4", "fileUri": "..."}}`
**Upload**: Via File API (POST /upload/v1beta/files)
**Formats**: MP4, MPEG, MOV, AVI, FLV, MKV, WebM
**Max duration**: ~1 hour at default resolution

## Python Examples

### Example 1: Video Understanding

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Upload video
uploaded = client.files.upload(file="presentation.mp4")

# Wait for processing (videos take longer)
while uploaded.state == "PROCESSING":
    time.sleep(5)
    uploaded = client.files.get(name=uploaded.name)

if uploaded.state == "FAILED":
    raise Exception(f"Video processing failed: {uploaded.error}")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[
            types.Part(file_data=types.FileData(
                mime_type=uploaded.mime_type, file_uri=uploaded.uri
            )),
            types.Part(text="Summarize this video. Include key topics and visual elements."),
        ])
    ]
)
print(response.text)
```

### Example 2: Timestamp-Based Query

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

uploaded = client.files.upload(file="tutorial.mp4")
while uploaded.state == "PROCESSING":
    time.sleep(5)
    uploaded = client.files.get(name=uploaded.name)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[
            types.Part(file_data=types.FileData(
                mime_type=uploaded.mime_type, file_uri=uploaded.uri
            )),
            types.Part(text="What happens at the 2:30 mark? Create a timeline of key moments."),
        ])
    ]
)
print(response.text)

# Clean up
client.files.delete(name=uploaded.name)
```

## Comparison with Other APIs

### vs OpenAI

- **Video input**: Gemini: native video understanding | OpenAI: **no native video input** (images only)
- **UNIQUE to Gemini**: Full video processing with frame extraction and audio

### vs Anthropic

- **Video input**: Gemini: native video understanding | Anthropic: **no video input** (images only)
- **UNIQUE to Gemini**: Video is a major multimodal differentiator

## Error Responses

- **400**: Unsupported video format
- **404**: Invalid File API reference
- File state "FAILED": Video could not be processed (corrupt, unsupported codec)

## Rate Limiting / Throttling

Standard rate limits apply. Video consumes significant tokens (~1 FPS extracted frames + audio). See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] ~1 hour max at default resolution (longer videos may be truncated) (GEMAPI-SC-GOOG-VIDUND)
- Video processing time depends on file size and duration - can take minutes

## Gotchas and Quirks

- Video MUST be uploaded via File API (no inline base64) - different from images
- Processing can take significantly longer than images - always poll state
- Frame extraction at 1 FPS means fast-moving content between frames may be missed
- Video tokens are expensive - use countTokens to estimate cost before processing
- File API files expire after 48 hours - re-upload for long-term use

## Sources

- GEMAPI-SC-GOOG-VIDUND: https://ai.google.dev/gemini-api/docs/video-understanding [VERIFIED]
- GEMAPI-SC-GOOG-FILINP: https://ai.google.dev/gemini-api/docs/file-input-methods [VERIFIED]

## Document History

**[2026-03-20 03:55]**
- Initial document created
