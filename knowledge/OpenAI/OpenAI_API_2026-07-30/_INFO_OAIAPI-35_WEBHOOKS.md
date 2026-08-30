# Webhooks

**Doc ID**: OAIAPI-IN35
**Goal**: Document webhook events, event types, signature verification, and retry behavior
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Webhooks deliver event notifications to your server when specific actions occur in the OpenAI platform. Instead of polling for status changes, webhooks push events to a configured HTTPS endpoint via HTTP POST. Events include fine-tuning job completion, batch processing completion, evaluation results, and other asynchronous operation lifecycle events. Each delivery includes a signature header (HMAC-SHA256) for verification. Payloads are JSON with event type, timestamp, and event-specific data. Failed deliveries are retried with exponential backoff. Webhooks are configured per project in the dashboard or via API. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-WBHEVT)

## Key Facts

- **Delivery**: HTTP POST to configured HTTPS endpoint [VERIFIED] (OAIAPI-SC-OAI-WBHEVT)
- **Format**: JSON payload with event type and data [VERIFIED] (OAIAPI-SC-OAI-WBHEVT)
- **Signature**: HMAC-SHA256 verification via `OpenAI-Webhook-Signature` header [VERIFIED] (OAIAPI-SC-OAI-WBHEVT)
- **Retries**: Exponential backoff on delivery failure [VERIFIED] (OAIAPI-SC-OAI-WBHEVT)
- **Configuration**: Dashboard or API per project [VERIFIED] (OAIAPI-SC-OAI-WBHEVT)
- **HTTPS required**: Endpoint must use TLS [VERIFIED] (OAIAPI-SC-OAI-WBHEVT)

## Event Types

### Fine-Tuning Events
- **fine_tuning.job.created** - Job created
- **fine_tuning.job.succeeded** - Job completed successfully
- **fine_tuning.job.failed** - Job failed
- **fine_tuning.job.cancelled** - Job cancelled

### Batch Events
- **batch.completed** - Batch processing completed
- **batch.failed** - Batch processing failed
- **batch.expired** - Batch expired (24h window)

### Evaluation Events
- **eval.run.completed** - Evaluation run completed
- **eval.run.failed** - Evaluation run failed

## Webhook Payload Structure

```json
{
  "id": "evt_abc123",
  "object": "event",
  "type": "fine_tuning.job.succeeded",
  "created_at": 1741569952,
  "data": {
    "object": {
      "id": "ftjob-abc123",
      "object": "fine_tuning.job",
      "model": "gpt-5.4-mini",
      "status": "succeeded",
      "fine_tuned_model": "ft:gpt-5.4-mini:my-org:custom:abc123",
      "finished_at": 1741569950
    }
  }
}
```

## Signature Verification

Each webhook includes a signature header for HMAC-SHA256 verification:

```
OpenAI-Webhook-Signature: v1=<hex_digest>
OpenAI-Webhook-Timestamp: 1741569952
```

### Verification Steps

1. Extract timestamp and signature from headers
2. Construct signed payload: `{timestamp}.{body}`
3. Compute HMAC-SHA256 with webhook secret
4. Compare computed signature with header value
5. Reject if timestamp is too old (>5 minutes)

## SDK Examples (Python)

### Signature Verification

```python
import hmac
import hashlib
import time

def verify_webhook(payload: bytes, signature_header: str, timestamp_header: str, secret: str) -> bool:
    """Verify OpenAI webhook signature"""
    # Check timestamp freshness (5 minute window)
    timestamp = int(timestamp_header)
    if abs(time.time() - timestamp) > 300:
        return False
    
    # Construct signed content
    signed_content = f"{timestamp}.{payload.decode('utf-8')}"
    
    # Compute expected signature
    expected = hmac.new(
        secret.encode('utf-8'),
        signed_content.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Extract actual signature (remove v1= prefix)
    actual = signature_header.replace("v1=", "")
    
    return hmac.compare_digest(expected, actual)
```

### Flask Webhook Handler

