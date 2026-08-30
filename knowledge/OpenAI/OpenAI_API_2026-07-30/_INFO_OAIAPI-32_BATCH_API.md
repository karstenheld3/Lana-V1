# Batch API

**Doc ID**: OAIAPI-IN32
**Goal**: Document Batch API for asynchronous bulk processing with 50% cost reduction
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Batch API (`POST /v1/batches`) processes large volumes of requests asynchronously at 50% cost reduction. Submit JSONL files with requests, receive results within 24h. Supported endpoints: `/v1/chat/completions`, `/v1/responses`, `/v1/embeddings`, `/v1/images/generations` (NEW: GPT Image 2 Batch support), `/v1/videos` (NEW: Sora Batch support). Maximum batch queue limits vary by tier. [VERIFIED] (OAIAPI-SC-OAI-BTCAPI, OAIAPI-SC-OAI-GBATCH)

## Key Facts

- **Cost**: 50% discount vs real-time API [VERIFIED] (OAIAPI-SC-OAI-GBATCH)
- **Rate limits**: No RPM/TPM limits for batch requests [VERIFIED] (OAIAPI-SC-OAI-GBATCH)
- **Completion**: Within 24 hours (often faster) [VERIFIED] (OAIAPI-SC-OAI-BATCRT)
- **Max requests**: 50,000 per batch [VERIFIED] (OAIAPI-SC-OAI-GBATCH)
- **Supported endpoints**: `/v1/chat/completions`, `/v1/responses`, `/v1/embeddings`, `/v1/images/generations`, `/v1/videos` [VERIFIED]

## Use Cases

- **Bulk embeddings**: Process thousands of documents at half price
- **Data processing**: Transform large datasets offline
- **Evaluations**: Run eval suites without rate limit concerns
- **Content generation**: Generate batch content overnight
- **Cost optimization**: 50% savings for non-urgent workloads

## REST API

**Create**: `POST /v1/batches`
**Retrieve**: `GET /v1/batches/{batch_id}`
**List**: `GET /v1/batches`
**Cancel**: `POST /v1/batches/{batch_id}/cancel`

### Create Batch Request

```json
{
  "input_file_id": "file-abc123",
  "endpoint": "/v1/chat/completions",
  "completion_window": "24h"
}
```

**Required parameters:**
- **input_file_id** (string) - File ID from Files API (JSONL format)
- **endpoint** (string) - Target API endpoint
- **completion_window** (string) - Currently only `"24h"` supported

### Batch Object Response

```json
{
  "id": "batch_abc123",
  "object": "batch",
  "endpoint": "/v1/chat/completions",
  "input_file_id": "file_xyz",
  "completion_window": "24h",
  "status": "in_progress",
  "created_at": 1234567890,
  "request_counts": {
    "total": 1000,
    "completed": 500,
    "failed": 10
  },
  "output_file_id": "file_out123",
  "error_file_id": "file_err123"
}
```

## Request File Format (JSONL)

Each line in the input file:

```json
{
  "custom_id": "request-1",
  "method": "POST",
  "url": "/v1/chat/completions",
  "body": {
    "model": "gpt-5.5",
    "messages": [{"role": "user", "content": "Summarize article 1"}],
    "max_completion_tokens": 200
  }
}
```

**Required fields per line:**
- **custom_id** (string) - Unique identifier (max 64 chars), used to match results
- **method** (string) - Always `"POST"`
- **url** (string) - API endpoint path
- **body** (object) - Same parameters as the real-time API

## Batch Status Values

- **validating** - Checking input file format and validity
- **in_progress** - Processing requests
- **finalizing** - Completing and writing output
- **completed** - All requests processed successfully
- **failed** - Batch failed (check error_file_id)
- **expired** - Exceeded 24-hour window
- **cancelled** - User cancelled via API

## Results Format

### Success

```json
{
  "id": "batch_req_abc",
  "custom_id": "request-1",
  "response": {
    "status_code": 200,
    "request_id": "req_xyz",
    "body": {
      "id": "chatcmpl_123",
      "object": "chat.completion",
      "model": "gpt-5.5",
      "choices": [{"message": {"role": "assistant", "content": "..."}}]
    }
  },
  "error": null
}
```

