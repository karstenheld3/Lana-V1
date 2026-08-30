# Messages API - Create a Message

**Doc ID**: ANTAPI-IN08
**Goal**: Document POST /v1/messages with full request/response schema, content block types, and examples
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL, auth headers

## Summary

The Messages API (`POST /v1/messages`) is the primary endpoint for all Claude interactions. It accepts a structured list of input messages with text, image, PDF, and tool-result content, and generates the next assistant message. The API supports single queries and stateless multi-turn conversations. Messages follow a user/assistant alternation pattern (consecutive same-role turns are auto-combined). System prompts use a separate top-level `system` parameter. The response contains content blocks (text, tool_use, thinking) with usage statistics.

## Key Facts

- **Endpoint**: `POST /v1/messages`
- **Auth**: `x-api-key` header
- **Required Params**: `model`, `max_tokens`, `messages`
- **Message Limit**: 100,000 messages per request
- **Content Types**: text, image, document (PDF), tool_use, tool_result, search_result, container_upload
- **Stop Reasons**: end_turn, max_tokens, stop_sequence, tool_use, pause_turn, refusal
- **Status**: GA

## Request Body (Full Schema)

### Required Parameters

- **model** (`string`) - Model ID (e.g., `"claude-opus-5"`, `"claude-opus-4-20250514"`)
- **max_tokens** (`integer`) - Maximum tokens to generate. Model-specific maximums apply
- **messages** (`array[MessageParam]`) - Input messages array

### Optional Parameters

- **system** (`string | array[ContentBlockParam]`) - System prompt. No "system" role exists in messages
- **temperature** (`number`, default: `1.0`) - Sampling temperature, 0.0-1.0
- **top_p** (`number`) - Nucleus sampling threshold. Use temperature OR top_p, not both
- **top_k** (`integer`) - Sample from top K options only. Advanced use
- **stop_sequences** (`array[string]`) - Custom sequences that trigger stop
- **stream** (`boolean`, default: `false`) - Enable SSE streaming
- **tools** (`array[ToolUnion]`) - Tool definitions for function calling
- **tool_choice** (`ToolChoice`) - How the model selects tools (auto, any, none, specific)
- **metadata** (`object`) - Request metadata
  - **user_id** (`string`) - External user identifier (UUID/hash, no PII)
- **cache_control** (`CacheControlEphemeral`) - Top-level cache control, auto-applies to last cacheable block
  - **ttl** (`string`, default: `"5m"`) - Time-to-live: `"5m"` or `"1h"`
- **thinking** (`ThinkingConfigParam`) - Extended thinking configuration
- **output_config** (`OutputConfig`) - Output format configuration
  - **format** (`JSONOutputFormat`) - Structured output schema
- **inference_geo** (`string`) - Geographic region for inference processing
- **container_id** (`string`) - Container ID for code execution reuse

## Message Structure

Each message has a `role` ("user" or "assistant") and `content` (string or array of content blocks).

### Simple String Content

```json
{"role": "user", "content": "Hello, Claude"}
```

### Content Block Array (equivalent)

```json
{"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}
```

### Multi-turn Conversation

```json
[
  {"role": "user", "content": "Hello there."},
  {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
  {"role": "user", "content": "Can you explain LLMs in plain English?"}
]
```

### Assistant Prefill (constrain response start)

```json
[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("}
]
```

**Note**: Claude Opus 4.6 does not support prefilling. Use structured outputs or `output_config.format` instead.

## Content Block Types (Input)

- **TextBlockParam** - `{"type": "text", "text": "...", "cache_control": {...}, "citations": {...}}`
- **ImageBlockParam** - `{"type": "image", "source": {"type": "base64"|"url", ...}}`
- **DocumentBlockParam** - `{"type": "document", "source": {"type": "base64"|"url"|"content"|"plain_text", ...}}`
- **ToolUseBlockParam** - `{"type": "tool_use", "id": "...", "name": "...", "input": {...}}`
- **ToolResultBlockParam** - `{"type": "tool_result", "tool_use_id": "...", "content": "..."}`
- **SearchResultBlockParam** - `{"type": "search_result", ...}`
- **ContainerUploadBlockParam** - `{"type": "container_upload", ...}` (file upload to code execution container)
- **ThinkingBlockParam** - `{"type": "thinking", "thinking": "..."}` (for multi-turn with thinking)
- **RedactedThinkingBlockParam** - `{"type": "redacted_thinking", ...}`
- **ToolReferenceBlockParam** - `{"type": "tool_reference", ...}` (in tool_result content)