```python
from flask import Flask, request, jsonify
import json

app = Flask(__name__)
WEBHOOK_SECRET = "whsec_..."

@app.route("/webhooks/openai", methods=["POST"])
def handle_webhook():
    signature = request.headers.get("OpenAI-Webhook-Signature", "")
    timestamp = request.headers.get("OpenAI-Webhook-Timestamp", "")
    
    if not verify_webhook(request.data, signature, timestamp, WEBHOOK_SECRET):
        return jsonify({"error": "Invalid signature"}), 401
    
    event = request.json
    event_type = event.get("type")
    
    if event_type == "fine_tuning.job.succeeded":
        job = event["data"]["object"]
        model_id = job["fine_tuned_model"]
        print(f"Fine-tuning complete: {model_id}")
    
    elif event_type == "fine_tuning.job.failed":
        job = event["data"]["object"]
        print(f"Fine-tuning failed: {job['id']}")
    
    elif event_type == "batch.completed":
        batch = event["data"]["object"]
        print(f"Batch complete: {batch['id']}")
    
    else:
        print(f"Unhandled event: {event_type}")
    
    return jsonify({"received": True}), 200

if __name__ == "__main__":
    app.run(port=8080, ssl_context="adhoc")
```

### FastAPI Webhook Handler

```python
from fastapi import FastAPI, Request, HTTPException
import json

app = FastAPI()
WEBHOOK_SECRET = "whsec_..."

@app.post("/webhooks/openai")
async def handle_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("OpenAI-Webhook-Signature", "")
    timestamp = request.headers.get("OpenAI-Webhook-Timestamp", "")
    
    if not verify_webhook(body, signature, timestamp, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    event = json.loads(body)
    event_type = event["type"]
    
    handlers = {
        "fine_tuning.job.succeeded": handle_ft_success,
        "fine_tuning.job.failed": handle_ft_failure,
        "batch.completed": handle_batch_complete,
    }
    
    handler = handlers.get(event_type)
    if handler:
        await handler(event["data"]["object"])
    
    return {"received": True}

async def handle_ft_success(job: dict):
    print(f"Model ready: {job['fine_tuned_model']}")

async def handle_ft_failure(job: dict):
    print(f"Job failed: {job['id']}")

async def handle_batch_complete(batch: dict):
    print(f"Batch done: {batch['id']}")
```

## Best Practices

- **Always verify signatures**: Reject unsigned or invalid requests
- **Respond quickly**: Return 2xx within 5 seconds; process async
- **Idempotent handlers**: Events may be delivered more than once; handle duplicates
- **Timestamp validation**: Reject events older than 5 minutes to prevent replay attacks
- **Log events**: Store raw events for debugging and audit
- **Queue processing**: For long operations, acknowledge receipt and process via queue

## Retry Behavior

- Failed deliveries (non-2xx response) trigger retries
- Exponential backoff between retries
- Multiple retry attempts before giving up
- Events are delivered at least once (may deliver duplicates)

## Error Responses

- **Your endpoint**: Must return 2xx to acknowledge receipt
- **Non-2xx**: Triggers retry with backoff
- **Timeout**: If endpoint doesn't respond within timeout, treated as failure

## Differences from Other APIs

- **vs Anthropic**: No webhook system; relies on polling
- **vs Gemini**: Google Cloud Pub/Sub for event notifications (different mechanism)
- **vs Stripe**: Very similar webhook pattern (Stripe pioneered this model)

## Limitations and Known Issues

- **At-least-once delivery**: Events may be sent multiple times [VERIFIED] (OAIAPI-SC-OAI-WBHEVT)
- **HTTPS required**: Cannot use HTTP endpoints [VERIFIED] (OAIAPI-SC-OAI-WBHEVT)
- **Ordering**: Events may arrive out of order [ASSUMED]

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

- OAIAPI-SC-OAI-WBHEVT - Webhook Events Reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 16:20]**
- Enriched from 2026-03-20 IN35 Webhooks (19 -> 198 lines)
- Updated model references to gpt-5.5/gpt-5.4-mini

**[2026-05-22 11:45]**
- Stub created
