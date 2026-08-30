# Official SDKs

**Doc ID**: OAIAPI-IN46
**Goal**: Document official OpenAI SDKs - Python, TypeScript, .NET, Java, Go, Ruby, and Agents SDK
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI provides official SDKs for Python, TypeScript/Node.js, .NET, Java, Go, and Ruby. The Python SDK (`openai` package, latest v2.45.0 as of 2026-07) is the primary SDK with full API coverage including Responses, Chat Completions, Realtime, Files, Vector Stores, Containers, Fine-tuning, and all administrative endpoints. The Agents SDK (`openai-agents` for Python, `@openai/agents` for TypeScript) adds higher-level abstractions for multi-agent systems. **NEW since 2026-05**: Amazon Bedrock Responses support (v2.40.0), inline moderation (v2.41.0), admin spend_alerts (v2.42.0), GPT-5.6 support (v2.45.0). Workload Identity Federation supported for keyless auth (v2.39.0+). All SDKs handle authentication, retries with exponential backoff, streaming, pagination, and error handling automatically. [VERIFIED] (OAIAPI-SC-GH-SDKPY, OAIAPI-SC-GH-AGNTPY, OAIAPI-SC-OAI-GADMSK)

## Key Facts

- **Python SDK**: `pip install openai` - primary SDK, full API coverage [VERIFIED] (OAIAPI-SC-GH-SDKPY)
- **TypeScript SDK**: `npm install openai` - full API coverage [VERIFIED] (OAIAPI-SC-GH-SDKPY)
- **Agents SDK (Python)**: `pip install openai-agents` - multi-agent framework [VERIFIED] (OAIAPI-SC-GH-AGNTPY)
- **Agents SDK (TypeScript)**: `npm install @openai/agents` - added 2026-05 [VERIFIED] (OAIAPI-SC-OAI-GCHLOG)
- **.NET SDK**: `dotnet add package OpenAI` [VERIFIED] (OAIAPI-SC-GH-SDKREL)
- **Java SDK**: Maven/Gradle package [VERIFIED] (OAIAPI-SC-GH-SDKREL)
- **Go SDK**: `go get github.com/openai/openai-go` [VERIFIED] (OAIAPI-SC-GH-SDKREL)
- **Ruby SDK**: `gem install openai` [VERIFIED] (OAIAPI-SC-GH-SDKREL)
- **Admin APIs in SDKs**: All languages since 2026-05 [VERIFIED] (OAIAPI-SC-OAI-GADMSK)
- **Auto-retry**: All SDKs retry on 429/5xx with exponential backoff [VERIFIED] (OAIAPI-SC-GH-SDKPY)

## SDK Matrix

- **Python** (`openai`): pip install openai. Full API + Agents SDK + Admin APIs
- **TypeScript/Node** (`openai`): npm install openai. Full API + Agents SDK (NEW 2026-05) + Admin APIs
- **Go** (`openai-go`): go get github.com/openai/openai-go. Full API + Admin APIs (NEW)
- **Ruby** (`openai`): gem install openai. Full API + Admin APIs (NEW)
- **Java** (`openai-java`): Maven/Gradle. Full API + Admin APIs (NEW)
- **.NET** (`OpenAI`): NuGet. Full API

## Quick Reference

```bash
# Python
pip install openai
pip install openai-agents  # Agents SDK

# TypeScript/Node.js
npm install openai
npm install @openai/agents  # Agents SDK

# .NET
dotnet add package OpenAI

# Go
go get github.com/openai/openai-go
```

## Python SDK

### Installation and Configuration

```python
from openai import OpenAI

# Auto-reads OPENAI_API_KEY env var
client = OpenAI()

# Explicit configuration
client = OpenAI(
    api_key="sk-...",
    organization="org-...",
    project="proj-...",
    timeout=60.0,
    max_retries=3
)
```

### Key Features

- **Typed responses**: All API responses are Pydantic models
- **Streaming**: Iterator-based streaming with `.stream()` methods
- **Async support**: `AsyncOpenAI` client for asyncio
- **Auto-pagination**: Iterate over paginated results automatically
- **File uploads**: `client.files.create(file=open(...), purpose=...)`
- **Error handling**: Typed exceptions (`APIError`, `RateLimitError`, etc.)

### Async Client

```python
from openai import AsyncOpenAI
import asyncio

async def main():
    client = AsyncOpenAI()
    
    response = await client.responses.create(
        model="gpt-5.6-sol",
        input="Hello"
    )
    print(response.output_text)

asyncio.run(main())
```

### Streaming

```python
from openai import OpenAI

client = OpenAI()

stream = client.responses.create(
    model="gpt-5.6-sol",
    input="Write a haiku",
    stream=True
)

for event in stream:
    if hasattr(event, 'delta'):
        print(event.delta, end="", flush=True)
```

### Error Handling

```python
from openai import OpenAI, APIError, RateLimitError, APITimeoutError

client = OpenAI()

try:
    response = client.responses.create(
        model="gpt-5.6-sol",
        input="Hello"
    )
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.response.headers.get('retry-after')}")
except APITimeoutError:
    print("Request timed out")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

### Auto-Pagination

```python
from openai import OpenAI

client = OpenAI()

for model in client.models.list():
    print(model.id)
```

### Admin APIs (NEW 2026-05)

```python
from openai import OpenAI

client = OpenAI()

# Admin APIs now in SDK
projects = client.admin.organization.projects.list()
```

## Agents SDK (Python)

### Core Concepts

- **Agent**: Configured LLM with instructions, tools, and handoff targets
- **Runner**: Executes agent loops (tool calls, handoffs, guardrails)
- **Handoff**: Transfer control between agents
- **Guardrails**: Input/output validation
- **Tracing**: Built-in observability

### Basic Agent

```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model="gpt-5.6-sol"
)

