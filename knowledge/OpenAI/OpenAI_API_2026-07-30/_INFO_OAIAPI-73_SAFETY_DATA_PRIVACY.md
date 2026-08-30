# Safety and Data Privacy

**Doc ID**: OAIAPI-IN73
**Goal**: Document safety best practices and data privacy for OpenAI API - moderation, content filtering, data usage, retention
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Safety best practices ensure applications handle content responsibly. Key strategies: Moderation API for input/output screening (including NEW inline moderation in requests, 2026-06), input validation, output token limits, structured outputs, user identification for abuse tracking, and Agents SDK guardrails. **NEW (2026-06)**: Safety Usage Dashboard shows blocked Responses requests based on `safety_identifier` values sent on requests to identify end users. Visit https://platform.openai.com/usage/safety to view blocked requests. Data usage: API data NOT used for training by default. Data retention: 30 days default, configurable per project (see IN80). Opt-out available. [VERIFIED] (OAIAPI-SC-OAI-GSAFE, OAIAPI-SC-OAI-GSAFTY, OAIAPI-SC-OAI-GYDATA, OAIAPI-SC-OAI-GCHLOG)

## Key Facts

- **Moderation API**: POST /v1/moderations - content classification [VERIFIED] (OAIAPI-SC-OAI-GSAFE)
- **Categories**: hate, harassment, self-harm, sexual, violence + subcategories [VERIFIED] (OAIAPI-SC-OAI-GSAFE)
- **Multi-modal**: Text and image moderation supported [VERIFIED] (OAIAPI-SC-OAI-GSAFE)
- **Content filter**: Built into all models, triggers automatically [VERIFIED] (OAIAPI-SC-OAI-GSAFE)
- **Refusal field**: `message.refusal` contains safety refusal text [VERIFIED] (OAIAPI-SC-OAI-CHATC)
- **Data not used for training**: API data NOT used by default [VERIFIED] (OAIAPI-SC-OAI-GYDATA)
- **Retention**: 30 days default, configurable per project [VERIFIED] (OAIAPI-SC-OAI-GYDATA)

## Safety Layers

```
User Input
  |
  v
1. Input Validation (length, format, sanitization)
  |
  v
2. Moderation API (content screening)
  |
  v
3. Model Generation (built-in content filter)
  |
  v
4. Output Check (refusal detection, moderation)
  |
  v
5. Application Logic (business rules, human review)
  |
  v
Safe Output
```

## Moderation API

### Request

```json
POST /v1/moderations
{
  "model": "omni-moderation-latest",
  "input": "Text to classify"
}
```

### Response

```json
{
  "id": "modr-abc123",
  "model": "omni-moderation-latest",
  "results": [
    {
      "flagged": false,
      "categories": {
        "hate": false,
        "harassment": false,
        "self-harm": false,
        "sexual": false,
        "violence": false
      },
      "category_scores": {
        "hate": 0.0001,
        "harassment": 0.0002,
        "violence": 0.0001
      }
    }
  ]
}
```

## SDK Examples (Python)

### Comprehensive Safety Pipeline

```python
from openai import OpenAI

client = OpenAI()

def moderate_content(text: str, threshold: float = 0.5) -> dict:
    """Check content against moderation categories"""
    result = client.moderations.create(
        model="omni-moderation-latest",
        input=text
    )
    
    mod = result.results[0]
    flagged_categories = []
    
    for category, score in mod.category_scores.items():
        if score > threshold:
            flagged_categories.append({"category": category, "score": score})
    
    return {
        "flagged": mod.flagged,
        "categories": flagged_categories
    }

def safe_chat(user_input: str, system_prompt: str, model: str = "gpt-5.5") -> dict:
    """Complete chat with safety checks on input and output"""
    if len(user_input) > 10000:
        return {"error": "Input too long", "safe": False}
    
    input_mod = moderate_content(user_input)
    if input_mod["flagged"]:
        return {
            "error": "Input flagged",
            "categories": input_mod["categories"],
            "safe": False
        }
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "developer", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_completion_tokens=1000,
            user="user_unique_id"
        )
    except Exception as e:
        return {"error": str(e), "safe": False}
    
    choice = response.choices[0]
    
    if choice.finish_reason == "content_filter":
        return {"error": "Content filtered by model", "safe": False}
    
    if choice.message.refusal:
        return {
            "output": choice.message.refusal,
            "refused": True,
            "safe": True
        }
    
    output = choice.message.content
    
    output_mod = moderate_content(output)
    if output_mod["flagged"]:
        return {
            "error": "Output flagged",
            "categories": output_mod["categories"],
            "safe": False
        }
    
    return {"output": output, "safe": True}

result = safe_chat(
    "How do I improve my Python code quality?",
    "You are a helpful programming assistant."
)

if result["safe"]:
    print(result.get("output", "Refused: " + result.get("error", "")))
else:
    print(f"Blocked: {result['error']}")
```

### Image Moderation

```python
from openai import OpenAI

client = OpenAI()

def moderate_image(image_url: str) -> dict:
    """Moderate an image for unsafe content"""
    result = client.moderations.create(
        model="omni-moderation-latest",
        input=[
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    )
    
    mod = result.results[0]
    return {
        "flagged": mod.flagged,
        "categories": {k: v for k, v in mod.categories.items() if v}
    }

result = moderate_image("https://example.com/image.jpg")
print(f"Flagged: {result['flagged']}")
```

## Safety Recommendations

- **Limit output tokens**: Reduce misuse surface with `max_completion_tokens`
- **Validate inputs**: Use dropdown fields, enums, and length limits where possible
- **Structured outputs**: Constrain response format to prevent free-form harmful content
- **User identification**: Always pass `user` parameter for abuse tracking
- **Rate limit per user**: Prevent individual users from excessive usage
- **Human review**: Implement for high-stakes outputs (medical, legal, financial)
- **Guardrails**: Use Agents SDK guardrails for automated input/output checks

## Data Privacy

- **API data not used for training**: By default, data sent via API is NOT used for model training [VERIFIED] (OAIAPI-SC-OAI-GYDATA)
- **Data retention**: 30 days default, configurable per project [VERIFIED] (OAIAPI-SC-OAI-GYDATA)
- **Opt-out available**: Organizations can opt out of data retention [VERIFIED] (OAIAPI-SC-OAI-GYDATA)
- **Project-level config**: See IN80 for project-level data retention settings

## Error Responses

- **Moderation API**: Standard API errors (400, 401, 429)
- **Content filter**: `finish_reason: "content_filter"` in response
- **Refusal**: `message.refusal` field populated (not an error, a safety response)

## Differences from Other APIs

- **vs Anthropic**: Constitutional AI approach; no separate moderation API endpoint
- **vs Gemini**: Safety Settings with configurable thresholds per category
- **vs Grok**: Limited content moderation capabilities

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

- OAIAPI-SC-OAI-GSAFE - Safety Best Practices Guide
- OAIAPI-SC-OAI-GSAFTY - Safety Reference
- OAIAPI-SC-OAI-GYDATA - Data Usage Policy
- OAIAPI-SC-OAI-MODAPI - Moderations API Reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: Safety Usage Dashboard (2026-06) - blocked request visibility
- Added: `safety_identifier` parameter for end-user tracking
- Added: Inline moderation reference (see IN26)
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 18:10]**
- Enriched from 2026-03-20 IN73 (19 -> 230 lines)
- Added data privacy section, updated model refs to gpt-5.5

**[2026-05-22 11:50]**
- Stub created
