# INFO: Gemini API Function Calling

**Doc ID**: GEMAPI-IN16
**Goal**: Document function declarations, parallel/compositional calling, function IDs, calling modes, and MCP
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini API function calling enables the model to interact with external systems by generating structured function call requests that the application executes and returns results for. Functions are defined in the `tools` array using `functionDeclarations` with a subset of OpenAPI schema format. The API supports four calling modes: AUTO (model decides), ANY (force function call), NONE (disable), and VALIDATED (preview, ensures schema adherence). Gemini uniquely supports parallel function calling (multiple independent calls per turn with ID-based result mapping) and compositional function calling (sequential chaining where one function's output feeds the next). The Python SDK offers automatic function calling where the SDK handles the execute-and-return loop. Function IDs (`id` field) map results back to specific calls, enabling async execution and out-of-order result returns. Gemini 3 models combine function calling with built-in tools (Google Search, Code Execution, URL Context) and structured output in a single request. Native MCP (Model Context Protocol) support enables automatic tool calling from MCP servers.

## Key Facts

- [VERIFIED] Functions defined in `tools[].functionDeclarations[]` using OpenAPI schema subset (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Calling modes: AUTO, ANY, NONE, VALIDATED (preview) (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Parallel calling: multiple function calls per turn with ID mapping (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Compositional calling: sequential chaining of functions (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Automatic function calling: Python SDK feature only (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Native MCP support in SDKs (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Gemini 3: combine function calling with built-in tools and structured output (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] OpenAPI schema subset only; deeply nested schemas may be rejected in ANY mode (GEMAPI-SC-GOOG-FUNCAL)

## Use Cases

- **External API integration**: Weather, databases, calendars, CRM systems
- **Agentic workflows**: Multi-step task execution with tool chains
- **Data retrieval**: Search databases, fetch real-time information
- **Action execution**: Send emails, schedule meetings, create records
- **Multi-tool orchestration**: Combine custom functions with Google Search, code execution

## Quick Reference

**Request field**: `tools[].functionDeclarations[]`
**Config field**: `toolConfig.functionCallingConfig.mode`
**Model output**: `parts[].functionCall` with `{name, args, id}`
**User response**: `parts[].functionResponse` with `{name, response, id}`

## Function Declaration Schema

```json
{
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": "get_weather",
          "description": "Gets current weather for a location. Returns temperature in Celsius.",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "City name, e.g., 'San Francisco, CA'"
              },
              "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit"
              }
            },
            "required": ["location"]
          }
        }
      ]
    }
  ]
}
```

**Declaration Fields:**
- **name** (string, required): Unique function name (underscores/camelCase, no spaces)
- **description** (string, required): Detailed explanation of function purpose and capabilities
- **parameters** (object, required): Input parameters in OpenAPI schema subset
  - **type** (string): Always "object" at top level
  - **properties** (object): Parameter definitions with type, description, enum
  - **required** (array): Required parameter names

## Calling Modes

Configured via `toolConfig.functionCallingConfig.mode`:

- **AUTO** (default): Model decides between text response or function call based on context
- **ANY**: Forces function call; with `allowedFunctionNames` restricts to specific functions
- **NONE**: Disables function calling (keeps declarations for context but prevents calls)
- **VALIDATED** (preview): Like AUTO but ensures schema adherence when function calls are made

```json
{
  "toolConfig": {
    "functionCallingConfig": {
      "mode": "ANY",
      "allowedFunctionNames": ["get_weather", "get_forecast"]
    }
  }
}
```

## Function Call and Response Flow

### Step 1: Model Returns Function Call

```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "functionCall": {
          "name": "get_weather",
          "args": {"location": "Paris", "unit": "celsius"},
          "id": "call_001"
        }
      }],
      "role": "model"
    }
  }]
}
```

### Step 2: User Returns Function Result

```json
{
  "contents": [
    {"role": "user", "parts": [{"text": "What's the weather in Paris?"}]},
    {"role": "model", "parts": [{"functionCall": {"name": "get_weather", "args": {"location": "Paris"}, "id": "call_001"}}]},
    {"role": "user", "parts": [{"functionResponse": {"name": "get_weather", "response": {"temperature": 22, "condition": "sunny"}, "id": "call_001"}}]}
  ]
}
```

### Step 3: Model Generates Final Response

The model uses the function result to produce a natural language response.

## Parallel Function Calling

Model can request multiple independent function calls in a single turn:

```json
{
  "candidates": [{
    "content": {
      "parts": [
        {"functionCall": {"name": "get_weather", "args": {"location": "Paris"}, "id": "call_001"}},
        {"functionCall": {"name": "get_weather", "args": {"location": "London"}, "id": "call_002"}}
      ],
      "role": "model"
    }
  }]
}
```

Results can be returned in **any order** - the API maps results back via `id`:

```json
{
  "role": "user",
  "parts": [
    {"functionResponse": {"name": "get_weather", "response": {"temp": 15}, "id": "call_002"}},
    {"functionResponse": {"name": "get_weather", "response": {"temp": 22}, "id": "call_001"}}
  ]
}
```

## Compositional Function Calling

Sequential chaining where the model calls functions one after another, using outputs as inputs:

1. Model calls `get_current_location()` -> returns "Paris"
2. Model calls `get_weather(location="Paris")` -> returns temperature
3. Model generates final response

This happens automatically when the model determines a multi-step approach is needed.

## Python Examples

### Example 1: Basic Function Calling

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Define functions
weather_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_weather",
            description="Gets current weather for a city",
            parameters={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        )
    ]
)

# Step 1: Send prompt with tools
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the weather in Tokyo?",
    config=types.GenerateContentConfig(tools=[weather_tool])
)

# Step 2: Check for function call
if response.candidates[0].content.parts[0].function_call:
    fc = response.candidates[0].content.parts[0].function_call
    print(f"Function: {fc.name}, Args: {fc.args}")

    # Step 3: Execute function and return result
    weather_result = {"temperature": 28, "condition": "partly cloudy"}

    response2 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(role="user", parts=[types.Part(text="What is the weather in Tokyo?")]),
            types.Content(role="model", parts=[types.Part(function_call=fc)]),
            types.Content(role="user", parts=[
                types.Part(function_response=types.FunctionResponse(
                    name=fc.name,
                    response=weather_result
                ))
            ]),
        ],
        config=types.GenerateContentConfig(tools=[weather_tool])
    )
    print(response2.text)
```

### Example 2: Automatic Function Calling (Python SDK)

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_current_temperature(city: str) -> dict:
    """Gets the current temperature for a city.

    Args:
        city: The city name to get temperature for.

    Returns:
        Dictionary with temperature and unit.
    """
    # In production, call a real weather API
    temperatures = {"Tokyo": 28, "Paris": 22, "London": 15}
    return {"temperature": temperatures.get(city, 20), "unit": "celsius"}

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the temperature in Paris right now?",
    config=types.GenerateContentConfig(
        tools=[get_current_temperature],  # Pass Python function directly
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=False
        )
    )
)

# SDK handles the function call loop automatically
print(response.text)
```

### Example 3: Forced Function Call (ANY mode)

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

tools = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="extract_entities",
            description="Extracts named entities from text",
            parameters={
                "type": "object",
                "properties": {
                    "people": {"type": "array", "items": {"type": "string"}},
                    "locations": {"type": "array", "items": {"type": "string"}},
                    "organizations": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["people", "locations", "organizations"]
            }
        )
    ]
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="John Smith from Google visited the Eiffel Tower in Paris last Tuesday.",
    config=types.GenerateContentConfig(
        tools=[tools],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode="ANY")
        )
    )
)