## Tool Definitions

```json
{
  "tools": [
    {
      "name": "get_stock_price",
      "description": "Get the current stock price for a given ticker symbol.",
      "input_schema": {
        "type": "object",
        "properties": {
          "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
          }
        },
        "required": ["ticker"]
      }
    }
  ]
}
```

Tool definition fields:

- **name** (`string`, required) - Tool name, used in tool_use blocks
- **description** (`string`, recommended) - Detailed description for the model
- **input_schema** (`object`, required) - JSON Schema (draft 2020-12) defining input shape
- **cache_control** (`CacheControlEphemeral`, optional) - Cache control for this tool definition
- **hidden** (`boolean`, optional) - If true, not included in system prompt; loaded via tool_reference from tool search
- **eager_streaming** (`boolean`, optional) - Enable incremental input streaming for this tool

## Server-Side Tools

Built-in tools invoked by the server (not the client):

- **WebSearchTool** - Web search
- **WebFetchTool** - Web page fetching
- **CodeExecutionTool** - Sandboxed code execution
- **ToolBash** - Bash shell commands
- **ToolTextEditor** - File viewing/editing
- **MemoryTool** - Persistent memory
- **ToolSearchTool** - Dynamic tool search

## Response Body (Full Schema)

```json
{
  "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Hello! How can I assist you today?"
    }
  ],
  "model": "claude-opus-5",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 12,
    "output_tokens": 8,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0
  }
}
```

### Response Fields

- **id** (`string`) - Unique message ID (format: `msg_...`). Format may change over time
- **type** (`string`) - Always `"message"`
- **role** (`string`) - Always `"assistant"`
- **content** (`array[ContentBlock]`) - Response content blocks
- **model** (`string`) - Model that generated the response
- **stop_reason** (`string | null`) - Why generation stopped:
  - `"end_turn"` - Natural stopping point
  - `"max_tokens"` - Hit max_tokens or model maximum
  - `"stop_sequence"` - Custom stop sequence generated
  - `"tool_use"` - Model invoked one or more tools
  - `"pause_turn"` - Long-running turn paused; send response back as-is to continue
  - `"refusal"` - Streaming classifiers intervened for policy violation
- **stop_sequence** (`string | null`) - Which custom stop sequence was generated, if any
- **usage** (`Usage`) - Token usage for billing and rate limits
  - **input_tokens** (`integer`) - Input tokens consumed
  - **output_tokens** (`integer`) - Output tokens generated
  - **cache_creation_input_tokens** (`integer`) - Tokens written to cache
  - **cache_read_input_tokens** (`integer`) - Tokens read from cache
- **container** (`Container | null`) - Container info for code execution tool
  - **id** (`string`) - Container ID
  - **expires_at** (`string`) - ISO 8601 expiration timestamp

## Content Block Types (Response)

- **TextBlock** - `{"type": "text", "text": "...", "citations": [...]}`
- **ToolUseBlock** - `{"type": "tool_use", "id": "toolu_...", "name": "...", "input": {...}}`
- **ThinkingBlock** - `{"type": "thinking", "thinking": "...", "signature": "..."}`
- **RedactedThinkingBlock** - `{"type": "redacted_thinking", "data": "..."}`
- **ServerToolUseBlock** - `{"type": "server_tool_use", ...}` (server-side tool invocation)
- **WebSearchToolResultBlock** - `{"type": "web_search_tool_result", ...}`
- **WebFetchToolResultBlock** / **WebFetchToolResultErrorBlock**
- **CodeExecutionToolResultBlock** / **CodeExecutionResultBlock**
- **BashCodeExecutionToolResultBlock**
- **TextEditorCodeExecutionToolResultBlock**
- **ToolSearchToolResultBlock**

