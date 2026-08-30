# INFO: Gemini API URL Context

**Doc ID**: GEMAPI-IN20
**Goal**: Document URL Context tool for web page content extraction and grounding
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

URL Context is a built-in Gemini tool that fetches and processes web page content server-side when URLs are detected in prompts. When enabled via `{"urlContext": {}}` in the tools array, the model can extract and reason about content from provided URLs without the user needing to manually fetch or paste page content. The tool handles JavaScript-rendered content, follows redirects, and extracts meaningful text from web pages. This is unique to Gemini - OpenAI and Anthropic require users to provide page content manually or use separate scraping tools. URL Context can be combined with other built-in tools (Google Search, Code Execution) in Gemini 3 models.

## Key Facts

- [VERIFIED] Activation: `{"urlContext": {}}` in tools array (GEMAPI-SC-GOOG-URLCTX)
- [VERIFIED] Server-side web page fetching and content extraction (GEMAPI-SC-GOOG-URLCTX)
- [VERIFIED] Handles JS-rendered content (GEMAPI-SC-GOOG-URLCTX)
- [VERIFIED] Combinable with other tools in Gemini 3 (GEMAPI-SC-GOOG-TOOLCM)

## Quick Reference

**Tool config**: `{"tools": [{"urlContext": {}}]}`

## Python Examples

### Example 1: Analyze a Web Page

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Summarize the key points from this article: https://example.com/article",
    config=types.GenerateContentConfig(
        tools=[types.Tool(url_context=types.UrlContext())]
    )
)
print(response.text)
```

### Example 2: Compare Multiple URLs

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""Compare the pricing pages of these two services:
    - https://example1.com/pricing
    - https://example2.com/pricing
    Which offers better value for a small team?""",
    config=types.GenerateContentConfig(
        tools=[types.Tool(url_context=types.UrlContext())]
    )
)
print(response.text)
```

## Comparison with Other APIs

### vs OpenAI

- **URL processing**: Gemini: built-in URL Context tool | OpenAI: no equivalent (user must provide content)
- **UNIQUE to Gemini**: Server-side URL content extraction as a built-in tool

### vs Anthropic

- **URL processing**: Gemini: built-in URL Context | Anthropic: `web_fetch` server-side tool (similar)
- **JS rendering**: Both handle JavaScript-rendered content

## Error Responses

- URLs behind authentication or paywalls may fail silently (no content extracted)
- robots.txt restrictions may prevent access

## Rate Limiting / Throttling

Standard rate limits plus potential per-URL fetch latency. See GEMAPI-IN04.

## Limitations and Known Issues

- Cannot access authenticated/paywalled content
- May respect robots.txt restrictions
- Content extraction quality varies by site complexity

## Gotchas and Quirks

- Tool fetches content server-side - no user cookies or authentication applied
- Model may not fetch URL if it believes it already knows the answer
- URL must be in the prompt text - not in a separate parameter
- Latency increases with number of URLs (sequential fetching)

## Sources

- GEMAPI-SC-GOOG-URLCTX: https://ai.google.dev/gemini-api/docs/url-context [VERIFIED]
- GEMAPI-SC-GOOG-TOOLCM: https://ai.google.dev/gemini-api/docs/tool-combination [VERIFIED]

## Document History

**[2026-03-20 04:20]**
- Initial document created
