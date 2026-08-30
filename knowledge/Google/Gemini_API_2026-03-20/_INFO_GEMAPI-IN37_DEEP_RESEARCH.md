# INFO: Gemini API Deep Research

**Doc ID**: GEMAPI-IN37
**Goal**: Document the Deep Research model for autonomous multi-step research tasks
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini Deep Research (`gemini-2.5-pro-deep-research`) is a specialized model that autonomously conducts multi-step web research to produce comprehensive reports. Given a research query, the model creates a research plan, executes multiple web searches, synthesizes findings, and produces a detailed structured report with citations. The process is asynchronous - the model may take several minutes to complete research. Deep Research leverages Google Search grounding internally and produces reports that include source attributions. This is accessed via the standard `generateContent` endpoint with the deep research model. The model autonomously decides search queries, evaluates sources, and iterates until satisfied with coverage. This is unique to Gemini - neither OpenAI nor Anthropic offer an equivalent autonomous research model through their APIs.

## Key Facts

- [VERIFIED] Model: `gemini-2.5-pro-deep-research` (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Autonomous multi-step web research (GEMAPI-SC-GOOG-DEEPRS)
- [VERIFIED] Produces structured reports with citations (GEMAPI-SC-GOOG-DEEPRS)
- [VERIFIED] Asynchronous - may take minutes (GEMAPI-SC-GOOG-DEEPRS)
- [VERIFIED] UNIQUE to Gemini - no equivalent in OpenAI or Anthropic (GEMAPI-SC-GOOG-DEEPRS)

## Quick Reference

**Model**: `gemini-2.5-pro-deep-research`
**Endpoint**: Standard `generateContent`
**Duration**: Minutes (autonomous research)
**Output**: Structured report with citations

## Python Examples

### Example 1: Basic Deep Research

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-pro-deep-research",
    contents="Research the current state of quantum computing hardware. Compare approaches from IBM, Google, and IonQ. Include recent breakthroughs and remaining challenges.",
    config=types.GenerateContentConfig(
        temperature=0.3,
    )
)

print(response.text)
print(f"\nTokens used: {response.usage_metadata.total_token_count}")
```

### Example 2: Streaming Deep Research

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

for chunk in client.models.generate_content_stream(
    model="gemini-2.5-pro-deep-research",
    contents="What are the latest advances in CRISPR gene editing therapy? Focus on clinical trials approved in 2025-2026."
):
    if chunk.text:
        print(chunk.text, end="", flush=True)
print()
```

## Comparison with Other APIs

### vs OpenAI

- **Deep research**: Gemini: dedicated model | OpenAI: deep research in ChatGPT (not API)
- **API access**: Gemini: available via API | OpenAI: ChatGPT-only feature (no API)
- **UNIQUE API advantage**: Gemini exposes deep research through the standard API

### vs Anthropic

- **Deep research**: Gemini: dedicated model | Anthropic: **no equivalent**

## Error Responses

- **429**: Rate limits are more restrictive for deep research model
- Long research may time out on very broad queries

## Rate Limiting / Throttling

Deep research model has restricted rate limits (preview). See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Preview status (GEMAPI-SC-GOOG-MODELS)
- Research quality depends on web availability of sources
- May take several minutes for comprehensive reports
- Cannot control which sources the model uses

## Gotchas and Quirks

- Uses standard generateContent endpoint but takes significantly longer
- Streaming shows research progress incrementally
- Queries should be specific and well-scoped for best results
- The model may produce very long outputs - set maxOutputTokens appropriately
- Cannot provide custom sources - model searches autonomously

## Sources

- GEMAPI-SC-GOOG-DEEPRS: https://ai.google.dev/gemini-api/docs/deep-research [VERIFIED]
- GEMAPI-SC-GOOG-MODELS: https://ai.google.dev/gemini-api/docs/models [VERIFIED]

## Document History

**[2026-03-20 05:45]**
- Initial document created