## Python Examples

### Basic Message

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(message.content[0].text)
```

### With System Prompt

```python
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    system="You are a helpful assistant that responds in haiku format.",
    messages=[{"role": "user", "content": "Tell me about the ocean"}],
)
```

### Multi-turn Conversation

```python
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a high-level programming language."},
        {"role": "user", "content": "What are its main use cases?"},
    ],
)
```

### With Tool Use

```python
import json

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    tools=[
        {
            "name": "get_weather",
            "description": "Get the current weather for a location.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        }
    ],
    messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
)

# Check if model wants to use a tool
for block in message.content:
    if block.type == "tool_use":
        print(f"Tool: {block.name}")
        print(f"Input: {json.dumps(block.input, indent=2)}")
        # Execute tool, then send result back
```

### Tool Result Loop

```python
import anthropic
import json

client = anthropic.Anthropic()

def get_weather(location: str) -> str:
    """Simulated weather lookup."""
    return json.dumps({"temp": "72F", "condition": "sunny", "location": location})

tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City, State"}
            },
            "required": ["location"],
        },
    }
]

messages = [{"role": "user", "content": "What's the weather in NYC and LA?"}]

# Agentic loop
while True:
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )

    if response.stop_reason == "end_turn":
        # Final text response
        for block in response.content:
            if hasattr(block, "text"):
                print(block.text)
        break

    if response.stop_reason == "tool_use":
        # Process tool calls
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = get_weather(block.input["location"])
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )
        messages.append({"role": "user", "content": tool_results})
```

### With Image Input

```python
import anthropic
import base64
import httpx

client = anthropic.Anthropic()

# From URL
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://example.com/image.jpg",
                    },
                },
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
)

# From base64
image_data = base64.standard_b64encode(httpx.get("https://example.com/image.jpg").content).decode("utf-8")
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {"type": "text", "text": "What's in this image?"},
            ],
        }
    ],
)
```

### With PDF Input

```python
import anthropic
import base64

client = anthropic.Anthropic()

# From URL
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "url",
                        "url": "https://example.com/document.pdf",
                    },
                },
                {"type": "text", "text": "Summarize this document."},
            ],
        }
    ],
)

# From base64
with open("document.pdf", "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {"type": "text", "text": "What are the key findings?"},
            ],
        }
    ],
)
```

### With Prompt Caching

```python
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are a helpful assistant with extensive knowledge...",
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        }
    ],
    messages=[{"role": "user", "content": "What is quantum computing?"}],
)
print(f"Cache created: {message.usage.cache_creation_input_tokens}")
print(f"Cache read: {message.usage.cache_read_input_tokens}")
```

## TypeScript Examples

### Basic Message

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const message = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  messages: [{ role: "user", content: "What is the capital of France?" }],
});
// message.content[0].type === "text"
console.log(message.content[0].type === "text" ? message.content[0].text : "");
```

### With System Prompt

```typescript
const message = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  system: "You are a helpful assistant that responds in haiku format.",
  messages: [{ role: "user", content: "Tell me about the ocean" }],
});
```

### Streaming

```typescript
const stream = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello" }],
  stream: true,
});

for await (const event of stream) {
  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
    process.stdout.write(event.delta.text);
  } else if (event.type === "message_delta") {
    console.log(`\nStop reason: ${event.delta.stop_reason}`);
  }
}
```

### Tool Use with Agentic Loop

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();
const tools: Anthropic.Tool[] = [
  {
    name: "get_weather",
    description: "Get current weather for a location.",
    input_schema: {
      type: "object" as const,
      properties: { location: { type: "string", description: "City, State" } },
      required: ["location"],
    },
  },
];

function getWeather(location: string): string {
  return JSON.stringify({ temp: "72F", condition: "sunny", location });
}

const messages: Anthropic.MessageParam[] = [
  { role: "user", content: "What's the weather in NYC and LA?" },
];

