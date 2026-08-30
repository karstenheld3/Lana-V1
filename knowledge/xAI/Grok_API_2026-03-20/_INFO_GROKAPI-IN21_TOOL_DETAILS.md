# INFO: Tool Usage Details

**Doc ID**: GROKAPI-IN21
**Goal**: tool_calls vs server_side_tool_usage, billing, function name mapping, token patterns
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Tool usage tracking distinguishes between `tool_calls` (all attempted tool calls including failures) and `server_side_tool_usage` (only successful calls that are billed). The response exposes both fields. `tool_calls` contains individual call details (id, function.name, function.arguments). `server_side_tool_usage` is a map of usage categories to invocation counts (e.g., `{'SERVER_SIDE_TOOL_WEB_SEARCH': 3, 'SERVER_SIDE_TOOL_X_SEARCH': 2}`). Only successful executions are billed - failed attempts are not charged. Function names in tool_calls are granular (e.g., `x_keyword_search`, `browse_page`) while usage categories are high-level (e.g., `SERVER_SIDE_TOOL_WEB_SEARCH`). Agentic requests have unique token patterns: high reasoning tokens, high cached tokens across multiple tool calls within a session. [VERIFIED] (GROKAPI-SC-XAI-TOOLDETAILS | https://docs.x.ai/developers/tools/tool-usage-details)

## Key Facts

- [VERIFIED] `tool_calls`: All attempted calls (including failures) (GROKAPI-SC-XAI-TOOLDETAILS)
- [VERIFIED] `server_side_tool_usage`: Only successful (billable) calls (GROKAPI-SC-XAI-TOOLDETAILS)
- [VERIFIED] Failed tool attempts are NOT billed (GROKAPI-SC-XAI-TOOLDETAILS)
- [VERIFIED] Agentic system handles failures gracefully, continues with alternatives (GROKAPI-SC-XAI-TOOLDETAILS)

## Function Name to Usage Category Mapping

- **`SERVER_SIDE_TOOL_WEB_SEARCH`**: web_search, web_search_with_snippets, browse_page
- **`SERVER_SIDE_TOOL_X_SEARCH`**: x_user_search, x_keyword_search, x_semantic_search, x_thread_fetch
- **`SERVER_SIDE_TOOL_CODE_EXECUTION`**: code_execution
- **`SERVER_SIDE_TOOL_VIEW_X_VIDEO`**: view_x_video
- **`SERVER_SIDE_TOOL_VIEW_IMAGE`**: view_image
- **`SERVER_SIDE_TOOL_COLLECTIONS_SEARCH`**: collections_search
- **`SERVER_SIDE_TOOL_MCP`**: `{server_label}.{tool_name}` or `{tool_name}`

## Examples

### Inspecting Tool Usage

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Research AI safety trends on X and the web."}],
    tools=[{"type": "web_search"}, {"type": "x_search"}],
)

# All attempted calls (may include failures)
print(f"Tool calls: {len(response.tool_calls)}")
for tc in response.tool_calls:
    print(f"  {tc.function.name}: {tc.function.arguments[:80]}...")

# Successful calls only (determines billing)
print(f"Billable usage: {response.server_side_tool_usage}")
# e.g., {'SERVER_SIDE_TOOL_X_SEARCH': 3, 'SERVER_SIDE_TOOL_WEB_SEARCH': 2}
```

## Token Usage Patterns in Agentic Requests

- **High reasoning tokens**: Agent thinks through multi-step research (e.g., 3,000+ reasoning tokens)
- **High cached tokens**: Prompt cache reuse across multiple tool calls (e.g., 177K cached tokens)
- **Input tokens grow**: Each tool result adds to context

## Differences from Other APIs

### vs OpenAI
- **Unique**: `server_side_tool_usage` field with billing categories (OpenAI has no equivalent)
- **Granular function names**: xAI exposes internal sub-functions (x_keyword_search, browse_page)
- **Billing transparency**: Clear separation of attempted vs successful calls

### vs Anthropic
- **Different model**: Anthropic has no server-side tools, so no equivalent tracking

## Sources

- GROKAPI-SC-XAI-TOOLDETAILS | https://docs.x.ai/developers/tools/tool-usage-details | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:00]**
- Initial document created with tool usage tracking, function name mapping, and billing details
