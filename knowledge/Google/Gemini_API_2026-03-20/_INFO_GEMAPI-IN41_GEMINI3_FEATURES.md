# INFO: Gemini 3 Model Features

**Doc ID**: GEMAPI-IN41
**Goal**: Document Gemini 3 series specific features, improvements over 2.5, and new capabilities
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini 3 is the latest model family introducing several architectural and capability improvements over Gemini 2.5. Key additions include: **thinkingLevel** (off/low/default/high) replacing integer thinkingBudget for simpler thinking control, **multi-tool combination** allowing built-in tools (Google Search, Code Execution, URL Context) and custom function calling to work together in a single request with context circulation, **Nano Banana Pro** (`gemini-3-pro-image-preview`) for high-quality native image generation, **Nano Banana 2** (`gemini-3.1-flash-image-preview`) for optimized speed image generation, **structured output with tools** (combine JSON schema with tool use), and **context engineering emphasis** (thought signature bypass: "context_engineering_is_the_way_to_go"). Gemini 3 Flash (`gemini-3-flash-preview`) and Gemini 3 Pro (`gemini-3-pro-preview`) are the primary models. The Flash-Lite variant provides a cost-optimized option for high-volume use cases.

## Key Facts

- [VERIFIED] Models: gemini-3-flash-preview, gemini-3-pro-preview, gemini-3-flash-lite-preview (GEMAPI-SC-GOOG-GEM3DV)
- [VERIFIED] thinkingLevel: off/low/default/high (GEMAPI-SC-GOOG-GEM3DV)
- [VERIFIED] Multi-tool combination: built-in + custom functions in one request (GEMAPI-SC-GOOG-GEM3DV)
- [VERIFIED] Nano Banana Pro/2: native image generation models (GEMAPI-SC-GOOG-GEM3DV)
- [VERIFIED] Structured output + tools combinable (GEMAPI-SC-GOOG-GEM3DV)
- [VERIFIED] Thought signature bypass: "context_engineering_is_the_way_to_go" (GEMAPI-SC-GOOG-GEM3DV)

## Model Variants

- **gemini-3-flash-preview**: Fast, cost-effective, best for most tasks
- **gemini-3-pro-preview**: Highest quality, best for complex reasoning
- **gemini-3-flash-lite-preview**: Lowest cost, optimized for high-volume simple tasks
- **gemini-3-pro-image-preview**: Nano Banana Pro (high-quality image generation)
- **gemini-3.1-flash-image-preview**: Nano Banana 2 (fast image generation)

## New Features in Gemini 3

### 1. thinkingLevel (Replaces thinkingBudget)

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Simple: off/low/default/high instead of integer budget
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high")
    ),
    contents="Prove that the square root of 2 is irrational"
)
print(response.text)
```

### 2. Multi-Tool Combination

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def save_to_database(data: str, table: str) -> dict:
    """Saves data to a database table.

    Args:
        data: JSON string of data to save.
        table: Target database table name.

    Returns:
        Dictionary with save status.
    """
    return {"status": "saved", "table": table, "rows": 1}

# Combine Google Search + Code Execution + custom function
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Search for the latest GDP data of G7 countries, calculate the average, and save it to the economics table.",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(code_execution=types.ToolCodeExecution()),
            save_to_database,
        ],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
    )
)
print(response.text)
```

### 3. Structured Output with Tools

```python
from google import genai
from google.genai import types
from pydantic import BaseModel
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

class ResearchResult(BaseModel):
    topic: str
    findings: list[str]
    sources: list[str]
    confidence: float

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        response_mime_type="application/json",
        response_json_schema=ResearchResult.model_json_schema(),
    ),
    contents="Research the current state of solid-state batteries"
)

result = ResearchResult.model_validate_json(response.text)
print(f"Topic: {result.topic}")
print(f"Confidence: {result.confidence:.0%}")
for finding in result.findings:
    print(f"  - {finding}")
```

