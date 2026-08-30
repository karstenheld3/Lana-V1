# INFO: Gemini API File Search Stores

**Doc ID**: GEMAPI-IN28
**Goal**: Document file search stores (corpus/chunk-based RAG) for retrieval-augmented generation
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini API File Search Stores (also called Semantic Retrieval or Corpora) provide server-side retrieval-augmented generation (RAG). Users create a Corpus, upload Documents with Chunks of text, and the API automatically retrieves relevant chunks when answering queries. This is configured via the `retrieval` tool in the tools array. The Corpus API manages the lifecycle: create corpus, add documents, add chunks (with optional metadata), then query. Chunks are automatically embedded and indexed. This is conceptually similar to OpenAI's File Search (vector stores) in the Assistants API but uses a different API structure. The feature enables grounding model responses in custom knowledge bases without building external vector search infrastructure.

## Key Facts

- [VERIFIED] Corpus API: create, update, delete corpora (GEMAPI-SC-GOOG-SEMRET)
- [VERIFIED] Document/Chunk hierarchy within corpora (GEMAPI-SC-GOOG-SEMRET)
- [VERIFIED] Automatic embedding and indexing of chunks (GEMAPI-SC-GOOG-SEMRET)
- [VERIFIED] Retrieval tool integration with generateContent (GEMAPI-SC-GOOG-SEMRET)
- [VERIFIED] Chunk metadata for filtering (GEMAPI-SC-GOOG-SEMRET)

## Quick Reference

**Corpus**: `POST /v1beta/corpora` (create), `GET /v1beta/corpora` (list)
**Document**: `POST /v1beta/corpora/{corpus}/documents`
**Chunk**: `POST /v1beta/corpora/{corpus}/documents/{doc}/chunks`
**Query**: `POST /v1beta/corpora/{corpus}:query`
**Tool**: `{"retrieval": {"source": {"inlinePassages": {...}}}}` or corpus reference

## REST API

### Create Corpus

```json
POST https://generativelanguage.googleapis.com/v1beta/corpora

{
  "displayName": "Product Documentation"
}
```

### Add Document

```json
POST https://generativelanguage.googleapis.com/v1beta/corpora/{corpusId}/documents

{
  "displayName": "API Reference v2"
}
```

### Add Chunks

```json
POST https://generativelanguage.googleapis.com/v1beta/corpora/{corpusId}/documents/{docId}/chunks:batchCreate

{
  "requests": [
    {
      "chunk": {
        "data": {"stringValue": "The API supports REST and WebSocket protocols."},
        "customMetadata": [
          {"key": "section", "stringValue": "overview"},
          {"key": "version", "numericValue": 2}
        ]
      }
    }
  ]
}
```

### Query Corpus

```json
POST https://generativelanguage.googleapis.com/v1beta/corpora/{corpusId}:query

{
  "query": "What protocols are supported?",
  "resultsCount": 5,
  "metadataFilters": [
    {"key": "section", "conditions": [{"stringValue": "overview", "operation": "EQUAL"}]}
  ]
}
```

## Python Examples

### Example 1: Build and Query Knowledge Base

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Create corpus
corpus = client.corpora.create(display_name="Product FAQ")

# Add document
doc = client.corpora.documents.create(
    corpus=corpus.name,
    display_name="Common Questions"
)

# Add chunks
chunks_data = [
    "Our API supports both REST and WebSocket protocols for real-time communication.",
    "Authentication is handled via API keys passed in the x-goog-api-key header.",
    "Rate limits are 1000 RPM for Tier 1 users and 4000 RPM for Tier 2.",
]

for text in chunks_data:
    client.corpora.documents.chunks.create(
        document=doc.name,
        chunk=types.Chunk(data=types.ChunkData(string_value=text))
    )

