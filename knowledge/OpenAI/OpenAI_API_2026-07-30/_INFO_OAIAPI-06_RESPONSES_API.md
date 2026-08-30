# Responses API

**Doc ID**: OAIAPI-IN06
**Goal**: Document Responses API - create, retrieve, delete, cancel, compact; tools, reasoning, background mode
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Responses API (`POST /v1/responses`) is OpenAI's recommended primary interface for text generation, replacing the Assistants API pattern. It provides a stateless request/response model with optional state via `previous_response_id` chaining or Conversations API. Supports all GPT-5.x models (GPT-5.6 Sol/Terra/Luna as of 2026-07). Features include: built-in tools (web_search, file_search, code_interpreter, computer_use, hosted_shell, apply_patch, skills, mcp, tool_search, **programmatic_tool_calling** [NEW]), reasoning effort control (6 levels including `max`), structured outputs, streaming, background mode, flex processing, compaction, and **inline moderation** [NEW]. **NEW (2026-07)**: Programmatic Tool Calling lets GPT-5.6 write JavaScript to orchestrate tool calls in a V8 sandbox (see IN94). Multi-Agent orchestration beta enables parallel subagent coordination (see IN95). Persisted reasoning (`reasoning.context`) carries chain-of-thought across turns. Pro mode (`reasoning.mode: "pro"`) applies more compute for harder tasks. **NEW (2026-06)**: Inline moderation - pass `moderation` object to score input/output without separate API call. The API also supports input token counting (`POST /v1/responses/input_tokens/count`), response cancellation, and response compaction for long-running workflows. [VERIFIED] (OAIAPI-SC-OAI-RESOVW, OAIAPI-SC-OAI-RESCRT, OAIAPI-SC-OAI-GCHLOG)

## REST API

### Create a Response

**Endpoint**: `POST /v1/responses`

**Request**:

```json
{
  "model": "gpt-5.5",
  "input": "Analyze the trade-offs between REST and GraphQL for a high-traffic API.",
  "instructions": "You are a senior API architect. Be thorough and specific.",
  "reasoning": {"effort": "high"},
  "tools": [
    {"type": "web_search"}
  ],
  "text": {
    "format": {"type": "json_schema", "name": "analysis", "schema": {}}
  },
  "max_output_tokens": 4096,
  "temperature": 0.7,
  "store": true
}
```

**Key Parameters**:

- **model** (string, required) - Model ID (e.g., `gpt-5.5`, `gpt-5.4-mini`)
- **input** (string | array, required) - User input text or array of content items
- **instructions** (string, optional) - System instructions (replaces system message)
- **reasoning** (object, optional) - `{"effort": "none"|"low"|"medium"|"high"|"xhigh"}`
- **tools** (array, optional) - Array of tool configurations
- **text** (object, optional) - Output format configuration (structured outputs)
- **max_output_tokens** (integer, optional) - Maximum tokens in response
- **temperature** (number, optional) - Sampling temperature (0-2)
- **previous_response_id** (string, optional) - Chain to previous response for multi-turn
- **store** (boolean, optional) - Store response for later retrieval. Default: true
- **background** (boolean, optional) - Run in background mode
- **stream** (boolean, optional) - Enable streaming

**Response** (`200 OK`):

```json
{
  "id": "resp_abc123",
  "object": "response",
  "status": "completed",
  "model": "gpt-5.5-2026-04-23",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        {"type": "output_text", "text": "Here is my analysis..."}
      ]
    }
  ],
  "usage": {
    "input_tokens": 150,
    "output_tokens": 1200,
    "total_tokens": 1350,
    "prompt_tokens_details": {
      "cached_tokens": 100
    }
  }
}
```

### Retrieve a Response

**Endpoint**: `GET /v1/responses/{response_id}`

### Delete a Response

**Endpoint**: `DELETE /v1/responses/{response_id}`

### Cancel a Response

**Endpoint**: `POST /v1/responses/{response_id}/cancel`

Cancels a running response (useful for background mode).

### Compact a Response

**Endpoint**: `POST /v1/responses/{response_id}/compact`

Compacts conversation history for long-running workflows. See IN78 Compaction.

### Count Input Tokens

**Endpoint**: `POST /v1/responses/input_tokens/count`

