# INFO: Streaming

**Doc ID**: GROKAPI-IN08
**Goal**: SSE streaming, synchronous mode, streaming with tools, event format
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok API supports Server-Sent Events (SSE) streaming for both Chat Completions and Responses APIs. Enable via `stream: true` in the request body. Chat Completions streaming returns `chat.completion.chunk` objects with incremental `delta.content` fields, terminated by `data: [DONE]`. The Responses API streaming returns typed events. Each chunk includes running usage statistics (`prompt_tokens`, `completion_tokens`). Streaming is recommended for real-time UX and for long-running reasoning model requests where timeouts might occur. Tool-using requests also support streaming, with tool call events interleaved with content events. SDKs provide high-level streaming abstractions (e.g., `chat.stream()` in xAI SDK, `client.responses.create(..., stream=True)` in OpenAI SDK). [VERIFIED] (GROKAPI-SC-XAI-STREAMING | https://docs.x.ai/developers/model-capabilities/text/streaming)

## Key Facts

- [VERIFIED] Enable streaming: `stream: true` in request body (GROKAPI-SC-XAI-STREAMING)
- [VERIFIED] Chat Completions: `chat.completion.chunk` objects with `delta.content` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Stream terminator: `data: [DONE]` (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Each chunk includes running usage statistics (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Tool calls stream as separate events (GROKAPI-SC-XAI-TOOLSTREAMING)

## Quick Reference

- **Enable**: `stream: true`
- **Format**: Server-Sent Events (SSE)
- **Terminator**: `data: [DONE]`
- **Chunk object**: `chat.completion.chunk` (Chat Completions) or typed events (Responses)

## SSE Event Format (Chat Completions)

```json
data: {
  "id": "<completion_id>",
  "object": "chat.completion.chunk",
  "created": 1752854522,
  "model": "grok-4.20-beta-latest-non-reasoning",
  "choices": [{"index": 0, "delta": {"content": "Hello", "role": "assistant"}}],
  "usage": {
    "prompt_tokens": 41, "completion_tokens": 1, "total_tokens": 42,
    "prompt_tokens_details": {"text_tokens": 41, "audio_tokens": 0, "image_tokens": 0, "cached_tokens": 0}
  },
  "system_fingerprint": "fp_xxxxxxxxxx"
}

data: [DONE]
```

## Examples

### Streaming (OpenAI SDK - Chat Completions)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

stream = client.chat.completions.create(
    model="grok-4.20-beta-latest-non-reasoning",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about programming."},
    ],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

### Streaming (OpenAI SDK - Responses API)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

stream = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Explain quantum computing briefly."}],
    stream=True,
)

for event in stream:
    if hasattr(event, "delta") and event.delta:
        print(event.delta, end="", flush=True)
print()
```

### Streaming with xAI SDK

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(model="grok-4.20-beta-latest-non-reasoning")
chat.append(system("You are a helpful assistant."))
chat.append(user("Write a haiku about programming."))

for response, chunk in chat.stream():
    if chunk.content:
        print(chunk.content, end="", flush=True)
print()
```

### Streaming with Tools (xAI SDK)

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.20-beta-latest-non-reasoning",
    tools=[web_search()],
    include=["verbose_streaming"],
)

chat.append(user("What is the latest news about AI?"))

is_thinking = True
for response, chunk in chat.stream():
    for tool_call in chunk.tool_calls:
        print(f"\nTool: {tool_call.function.name}({tool_call.function.arguments})")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\n\nResponse:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)
```

## Differences from Other APIs

### vs OpenAI

- **Compatible**: Same SSE format for Chat Completions, same SDK streaming methods
- **Usage in chunks**: xAI includes running usage in each chunk (not all OpenAI endpoints do)

### vs Anthropic

- **Different format**: Anthropic uses typed SSE events (`message_start`, `content_block_delta`, `message_stop`); xAI uses OpenAI-compatible format
- **Tool events**: Different event structure for tool call streaming

### vs Gemini

- **Different format**: Gemini uses `generateContent` with `stream=true` returning JSON chunks; xAI uses OpenAI-compatible SSE

## Sources

- GROKAPI-SC-XAI-STREAMING | https://docs.x.ai/developers/model-capabilities/text/streaming | Accessed: 2026-03-20
- GROKAPI-SC-XAI-TOOLSTREAMING | https://docs.x.ai/developers/tools/streaming | Accessed: 2026-03-20
- GROKAPI-SC-XAI-RESTREF | https://docs.x.ai/llms.txt | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:05]**
- Initial document created with SSE format, streaming examples for all SDKs
