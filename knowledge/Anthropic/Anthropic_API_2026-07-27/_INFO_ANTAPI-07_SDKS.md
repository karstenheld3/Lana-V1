# Client SDKs

**Doc ID**: ANTAPI-IN07
**Goal**: Document official SDK installation, configuration, and usage patterns with focus on Python
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL and general overview
- `_INFO_ANTAPI-04_AUTHENTICATION.md [ANTAPI-IN04]` for API key configuration

## Summary

Anthropic provides official client SDKs in 8 languages: Python, TypeScript, Java, Go, Ruby, C#, PHP, and a CLI (`ant`). A Swift SDK is available in beta for Apple Foundation Models integration. All SDKs handle authentication headers, request formatting, error handling, retries, streaming, and timeouts automatically. The Python SDK (`anthropic` package, v0.120.0 as of Jul 24, 2026) provides sync and async clients with Pydantic models. SDKs support direct API, Claude Platform on AWS, Amazon Bedrock (Messages API and legacy InvokeModel), Google Vertex AI, and Microsoft Foundry platforms.

## Key Facts

- **Python Package**: `anthropic` (pip install anthropic)
- **Env Variable**: `ANTHROPIC_API_KEY`
- **Sync Client**: `anthropic.Anthropic()`
- **Async Client**: `anthropic.AsyncAnthropic()`
- **Beta Namespace**: `client.beta.messages.create()`
- **GitHub**: https://github.com/anthropics/anthropic-sdk-python

## Available SDKs

- **CLI** (`ant`) - Shell scripting, typed flags, response transforms
- **Python** - Sync and async clients, Pydantic models
- **TypeScript** - Node.js, Deno, Bun, and browser support
- **Java** - Builder pattern, CompletableFuture async
- **Go** - Context-based cancellation, functional options
- **Ruby** - Sorbet types, streaming helpers
- **C#** - .NET Standard 2.0+, IChatClient integration
- **PHP** - Value objects, builder pattern
- **Swift** (beta) - Apple Foundation Models integration

## Python SDK

### Installation

```bash
pip install anthropic

# Platform-specific extras
pip install "anthropic[aws]"       # Claude Platform on AWS
pip install "anthropic[bedrock]"   # Amazon Bedrock
pip install "anthropic[vertex]"    # Vertex AI
pip install "anthropic[aiohttp]"   # Improved async performance
```

### Basic Usage

```python
import anthropic

# Reads ANTHROPIC_API_KEY from environment
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
print(message.content[0].text)
```

### Async Usage

```python
import anthropic
import asyncio

async def main():
    client = anthropic.AsyncAnthropic()

    message = await client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello, Claude"}],
    )
    print(message.content[0].text)

asyncio.run(main())
```

### Streaming

```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a story"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Streaming with Final Message

```python
import anthropic

client = anthropic.Anthropic()

# Get complete message without event-handling code
with client.messages.stream(
    max_tokens=128000,
    messages=[{"role": "user", "content": "Write a detailed analysis..."}],
    model="claude-opus-5",
) as stream:
    message = stream.get_final_message()
print(message.content[0].text)
```

### Beta Features

```python
import anthropic

client = anthropic.Anthropic()

# Access beta features via beta namespace
response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    betas=["files-api-2025-04-14"],
)
```

### Error Handling

```python
import anthropic

client = anthropic.Anthropic()

try:
    message = client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}],
    )
except anthropic.AuthenticationError as e:
    print(f"Auth failed: {e}")
except anthropic.RateLimitError as e:
    print(f"Rate limited: {e}")
except anthropic.APIStatusError as e:
    print(f"API error {e.status_code}: {e.message}")
```

### Request ID Access

```python
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
print(f"Request ID: {message._request_id}")
```

### Platform Configuration

```python
import anthropic

# Claude Platform on AWS (Anthropic-managed infra, AWS billing)
client = anthropic.AnthropicAWS(
    workspace_id="your-workspace-id",  # or ANTHROPIC_AWS_WORKSPACE_ID env var
)