### 4. Flash-Lite for High Volume

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Cost-optimized for classification, extraction, simple tasks
response = client.models.generate_content(
    model="gemini-3-flash-lite-preview",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="off"),
        response_mime_type="application/json",
        response_json_schema={
            "type": "object",
            "properties": {
                "category": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                "confidence": {"type": "number"}
            },
            "required": ["category", "confidence"]
        },
    ),
    contents="Classify: 'The product quality exceeded my expectations.'"
)
print(response.text)
```

## Gemini 3 vs Gemini 2.5

- **Thinking control**: 2.5: integer `thinkingBudget` | 3: string `thinkingLevel` (simpler)
- **Multi-tool**: 2.5: limited tool combination | 3: full multi-tool with context circulation
- **Structured + tools**: 2.5: not combined | 3: structured output works with tools
- **Image gen quality**: 2.5: Nano Banana | 3: Nano Banana Pro (higher quality) + Nano Banana 2 (faster)
- **Flash-Lite**: 2.5: Flash only | 3: Flash + Flash-Lite (cost tier)
- **Thought signatures**: 2.5: standard | 3: bypass string for strict validation

## Comparison with Other APIs

### vs OpenAI

- **Multi-tool combination**: Gemini 3: native in single call | OpenAI: Assistants API with tools
- **Thinking control**: Gemini 3: 4 levels | OpenAI: 3 levels (reasoning.effort)
- **Native image gen**: Gemini 3: in conversation model | OpenAI: separate DALL-E
- **Cost tiers**: Gemini 3: Pro/Flash/Flash-Lite | OpenAI: GPT-4o/GPT-4o-mini

### vs Anthropic

- **Multi-tool**: Gemini 3: multi-tool single call | Anthropic: one tool type per turn
- **Image generation**: Gemini 3: native | Anthropic: none
- **Cost tiers**: Gemini 3: 3 tiers | Anthropic: Opus/Sonnet/Haiku
- **Thinking**: Gemini 3: level-based | Anthropic: budget_tokens

## Error Responses

- **400**: Invalid thinkingLevel value, incompatible tool combination
- Preview models may have more restrictive rate limits

## Rate Limiting / Throttling

Preview models have separate rate limits. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] All Gemini 3 models are in preview (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] `gemini-3-pro-preview` has been SHUT DOWN - replaced by `gemini-3.1-pro-preview` (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Thought signature circulation is REQUIRED for Gemini 3 Flash even when set to minimal (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] Gemini 3 returns thought signatures for ALL part types, not just function calling (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] Nano Banana 2 (3.1 Flash Image): 4K output, 512px option, new aspect ratios 1:4/4:1/1:8/8:1 (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] Nano Banana 2 adds Google Search grounding for images (verify facts before generating) (GEMAPI-SC-GOOG-IMGGEN)
- [VERIFIED] Multi-tool context circulation may have edge cases (GEMAPI-SC-GOOG-TOOLCM)

## Gotchas and Quirks

- All Gemini 3 models are preview - API may change
- `gemini-3-pro-preview` was shut down fast - preview models can be short-lived, pin to specific versions
- `thinkingBudget` still works on Gemini 3 for backward compatibility but `thinkingLevel` is preferred
- Flash-Lite has reduced capabilities vs Flash - test for your use case
- Multi-tool results appear as mixed `functionCall`/`toolCall`/`toolResponse` parts - iterate all parts
- Thought signature bypass "context_engineering_is_the_way_to_go" needed for strict validation without real signatures
- Thought signatures MUST be circulated even at minimal level for Gemini 3 Flash - SDK handles this automatically
- Do NOT concatenate or merge parts with thought signatures - return entire response as-is
- Nano Banana is the internal code name for native image generation capability
- Gemini 3 image models have "thinking mode" for images - generates interim thought images (not charged)

## Sources

- GEMAPI-SC-GOOG-GEM3DV: https://ai.google.dev/gemini-api/docs/gemini-3 [VERIFIED]
- GEMAPI-SC-GOOG-MODELS: https://ai.google.dev/gemini-api/docs/models [VERIFIED]
- GEMAPI-SC-GOOG-TOOLCM: https://ai.google.dev/gemini-api/docs/tool-combination [VERIFIED]

## Document History

**[2026-03-20 07:35]**
- Fixed: types.CodeExecution() does not exist in SDK. Corrected to types.ToolCodeExecution()
- Source: google-genai v1.68.0, google/genai/types.py

**[2026-03-20 06:55]**
- Added: gemini-3-pro shutdown, 3.1-pro replacement, mandatory thought signatures for G3 Flash
- Added: Nano Banana 2 capabilities (4K, search grounding, new aspect ratios), image thinking mode

**[2026-03-20 06:05]**
- Initial document created with Gemini 3 features and comparisons
