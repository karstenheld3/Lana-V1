# Function Calling

**Doc ID**: OAIAPI-IN13
**Goal**: Document function calling with JSON schema, strict mode, tool_choice, and parallel calls
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI-IN12_TOOLS_OVERVIEW.md [OAIAPI-IN12]` for tools context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Function calling enables models to invoke developer-defined functions by generating structured JSON arguments matching function schema. Define functions with name, description, and JSON Schema parameters. Model determines when to call functions based on context, generates arguments as JSON string, and returns tool_call object. Developer executes function in application code, submits results back to API, and model uses results to generate final response. Strict mode enforces schema compliance with constrained sampling - output guaranteed to match schema exactly. Parallel function calls allow multiple invocations in single response. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-GFNCAL, OAIAPI-SC-OAI-GSTRCT)

## Key Facts

- **Schema format**: JSON Schema for parameter definition [VERIFIED]
- **Strict mode**: Guarantees schema-compliant output [VERIFIED]
- **Parallel calls**: Multiple functions invoked simultaneously [VERIFIED]
- **tool_choice**: Control when functions called [VERIFIED]
- **Execution**: Developer executes, model doesn't run functions [VERIFIED]

## Function Definition Schema

### Required Fields

- **name**: Function identifier (letters, numbers, underscores)
- **description**: What the function does (helps model decide when to call)
- **parameters**: JSON Schema defining function arguments

### Optional Fields

- **strict**: Enable strict mode (boolean, default: false)

### Parameters Schema

Supported JSON Schema types:
- **string**, **number**, **integer**, **boolean**, **object**, **array**, **enum**, **null**

## Strict Mode

```python
{
    "type": "function",
    "function": {
        "name": "extract_data",
        "parameters": {...},
        "strict": True
    }
}
```

**Benefits:**
- Guaranteed compliance: Output matches schema exactly
- No validation needed: Trust model output structure
- Reliable parsing: JSON.parse never fails

**Restrictions:**
- All objects must have `additionalProperties: false`
- All required fields must be specified
- No `anyOf`, `allOf`, `oneOf` (use single schema)

## Function Calling Flow

1. **Define function** with schema in tools array
2. **Model calls function** - returns tool_call with name and arguments (JSON string)
3. **Execute function** - parse arguments, run in your code
4. **Return result** - submit as tool role message with tool_call_id
5. **Model continues** - uses result to generate final response

### Tool Call Response Format

```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_user",
        "arguments": "{\"user_id\":\"12345\"}"
      }
    }
  ]
}
```

### Returning Results

```python
{
    "role": "tool",
    "tool_call_id": "call_abc123",
    "content": json.dumps(result)
}
```

## Parallel Function Calls

Model can call multiple functions simultaneously:

```json
{
  "tool_calls": [
    {"id": "call_1", "function": {"name": "get_weather", "arguments": "{\"location\":\"Paris\"}"}},
    {"id": "call_2", "function": {"name": "get_weather", "arguments": "{\"location\":\"London\"}"}},
    {"id": "call_3", "function": {"name": "get_weather", "arguments": "{\"location\":\"Tokyo\"}"}}
  ]
}
```

Execute all and return all results together.

## SDK Examples (Python)

### Basic Function Calling

```python
from openai import OpenAI
import json

client = OpenAI()

def get_current_weather(location: str, unit: str = "celsius"):
    return {"location": location, "temperature": 22, "unit": unit, "conditions": "Sunny"}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[{"role": "user", "content": "What's the weather like in Boston?"}],
    tools=tools
)

if hasattr(response.output[0], 'tool_calls'):
    tool_call = response.output[0].tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    result = get_current_weather(**arguments)
    
    final_response = client.responses.create(
        model="gpt-5.6-sol",
        input=[{
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        }]
    )
    print(final_response.output[0].content[0].text)
