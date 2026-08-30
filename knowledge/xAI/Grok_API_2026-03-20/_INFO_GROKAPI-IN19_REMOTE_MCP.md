# INFO: Remote MCP Tools

**Doc ID**: GROKAPI-IN19
**Goal**: Remote MCP server integration, configuration, access control, multi-server support
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Remote MCP (Model Context Protocol) tools extend Grok's capabilities by connecting to external MCP tool servers. This is a **notable Grok feature** - native MCP integration directly in the API (Gemini has similar, OpenAI/Anthropic do not). MCP tools are server-side: Grok autonomously invokes them during inference. Configuration specifies MCP server URLs, authentication, and optionally a `server_label` for namespacing tool names. Multiple MCP servers can be used simultaneously. Access control allows restricting which tools are available. No per-invocation fee for MCP tools - billed for tokens only. Usage category in billing: `SERVER_SIDE_TOOL_MCP` with function names as `{server_label}.{tool_name}` or just `{tool_name}`. [VERIFIED] (GROKAPI-SC-XAI-REMOTEMCP | https://docs.x.ai/developers/tools/remote-mcp)

## Key Facts

- [VERIFIED] Native MCP integration in API (GROKAPI-SC-XAI-REMOTEMCP)
- [VERIFIED] Server-side execution: Grok invokes MCP tools during inference (GROKAPI-SC-XAI-REMOTEMCP)
- [VERIFIED] No invocation fee - token-based billing only (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Multi-server support (GROKAPI-SC-XAI-REMOTEMCP)
- [VERIFIED] Optional server_label for tool namespacing (GROKAPI-SC-XAI-TOOLDETAILS)
- [VERIFIED] Access control for restricting available tools (GROKAPI-SC-XAI-REMOTEMCP)

## Quick Reference

- **Tool type**: Server-side (MCP)
- **Cost**: Token-based only (no per-invocation fee)
- **Configuration**: MCP server URL + auth + optional label
- **Multi-server**: Yes
- **Usage category**: `SERVER_SIDE_TOOL_MCP`

## Examples

### Basic MCP Tool Usage (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Use the weather tool to get today's forecast for NYC."}],
    tools=[
        {
            "type": "mcp",
            "server_label": "weather",
            "server_url": "https://my-mcp-server.example.com/mcp",
            "headers": {"Authorization": "Bearer my-mcp-key"},
        },
    ],
)
print(response.output_text)
```

### Multiple MCP Servers

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Get weather for NYC and check my calendar for today."}],
    tools=[
        {
            "type": "mcp",
            "server_label": "weather",
            "server_url": "https://weather-mcp.example.com/mcp",
        },
        {
            "type": "mcp",
            "server_label": "calendar",
            "server_url": "https://calendar-mcp.example.com/mcp",
        },
        {"type": "web_search"},  # Can mix with other tool types
    ],
)
```

## Differences from Other APIs

### vs OpenAI
- **UNIQUE**: OpenAI has no native MCP integration in API (MCP is client-side only in OpenAI ecosystem)

### vs Anthropic
- **UNIQUE**: Anthropic has no native MCP in API (MCP is Claude Desktop/client-side only)

### vs Gemini
- **Similar**: Gemini has some MCP integration capability
- **Both server-side**: MCP tools execute server-side in both

## Sources

- GROKAPI-SC-XAI-REMOTEMCP | https://docs.x.ai/developers/tools/remote-mcp | Accessed: 2026-03-20
- GROKAPI-SC-XAI-TOOLDETAILS | https://docs.x.ai/developers/tools/tool-usage-details | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:45]**
- Initial document created with Remote MCP reference, multi-server examples
