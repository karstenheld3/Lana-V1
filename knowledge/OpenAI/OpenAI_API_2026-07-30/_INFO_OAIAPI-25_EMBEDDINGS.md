# Embeddings

**Doc ID**: OAIAPI-IN25
**Goal**: Document embeddings API with models, dimensions, use cases, and similarity search
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI Embeddings API (POST /v1/embeddings) converts text into numerical vector representations for semantic similarity, search, clustering, and recommendations. Models: text-embedding-3-large (3072 dimensions, highest quality), text-embedding-3-small (1536 dimensions, cost-effective), text-embedding-ada-002 (legacy, 1536 fixed). Supports dimension reduction via `dimensions` parameter. Input max 8191 tokens per text. Batch processing supported. Embeddings are deterministic and normalized to unit length. [VERIFIED] (OAIAPI-SC-OAI-EMBCRT, OAIAPI-SC-OAI-GEMBED)

## Key Facts

- **Endpoint**: POST /v1/embeddings [VERIFIED]
- **Models**: text-embedding-3-large, text-embedding-3-small, text-embedding-ada-002 [VERIFIED]
- **Dimensions**: Up to 3072 (configurable via `dimensions` param) [VERIFIED]
- **Max input**: 8191 tokens per text [VERIFIED]
- **Batch**: Multiple texts per request [VERIFIED]

## Models

- **text-embedding-3-large**: 3072 dims (default), configurable down, highest quality
- **text-embedding-3-small**: 1536 dims (default), configurable down, cost-effective
- **text-embedding-ada-002** (legacy): 1536 dims (fixed)

## Request Parameters

**Required:**
- **model**: Model ID
- **input**: Text string or array of strings

**Optional:**
- **dimensions**: Output vector size (v3 models only)
- **encoding_format**: "float" (default) or "base64"
- **user**: End-user identifier

## Response Format

```json
{
  "object": "list",
  "data": [
    {"object": "embedding", "index": 0, "embedding": [0.123, -0.456, 0.789]}
  ],
  "model": "text-embedding-3-large",
  "usage": {"prompt_tokens": 10, "total_tokens": 10}
}
```

## Similarity Calculation

OpenAI embeddings are normalized, so dot product = cosine similarity:

```python
import numpy as np

similarity = np.dot(embedding1, embedding2)
```

Distance metrics: cosine similarity (-1 to 1), euclidean distance (0 to inf), dot product

## SDK Examples (Python)

### Basic Embedding

```python
from openai import OpenAI

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-large",
    input="The quick brown fox jumps over the lazy dog"
)

embedding = response.data[0].embedding
print(f"Dimensions: {len(embedding)}")
```

### Batch Embeddings

```python
from openai import OpenAI

client = OpenAI()

texts = [
    "Machine learning is a subset of AI",
    "Neural networks are inspired by the brain",
    "Deep learning uses multiple layers"
]

response = client.embeddings.create(model="text-embedding-3-small", input=texts)
for i, data in enumerate(response.data):
    print(f"Text {i}: {len(data.embedding)} dimensions")
```

### Dimension Reduction

```python
from openai import OpenAI

client = OpenAI()

response_full = client.embeddings.create(model="text-embedding-3-large", input="Sample text")
print(f"Full: {len(response_full.data[0].embedding)} dimensions")

response_reduced = client.embeddings.create(
    model="text-embedding-3-large", input="Sample text", dimensions=1024
)
print(f"Reduced: {len(response_reduced.data[0].embedding)} dimensions")
```

### Semantic Search

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

documents = [
    "The cat sat on the mat",
    "The dog played in the park",
    "Machine learning is fascinating",
    "Deep learning uses neural networks"
]

doc_response = client.embeddings.create(model="text-embedding-3-small", input=documents)
doc_embeddings = [d.embedding for d in doc_response.data]

query = "Tell me about artificial intelligence"
query_response = client.embeddings.create(model="text-embedding-3-small", input=query)
query_embedding = query_response.data[0].embedding