# Query with retrieval
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How do I authenticate API requests?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(retrieval=types.Retrieval(
            source=types.RetrievalSource(corpus=corpus.name)
        ))]
    )
)
print(response.text)
```

**SDK-verified correction** (google-genai v1.68.0):

The types `RetrievalSource`, `GroundingPassage`, `GroundingPassages`, `Chunk`, `ChunkData`
and the `client.corpora` API do NOT exist in `google-genai`. These are from the deprecated
`google-generativeai` SDK. The new SDK uses `client.file_search_stores` + `types.FileSearch`.

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Create file search store
store = client.file_search_stores.create(
    config=types.CreateFileSearchStoreConfig(display_name="Product FAQ")
)

# Upload file to use with the store
file = client.files.upload(file="faq.txt")

# Query with file_search tool
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How do I authenticate API requests?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(file_search=types.FileSearch(
            file_search_store_names=[store.name]
        ))]
    )
)
print(response.text)
```

### Example 2: Inline Passages (No Corpus)

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

passages = [
    types.GroundingPassage(
        id="doc1",
        content=types.Content(parts=[
            types.Part(text="The Gemini API uses x-goog-api-key for authentication.")
        ])
    ),
    types.GroundingPassage(
        id="doc2",
        content=types.Content(parts=[
            types.Part(text="Rate limits are per-project, not per-key.")
        ])
    ),
]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How are rate limits applied?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(retrieval=types.Retrieval(
            source=types.RetrievalSource(
                inline_passages=types.GroundingPassages(passages=passages)
            )
        ))]
    )
)
print(response.text)
```

**SDK-verified correction** (google-genai v1.68.0):

`GroundingPassage`, `GroundingPassages`, `RetrievalSource` do NOT exist in `google-genai`.
Inline passages via Retrieval are not supported in the new SDK. Use `FileSearch` with
`file_search_store_names` or provide context directly in the prompt/system_instruction.

## Comparison with Other APIs

### vs OpenAI

- **Feature**: Gemini: Corpora/Semantic Retrieval | OpenAI: Vector Stores/File Search (Assistants)
- **Structure**: Gemini: Corpus > Document > Chunk | OpenAI: Vector Store > Files (auto-chunked)
- **Chunking**: Gemini: manual chunk creation | OpenAI: automatic chunking of uploaded files
- **Inline option**: Gemini: inline passages without corpus | OpenAI: no inline equivalent
- **Metadata**: Gemini: custom metadata + filtering | OpenAI: limited metadata

### vs Anthropic

- **RAG**: Gemini: built-in Corpus API | Anthropic: no built-in vector search
- **ADVANTAGE**: Gemini provides server-side RAG without external infrastructure

## Error Responses

- **400**: Invalid chunk data, metadata format errors
- **404**: Corpus or document not found
- **429**: Corpus operation rate limits

## Rate Limiting / Throttling

Corpus operations have separate rate limits. See GEMAPI-IN04.

## Limitations and Known Issues

- [COMMUNITY] Corpus API may have latency for large knowledge bases (GEMAPI-SC-GOOG-SEMRET)
- Manual chunking required (no auto-chunking of uploaded files)

## Gotchas and Quirks

- Unlike OpenAI's File Search which auto-chunks files, Gemini requires manual chunk creation
- Inline passages are an alternative when you don't want persistent storage
- Chunk metadata enables powerful filtering but requires upfront schema planning
- Corpus data persists until deleted (no TTL like File API)

## Sources

- GEMAPI-SC-GOOG-SEMRET: https://ai.google.dev/gemini-api/docs/semantic-retrieval [VERIFIED]

## Document History

**[2026-03-20 07:40]**
- Fixed: Example 1 used old SDK types (RetrievalSource, Chunk, ChunkData, client.corpora) - none exist in google-genai
- Fixed: Example 2 used GroundingPassage, GroundingPassages - not in google-genai
- Added: SDK-verified corrections using client.file_search_stores + types.FileSearch
- Source: google-genai v1.68.0, google/genai/file_search_stores.py, google/genai/types.py

**[2026-03-20 05:00]**
- Initial document created