```

### Strict Mode Function

```python
from openai import OpenAI
import json

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_person",
            "description": "Extract person information",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "email": {"type": "string"}
                },
                "required": ["name", "age"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "Extract: John Smith is 30 years old, email: john@example.com"}
    ],
    tools=tools,
    tool_choice="required"
)

tool_call = response.output[0].tool_calls[0]
data = json.loads(tool_call.function.arguments)
print(f"Name: {data['name']}, Age: {data['age']}")
```

### Multiple Functions with Parallel Calls

```python
from openai import OpenAI
import json

client = OpenAI()

def get_weather(location):
    return f"Sunny in {location}"

def get_time(timezone):
    return f"Current time in {timezone}: 14:30"

tools = [
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get current time for timezone",
            "parameters": {
                "type": "object",
                "properties": {"timezone": {"type": "string"}},
                "required": ["timezone"]
            }
        }
    }
]

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[{"role": "user", "content": "What's the weather and time in Tokyo?"}],
    tools=tools
)

if hasattr(response.output[0], 'tool_calls'):
    results = []
    for call in response.output[0].tool_calls:
        args = json.loads(call.function.arguments)
        if call.function.name == "get_weather":
            result = get_weather(args["location"])
        elif call.function.name == "get_time":
            result = get_time(args["timezone"])
        results.append({"role": "tool", "tool_call_id": call.id, "content": result})
    
    final = client.responses.create(model="gpt-5.6-sol", input=results)
    print(final.output[0].content[0].text)
```

### Production Function Handler

```python
from openai import OpenAI
import json
from typing import Callable, Dict

class FunctionHandler:
    def __init__(self):
        self.client = OpenAI()
        self.functions: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable):
        self.functions[name] = func
    
    def call_with_functions(self, prompt: str, tools: list):
        response = self.client.responses.create(
            model="gpt-5.6-sol",
            input=[{"role": "user", "content": prompt}],
            tools=tools
        )
        
        if hasattr(response.output[0], 'tool_calls'):
            tool_results = []
            for call in response.output[0].tool_calls:
                func = self.functions.get(call.function.name)
                if not func:
                    raise ValueError(f"Unknown function: {call.function.name}")
                args = json.loads(call.function.arguments)
                result = func(**args)
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result) if not isinstance(result, str) else result
                })
            
            final = self.client.responses.create(model="gpt-5.6-sol", input=tool_results)
            return final.output[0].content[0].text
        
        return response.output[0].content[0].text

# Usage
handler = FunctionHandler()
handler.register("get_weather", lambda location: f"Sunny in {location}")
result = handler.call_with_functions("What's the weather in Paris?", tools)
```

## Error Responses

- **400 Bad Request** - Invalid function schema or arguments
- **Parsing errors** - Malformed JSON in function arguments (strict mode prevents this)

## Differences from Other APIs

- **vs Anthropic Tools**: Similar structure, Anthropic uses `tools` array too
- **vs Gemini Function Calling**: Gemini uses `function_declarations`, similar concept
- **vs Legacy Functions**: Old `functions` array replaced by `tools` with `type: function`

## Limitations and Known Issues

- **No function execution**: Model only generates arguments, doesn't run functions [VERIFIED]
- **Strict mode limitations**: No complex schema features (anyOf, allOf, oneOf) [VERIFIED]
- **Description quality matters**: Poor descriptions reduce accuracy [ASSUMED]

## Gotchas and Quirks

- **Arguments as string**: function.arguments is JSON string, not object [VERIFIED]
- **Tool result must be string**: content field expects string, stringify objects [VERIFIED]
- **Parallel calls optional**: Model decides, not controllable [VERIFIED]

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

- OAIAPI-SC-OAI-GFNCAL - Function calling guide
- OAIAPI-SC-OAI-GSTRCT - Structured outputs guide
- OAIAPI-SC-OAI-GTOOLS - Tools overview

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 14:35]**
- Enriched: Full function schema, strict mode, calling flow, SDK examples, production handler from 2026-03-20
- Updated: Model refs to gpt-5.5

**[2026-05-22 11:40]**
- Stub created