# Amazon Bedrock Messages API (new, recommended)
client = anthropic.AnthropicBedrockMantle()

# Amazon Bedrock legacy (InvokeModel API)
client = anthropic.AnthropicBedrock()

# Google Vertex AI
client = anthropic.AnthropicVertex(
    project_id="your-project",
    region="us-east5",
)

# Microsoft Foundry
client = anthropic.AnthropicFoundry()
```

## TypeScript SDK

### Installation

```bash
npm install @anthropic-ai/sdk
```

### Basic Usage

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({ apiKey: "sk-ant-..." });
// Or reads ANTHROPIC_API_KEY from environment:
// const client = new Anthropic();

const message = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello, Claude" }],
});
console.log(message.content[0].type === "text" ? message.content[0].text : "");
```

### Streaming

The TypeScript SDK returns an `AsyncIterable<RawMessageStreamEvent>` when `stream: true`:

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const stream = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Tell me a story" }],
  stream: true,
});

for await (const event of stream) {
  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
    process.stdout.write(event.delta.text);
  }
}
```

### Streaming with Thinking

```typescript
const stream = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 8192,
  thinking: { type: "enabled", budget_tokens: 4000 },
  messages: [{ role: "user", content: "Solve this problem..." }],
  stream: true,
});

for await (const event of stream) {
  if (event.type === "content_block_start") {
    if (event.content_block.type === "thinking") console.log("[THINKING]");
    else if (event.content_block.type === "text") console.log("\n[ANSWER]");
  } else if (event.type === "content_block_delta") {
    if (event.delta.type === "thinking_delta") process.stdout.write(event.delta.thinking);
    else if (event.delta.type === "text_delta") process.stdout.write(event.delta.text);
  }
}
```

### Error Handling

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

try {
  const message = await client.messages.create({
    model: "claude-sonnet-4-5-20250929",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello" }],
  });
} catch (err) {
  if (err instanceof Anthropic.AuthenticationError) {
    console.error("Auth failed:", err.message);
  } else if (err instanceof Anthropic.RateLimitError) {
    console.error("Rate limited:", err.message);
  } else if (err instanceof Anthropic.BadRequestError) {
    console.error("Bad request:", err.status, err.message);
  } else if (err instanceof Anthropic.APIError) {
    console.error("API error:", err.status, err.message);
  }
}
```

### RequestOptions (Second Argument)

The `create()` method accepts a second argument of type `RequestOptions`:

```typescript
const message = await client.messages.create(
  {
    model: "claude-sonnet-4-5-20250929",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello" }],
  },
  {
    signal: abortController.signal,    // AbortSignal for cancellation
    timeout: 30000,                    // Per-request timeout in ms
    maxRetries: 3,                     // Override default retry count
    headers: { "anthropic-beta": "feature-name" },  // Extra headers
  }
);
```

### Beta Features via Headers

SDK v0.115.0 does NOT support a `betas` body parameter on `messages.create()`. Passing `betas: [...]` in the body causes API error `"betas: Extra inputs are not permitted"`. Use `headers` in RequestOptions:

```typescript
// WRONG - causes 400 error in SDK v0.115.0:
await client.messages.create({
  model: "claude-opus-4-5-20251101",
  max_tokens: 1024,
  betas: ["some-beta-feature"],  // NOT a valid body parameter
  messages: [...],
});

// CORRECT - pass beta via headers:
await client.messages.create(
  {
    model: "claude-opus-4-5-20251101",
    max_tokens: 1024,
    messages: [...],
  },
  { headers: { "anthropic-beta": "some-beta-feature" } }
);
```

