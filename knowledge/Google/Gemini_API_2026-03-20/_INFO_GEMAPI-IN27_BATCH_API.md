# INFO: Gemini API Batch Processing

**Doc ID**: GEMAPI-IN27
**Goal**: Document batchGenerateContent endpoint, async processing, and batch job management
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini Batch API enables asynchronous bulk processing of multiple `generateContent` requests in a single batch job. Requests are submitted as a JSONL file (one request per line) via `POST /v1beta/models/{model}:batchGenerateContent`. The API processes requests asynchronously and writes results to a specified output location. Batch jobs have separate rate limits: 100 concurrent requests, 2GB input file size, and 20GB storage. Batch processing is ideal for non-time-sensitive workloads like data labeling, content classification, bulk summarization, and offline analysis. Jobs can be monitored, listed, and cancelled. This is conceptually similar to OpenAI's Batch API but uses a different file format and management interface.

## Key Facts

- [VERIFIED] Endpoint: `POST /v1beta/models/{model}:batchGenerateContent` (GEMAPI-SC-GOOG-BATCH)
- [VERIFIED] Input: JSONL file with generateContent requests (GEMAPI-SC-GOOG-BATCH)
- [VERIFIED] Asynchronous processing (GEMAPI-SC-GOOG-BATCH)
- [VERIFIED] Limits: 100 concurrent, 2GB input, 20GB storage (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Jobs can be monitored, listed, cancelled (GEMAPI-SC-GOOG-BATCH)

## Quick Reference

**Create**: `POST /v1beta/models/{model}:batchGenerateContent`
**List**: `GET /v1beta/batchJobs`
**Get**: `GET /v1beta/batchJobs/{name}`
**Cancel**: `POST /v1beta/batchJobs/{name}:cancel`

## Python Examples

### Example 1: Submit Batch Job

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Create batch requests
requests = []
prompts = [
    "Classify this text as positive/negative: 'Great product!'",
    "Classify this text as positive/negative: 'Terrible service.'",
    "Classify this text as positive/negative: 'It was okay.'",
]

for i, prompt in enumerate(prompts):
    requests.append(types.BatchGenerateContentRequest(
        request=types.GenerateContentRequest(
            model="gemini-2.5-flash",
            contents=[types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            )]
        ),
        metadata={"id": f"request_{i}"}
    ))

# Submit batch
batch_job = client.batches.create(
    model="gemini-2.5-flash",
    requests=requests
)
print(f"Batch job: {batch_job.name}")
print(f"State: {batch_job.state}")
```

**SDK-verified correction** (google-genai v1.68.0, `google/genai/batches.py`):

`BatchGenerateContentRequest` and `GenerateContentRequest` do NOT exist in `google-genai`.
The SDK uses `types.InlinedRequest` passed as `src` to `client.batches.create()`.

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompts = [
    "Classify this text as positive/negative: 'Great product!'",
    "Classify this text as positive/negative: 'Terrible service.'",
    "Classify this text as positive/negative: 'It was okay.'",
]

requests = [
    types.InlinedRequest(
        contents=prompt,
        metadata={"id": f"request_{i}"},
    )
    for i, prompt in enumerate(prompts)
]

batch_job = client.batches.create(
    model="gemini-2.5-flash",
    src=requests,
)
print(f"Batch job: {batch_job.name}")
print(f"State: {batch_job.state}")
```

### Example 2: Monitor and Retrieve Results

```python
from google import genai
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Poll for completion
job_name = "batchJobs/abc123"
while True:
    job = client.batches.get(name=job_name)
    print(f"State: {job.state}")
    if job.state in ("SUCCEEDED", "FAILED", "CANCELLED"):
        break
    time.sleep(10)

# Get results
if job.state == "SUCCEEDED":
    for result in client.batches.list_results(name=job_name):
        print(f"Request {result.metadata.get('id')}: {result.response.text[:100]}")
```

## Comparison with Other APIs

### vs OpenAI

- **Batch endpoint**: Gemini: `batchGenerateContent` | OpenAI: `/v1/batches`
- **Input format**: Gemini: inline requests or JSONL | OpenAI: JSONL file upload
- **Pricing**: Gemini: standard pricing | OpenAI: 50% discount
- **Completion time**: Both: up to 24 hours
- **Management**: Both support list/get/cancel operations

### vs Anthropic

- **Batch endpoint**: Gemini: `batchGenerateContent` | Anthropic: `/v1/messages/batches`
- **Pricing**: Gemini: standard | Anthropic: 50% discount
- **Management**: Similar operations available

## Error Responses

- **400**: Invalid batch format, too many requests
- **429**: Too many concurrent batch jobs
- Job state "FAILED": Processing error in one or more requests

## Rate Limiting / Throttling

Separate batch limits: 100 concurrent, 2GB input, 20GB storage. Per-model enqueued token limits. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] 100 concurrent batch requests max (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] 2GB input file size limit (GEMAPI-SC-GOOG-RTLMTS)
- No streaming support in batch mode
- Results not available until entire batch completes

## Gotchas and Quirks

- Batch processing is async - not suitable for real-time applications
- Individual request failures within a batch do not fail the entire job
- No batch pricing discount (unlike OpenAI's 50% off)
- Storage limits shared with File API (20GB total)

## Sources

- GEMAPI-SC-GOOG-BATCH: https://ai.google.dev/gemini-api/docs/batch [VERIFIED]
- GEMAPI-SC-GOOG-RTLMTS: https://ai.google.dev/gemini-api/docs/rate-limits [VERIFIED]

## Document History

**[2026-03-20 07:45]**
- Fixed: BatchGenerateContentRequest/GenerateContentRequest don't exist in SDK
- Added: SDK-verified correction using types.InlinedRequest + client.batches.create(src=...)
- Source: google-genai v1.68.0, google/genai/batches.py

**[2026-03-20 04:55]**
- Initial document created
