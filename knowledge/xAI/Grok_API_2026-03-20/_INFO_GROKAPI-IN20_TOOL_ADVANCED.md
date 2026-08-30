# INFO: Advanced Tool Usage

**Doc ID**: GROKAPI-IN20
**Goal**: Mixing server/client tools, multi-tool orchestration, images in context, multi-turn with tools
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Advanced tool usage covers patterns for mixing server-side and client-side tools, combining multiple tools in a single request, using images in tool context, and handling multi-turn conversations with tool state preservation. Server-side tools (web_search, x_search, code_execution, collections_search) can be freely combined with client-side function calling in the same request. The model autonomously orchestrates which tools to use and in what order. Multi-turn conversations with tools use `previous_response_id` to preserve agentic state including tool call history. Images can be passed in conversation context alongside tool-using requests. Structured outputs can be combined with tool use for typed extraction from search results. [VERIFIED] (GROKAPI-SC-XAI-TOOLADVANCED | https://docs.x.ai/developers/tools/advanced-usage)

## Key Facts

- [VERIFIED] Server-side and client-side tools can be mixed in same request (GROKAPI-SC-XAI-TOOLADVANCED)
- [VERIFIED] Model autonomously decides tool invocation order (GROKAPI-SC-XAI-TOOLADVANCED)
- [VERIFIED] Multi-turn preserves agentic state via previous_response_id (GROKAPI-SC-XAI-TOOLADVANCED)
- [VERIFIED] Images can be included in context with tool-using requests (GROKAPI-SC-XAI-TOOLADVANCED)
- [VERIFIED] Structured outputs work with tool results (GROKAPI-SC-XAI-STRUCTOUT)

## Key Patterns

### Pattern 1: Server + Client Tool Mix

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Find Bitcoin price and save it."}],
    tools=[
        {"type": "web_search"},  # Server-side
        {"type": "function", "name": "save_data", "description": "Save to DB",
         "parameters": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}}},
    ],
)
```

### Pattern 2: Multi-Turn Tool Conversations

```python
# Turn 1: Search and analyze
r1 = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Research quantum computing breakthroughs."}],
    tools=[{"type": "web_search"}, {"type": "x_search"}],
)

# Turn 2: Continue with preserved tool state
r2 = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    previous_response_id=r1.id,
    input=[{"role": "user", "content": "Now compare with classical computing limitations."}],
    tools=[{"type": "web_search"}, {"type": "code_execution"}],
)
```

### Pattern 3: Structured Output + Tools

```python
from pydantic import BaseModel, Field

class ResearchResult(BaseModel):
    title: str = Field(description="Research paper title")
    authors: str = Field(description="Paper authors")
    year: str = Field(description="Publication year")
    summary: str = Field(description="Brief summary")

response = client.responses.parse(
    model="grok-4.20-beta-latest-non-reasoning",
    input="Find the latest proof of the four color theorem.",
    tools=[{"type": "web_search"}],
    text_format=ResearchResult,
)
print(response.output_parsed)
```

## Differences from Other APIs

### vs OpenAI
- **Compatible patterns**: Same multi-turn and function calling patterns
- **Server-side mixing**: xAI can mix built-in search tools with function calling natively

### vs Anthropic
- **Different model**: Anthropic uses tool_use blocks with separate turn handling
- **No server-side tools**: Anthropic has no built-in search/code tools to mix

## Sources

- GROKAPI-SC-XAI-TOOLADVANCED | https://docs.x.ai/developers/tools/advanced-usage | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:55]**
- Initial document created with advanced tool patterns and examples
