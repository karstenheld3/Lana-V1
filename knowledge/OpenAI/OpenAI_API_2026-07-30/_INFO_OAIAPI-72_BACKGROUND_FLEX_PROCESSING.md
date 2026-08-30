# Background and Flex Processing

**Doc ID**: OAIAPI-IN72
**Goal**: Document Flex Processing and Background mode - discounted/async API processing options
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Two complementary processing modes for non-interactive workloads. **Flex Processing**: 50% discount via `service_tier: "flex"`, uses standard sync/streaming API flow with variable latency. **Background mode**: run responses asynchronously with `store: true`, poll for completion or use webhooks. Comparison: Batch API = bulk JSONL file upload, Background = single async response, Flex = lower-priority sync. Both compatible with prompt caching for additional savings. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-GFLEX, OAIAPI-SC-OAI-GBKGND)

## Key Facts

- **Flex discount**: 50% on token pricing [VERIFIED] (OAIAPI-SC-OAI-GFLEX)
- **Flex parameter**: `service_tier: "flex"` [VERIFIED] (OAIAPI-SC-OAI-GFLEX)
- **APIs**: Responses API and Chat Completions API [VERIFIED] (OAIAPI-SC-OAI-GFLEX)
- **Caching compatible**: Stacks with prompt caching discount [VERIFIED] (OAIAPI-SC-OAI-GFLEX)
- **Background mode**: Async via `store: true`, poll or webhook [VERIFIED] (OAIAPI-SC-OAI-GBKGND)
- **Background retention**: Response data retained ~10 minutes [VERIFIED] (OAIAPI-SC-OAI-GBKGND)

## Use Cases

- **Data pipelines**: Bulk processing of documents, logs, or records
- **Content generation**: Generating large volumes of content offline
- **Analysis**: Batch analysis of datasets
- **Deep research**: Long-running research tasks via background mode
- **Testing**: Running large test suites against model outputs
- **Migration**: Processing historical data through new models

## Flex vs Background vs Batch Comparison

- **Flex Processing**
  - Same API call flow (sync/stream)
  - 50% discount
  - Variable latency
  - Compatible with streaming
  - No file upload/polling
  - Stacks with prompt caching

- **Background Mode**
  - Single async response
  - Poll or webhook for completion
  - Good for long-running tasks (deep research, complex reasoning)
  - Response retained ~10 minutes
  - No streaming during processing

- **Batch API**
  - File upload -> poll -> download results
  - 50% discount
  - Up to 24h completion window
  - No streaming
  - Requires JSONL file management
  - Separate rate limit pool

## SDK Examples (Python)

### Basic Flex Processing

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {"role": "developer", "content": "Summarize the following text concisely."},
        {"role": "user", "content": "Long text to summarize..."}
    ],
    service_tier="flex"
)

print(f"Service tier: {response.service_tier}")  # "flex"
print(response.choices[0].message.content)
```

### Bulk Processing with Flex

```python
from openai import AsyncOpenAI
import asyncio

async def process_batch_flex(items: list, system_prompt: str, model: str = "gpt-5.5"):
    """Process multiple items with flex pricing"""
    client = AsyncOpenAI()
    results = []
    
    sem = asyncio.Semaphore(10)
    
    async def process_one(item):
        async with sem:
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "developer", "content": system_prompt},
                        {"role": "user", "content": item}
                    ],
                    service_tier="flex",
                    max_completion_tokens=500
                )
                return {
                    "input": item[:50],
                    "output": response.choices[0].message.content,
                    "tokens": response.usage.total_tokens,
                    "tier": response.service_tier
                }
            except Exception as e:
                return {"input": item[:50], "error": str(e)}
    
    tasks = [process_one(item) for item in items]
    results = await asyncio.gather(*tasks)
    
    success = sum(1 for r in results if "output" in r)
    total_tokens = sum(r.get("tokens", 0) for r in results)
    
    print(f"Processed: {success}/{len(items)}")
    print(f"Total tokens: {total_tokens}")
    
    return results

items = ["Summarize: " + doc for doc in documents]
results = asyncio.run(process_batch_flex(
    items,
    system_prompt="Create a one-paragraph summary."
))
```

### Flex with Responses API

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Analyze this dataset and provide key insights.",
    service_tier="flex"
)

print(response.output_text)
```

## Error Responses

- **400 Bad Request** - Invalid service_tier value
- **429 Too Many Requests** - Flex capacity exhausted

## Differences from Other APIs

- **vs Anthropic**: No equivalent flex/discount tier
- **vs Gemini**: No equivalent discount processing tier
- **vs Batch API**: Same discount but different UX - Flex uses standard API calls

## Limitations and Known Issues

- **No SLA guarantee**: Lower priority than default tier, no completion time guarantee [VERIFIED] (OAIAPI-SC-OAI-GFLEX)
- **Unpredictable latency**: Response time varies with capacity [VERIFIED] (OAIAPI-SC-OAI-GFLEX)
- **Not for real-time**: Not suitable for user-facing interactive applications [VERIFIED] (OAIAPI-SC-OAI-GFLEX)
- **Background retention**: Data retained only ~10 minutes after completion [VERIFIED] (OAIAPI-SC-OAI-GBKGND)

## TypeScript Examples

### Client Setup and Basic Usage

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  organization: process.env.OPENAI_ORG_ID,
});

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Hello!",
});
console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-GFLEX - Flex Processing Guide
- OAIAPI-SC-OAI-GBKGND - Background Mode Guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 18:10]**
- Enriched from 2026-03-20 IN72 (19 -> 170 lines)
- Added background mode details, updated model refs to gpt-5.5

**[2026-05-22 11:50]**
- Stub created
