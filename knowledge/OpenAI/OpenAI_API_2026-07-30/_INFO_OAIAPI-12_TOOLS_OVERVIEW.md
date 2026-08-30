# Tools Overview

**Doc ID**: OAIAPI-IN12
**Goal**: Document tool types, built-in tools vs function calling, tool_choice parameter
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI API supports two categories of tools: built-in tools provided by OpenAI (web_search, file_search, code_interpreter, computer_use, hosted_shell, apply_patch, skills, mcp, tool_search, image_generation, local_shell, **programmatic_tool_calling** [NEW 2026-07]) and custom function calling where developers define functions. **NEW (2026-07)**: Programmatic Tool Calling lets GPT-5.6 write JavaScript to orchestrate multiple tool calls in an isolated V8 sandbox, reducing round-trips and tokens for tool-heavy workflows (see IN94). Tools extend model capabilities beyond text generation. The tool_choice parameter controls tool usage: "auto" (model decides), "required" (must use tools), "none" (no tools), or specific tool selection. Models can execute parallel tool calls in single response. Tool results must be provided back to model for response continuation. [VERIFIED] (OAIAPI-SC-OAI-GTOOLS, OAIAPI-SC-OAI-GFNCAL, OAIAPI-SC-OAI-GLATEST)

## Key Facts

- **Built-in tools**: web_search, file_search, code_interpreter, computer_use, hosted_shell, apply_patch, skills, mcp, tool_search, image_generation, local_shell, programmatic_tool_calling (NEW) [VERIFIED]
- **Programmatic Tool Calling**: Model-written JS orchestrates tools in V8 sandbox (GPT-5.6, NEW 2026-07) [VERIFIED]
- **Function calling**: Custom developer-defined functions [VERIFIED]
- **tool_choice**: Controls when/which tools used (auto, required, none, specific) [VERIFIED]
- **Parallel calls**: Model can invoke multiple tools simultaneously [VERIFIED]
- **Tool loop**: Call tool -> Execute -> Return result -> Model continues [VERIFIED]

## Built-In Tool Guides

- **Web search**: https://developers.openai.com/api/docs/guides/tools-web-search (IN14)
- **File search**: https://developers.openai.com/api/docs/guides/tools-file-search
- **Code interpreter**: https://developers.openai.com/api/docs/guides/tools-code-interpreter
- **Computer use**: https://developers.openai.com/api/docs/guides/tools-computer-use (IN65)
- **Shell (hosted)**: https://developers.openai.com/api/docs/guides/tools-shell
- **Local shell**: https://developers.openai.com/api/docs/guides/tools-local-shell (IN88)
- **Apply Patch**: https://developers.openai.com/api/docs/guides/tools-apply-patch (IN89)
- **Skills**: https://developers.openai.com/api/docs/guides/tools-skills (IN17)
- **MCP and Connectors**: https://developers.openai.com/api/docs/guides/tools-connectors-mcp (IN66)
- **Tool search**: https://developers.openai.com/api/docs/guides/tools-tool-search
- **Image generation (tool)**: https://developers.openai.com/api/docs/guides/tools-image-generation
- **Retrieval**: https://developers.openai.com/api/docs/guides/retrieval

## Tool Types

### Built-in Tools

- **file_search**: Search uploaded files in vector stores. RAG, document Q&A. Config: vector_store_ids, max_num_results
- **web_search**: Real-time web search. Current events, latest information. Config: max_results
- **code_interpreter**: Execute Python in sandbox. Data analysis, calculations, chart generation
- **tool_search**: Discover and use skills from Skills API. Dynamic tool discovery
- **computer_use**: Interact with computer interfaces. UI automation, testing, screenshots
- **hosted_shell**: Execute shell commands in hosted container
- **apply_patch**: Apply code patches to files in container
- **local_shell**: Execute shell commands locally (Agents SDK only, requires user consent)
- **skills**: Invoke pre-defined skills
- **mcp**: Connect to MCP servers
- **image_generation**: Generate images using GPT Image 2

### Function Calling

Developer-defined functions:
- Define function schema (name, description, parameters)
- Model decides when to call
- Execute function in your code
- Return results to model
- Model uses results in response

## tool_choice Parameter

- **auto** (default): Model decides whether to use tools
- **required**: Model must use at least one tool
- **none**: Disable all tools, text-only response
- **Specific tool**: `{"type": "function", "function": {"name": "get_weather"}}` forces that tool

## Tool Execution Flow

1. **Model decides**: Based on input, decides which tools to call
2. **Tool call returned**: Response includes tool_calls array
3. **Execute tools**: Developer executes requested functions
4. **Return results**: Submit tool results back to API
5. **Model continues**: Uses tool results to generate final response