### Error

```json
{
  "id": "batch_req_def",
  "custom_id": "request-2",
  "response": {"status_code": 400, "request_id": "req_abc"},
  "error": {
    "message": "Invalid request",
    "type": "invalid_request_error",
    "code": "invalid_value"
  }
}
```

## SDK Examples (Python)

### Prepare and Submit Batch

```python
from openai import OpenAI
import json

client = OpenAI()

# Prepare batch file
requests = []
for i in range(1000):
    requests.append({
        "custom_id": f"request-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-5.5",
            "messages": [{"role": "user", "content": f"Summarize article {i}"}],
            "max_completion_tokens": 200
        }
    })

with open("batch_requests.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# Upload file
batch_file = client.files.create(
    file=open("batch_requests.jsonl", "rb"),
    purpose="batch",
)

# Create batch (50% cheaper, no rate limits)
batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
)
print(f"Batch: {batch.id}, Status: {batch.status}")
```

### Monitor and Retrieve Results

```python
from openai import OpenAI
import time
import json

client = OpenAI()

batch_id = "batch_abc123"

# Poll until complete
while True:
    batch = client.batches.retrieve(batch_id)
    print(f"Status: {batch.status}, Progress: {batch.request_counts.completed}/{batch.request_counts.total}")

    if batch.status in ("completed", "failed", "expired", "cancelled"):
        break
    time.sleep(60)

# Download results
if batch.status == "completed":
    output = client.files.content(batch.output_file_id)
    results = [json.loads(line) for line in output.text.strip().split("\n")]
    print(f"Got {len(results)} results")

    for result in results[:5]:
        print(f"  {result['custom_id']}: {result['response']['body']['choices'][0]['message']['content'][:80]}")
```

### Batch Embeddings

```python
from openai import OpenAI
import json

client = OpenAI()

documents = ["Document 1 text...", "Document 2 text...", "Document 3 text..."]

requests = []
for i, doc in enumerate(documents):
    requests.append({
        "custom_id": f"embed-{i}",
        "method": "POST",
        "url": "/v1/embeddings",
        "body": {
            "model": "text-embedding-3-small",
            "input": doc
        }
    })

with open("embed_batch.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

batch_file = client.files.create(file=open("embed_batch.jsonl", "rb"), purpose="batch")
batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/embeddings",
    completion_window="24h",
)
print(f"Embedding batch: {batch.id}")
```

## Limitations and Known Issues

- **No streaming**: Batch results are complete responses only [VERIFIED]
- **24h max**: Batches that exceed 24h expire [VERIFIED]
- **50K limit**: Maximum 50,000 requests per batch [VERIFIED]
- **File size**: Input file limited to 100 MB [VERIFIED]

## Gotchas and Quirks

- **Image Batch**: GPT Image 2 supports Batch via `/v1/images/generations` with 50% discount [VERIFIED]
- **Video Batch**: Sora models support Batch via `/v1/videos` [VERIFIED]
- **Responses Batch**: `/v1/responses` endpoint now supported for batch [VERIFIED]
- **Results order**: Output lines match input order by custom_id [VERIFIED]
- **Partial success**: Batch can complete with some failed requests (check error_file_id) [VERIFIED]
- **completion_window**: Only "24h" is currently supported, no shorter windows [VERIFIED]

## TypeScript Examples

### Basic Response

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Explain this concept briefly.",
});

console.log(response.output_text);
```

### With Instructions

```typescript
const response = await client.responses.create({
  model: "gpt-4o-mini",
  instructions: "You are a helpful assistant.",
  input: "What is 2+2?",
});

console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-BTCAPI - Batch API create/retrieve/list/cancel
- OAIAPI-SC-OAI-GBATCH - Batch API guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Full JSONL format, status values, results format, monitoring, embeddings batch, limitations

**[2026-05-22 11:15]**
- Added: Image and Video Batch support notes
