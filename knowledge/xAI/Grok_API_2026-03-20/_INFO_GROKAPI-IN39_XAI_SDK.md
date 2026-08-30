# INFO: xAI SDK (gRPC API)

**Doc ID**: GROKAPI-IN39
**Goal**: Native xAI Python SDK, gRPC vs REST, SDK-specific features, installation
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The xAI SDK (`xai_sdk`) is the native Python SDK that communicates via gRPC (not REST). It provides additional features not available in the OpenAI-compatible REST API: native streaming with `chat.stream()`, structured output with `chat.parse(Model)`, tool helpers (`web_search()`, `x_search()`, `code_execution()`, `collections_search()`), video generation (`client.video.generate()`), and async support via `AsyncClient`. Key limitation: `code_interpreter` and `file_search` tool names are NOT supported in gRPC API - use `code_execution` and `collections_search` instead. The SDK also provides message builders (`user()`, `system()`, `tool()`, `tool_result()`). Install via `pip install xai-sdk`. [VERIFIED] (GROKAPI-SC-XAI-SDK | https://docs.x.ai/developers/xai-sdk)

## Key Facts

- [VERIFIED] Protocol: gRPC (not REST) (GROKAPI-SC-XAI-SDK)
- [VERIFIED] Install: `pip install xai-sdk` (GROKAPI-SC-XAI-SDK)
- [VERIFIED] `code_interpreter` and `file_search` NOT supported in gRPC (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Native streaming: `chat.stream()` yields `(response, chunk)` tuples (GROKAPI-SC-XAI-SDK)
- [VERIFIED] Structured output: `chat.parse(Model)` returns `(response, parsed_object)` (GROKAPI-SC-XAI-SDK)
- [VERIFIED] Async support: `AsyncClient` for async/await patterns (GROKAPI-SC-XAI-SDK)
- [VERIFIED] Video generation: `client.video.generate()` (GROKAPI-SC-XAI-SDK)

## Quick Reference

- **Install**: `pip install xai-sdk`
- **Client**: `from xai_sdk import Client` or `from xai_sdk import AsyncClient`
- **Chat**: `client.chat.create(model=..., tools=[...])`
- **Stream**: `for response, chunk in chat.stream():`
- **Sample**: `response = chat.sample()`
- **Parse**: `response, obj = chat.parse(PydanticModel)`
- **Video**: `client.video.generate(prompt=..., model=...)`
- **Messages**: `user()`, `system()`, `tool()`, `tool_result()`
- **Tools**: `web_search()`, `x_search()`, `code_execution()`, `collections_search()`

## Examples

### Basic Chat

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(model="grok-4.20-beta-latest-non-reasoning")
chat.append(system("You are a helpful assistant."))
chat.append(user("What is 42?"))
response = chat.sample()
print(response.content)
```

### Streaming with Tools

```python
from xai_sdk.tools import web_search, x_search

chat = client.chat.create(
    model="grok-4.20-beta-latest-non-reasoning",
    tools=[web_search(), x_search()],
    include=["verbose_streaming"],
)
chat.append(user("What is the latest AI news?"))

for response, chunk in chat.stream():
    if chunk.content:
        print(chunk.content, end="", flush=True)
```

### Structured Output

```python
from pydantic import BaseModel, Field

class Summary(BaseModel):
    title: str = Field(description="Brief title")
    key_points: list[str] = Field(description="Main points")

response, summary = chat.parse(Summary)
print(summary.title)
```

## Differences: xAI SDK vs OpenAI SDK

- **Protocol**: gRPC vs REST
- **Streaming**: `chat.stream()` yields tuples vs iterator of chunks
- **Parse**: `chat.parse(Model)` vs `client.beta.chat.completions.parse()`
- **Tool names**: `code_execution` only (no `code_interpreter`), `collections_search` only (no `file_search`)
- **Video**: `client.video.generate()` (no OpenAI SDK equivalent)
- **Messages**: Helper functions `user()`, `system()` vs dict literals

## Sources

- GROKAPI-SC-XAI-SDK | https://docs.x.ai/developers/xai-sdk | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 06:10]**
- Initial document created with xAI SDK reference and comparison