fc = response.candidates[0].content.parts[0].function_call
print(f"People: {fc.args.get('people')}")
print(f"Locations: {fc.args.get('locations')}")
print(f"Organizations: {fc.args.get('organizations')}")
```

### Example 4: MCP Integration

```python
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents="List files in /tmp directory",
                config=types.GenerateContentConfig(
                    tools=mcp_tools,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=False
                    )
                )
            )
            print(response.text)
```

## cURL Examples

### Example: Function Calling

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"role": "user", "parts": [{"text": "Schedule meeting with Alice at 3pm tomorrow"}]}],
    "tools": [{
      "functionDeclarations": [{
        "name": "schedule_meeting",
        "description": "Schedules a meeting",
        "parameters": {
          "type": "object",
          "properties": {
            "attendees": {"type": "array", "items": {"type": "string"}},
            "time": {"type": "string"},
            "date": {"type": "string"}
          },
          "required": ["attendees", "time", "date"]
        }
      }]
    }]
  }'
```

## Comparison with Other APIs

### vs OpenAI

- **Declaration format**: Gemini: `tools[].functionDeclarations[]` | OpenAI: `tools[].function`
- **Schema format**: Both use OpenAPI schema subset (slightly different subsets)
- **Parallel calling**: Both support parallel function calls
- **Compositional calling**: Gemini: native sequential chaining | OpenAI: no equivalent
- **Auto calling**: Gemini: Python SDK auto-execution | OpenAI: no SDK auto-execution
- **Function IDs**: Gemini: `id` field for async mapping | OpenAI: `tool_call_id`
- **Modes**: Gemini: AUTO/ANY/NONE/VALIDATED | OpenAI: auto/required/none
- **MCP**: Gemini: native SDK support | OpenAI: native SDK support
- **Built-in combo**: Gemini: custom functions + Google Search + Code Execution | OpenAI: separate tools

