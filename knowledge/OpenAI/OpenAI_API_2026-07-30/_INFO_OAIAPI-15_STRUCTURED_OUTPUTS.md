# Structured Outputs

**Doc ID**: OAIAPI-IN15
**Goal**: Document JSON schema response formatting, text.format parameter, and strict mode
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Structured outputs force model responses into specific JSON schema format using text.format parameter in Responses API (response_format in Chat Completions). Three format types: json_schema (strict schema enforcement), json_object (valid JSON without schema), and text (default free-form). Strict mode (strict: true) uses constrained sampling to guarantee schema-compliant output - model output mathematically proven to match schema. Schema defined using JSON Schema specification. Strict mode requires additionalProperties: false on all objects, no anyOf/allOf/oneOf, and explicit required arrays. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-GSTRCT)

## Key Facts

- **Parameter**: text.format in Responses API [VERIFIED]
- **Format types**: json_schema, json_object, text [VERIFIED]
- **Strict mode**: Guarantees schema compliance via constrained sampling [VERIFIED]
- **Schema**: JSON Schema specification [VERIFIED]
- **Output**: JSON string in response.output[0].content[0].text [VERIFIED]

## Format Types

### json_schema

Strict schema enforcement:
```python
text={
    "format": {
        "type": "json_schema",
        "json_schema": {
            "name": "response",
            "schema": {
                "type": "object",
                "properties": {"answer": {"type": "string"}},
                "required": ["answer"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
}
```

### json_object

Valid JSON without schema:
```python
text={"format": {"type": "json_object"}}
```

### text

Default free-form text (no format constraint).

## Strict Mode

### Requirements

1. `additionalProperties: false` on all objects
2. `required` array for all required fields
3. No `anyOf`/`allOf`/`oneOf` (use single schema)
4. No `patternProperties` or `propertyNames`
5. Explicit types on all properties

### Benefits

- **Guaranteed compliance**: Output always matches schema
- **No validation needed**: Trust output structure
- **Reliable parsing**: JSON.parse never fails on structure
- **Type safety**: All types enforced

## JSON Schema Definition

### Supported Types

- **string**, **number**, **integer**, **boolean**, **array**, **object**, **null**, **enum**

### Nested Objects

```python
{
    "type": "object",
    "properties": {
        "person": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"],
            "additionalProperties": False
        }
    },
    "required": ["person"],
    "additionalProperties": False
}
```

### Arrays

```python
{
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["items"],
    "additionalProperties": False
}
```

## SDK Examples (Python)

### Basic Structured Output

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "Extract person info: John Smith is 30 years old, email: john@example.com"}
    ],
    text={
        "format": {
            "type": "json_schema",
            "json_schema": {
                "name": "person",
                "schema": {
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
    }
)

data = json.loads(response.output[0].content[0].text)
print(f"Name: {data['name']}, Age: {data['age']}, Email: {data.get('email')}")
```

### Nested Structure

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "Create a company profile for Acme Corp, founded 1999, CEO Alice Johnson"}
    ],
    text={
        "format": {
            "type": "json_schema",
            "json_schema": {
                "name": "company",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "founded": {"type": "integer"},
                        "ceo": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "title": {"type": "string"}
                            },
                            "required": ["name", "title"],
                            "additionalProperties": False
                        }
                    },
                    "required": ["name", "founded", "ceo"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    }
)

company = json.loads(response.output[0].content[0].text)
print(company)
```

### Array Output

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "List the top 5 programming languages with their primary use cases"}
    ],
    text={
        "format": {
            "type": "json_schema",
            "json_schema": {
                "name": "languages",
                "schema": {
                    "type": "object",
                    "properties": {
                        "languages": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "use_case": {"type": "string"}
                                },
                                "required": ["name", "use_case"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["languages"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    }
)

data = json.loads(response.output[0].content[0].text)
for lang in data["languages"]:
    print(f"{lang['name']}: {lang['use_case']}")
```

### Enum Validation

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "Classify this text as positive, negative, or neutral: 'This product is amazing!'"}
    ],
    text={
        "format": {
            "type": "json_schema",
            "json_schema": {
                "name": "sentiment",
                "schema": {
                    "type": "object",
                    "properties": {
                        "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                        "confidence": {"type": "number"}
                    },
                    "required": ["sentiment", "confidence"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    }
)

result = json.loads(response.output[0].content[0].text)
print(f"Sentiment: {result['sentiment']} ({result['confidence']*100}% confident)")
```

### JSON Object (No Schema)

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "Create a JSON object with any relevant information about Python programming"}
    ],
    text={"format": {"type": "json_object"}}
)

data = json.loads(response.output[0].content[0].text)
print(json.dumps(data, indent=2))
```

## Error Responses

- **400 Bad Request** - Invalid schema definition
- **Schema validation errors** - Strict mode prevents runtime errors

## Differences from Other APIs

- **vs Anthropic**: Anthropic has no equivalent, uses system prompts for structure
- **vs Gemini**: Gemini has response_mime_type for JSON, less strict
- **vs Response Format (legacy)**: text.format replaces response_format in Responses API

## Limitations and Known Issues

- **Strict mode restrictions**: No anyOf/allOf/oneOf schemas [VERIFIED]
- **Complex schemas**: Very complex schemas may impact latency [ASSUMED]
- **Schema size**: Large schemas count toward token limits [ASSUMED]

## Gotchas and Quirks

- **additionalProperties required**: Forget this and strict mode fails [VERIFIED]
- **Output is string**: Must JSON.parse the response content [VERIFIED]
- **Schema in input**: Schema definition counts toward input token limit [VERIFIED]

## TypeScript Examples

### JSON Schema Output

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Extract: John is 30 years old",
  text: {
    format: {
      type: "json_schema",
      name: "person",
      schema: {
        type: "object",
        properties: {
          name: { type: "string" },
          age: { type: "number" },
        },
        required: ["name", "age"],
        additionalProperties: false,
      },
      strict: true,
    },
  },
});

const data = JSON.parse(response.output_text);
console.log(`${data.name}, age ${data.age}`);
```

## Sources

- OAIAPI-SC-OAI-GSTRCT - Structured outputs guide
- OAIAPI-SC-OAI-RESCRT - POST Create a response

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 14:40]**
- Enriched: Full format types, schema definition, strict mode, SDK examples from 2026-03-20
- Updated: Model refs to gpt-5.5

**[2026-05-22 11:40]**
- Stub created
