# Vector Store Files

**Doc ID**: OAIAPI-IN37
**Goal**: Document vector store file management - create, retrieve, update, delete, list
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Vector Store Files API manages individual files within a vector store. Add files (POST), retrieve details (GET), update metadata (POST), delete indexed data (DELETE), list with pagination (GET). Each file is chunked, embedded, and indexed asynchronously. Chunking: auto (800/400 defaults) or static (100-4096 tokens). Metadata up to 16 key-value pairs. Custom attributes for search filtering. Status: in_progress, completed, failed, cancelled. [VERIFIED] (OAIAPI-SC-OAI-VSFIL)

## Key Facts

- **Async processing**: Files indexed in background, poll until completed [VERIFIED]
- **Chunking**: auto (800/400) or static (100-4096 tokens) [VERIFIED]
- **Metadata**: Up to 16 key-value pairs per file [VERIFIED]
- **Attributes**: Custom key-value pairs for search filtering [VERIFIED]
- **Pagination**: Cursor-based, limit 1-100 [VERIFIED]
- **Error types**: server_error, unsupported_file, invalid_file [VERIFIED]

## Vector Store File Object

```json
{
  "id": "file-abc123",
  "object": "vector_store.file",
  "vector_store_id": "vs_abc123",
  "status": "completed",
  "usage_bytes": 12345,
  "last_error": null,
  "attributes": {"category": "support"},
  "chunking_strategy": {
    "type": "static",
    "static": {"max_chunk_size_tokens": 800, "chunk_overlap_tokens": 400}
  }
}
```

Status: in_progress, completed, failed, cancelled

## SDK Examples (Python)

### Add File with Attributes

```python
from openai import OpenAI

client = OpenAI()

with open("product_manual.pdf", "rb") as f:
    file = client.files.create(file=f, purpose="assistants")

vs_file = client.vector_stores.files.create(
    vector_store_id="vs_abc123",
    file_id=file.id,
    attributes={"category": "product", "version": "2.0"}
)
print(f"File: {vs_file.id}, Status: {vs_file.status}")
```

### Poll Until Ready

```python
from openai import OpenAI
import time

client = OpenAI()

while True:
    vs_file = client.vector_stores.files.retrieve(
        vector_store_id="vs_abc123", file_id="file-xyz789"
    )
    if vs_file.status == "completed":
        print(f"Ready. Usage: {vs_file.usage_bytes} bytes")
        break
    elif vs_file.status == "failed":
        print(f"Error: {vs_file.last_error.code} - {vs_file.last_error.message}")
        break
    time.sleep(2)
```

### List and Filter Files

```python
from openai import OpenAI

client = OpenAI()

def list_all_vs_files(vs_id: str, status_filter: str = None):
    all_files, after = [], None
    while True:
        params = {"vector_store_id": vs_id, "limit": 100, "order": "desc"}
        if after:
            params["after"] = after
        if status_filter:
            params["filter"] = status_filter
        response = client.vector_stores.files.list(**params)
        all_files.extend(response.data)
        if not response.has_more:
            break
        after = response.last_id
    return all_files

completed = list_all_vs_files("vs_abc123", "completed")
print(f"Completed: {len(completed)}")

failed = list_all_vs_files("vs_abc123", "failed")
for f in failed:
    print(f"Failed: {f.id} - {f.last_error.message}")
```

### Delete File from Vector Store

```python
from openai import OpenAI

client = OpenAI()

result = client.vector_stores.files.delete(
    vector_store_id="vs_abc123", file_id="file-xyz789"
)
print(f"Deleted: {result.deleted}")
```

## Error Responses

- **400 Bad Request** - Invalid file_id or chunking parameters
- **404 Not Found** - Vector store or file not found
- **409 Conflict** - File already exists in vector store
- **429 Too Many Requests** - Rate limit exceeded

## Limitations and Known Issues

- **Processing time**: Large files can take minutes to index [VERIFIED]
- **No custom embeddings**: Must use OpenAI's embedding model [VERIFIED]
- **Chunk size cap**: max_chunk_size_tokens capped at 4096 [VERIFIED]

## Gotchas and Quirks

- **Delete scope**: Removes indexed data, NOT the underlying file object [VERIFIED]
- **Legacy chunking**: Old files show type "other" [VERIFIED]
- **Beta header**: Requires OpenAI-Beta: assistants=v2 for REST [VERIFIED]
- **Overlap constraint**: chunk_overlap must not exceed half of max_chunk_size [VERIFIED]

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

- OAIAPI-SC-OAI-VSFIL - Vector Store Files API

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 16:00]**
- Enriched: Full object, chunking, SDK examples from 2026-03-20

**[2026-05-22 11:45]**
- Stub created
