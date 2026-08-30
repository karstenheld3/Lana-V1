# INFO: Gemini API File API

**Doc ID**: GEMAPI-IN23
**Goal**: Document file upload, management, lifecycle, and usage with generateContent
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini File API enables uploading and managing files for use as multimodal input in `generateContent` requests. Files are uploaded via `POST /upload/v1beta/files` with resumable upload support for large files. Uploaded files are referenced in prompts using `fileData` parts with the file's URI. Files have a 48-hour TTL and are automatically deleted unless explicitly managed. The API supports listing, getting metadata, and deleting files. Supported file types include images (JPEG, PNG, GIF, WebP, BMP), audio (MP3, WAV, AAC, OGG, FLAC), video (MP4, MOV, AVI, MKV, WebM), and documents (PDF, plain text). Maximum upload size is 2GB per file. Files transition through states: PROCESSING -> ACTIVE (ready for use) or FAILED. The File API is the recommended method for large media files and video (which cannot be sent inline).

## Key Facts

- [VERIFIED] Upload endpoint: `POST /upload/v1beta/files` (GEMAPI-SC-GOOG-FILAPI)
- [VERIFIED] Resumable uploads for large files (GEMAPI-SC-GOOG-FILAPI)
- [VERIFIED] 48-hour TTL, auto-deleted (GEMAPI-SC-GOOG-FILAPI)
- [VERIFIED] Max 2GB per file (GEMAPI-SC-GOOG-FILAPI)
- [VERIFIED] States: PROCESSING -> ACTIVE or FAILED (GEMAPI-SC-GOOG-FILAPI)
- [VERIFIED] Reference via fileData part with fileUri (GEMAPI-SC-GOOG-FILAPI)

## Quick Reference

**Upload**: `POST /upload/v1beta/files`
**List**: `GET /v1beta/files`
**Get**: `GET /v1beta/files/{name}`
**Delete**: `DELETE /v1beta/files/{name}`
**TTL**: 48 hours
**Max size**: 2GB

## REST API

### Upload File

```
POST https://generativelanguage.googleapis.com/upload/v1beta/files
```

**Headers:**
- `x-goog-api-key`: API key
- `Content-Type`: multipart/related or the file's MIME type
- `X-Goog-Upload-Protocol`: resumable (for large files)

### List Files

```
GET https://generativelanguage.googleapis.com/v1beta/files
```

### Get File Metadata

```
GET https://generativelanguage.googleapis.com/v1beta/files/{name}
```

**Response:**
```json
{
  "name": "files/abc123",
  "displayName": "photo.jpg",
  "mimeType": "image/jpeg",
  "sizeBytes": "1234567",
  "createTime": "2026-03-20T04:00:00Z",
  "updateTime": "2026-03-20T04:00:00Z",
  "expirationTime": "2026-03-22T04:00:00Z",
  "sha256Hash": "...",
  "uri": "https://generativelanguage.googleapis.com/v1beta/files/abc123",
  "state": "ACTIVE"
}
```

### Delete File

```
DELETE https://generativelanguage.googleapis.com/v1beta/files/{name}
```

### Use in generateContent

```json
{
  "contents": [{
    "parts": [
      {"fileData": {"mimeType": "image/jpeg", "fileUri": "https://generativelanguage.googleapis.com/v1beta/files/abc123"}},
      {"text": "Describe this image"}
    ]
  }]
}
```

## Python Examples

### Example 1: Upload and Use File

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Upload file
uploaded = client.files.upload(file="document.pdf")
print(f"Uploaded: {uploaded.name}, State: {uploaded.state}")

# Wait for processing
while uploaded.state == "PROCESSING":
    time.sleep(2)
    uploaded = client.files.get(name=uploaded.name)

if uploaded.state == "FAILED":
    raise Exception(f"File processing failed")

# Use in prompt
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[
            types.Part(file_data=types.FileData(
                mime_type=uploaded.mime_type,
                file_uri=uploaded.uri
            )),
            types.Part(text="Summarize this document"),
        ])
    ]
)
print(response.text)
```

### Example 2: List and Clean Up Files

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# List all files
for file in client.files.list():
    print(f"{file.name}: {file.display_name} ({file.state}) - expires {file.expiration_time}")

# Delete specific file
client.files.delete(name="files/abc123")
```

### Example 3: Upload with Display Name

```python
from google import genai
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

uploaded = client.files.upload(
    file="recording.mp3",
    config={"display_name": "Meeting Recording March 2026"}
)

while uploaded.state == "PROCESSING":
    time.sleep(2)
    uploaded = client.files.get(name=uploaded.name)

print(f"Ready: {uploaded.uri}")
```

## cURL Examples

### Example 1: Upload File

```bash
curl "https://generativelanguage.googleapis.com/upload/v1beta/files" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -F "file=@photo.jpg"
```

### Example 2: List Files

```bash
curl "https://generativelanguage.googleapis.com/v1beta/files" \
  -H "x-goog-api-key: $GEMINI_API_KEY"
```

## Comparison with Other APIs

### vs OpenAI

- **File API**: Gemini: `/upload/v1beta/files` | OpenAI: `/v1/files` (for Assistants/Fine-tuning)
- **TTL**: Gemini: 48 hours auto-delete | OpenAI: persistent until deleted
- **Max size**: Gemini: 2GB | OpenAI: 512MB
- **Usage**: Gemini: direct in generateContent via fileData | OpenAI: via Assistants API
- **Processing state**: Gemini: PROCESSING/ACTIVE/FAILED | OpenAI: processed/error

### vs Anthropic

- **File API**: Gemini: dedicated File API | Anthropic: inline base64 or URL (no persistent file storage)
- **Persistence**: Gemini: 48-hour storage | Anthropic: no server-side file storage
- **ADVANTAGE**: Gemini's File API enables reuse across requests without re-uploading

## Error Responses

- **400**: Unsupported file type, file too large
- **404**: File not found (expired or deleted)
- State "FAILED": File could not be processed

## Rate Limiting / Throttling

File upload has separate rate limits. Storage limit: 20GB total. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] 48-hour TTL - files auto-delete (GEMAPI-SC-GOOG-FILAPI)
- [VERIFIED] 2GB max per file (GEMAPI-SC-GOOG-FILAPI)
- [VERIFIED] 20GB total storage limit (GEMAPI-SC-GOOG-RTLMTS)

## Gotchas and Quirks

- Files expire after 48 hours - must re-upload for long-term use
- Must poll `files.get()` until state is ACTIVE before using in prompts
- Video files can take minutes to process (longer than images/audio)
- `fileUri` is a full HTTPS URL, not just the file name
- Cannot update a file - must delete and re-upload
- Storage is per-project (shared across all API keys in project)

## Sources

- GEMAPI-SC-GOOG-FILAPI: https://ai.google.dev/gemini-api/docs/files [VERIFIED]
- GEMAPI-SC-GOOG-FILINP: https://ai.google.dev/gemini-api/docs/file-input-methods [VERIFIED]

## Document History

**[2026-03-20 04:35]**
- Initial document created with full File API documentation
