# INFO: Gemini API Thinking / Reasoning

**Doc ID**: GEMAPI-IN10
**Goal**: Document thinking/reasoning configuration, thinkingBudget, thinkingLevel, and thought signatures
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini 2.5+ models include built-in "thinking" (reasoning) capabilities that are enabled by default. The model internally reasons through complex problems before generating a response, consuming additional "thinking tokens" that count toward billing. Two configuration mechanisms exist: `thinkingBudget` (Gemini 2.5 models, integer token count 0-24576) and `thinkingLevel` (Gemini 3 models, string values off/low/default/high). Setting budget to 0 or level to "off" disables thinking entirely. Thinking tokens appear in `usageMetadata.thoughtsTokenCount` in the response. Thought signatures enable continuity across multi-turn conversations and caching - they must be preserved and passed back in subsequent requests. Gemini 3 requires a specific dummy string for thought signatures when bypassing strict validation. Higher thinking budgets increase response quality for complex tasks but increase latency and cost.

## Key Facts

- [VERIFIED] Thinking enabled by default on Gemini 2.5+ models (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] thinkingBudget: integer token count for Gemini 2.5 (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] thinkingLevel: off/low/default/high for Gemini 3 (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] Thought signatures for conversation/cache continuity (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] Thinking tokens reported in usageMetadata.thoughtsTokenCount (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Gemini 3 thought signature bypass: "context_engineering_is_the_way_to_go" (GEMAPI-SC-GOOG-GEM3DV)

## Use Cases

- **Complex reasoning**: Math, logic, coding problems benefit from higher thinking
- **Cost optimization**: Disable thinking for simple tasks to reduce token usage
- **Speed optimization**: Lower thinking budget for latency-sensitive applications
- **Conversation continuity**: Thought signatures maintain reasoning context across turns

## Quick Reference

**Gemini 2.5 Config**:
```json
{"generationConfig": {"thinkingConfig": {"thinkingBudget": 1024}}}
```

**Gemini 3 Config**:
```json
{"generationConfig": {"thinkingConfig": {"thinkingLevel": "high"}}}
```

## Configuration

### thinkingBudget (Gemini 2.5)

Controls the number of thinking tokens the model can use:
- **0**: Thinking disabled entirely
- **1-24576**: Token budget for internal reasoning
- **Default**: Model decides optimal budget based on task complexity

### thinkingLevel (Gemini 3)

String-based thinking control:
- **off**: No thinking
- **low**: Minimal thinking for simple tasks
- **default**: Standard thinking (model-determined)
- **high**: Maximum thinking for complex problems

### Thought Signatures

Thought signatures are opaque strings returned with thinking model responses that encode reasoning state. They must be preserved when:
- Continuing multi-turn conversations
- Using context caching with thinking content
- Replaying or resuming interactions

**Gemini 3 strict validation bypass**: When thought signatures are not available (e.g., testing), use the dummy string: `"context_engineering_is_the_way_to_go"`

## REST API

### Request with Thinking Config

```json
{
  "contents": [{"parts": [{"text": "Solve this math problem: ..."}]}],
  "generationConfig": {
    "thinkingConfig": {
      "thinkingBudget": 4096
    }
  }
}
```

### Response with Thinking Metadata

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {"text": "The answer is 42."}
        ],
        "role": "model"
      },
      "finishReason": "STOP"
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 50,
    "candidatesTokenCount": 10,
    "totalTokenCount": 560,
    "thoughtsTokenCount": 500
  }
}
```

Note: `thoughtsTokenCount` (500) + `candidatesTokenCount` (10) + `promptTokenCount` (50) = `totalTokenCount` (560). Thinking tokens are billed.

## Python Examples

### Example 1: Default Thinking (Enabled)

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the square root of 1764?"
)
print(response.text)
print(f"Thinking tokens: {response.usage_metadata.thoughts_token_count}")
print(f"Output tokens: {response.usage_metadata.candidates_token_count}")
print(f"Total tokens: {response.usage_metadata.total_token_count}")
```

### Example 2: Disable Thinking (Cost Savings)

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    ),
    contents="What color is the sky?"
)
print(response.text)
# thoughtsTokenCount should be 0
```

### Example 3: High Thinking Budget for Complex Tasks

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=8192)
    ),
    contents="Write a proof that there are infinitely many prime numbers."
)
print(response.text)
print(f"Thinking tokens used: {response.usage_metadata.thoughts_token_count}")
```

