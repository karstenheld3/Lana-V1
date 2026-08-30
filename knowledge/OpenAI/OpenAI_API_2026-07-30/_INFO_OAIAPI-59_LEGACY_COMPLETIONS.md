# Completions API (Legacy)

**Doc ID**: OAIAPI-IN59
**Goal**: Document the legacy Completions API - single-prompt text completion (deprecated)
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The legacy Completions API (`POST /v1/completions`) generates text completions for a single prompt string. Unlike Chat Completions which uses a messages array with roles, it takes a flat `prompt` string. Supported only by `gpt-3.5-turbo-instruct` and older models. **Deprecated** in favor of Chat Completions and the Responses API. Returns `text_completion` object with choices array. Supports streaming, temperature, top_p, max_tokens, stop sequences, n, logprobs, echo, suffix, best_of. The `suffix` parameter enables fill-in-the-middle completion. [VERIFIED] (OAIAPI-SC-OAI-CMPLT)

## Key Facts

- **Status**: DEPRECATED - use Chat Completions or Responses API instead [VERIFIED] (OAIAPI-SC-OAI-CMPLT)
- **Endpoint**: POST /v1/completions [VERIFIED] (OAIAPI-SC-OAI-CMPLT)
- **Models**: gpt-3.5-turbo-instruct only (GPT-4+ not supported) [VERIFIED] (OAIAPI-SC-OAI-CMPLT)
- **Input**: Single `prompt` string (not messages array) [VERIFIED] (OAIAPI-SC-OAI-CMPLT)
- **Unique features**: `suffix` (fill-in-middle), `echo`, `best_of` [VERIFIED] (OAIAPI-SC-OAI-CMPLT)

## Quick Reference

```
POST /v1/completions

{
  "model": "gpt-3.5-turbo-instruct",
  "prompt": "Write a tagline for an ice cream shop: ",
  "max_tokens": 50,
  "temperature": 0.7
}
```

## Response Object

```json
{
  "id": "cmpl-abc123",
  "object": "text_completion",
  "created": 1699061776,
  "model": "gpt-3.5-turbo-instruct",
  "choices": [
    {
      "text": "Every scoop tells a story!",
      "index": 0,
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 7,
    "total_tokens": 17
  }
}
```

## SDK Examples (Python)

### Basic Usage

```python
from openai import OpenAI

client = OpenAI()

response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="Translate to French: Hello, how are you?",
    max_tokens=50
)

print(response.choices[0].text)
```

## Migration

Replace with Chat Completions:

```python
# Before (Completions)
response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="Summarize: The cat sat on the mat."
)

# After (Chat Completions)
response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Summarize: The cat sat on the mat."}]
)
```

## Differences from Other APIs

- **vs Chat Completions**: Completions uses flat prompt; Chat uses messages array with roles
- **vs Anthropic**: Anthropic never had a flat-prompt completions endpoint
- **vs Gemini**: Gemini generateContent always uses structured content format

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

- OAIAPI-SC-OAI-CMPLT - Legacy Completions API Reference
- OAIAPI-SC-OAI-LGCOMP - Legacy Completions Reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:40]**
- Enriched from 2026-03-20 IN59 (19 -> 100 lines)
- Updated migration model ref to gpt-5.5

**[2026-05-22 11:50]**
- Stub created
