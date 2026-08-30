# INFO: Files API

**Doc ID**: GROKAPI-IN28
**Goal**: File upload, management, supported formats, size limits
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Files API (`/v1/files`) enables uploading, listing, retrieving, and deleting files for use with various Grok features including collections (RAG), chat with files, and batch API. Files are uploaded as multipart form data. The API supports various document formats including PDF, text, CSV, JSON, and common office formats. Files are stored on xAI servers and referenced by file ID. Compatible with OpenAI's Files API endpoint format. [VERIFIED] (GROKAPI-SC-XAI-FILES | https://docs.x.ai/developers/files)

## Key Facts

- [VERIFIED] Endpoint: `POST /v1/files` for upload (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] List: `GET /v1/files` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Get: `GET /v1/files/{file_id}` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Delete: `DELETE /v1/files/{file_id}` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Content: `GET /v1/files/{file_id}/content` (GROKAPI-SC-XAI-RESTREF)

## Quick Reference

- **Upload**: `POST /v1/files` (multipart)
- **List**: `GET /v1/files`
- **Get**: `GET /v1/files/{file_id}`
- **Content**: `GET /v1/files/{file_id}/content`
- **Delete**: `DELETE /v1/files/{file_id}`

## Examples

### Upload File (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

file = client.files.create(
    file=open("report.pdf", "rb"),
    purpose="assistants",
)
print(f"File ID: {file.id}")
```

### Upload File (cURL)

```bash
curl https://api.x.ai/v1/files \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -F purpose="assistants" \
  -F file="@report.pdf"
```

### List Files

```python
files = client.files.list()
for f in files.data:
    print(f"{f.id}: {f.filename} ({f.bytes} bytes)")
```

## Differences from Other APIs

### vs OpenAI
- **Compatible endpoint**: Same `/v1/files` format and SDK methods
- **Same purpose values**: "assistants", "batch", etc.

### vs Anthropic
- **UNIQUE**: Anthropic has no Files API (passes content inline)

## Sources

- GROKAPI-SC-XAI-FILES | https://docs.x.ai/developers/files | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:30]**
- Initial document created with Files API reference
