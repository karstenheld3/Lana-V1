# INFO: Collections API

**Doc ID**: GROKAPI-IN30
**Goal**: Collection CRUD, document upload, indexing, management via API and Console
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Collections API enables creating and managing document collections for RAG (Retrieval-Augmented Generation) with the `collections_search` tool. Collections are containers for uploaded documents that are automatically indexed for semantic search. Documents can be uploaded via the API or xAI Console. Collections support CRUD operations: create, list, get, update, delete. Files within collections also support CRUD. The API uses the standard `https://api.x.ai/v1/` base URL. Collections can also be managed via the xAI Console UI. This is a **unique Grok feature** - a fully integrated RAG pipeline within the API (OpenAI has a similar concept with vector stores in Assistants, but different architecture). [VERIFIED] (GROKAPI-SC-XAI-COLLECTIONS | https://docs.x.ai/developers/collections)

## Key Facts

- [VERIFIED] Collections are containers for uploaded documents (GROKAPI-SC-XAI-COLLECTIONS)
- [VERIFIED] Documents automatically indexed for semantic search (GROKAPI-SC-XAI-COLLECTIONS)
- [VERIFIED] CRUD: Create, list, get, update, delete collections and files (GROKAPI-SC-XAI-COLLECTIONS)
- [VERIFIED] Used with `collections_search` tool for RAG queries (GROKAPI-SC-XAI-COLLSEARCH)
- [VERIFIED] Console management: https://console.x.ai (GROKAPI-SC-XAI-COLLECTIONS)

## Quick Reference

### Collection Endpoints
- **Create**: `POST /v1/collections`
- **List**: `GET /v1/collections`
- **Get**: `GET /v1/collections/{collection_id}`
- **Update**: `PUT /v1/collections/{collection_id}`
- **Delete**: `DELETE /v1/collections/{collection_id}`

### File Endpoints
- **Upload**: `POST /v1/collections/{collection_id}/files`
- **List**: `GET /v1/collections/{collection_id}/files`
- **Get**: `GET /v1/collections/{collection_id}/files/{file_id}`
- **Delete**: `DELETE /v1/collections/{collection_id}/files/{file_id}`

## Examples

### Create Collection and Upload Document

```python
import os
import requests

api_key = os.getenv("XAI_API_KEY")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

# Create collection
collection = requests.post(
    "https://api.x.ai/v1/collections",
    headers=headers,
    json={"name": "Q3 Reports", "description": "Quarterly financial reports"},
).json()

collection_id = collection["id"]

# Upload file
with open("q3_report.pdf", "rb") as f:
    upload = requests.post(
        f"https://api.x.ai/v1/collections/{collection_id}/files",
        headers={"Authorization": f"Bearer {api_key}"},
        files={"file": ("q3_report.pdf", f, "application/pdf")},
    ).json()

print(f"Collection: {collection_id}")
print(f"File: {upload['id']}")
```

### Query Collection with collections_search

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What were Q3 revenue figures?"}],
    tools=[{"type": "collections_search", "collection_ids": [collection_id]}],
)
print(response.output_text)
```

## Differences from Other APIs

### vs OpenAI
- **Similar concept**: OpenAI has vector stores in Assistants API
- **Different architecture**: xAI collections are standalone resources; OpenAI vector stores are tied to Assistants
- **Integrated RAG**: xAI collections_search works in standard Responses API (not just Assistants)

### vs Anthropic
- **UNIQUE**: Anthropic has no built-in document storage or RAG

### vs Gemini
- **Similar**: Gemini has semantic retrieval with corpora
- **Different API**: Different management endpoints

## Sources

- GROKAPI-SC-XAI-COLLECTIONS | https://docs.x.ai/developers/collections | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:25]**
- Initial document created with Collections API reference