for (let i = 0; i < 10; i++) {
  const response = await client.messages.create({
    model: "claude-sonnet-4-5-20250929",
    max_tokens: 1024,
    tools,
    messages,
  });

  if (response.stop_reason === "end_turn") {
    for (const block of response.content) {
      if (block.type === "text") console.log(block.text);
    }
    break;
  }

  messages.push({ role: "assistant", content: response.content });
  const toolResults: Anthropic.ToolResultBlockParam[] = [];
  for (const block of response.content) {
    if (block.type === "tool_use") {
      toolResults.push({
        type: "tool_result",
        tool_use_id: block.id,
        content: getWeather((block.input as { location: string }).location),
      });
    }
  }
  messages.push({ role: "user", content: toolResults });
}
```

### With Prompt Caching

```typescript
const message = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  system: [
    {
      type: "text",
      text: "You are a helpful assistant with extensive knowledge...",
      cache_control: { type: "ephemeral" },
    },
  ],
  messages: [{ role: "user", content: "What is quantum computing?" }],
});
console.log(`Cache created: ${message.usage.cache_creation_input_tokens}`);
console.log(`Cache read: ${message.usage.cache_read_input_tokens}`);
```

## Gotchas and Quirks

- No "system" role in messages; use the top-level `system` parameter
- Consecutive same-role messages are auto-combined, not rejected
- Claude Opus 4.6 does not support assistant message prefilling
- `stop_reason: "pause_turn"` means a long turn was paused; send the response back as-is to continue
- `stop_reason: "refusal"` occurs when streaming classifiers detect policy violations
- In streaming mode, `stop_reason` is null in the `message_start` event
- The `id` format (`msg_...`) may change over time; do not parse it
- Tool definitions should have detailed descriptions for best model performance

## Error Codes

- **400** `invalid_request_error` - Invalid params, unsupported model, prefill on Opus 4.6
- **401** `authentication_error` - Invalid API key
- **413** `request_too_large` - Request exceeds 32 MB
- **429** `rate_limit_error` - Rate or acceleration limit hit

## Related Endpoints

- `_INFO_ANTAPI-09_STREAMING.md [ANTAPI-IN09]` - SSE streaming events
- `_INFO_ANTAPI-10_TOKEN_COUNTING.md [ANTAPI-IN10]` - Pre-request token estimation
- `_INFO_ANTAPI-11_STOP_REASONS.md [ANTAPI-IN11]` - Stop reason handling
- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` - Tool use patterns
- `_INFO_ANTAPI-20_PROMPT_CACHING.md [ANTAPI-IN20]` - Caching details

## Sources

- ANTAPI-SC-ANTH-MSGCRT - https://platform.claude.com/docs/en/api/messages/create - Full endpoint reference
- ANTAPI-SC-ANTH-MSGGUIDE - https://platform.claude.com/docs/en/build-with-claude/working-with-messages - Usage patterns
- ANTAPI-SC-GH-SDKAPI - https://github.com/anthropics/anthropic-sdk-python/blob/main/api.md - SDK types

## SDK Verification

All 8 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `resources/messages/messages.py` (lines 103-130): `create(max_tokens, messages, model, system, tools, tool_choice, temperature, thinking, cache_control, ...)` signature
- `types/cache_control_ephemeral_param.py`: `CacheControlEphemeralParam(type="ephemeral", ttl="5m"|"1h")`
- `types/message.py` (line 16): `Message(id, content, model, stop_reason, stop_sequence, usage, container)`
- `types/tool_use_block.py`: `ToolUseBlock(type, id, name, input)` - verified `.type`, `.name`, `.input`, `.id` attributes

**Notes**:
- Tool result loop pattern (example 5) correctly passes `response.content` (list of Pydantic models) back in messages; SDK `maybe_transform` handles serialization
- Image source types `"url"` and `"base64"` verified in `types/base64_image_source_param.py` and `types/url_image_source_param.py`
- Document source types `"url"` and `"base64"` verified in `types/base64_pdf_source_param.py` and `types/url_pdf_source_param.py`

## Document History

**[2026-07-27]**
- Added: TypeScript Examples section (basic message, system prompt, streaming, tool use agentic loop, prompt caching)

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:15]**
- Added: SDK verification section (anthropic 0.120.0, all 8 examples valid)

**[2026-03-20 02:30]**
- Initial documentation created with full request/response schema, 8 Python examples
