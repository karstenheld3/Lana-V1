# Priority Processing

**Doc ID**: OAIAPI-IN84
**Goal**: Document priority processing tiers and request prioritization
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Priority processing provides differentiated request handling. Three processing tiers: Standard (default, normal queuing), Flex (lower priority, reduced cost), and Batch (bulk async, 50% discount, 24h window). Priority processing is distinct from Flex - it represents the standard synchronous path with normal rate limits and latency guarantees. Compare: Standard = real-time, normal cost; Flex = reduced priority, lower cost; Batch = async JSONL, 50% discount. [VERIFIED] (OAIAPI-SC-OAI-GPRIO)

## Key Facts

- **Three tiers**: Standard, Flex, Batch [VERIFIED] (OAIAPI-SC-OAI-GPRIO)
- **Standard**: Default synchronous path, normal pricing, lowest latency
- **Flex**: Lower cost, higher latency tolerance, queue-based
- **Batch**: 50% discount, async JSONL, 24h completion window

## Processing Tiers

### Standard (Default)

- **Latency**: Lowest, real-time responses
- **Cost**: Full price
- **Rate limits**: Normal RPM/TPM per tier
- **Use case**: Interactive applications, chatbots, real-time features
- **How to use**: Default behavior, no additional configuration needed

### Flex Processing

- **Latency**: Higher, requests queued during peak load
- **Cost**: Reduced (discount varies by model)
- **Rate limits**: Separate from standard limits
- **Use case**: Background tasks, non-interactive workloads, cost optimization
- **How to use**: Set processing tier in request

### Batch Processing

- **Latency**: Up to 24 hours
- **Cost**: 50% discount
- **Rate limits**: No RPM/TPM limits
- **Use case**: Large-scale data processing, evaluations, content generation
- **How to use**: Submit JSONL via Batch API (see IN32)

## Choosing a Tier

- **Need real-time response?** → Standard
- **Can tolerate seconds of delay for cost savings?** → Flex
- **Can wait hours for 50% savings?** → Batch

## SDK Examples (Python)

### Standard (Default)

```python
from openai import OpenAI

client = OpenAI()

# Standard processing - default, no extra config
response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Flex Processing

```python
from openai import OpenAI

client = OpenAI()

# Flex processing - lower cost, higher latency tolerance
response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Summarize this document..."}],
    service_tier="flex",
)
print(response.choices[0].message.content)
```

## Gotchas and Quirks

- **Flex availability**: Not all models support Flex processing [VERIFIED]
- **Flex latency variable**: During low-demand periods, Flex may be as fast as Standard [COMMUNITY]
- **Batch vs Flex**: Batch requires JSONL file upload workflow; Flex is a single request parameter [VERIFIED]
- **service_tier param**: Use `service_tier="flex"` in Chat Completions [VERIFIED]

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

- OAIAPI-SC-OAI-GPRIO - Priority processing guide (https://developers.openai.com/api/docs/guides/priority-processing)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Full tier comparison, SDK examples, choosing guide, gotchas

**[2026-05-22 13:00]**
- Initial documentation (gap found during /improve review)
