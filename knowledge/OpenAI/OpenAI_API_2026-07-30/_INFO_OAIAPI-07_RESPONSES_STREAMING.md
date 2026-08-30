# Responses Streaming

**Doc ID**: OAIAPI-IN07
**Goal**: Document SSE streaming events for Responses API
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API overview

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Responses API supports Server-Sent Events (SSE) streaming via `stream: true`. Events include `response.created`, `response.output_item.added`, `response.output_text.delta`, `response.output_text.done`, `response.completed`, and tool-specific events. GPT-5.5 streaming works identically to GPT-5.4. Streaming enables real-time UI updates, progressive content display, and early response cancellation. Client must handle partial state accumulation - delta events contain incremental changes, not full content. Compatible with all Responses API features including tools, structured outputs, and reasoning. [VERIFIED] (OAIAPI-SC-OAI-RESSTR)

## Key Facts

- **Protocol**: Server-Sent Events (SSE) [VERIFIED] (OAIAPI-SC-OAI-RESSTR)
- **Enable**: Set `stream: true` in request [VERIFIED] (OAIAPI-SC-OAI-RESCRT)
- **Event types**: response.delta, response.done, response.failed, tool events [VERIFIED] (OAIAPI-SC-OAI-RESSTR)
- **Format**: `event: type\ndata: {json}\n\n` [VERIFIED] (OAIAPI-SC-OAI-RESSTR)
- **Accumulation**: Client accumulates deltas for full response [VERIFIED] (OAIAPI-SC-OAI-RESSTR)

## Use Cases

- **Real-time chat**: Display response as it generates
- **Progress indication**: Show typing indicators during generation
- **Early cancellation**: Cancel long responses before completion
- **Streaming UI**: Update interface progressively

## Event Types

### response.delta

Incremental content update:
```json
{
  "event": "response.delta",
  "data": {
    "id": "resp_abc123",
    "delta": {
      "output": [
        {
          "index": 0,
          "content": [
            {
              "type": "text",
              "text": "Hello"
            }
          ]
        }
      ]
    }
  }
}
```

**Fields:**
- **index**: Output item index
- **content**: Array of content deltas
- **text**: Incremental text chunk

### response.done

Stream completion marker:
```json
{
  "event": "response.done",
  "data": {
    "id": "resp_abc123",
    "status": "completed",
    "usage": {
      "input_tokens": 10,
      "output_tokens": 50,
      "total_tokens": 60
    }
  }
}
```

**Indicates:** Response fully generated, no more deltas

### response.failed

Error during streaming:
```json
{
  "event": "response.failed",
  "data": {
    "id": "resp_abc123",
    "status": "failed",
    "error": {
      "type": "api_error",
      "message": "Internal server error"
    }
  }
}
```

### tool_calls.delta

Tool call incremental update:
```json
{
  "event": "tool_calls.delta",
  "data": {
    "index": 0,
    "id": "call_abc",
    "type": "function",
    "function": {
      "name": "get_weather",
      "arguments": "{\"location\":"
    }
  }
}
```

### tool_calls.done

Tool call completion:
```json
{
  "event": "tool_calls.done",
  "data": {
    "index": 0,
    "id": "call_abc",
    "type": "function",
    "function": {
      "name": "get_weather",
      "arguments": "{\"location\":\"Paris\"}"
    }
  }
}
```

## Event Processing

### State Accumulation

Client must accumulate deltas:
1. Initialize empty response state
2. Process each delta event, merging into state
3. Display accumulated content progressively
4. Finalize on response.done

### Event Order

Events arrive in sequence:
1. Multiple response.delta events
2. Optional tool_calls.delta/done events
3. Final response.done or response.failed event

## SDK Examples (Python)

### Basic Streaming (Preferred SDK Pattern)

```python
from openai import OpenAI

client = OpenAI()

with client.responses.stream(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "Write a short poem"}
    ]
) as stream:
    for event in stream:
        if event.type == "response.text_delta":
            print(event.delta, end="", flush=True)

# Alternative: get final text after streaming
with client.responses.stream(
    model="gpt-5.6-sol",
    input=[{"role": "user", "content": "Write a short poem"}]
) as stream:
    response = stream.get_final_response()
    print(response.output[0].content[0].text)
```

### Basic Streaming (create with stream=True)

