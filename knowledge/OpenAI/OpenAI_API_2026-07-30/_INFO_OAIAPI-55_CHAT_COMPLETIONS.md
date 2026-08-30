# Chat Completions

**Doc ID**: OAIAPI-IN55
**Goal**: Document Chat Completions API - create, retrieve, update, delete, list; messages format
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Chat Completions API (`POST /v1/chat/completions`) is the stable text generation interface. While the Responses API is now recommended, Chat Completions remains fully supported. GPT-5.6 (Sol/Terra/Luna) works with Chat Completions including full reasoning controls (`effort`, `mode: "pro"`, `context`). Inline moderation available via `moderation` parameter (2026-06). Supports streaming, function calling, structured outputs via `response_format`, stored completions (retrieve/update/delete/list), and message history listing. [VERIFIED] (OAIAPI-SC-OAI-CHTCRT, OAIAPI-SC-OAI-GCHLOG)

## Key Facts

- **Endpoint**: `POST /v1/chat/completions` [VERIFIED] (OAIAPI-SC-OAI-CHTCRT)
- **Message roles**: developer, system, user, assistant, tool [VERIFIED]
- **Content modalities**: Text, images, audio [VERIFIED]
- **Structured outputs**: JSON schema via `response_format` [VERIFIED]
- **Tool calling**: Function tools with JSON arguments [VERIFIED]
- **Streaming**: SSE via `stream: true` [VERIFIED]
- **Recommendation**: Use Responses API for new projects [VERIFIED]

## REST API

### Create a Chat Completion

**Endpoint**: `POST /v1/chat/completions`

```json
{
  "model": "gpt-5.5",
  "messages": [
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum entanglement."}
  ],
  "reasoning_effort": "medium",
  "max_completion_tokens": 4096,
  "temperature": 0.7,
  "stream": false,
  "store": true
}
```

### Request Parameters

**Required:**
- **model** (string) - Model ID (e.g., "gpt-5.5", "gpt-5.4-mini")
- **messages** (array) - Array of message objects with `role` and `content`

**Common Optional:**
- **temperature** (number) - 0-2, default 1. Lower = more focused
- **max_completion_tokens** (integer) - Maximum tokens in output
- **reasoning_effort** (string) - `none`/`low`/`medium`/`high`/`xhigh`
- **stream** (boolean) - Enable SSE streaming
- **store** (boolean) - Store for later retrieval
- **stop** (string/array) - Stop sequences
- **seed** (integer) - Deterministic sampling seed
- **n** (integer) - Number of completions to generate (default 1)

**Tools:**
- **tools** (array) - Tool definitions (function type)
- **tool_choice** (string/object) - "auto", "none", "required", or specific function
- **parallel_tool_calls** (boolean) - Allow multiple simultaneous tool calls (default true)

**Output Format:**
- **response_format** (object) - `{"type": "text"}`, `{"type": "json_object"}`, or `{"type": "json_schema", "json_schema": {...}}`

**Advanced:**
- **frequency_penalty** (number) - -2.0 to 2.0
- **presence_penalty** (number) - -2.0 to 2.0
- **logprobs** (boolean) - Return log probabilities
- **top_logprobs** (integer) - 0-20
- **service_tier** (string) - "auto" or "flex"
- **prediction** (object) - Predicted output for faster completions

### Response Object

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1741569952,
  "model": "gpt-5.5",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum entanglement is...",
        "refusal": null,
        "annotations": []
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 50,
    "total_tokens": 69,
    "prompt_tokens_details": {"cached_tokens": 0, "audio_tokens": 0},
    "completion_tokens_details": {"reasoning_tokens": 0, "audio_tokens": 0, "accepted_prediction_tokens": 0, "rejected_prediction_tokens": 0}
  },
  "service_tier": "default"
}
```

### Finish Reasons

- **stop** - Natural completion or stop sequence hit
- **length** - max_completion_tokens reached
- **tool_calls** - Model wants to call tool(s)
- **content_filter** - Content filtered by safety system

### Retrieve / Update / Delete / List

- `GET /v1/chat/completions/{completion_id}`
- `POST /v1/chat/completions/{completion_id}`
- `DELETE /v1/chat/completions/{completion_id}`
- `GET /v1/chat/completions`

### List Messages

- `GET /v1/chat/completions/{completion_id}/messages`

## SDK Examples (Python)

### Basic Completion

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {"role": "system", "content": "You are a senior software engineer."},
        {"role": "user", "content": "Review this code for security issues."}
    ],
    reasoning_effort="high",
)
print(response.choices[0].message.content)
```

### Streaming

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Write a haiku about programming."}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

### With Function Calling

