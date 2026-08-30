# Web Search and Web Fetch Tools

**Doc ID**: ANTAPI-IN24
**Goal**: Document web search and web fetch server tools - configuration, parameters, and usage
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` for tool use architecture

## Summary

Web search and web fetch are server-side tools that execute on Anthropic's servers. Web search (`web_search_20250305`) performs real-time web searches and returns results with citations. Web fetch (`web_fetch_tool_20250910` / `web_fetch_tool_20260209` / `web_fetch_tool_20260309`) retrieves and processes web page content. Both tools run in the server-side sampling loop (up to 10 iterations) and may return `pause_turn` if the loop limit is reached.

## Key Facts

- **Web Search Type**: `web_search_20250305` / `web_search_20260209` / `web_search_20260318`
- **Web Fetch Type**: `web_fetch_tool_20250910` / `web_fetch_tool_20260209` / `web_fetch_tool_20260309` / `web_fetch_20260318`
- **Latest Versions**: `web_search_20260318` and `web_fetch_20260318` (with `response_inclusion`)
- **Execution**: Server-side (no client implementation needed)
- **Citations**: Automatic with `web_search_result_location` type
- **Max Iterations**: 10 per request (server sampling loop)
- **Pricing**: Additional per-search charges on top of token costs
- **Status**: GA

## Web Search Tool

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{"role": "user", "content": "What are the latest developments in quantum computing?"}],
)

for block in message.content:
    if hasattr(block, "text"):
        print(block.text)
    elif block.type == "web_search_tool_result":
        for result in block.content:
            if hasattr(result, "url"):
                print(f"Source: {result.url}")
```

### Web Search Parameters

- **type** (`string`, required) - `"web_search_20250305"`
- **name** (`string`, required) - `"web_search"`
- **max_uses** (`integer`, optional) - Maximum search invocations per request
- **cache_control** (`CacheControlEphemeral`, optional) - Prompt caching
- **hidden** (`boolean`, optional) - Exclude from system prompt
- **citations_config** (`CitationsConfigParam`, optional) - Citation configuration

## Web Fetch Tool

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[{"type": "web_fetch_tool_20260309", "name": "web_fetch"}],
    messages=[{"role": "user", "content": "Fetch and summarize https://example.com/article"}],
)
```

### Web Fetch Parameters

- **type** (`string`, required) - `"web_fetch_tool_20260309"` (latest version)
- **name** (`string`, required) - `"web_fetch"`
- **max_content_tokens** (`integer`, optional) - Max tokens for web page text content
- **max_uses** (`integer`, optional) - Maximum fetch invocations per request
- **allowed_domains** (`array[string]`, optional) - Whitelist of allowed domains
- **blocked_domains** (`array[string]`, optional) - Blacklist of blocked domains
- **use_cache** (`boolean`, optional) - Set false to bypass cache and fetch fresh content
- **citations_config** (`CitationsConfigParam`, optional) - Citation configuration

### Domain Filtering

```python
# Only allow specific domains
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[
        {
            "type": "web_fetch_tool_20260309",
            "name": "web_fetch",
            "allowed_domains": ["docs.python.org", "pypi.org"],
        }
    ],
    messages=[{"role": "user", "content": "Fetch the Python docs for asyncio"}],
)

# Block specific domains
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[
        {
            "type": "web_fetch_tool_20260309",
            "name": "web_fetch",
            "blocked_domains": ["example-blocked.com"],
        }
    ],
    messages=[{"role": "user", "content": "Fetch this article"}],
)
```

## Response Content Blocks

- **WebSearchToolResultBlock** - Contains search results with URLs, titles, content
- **WebSearchResultBlock** - Individual search result within a tool result
- **WebFetchToolResultBlock** - Fetched page content
- **WebFetchToolResultErrorBlock** - Fetch error (timeout, blocked, etc.)

## Handling pause_turn

```python
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{"role": "user", "content": "Research AI safety thoroughly"}],
)

while message.stop_reason == "pause_turn":
    messages = [
        {"role": "user", "content": "Research AI safety thoroughly"},
        {"role": "assistant", "content": message.content},
    ]
    message = client.messages.create(
        model="claude-opus-5",
        max_tokens=4096,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=messages,
    )
```

## Platform Availability

- Claude API (Anthropic) - supported
- Amazon Bedrock - **NOT available**
- Google Vertex AI - **NOT available**
- Microsoft Azure AI Foundry - check current availability

## Pricing

- **Web search**: Charged per search invocation on top of standard token costs
- **Web fetch**: Charged per fetch invocation on top of standard token costs
- **With code execution**: When web search or web fetch is in the request, code execution tool calls are free (no execution time charges)

## Gotchas and Quirks

- Web search incurs additional per-search charges beyond token costs
- Server sampling loop runs up to 10 iterations; handle `pause_turn` for complex queries
- `use_cache: false` on web fetch forces fresh content (useful for rapidly-changing sources)
- `max_content_tokens` on web fetch is approximate; does not apply to binary content like PDFs
- Web search results automatically include citations with `web_search_result_location` type
- Multiple tool versions exist; use the latest version for best results
- **Not available on Bedrock or Vertex AI**
- Server tools cannot be combined with `tool_choice: {type: "tool"}` forced selection

## Related Endpoints

- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` - Tool use architecture
- `_INFO_ANTAPI-17_CITATIONS.md [ANTAPI-IN17]` - Citation types including web search results
- `_INFO_ANTAPI-11_STOP_REASONS.md [ANTAPI-IN11]` - pause_turn handling

## Sources

- ANTAPI-SC-ANTH-WEBSRCH - https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool - Web search tool
- ANTAPI-SC-ANTH-WEBFTCH - https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool - Web fetch tool

## SDK Verification

All 4 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `types/web_search_tool_20250305_param.py`: `WebSearchTool20250305Param(type="web_search_20250305", name="web_search", max_uses?, allowed_domains?, blocked_domains?)`
- `types/web_fetch_tool_20260309_param.py`: `WebFetchTool20260309Param(type="web_fetch_tool_20260309", name="web_fetch", allowed_domains?, blocked_domains?, max_content_tokens?, use_cache?)`
- `types/tool_union_param.py`: Both web tool types included in `ToolUnionParam` union

**Notes**:
- SDK also includes `web_search_20260209` and `web_fetch_tool_20260209` versions
- `allowed_domains` and `blocked_domains` params confirmed on both web_search and web_fetch types

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: web_search_20260318 and web_fetch_20260318 versions with response_inclusion parameter
- Changed: Model references to claude-opus-5

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:40]**
- Added: SDK verification section (anthropic 0.120.0, all 4 examples valid)

**[2026-03-20 05:00]**
- Added: Platform availability (API only, NOT Bedrock/Vertex)
- Added: Pricing details (per-invocation charges, free code execution combo)
- Added: Server tool forced selection restriction

**[2026-03-20 03:45]**
- Initial documentation created from web search and web fetch tool guides
