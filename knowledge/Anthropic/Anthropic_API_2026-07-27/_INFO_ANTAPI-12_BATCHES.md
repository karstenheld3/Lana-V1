# Message Batches API

**Doc ID**: ANTAPI-IN12
**Goal**: Document Message Batches API - create, retrieve, list, cancel, delete, results endpoints
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` for Messages API request schema

## Summary

The Message Batches API processes large volumes of Messages requests asynchronously with 50% cost reduction. Each batch can contain up to 100,000 requests or 256 MB. Batches are processed within 1 hour typically, with a 24-hour expiration window. Results are available in JSONL format for 29 days. All active models and all Messages API features are supported. Opus 4.7, Opus 4.6, and Sonnet 4.6 support up to 300k output tokens per request via the `output-300k-2026-03-24` beta header.

## Key Facts

- **Base Endpoint**: `/v1/messages/batches`
- **Cost**: 50% reduction vs standard Messages API
- **Max Requests**: 100,000 per batch
- **Max Size**: 256 MB per batch
- **Processing**: Most complete within 1 hour
- **Expiration**: 24 hours if not completed
- **Results Retention**: 29 days after creation
- **Result Format**: JSONL (one JSON object per line)
- **Scope**: Workspace-level (scoped to API key's workspace)
- **Status**: GA

## Endpoints

### POST /v1/messages/batches - Create Batch

**Request Body:**

- **requests** (`array[BatchRequest]`, required) - List of message requests, each containing:
  - **custom_id** (`string`, required) - Unique identifier for tracking this request
  - **params** (`object`, required) - Standard Messages API parameters (model, max_tokens, messages, etc.)

```python
import anthropic

client = anthropic.Anthropic()

batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": "request-001",
            "params": {
                "model": "claude-opus-5",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "Hello, world"}],
            },
        },
        {
            "custom_id": "request-002",
            "params": {
                "model": "claude-opus-5",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "Hi again, friend"}],
            },
        },
    ]
)
print(f"Batch ID: {batch.id}")
print(f"Status: {batch.processing_status}")
```

**Response (MessageBatch):**

```json
{
  "id": "msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d",
  "type": "message_batch",
  "processing_status": "in_progress",
  "request_counts": {
    "processing": 2,
    "succeeded": 0,
    "errored": 0,
    "canceled": 0,
    "expired": 0
  },
  "ended_at": null,
  "created_at": "2024-09-24T18:37:24.100435Z",
  "expires_at": "2024-09-25T18:37:24.100435Z",
  "cancel_initiated_at": null,
  "results_url": null
}
```

### GET /v1/messages/batches/{batch_id} - Retrieve Batch

```python
batch = client.messages.batches.retrieve("msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d")
print(f"Status: {batch.processing_status}")
print(f"Succeeded: {batch.request_counts.succeeded}")
print(f"Results URL: {batch.results_url}")
```

### GET /v1/messages/batches - List Batches

```python
batches = client.messages.batches.list()
for batch in batches:
    print(f"{batch.id}: {batch.processing_status}")
```

### POST /v1/messages/batches/{batch_id}/cancel - Cancel Batch

Initiates cancellation. Already-completed requests are not affected.

```python
batch = client.messages.batches.cancel("msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d")
print(f"Cancel initiated: {batch.cancel_initiated_at}")
```

### DELETE /v1/messages/batches/{batch_id} - Delete Batch

```python
result = client.messages.batches.delete("msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d")
```

### GET /v1/messages/batches/{batch_id}/results - Retrieve Results

Returns JSONL stream of results. Each line contains `custom_id` and `result` with type `succeeded`, `errored`, `canceled`, or `expired`.

```python
# Stream results
results = client.messages.batches.results("msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d")
for result in results:
    if result.result.type == "succeeded":
        message = result.result.message
        print(f"{result.custom_id}: {message.content[0].text[:50]}")
    elif result.result.type == "errored":
        print(f"{result.custom_id}: ERROR - {result.result.error}")
    elif result.result.type == "expired":
        print(f"{result.custom_id}: EXPIRED")
    elif result.result.type == "canceled":
        print(f"{result.custom_id}: CANCELED")
```

## MessageBatch Response Fields

- **id** (`string`) - Batch ID (format: `msgbatch_...`)
- **type** (`string`) - Always `"message_batch"`
- **processing_status** (`string`) - `"in_progress"` or `"ended"`
- **request_counts** (`object`) - Counts per result type:
  - **processing** (`integer`) - Still being processed
  - **succeeded** (`integer`) - Completed successfully
  - **errored** (`integer`) - Failed with error
  - **canceled** (`integer`) - Canceled before completion
  - **expired** (`integer`) - Expired (24h limit)
- **created_at** (`string`) - ISO 8601 creation timestamp
- **ended_at** (`string | null`) - ISO 8601 completion timestamp
- **expires_at** (`string`) - ISO 8601 expiration timestamp (24h from creation)
- **cancel_initiated_at** (`string | null`) - ISO 8601 cancel initiation timestamp
- **results_url** (`string | null`) - URL to download results (available when ended)

## Result Types (JSONL)

Each result line:

```json
{"custom_id": "request-001", "result": {"type": "succeeded", "message": {...}}}
{"custom_id": "request-002", "result": {"type": "errored", "error": {"type": "invalid_request", "message": "..."}}}
{"custom_id": "request-003", "result": {"type": "expired"}}
{"custom_id": "request-004", "result": {"type": "canceled"}}
```

For `errored` results: `invalid_request` errors require fixing the request body; server errors can be retried directly.

## Complete Batch Workflow

```python
import anthropic
import time

