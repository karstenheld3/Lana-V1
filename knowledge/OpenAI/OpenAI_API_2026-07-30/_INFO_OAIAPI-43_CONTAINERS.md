# Containers API

**Doc ID**: OAIAPI-IN43
**Goal**: Document the Containers API for sandboxed execution environments used by Code Interpreter and Shell tools
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Containers API manages sandboxed virtual machines used by Code Interpreter and Shell tools. Containers provide isolated Python execution environments where models can run code, process files, and generate outputs. Create containers explicitly (`POST /v1/containers`) or automatically via `"container": {"type": "auto"}` in tool configuration. Memory tiers: 1g (default), 4g, 16g, 64g - selected at creation and fixed. Container IDs follow the `cntr_` prefix pattern. Containers persist until explicitly deleted or expired. Files can be uploaded via Container Files API. ZDR organizations cannot use hosted containers. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-CNTAPI, OAIAPI-SC-OAI-GCODEI)

## Key Facts

- **Purpose**: Sandboxed VMs for Code Interpreter and Shell tools [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **Memory tiers**: 1g (default), 4g, 16g, 64g [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **ID prefix**: `cntr_` [VERIFIED] (OAIAPI-SC-OAI-CNTAPI)
- **Creation modes**: Explicit (POST /v1/containers) or auto (tool config) [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **Memory is fixed**: Cannot change memory_limit after creation [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **ZDR restriction**: Not available for Zero Data Retention orgs [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **Persistence**: Containers persist until deleted or expired [VERIFIED] (OAIAPI-SC-OAI-GCODEI)

## Quick Reference

```
POST   /v1/containers                  # Create container
GET    /v1/containers/{container_id}    # Retrieve container
DELETE /v1/containers/{container_id}    # Delete container
GET    /v1/containers                   # List containers

Headers:
  Authorization: Bearer $OPENAI_API_KEY
  Content-Type: application/json
```

## Container Object

```json
{
  "id": "cntr_abc123",
  "object": "container",
  "name": "My Container",
  "created_at": 1699061776,
  "status": "active",
  "memory_limit": "4g",
  "metadata": {}
}
```

### Memory Tiers

- **1g**: Default tier. Sufficient for simple scripts, small datasets
- **4g**: Medium workloads. Moderate datasets, pandas operations
- **16g**: Large workloads. Large DataFrames, image processing
- **64g**: Maximum tier. Very large datasets, complex computations

## Operations

### Create Container

```
POST /v1/containers
```

**Request:**
```json
{
  "name": "Data Analysis Container",
  "memory_limit": "4g",
  "metadata": {
    "project": "quarterly_report"
  }
}
```

**Parameters:**
- **name** (optional): Human-readable name
- **memory_limit** (optional): "1g", "4g", "16g", or "64g" (default "1g")
- **metadata** (optional): Up to 16 key-value pairs

### Auto-Create via Tool Config

Instead of explicit creation, pass container config in the tool:

```json
{
  "type": "code_interpreter",
  "container": {
    "type": "auto",
    "memory_limit": "4g",
    "file_ids": ["file-abc123", "file-def456"]
  }
}
```

Auto mode creates a new container or reuses an active container from a previous `code_interpreter_call` item in the conversation context.

### Retrieve Container

```
GET /v1/containers/{container_id}
```

### Delete Container

```
DELETE /v1/containers/{container_id}
```

Permanently deletes the container and all files within it.

### List Containers

```
GET /v1/containers
```

**Query Parameters:**
- **limit** (optional): 1-100, default 20
- **order** (optional): `asc` or `desc`
- **after** (optional): Cursor for pagination

## Using with Code Interpreter

### Explicit Container

```json
{
  "model": "gpt-5.5",
  "tools": [
    {
      "type": "code_interpreter",
      "container": "cntr_abc123"
    }
  ],
  "input": "Analyze the data in the uploaded CSV file"
}
```

### Auto Container with Files

```json
{
  "model": "gpt-5.5",
  "tools": [
    {
      "type": "code_interpreter",
      "container": {
        "type": "auto",
        "memory_limit": "4g",
        "file_ids": ["file-abc123"]
      }
    }
  ],
  "input": "Create a bar chart from the sales data"
}
```

## Using with Shell Tool

```json
{
  "model": "gpt-5.5",
  "tools": [
    {
      "type": "shell",
      "container": "cntr_abc123"
    }
  ],
  "input": "List all files in the working directory"
}
```

## SDK Examples (Python)

### Create and Use Container

```python
from openai import OpenAI

client = OpenAI()

# Create container with 4GB memory
container = client.containers.create(
    name="Data Analysis",
    memory_limit="4g"
)

print(f"Container: {container.id}")

# Use container with Code Interpreter
response = client.responses.create(
    model="gpt-5.6-sol",
    tools=[{
        "type": "code_interpreter",
        "container": container.id
    }],
    input="Calculate the first 20 Fibonacci numbers and plot them"
)

print(response.output_text)
```

### Upload Files and Analyze

```python
from openai import OpenAI

client = OpenAI()

def analyze_data(file_path: str, question: str, memory: str = "4g") -> str:
    """Upload a file to a container and analyze it"""
    with open(file_path, "rb") as f:
        file = client.files.create(file=f, purpose="assistants")
    
    container = client.containers.create(
        name=f"Analysis: {file_path}",
        memory_limit=memory
    )
    
    client.containers.files.create(
        container_id=container.id,
        file_id=file.id
    )
    
    try:
        response = client.responses.create(
            model="gpt-5.6-sol",
            tools=[{
                "type": "code_interpreter",
                "container": container.id
            }],
            input=question
        )
        return response.output_text
    finally:
        client.containers.delete(container.id)

try:
    result = analyze_data(
        "sales_q4.csv",
        "Summarize the sales data. Show top 5 products by revenue."
    )
    print(result)
except Exception as e:
    print(f"Error: {e}")
```

### Auto Container with File Upload

```python
from openai import OpenAI

client = OpenAI()

with open("report.csv", "rb") as f:
    file = client.files.create(file=f, purpose="assistants")

response = client.responses.create(
    model="gpt-5.6-sol",
    tools=[{
        "type": "code_interpreter",
        "container": {
            "type": "auto",
            "memory_limit": "4g",
            "file_ids": [file.id]
        }
    }],
    tool_choice="required",
    input="Create a summary report with charts from the uploaded data"
)

for item in response.output:
    if item.type == "code_interpreter_call":
        print(f"Container used: {item.container_id}")

print(response.output_text)
```

## Error Responses

- **400 Bad Request** - Invalid memory_limit value
- **404 Not Found** - Container not found
- **403 Forbidden** - ZDR organization cannot use containers
- **429 Too Many Requests** - Rate limit exceeded

## Rate Limiting

- **Container creation**: Standard API rate limits
- **Concurrent containers**: Limited per organization
- **Execution time**: Container code execution has timeout limits
- **Billing**: Per-minute with 5-minute minimum (changed 2026-06-02; previously 20-minute flat rate). Higher memory tiers cost more per minute.

## Differences from Other APIs

- **vs Anthropic**: Anthropic has no sandboxed execution environment API
- **vs Gemini**: Gemini Code Execution runs in Google's infrastructure but no explicit container management API
- **vs Grok**: Grok has no code execution/container API
- **vs AWS Lambda/Cloud Run**: OpenAI containers are AI-integrated; cloud services are general-purpose

## Limitations and Known Issues

- **Python only**: Code Interpreter runs Python; no other languages [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **No network access**: Containers are sandboxed with no internet [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **Memory fixed**: Cannot resize after creation [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **ZDR incompatible**: Hosted containers not available for ZDR organizations [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **Pre-installed packages only**: Cannot pip install arbitrary packages [ASSUMED]

## Gotchas and Quirks

- **Auto reuse**: Auto containers reuse active containers from previous code_interpreter_call items in context [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **Container ID in output**: Find auto-created container_id in the code_interpreter_call output item [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **Shell + ZDR**: Shell tool also uses containers, same ZDR restriction applies [VERIFIED] (OAIAPI-SC-OAI-GCODEI)
- **MAM instead of ZDR**: Hosted containers use Modified Abuse Monitoring instead of ZDR [VERIFIED] (OAIAPI-SC-OAI-GCODEI)

## TypeScript Examples

### Client Setup and Basic Usage

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  organization: process.env.OPENAI_ORG_ID,
});

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Hello!",
});
console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-CNTAPI - Containers API (create, retrieve, delete, list)
- OAIAPI-SC-OAI-GCODEI - Code Interpreter Guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Changed: Billing model updated to per-minute with 5-min minimum (2026-06-02)
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 16:45]**
- Enriched from 2026-03-20 IN43 (19 -> 295 lines)
- Updated model references to gpt-5.5

**[2026-05-22 11:45]**
- Stub created
