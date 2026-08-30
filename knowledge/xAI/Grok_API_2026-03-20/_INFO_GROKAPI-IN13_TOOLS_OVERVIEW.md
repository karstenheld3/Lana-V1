# INFO: Tools Overview

**Doc ID**: GROKAPI-IN13
**Goal**: Tool types (server-side vs client-side), pricing model, how tools work, tool list
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok API distinguishes between two tool categories: **server-side tools** that execute on xAI servers and **client-side tools** (function calling) where the model returns tool calls for the client to execute. Server-side tools are unique to Grok - the model autonomously invokes them during inference, and results are returned directly in the response. Available server-side tools: `web_search` (internet search), `x_search` (X/Twitter search), `code_execution`/`code_interpreter` (Python sandbox), `attachment_search` (file search), `collections_search`/`file_search` (RAG), `view_image` (image analysis from search), `view_x_video` (video analysis from X), and Remote MCP tools. Server-side tools have per-invocation costs beyond token billing. Client-side function calling follows the OpenAI pattern. Tools can be mixed in a single request. The agent autonomously decides how many tool calls to make based on query complexity. In the gRPC API (xAI SDK), `code_interpreter` and `file_search` names are not supported. [VERIFIED] (GROKAPI-SC-XAI-TOOLSOVERVIEW | https://docs.x.ai/developers/tools/overview)

## Key Facts

- [VERIFIED] Two tool types: server-side (auto-execute on xAI) and client-side (function calling) (GROKAPI-SC-XAI-TOOLSOVERVIEW)
- [VERIFIED] Server-side tools: web_search, x_search, code_execution, attachment_search, collections_search, view_image, view_x_video, Remote MCP (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Server-side tools have per-invocation costs + token costs (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] view_image and view_x_video: no invocation fee, billed for image tokens only (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Remote MCP tools: no invocation fee, billed for tokens only (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Agent autonomously decides how many tools to call based on query complexity (GROKAPI-SC-XAI-TOOLSOVERVIEW)
- [VERIFIED] gRPC API does not support `code_interpreter` and `file_search` names (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] All tool names work in the Responses API (GROKAPI-SC-XAI-MODELS)

## Quick Reference

### Server-Side Tools (Execute on xAI Servers)

- **`web_search`**: Search the internet and browse web pages
- **`x_search`**: Search X posts, user profiles, and threads
- **`code_execution`** / **`code_interpreter`**: Run Python code in sandbox
- **`attachment_search`**: Search through files attached to messages
- **`collections_search`** / **`file_search`**: Query uploaded document collections (RAG)
- **`view_image`**: Analyze images found during web/X search
- **`view_x_video`**: Analyze videos found during X search
- **Remote MCP**: Connect custom MCP tool servers

### Client-Side Tools (Function Calling)

- **`function`**: Custom function definitions with JSON schema parameters

### Billing

- **web_search, x_search, code_execution, attachment_search, collections_search**: Per-invocation fee + token costs
- **view_image, view_x_video**: Image token costs only (no invocation fee)
- **Remote MCP**: Token costs only (no invocation fee)

## Examples

### Enabling Server-Side Tools (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What is the latest AI news?"}],
    tools=[
        {"type": "web_search"},
        {"type": "x_search"},
    ],
)
print(response.output_text)
```

### Mixing Server-Side and Client-Side Tools

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Find the current price of Bitcoin and save it to my database."}],
    tools=[
        {"type": "web_search"},  # Server-side
        {  # Client-side function
            "type": "function",
            "function": {
                "name": "save_to_database",
                "description": "Save data to the user's database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": "string"},
                    },
                    "required": ["key", "value"],
                },
            },
        },
    ],
)
```

### All Server-Side Tools (xAI SDK)

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search, code_execution, collections_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.20-beta-latest-non-reasoning",
    tools=[
        web_search(),
        x_search(),
        code_execution(),
        collections_search(collection_ids=["col_abc123"]),
    ],
)

chat.append(user("Analyze recent AI trends using web data, X posts, and run calculations."))
response = chat.sample()
print(response.content)
```

## Differences from Other APIs

### vs OpenAI

- **Server-side tools**: xAI has built-in tools that execute on server (web_search, x_search, code_execution); OpenAI tools are client-side except Assistants API (file_search, code_interpreter)
- **Pricing model**: xAI has separate per-invocation costs; OpenAI bundles tool costs
- **X Search**: UNIQUE to Grok - no equivalent in OpenAI
- **Tool mixing**: Can combine server-side and client-side in one request (OpenAI Assistants can too, but differently)

### vs Anthropic

- **No server-side tools**: Anthropic has no built-in search or code execution tools
- **Computer use**: Anthropic has computer_use tool; xAI has no equivalent
- **MCP**: Both support MCP tools, but xAI has native Remote MCP in API

### vs Gemini

- **Similar grounding**: Gemini has google_search_retrieval grounding; xAI has web_search
- **Code execution**: Both have built-in Python sandbox (Gemini code_execution, xAI code_execution)
- **X Search**: UNIQUE to Grok

## Sources

- GROKAPI-SC-XAI-TOOLSOVERVIEW | https://docs.x.ai/developers/tools/overview | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:15]**
- Initial document created with tool types, pricing, and comparison
