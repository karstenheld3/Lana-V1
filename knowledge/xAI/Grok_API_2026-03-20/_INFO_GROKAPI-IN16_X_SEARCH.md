# INFO: X Search Tool

**Doc ID**: GROKAPI-IN16
**Goal**: X (Twitter) search tool - handle filtering, date range, image/video understanding, citations
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references
- `_INFO_GROKAPI-IN13_TOOLS_OVERVIEW.md [GROKAPI-IN13]` for tools architecture

## Summary

X Search is a **UNIQUE Grok feature** (no equivalent in OpenAI, Anthropic, or Gemini APIs) that enables Grok to perform keyword search, semantic search, user search, and thread fetch on X (formerly Twitter). It provides real-time access to social media content including posts, user profiles, threads, images, and videos. The tool supports handle filtering (`allowed_x_handles` / `excluded_x_handles`, max 10 each, mutually exclusive), date range filtering (`from_date` / `to_date` in ISO8601), image understanding (`enable_image_understanding`), and video understanding (`enable_video_understanding`). It is a server-side tool that executes on xAI servers - the model autonomously decides when and how to search. Results include structured citations with post URLs. Available in all SDKs: `x_search` (xAI/OpenAI SDK), `xai.tools.xSearch()` (Vercel AI SDK). Incurs per-invocation cost beyond token billing. [VERIFIED] (GROKAPI-SC-XAI-XSEARCH | https://docs.x.ai/developers/tools/x-search)

## Key Facts

- [VERIFIED] Tool name: `x_search` (all SDKs) (GROKAPI-SC-XAI-XSEARCH)
- [VERIFIED] Server-side tool: executes on xAI servers, model decides invocations (GROKAPI-SC-XAI-XSEARCH)
- [VERIFIED] Capabilities: keyword search, semantic search, user search, thread fetch (GROKAPI-SC-XAI-XSEARCH)
- [VERIFIED] Handle filtering: `allowed_x_handles` (max 10), `excluded_x_handles` (max 10) (GROKAPI-SC-XAI-XSEARCH)
- [VERIFIED] Cannot use allowed and excluded handles in same request (GROKAPI-SC-XAI-XSEARCH)
- [VERIFIED] Date range: `from_date`/`to_date` in ISO8601 format (YYYY-MM-DD) (GROKAPI-SC-XAI-XSEARCH)
- [VERIFIED] Image understanding: `enable_image_understanding` parameter (GROKAPI-SC-XAI-XSEARCH)
- [VERIFIED] Video understanding: `enable_video_understanding` parameter (GROKAPI-SC-XAI-XSEARCH)
- [VERIFIED] Per-invocation billing (separate from token costs) (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Returns structured citations with post URLs (GROKAPI-SC-XAI-XSEARCH)

## Quick Reference

- **Tool type**: Server-side (auto-executes on xAI servers)
- **Tool name**: `x_search`
- **Parameters**:
  - `allowed_x_handles` (array, max 10): Only search these handles
  - `excluded_x_handles` (array, max 10): Exclude these handles
  - `from_date` (string, ISO8601): Search start date
  - `to_date` (string, ISO8601): Search end date
  - `enable_image_understanding` (boolean): Analyze images in posts
  - `enable_video_understanding` (boolean): Analyze videos in posts
- **Billing**: Per-invocation + token costs

## Examples

### Basic X Search (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[
        {"role": "user", "content": "What are people saying about xAI on X?"},
    ],
    tools=[
        {"type": "x_search"},
    ],
)

print(response.output_text)
```

### Handle Filtering - Include Specific Users

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What is the current status of xAI?"}],
    tools=[
        {
            "type": "x_search",
            "allowed_x_handles": ["elonmusk"],
        },
    ],
)
```

### Handle Filtering - Exclude Specific Users

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What is the current status of xAI?"}],
    tools=[
        {
            "type": "x_search",
            "excluded_x_handles": ["elonmusk"],
        },
    ],
)
```

### Date Range Filtering

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What happened with xAI in early October 2025?"}],
    tools=[
        {
            "type": "x_search",
            "from_date": "2025-10-01",
            "to_date": "2025-10-10",
        },
    ],
)
```

### With Image and Video Understanding

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Show me viral tech memes from this week on X"}],
    tools=[
        {
            "type": "x_search",
            "enable_image_understanding": True,
            "enable_video_understanding": True,
        },
    ],
)
```

### xAI SDK with Streaming

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.20-beta-latest-non-reasoning",
    tools=[x_search(allowed_x_handles=["elonmusk"])],
    include=["verbose_streaming"],
)

chat.append(user("What are the latest announcements from Elon Musk about xAI?"))

for response, chunk in chat.stream():
    for tool_call in chunk.tool_calls:
        print(f"\nSearching X: {tool_call.function.arguments}")
    if chunk.content:
        print(chunk.content, end="", flush=True)

print(f"\n\nCitations: {response.citations}")
```

### Vercel AI SDK

```typescript
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text, sources } = await generateText({
  model: xai.responses('grok-4.20-beta-latest-non-reasoning'),
  prompt: 'What are people saying about xAI on X?',
  tools: {
    x_search: xai.tools.xSearch({
      allowedXHandles: ['elonmusk'],
      fromDate: '2025-10-01',
      toDate: '2025-10-10',
    }),
  },
});

console.log(text);
console.log('Citations:', sources);
```

### cURL

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-4.20-beta-latest-non-reasoning",
    "input": [
      {"role": "user", "content": "What are people saying about xAI on X?"}
    ],
    "tools": [
      {
        "type": "x_search",
        "allowed_x_handles": ["elonmusk"],
        "from_date": "2025-10-01",
        "to_date": "2025-10-10"
      }
    ]
  }'
```

## Use Cases

- **Social media monitoring**: Track brand mentions, sentiment analysis
- **Trend analysis**: Research trending topics with date range filtering
- **Competitive intelligence**: Monitor competitor announcements
- **News gathering**: Real-time news from X posts
- **Public opinion research**: Analyze public discourse on topics
- **Influencer tracking**: Filter to specific handles for focused analysis

## Differences from Other APIs

### vs OpenAI

- **UNIQUE**: No X/Twitter search capability in OpenAI API
- **Closest**: OpenAI has no built-in social media search tool

### vs Anthropic

- **UNIQUE**: No X/Twitter search capability in Anthropic API
- **Closest**: Anthropic has no built-in search tools of any kind

### vs Gemini

- **UNIQUE**: Gemini has Google Search grounding but NO X/Twitter-specific search
- **Key advantage**: Direct access to X post data, user profiles, threads

### vs Web Search (Grok's own)

- **Specialized**: X Search targets X/Twitter specifically; web_search is general internet
- **Additional params**: Handle filtering, date range, image/video understanding from posts
- **Can combine**: Use both x_search and web_search in same request for comprehensive research

## Limitations and Known Issues

- [VERIFIED] Max 10 handles per allowed/excluded list (GROKAPI-SC-XAI-XSEARCH)
- [VERIFIED] Cannot use allowed_x_handles and excluded_x_handles simultaneously (GROKAPI-SC-XAI-XSEARCH)
- [VERIFIED] Image/video understanding incurs additional token costs (GROKAPI-SC-XAI-MODELS)

## Gotchas and Quirks

- Handle filtering is at the tool level, not per-query - set once for the entire request
- The model autonomously decides how many X searches to perform - complex queries may trigger multiple invocations
- Date filtering is inclusive of both from_date and to_date

## Sources

- GROKAPI-SC-XAI-XSEARCH | https://docs.x.ai/developers/tools/x-search | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:00]**
- Initial document created with full X Search reference, all parameters, and examples