Pre-request token estimation for cost calculation.

## SDK Examples (Python)

### Basic Response

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Explain the CAP theorem in distributed systems.",
)
print(response.output_text)
```

### Multi-Turn with Previous Response

```python
from openai import OpenAI

client = OpenAI()

r1 = client.responses.create(
    model="gpt-5.6-sol",
    input="What is the CAP theorem?",
)
print(f"Turn 1: {r1.output_text[:200]}...")

r2 = client.responses.create(
    model="gpt-5.6-sol",
    input="Give me a concrete example with a real database.",
    previous_response_id=r1.id,
)
print(f"Turn 2: {r2.output_text[:200]}...")
```

### With Tools and Reasoning

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    instructions="You are a technical researcher. Cite sources.",
    input="What are the latest developments in LLM safety?",
    tools=[
        {"type": "web_search", "search_context_size": "high"},
        {"type": "code_interpreter"},
    ],
    reasoning={"effort": "high"},
)
print(response.output_text)
```

### Structured Output

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="List the top 3 programming languages for data science with pros and cons.",
    text={
        "format": {
            "type": "json_schema",
            "name": "languages",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "languages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "pros": {"type": "array", "items": {"type": "string"}},
                                "cons": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["name", "pros", "cons"],
                        }
                    }
                },
                "required": ["languages"],
            }
        }
    },
)
import json
print(json.dumps(json.loads(response.output_text), indent=2))
```

### Background Mode

```python
from openai import OpenAI

client = OpenAI()

# Start background response
response = client.responses.create(
    model="gpt-5.6-sol",
    input="Conduct a thorough analysis of the entire repository...",
    reasoning={"mode": "pro"},
    background=True,
)
print(f"Background response ID: {response.id}")
print(f"Status: {response.status}")  # "in_progress"

# Poll for completion
import time
while response.status != "completed":
    time.sleep(5)
    response = client.responses.retrieve(response.id)
    print(f"Status: {response.status}")

print(response.output_text)
```

## Error Responses

- **400 Bad Request** - Invalid model, incompatible parameters, schema error
- **401 Unauthorized** - Invalid API key
- **429 Too Many Requests** - Rate limit exceeded
- **500 Internal Server Error** - Server error

## Gotchas and Quirks

- **GPT-5.6 defaults**: Reasoning defaults to `medium`. Pro mode available for harder tasks [VERIFIED]
- **Programmatic Tool Calling**: GPT-5.6 writes JS to orchestrate tools in V8 sandbox. Enable via `tools: [{"type": "programmatic_tool_calling"}]` [VERIFIED]
- **Multi-Agent beta**: Parallel subagents via `agents` parameter. Beta - breaking changes possible [VERIFIED]
- **Inline moderation**: Pass `moderation: {"input": true, "output": true}` for in-request content scoring [VERIFIED]
- **Persisted reasoning**: `reasoning.context` carries chain-of-thought across turns without rebuild [VERIFIED]
- **Compaction**: Available via POST compact endpoint for managing context growth [VERIFIED]
- **return_token_budget**: Web search parameter for extended reasoning [VERIFIED]
- **store default**: Responses are stored by default (`store: true`). Set `false` for ephemeral use [VERIFIED]

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

- OAIAPI-SC-OAI-RESOVW - Responses API Overview
- OAIAPI-SC-OAI-RESCRT - POST Create a response
- OAIAPI-SC-OAI-RESCAN - POST Cancel a response
- OAIAPI-SC-OAI-RESCMP - POST Compact a response
- OAIAPI-SC-OAI-RESTOK - POST Count input tokens

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: Programmatic Tool Calling (GPT-5.6, V8 sandbox orchestration)
- Added: Multi-Agent orchestration beta (parallel subagents)
- Added: Inline moderation (`moderation` object in requests)
- Added: Persisted reasoning (`reasoning.context`)
- Added: Pro mode (`reasoning.mode: "pro"`)
- Changed: Model references from GPT-5.5 to GPT-5.6
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 10:45]**
- Updated from 2026-03-20 version
- Added: Compaction endpoint reference
- Added: return_token_budget for web search
- Changed: Model references to GPT-5.5
- Changed: Reasoning default note (medium for GPT-5.5)
