# INFO: Responses API

**Doc ID**: GROKAPI-IN06
**Goal**: Complete Responses API reference - create, chain, retrieve, delete responses with encrypted thinking
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references
- `_INFO_GROKAPI-IN01_INTRODUCTION.md [GROKAPI-IN01]` for base URL and auth

## Summary

The Responses API (`POST /v1/responses`) is the recommended text generation interface for the Grok API, replacing the legacy Chat Completions API. It stores request/response history on xAI servers for 30 days by default (configurable via `store: false`), enabling multi-turn conversations by passing `previous_response_id` without repeating the full context. The API supports the `developer` role as an alias for `system`, with a single system/developer message as the first message. Encrypted thinking content can be returned for reasoning models via `include: ["reasoning.encrypted_content"]`, which must be passed back in subsequent requests for accurate multi-turn reasoning. Responses can be retrieved by ID (`GET /v1/responses/{response_id}`) and deleted (`DELETE /v1/responses/{response_id}`). The `instructions` parameter is currently not supported. Compatible with OpenAI Python/JS SDK via `client.responses.create()`. [VERIFIED] (GROKAPI-SC-XAI-GENTEXT | https://docs.x.ai/developers/model-capabilities/text/generate-text)

## Key Facts

- [VERIFIED] Endpoint: `POST /v1/responses` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Responses stored 30 days by default; disable with `store: false` (GROKAPI-SC-XAI-GENTEXT)
- [VERIFIED] Multi-turn via `previous_response_id` - no need to repeat context (GROKAPI-SC-XAI-GENTEXT)
- [VERIFIED] `developer` role supported as alias for `system` (GROKAPI-SC-XAI-GENTEXT)
- [VERIFIED] Single system/developer message only, must be first message (GROKAPI-SC-XAI-GENTEXT)
- [VERIFIED] `instructions` parameter NOT supported (returns error) (GROKAPI-SC-XAI-GENTEXT)
- [VERIFIED] Encrypted thinking: `include: ["reasoning.encrypted_content"]` for reasoning models (GROKAPI-SC-XAI-GENTEXT)
- [VERIFIED] Retrieve: `GET /v1/responses/{response_id}` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Delete: `DELETE /v1/responses/{response_id}` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Recommended timeout: 3600s for reasoning models (GROKAPI-SC-XAI-GENTEXT)

## Quick Reference

- **Create**: `POST /v1/responses`
- **Retrieve**: `GET /v1/responses/{response_id}`
- **Delete**: `DELETE /v1/responses/{response_id}`
- **Input field**: `input` (array of messages)
- **Model field**: `model` (string)
- **Store control**: `store` (boolean, default: true)
- **Chaining**: `previous_response_id` (string)
- **Reasoning**: `include: ["reasoning.encrypted_content"]`

## Endpoint Reference

**Endpoint**: `POST /v1/responses`
**Authentication**: `Authorization: Bearer <API_KEY>`

### Request Body

- **`model`** (string, required): Model ID (e.g., `grok-4.20-beta-latest-non-reasoning`)
- **`input`** (array, required): Array of message objects
  - **`role`** (string): `system`, `developer`, `user`, or `assistant`
  - **`content`** (string or array): Text string or array of content parts
- **`previous_response_id`** (string, optional): ID of previous response for multi-turn
- **`store`** (boolean, optional): Store response on server. Default: `true`
- **`include`** (array, optional): Additional data to include. Values: `["reasoning.encrypted_content"]`
- **`tools`** (array, optional): Tool definitions (server-side and client-side)
- **`tool_choice`** (string, optional): Tool selection strategy. Default: `"auto"`
- **`parallel_tool_calls`** (boolean, optional): Allow parallel tool execution. Default: `true`
- **`temperature`** (number, optional): Sampling temperature (0-2)
- **`top_p`** (number, optional): Nucleus sampling parameter
- **`max_output_tokens`** (integer, optional): Maximum completion tokens
- **`text`** (object, optional): Text format configuration
  - **`format.type`** (string): `"text"` or `"json_schema"`
- **`stream`** (boolean, optional): Enable SSE streaming. Default: `false`

### Response Body

```json
{
  "created_at": 1754475266,
  "id": "ad5663da-63e6-86c6-e0be-ff15effa8357",
  "max_output_tokens": null,
  "model": "grok-4-0709",
  "object": "response",
  "output": [
    {
      "content": [
        {
          "type": "output_text",
          "text": "Response text here.",
          "logprobs": null,
          "annotations": []
        }
      ],
      "id": "msg_ad5663da-...",
      "role": "assistant",
      "type": "message",
      "status": "completed"
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": null,
  "temperature": null,
  "text": {"format": {"type": "text"}},
  "tool_choice": "auto",
  "tools": [],
  "top_p": null,
  "usage": {
    "prompt_tokens": 32,
    "completion_tokens": 9,
    "total_tokens": 151,
    "prompt_tokens_details": {
      "text_tokens": 32,
      "audio_tokens": 0,
      "image_tokens": 0,
      "cached_tokens": 8
    },
    "completion_tokens_details": {
      "reasoning_tokens": 110,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    },
    "num_sources_used": 0
  },
  "user": null,
  "incomplete_details": null,
  "status": "completed",
  "store": true
}
```

## Examples

### Basic Text Generation (xAI SDK)

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(api_key=os.getenv("XAI_API_KEY"), timeout=3600)

chat = client.chat.create(model="grok-4.20-beta-latest-non-reasoning")
chat.append(system("You are a helpful coding assistant."))
chat.append(user("Write a Python function to calculate fibonacci numbers."))
response = chat.sample()

print(response.content)
print(f"Response ID: {response.id}")
```

### Basic Text Generation (OpenAI SDK)

```python
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0),
)

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function to calculate fibonacci numbers."},
    ],
)