## SDK Examples (Python)

### Using Built-in Tools

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "Search the web for latest AI news"}
    ],
    tools=[
        {"type": "web_search"}
    ]
)

print(response.output[0].content[0].text)
```

### Combining Multiple Built-in Tools

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "Search my documents and the web for quantum computing"}
    ],
    tools=[
        {
            "type": "file_search",
            "file_search": {
                "vector_store_ids": ["vs_abc123"]
            }
        },
        {"type": "web_search"}
    ]
)

print(response.output[0].content[0].text)
```

### Function Calling with tool_choice

```python
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get current time for timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string"}
                },
                "required": ["timezone"]
            }
        }
    }
]

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "What time is it in Tokyo?"}
    ],
    tools=tools,
    tool_choice="required"
)

print(response.output[0].content)
```

### Handling Parallel Tool Calls

```python
from openai import OpenAI
import json

client = OpenAI()

def execute_function(name: str, arguments: str):
    args = json.loads(arguments)
    if name == "get_weather":
        return f"Weather in {args['location']}: Sunny, 22C"
    return "Unknown function"

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "What's the weather in Paris, London, and Tokyo?"}
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for location",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"]
                }
            }
        }
    ]
)

tool_calls = response.output[0].tool_calls if hasattr(response.output[0], 'tool_calls') else []

if tool_calls:
    tool_results = []
    for call in tool_calls:
        result = execute_function(call.function.name, call.function.arguments)
        tool_results.append({
            "tool_call_id": call.id,
            "output": result
        })
    
    final_response = client.responses.create(
        model="gpt-5.6-sol",
        input=[
            {"role": "tool", "tool_call_id": tr["tool_call_id"], "content": tr["output"]}
            for tr in tool_results
        ]
    )
    
    print(final_response.output[0].content[0].text)
```

## Limitations and Model Support

- **GPT-5.4-nano**: Does NOT support computer_use, hosted_shell [VERIFIED]
- **computer_use**: GPT-5.4+ only, not GPT-5.4-nano [VERIFIED]
- **local_shell**: Agents SDK only, requires explicit user consent [VERIFIED]
- **tool_search**: Requires Skills API - only useful when many tools are defined [VERIFIED]
- **image_generation (tool)**: Uses GPT Image 2, subject to image rate limits [VERIFIED]
- **Max tools per request**: Limited number of tools in single request [ASSUMED]
- **Tool timeout**: Long-running tools may timeout [ASSUMED]

## Error Responses

- **400 Bad Request** - Invalid tool definition or tool_choice
- **404 Not Found** - Referenced vector store or skill not found
- **429 Too Many Requests** - Tool usage counts toward rate limits

## Differences from Other APIs

- **vs Anthropic Tools**: Similar concept, different tool types (no built-in web_search in Anthropic)
- **vs Gemini Tools**: Gemini has function calling, no equivalent to code_interpreter
- **vs Function Calling (legacy)**: tools array replaces functions array

## Gotchas and Quirks

- **tool_choice=required**: Does not guarantee tool - model still needs valid reason [ASSUMED]
- **Parallel calls optional**: Model decides whether to parallelize [VERIFIED]
- **Tool result format**: Must match expected structure or model fails [ASSUMED]

## TypeScript Examples

### Function Calling (Responses API)

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "What is the weather in Paris?",
  tools: [
    {
      type: "function",
      name: "get_weather",
      description: "Get current weather for a location",
      parameters: {
        type: "object",
        properties: { location: { type: "string" } },
        required: ["location"],
      },
    },
  ],
});

for (const item of response.output) {
  if (item.type === "function_call") {
    console.log(`Call: ${item.name}(${item.arguments})`);
  }
}
```

## Sources

- OAIAPI-SC-OAI-GTOOLS - Using tools guide
- OAIAPI-SC-OAI-GFNCAL - Function calling guide
- OAIAPI-SC-OAI-RESCRT - POST Create a response

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: Programmatic Tool Calling (GPT-5.6, 2026-07) as new built-in tool type
- Updated: Built-in tools list to include programmatic_tool_calling
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 14:30]**
- Enriched: Full tool types, tool_choice, execution flow, SDK examples, parallel calls from 2026-03-20
- Updated: Model refs to gpt-5.5
- Added: hosted_shell, apply_patch, local_shell, skills, mcp, image_generation tools

**[2026-05-22 13:20]**
- Expanded: All 12 tool sub-guide links, model support limitations

**[2026-05-22 11:40]**
- Stub created
