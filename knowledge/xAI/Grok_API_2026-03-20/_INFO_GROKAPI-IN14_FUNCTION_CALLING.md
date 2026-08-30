# INFO: Function Calling

**Doc ID**: GROKAPI-IN14
**Goal**: Client-side function calling, tool definitions, Pydantic schemas, tool_choice, parallel calling
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references
- `_INFO_GROKAPI-IN13_TOOLS_OVERVIEW.md [GROKAPI-IN13]` for tool architecture

## Summary

Function calling enables the model to invoke custom tools defined by the developer. The model returns a `function_call` output item with the function name and JSON arguments; the developer executes the function locally and returns results via `function_call_output`. Tool definitions use JSON Schema for parameters. In the Responses API, function calls are returned as typed output items (`type: "function_call"`) with a `call_id` for correlation. Multi-turn tool use works via `previous_response_id` - send the function result and continue. With streaming, function calls are returned as a single complete chunk (not streamed incrementally). Supports `tool_choice` for controlling tool selection: `"auto"` (default), `"none"`, `"required"`, or specific function name. Parallel tool calls enabled by default (`parallel_tool_calls: true`). Compatible with OpenAI SDK function calling patterns. [VERIFIED] (GROKAPI-SC-XAI-FUNCCALL | https://docs.x.ai/developers/tools/function-calling)

## Key Facts

- [VERIFIED] Tool type: `"function"` with `name`, `description`, `parameters` (JSON Schema) (GROKAPI-SC-XAI-FUNCCALL)
- [VERIFIED] Response: `function_call` output item with `call_id` and `arguments` (GROKAPI-SC-XAI-FUNCCALL)
- [VERIFIED] Result: `function_call_output` input with `call_id` and `output` (GROKAPI-SC-XAI-FUNCCALL)
- [VERIFIED] Streaming: function call returned as single complete chunk (GROKAPI-SC-XAI-FUNCCALL)
- [VERIFIED] Parallel tool calls: enabled by default (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] Can mix with server-side tools in same request (GROKAPI-SC-XAI-TOOLADVANCED)

## Quick Reference

- **Define tool**: `{"type": "function", "name": "...", "description": "...", "parameters": {...}}`
- **Model returns**: `{"type": "function_call", "call_id": "...", "name": "...", "arguments": "..."}`
- **Send result**: `{"type": "function_call_output", "call_id": "...", "output": "..."}`
- **tool_choice**: `"auto"` (default), `"none"`, `"required"`, or `{"type": "function", "name": "func_name"}`

## Examples

### Complete Function Calling Flow (OpenAI SDK)

```python
import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

tools = [
    {
        "type": "function",
        "name": "get_temperature",
        "description": "Get current temperature for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "fahrenheit"},
            },
            "required": ["location"],
        },
    },
]

# Step 1: Send request with tools
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What is the temperature in San Francisco?"}],
    tools=tools,
)

# Step 2: Handle function calls
for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        # Execute your function locally
        result = {"location": args["location"], "temperature": 59, "unit": args.get("unit", "fahrenheit")}

        # Step 3: Return result and continue
        response = client.responses.create(
            model="grok-4.20-beta-latest-non-reasoning",
            input=[{"type": "function_call_output", "call_id": item.call_id, "output": json.dumps(result)}],
            tools=tools,
            previous_response_id=response.id,
        )

# Step 4: Get final response
for item in response.output:
    if item.type == "message":
        print(item.content[0].text)
```

### Function Calling (xAI SDK)

```python
import os
import json
from xai_sdk import Client
from xai_sdk.chat import user, tool, tool_result

client = Client(api_key=os.getenv("XAI_API_KEY"))

tools = [
    tool(
        name="get_temperature",
        description="Get current temperature for a location",
        parameters={
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    ),
]

chat = client.chat.create(model="grok-4.20-beta-latest-non-reasoning", tools=tools)
chat.append(user("What is the temperature in San Francisco?"))
response = chat.sample()

if response.tool_calls:
    chat.append(response)
    for tc in response.tool_calls:
        args = json.loads(tc.function.arguments)
        result = {"location": args["location"], "temperature": 59, "unit": "fahrenheit"}
        chat.append(tool_result(json.dumps(result), tool_call_id=tc.id))
    response = chat.sample()

print(response.content)
```

### Mixing Server-Side and Client-Side Tools

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Search for Bitcoin price and save to my DB."}],
    tools=[
        {"type": "web_search"},  # Server-side (auto-executes)
        {
            "type": "function",
            "name": "save_to_db",
            "description": "Save a key-value pair to database",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["key", "value"],
            },
        },
    ],
)
```

### cURL

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-4.20-beta-latest-non-reasoning",
    "input": [
      {"role": "user", "content": "What is the temperature in San Francisco?"}
    ],
    "tools": [
      {
        "type": "function",
        "name": "get_temperature",
        "description": "Get current temperature for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string", "description": "City name"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
          },
          "required": ["location"]
        }
      }
    ]
  }'
```

## Differences from Other APIs

### vs OpenAI

- **Compatible**: Same function calling format, same SDK patterns
- **Mixing**: Can combine server-side tools (web_search) with function calling in one request
- **Streaming**: Function calls returned as single chunk (same as OpenAI)

### vs Anthropic

- **Different format**: Anthropic uses `tool_use` content blocks; xAI uses OpenAI-compatible `function_call` items
- **Result format**: Anthropic uses `tool_result` role; xAI uses `function_call_output` type

### vs Gemini

- **Different format**: Gemini uses `functionDeclarations` in tools; xAI uses OpenAI-compatible function definitions

## Sources

- GROKAPI-SC-XAI-FUNCCALL | https://docs.x.ai/developers/tools/function-calling | Accessed: 2026-03-20
- GROKAPI-SC-XAI-TOOLADVANCED | https://docs.x.ai/developers/tools/advanced-usage | Accessed: 2026-03-20

## Document History

**[2026-03-20 12:00]**
- Fixed: xAI SDK example - added `tool_call_id=tc.id` to `tool_result()` call per SDK best practice

**[2026-03-20 04:20]**
- Initial document created with complete function calling flow and examples
