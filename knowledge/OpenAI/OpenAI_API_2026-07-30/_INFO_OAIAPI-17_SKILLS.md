# Skills API

**Doc ID**: OAIAPI-IN17
**Goal**: Document Skills API for reusable tool packages, versioning, and tool_search integration
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI-IN12_TOOLS_OVERVIEW.md [OAIAPI-IN12]` for tools context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Skills API provides reusable tool packages with versioning support. Create skills containing multiple function definitions, manage versions independently, and enable dynamic discovery via tool_search. CRUD operations: create (POST /v1/skills), retrieve (GET /v1/skills/{skill_id}), list (GET /v1/skills), delete (DELETE /v1/skills/{skill_id}). Each skill has name, description, functions array, and version. Versions are immutable once published. Content retrieval via GET /v1/skills/{skill_id}/versions/{version}/content. tool_search built-in tool enables models to discover and use skills dynamically. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-SKLAPI)

## Key Facts

- **Purpose**: Reusable tool packages with versioning [VERIFIED]
- **Operations**: Create, retrieve, list, delete skills [VERIFIED]
- **Versioning**: Immutable versions, create new for updates [VERIFIED]
- **Discovery**: tool_search enables dynamic skill discovery [VERIFIED]
- **Content**: Skills contain multiple function definitions [VERIFIED]

## Skill Object

```json
{
  "id": "skill_abc123",
  "object": "skill",
  "name": "weather_tools",
  "description": "Tools for weather information",
  "version": "1.0.0",
  "created_at": 1234567890,
  "functions": [
    {
      "name": "get_weather",
      "description": "Get current weather",
      "parameters": {...}
    }
  ]
}
```

**Fields:**
- **id**: Unique skill identifier
- **object**: Always "skill"
- **name**: Skill name (unique per account)
- **description**: What the skill does
- **version**: Semantic version (e.g., "1.0.0")
- **created_at**: Unix timestamp
- **functions**: Array of function definitions

## REST API Operations

### Create Skill

```
POST /v1/skills
```

### Retrieve Skill

```
GET /v1/skills/{skill_id}
```

### List Skills

```
GET /v1/skills
```

### Delete Skill

```
DELETE /v1/skills/{skill_id}
```

### Get Skill Content

```
GET /v1/skills/{skill_id}/versions/{version}/content
```

## Versioning

Semantic versioning: `MAJOR.MINOR.PATCH`. Versions are immutable once created - create new version for changes.

## tool_search Integration

```python
tools=[{"type": "tool_search"}]
```

Discovery process:
1. Model analyzes request, determines needed capabilities
2. Searches skills by name/description
3. Loads function definitions
4. Calls appropriate functions
5. Uses results in response

## SDK Examples (Python)

### Create Skill

```python
from openai import OpenAI

client = OpenAI()

skill = client.skills.create(
    name="calculation_tools",
    description="Mathematical calculation tools",
    version="1.0.0",
    functions=[
        {
            "name": "calculate",
            "description": "Perform mathematical calculation",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        },
        {
            "name": "convert_units",
            "description": "Convert between units",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "from_unit": {"type": "string"},
                    "to_unit": {"type": "string"}
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        }
    ]
)
print(f"Created skill: {skill.id}")
```

### Create Skill (SDK v2.45.0 verified)

```python
# SDK skills.create(files=...) accepts file upload, not name/functions directly
from openai import OpenAI
import json, tempfile, os

client = OpenAI()

skill_def = {
    "name": "calculation_tools",
    "description": "Mathematical calculation tools",
    "version": "1.0.0",
    "functions": [
        {
            "name": "calculate",
            "description": "Perform mathematical calculation",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        }
    ]
}

with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    json.dump(skill_def, f)
    tmp_path = f.name

try:
    skill = client.skills.create(files=open(tmp_path, "rb"))
    print(f"Created skill: {skill.id}")
finally:
    os.unlink(tmp_path)
```

### List and Retrieve Skills

```python
from openai import OpenAI

client = OpenAI()

skills = client.skills.list()
for skill in skills.data:
    print(f"{skill.name} v{skill.version}: {skill.description}")

skill = client.skills.retrieve("skill_abc123")
print(f"Functions: {len(skill.functions)}")
```

### Using Skills with tool_search

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "What's the weather in Seattle? Use available weather tools."}
    ],
    tools=[
        {"type": "tool_search"}
    ]
)

print(response.output[0].content[0].text)
```

### Version Management

```python
from openai import OpenAI

client = OpenAI()

# Create v1.0.0
skill_v1 = client.skills.create(
    name="data_tools",
    version="1.0.0",
    description="Data processing tools",
    functions=[{
        "name": "process_data",
        "description": "Process data",
        "parameters": {
            "type": "object",
            "properties": {"data": {"type": "array", "items": {"type": "string"}}}
        }
    }]
)

# Create v1.1.0 with new function
skill_v1_1 = client.skills.create(
    name="data_tools",
    version="1.1.0",
    description="Data processing tools with validation",
    functions=[
        {"name": "process_data", "description": "Process data", "parameters": {...}},
        {"name": "validate_data", "description": "Validate data format", "parameters": {...}}
    ]
)
```

### Delete Skill

```python
from openai import OpenAI
client = OpenAI()
client.skills.delete("skill_abc123")
```

## Error Responses

- **404 Not Found** - Skill or version does not exist
- **400 Bad Request** - Invalid skill definition
- **409 Conflict** - Skill name/version already exists

## Differences from Other APIs

- **vs Anthropic**: No equivalent skills system
- **vs Gemini**: No equivalent
- **vs OpenAI Plugins (legacy)**: Skills are API-level, not ChatGPT plugins

## Limitations and Known Issues

- **Limited documentation**: Relatively new API, docs sparse [VERIFIED]
- **tool_search reliability**: Discovery not always accurate [ASSUMED]
- **No skill marketplace**: No public skill sharing yet [ASSUMED]

## Gotchas and Quirks

- **Name must be unique**: Cannot have multiple skills with same name in account [VERIFIED]
- **Versions immutable**: Cannot edit existing versions [VERIFIED]
- **tool_search overhead**: Discovery adds latency vs direct function calling [ASSUMED]
- **SDK create method**: Uses files= param, not name/functions directly [VERIFIED]

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

- OAIAPI-SC-OAI-SKLAPI - Skills API reference
- OAIAPI-SC-OAI-GTOOLS - Tools overview (tool_search)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 14:45]**
- Enriched: Full skill object, REST API, versioning, SDK examples, tool_search integration from 2026-03-20
- Updated: Model refs to gpt-5.5
- Added: SDK v2.29.0 verified create method

**[2026-05-22 11:40]**
- Stub created