print(response.output_text)
print(f"Response ID: {response.id}")
```

### Multi-Turn Conversation (Chaining)

```python
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0),
)

# First message
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
)
print(f"Turn 1: {response.output_text}")

# Continue conversation using previous_response_id
response2 = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    previous_response_id=response.id,
    input=[
        {"role": "user", "content": "What is its population?"},
    ],
)
print(f"Turn 2: {response2.output_text}")
```

### Disable Storage

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Sensitive query"}],
    store=False,  # Response not stored on server
)
```

### Encrypted Thinking Content (Reasoning Models)

```python
# First request with encrypted thinking
response = client.responses.create(
    model="grok-4.20-reasoning",
    input=[
        {"role": "system", "content": "You are a math expert."},
        {"role": "user", "content": "Prove that sqrt(2) is irrational."},
    ],
    include=["reasoning.encrypted_content"],
)

print(response.output_text)

# Continue with encrypted thinking preserved
response2 = client.responses.create(
    model="grok-4.20-reasoning",
    previous_response_id=response.id,
    input=[
        {"role": "user", "content": "Can you generalize this proof?"},
    ],
    include=["reasoning.encrypted_content"],
)
```

### Retrieve Previous Response

```python
stored = client.responses.retrieve("ad5663da-63e6-86c6-e0be-ff15effa8357")
print(stored.output_text)
```

### Delete Response

```python
client.responses.delete("ad5663da-63e6-86c6-e0be-ff15effa8357")
```

## Differences from Other APIs

### vs OpenAI Responses API

- **Compatible**: Same `client.responses.create()` SDK method
- **Storage**: xAI stores 30 days by default; OpenAI also stores but with different retention
- **`instructions` param**: NOT supported on xAI (returns error); supported on OpenAI
- **Encrypted thinking**: xAI uses encrypted content for reasoning continuity; OpenAI exposes thinking blocks
- **`developer` role**: Supported as system alias on both
- **Timeout**: xAI recommends 3600s for reasoning models (longer than typical OpenAI)

### vs Anthropic Messages API

- **Endpoint**: `POST /v1/responses` vs `POST /v1/messages`
- **Input field**: `input` vs `messages`
- **System prompt**: In `input` array as system role vs separate `system` parameter
- **Multi-turn**: `previous_response_id` (stateful) vs full message replay (stateless)
- **Storage**: xAI stores server-side; Anthropic is stateless
- **Thinking**: xAI encrypts reasoning; Anthropic exposes thinking blocks in `thinking` field

### vs OpenAI Chat Completions (Legacy)

- **Input field**: `input` vs `messages`
- **Response structure**: `output` array with typed content vs `choices` array
- **Multi-turn**: `previous_response_id` vs full message replay
- **Storage**: Stored by default vs stateless

## Limitations and Known Issues

- [VERIFIED] `instructions` parameter not supported - returns error if specified (GROKAPI-SC-XAI-GENTEXT)
- [VERIFIED] Single system/developer message only, must be first (GROKAPI-SC-XAI-GENTEXT)
- [VERIFIED] Vercel AI SDK cannot retrieve or delete previous responses - use OpenAI SDK (GROKAPI-SC-XAI-GENTEXT)
- [VERIFIED] Reasoning models require longer timeouts (3600s recommended) (GROKAPI-SC-XAI-GENTEXT)

## Sources

- GROKAPI-SC-XAI-GENTEXT | https://docs.x.ai/developers/model-capabilities/text/generate-text | Accessed: 2026-03-20
- GROKAPI-SC-XAI-RESTREF | https://docs.x.ai/llms.txt | Accessed: 2026-03-20

## Document History

**[2026-03-20 03:30]**
- Initial document created with full Responses API reference, examples, and comparisons
