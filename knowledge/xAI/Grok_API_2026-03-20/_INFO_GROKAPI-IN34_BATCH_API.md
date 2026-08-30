# INFO: Batch API

**Doc ID**: GROKAPI-IN34
**Goal**: Async batch processing, JSONL format, batch lifecycle, cost savings, limitations
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Batch API enables processing large volumes of requests asynchronously at reduced pricing. Requests are submitted as JSONL files, processed in the background, and results retrieved when complete. The lifecycle: upload JSONL file -> create batch -> monitor progress -> retrieve results. Supports cancel, list, check status, and cost tracking operations. Tool use is supported in batch requests. Batch processing is ideal for non-time-sensitive workloads like data labeling, classification, content generation, and bulk analysis. Batch API pricing is discounted compared to real-time API calls. [VERIFIED] (GROKAPI-SC-XAI-BATCH | https://docs.x.ai/developers/advanced-api-usage/batch-api)

## Key Facts

- [VERIFIED] Async processing at reduced pricing (GROKAPI-SC-XAI-BATCH)
- [VERIFIED] JSONL file format for input (GROKAPI-SC-XAI-BATCH)
- [VERIFIED] Lifecycle: upload -> create -> monitor -> retrieve (GROKAPI-SC-XAI-BATCH)
- [VERIFIED] Supports cancel, list, status check, cost tracking (GROKAPI-SC-XAI-BATCH)
- [VERIFIED] Tool use supported in batch requests (GROKAPI-SC-XAI-BATCH)

## Quick Reference

- **Upload JSONL**: `POST /v1/files` (purpose: "batch")
- **Create batch**: `POST /v1/batches`
- **Get status**: `GET /v1/batches/{batch_id}`
- **List batches**: `GET /v1/batches`
- **Cancel**: `POST /v1/batches/{batch_id}/cancel`
- **Results**: Download output file via `GET /v1/files/{output_file_id}/content`

## JSONL Input Format

Each line is a JSON object with:
```json
{"custom_id": "req-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "grok-4.20-beta-latest-non-reasoning", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 100}}
```

## Examples

### Complete Batch Workflow (OpenAI SDK)

```python
import os
import time
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# Step 1: Upload JSONL file
batch_file = client.files.create(
    file=open("batch_input.jsonl", "rb"),
    purpose="batch",
)

# Step 2: Create batch
batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
)
print(f"Batch ID: {batch.id}")

# Step 3: Monitor progress
while True:
    batch = client.batches.retrieve(batch.id)
    print(f"Status: {batch.status} ({batch.request_counts.completed}/{batch.request_counts.total})")
    if batch.status in ("completed", "failed", "expired"):
        break
    time.sleep(30)

# Step 4: Retrieve results
if batch.status == "completed":
    content = client.files.content(batch.output_file_id)
    with open("batch_output.jsonl", "wb") as f:
        f.write(content.content)
```

### cURL

```bash
# Upload JSONL
curl https://api.x.ai/v1/files \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -F purpose="batch" \
  -F file="@batch_input.jsonl"

# Create batch
curl https://api.x.ai/v1/batches \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input_file_id": "file-abc123", "endpoint": "/v1/chat/completions", "completion_window": "24h"}'
```

## Use Cases

- **Data labeling**: Classify thousands of text samples
- **Content generation**: Generate descriptions for product catalogs
- **Bulk analysis**: Analyze large document sets
- **Translation**: Translate content at scale
- **Evaluation**: Run model evaluations on test datasets

## Differences from Other APIs

### vs OpenAI
- **Compatible**: Same Batch API format and endpoints
- **Same JSONL format**: Same input/output format
- **Same SDK**: `client.batches.create()` works for both

### vs Anthropic
- **Similar concept**: Anthropic has Message Batches API
- **Different format**: Anthropic uses different batch request structure

### vs Gemini
- **No equivalent**: Gemini has no batch API (uses standard concurrent requests)

## Sources

- GROKAPI-SC-XAI-BATCH | https://docs.x.ai/developers/advanced-api-usage/batch-api | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:40]**
- Initial document created with Batch API lifecycle, JSONL format, and examples
