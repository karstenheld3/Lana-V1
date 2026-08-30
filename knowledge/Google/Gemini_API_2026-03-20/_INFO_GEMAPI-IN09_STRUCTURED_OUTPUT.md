# INFO: Gemini API Structured Output

**Doc ID**: GEMAPI-IN09
**Goal**: Document JSON mode, responseSchema, responseMimeType, and supported JSON Schema subset
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini API structured output constrains model responses to conform to a JSON Schema, producing syntactically valid JSON strings. Activation requires setting `responseMimeType` to `application/json` and providing `responseSchema` (or `response_json_schema` in SDK) in `generationConfig`. The schema supports a subset of JSON Schema: types `string`, `number`, `integer`, `boolean`, `object`, `array`, and `null` (via `{"type": ["string", "null"]}`). Descriptive properties `title` and `description` guide the model. Output key order matches schema key order. Pydantic models integrate natively with the Python SDK via `model_json_schema()`. Gemini 3 models support combining structured output with built-in tools (Google Search, URL Context, Code Execution). Streaming works with structured output. Very large or deeply nested schemas may be rejected. Unsupported JSON Schema features are silently ignored.

## Key Facts

- [VERIFIED] Activation: `responseMimeType: "application/json"` + `responseSchema` (GEMAPI-SC-GOOG-STRUCT)
- [VERIFIED] Supported types: string, number, integer, boolean, object, array, null (GEMAPI-SC-GOOG-STRUCT)
- [VERIFIED] Null via union: `{"type": ["string", "null"]}` (GEMAPI-SC-GOOG-STRUCT)
- [VERIFIED] Output key order matches schema key order (GEMAPI-SC-GOOG-STRUCT)
- [VERIFIED] `title` and `description` properties guide model output (GEMAPI-SC-GOOG-STRUCT)
- [VERIFIED] Pydantic integration via `model_json_schema()` (GEMAPI-SC-GOOG-STRUCT)
- [VERIFIED] Gemini 3: structured output combinable with built-in tools (GEMAPI-SC-GOOG-STRUCT)
- [VERIFIED] Unsupported JSON Schema features silently ignored (GEMAPI-SC-GOOG-STRUCT)

## Quick Reference

**Activation**: Set `generationConfig.responseMimeType` to `"application/json"` and provide `generationConfig.responseSchema`
**SDK**: Use `response_mime_type` and `response_json_schema` config parameters

## REST API

### Request (Structured Output)

```json
{
  "contents": [{"parts": [{"text": "Extract info about Paris"}]}],
  "generationConfig": {
    "responseMimeType": "application/json",
    "responseSchema": {
      "type": "object",
      "properties": {
        "city_name": {
          "type": "string",
          "description": "Name of the city"
        },
        "country": {
          "type": "string",
          "description": "Country the city is in"
        },
        "population": {
          "type": "integer",
          "description": "Approximate population"
        },
        "landmarks": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Famous landmarks"
        },
        "is_capital": {
          "type": "boolean"
        },
        "mayor": {
          "type": ["string", "null"],
          "description": "Current mayor, null if unknown"
        }
      },
      "required": ["city_name", "country", "population", "landmarks"]
    }
  }
}
```

### Supported JSON Schema Subset

**Types:**
- `string` - Text values
- `number` - Floating-point numbers
- `integer` - Whole numbers
- `boolean` - true/false
- `object` - Key-value pairs with `properties`
- `array` - Lists with `items`
- `null` - Via union type: `{"type": ["string", "null"]}`

**Properties:**
- `type` (required): Data type
- `description`: Guides model output
- `title`: Short property description
- `properties`: Object property definitions
- `items`: Array item schema
- `required`: Required property names
- `enum`: Fixed set of allowed values

**NOT Supported (silently ignored):**
- `$ref` / `$defs` (schema references)
- `oneOf` / `anyOf` / `allOf` (composition)
- `additionalProperties`
- `pattern` (regex validation)
- `minimum` / `maximum` (numeric constraints)
- `minLength` / `maxLength` (string constraints)
- `minItems` / `maxItems` (array constraints)

## Python Examples

### Example 1: Pydantic Model