```python
from openai import OpenAI

client = OpenAI()

stream = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "Write a short poem"}
    ],
    stream=True
)

for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
    elif event.type == "response.completed":
        print("\n")
```

### Streaming with Error Handling

```python
from openai import OpenAI

client = OpenAI()

try:
    stream = client.responses.create(
        model="gpt-5.6-sol",
        input=[{"role": "user", "content": "Explain AI"}],
        stream=True
    )
    
    full_text = ""
    for event in stream:
        if event.type == "response.output_text.delta":
            full_text += event.delta
            print(event.delta, end="", flush=True)
        
        elif event.type == "response.completed":
            print(f"\n\nTokens used: {event.response.usage.total_tokens}")
        
        elif event.type == "response.failed":
            print(f"\nError: {event.response.error.message}")
            break

except Exception as e:
    print(f"Stream error: {e}")
```

### Streaming with Tools

```python
from openai import OpenAI
import json

client = OpenAI()

stream = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "What's the weather in Paris?"}
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            }
        }
    ],
    stream=True
)

for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
    elif event.type == "response.function_call_arguments.delta":
        print(event.delta, end="")
    elif event.type == "response.completed":
        print(f"\nCompleted: {event.response.status}")
```

### Production Streaming Handler

```python
from openai import OpenAI
from typing import Iterator
import logging

logger = logging.getLogger(__name__)

def stream_response(prompt: str) -> Iterator[str]:
    client = OpenAI()
    
    try:
        with client.responses.stream(
            model="gpt-5.6-sol",
            input=[{"role": "user", "content": prompt}]
        ) as stream:
            for event in stream:
                if event.type == "response.text_delta":
                    yield event.delta
                elif event.type == "response.completed":
                    logger.info(f"Stream completed: {event.response.usage.total_tokens} tokens")
                    return
                elif event.type == "response.failed":
                    logger.error(f"Stream failed: {event.response.error.message}")
                    raise Exception(f"Stream error: {event.response.error.message}")
    
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        raise

# Usage
for chunk in stream_response("Explain quantum computing"):
    print(chunk, end="", flush=True)
print()
```

## Error Responses

- **Stream interruption**: Network issues cause incomplete streams
- **Server errors**: response.failed event with error details
- **Timeout**: Long pauses may indicate issues

## Rate Limiting / Throttling

- **Streaming counts toward limits**: Each stream uses RPM/TPM quota
- **Token counting**: All generated tokens count, even if stream cancelled early

## Differences from Other APIs

- **vs Chat Completions streaming**: Similar SSE format, different event names (response.output_text.delta vs chat.completion.chunk)
- **vs Anthropic streaming**: Anthropic uses content_block_delta, OpenAI uses response.output_text.delta
- **vs Gemini streaming**: Gemini uses different event structure

## Limitations and Known Issues

- **No pause/resume**: Cannot pause stream and resume later [VERIFIED] (OAIAPI-SC-OAI-RESSTR)
- **Buffering delays**: Some proxies/CDNs may buffer SSE events [ASSUMED]
- **Connection timeout**: Long streams may timeout on slow connections [ASSUMED]

## Gotchas and Quirks

- **Delta accumulation required**: Deltas are incremental, not complete [VERIFIED] (OAIAPI-SC-OAI-RESSTR)
- **Event field optional**: Not all events have delta field [VERIFIED] (OAIAPI-SC-OAI-RESSTR)
- **Flush required**: Must flush stdout for real-time display [VERIFIED]
- **responses.stream() preferred**: SDK provides `responses.stream()` context manager as preferred pattern over `create(stream=True)` [VERIFIED]

## TypeScript Examples

### Streaming Response

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const stream = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Explain streaming in 3 sentences.",
  stream: true,
});

for await (const event of stream) {
  if (event.type === "response.output_text.delta") {
    process.stdout.write(event.delta);
  }
}
console.log();
```

## Sources

- OAIAPI-SC-OAI-RESSTR - Streaming events reference
- OAIAPI-SC-OAI-RESCRT - POST Create a response

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 14:05]**
- Enriched: Full event types, SDK examples, gotchas merged from 2026-03-20 baseline
- Updated: Model refs gpt-5.4 -> gpt-5.5
- Updated: Event names to current API (response.output_text.delta, response.completed)
- Added: responses.stream() preferred pattern note

**[2026-05-22 11:35]**
- Stub created with summary and basic SDK example