```python
from openai import OpenAI
import json

client = OpenAI()

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "What's the weather in Berlin?"}],
    tools=tools,
)

if response.choices[0].message.tool_calls:
    call = response.choices[0].message.tool_calls[0]
    args = json.loads(call.function.arguments)
    print(f"Function: {call.function.name}, Args: {args}")
```

### Structured Outputs

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {"role": "user", "content": "Extract: John Smith, age 30, works at Acme Corp"}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "person",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "company": {"type": "string"}
                },
                "required": ["name", "age", "company"],
                "additionalProperties": False
            }
        }
    }
)

person = json.loads(response.choices[0].message.content)
print(person)  # {"name": "John Smith", "age": 30, "company": "Acme Corp"}
```

### Tool Calling with Follow-up

```python
from openai import OpenAI
import json

client = OpenAI()

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"]
        }
    }
}]

messages = [{"role": "user", "content": "What's the weather in Tokyo?"}]
response = client.chat.completions.create(model="gpt-5.6-sol", messages=messages, tools=tools)

message = response.choices[0].message
if message.tool_calls:
    call = message.tool_calls[0]
    result = {"temperature": 22, "condition": "cloudy"}

    # Continue conversation with tool result
    messages.append(message)
    messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})

    followup = client.chat.completions.create(model="gpt-5.6-sol", messages=messages, tools=tools)
    print(followup.choices[0].message.content)
```

### Production Multi-Turn Chat

```python
from openai import OpenAI

client = OpenAI()

def chat_loop(system_prompt: str, model: str = "gpt-5.5"):
    messages = [{"role": "developer", "content": system_prompt}]

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("quit", "exit"):
            break

        messages.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_completion_tokens=1000,
        )

        choice = response.choices[0]
        if choice.finish_reason == "content_filter":
            print("Assistant: [Content filtered]")
            continue
        if choice.message.refusal:
            print(f"Assistant: [Refused: {choice.message.refusal}]")
            continue

        messages.append({"role": "assistant", "content": choice.message.content})
        print(f"Assistant: {choice.message.content}")
        cached = response.usage.prompt_tokens_details.cached_tokens
        print(f"  [{response.usage.total_tokens} tokens, {cached} cached]")
```

## Error Responses

- **400 Bad Request** - Invalid parameters, malformed messages
- **401 Unauthorized** - Invalid API key
- **404 Not Found** - Model not found
- **422 Unprocessable Entity** - Invalid schema for structured outputs
- **429 Too Many Requests** - Rate limit exceeded
- **500 Internal Server Error** - Server error

## Differences from Other APIs

- **vs Responses API**: Chat Completions uses messages array; Responses uses simpler input. Responses supports built-in tools (file_search, web_search). Chat Completions is more widely adopted in existing codebases
- **vs Anthropic Messages**: Similar shape. Anthropic uses `system` param (not in messages), `max_tokens` is required
- **vs Gemini generateContent**: Different structure - uses `contents` array with `parts`

## Gotchas and Quirks

- **Responses API preferred**: OpenAI recommends Responses API for new projects [VERIFIED]
- **reasoning_effort**: Parameter name differs from Responses API (`reasoning.effort` vs `reasoning_effort`) [VERIFIED]
- **GPT-5.5 default medium**: Reasoning defaults to medium in Chat Completions too [VERIFIED]
- **max_tokens deprecated**: Use `max_completion_tokens` instead [VERIFIED]
- **Tool call JSON**: Model may generate invalid JSON in tool call arguments; always validate [VERIFIED]
- **Cached tokens**: `prompt_tokens_details.cached_tokens` shows automatic prompt caching savings [VERIFIED]
- **Store default**: New accounts default to `store=true`; existing accounts may differ [VERIFIED]
- **developer vs system**: GPT-5.x models use `developer` role; older models use `system` [VERIFIED]

## TypeScript Examples

### Basic Chat Completion

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const completion = await client.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Hello!" },
  ],
});

console.log(completion.choices[0].message.content);
```

### Streaming

```typescript
const stream = await client.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [{ role: "user", content: "Count to 5." }],
  stream: true,
});

for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content;
  if (content) process.stdout.write(content);
}
```

## Sources

- OAIAPI-SC-OAI-CHTCRT - POST Create a chat completion
- OAIAPI-SC-OAI-CHTLST - List/Retrieve/Update/Delete
- OAIAPI-SC-OAI-CHTSTR - Streaming events
- OAIAPI-SC-OAI-CHTMSG - List messages

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Changed: Model references from GPT-5.5 to GPT-5.6 (Sol/Terra/Luna)
- Added: Full reasoning controls (effort, mode, context)
- Added: Inline moderation parameter reference
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 11:10]**
- Updated from 2026-03-20: model refs to GPT-5.5, reasoning_effort note
