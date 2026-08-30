# Uploads API

**Doc ID**: OAIAPI-IN34
**Goal**: Document multipart upload API for large files with chunking and resumability
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Uploads API enables multipart upload for large files. Create upload (POST /v1/uploads), add parts (POST /v1/uploads/{upload_id}/parts), complete (POST /v1/uploads/{upload_id}/complete). Resumable - resume by adding remaining parts. Min part 5MB, max total 512MB. 1 hour expiration. Parts uploadable in any order but must be ordered on complete. On completion returns file ID for Files API. [VERIFIED] (OAIAPI-SC-OAI-UPLCRT, OAIAPI-SC-OAI-GUPLOAD)

## Key Facts

- **Min part size**: 5MB (except last) [VERIFIED]
- **Max total size**: 512MB [VERIFIED]
- **Resumable**: Can resume interrupted uploads [VERIFIED]
- **Expiration**: 1 hour if not completed [VERIFIED]
- **Parallel**: Parts uploadable concurrently [VERIFIED]

## Upload Workflow

1. **Create**: POST /v1/uploads `{purpose, filename, bytes, mime_type}`
2. **Add parts**: POST /v1/uploads/{id}/parts (binary data, min 5MB each)
3. **Complete**: POST /v1/uploads/{id}/complete `{part_ids: [...]}`
4. **Cancel** (optional): POST /v1/uploads/{id}/cancel

Status values: pending, completed, cancelled, expired

## SDK Examples (Python)

### Basic Multipart Upload

```python
from openai import OpenAI
import os

client = OpenAI()

file_path = "large_training_data.jsonl"
file_size = os.path.getsize(file_path)
part_size = 10 * 1024 * 1024  # 10MB

upload = client.uploads.create(
    purpose="fine-tune", filename=os.path.basename(file_path),
    bytes=file_size, mime_type="application/jsonl"
)

part_ids = []
with open(file_path, "rb") as f:
    while chunk := f.read(part_size):
        part = client.uploads.parts.create(upload_id=upload.id, data=chunk)
        part_ids.append(part.id)
        print(f"Uploaded part {len(part_ids)}")

completed = client.uploads.complete(upload_id=upload.id, part_ids=part_ids)
print(f"File ID: {completed.file.id}")
```

### Resumable Upload

```python
from openai import OpenAI
import os, pickle

client = OpenAI()

def save_progress(upload_id, part_ids, offset):
    with open("upload_progress.pkl", "wb") as f:
        pickle.dump({"upload_id": upload_id, "part_ids": part_ids, "offset": offset}, f)

def load_progress():
    try:
        with open("upload_progress.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

file_path = "large_file.jsonl"
file_size = os.path.getsize(file_path)
part_size = 10 * 1024 * 1024

progress = load_progress()
if progress:
    upload_id, part_ids, offset = progress["upload_id"], progress["part_ids"], progress["offset"]
else:
    upload = client.uploads.create(
        purpose="fine-tune", filename=os.path.basename(file_path),
        bytes=file_size, mime_type="application/jsonl"
    )
    upload_id, part_ids, offset = upload.id, [], 0

with open(file_path, "rb") as f:
    f.seek(offset)
    while chunk := f.read(part_size):
        try:
            part = client.uploads.parts.create(upload_id=upload_id, data=chunk)
            part_ids.append(part.id)
            offset += len(chunk)
            save_progress(upload_id, part_ids, offset)
        except Exception as e:
            print(f"Interrupted: {e}. Run again to resume.")
            raise

completed = client.uploads.complete(upload_id=upload_id, part_ids=part_ids)
os.remove("upload_progress.pkl")
print(f"Complete: {completed.file.id}")
```

### Parallel Part Upload

```python
from openai import OpenAI
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

client = OpenAI()

file_path = "large_file.jsonl"
file_size = os.path.getsize(file_path)
part_size = 10 * 1024 * 1024

upload = client.uploads.create(
    purpose="fine-tune", filename=os.path.basename(file_path),
    bytes=file_size, mime_type="application/jsonl"
)

chunks = []
with open(file_path, "rb") as f:
    while chunk := f.read(part_size):
        chunks.append(chunk)

part_results = {}
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {
        executor.submit(lambda c: client.uploads.parts.create(upload_id=upload.id, data=c), chunk): i
        for i, chunk in enumerate(chunks)
    }
    for future in as_completed(futures):
        i = futures[future]
        part_results[i] = future.result().id

part_ids = [part_results[i] for i in sorted(part_results)]
completed = client.uploads.complete(upload_id=upload.id, part_ids=part_ids)
print(f"Complete: {completed.file.id}")
```

## Error Responses

- **400 Bad Request** - Invalid upload parameters or part data
- **404 Not Found** - Upload not found
- **410 Gone** - Upload expired
- **413 Payload Too Large** - Total size exceeds limit

## Differences from Other APIs

- **vs Files API**: Uploads for large files, Files for small
- **vs S3 multipart**: Similar concept, OpenAI-specific

## Limitations and Known Issues

- **1 hour expiration**: Must complete within 1 hour [VERIFIED]
- **Part size minimum**: 5MB minimum (except last) [VERIFIED]
- **No partial download**: Cannot download incomplete uploads [ASSUMED]

## Gotchas and Quirks

- **Order matters on complete**: Must provide parts in correct order [VERIFIED]
- **Cannot modify parts**: Once uploaded, immutable [VERIFIED]
- **Expiration non-extendable**: Cannot extend 1-hour limit [ASSUMED]

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

- OAIAPI-SC-OAI-UPLCRT - POST Create upload
- OAIAPI-SC-OAI-UPLPRT - POST Add upload part
- OAIAPI-SC-OAI-UPLCMP - POST Complete upload
- OAIAPI-SC-OAI-UPLCAN - POST Cancel upload
- OAIAPI-SC-OAI-GUPLOAD - Uploads guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 15:50]**
- Enriched: Full workflow, SDK examples (basic, resumable, parallel) from 2026-03-20
- Changed: Doc ID from IN29 to IN34 per renumbering

**[2026-05-22 11:45]**
- Stub created