client = anthropic.Anthropic()

# 1. Create batch
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"item-{i}",
            "params": {
                "model": "claude-opus-5",
                "max_tokens": 256,
                "messages": [{"role": "user", "content": f"Summarize topic {i}"}],
            },
        }
        for i in range(100)
    ]
)
print(f"Created batch: {batch.id}")

# 2. Poll for completion
while True:
    batch = client.messages.batches.retrieve(batch.id)
    if batch.processing_status == "ended":
        break
    print(f"Processing: {batch.request_counts.processing} remaining...")
    time.sleep(30)

# 3. Retrieve results
print(f"Succeeded: {batch.request_counts.succeeded}")
print(f"Errored: {batch.request_counts.errored}")
print(f"Expired: {batch.request_counts.expired}")

for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        msg = result.result.message
        print(f"{result.custom_id}: {msg.content[0].text[:80]}")
```

## Use Cases

- **Large-scale evaluations** - Process thousands of test cases
- **Content moderation** - Analyze large volumes of user content
- **Data analysis** - Generate insights for large datasets
- **Bulk content generation** - Product descriptions, summaries

## Batch Limits

- **Max requests per batch**: 100,000
- **Processing window**: Up to 24 hours (requests may expire if not processed in time)
- **Results retention**: 29 days (metadata viewable after, but results not downloadable)
- **Supported features**: Most Messages API features including tools, system prompts, images, PDFs
- **300k output**: Opus 4.7, Opus 4.6, Sonnet 4.6 support `max_tokens` up to 300,000 with `output-300k-2026-03-24` beta header
- **Rate limits**: Separate from Messages API; shared across all models (see IN34)

## Gotchas and Quirks

- Validation of `params` is performed asynchronously; test individual requests with Messages API first
- Results may arrive in any order (not necessarily matching request order)
- Batch processing may be slowed during high demand, causing more expirations
- Due to high throughput, batches may slightly exceed workspace spend limits
- Use 1-hour cache TTL with prompt caching for better cache hit rates in batches (5-minute TTL may expire before batch processes)
- Results are available for 29 days; batch metadata remains viewable after that but results cannot be downloaded
- Each request in a batch is processed independently; you can mix different request types
- A single batch with 1,000 items counts as 1,000 batch requests toward queue limits

## Related Endpoints

- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` - Messages API (same params schema)
- `_INFO_ANTAPI-20_PROMPT_CACHING.md [ANTAPI-IN20]` - Caching with batches (use 1h TTL)
- `_INFO_ANTAPI-36_RATE_LIMITS.md [ANTAPI-IN36]` - Batch-specific rate limits

## Sources

- ANTAPI-SC-ANTH-BATCH - https://platform.claude.com/docs/en/build-with-claude/batch-processing - Full batch guide
- ANTAPI-SC-ANTH-BTCHCRT - https://platform.claude.com/docs/en/api/messages/batches/create - Create endpoint
- ANTAPI-SC-ANTH-BTCHLST - https://platform.claude.com/docs/en/api/messages/batches/list - List endpoint

## SDK Verification

All 7 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `resources/messages/batches.py` (lines 47-310): All 6 methods confirmed:
  - `create(requests=Iterable[Request])` -> `MessageBatch`
  - `retrieve(message_batch_id: str)` -> `MessageBatch`
  - `list(after_id?, before_id?, limit?)` -> `SyncPage[MessageBatch]`
  - `cancel(message_batch_id: str)` -> `MessageBatch`
  - `delete(message_batch_id: str)` -> `DeletedMessageBatch`
  - `results(message_batch_id: str)` -> `JSONLDecoder[MessageBatchIndividualResponse]`
- `types/messages/message_batch.py`: `MessageBatch.id`, `.processing_status`, `.request_counts`, `.cancel_initiated_at`, `.results_url`
- `types/messages/message_batch_individual_response.py`: `result.custom_id`, `result.result.type`, `result.result.message`

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references to claude-opus-5
- Added: 300k output token support (output-300k-2026-03-24 beta header)

**[2026-03-20 06:25]**
- Added: SDK verification section (anthropic 0.120.0, all 7 examples valid)

**[2026-03-20 05:00]**
- Added: Batch limits (100K requests, 24h processing, 29-day results retention)
- Added: Queue limit counting clarification

**[2026-03-20 02:50]**
- Initial documentation created with all 6 batch endpoints and Python examples