### Example 4: Gemini 3 Thinking Level

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high")
    ),
    contents="Solve: If a train travels at 120 km/h for 2.5 hours, then at 90 km/h for 1.75 hours, what is the average speed for the entire journey?"
)
print(response.text)
```

## cURL Examples

### Example 1: With Thinking Budget

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Explain the P vs NP problem"}]}],
    "generationConfig": {
      "thinkingConfig": {"thinkingBudget": 4096}
    }
  }'
```

### Example 2: Thinking Disabled

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Hello, how are you?"}]}],
    "generationConfig": {
      "thinkingConfig": {"thinkingBudget": 0}
    }
  }'
```

## Comparison with Other APIs

### vs OpenAI

- **Parameter**: Gemini: `thinkingBudget`/`thinkingLevel` | OpenAI: `reasoning.effort` (low/medium/high)
- **Granularity**: Gemini: integer token budget (fine-grained) | OpenAI: three discrete levels
- **Default**: Gemini 2.5+: thinking ON by default | OpenAI o-series: reasoning always on
- **Token reporting**: Gemini: `thoughtsTokenCount` | OpenAI: `completion_tokens_details.reasoning_tokens`
- **Thought signatures**: Gemini: explicit signature passing | OpenAI: no equivalent
- **Disable option**: Gemini: budget=0 or level=off | OpenAI: effort=low (reduced, not off)

### vs Anthropic

- **Parameter**: Gemini: `thinkingBudget`/`thinkingLevel` | Anthropic: `thinking.type: "enabled"` + `budget_tokens`
- **Granularity**: Both support integer token budget
- **Visibility**: Gemini: thinking content not returned | Anthropic: thinking blocks visible in response
- **Signatures**: Gemini: thought signatures for continuity | Anthropic: `thinking` blocks with `signature` field
- **Default**: Gemini: on by default | Anthropic: off by default (must enable)

## Error Responses

- **400**: Invalid thinkingBudget value (negative, exceeds max)
- Using `thinkingBudget` with Gemini 3 models works for backward compatibility but `thinkingLevel` is preferred

## Rate Limiting / Throttling

Thinking tokens count toward TPM rate limits. High thinking budgets consume more of your TPM quota per request. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Thinking enabled by default increases latency and cost on 2.5+ models (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] Thinking can consume all tokens hitting MAX_TOKENS before producing output (GEMAPI-SC-GOOG-THINKG)
- [COMMUNITY] thinkingBudget is a guide, not a hard limit - model may use fewer tokens (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] Gemini 2.5: thought signatures returned ONLY with function calling declarations (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] Gemini 3: thought signatures returned for ALL part types (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] Thought signature circulation is REQUIRED even when thinkingLevel set to minimal for Gemini 3 Flash (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] "Thought summaries" feature provides readable summaries of internal reasoning (GEMAPI-SC-GOOG-THINKG)

## Gotchas and Quirks

- Thinking is ON by default for 2.5+ - unexpected higher latency and cost vs older models
- Thinking tokens are billed but NOT visible in response content
- `thinkingBudget` is a **guide**, not a hard limit - model may use fewer or (rarely) more tokens
- Thinking can consume all available tokens, producing no output text (MAX_TOKENS finish reason)
- Must preserve thought signatures across turns for reasoning continuity
- Gemini 3 strict validation requires dummy signature string when real signatures unavailable
- Do NOT concatenate parts with signatures together - each signed part must remain separate
- Do NOT merge a part with a signature with another part without a signature
- Return the ENTIRE response with all parts back to the model in subsequent turns
- SDK handles signature circulation automatically - manual handling only for REST or modified history
- Gemini 2.5 vs 3 signature scope is different: 2.5 = function calling only, 3 = all parts

## Sources

- GEMAPI-SC-GOOG-THINKG: https://ai.google.dev/gemini-api/docs/thinking [VERIFIED]
- GEMAPI-SC-GOOG-GEM3DV: https://ai.google.dev/gemini-api/docs/gemini-3 [VERIFIED]
- GEMAPI-SC-GOOG-TROUBL: https://ai.google.dev/gemini-api/docs/troubleshooting [VERIFIED]

## Document History

**[2026-03-20 06:30]**
- Added: thought summaries feature, Gemini 3 Flash mandatory signature circulation
- Added: signature scope difference (2.5 vs 3), part merging prohibitions

**[2026-03-20 03:30]**
- Initial document created with thinking configuration and examples
