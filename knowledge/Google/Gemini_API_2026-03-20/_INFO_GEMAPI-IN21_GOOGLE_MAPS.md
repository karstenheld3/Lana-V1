# INFO: Gemini API Grounding with Google Maps

**Doc ID**: GEMAPI-IN21
**Goal**: Document Google Maps grounding tool for location-based queries
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Grounding with Google Maps is a built-in Gemini tool that enables location-aware responses using Google Maps data. When enabled via `{"googleMaps": {}}` in the tools array, the model can access real-time location data including places, businesses, directions, reviews, and geographic information. The tool is server-side and executes within a single API call. Responses include structured location data with business names, addresses, ratings, and map references. This is unique to Gemini - neither OpenAI nor Anthropic offer native maps grounding. Combinable with other built-in tools in Gemini 3.

## Key Facts

- [VERIFIED] Activation: `{"googleMaps": {}}` in tools array (GEMAPI-SC-GOOG-GRNDS)
- [VERIFIED] Server-side Google Maps data access (GEMAPI-SC-GOOG-GRNDS)
- [VERIFIED] Returns structured location data with places, ratings, addresses (GEMAPI-SC-GOOG-GRNDS)
- [VERIFIED] UNIQUE to Gemini - no equivalent in OpenAI or Anthropic (GEMAPI-SC-GOOG-GRNDS)

## Quick Reference

**Tool config**: `{"tools": [{"googleMaps": {}}]}`

## Python Examples

### Example 1: Find Places

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Find the top-rated Italian restaurants near Times Square, New York",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_maps=types.GoogleMaps())]
    )
)
print(response.text)
```

### Example 2: Combined Search and Maps

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="I'm visiting Lisbon next week. Find the best seafood restaurants and tell me about the current weather there.",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(google_maps=types.GoogleMaps()),
            types.Tool(google_search=types.GoogleSearch()),
        ]
    )
)
print(response.text)
```

## Comparison with Other APIs

### vs OpenAI

- **Maps grounding**: Gemini: native Google Maps | OpenAI: **no equivalent**
- **UNIQUE to Gemini**: No other major LLM API offers built-in maps grounding

### vs Anthropic

- **Maps grounding**: Gemini: native Google Maps | Anthropic: **no equivalent**

## Error Responses

- Location queries that cannot be resolved may return text-only responses without map data

## Rate Limiting / Throttling

Standard rate limits plus potential Maps API usage considerations. See GEMAPI-IN04.

## Limitations and Known Issues

- Coverage depends on Google Maps data availability per region
- Business information may not be real-time (cached data)

## Gotchas and Quirks

- Model decides when to use Maps vs providing answer from training data
- Cannot force Maps usage (AUTO mode only)
- Location/time info in system instructions may conflict with Maps tool
- Maps ToS may require attribution for displayed results

## Sources

- GEMAPI-SC-GOOG-GRNDS: https://ai.google.dev/gemini-api/docs/grounding [VERIFIED]
- GEMAPI-SC-GOOG-TOOLCM: https://ai.google.dev/gemini-api/docs/tool-combination [VERIFIED]

## Document History

**[2026-03-20 04:25]**
- Initial document created
