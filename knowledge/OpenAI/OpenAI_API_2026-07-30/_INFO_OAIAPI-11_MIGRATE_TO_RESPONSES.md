# Migration Guide: Chat Completions to Responses API

**Doc ID**: OAIAPI-IN11
**Goal**: Document migration from Chat Completions API to Responses API with parameter mapping and code examples
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API details

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Responses API is the recommended primary interface, replacing Chat Completions for new applications. Key migration changes: `messages` becomes `input`, `response_format` becomes `text.format`, streaming uses different event names (response.output_text.delta vs chat.completion.chunk), and new features include built-in tools (web_search, file_search, code_interpreter, computer_use, hosted_shell, apply_patch), conversation state management, background mode, and compaction. Most Chat Completions parameters have direct equivalents. Breaking changes: structured outputs schema nesting different, no `n` parameter, tool_choice syntax modified. Migration benefits: built-in tools, conversation persistence, background processing, unified API. Both APIs maintained for compatibility but new features only in Responses API. [VERIFIED] (OAIAPI-SC-OAI-GMIGRR)

## Key Facts

- **Recommended**: Responses API is primary interface going forward [VERIFIED]
- **Parameter mapping**: Most parameters have direct equivalents [VERIFIED]
- **Breaking changes**: Structured outputs, n parameter, streaming events [VERIFIED]
- **New features**: Built-in tools, conversations, background mode, compaction [VERIFIED]
- **Compatibility**: Chat Completions still supported for existing apps [VERIFIED]

## Parameter Mapping

### Request Parameters

- `messages` -> `input` (array of input items)
- `model` -> `model` (same format)
- `temperature` -> `temperature` (same, 0-2)
- `top_p` -> `top_p` (same, 0-1)
- `n` -> **REMOVED** (generate multiple responses not supported)
- `stream` -> `stream` (same boolean)
- `stop` -> `stop` (same array of strings)
- `max_tokens` -> `text.max_output_tokens` (nested in text object)
- `presence_penalty` -> `presence_penalty` (same, -2 to 2)
- `frequency_penalty` -> `frequency_penalty` (same, -2 to 2)
- `logit_bias` -> **NOT YET** (not in Responses API)
- `user` -> `user` (same, end-user ID)
- `response_format` -> `text.format` (different structure)
- `tools` -> `tools` (same structure, plus built-ins)
- `tool_choice` -> `tool_choice` (slightly modified syntax)

### Response Parameters

- `choices[0].message` -> `output[0]` (different structure)
- `choices[0].finish_reason` -> `status` (different values)
- `usage` -> `usage` (same structure)
- `id` -> `id` (same format)

## Code Migration Examples

### Basic Request

**Before (Chat Completions):**
```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "What is AI?"}
    ],
    temperature=0.7,
    max_tokens=500
)
print(response.choices[0].message.content)
```

**After (Responses API):**
```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "What is AI?"}
    ],
    temperature=0.7,
    text={"max_output_tokens": 500}
)
print(response.output[0].content[0].text)
```

### Function Calling

**Before:**
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"]
            }
        }
    }],
    tool_choice="auto"
)
```

**After:**
```python
response = client.responses.create(
    model="gpt-5.6-sol",
    input=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"]
            }
        }
    }],
    tool_choice="auto"
)
```

### Structured Outputs

**Before:**
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Extract: John is 30"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "person",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
                "required": ["name", "age"]
            }
        }
    }
)
```

**After:**
```python
response = client.responses.create(
    model="gpt-5.6-sol",
    input=[{"role": "user", "content": "Extract: John is 30"}],
    text={
        "format": {
            "type": "json_schema",
            "json_schema": {
                "name": "person",
                "schema": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
                    "required": ["name", "age"]
                },
                "strict": True
            }
        }
    }
)
```

### Streaming

**Before:**
```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Tell a story"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

**After (SDK preferred pattern):**
```python
with client.responses.stream(
    model="gpt-5.6-sol",
    input=[{"role": "user", "content": "Tell a story"}]
) as stream:
    for event in stream:
        if event.type == "response.text_delta":
            print(event.delta, end="", flush=True)
```

## New Capabilities in Responses API

### Built-in Tools

```python
response = client.responses.create(
    model="gpt-5.6-sol",
    input=[{"role": "user", "content": "Latest AI news"}],
    tools=[{"type": "web_search"}]
)
```

### Conversation State (SDK verified)

```python
conversation = client.conversations.create()

response1 = client.responses.create(
    model="gpt-5.6-sol",
    conversation={"id": conversation.id},
    input=[{"role": "user", "content": "My name is Alice"}]
)

response2 = client.responses.create(
    model="gpt-5.6-sol",
    conversation={"id": conversation.id},
    input=[{"role": "user", "content": "What's my name?"}]
)
```

### Background Mode

```python
response = client.responses.create(
    model="gpt-5.6-sol",
    input=[{"role": "user", "content": "Research AI trends"}],
    reasoning={"mode": "pro"},
    background=True,
)

while response.status == "in_progress":
    response = client.responses.retrieve(response.id)
```

## Breaking Changes

### 1. No `n` Parameter
Cannot generate multiple responses in one call. **Workaround:** Make multiple API calls.

### 2. Structured Outputs Schema
Different nesting: Chat uses `response_format.json_schema.schema`, Responses uses `text.format.json_schema.schema`.

### 3. Streaming Event Names
Chat uses `chat.completion.chunk`, Responses uses `response.output_text.delta`.

### 4. Response Access
Chat uses `choices[0].message.content`, Responses uses `output[0].content[0].text`.

## Migration Strategy

1. **Identify dependencies**: Check Chat Completions-specific code
2. **Update imports**: No changes needed (same OpenAI client)
3. **Map parameters**: Use parameter mapping above
4. **Test thoroughly**: Verify output format changes
5. **Monitor costs**: GPT-5.5 is $5/$30 vs GPT-5.4 $2.50/$15

### Parallel Running

```python
def generate_response(prompt, use_new_api=False):
    if use_new_api:
        return client.responses.create(
            model="gpt-5.6-sol",
            input=[{"role": "user", "content": prompt}]
        )
    else:
        return client.chat.completions.create(
            model="gpt-5.4",
            messages=[{"role": "user", "content": prompt}]
        )
```

## Differences from Other APIs

- **vs Anthropic Messages**: Anthropic has no Chat Completions equivalent, only Messages (similar to Responses)
- **vs Gemini**: Gemini uses generateContent (similar pattern to Responses)

## Limitations and Known Issues

- **No logit_bias**: Not yet supported in Responses API [VERIFIED]
- **No n parameter**: Cannot generate multiple responses in one call [VERIFIED]
- **Model availability**: Some legacy models only in Chat Completions [ASSUMED]

## Gotchas and Quirks

- **Input vs messages**: Most common migration error [VERIFIED]
- **Nested text settings**: max_tokens nested in text object [VERIFIED]
- **Output array access**: Always array even for single response [VERIFIED]
- **conversation= param**: SDK uses `conversation={"id": "..."}` not `conversation_id="..."` [VERIFIED]

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

- OAIAPI-SC-OAI-GMIGRR - Migration guide from Chat Completions to Responses
- OAIAPI-SC-OAI-RESCRT - POST Create a response
- OAIAPI-SC-OAI-CHTCRT - POST Create chat completion

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 14:25]**
- Enriched: Full parameter mapping, code examples, breaking changes, migration strategy from 2026-03-20
- Updated: Model refs to gpt-5.5, pricing to current
- Updated: Streaming event names to current (response.output_text.delta)
- Added: SDK verified patterns

**[2026-05-22 11:40]**
- Stub created