For the Python SDK, use `client.beta.messages.create()` with `betas=[...]` parameter instead.

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
      properties: {
        location: { type: "string", description: "City, State" },
      },
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

  // Append assistant response, then tool results
  messages.push({ role: "assistant", content: response.content });
  const toolResults: Anthropic.ToolResultBlockParam[] = [];
  for (const block of response.content) {
    if (block.type === "tool_use") {
      const result = getWeather((block.input as { location: string }).location);
      toolResults.push({ type: "tool_result", tool_use_id: block.id, content: result });
    }
  }
  messages.push({ role: "user", content: toolResults });
}
```

## SDK Benefits Over Raw HTTP

- Automatic header management (x-api-key, anthropic-version, content-type)
- Type-safe request and response handling (Pydantic models in Python)
- Built-in retry logic with exponential backoff for transient errors
- Streaming support with high-level helpers
- Request timeout management and TCP keep-alive
- 10-minute timeout validation for non-streaming requests

## CLI (`ant`)

The `ant` CLI provides command-line access to the Claude API for shell scripting, native integration with Claude Code, and YAML-based API resource versioning. See https://platform.claude.com/docs/en/api/sdks/cli for usage.

## GitHub Repositories

- **Python**: https://github.com/anthropics/anthropic-sdk-python
- **TypeScript**: https://github.com/anthropics/anthropic-sdk-typescript
- **Java**: https://github.com/anthropics/anthropic-sdk-java
- **Go**: https://github.com/anthropics/anthropic-sdk-go
- **Ruby**: https://github.com/anthropics/anthropic-sdk-ruby
- **C#**: https://github.com/anthropics/anthropic-sdk-csharp
- **PHP**: https://github.com/anthropics/anthropic-sdk-php

## Gotchas and Quirks

- The Python SDK uses `_request_id` (with underscore prefix) to access the request ID
- `client.messages.stream()` is a context manager; use `with` statement
- Beta features require the `beta` namespace: `client.beta.messages.create()`
- SDKs validate non-streaming requests against a 10-minute timeout
- Five platform clients: AnthropicAWS (beta), AnthropicBedrockMantle, AnthropicBedrock (legacy), AnthropicVertex, AnthropicFoundry
- Use AnthropicBedrockMantle for new Bedrock projects; AnthropicBedrock is for existing InvokeModel API apps

## Related Endpoints

- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` - API overview
- `_INFO_ANTAPI-04_AUTHENTICATION.md [ANTAPI-IN04]` - API key configuration
- `_INFO_ANTAPI-09_STREAMING.md [ANTAPI-IN09]` - Streaming details
- `_INFO_ANTAPI-51_Effort_Adaptive_Params.md [ANTAPI-IN51]` - Effort and adaptive reasoning parameters (Python + TypeScript)

## Sources

- ANTAPI-SC-ANTH-SDKOVW - https://platform.claude.com/docs/en/api/client-sdks - SDK overview, platform support, repos
- ANTAPI-SC-ANTH-SDKPY - https://platform.claude.com/docs/en/api/sdks/python - Python SDK details
- ANTAPI-SC-GH-SDKPY - https://github.com/anthropics/anthropic-sdk-python - SDK source, api.md

## SDK Verification

Examples updated for `anthropic` SDK 0.120.0. Pending re-verification in Prompt 3.

## Document History

**[2026-07-27]**
- Added: Full TypeScript SDK section (installation, basic usage, streaming, thinking, error handling, RequestOptions, beta headers, tool use with agentic loop)
- Added: `betas` vs `headers` distinction for SDK v0.115.0 (betas body param not supported)
- Source: Live API tests (`_INFO_ANTAPI-50_SDK_Model_Methods.md`) and SDK source inspection

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: SDK version 0.104.0 -> 0.120.0 (Jul 24, 2026)
- Added: Swift SDK (beta) for Apple Foundation Models
- Changed: Model references to claude-opus-5

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Added: ant CLI, AnthropicAWS, AnthropicBedrockMantle, AnthropicFoundry clients
- Added: Platform-specific install extras (aws, aiohttp)

**[2026-03-20 06:10]**
- Added: SDK verification section (anthropic 0.120.0, all 9 examples valid)

**[2026-03-20 02:22]**
- Initial documentation created from SDK overview and Python SDK pages
