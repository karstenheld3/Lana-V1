# INFO: Chat Completions API (Legacy)

**Doc ID**: GROKAPI-IN07
**Goal**: Legacy Chat Completions API reference, messages format, conversations, image understanding
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Chat Completions API (`POST /v1/chat/completions`) is the legacy text generation interface, directly compatible with the OpenAI Chat Completions format. It accepts a `messages` array with system/user/assistant roles and returns responses in `choices[0].message.content`. Unlike the Responses API, it is stateless - the full conversation history must be sent with each request. It supports image understanding via multimodal content arrays with `image_url` parts (base64 or URL). The response includes a `system_fingerprint` field for reproducibility tracking. For new projects, the Responses API (`POST /v1/responses`) is recommended instead. The Chat Completions API does NOT support multi-agent models. [VERIFIED] (GROKAPI-SC-XAI-CHATCOMP | https://docs.x.ai/developers/model-capabilities/text/chat-completions)

## Key Facts

- [VERIFIED] Endpoint: `POST /v1/chat/completions` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Stateless: full conversation history must be resent each request (GROKAPI-SC-XAI-CHATCOMP)
- [VERIFIED] OpenAI-compatible request/response format (GROKAPI-SC-XAI-CHATCOMP)
- [VERIFIED] Image understanding via content array with `image_url` type (GROKAPI-SC-XAI-CHATCOMP)
- [VERIFIED] Only grok-3-mini returns `reasoning_content` in Chat Completions (GROKAPI-SC-XAI-REASONING)
- [VERIFIED] Multi-agent models NOT supported in Chat Completions (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Response includes `system_fingerprint` field (GROKAPI-SC-XAI-RESTREF)

## Quick Reference

- **Endpoint**: `POST /v1/chat/completions`
- **Input field**: `messages` (array)
- **Output**: `choices[0].message.content`
- **Max tokens**: `max_tokens` (integer)
- **Streaming**: `stream: true` for SSE

## Endpoint Reference

### Request Body

- **`model`** (string, required): Model ID
- **`messages`** (array, required): Array of message objects
  - **`role`** (string): `system`, `user`, `assistant`
  - **`content`** (string or array): Text or multimodal content parts
- **`max_tokens`** (integer, optional): Maximum completion tokens
- **`temperature`** (number, optional): 0-2
- **`top_p`** (number, optional): Nucleus sampling
- **`stream`** (boolean, optional): Enable SSE streaming
- **`tools`** (array, optional): Tool definitions
- **`tool_choice`** (string, optional): Tool selection strategy
- **`presence_penalty`** (number, optional): -2 to 2 (not supported on Grok 4)
- **`frequency_penalty`** (number, optional): -2 to 2 (not supported on Grok 4)
- **`stop`** (string/array, optional): Stop sequences (not supported on Grok 4)
- **`response_format`** (object, optional): For structured outputs

### Response Body

```json
{
  "id": "a3d1008e-4544-40d4-d075-11527e794e4a",
  "object": "chat.completion",
  "created": 1752854522,
  "model": "grok-4-0709",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Response text here.",
      "refusal": null
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 32,
    "completion_tokens": 9,
    "total_tokens": 135,
    "prompt_tokens_details": {
      "text_tokens": 32, "audio_tokens": 0,
      "image_tokens": 0, "cached_tokens": 6
    },
    "completion_tokens_details": {
      "reasoning_tokens": 94, "audio_tokens": 0,
      "accepted_prediction_tokens": 0, "rejected_prediction_tokens": 0
    },
    "num_sources_used": 0
  },
  "system_fingerprint": "fp_3a7881249c"
}
```

## Examples

### Basic Chat Completion

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.chat.completions.create(
    model="grok-4.20-beta-latest-non-reasoning",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain Python decorators in 3 sentences."},
    ],
    max_tokens=200,
)

print(response.choices[0].message.content)
```

### Multi-Turn Conversation

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"},
]

r1 = client.chat.completions.create(
    model="grok-4.20-beta-latest-non-reasoning",
    messages=messages,
)

# Must resend full history
messages.append({"role": "assistant", "content": r1.choices[0].message.content})
messages.append({"role": "user", "content": "What is its population?"})

r2 = client.chat.completions.create(
    model="grok-4.20-beta-latest-non-reasoning",
    messages=messages,
)
print(r2.choices[0].message.content)
```

### Image Understanding

```python
import base64

with open("image.jpg", "rb") as f:
    b64_image = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.completions.create(
    model="grok-2-vision-1212",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{b64_image}",
                "detail": "high"
            }},
            {"type": "text", "text": "Describe what's in this image."},
        ],
    }],
)
print(response.choices[0].message.content)
```

## Differences from Other APIs

### vs OpenAI Chat Completions

- **Fully compatible**: Same request/response format, same SDK methods
- **Additional fields**: `num_sources_used` in usage (for tool-using requests)
- **Model restrictions**: Grok 4 rejects presencePenalty, frequencyPenalty, stop
- **No logprobs**: Grok 4.20 silently ignores logprobs

### vs Grok Responses API

- **Stateless**: Must resend full history (no `previous_response_id`)
- **No storage**: Responses not stored server-side
- **Different output**: `choices[0].message.content` vs `output[0].content[0].text`
- **No multi-agent**: Multi-agent models only work with Responses API
- **Parameter names**: `max_tokens` vs `max_output_tokens`

## Sources

- GROKAPI-SC-XAI-CHATCOMP | https://docs.x.ai/developers/model-capabilities/text/chat-completions | Accessed: 2026-03-20
- GROKAPI-SC-XAI-RESTREF | https://docs.x.ai/llms.txt | Accessed: 2026-03-20

## Document History

**[2026-03-20 03:50]**
- Initial document created with full Chat Completions API reference
