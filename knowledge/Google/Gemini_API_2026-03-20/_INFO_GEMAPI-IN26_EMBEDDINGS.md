# INFO: Gemini API Embeddings

**Doc ID**: GEMAPI-IN26
**Goal**: Document the embedContent endpoint, embedding models, task types, and dimensionality
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini API provides text and multimodal embeddings via the `embedContent` endpoint (`POST /v1beta/models/{model}:embedContent`) and batch variant `batchEmbedContents`. Embedding models include `gemini-embedding-001` (text-only, 768 dimensions) and `gemini-embedding-2-preview` (multimodal: text, image, video, audio). A `taskType` parameter optimizes embeddings for specific use cases: RETRIEVAL_QUERY, RETRIEVAL_DOCUMENT, SEMANTIC_SIMILARITY, CLASSIFICATION, CLUSTERING, QUESTION_ANSWERING, and FACT_VERIFICATION. Output dimensionality is configurable (128, 256, 512, 768 for gemini-embedding-001). The batch endpoint processes up to 100 texts in a single request. Embeddings are returned as float arrays in the `values` field. This is a first-class API feature, unlike OpenAI which uses a separate endpoint with different models.

## Key Facts

- [VERIFIED] Endpoint: `POST /v1beta/models/{model}:embedContent` (GEMAPI-SC-GOOG-EMBEDS)
- [VERIFIED] Batch: `POST /v1beta/models/{model}:batchEmbedContents` (up to 100) (GEMAPI-SC-GOOG-EMBEDS)
- [VERIFIED] Models: gemini-embedding-001 (text), gemini-embedding-2-preview (multimodal) (GEMAPI-SC-GOOG-EMBEDS)
- [VERIFIED] Task types: RETRIEVAL_QUERY, RETRIEVAL_DOCUMENT, SEMANTIC_SIMILARITY, CLASSIFICATION, CLUSTERING, QUESTION_ANSWERING, FACT_VERIFICATION (GEMAPI-SC-GOOG-EMBEDS)
- [VERIFIED] Configurable output dimensions (GEMAPI-SC-GOOG-EMBEDS)
- [VERIFIED] gemini-embedding-2-preview: text + image + video + audio (GEMAPI-SC-GOOG-EMBEDS)

## Quick Reference

**Single**: `POST /v1beta/models/{model}:embedContent`
**Batch**: `POST /v1beta/models/{model}:batchEmbedContents`
**Models**: `gemini-embedding-001`, `gemini-embedding-2-preview`
**Dimensions**: 128, 256, 512, 768 (model-dependent)

## REST API

### embedContent Request

```json
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent

{
  "content": {
    "parts": [{"text": "What is the meaning of life?"}]
  },
  "taskType": "RETRIEVAL_QUERY",
  "outputDimensionality": 256
}
```

### Response

```json
{
  "embedding": {
    "values": [0.013168523, -0.008711934, 0.04562653, ...]
  }
}
```

### batchEmbedContents Request

```json
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:batchEmbedContents

{
  "requests": [
    {
      "content": {"parts": [{"text": "Document 1 text"}]},
      "taskType": "RETRIEVAL_DOCUMENT"
    },
    {
      "content": {"parts": [{"text": "Document 2 text"}]},
      "taskType": "RETRIEVAL_DOCUMENT"
    }
  ]
}
```

### Batch Response

```json
{
  "embeddings": [
    {"values": [0.013, -0.008, ...]},
    {"values": [0.025, 0.012, ...]}
  ]
}
```

**Task Types:**
- **RETRIEVAL_QUERY**: Optimize for search queries
- **RETRIEVAL_DOCUMENT**: Optimize for document indexing
- **SEMANTIC_SIMILARITY**: General similarity comparison
- **CLASSIFICATION**: Text classification tasks
- **CLUSTERING**: Grouping similar content
- **QUESTION_ANSWERING**: Q&A embeddings
- **FACT_VERIFICATION**: Fact-checking embeddings

## Python Examples

### Example 1: Single Embedding

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents="What is machine learning?",
    config={"task_type": "RETRIEVAL_QUERY", "output_dimensionality": 256}
)
print(f"Dimensions: {len(result.embeddings[0].values)}")
print(f"First 5 values: {result.embeddings[0].values[:5]}")
```

### Example 2: Batch Embeddings for Document Search

```python
from google import genai
import numpy as np
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

documents = [
    "Python is a programming language.",
    "Machine learning uses statistical methods.",
    "The Eiffel Tower is in Paris.",
    "Neural networks are inspired by the brain.",
]

# Embed documents
doc_result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=documents,
    config={"task_type": "RETRIEVAL_DOCUMENT", "output_dimensionality": 256}
)

# Embed query
query = "How does AI learn?"
query_result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=query,
    config={"task_type": "RETRIEVAL_QUERY", "output_dimensionality": 256}
)

# Calculate similarity
query_vec = np.array(query_result.embeddings[0].values)
for i, doc in enumerate(documents):
    doc_vec = np.array(doc_result.embeddings[i].values)
    similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
    print(f"{similarity:.3f} - {doc}")
```

### Example 3: Multimodal Embeddings

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Text embedding
text_result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="A sunset over the ocean"
)

# Image embedding
with open("sunset.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

image_result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[types.Content(parts=[
        types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=image_data))
    ])]
)

print(f"Text embedding dims: {len(text_result.embeddings[0].values)}")
print(f"Image embedding dims: {len(image_result.embeddings[0].values)}")
```

## cURL Examples

### Example: Single Embedding

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": {"parts": [{"text": "What is the meaning of life?"}]},
    "taskType": "RETRIEVAL_QUERY",
    "outputDimensionality": 256
  }'
```

## Comparison with Other APIs

### vs OpenAI

- **Endpoint**: Gemini: `embedContent` | OpenAI: `/v1/embeddings`
- **Task types**: Gemini: 7 task type optimizations | OpenAI: none (single general embedding)
- **Multimodal**: Gemini: text + image + video + audio | OpenAI: text only
- **Dimensions**: Gemini: configurable (128-768) | OpenAI: configurable (text-embedding-3)
- **Batch**: Gemini: batchEmbedContents (100) | OpenAI: array input (2048)
- **UNIQUE to Gemini**: Task type optimization, multimodal embeddings

### vs Anthropic

- **Embeddings**: Gemini: first-class API | Anthropic: Voyage AI partnership (separate API)
- **ADVANTAGE**: Gemini embeddings are native to the API

## Error Responses

- **400**: Content too long, invalid task type, unsupported dimensionality
- **404**: Invalid embedding model name

## Rate Limiting / Throttling

Embedding endpoints have separate RPM limits, typically higher than generation. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] gemini-embedding-2-preview is preview status (GEMAPI-SC-GOOG-MODELS)
- Maximum input length varies by model
- Batch limit: 100 items per request

## Gotchas and Quirks

- Use matching task types: RETRIEVAL_QUERY for queries, RETRIEVAL_DOCUMENT for docs
- Mismatched task types reduce search quality significantly
- Lower dimensions (128, 256) trade accuracy for speed/storage - test for your use case
- `content` field (singular) for single, `contents` for batch - naming inconsistency
- Multimodal embeddings (gemini-embedding-2-preview) produce same-dimensional vectors regardless of modality

## Sources

- GEMAPI-SC-GOOG-EMBEDS: https://ai.google.dev/gemini-api/docs/embeddings [VERIFIED]
- GEMAPI-SC-GOOG-EMBREF: https://ai.google.dev/api/embeddings [VERIFIED]

## Document History

**[2026-03-20 04:50]**
- Initial document created with embeddings API documentation
