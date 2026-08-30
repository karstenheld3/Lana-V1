# Vector Stores API

**Doc ID**: OAIAPI-IN36
**Goal**: Document Vector Stores for RAG, file management, chunking, and embedding configuration
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Vector Stores API manages document collections for RAG. Create vector store (POST /v1/vector_stores), add files, use with file_search tool in Responses API. Automatic chunking and embedding. Supports file batches, custom chunking (auto/static), expiration policies. File formats: PDF, DOCX, TXT, MD, HTML, CSV, etc. Files processed asynchronously. [VERIFIED] (OAIAPI-SC-OAI-VSCRT, OAIAPI-SC-OAI-GVECST)

## Key Facts

- **Purpose**: Document collections for RAG [VERIFIED]
- **Automatic**: Chunking and embedding handled automatically [VERIFIED]
- **File formats**: PDF, DOCX, TXT, MD, HTML, CSV, etc. [VERIFIED]
- **Integration**: Use with file_search tool [VERIFIED]
- **Async processing**: Files processed in background [VERIFIED]

## Vector Store Object

```json
{
  "id": "vs_abc123",
  "object": "vector_store",
  "name": "Product Documentation",
  "status": "completed",
  "usage_bytes": 150000000,
  "file_counts": {"total": 10, "completed": 10, "in_progress": 0, "failed": 0},
  "chunking_strategy": {"type": "auto"},
  "expires_after": null
}
```

Status: in_progress, completed, expired

## Chunking Strategies

- **auto** (default): Optimal settings automatically
- **static**: Custom `max_chunk_size_tokens` (100-4096) and `chunk_overlap_tokens` (0 to max/2)

## Expiration Policies

- **last_active_at**: Expires after N days of inactivity
- **created_at**: Expires N days after creation

## SDK Examples (Python)

### Create Vector Store

```python
from openai import OpenAI

client = OpenAI()

file_ids = []
for path in ["doc1.pdf", "doc2.pdf"]:
    with open(path, "rb") as f:
        file = client.files.create(file=f, purpose="assistants")
        file_ids.append(file.id)

vs = client.vector_stores.create(name="Product Docs", file_ids=file_ids)
print(f"VS: {vs.id}, Status: {vs.status}")
```

### Custom Chunking + Expiration

```python
from openai import OpenAI

client = OpenAI()

vs = client.vector_stores.create(
    name="Technical Docs",
    file_ids=["file_1", "file_2"],
    chunking_strategy={
        "type": "static",
        "static": {"max_chunk_size_tokens": 1000, "chunk_overlap_tokens": 200}
    },
    expires_after={"anchor": "last_active_at", "days": 7}
)
```

### Batch File Addition

```python
from openai import OpenAI

client = OpenAI()

file_ids = []
for i in range(10):
    with open(f"doc_{i}.pdf", "rb") as f:
        file = client.files.create(file=f, purpose="assistants")
        file_ids.append(file.id)

batch = client.vector_stores.file_batches.create(
    vector_store_id="vs_abc123", file_ids=file_ids
)
print(f"Batch: {batch.id}, Status: {batch.status}")
```

### Monitor Processing

```python
from openai import OpenAI
import time

client = OpenAI()

vs_id = "vs_abc123"
while True:
    vs = client.vector_stores.retrieve(vs_id)
    print(f"Completed: {vs.file_counts.completed}/{vs.file_counts.total}")
    if vs.status == "completed":
        break
    time.sleep(5)
```

### RAG Query

```python
from openai import OpenAI

client = OpenAI()

def ask_docs(question: str, vs_id: str) -> str:
    response = client.responses.create(
        model="gpt-5.6-sol",
        input=[{"role": "user", "content": question}],
        tools=[{
            "type": "file_search",
            "file_search": {"vector_store_ids": [vs_id], "max_num_results": 10}
        }]
    )
    return response.output[0].content[0].text

answer = ask_docs("What is the vacation policy?", "vs_abc123")
print(answer)
```

### Production Vector Store Manager

```python
from openai import OpenAI
from typing import List, Optional
import time

class VectorStoreManager:
    def __init__(self):
        self.client = OpenAI()
    
    def create_from_files(self, name: str, file_paths: List[str],
                          chunking: Optional[dict] = None, wait: bool = True):
        file_ids = []
        for path in file_paths:
            with open(path, "rb") as f:
                file = self.client.files.create(file=f, purpose="assistants")
                file_ids.append(file.id)
        
        params = {"name": name, "file_ids": file_ids}
        if chunking:
            params["chunking_strategy"] = chunking
        vs = self.client.vector_stores.create(**params)
        
        if wait:
            vs = self._wait(vs.id)
        return {"id": vs.id, "status": vs.status, "files": vs.file_counts.total}
    
    def _wait(self, vs_id: str, timeout: int = 600):
        start = time.time()
        while True:
            vs = self.client.vector_stores.retrieve(vs_id)
            if vs.status == "completed":
                return vs
            if time.time() - start > timeout:
                raise TimeoutError(f"Timeout: {vs_id}")
            time.sleep(5)
    
    def query(self, vs_id: str, question: str, model: str = "gpt-5.5"):
        response = self.client.responses.create(
            model=model, input=[{"role": "user", "content": question}],
            tools=[{"type": "file_search", "file_search": {"vector_store_ids": [vs_id]}}]
        )
        return response.output[0].content[0].text

manager = VectorStoreManager()
result = manager.create_from_files("KB", ["handbook.pdf", "faq.pdf"])
print(manager.query(result["id"], "What is the vacation policy?"))
```

## Error Responses

- **404 Not Found** - Vector store or file not found
- **400 Bad Request** - Invalid configuration or file format
- **413 Payload Too Large** - Too many files or size too large

## Differences from Other APIs

- **vs Pinecone**: OpenAI managed, Pinecone self-managed
- **vs Weaviate**: Simpler API, fewer config options
- **vs Chroma**: OpenAI integrated, Chroma standalone

## Limitations and Known Issues

- **File format support**: Not all formats supported [VERIFIED]
- **Processing time**: Large files take time to index [ASSUMED]
- **No custom embeddings**: Must use OpenAI embeddings [VERIFIED]

## Gotchas and Quirks

- **Async processing**: Files not immediately searchable [VERIFIED]
- **Deletion cascades**: Deleting vector store does not delete files [VERIFIED]
- **Storage costs**: Large vector stores consume storage quota [ASSUMED]

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

- OAIAPI-SC-OAI-VSCRT - POST Create vector store
- OAIAPI-SC-OAI-VSGET - GET Retrieve vector store
- OAIAPI-SC-OAI-VSFILE - Vector store files management
- OAIAPI-SC-OAI-GVECST - Vector stores guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 15:55]**
- Enriched: Full object, chunking, expiration, SDK examples (RAG, batch, manager) from 2026-03-20
- Updated: Model refs to gpt-5.5
- Changed: Doc ID from IN30 to IN36 per renumbering

**[2026-05-22 11:45]**
- Stub created
