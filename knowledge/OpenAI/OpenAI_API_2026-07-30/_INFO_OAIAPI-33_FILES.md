# Files API

**Doc ID**: OAIAPI-IN33
**Goal**: Document Files API for upload, retrieval, deletion, and purpose management
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Files API manages file uploads for fine-tuning, batch processing, and vector stores. Upload (POST /v1/files), retrieve metadata (GET /v1/files/{file_id}), download content (GET /v1/files/{file_id}/content), delete (DELETE /v1/files/{file_id}), list (GET /v1/files). Max size: 512MB (assistants), 100MB (fine-tune). Purpose types: fine-tune, batch, assistants, vision. Files persist until deleted. Organization-scoped. [VERIFIED] (OAIAPI-SC-OAI-FILCRT, OAIAPI-SC-OAI-GFILES)

## Key Facts

- **Max size**: 512MB (assistants), 100MB (fine-tune) [VERIFIED]
- **Purposes**: fine-tune, batch, assistants, vision [VERIFIED]
- **Persistence**: Files persist until manually deleted [VERIFIED]
- **Scope**: Organization-level [VERIFIED]
- **Purpose immutable**: Cannot change after upload [VERIFIED]

## File Purposes

- **fine-tune**: JSONL, 100MB, training/validation data
- **batch**: JSONL, 100MB, batch API requests
- **assistants**: Various (PDF, DOCX, TXT, XLSX, CSV, code), 512MB
- **vision**: Images (JPG, PNG, WEBP, GIF), 20MB

## File Object

```json
{
  "id": "file_abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1234567890,
  "filename": "training_data.jsonl",
  "purpose": "fine-tune",
  "status": "processed",
  "status_details": null
}
```

Status values: "uploaded", "processed", "error"

## SDK Examples (Python)

### Upload File

```python
from openai import OpenAI

client = OpenAI()

with open("training_data.jsonl", "rb") as f:
    file = client.files.create(file=f, purpose="fine-tune")

print(f"File ID: {file.id}, Size: {file.bytes} bytes")
```

### List and Filter Files

```python
from openai import OpenAI

client = OpenAI()

files = client.files.list(purpose="fine-tune")
for file in files.data:
    print(f"{file.id}: {file.filename} ({file.bytes} bytes)")
```

### Download Content

```python
from openai import OpenAI

client = OpenAI()

content = client.files.content("file_abc123")
with open("downloaded.jsonl", "wb") as f:
    f.write(content.content)
```

### Check Upload Status

```python
from openai import OpenAI
import time

client = OpenAI()

with open("large_file.pdf", "rb") as f:
    file = client.files.create(file=f, purpose="assistants")

while file.status == "uploaded":
    time.sleep(1)
    file = client.files.retrieve(file.id)

if file.status == "processed":
    print("File ready")
elif file.status == "error":
    print(f"Error: {file.status_details}")
```

### Production File Manager

```python
from openai import OpenAI
from typing import List
import time

class FileManager:
    def __init__(self):
        self.client = OpenAI()
    
    def upload(self, file_path: str, purpose: str, wait: bool = True):
        with open(file_path, "rb") as f:
            file = self.client.files.create(file=f, purpose=purpose)
        if wait:
            file = self._wait_processed(file.id)
        return {"id": file.id, "filename": file.filename, "status": file.status}
    
    def _wait_processed(self, file_id: str, timeout: int = 60):
        start = time.time()
        while True:
            file = self.client.files.retrieve(file_id)
            if file.status in ["processed", "error"]:
                return file
            if time.time() - start > timeout:
                raise TimeoutError(f"Processing timeout: {file_id}")
            time.sleep(1)
    
    def get_storage(self):
        files = self.client.files.list()
        storage = {}
        for f in files.data:
            storage.setdefault(f.purpose, {"count": 0, "bytes": 0})
            storage[f.purpose]["count"] += 1
            storage[f.purpose]["bytes"] += f.bytes
        return storage
    
    def cleanup_old(self, days: int = 30) -> int:
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        files = self.client.files.list()
        deleted = 0
        for f in files.data:
            if f.created_at < cutoff:
                self.client.files.delete(f.id)
                deleted += 1
        return deleted

manager = FileManager()
result = manager.upload("training_data.jsonl", purpose="fine-tune")
print(f"Uploaded: {result['id']}")
```

## Error Responses

- **400 Bad Request** - Invalid file format or purpose
- **413 Payload Too Large** - File exceeds size limit
- **404 Not Found** - File not found
- **429 Too Many Requests** - Rate limit exceeded

## Differences from Other APIs

- **vs Cloud storage**: API-integrated, not general-purpose
- **vs S3**: OpenAI-specific purposes, not generic object storage

## Limitations and Known Issues

- **No versioning**: Must delete and re-upload [VERIFIED]
- **No folders**: Flat file structure [VERIFIED]
- **Purpose immutable**: Cannot change after upload [VERIFIED]

## Gotchas and Quirks

- **Files don't auto-delete**: Must manually clean up [VERIFIED]
- **Wrong purpose**: Prevents usage in target API [VERIFIED]
- **Processing delay**: Files may take time to process [ASSUMED]

## TypeScript Examples

### File Operations

```typescript
import OpenAI from "openai";
import { createReadStream } from "fs";

const client = new OpenAI();

// List files
for await (const file of await client.files.list()) {
  console.log(`${file.id}: ${file.filename}`);
}

// Upload file
const uploaded = await client.files.create({
  file: createReadStream("data.jsonl"),
  purpose: "fine-tune",
});
console.log(`Uploaded: ${uploaded.id}`);
```

## Sources

- OAIAPI-SC-OAI-FILCRT - POST Upload file
- OAIAPI-SC-OAI-FILGET - GET Retrieve file
- OAIAPI-SC-OAI-FILCNT - GET Download content
- OAIAPI-SC-OAI-FILDEL - DELETE Delete file
- OAIAPI-SC-OAI-GFILES - Files guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 15:45]**
- Enriched: Full purposes, file object, SDK examples from 2026-03-20
- Changed: Doc ID from IN28 to IN33 per renumbering

**[2026-05-22 11:45]**
- Stub created
