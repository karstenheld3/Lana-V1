# INFO: Migration Guide

**Doc ID**: GROKAPI-IN12
**Goal**: Chat Completions vs Responses API comparison, parameter mapping, migration path
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok API offers two text generation interfaces: the legacy Chat Completions API (`POST /v1/chat/completions`) and the recommended Responses API (`POST /v1/responses`). The Responses API adds server-side storage (30 days), multi-turn via `previous_response_id`, encrypted reasoning content, and a typed output structure. Key parameter changes: `messages` becomes `input`, `max_tokens` becomes `max_output_tokens`, response content moves from `choices[0].message.content` to `output[0].content[0].text`. For model migration from Grok 3 to Grok 4: Grok 4 is always-reasoning (no non-reasoning mode), does not support presencePenalty/frequencyPenalty/stop/reasoning_effort params. Grok 4.20 does not support logprobs. Migration is straightforward for OpenAI SDK users - just change `client.chat.completions.create()` to `client.responses.create()` and update parameter names. [VERIFIED] (GROKAPI-SC-XAI-COMPARISON | https://docs.x.ai/developers/model-capabilities/text/comparison)

## Key Facts

- [VERIFIED] Parameter mapping: `messages` -> `input`, `max_tokens` -> `max_output_tokens` (GROKAPI-SC-XAI-COMPARISON)
- [VERIFIED] Response structure: `choices[0].message.content` -> `output[0].content[0].text` (GROKAPI-SC-XAI-COMPARISON)
- [VERIFIED] New in Responses API: `previous_response_id`, `store`, `include` params (GROKAPI-SC-XAI-COMPARISON)
- [VERIFIED] Grok 4 migration: no presencePenalty, frequencyPenalty, stop, reasoning_effort (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Grok 4.20 migration: logprobs field silently ignored (GROKAPI-SC-XAI-MODELS)

## Parameter Mapping

- **`messages`** -> **`input`**: Array of message objects (same format)
- **`max_tokens`** -> **`max_output_tokens`**: Maximum completion tokens
- **(new)** **`previous_response_id`**: Continue stored conversation
- **(new)** **`store`**: Control server-side storage (default: true)
- **(new)** **`include`**: Request additional data like `reasoning.encrypted_content`

## Response Structure Comparison

### Chat Completions Response

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you?"
    },
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18}
}
```

### Responses API Response

```json
{
  "id": "resp_123",
  "object": "response",
  "output": [{
    "type": "message",
    "role": "assistant",
    "content": [{
      "type": "output_text",
      "text": "Hello! How can I help you?"
    }],
    "status": "completed"
  }],
  "store": true,
  "previous_response_id": null,
  "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18}
}
```

## Migration Examples

### From Chat Completions to Responses API (OpenAI SDK)

```python
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0),
)

# BEFORE (Chat Completions)
# response = client.chat.completions.create(
#     model="grok-4.20-beta-latest-non-reasoning",
#     messages=[
#         {"role": "user", "content": "Hello"},
#     ],
#     max_tokens=100,
# )
# print(response.choices[0].message.content)

# AFTER (Responses API)
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[
        {"role": "user", "content": "Hello"},
    ],
    max_output_tokens=100,
)
print(response.output_text)
```

### Multi-Turn Migration

```python
# BEFORE: Resend full history each time
# r1 = client.chat.completions.create(
#     model="grok-4", messages=[{"role": "user", "content": "What is 2+2?"}]
# )
# r2 = client.chat.completions.create(
#     model="grok-4",
#     messages=[
#         {"role": "user", "content": "What is 2+2?"},
#         {"role": "assistant", "content": r1.choices[0].message.content},
#         {"role": "user", "content": "Now multiply by 10"},
#     ]
# )

# AFTER: Use previous_response_id
r1 = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What is 2+2?"}],
)

r2 = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    previous_response_id=r1.id,
    input=[{"role": "user", "content": "Now multiply by 10"}],
)
print(r2.output_text)
```

### Model Migration: Grok 3 to Grok 4

```python
# BEFORE (Grok 3 - these params are valid)
# response = client.responses.create(
#     model="grok-3",
#     input=[{"role": "user", "content": "Hello"}],
#     presence_penalty=0.5,    # NOT supported on Grok 4
#     frequency_penalty=0.5,   # NOT supported on Grok 4
#     stop=["\n\n"],           # NOT supported on Grok 4
# )

# AFTER (Grok 4 - remove unsupported params)
response = client.responses.create(
    model="grok-4",
    input=[{"role": "user", "content": "Hello"}],
    # No presence_penalty, frequency_penalty, stop
    # Grok 4 always reasons - no way to disable
)
```

## Differences from Other APIs

### vs OpenAI Migration

- **Same SDK**: Both use `client.responses.create()` - xAI migration mirrors OpenAI's own migration path
- **Same parameter mapping**: `messages` -> `input`, `max_tokens` -> `max_output_tokens`
- **xAI-specific**: `store` defaults to true (OpenAI may differ), encrypted reasoning content

### vs Anthropic

- **No migration needed**: Anthropic uses a single Messages API, no legacy/new split
- **Stateless**: Anthropic Messages API is always stateless (no previous_response_id equivalent)

## Sources

- GROKAPI-SC-XAI-COMPARISON | https://docs.x.ai/developers/model-capabilities/text/comparison | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MIGRATION | https://docs.x.ai/developers/advanced-api-usage/migration | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 03:45]**
- Initial document created with parameter mapping, response comparison, and migration examples
