# Web Search Tool

**Doc ID**: OAIAPI-IN14
**Goal**: Document web search tool configuration, search context, return_token_budget
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The web search tool enables models to search the internet for current information within Responses API calls. Configuration includes search context size, user location for localized results, and the `return_token_budget` parameter for opting into longer reasoning web search runs. **NEW (2026-06)**: Web search can now return image results alongside regular text results. Use image search when your application needs current or web-grounded visuals (product photos, landmarks, events, visual references). When enabled, the model autonomously decides when to search based on the query. Search results are billed as search content tokens. Available for GPT-5.6, GPT-5.5, GPT-5.4, and select mini models. [VERIFIED] (OAIAPI-SC-OAI-GWBSRC, OAIAPI-SC-OAI-GCHLOG)

## REST API

### Responses API with Web Search

**Endpoint**: `POST /v1/responses`

```json
{
  "model": "gpt-5.5",
  "input": "What are the latest developments in quantum computing?",
  "tools": [
    {
      "type": "web_search",
      "search_context_size": "medium",
      "user_location": {
        "type": "approximate",
        "country": "US"
      },
      "return_token_budget": 20000
    }
  ]
}
```

**Web Search Parameters**:

- **type** (string, required) - Always `"web_search"`
- **search_context_size** (string, optional) - Amount of search context: `"low"`, `"medium"`, `"high"`. Default: `"medium"`
- **user_location** (object, optional) - Location for localized results
  - **type**: `"approximate"`
  - **country**: ISO country code (e.g., `"US"`, `"DE"`)
  - **city**: City name (optional)
  - **region**: Region/state (optional)
- **return_token_budget** (integer, optional) - **[NEW 2026-05]** Token budget for extended reasoning search. Opt in to longer GPT-5.5+ reasoning web search runs for research and evaluation workloads. Higher values = more thorough but costlier searches.

## SDK Examples (Python)

### Basic Web Search

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="What happened in the tech industry today?",
    tools=[{"type": "web_search"}],
)
print(response.output_text)
```

### Extended Reasoning Search (NEW)

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Compare the performance characteristics of the latest GPU architectures for LLM inference workloads.",
    tools=[{
        "type": "web_search",
        "search_context_size": "high",
        "return_token_budget": 30000,
    }],
    reasoning={"effort": "high"},
)
print(response.output_text)
```

### Localized Search

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="What are the best restaurants near me?",
    tools=[{
        "type": "web_search",
        "user_location": {
            "type": "approximate",
            "country": "DE",
            "city": "Berlin",
        },
    }],
)
print(response.output_text)
```

## Pricing

- **Search content tokens**: Additional tokens retrieved from search index, billed at model's input token rate
- **return_token_budget**: Higher budgets increase token consumption and cost

## Gotchas and Quirks

- **return_token_budget**: Only effective with GPT-5.5+ models. Older models ignore it [VERIFIED]
- **Auto-trigger**: Model decides when to search. Cannot force a search [VERIFIED]
- **Cost variability**: Search-heavy queries can significantly increase token usage [VERIFIED]
- **Billing**: Search content tokens billed at special rate for some models [VERIFIED]

## TypeScript Examples

### Web Search Tool

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "What are the latest developments in AI?",
  tools: [{ type: "web_search_preview" }],
});

console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-GWBSRC - Web Search guide
- OAIAPI-SC-OAI-GCHLOG - Changelog (2026-05 - return_token_budget)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: Image results feature (2026-06) - web search returns images alongside text
- Updated: Model support to include GPT-5.6
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 10:40]**
- Updated from 2026-03-20 version
- Added: return_token_budget parameter (2026-05)
- Added: Extended reasoning search example
- Changed: Model references to GPT-5.5