### vs Anthropic

- **Declaration format**: Gemini: `functionDeclarations` | Anthropic: `tools[].input_schema`
- **Parallel calling**: Gemini: yes with IDs | Anthropic: sequential (one call per turn)
- **Compositional calling**: Gemini: native chaining | Anthropic: no equivalent
- **Auto calling**: Gemini: Python SDK | Anthropic: no auto-execution
- **Modes**: Gemini: 4 modes | Anthropic: auto/any/tool (similar)
- **MCP**: Both support MCP (Anthropic created MCP standard)
- **Multimodal responses**: Gemini: functions can return images/media | Anthropic: text only

## Error Responses

- **400**: Invalid function declaration schema, too many declarations
- Deeply nested schemas in ANY mode may be rejected
- Function call parts mixed with text/tool parts - iterate through parts array

## Rate Limiting / Throttling

Standard Gemini API rate limits apply. Function calling rounds count as separate requests. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Only OpenAPI schema subset supported for parameters (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] ANY mode may reject complex schemas (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Automatic function calling is Python SDK only (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] functionCall may not be last item in parts array when using built-in tools (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Built-in MCP support is EXPERIMENTAL - breaking changes expected in future releases (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] MCP: only tools supported, NOT resources nor prompts (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] MCP: only available in Python and JavaScript/TypeScript SDKs (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Supported parameter types in Python SDK are limited for auto function schema (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Multimodal function responses supported - functions can return images/media as results (GEMAPI-SC-GOOG-FUNCAL)

## Gotchas and Quirks

- `functionCall` may NOT be the last part when combining with built-in tools - always iterate parts array
- With built-in tools, response contains mixed `functionCall`, `toolCall`, and `toolResponse` parts - never assume position
- Automatic function calling handles the loop but requires Python SDK; REST requires manual orchestration
- Compositional calling happens automatically - no special configuration needed
- Function IDs enable async execution and out-of-order result returns
- VALIDATED mode is in preview and may change
- MCP tools appear alongside custom functions in the same tools array
- MCP is EXPERIMENTAL - manual MCP server integration is always an option if built-in limits apply
- For ANY mode, simplify schemas if rejected: shorten property names, reduce nesting, fewer declarations

## Sources

- GEMAPI-SC-GOOG-FUNCAL: https://ai.google.dev/gemini-api/docs/function-calling [VERIFIED]
- GEMAPI-SC-GOOG-TOOLCM: https://ai.google.dev/gemini-api/docs/tool-combination [VERIFIED]

## Document History

**[2026-03-20 06:40]**
- Added: MCP experimental status, MCP limitations (tools only, Python/JS only)
- Added: multimodal function responses, mixed part types warning, Python parameter type limits

**[2026-03-20 03:40]**
- Initial document created with full function calling documentation
