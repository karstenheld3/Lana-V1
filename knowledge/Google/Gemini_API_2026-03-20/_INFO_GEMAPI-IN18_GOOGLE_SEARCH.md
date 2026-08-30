# INFO: Gemini API Grounding with Google Search

**Doc ID**: GEMAPI-IN18
**Goal**: Document Google Search grounding tool, groundingMetadata, citations, and search suggestions
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Grounding with Google Search is a built-in Gemini tool that enables the model to access real-time web information. When enabled via `{"googleSearch": {}}` in the tools array, the model automatically searches the web when needed and includes structured citation metadata in the response. The `groundingMetadata` object contains `webSearchQueries` (queries the model issued), `groundingChunks` (source URLs with titles), and `groundingSupports` (text segments with source attributions and confidence scores). Google's Terms of Service require displaying search suggestions when using this feature. Grounding can be combined with other tools (Code Execution, URL Context, custom functions) in Gemini 3 models. This is unique to Gemini - OpenAI's web search and Anthropic's web search are conceptually similar but lack the structured citation metadata format.

## Key Facts

- [VERIFIED] Activation: `{"googleSearch": {}}` in tools array (GEMAPI-SC-GOOG-GRNDS)
- [VERIFIED] Response includes `groundingMetadata` with queries, chunks, supports (GEMAPI-SC-GOOG-GRNDS)
- [VERIFIED] Search suggestions widget required by ToS (GEMAPI-SC-GOOG-GRNDS)
- [VERIFIED] Combinable with other tools in Gemini 3 (GEMAPI-SC-GOOG-TOOLCM)

## Quick Reference

**Tool config**: `{"tools": [{"googleSearch": {}}]}`
**Response metadata**: `candidates[0].groundingMetadata`

## REST API

### Request

```json
{
  "contents": [{"parts": [{"text": "What are today's top tech news stories?"}]}],
  "tools": [{"googleSearch": {}}]
}
```

### Response with Grounding Metadata

```json
{
  "candidates": [{
    "content": {
      "parts": [{"text": "Here are today's top tech stories..."}],
      "role": "model"
    },
    "groundingMetadata": {
      "webSearchQueries": ["top tech news today 2026"],
      "groundingChunks": [
        {
          "web": {
            "uri": "https://example.com/tech-news",
            "title": "Top Tech News - March 2026"
          }
        }
      ],
      "groundingSupports": [
        {
          "segment": {
            "startIndex": 0,
            "endIndex": 120,
            "text": "Here are today's top tech stories..."
          },
          "groundingChunkIndices": [0],
          "confidenceScores": [0.95]
        }
      ],
      "searchEntryPoint": {
        "renderedContent": "<style>...</style><div>...</div>"
      }
    }
  }]
}
```

**groundingMetadata Fields:**
- **webSearchQueries** (array of string): Search queries the model issued
- **groundingChunks** (array): Source documents
  - **web.uri** (string): Source URL
  - **web.title** (string): Source page title
- **groundingSupports** (array): Text-to-source mappings
  - **segment** (object): Text range with startIndex, endIndex, text
  - **groundingChunkIndices** (array of int): Which chunks support this segment
  - **confidenceScores** (array of float): Confidence per supporting chunk
- **searchEntryPoint** (object): HTML/CSS for search suggestions widget (ToS required)

## Python Examples

### Example 1: Basic Grounding

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the current price of Bitcoin?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
)
print(response.text)

# Print sources
if response.candidates[0].grounding_metadata:
    gm = response.candidates[0].grounding_metadata
    print("\nSources:")
    for chunk in gm.grounding_chunks or []:
        print(f"  - {chunk.web.title}: {chunk.web.uri}")
    print(f"\nSearch queries: {gm.web_search_queries}")
```

### Example 2: Grounding with Citation Extraction

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Summarize recent advances in fusion energy research",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
)

text = response.text
gm = response.candidates[0].grounding_metadata

if gm and gm.grounding_supports:
    print("Response with inline citations:\n")
    for support in gm.grounding_supports:
        seg = support.segment
        sources = [gm.grounding_chunks[i].web.title
                   for i in support.grounding_chunk_indices]
        confidence = support.confidence_scores[0] if support.confidence_scores else 0
        print(f"[{confidence:.0%}] {seg.text[:100]}...")
        print(f"  Sources: {', '.join(sources)}\n")
```

## Comparison with Other APIs

### vs OpenAI

- **Tool name**: Gemini: `googleSearch` | OpenAI: `web_search` (in Responses API)
- **Citation format**: Gemini: structured `groundingMetadata` with segment offsets | OpenAI: annotations in content
- **Execution**: Gemini: single API call | OpenAI: Responses API with tool execution
- **Search widget**: Gemini: ToS-required HTML widget | OpenAI: no widget requirement
- **UNIQUE to Gemini**: Structured confidence scores per citation segment

### vs Anthropic

- **Tool name**: Gemini: `googleSearch` | Anthropic: `web_search` (server-side tool)
- **Citation format**: Gemini: `groundingMetadata` | Anthropic: search result content blocks
- **Execution**: Gemini: single call | Anthropic: multi-turn tool loop
- **UNIQUE to Gemini**: Google Maps grounding, search suggestions widget, segment-level confidence

## Error Responses

- Tool may return no grounding results if search yields nothing relevant
- groundingMetadata may be absent if model decided search was unnecessary

## Rate Limiting / Throttling

Google Search grounding may have additional rate limits beyond standard API limits. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Search suggestions widget HTML must be displayed per ToS (GEMAPI-SC-GOOG-GRNDS)
- Search results are real-time - responses are not reproducible
- Location and time in system_instruction may conflict with search tool (GEMAPI-SC-GOOG-TOOLCM)

## Gotchas and Quirks

- ToS requires rendering the `searchEntryPoint.renderedContent` HTML when displaying grounded responses
- Model may choose NOT to search even when tool is enabled (AUTO behavior)
- `groundingMetadata` only present when search was actually performed
- Conflicting location/time info in system instructions may cause tool combination issues
- No way to force search (unlike function calling ANY mode)

## Sources

- GEMAPI-SC-GOOG-GRNDS: https://ai.google.dev/gemini-api/docs/google-search [VERIFIED]
- GEMAPI-SC-GOOG-TOOLCM: https://ai.google.dev/gemini-api/docs/tool-combination [VERIFIED]

## Document History

**[2026-03-20 04:10]**
- Initial document created with grounding metadata schema and examples