similarities = [(i, np.dot(query_embedding, emb)) for i, emb in enumerate(doc_embeddings)]
similarities.sort(key=lambda x: x[1], reverse=True)

for i, sim in similarities[:2]:
    print(f"{documents[i]} (similarity: {sim:.4f})")
```

### Clustering

```python
from openai import OpenAI
from sklearn.cluster import KMeans
import numpy as np

client = OpenAI()

texts = ["Python programming", "Java development", "Cooking recipes",
         "Baking bread", "Machine learning", "Deep learning"]

response = client.embeddings.create(model="text-embedding-3-small", input=texts)
X = np.array([d.embedding for d in response.data])
kmeans = KMeans(n_clusters=3, random_state=0).fit(X)

for i, label in enumerate(kmeans.labels_):
    print(f"Cluster {label}: {texts[i]}")
```

### Production Embedding Service

```python
from openai import OpenAI
from typing import List, Union
import numpy as np

class EmbeddingService:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = OpenAI()
        self.model = model
    
    def embed(self, texts: Union[str, List[str]], dimensions: int = None) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        params = {"model": self.model, "input": texts}
        if dimensions:
            params["dimensions"] = dimensions
        response = self.client.embeddings.create(**params)
        return np.array([data.embedding for data in response.data])
    
    def similarity(self, text1: str, text2: str) -> float:
        embeddings = self.embed([text1, text2])
        return float(np.dot(embeddings[0], embeddings[1]))
    
    def find_most_similar(self, query: str, candidates: List[str], top_k: int = 5):
        embeddings = self.embed([query] + candidates)
        sims = [(candidates[i], float(np.dot(embeddings[0], embeddings[i+1])))
                for i in range(len(candidates))]
        sims.sort(key=lambda x: x[1], reverse=True)
        return sims[:top_k]

# Usage
service = EmbeddingService(model="text-embedding-3-large")
results = service.find_most_similar("AI and machine learning",
    ["Neural networks", "Cooking pasta", "AI applications", "Gardening"])
for text, sim in results:
    print(f"{text}: {sim:.4f}")
```

## Error Responses

- **400 Bad Request** - Invalid input or parameters
- **413 Payload Too Large** - Input exceeds token limit
- **429 Too Many Requests** - Rate limit exceeded

## Differences from Other APIs

- **vs Cohere**: Similar capabilities, different models
- **vs Sentence Transformers**: OpenAI hosted, ST self-hosted
- **vs Google Vertex AI**: Similar quality, different pricing

## Limitations and Known Issues

- **8191 token limit**: Longer texts must be chunked [VERIFIED]
- **English-optimized**: Best performance on English text [ASSUMED]
- **Static**: Embeddings don't change with context [ASSUMED]

## Gotchas and Quirks

- **Normalized vectors**: All embeddings normalized to unit length [VERIFIED]
- **Dimension reduction**: Can only reduce, not increase dimensions [VERIFIED]
- **Deterministic**: Same input always produces same embedding [VERIFIED]

## TypeScript Examples

### Create Embedding

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const result = await client.embeddings.create({
  model: "text-embedding-3-small",
  input: "Hello world",
  dimensions: 256,
});

console.log(`Dimensions: ${result.data[0].embedding.length}`);
```

### Batch Embeddings

```typescript
const result = await client.embeddings.create({
  model: "text-embedding-3-small",
  input: ["Hello", "World", "Test"],
});

console.log(`Vectors: ${result.data.length}`);
```

## Sources

- OAIAPI-SC-OAI-EMBCRT - POST Create embeddings
- OAIAPI-SC-OAI-GEMBED - Embeddings guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 15:15]**
- Enriched: Full models, similarity, SDK examples (search, clustering, production service) from 2026-03-20
- Changed: Doc ID from IN23 to IN25 per renumbering

**[2026-05-22 11:15]**
- Stub created
