# Programmatic Tool Calling

**Doc ID**: OAIAPI-IN94
**Goal**: Document Programmatic Tool Calling (PTC) - model-written JavaScript orchestration of tools in isolated V8 runtime
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API context
- `_INFO_OAIAPI-IN93_GPT56_LATEST_MODEL.md [OAIAPI-IN93]` for GPT-5.6 context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Overview

Programmatic Tool Calling (PTC) is a Responses API feature shipped with GPT-5.6 GA (2026-07-09). Instead of the traditional round-trip pattern where the model emits one tool call per turn, the model writes JavaScript that orchestrates multiple tool calls. The code executes in an isolated V8 runtime with no network access. Tools remain the only path to external systems.

PTC reduces token cost and latency for tool-heavy workflows by eliminating per-call round trips. Named customers report 38-63.5% token reductions on bounded multi-tool tasks.

## How It Works

1. Model receives prompt with `programmatic_tool_calling` tool enabled
2. Model writes JavaScript code that calls eligible tools in loops, conditionals, aggregations
3. V8 sandbox executes the code - tools are invoked via the sandbox interface
4. Results return to model as `program_output` items
5. Model produces final answer incorporating tool results

## REST API

### Enable Programmatic Tool Calling

Add `programmatic_tool_calling` to the tools array and mark eligible tools with `allowed_callers`:

**Endpoint**: `POST /v1/responses`

**Request**:

```json
{
  "model": "gpt-5.6-sol",
  "input": "Check the status of flights AA100, UA200, DL300 and tell me which are delayed.",
  "tools": [
    {
      "type": "programmatic_tool_calling"
    },
    {
      "type": "function",
      "name": "get_flight_status",
      "description": "Get current status of a flight by flight number",
      "parameters": {
        "type": "object",
        "properties": {
          "flight_number": {"type": "string"}
        },
        "required": ["flight_number"]
      },
      "allowed_callers": ["programmatic_tool_calling"]
    }
  ]
}
```

## SDK Examples

### Python

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Check flights AA100, UA200, DL300 and summarize which are delayed.",
    tools=[
        {"type": "programmatic_tool_calling"},
        {
            "type": "function",
            "name": "get_flight_status",
            "description": "Get current status of a flight by flight number",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_number": {"type": "string"}
                },
                "required": ["flight_number"],
            },
            "allowed_callers": ["programmatic_tool_calling"],
        },
    ],
)
print(response.output_text)
```

### Handling Program Items

When PTC is active, the response may contain `program` items and program-issued function calls. Preserve each call's `call_id` and `caller` linkage:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Aggregate inventory across 5 warehouses.",
    tools=[
        {"type": "programmatic_tool_calling"},
        {
            "type": "function",
            "name": "get_warehouse_inventory",
            "description": "Get inventory for a warehouse by ID",
            "parameters": {
                "type": "object",
                "properties": {"warehouse_id": {"type": "string"}},
                "required": ["warehouse_id"],
            },
            "allowed_callers": ["programmatic_tool_calling"],
        },
    ],
)

# Process output - program_output items contain aggregated results
for item in response.output:
    if item.type == "program_output":
        print(f"Program result: {item.content}")
    elif item.type == "message":
        print(f"Final answer: {item.content[0].text}")
```

## When to Use PTC

**Good fit (bounded workflows):**
- Filtering, joining, ranking, deduplication across multiple tool results
- Aggregation and validation of many parallel data sources
- Processing large intermediate outputs into smaller structured results

**Do NOT use PTC when:**
- One tool call is sufficient
- Intermediate outputs are already small
- Each result may change the model's next decision (requires judgment between steps)
- An action requires user approval
- Final output must preserve citations or native artifacts

## Security Model

- V8 sandbox: no network access, no filesystem, no system calls
- Tools are the ONLY exit path to external systems
- If a tool is not exposed, generated code cannot invoke it
- ZDR-compatible: no additional container costs

## Gotchas and Quirks

- Tool descriptions must document return fields, types, and error behavior precisely - model writes code against them
- Schema ambiguity becomes a bug repeated in a loop (PTC amplifies imprecise schemas)
- Multiple/parallel calls alone do not justify PTC - prefer direct calls when simple
- Do not rely on generic instructions like "use PTC efficiently" - explicitly state which stage uses PTC, which tools, output schema, concurrency limits

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

- https://developers.openai.com/api/docs/guides/programmatic-tool-calling
- https://openai.com/index/gpt-5-6/ (Launch announcement)
- OAIAPI-SC-OAI-GLATEST (Model guidance page)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Initial documentation for Programmatic Tool Calling
