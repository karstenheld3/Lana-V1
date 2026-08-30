# INFO: Gemini API OpenAI Compatibility

**Doc ID**: GEMAPI-IN06
**Goal**: Document the OpenAI-compatible endpoint, migration from OpenAI SDK, feature mapping, and limitations
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini API provides an OpenAI-compatible endpoint at `/v1beta/openai/` that allows existing OpenAI SDK clients to use Gemini models with minimal code changes. The endpoint supports `POST /v1beta/openai/chat/completions` with the standard OpenAI request format (messages array, model field, temperature, etc.). Migration requires only changing the base URL and API key configuration. The compatibility layer maps OpenAI parameters to Gemini equivalents: `reasoning_effort` maps to Gemini's `thinkingLevel`/`thinkingBudget`, streaming works via SSE, and function calling follows the OpenAI tool format. However, Gemini-specific features like built-in tools (Google Search, Code Execution, URL Context), safety settings, context caching, and the Live API are not accessible through the compatibility endpoint. This feature is unique to Gemini - Anthropic has no OpenAI-compatible endpoint.

## Key Facts

- [VERIFIED] Compat endpoint: `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions` (GEMAPI-SC-GOOG-OAICOM)
- [VERIFIED] Works with OpenAI Python/JS SDK via base_url override (GEMAPI-SC-GOOG-OAICOM)
- [VERIFIED] reasoning_effort maps to Gemini thinking configuration (GEMAPI-SC-GOOG-OAICOM)
- [VERIFIED] Not all Gemini features available via compat endpoint (GEMAPI-SC-GOOG-OAICOM)

## Use Cases

- **Migration**: Move existing OpenAI applications to Gemini with minimal code changes
- **Multi-provider**: Use same client code to target OpenAI or Gemini
- **Testing**: Compare model outputs using identical request format
- **Library compatibility**: Use frameworks built for OpenAI (LangChain, etc.) with Gemini

## Quick Reference

**Base URL**: `https://generativelanguage.googleapis.com/v1beta/openai/`
**Endpoint**: `POST /v1beta/openai/chat/completions`
**Auth**: `Authorization: Bearer YOUR_GEMINI_API_KEY` (OpenAI format)

## Migration from OpenAI SDK

### Python SDK

```python
from openai import OpenAI
import os

# Only change: base_url and api_key
client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    temperature=0.7,
    max_tokens=1024
)

print(response.choices[0].message.content)
```

### Streaming

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

stream = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "Write a short story."}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Function Calling

```python
from openai import OpenAI
import json
import os

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "What is the weather in Paris?"}],
    tools=tools
)

if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    print(f"Function: {tool_call.function.name}")
    print(f"Args: {tool_call.function.arguments}")
```

### Reasoning Effort Mapping

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# reasoning_effort maps to Gemini thinking levels
response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "Solve this math problem..."}],
    reasoning_effort="high"  # Maps to Gemini thinkingLevel
)
print(response.choices[0].message.content)
```

## Parameter Mapping

### Supported Parameters

- **model** -> Model name (use Gemini model identifiers)
- **messages** -> Mapped to Gemini `contents` array
- **temperature** -> Direct mapping
- **max_tokens** -> Maps to `maxOutputTokens`
- **stream** -> Uses `streamGenerateContent` endpoint
- **tools** -> Maps to Gemini function declarations
- **tool_choice** -> Maps to `toolConfig.functionCallingConfig`
- **reasoning_effort** -> Maps to Gemini `thinkingLevel`/`thinkingBudget`
- **stop** -> Maps to `stopSequences`
- **top_p** -> Direct mapping
- **n** -> Maps to `candidateCount`

### NOT Supported via Compat Endpoint

- Built-in tools (Google Search, Code Execution, URL Context, Google Maps)
- Safety settings configuration
- Context caching (cachedContent)
- Live API (WebSocket)
- Gemini-specific Part types (fileData, inlineData)
- systemInstruction as Content object (mapped from system role message)
- Structured output via responseSchema (use OpenAI's response_format instead)
- Image/video generation (Nano Banana, Imagen, Veo)

## REST API

### Request (OpenAI Format)

```
POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
```

**Headers:**
- `Authorization`: `Bearer YOUR_GEMINI_API_KEY`
- `Content-Type`: `application/json`

**Request Body:**

```json
{
  "model": "gemini-2.5-flash",
  "messages": [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello"}
  ],
  "temperature": 0.7,
  "max_tokens": 1024,
  "stream": false
}
```

### Response (OpenAI Format)

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1711000000,
  "model": "gemini-2.5-flash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 8,
    "total_tokens": 18
  }
}
```

## cURL Examples

### Example: OpenAI-Compatible Request

```bash
curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
  -H "Authorization: Bearer $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-flash",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

## Comparison with Other APIs

### vs OpenAI (Native)

- **Endpoint path**: Gemini compat: `/v1beta/openai/chat/completions` | OpenAI: `/v1/chat/completions`
- **Auth format**: Both use `Authorization: Bearer` in compat mode
- **Feature gap**: Gemini compat lacks Gemini-specific features; native Gemini API is more capable
- **Response format**: Identical to OpenAI format

### vs Anthropic

- **OpenAI compat**: Gemini: Yes | Anthropic: No
- This is a **UNIQUE Gemini feature** - Anthropic has no OpenAI-compatible endpoint

## Error Responses

- Errors follow OpenAI error format when using compat endpoint
- **400**: Invalid parameters
- **401**: Invalid API key (in Bearer format)
- **429**: Rate limited (same project-level limits apply)

## Rate Limiting / Throttling

Same project-level rate limits as native Gemini API. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Not all Gemini features accessible via compat endpoint (GEMAPI-SC-GOOG-OAICOM)
- [COMMUNITY] Endpoint URL changed from `/v1beta/chat/completions` to `/v1beta/openai/chat/completions` (GEMAPI-SC-GOOG-OAICOM)
- [COMMUNITY] OpenAI Responses API format not supported (GEMAPI-SC-GOOG-OAICOM)

## Gotchas and Quirks

- The compat endpoint uses `Authorization: Bearer` (not `x-goog-api-key`) - the only Gemini endpoint that does
- Model names are Gemini identifiers (`gemini-2.5-flash`), not OpenAI names
- The `system` role in messages is mapped to Gemini's `systemInstruction` internally
- The response uses `assistant` role (OpenAI convention), not `model` (Gemini convention)
- OpenAI's newer Responses API is not supported - only Chat Completions

## Sources

- GEMAPI-SC-GOOG-OAICOM: https://ai.google.dev/gemini-api/docs/openai [VERIFIED]

## Document History

**[2026-03-20 03:10]**
- Initial document created with migration guide, parameter mapping, and examples
