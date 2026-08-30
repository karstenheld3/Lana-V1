# INFO: Web Search Tool

**Doc ID**: GROKAPI-IN15
**Goal**: Web search tool, domain filtering, image understanding from search, citations
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Web Search tool (`web_search`) enables Grok to search the internet and browse web pages during inference. It is a server-side tool that auto-executes on xAI servers. The model autonomously performs multiple searches and page browses as needed. Internally uses sub-functions: `web_search` (search query), `web_search_with_snippets` (search with previews), and `browse_page` (full page read). Supports domain filtering (`allowed_domains`/`excluded_domains`) and image understanding from search results (`enable_image_understanding`). Results include structured citations with source URLs. Billed at $5 per 1,000 invocations plus token costs. Available in all SDKs: `web_search` (xAI/OpenAI), `xai.tools.webSearch()` (Vercel AI SDK). [VERIFIED] (GROKAPI-SC-XAI-WEBSEARCH | https://docs.x.ai/developers/tools/web-search)

## Key Facts

- [VERIFIED] Tool name: `web_search` (GROKAPI-SC-XAI-WEBSEARCH)
- [VERIFIED] Server-side tool: auto-executes on xAI servers (GROKAPI-SC-XAI-WEBSEARCH)
- [VERIFIED] Sub-functions: web_search, web_search_with_snippets, browse_page (GROKAPI-SC-XAI-TOOLDETAILS)
- [VERIFIED] Usage category: `SERVER_SIDE_TOOL_WEB_SEARCH` (GROKAPI-SC-XAI-TOOLDETAILS)
- [VERIFIED] Invocation cost: $5 per 1,000 calls (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Domain filtering: `allowed_domains`/`excluded_domains` (GROKAPI-SC-XAI-WEBSEARCH)
- [VERIFIED] Image understanding from search results: `enable_image_understanding` (GROKAPI-SC-XAI-WEBSEARCH)

## Quick Reference

- **Tool type**: Server-side
- **Tool name**: `web_search`
- **Cost**: $5 / 1K invocations + token costs
- **Parameters**:
  - `allowed_domains` (array): Only search these domains
  - `excluded_domains` (array): Exclude these domains
  - `enable_image_understanding` (boolean): Analyze images in search results

## Examples

### Basic Web Search (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What are the latest developments in AI safety?"}],
    tools=[{"type": "web_search"}],
)
print(response.output_text)
```

### Domain Filtering

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What does the latest Python release include?"}],
    tools=[{
        "type": "web_search",
        "allowed_domains": ["python.org", "docs.python.org"],
    }],
)
```

### Combined Web + X Search

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What's the sentiment around the new iPhone launch?"}],
    tools=[
        {"type": "web_search"},
        {"type": "x_search"},
    ],
)
```

## Differences from Other APIs

### vs OpenAI
- **Server-side**: Auto-executes (OpenAI has no built-in web search in standard API; Assistants has file_search)
- **Domain filtering**: xAI supports allowed/excluded domains natively

### vs Gemini
- **Similar concept**: Gemini has `google_search_retrieval` grounding
- **Different API**: xAI uses tool array; Gemini uses grounding config

### vs Anthropic
- **UNIQUE**: Anthropic has no built-in web search tool

## Sources

- GROKAPI-SC-XAI-WEBSEARCH | https://docs.x.ai/developers/tools/web-search | Accessed: 2026-03-20
- GROKAPI-SC-XAI-TOOLDETAILS | https://docs.x.ai/developers/tools/tool-usage-details | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:35]**
- Initial document created with web search reference, domain filtering, and pricing
