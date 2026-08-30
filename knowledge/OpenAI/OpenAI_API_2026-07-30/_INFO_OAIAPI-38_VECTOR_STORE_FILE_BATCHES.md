# Vector Store File Batches

**Doc ID**: OAIAPI-IN38
**Goal**: Document bulk file operations for vector stores - create batches, track progress, cancel
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Vector Store File Batches API enables bulk file addition to a vector store. Create batch (POST) with up to 2000 files. Two input modes: file_ids (shared config) or files (per-file attributes/chunking). Async processing with status tracking. Cancel in-progress batches. Completed files remain indexed on cancel. [VERIFIED] (OAIAPI-SC-OAI-VSFBT)

## Key Facts

- **Max batch size**: 2000 files per batch [VERIFIED]
- **Two modes**: file_ids (shared config) or files (per-file config), mutually exclusive [VERIFIED]
- **Async**: Batch processes in background, poll for status [VERIFIED]
- **Per-file overrides**: files mode allows different chunking/attributes per file [VERIFIED]
- **Cancellable**: In-progress batches can be cancelled [VERIFIED]

## File Batch Object

```json
{
  "id": "vsfb_abc123",
  "object": "vector_store.file_batch",
  "vector_store_id": "vs_abc123",
  "status": "in_progress",
  "file_counts": {"in_progress": 3, "completed": 7, "failed": 0, "cancelled": 0, "total": 10}
}
```

Status: in_progress, completed, cancelled, failed

## Input Modes

### Mode 1: file_ids (shared config)

```json
{
  "file_ids": ["file-abc", "file-def"],
  "attributes": {"department": "engineering"},
  "chunking_strategy": {"type": "static", "static": {"max_chunk_size_tokens": 1000, "chunk_overlap_tokens": 200}}
}
```

### Mode 2: files (per-file config)

```json
{
  "files": [
    {"file_id": "file-abc", "attributes": {"category": "finance"}},
    {"file_id": "file-def", "chunking_strategy": {"type": "static", "static": {"max_chunk_size_tokens": 2000, "chunk_overlap_tokens": 500}}}
  ]
}
```

## SDK Examples (Python)

### Simple Batch

```python
from openai import OpenAI

client = OpenAI()

file_ids = []
for path in ["report_q1.pdf", "report_q2.pdf", "report_q3.pdf"]:
    with open(path, "rb") as f:
        file = client.files.create(file=f, purpose="assistants")
        file_ids.append(file.id)

batch = client.vector_stores.file_batches.create(
    vector_store_id="vs_abc123",
    file_ids=file_ids,
    attributes={"type": "quarterly_report"}
)
print(f"Batch: {batch.id}, Files: {batch.file_counts.total}")
```

### Per-File Config Batch

```python
from openai import OpenAI

client = OpenAI()

batch = client.vector_stores.file_batches.create(
    vector_store_id="vs_abc123",
    files=[
        {"file_id": "file-fin001", "attributes": {"category": "finance"}},
        {"file_id": "file-leg002", "attributes": {"category": "legal"},
         "chunking_strategy": {"type": "static", "static": {"max_chunk_size_tokens": 2000, "chunk_overlap_tokens": 500}}}
    ]
)
```

### Monitor Batch Progress

```python
from openai import OpenAI
import time

client = OpenAI()

def wait_for_batch(vs_id: str, batch_id: str, timeout: int = 600):
    start = time.time()
    while True:
        batch = client.vector_stores.file_batches.retrieve(
            vector_store_id=vs_id, batch_id=batch_id
        )
        counts = batch.file_counts
        elapsed = time.time() - start
        print(f"[{elapsed:.0f}s] {counts.completed}/{counts.total} completed, {counts.failed} failed")
        
        if batch.status in ("completed", "failed", "cancelled"):
            return batch
        if elapsed > timeout:
            client.vector_stores.file_batches.cancel(vector_store_id=vs_id, batch_id=batch_id)
            raise TimeoutError(f"Batch timed out after {timeout}s")
        time.sleep(5)

batch = wait_for_batch("vs_abc123", "vsfb_xyz789")

if batch.file_counts.failed > 0:
    failed = client.vector_stores.file_batches.list_files(
        vector_store_id="vs_abc123", batch_id="vsfb_xyz789", filter="failed"
    )
    for f in failed.data:
        print(f"FAILED: {f.id} - {f.last_error.message}")
```

### Cancel Batch

```python
from openai import OpenAI

client = OpenAI()

batch = client.vector_stores.file_batches.cancel(
    vector_store_id="vs_abc123", batch_id="vsfb_xyz789"
)
print(f"Cancelled. Completed: {batch.file_counts.completed}, Cancelled: {batch.file_counts.cancelled}")
```

## Error Responses

- **400 Bad Request** - Both file_ids and files provided, exceeds 2000 files
- **404 Not Found** - Vector store or batch not found
- **429 Too Many Requests** - Rate limit exceeded

## Limitations and Known Issues

- **Max 2000 files**: Split larger sets into multiple batches [VERIFIED]
- **No partial retry**: Must re-add failed files individually [ASSUMED]
- **Mutual exclusivity**: Cannot mix file_ids and files modes [VERIFIED]

## Gotchas and Quirks

- **Cancel preserves completed**: Already-processed files remain indexed [VERIFIED]
- **Per-file mode ignores globals**: Top-level attributes/chunking ignored in files mode [VERIFIED]
- **Beta header**: Requires OpenAI-Beta: assistants=v2 for REST [VERIFIED]

## TypeScript Examples

### Vector Store Operations

```typescript
import OpenAI from "openai";

const client = new OpenAI();

// Create vector store
const store = await client.vectorStores.create({ name: "my-store" });
console.log(`Created: ${store.id}`);

// List stores
for await (const vs of await client.vectorStores.list()) {
  console.log(`${vs.id}: ${vs.name}`);
}
```

## Sources

- OAIAPI-SC-OAI-VSFBT - Vector Store File Batches API

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 16:05]**
- Enriched: Full modes, batch object, SDK examples from 2026-03-20

**[2026-05-22 11:45]**
- Stub created