```python
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional
import os

class MovieReview(BaseModel):
    title: str = Field(description="Movie title")
    year: int = Field(description="Release year")
    rating: float = Field(description="Rating out of 10")
    genre: str = Field(description="Primary genre")
    summary: str = Field(description="Brief review summary")
    recommended: bool = Field(description="Whether to recommend")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=MovieReview.model_json_schema(),
    ),
    contents="Review the movie Inception (2010)"
)

review = MovieReview.model_validate_json(response.text)
print(f"{review.title} ({review.year}) - {review.rating}/10")
print(f"Genre: {review.genre}")
print(f"Recommended: {review.recommended}")
print(f"Summary: {review.summary}")
```

### Example 2: Enum Constrained Values

```python
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from enum import Enum
import os

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class SentimentResult(BaseModel):
    text: str
    sentiment: Sentiment
    confidence: float = Field(description="Confidence score 0.0-1.0")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=SentimentResult.model_json_schema(),
    ),
    contents='Analyze sentiment: "This product is amazing, I love it!"'
)

result = SentimentResult.model_validate_json(response.text)
print(f"Sentiment: {result.sentiment.value} ({result.confidence:.0%})")
```

### Example 3: Streaming with Structured Output

```python
from google import genai
from google.genai import types
import json
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

schema = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["name", "description"]
            }
        }
    },
    "required": ["items"]
}

full_json = ""
for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=schema,
    ),
    contents="List 5 programming languages with descriptions"
):
    full_json += chunk.text

data = json.loads(full_json)
for item in data["items"]:
    print(f"- {item['name']}: {item['description']}")
```

## cURL Examples

### Example: Structured Output

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Extract info about Python programming language"}]}],
    "generationConfig": {
      "responseMimeType": "application/json",
      "responseSchema": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "creator": {"type": "string"},
          "year_created": {"type": "integer"},
          "paradigms": {"type": "array", "items": {"type": "string"}},
          "typed": {"type": "boolean"}
        },
        "required": ["name", "creator", "year_created"]
      }
    }
  }'
```

## Comparison with Other APIs

### vs OpenAI

- **Activation**: Gemini: `responseMimeType` + `responseSchema` | OpenAI: `response_format: {type: "json_schema", json_schema: {...}}`
- **Schema location**: Gemini: in `generationConfig` | OpenAI: in `response_format`
- **Schema subset**: Both support subsets of JSON Schema (different subsets)
- **Key ordering**: Gemini: matches schema order | OpenAI: no ordering guarantee
- **Tool combination**: Gemini 3: structured output + built-in tools | OpenAI: structured output + tools
- **Pydantic**: Gemini: `model_json_schema()` | OpenAI: `parse()` method with automatic parsing

### vs Anthropic

- **Activation**: Gemini: native JSON Schema | Anthropic: prompt-based or tool_use trick
- **Schema enforcement**: Gemini: guaranteed valid JSON | Anthropic: best-effort with tool_use
- **Native support**: Gemini: first-class | Anthropic: JSON mode is more limited

## Error Responses

- **400**: Invalid or overly complex schema, unsupported responseMimeType
- Schema rejection does not specify which property caused the issue

## Rate Limiting / Throttling

Standard Gemini API rate limits apply. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Only JSON Schema subset supported; unsupported features silently ignored (GEMAPI-SC-GOOG-STRUCT)
- [VERIFIED] Very large or deeply nested schemas may be rejected (GEMAPI-SC-GOOG-STRUCT)

## Gotchas and Quirks

- Unsupported schema features are **silently ignored**, not rejected - model may not enforce constraints you expect
- Must set BOTH `responseMimeType` AND `responseSchema` - setting only one may produce unstructured JSON
- Pydantic `model_json_schema()` may produce features Gemini ignores (e.g., `$defs`) - test schemas
- Response is always a string (even with JSON mode) - must parse with `json.loads()` or Pydantic
- Streaming with structured output returns partial JSON fragments - must assemble before parsing

## Sources

- GEMAPI-SC-GOOG-STRUCT: https://ai.google.dev/gemini-api/docs/structured-output [VERIFIED]

## Document History

**[2026-03-20 03:25]**
- Initial document created with JSON schema support and Pydantic examples