result = Runner.run_sync(agent, "What is the capital of France?")
print(result.final_output)
```

### Agent with Tools

```python
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(location: str) -> str:
    """Get current weather for a location"""
    return f"72F and sunny in {location}"

agent = Agent(
    name="Weather Bot",
    instructions="Help users with weather queries.",
    model="gpt-5.6-sol",
    tools=[get_weather]
)

result = Runner.run_sync(agent, "What's the weather in San Francisco?")
print(result.final_output)
```

### Multi-Agent Handoff

```python
from agents import Agent, Runner

sales_agent = Agent(
    name="Sales",
    instructions="Help with product questions and sales.",
    model="gpt-5.6-sol"
)

support_agent = Agent(
    name="Support",
    instructions="Help with technical issues.",
    model="gpt-5.6-sol"
)

triage_agent = Agent(
    name="Triage",
    instructions="Route users to the right agent.",
    model="gpt-5.6-sol",
    handoffs=[sales_agent, support_agent]
)

result = Runner.run_sync(triage_agent, "My product is broken")
print(f"Handled by: {result.last_agent.name}")
print(result.final_output)
```

## TypeScript SDK

### Installation and Usage

```typescript
import OpenAI from 'openai';

const client = new OpenAI();

const response = await client.responses.create({
  model: 'gpt-5.5',
  input: 'Hello',
});

console.log(response.output_text);
```

### Streaming

```typescript
import OpenAI from 'openai';

const client = new OpenAI();

const stream = await client.responses.create({
  model: 'gpt-5.5',
  input: 'Write a poem',
  stream: true,
});

for await (const event of stream) {
  process.stdout.write(event.delta ?? '');
}
```

## SDK Configuration Options

All SDKs support:

- **api_key**: API key (or OPENAI_API_KEY env var)
- **organization**: Organization ID (or OPENAI_ORG_ID env var)
- **project**: Project ID (or OPENAI_PROJECT_ID env var)
- **base_url**: Custom base URL (default: https://api.openai.com/v1)
- **timeout**: Request timeout in seconds
- **max_retries**: Number of retries on failure (default: 2)
- **default_headers**: Additional headers for all requests

## Error Types (Python SDK)

- **APIError**: Base class for all API errors
- **AuthenticationError**: Invalid API key (401)
- **PermissionDeniedError**: Insufficient permissions (403)
- **NotFoundError**: Resource not found (404)
- **UnprocessableEntityError**: Invalid parameters (422)
- **RateLimitError**: Rate limit exceeded (429)
- **InternalServerError**: Server error (500+)
- **APIConnectionError**: Network connectivity issues
- **APITimeoutError**: Request timeout

## Differences from Other APIs

- **vs Anthropic SDK**: `anthropic` Python package. Similar design but different method names (`messages.create` vs `responses.create`). No Agents SDK equivalent
- **vs Gemini SDK**: `google-generativeai` Python package. Different API surface (`generate_content`). Has Vertex AI SDK for enterprise
- **vs Grok SDK**: Uses OpenAI-compatible SDK (`openai` package with custom base_url)
- **Unique**: OpenAI has the most comprehensive SDK ecosystem (6 languages + Agents SDK)

## Limitations and Known Issues

- **Breaking changes**: SDK updates may include breaking changes; pin versions in production [VERIFIED] (OAIAPI-SC-GH-SDKPY)
- **Agents SDK maturity**: Relatively new, API surface may change [VERIFIED] (OAIAPI-SC-GH-AGNTPY)
- **Browser support**: TypeScript SDK works in Node.js; browser usage requires proxying API calls [VERIFIED] (OAIAPI-SC-GH-SDKPY)

## Gotchas and Quirks

- **Env var precedence**: Constructor params override env vars [VERIFIED] (OAIAPI-SC-GH-SDKPY)
- **Retry behavior**: Auto-retries on 429/5xx only; 4xx errors (except 429) are not retried [VERIFIED] (OAIAPI-SC-GH-SDKPY)
- **Streaming types**: Stream events have different types depending on the endpoint used [VERIFIED] (OAIAPI-SC-GH-SDKPY)
- **Agents SDK import**: Import from `agents` not `openai_agents` [VERIFIED] (OAIAPI-SC-GH-AGNTPY)

## TypeScript Examples

### SDK Installation and Configuration

```typescript
// npm install openai
import OpenAI from "openai";

// Default: reads OPENAI_API_KEY from environment
const client = new OpenAI();

// Explicit configuration
const configured = new OpenAI({
  apiKey: "sk-...",
  organization: "org-...",
  maxRetries: 3,
  timeout: 30_000,
});

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Hello!",
});
console.log(response.output_text);
```

## Sources

- OAIAPI-SC-GH-SDKPY - OpenAI Python SDK (GitHub)
- OAIAPI-SC-GH-AGNTPY - OpenAI Agents SDK Python (GitHub)
- OAIAPI-SC-GH-SDKREL - SDK release notes
- OAIAPI-SC-OAI-GADMSK - Admin API SDK support guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Updated: Python SDK version v2.38.0 -> v2.45.0
- Added: Amazon Bedrock Responses support (v2.40.0)
- Added: Inline moderation support (v2.41.0)
- Added: Workload Identity Federation support (v2.39.0+)
- Added: GPT-5.6 model support (v2.45.0)
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 17:00]**
- Enriched from 2026-03-20 IN46 (49 -> 290 lines)
- Updated model references to gpt-5.5
- Added Admin API SDK support, Ruby SDK, TypeScript Agents SDK

**[2026-05-22 11:25]**
- Added: Admin API SDK support in all languages, TypeScript Agents SDK
