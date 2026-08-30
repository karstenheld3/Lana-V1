# MCP: SDKs and Implementation Examples

**Doc ID**: MCP-IN08
**Goal**: Document SDK tiering system and practical implementation examples for TypeScript and Python
**Version scope**: Spec 2025-11-25 (current)

**Depends on:**
- `_INFO_MCP-05_ServerPrimitives.md [MCP-IN05]` for tools/resources/prompts context
- `_INFO_MCP-02_Sources.md [MCP-IN02]` for source references

## Summary

Ten official MCP SDKs span four tiers based on feature completeness, maintenance commitments, and documentation quality. TypeScript, Python, C#, and Go are Tier 1 with the highest conformance and support requirements. The Python SDK includes FastMCP for rapid server development; the TypeScript SDK provides both server and client APIs. All SDKs support stdio and Streamable HTTP transports. The MCP Inspector provides interactive debugging for protocol message inspection.

## SDK Tiering System

[VERIFIED, spec: community/sdk-tiers] SDKs are classified into three tiers based on feature completeness, maintenance commitments, and documentation quality.

### Current SDK Assignments

**Tier 1** (highest maintenance commitment):
- **TypeScript** - `@modelcontextprotocol/sdk` (npm). Repo: github.com/modelcontextprotocol/typescript-sdk
- **Python** - `mcp` (PyPI). Repo: github.com/modelcontextprotocol/python-sdk
- **C#** - `ModelContextProtocol` (NuGet). Repo: github.com/modelcontextprotocol/csharp-sdk
- **Go** - `github.com/mark3labs/mcp-go`. Repo: github.com/mark3labs/mcp-go

**Tier 2** (mid maintenance):
- **Java** - `io.modelcontextprotocol:sdk` (Maven). Repo: github.com/modelcontextprotocol/java-sdk
- **Rust** - `rmcp` (crates.io). Repo: github.com/aspect-build/rmcp

**Tier 3** (basic maintenance):
- **Swift** - `MCP` (SwiftPM). Repo: github.com/modelcontextprotocol/swift-sdk
- **Ruby** - `mcp` (RubyGems). Repo: github.com/modelcontextprotocol/ruby-sdk
- **PHP** - `logiscape/mcp-sdk-php` (Packagist). Repo: github.com/logiscape/mcp-sdk-php

**TBD**:
- **Kotlin** - Repo: github.com/modelcontextprotocol/kotlin-sdk

### Tier Requirements Summary

**Tier 1 requirements**: Conformance 100% pass, new features before spec release, issue triage within 2 business days, critical bug fix within 7 days, stable release with clear versioning, comprehensive docs with examples.

**Tier 2 requirements**: Conformance 80% pass, new features within 6 months, issue triage within 1 month, critical bug fix within 2 weeks, at least 1 stable release, basic docs for core features.

**Tier 3 requirements**: No conformance minimum, no feature timeline, no triage requirement, no bug fix timeline, stable release not required, no documentation minimum.

### Conformance Testing

Automated tests at github.com/modelcontextprotocol/conformance. Tests validate protocol message exchanges against published specifications. Tier relegation if tests fail continuously for 4 weeks.

## Python Server Example (FastMCP)

The Python SDK includes `FastMCP`, a high-level server framework. [VERIFIED, official docs]

### Setup

```bash
uv init weather && cd weather
uv venv && source .venv/bin/activate
uv add "mcp[cli]"
```

### Complete Weather Server

```python
# weather.py
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"

async def make_nws_request(url: str) -> dict | None:
    headers = {"User-Agent": "weather-app/1.0", "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    if not data["features"]:
        return "No active alerts for this state."
    alerts = []
    for feature in data["features"]:
        props = feature["properties"]
        alerts.append(f"Event: {props.get('event')}, "
                      f"Severity: {props.get('severity')}, "
                      f"Area: {props.get('areaDesc')}")
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    if not points_data:
        return "Unable to fetch forecast data for this location."
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data:
        return "Unable to fetch detailed forecast."
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:
        forecasts.append(f"{period['name']}: {period['temperature']}F "
                         f"{period['windSpeed']} {period['windDirection']} "
                         f"{period['detailedForecast']}")
    return "\n---\n".join(forecasts)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
```

**Run**: `uv run weather.py` (listens via stdio transport)

### Key Python SDK Patterns

- `@mcp.tool()` decorator auto-generates `inputSchema` from type hints and docstring
- `@mcp.resource("file:///{path}")` for resource templates
- `@mcp.prompt()` for prompt templates
- `FastMCP("name")` creates server with name
- `mcp.run(transport="stdio")` or `mcp.run(transport="sse")` for transport selection

## TypeScript Server Example

### Setup

```bash
mkdir weather && cd weather
npm init -y
npm install @modelcontextprotocol/sdk zod@3
npm install -D @types/node typescript
```

### Server Structure

```typescript
// src/index.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const NWS_API_BASE = "https://api.weather.gov";

const server = new McpServer({
  name: "weather",
  version: "1.0.0",
});

server.tool(
  "get-alerts",
  "Get weather alerts for a US state",
  { state: z.string().describe("Two-letter US state code") },
  async ({ state }) => {
    const response = await fetch(`${NWS_API_BASE}/alerts/active/area/${state}`, {
      headers: { "User-Agent": "weather-app/1.0" },
    });
    const data = await response.json();
    const alerts = (data.features || []).map((f: any) => {
      const p = f.properties;
      return `Event: ${p.event}, Severity: ${p.severity}, Area: ${p.areaDesc}`;
    });
    return { content: [{ type: "text", text: alerts.join("\n---\n") || "No alerts" }] };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Weather MCP Server running on stdio");
}

main().catch(console.error);
```

**Build and run**: `npx tsc && node build/index.js`

### Key TypeScript SDK Patterns

- `server.tool(name, description, schema, handler)` using Zod schemas
- `server.resource(name, uri, handler)` for resources
- `server.prompt(name, description, handler)` for prompts
- `StdioServerTransport` or `SSEServerTransport` for transport

## Python Client Example

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

async def main():
    exit_stack = AsyncExitStack()
    server_params = StdioServerParameters(
        command="python",
        args=["weather.py"],
        env=None
    )
    stdio_transport = await exit_stack.enter_async_context(
        stdio_client(server_params)
    )
    stdio, write = stdio_transport
    session = await exit_stack.enter_async_context(
        ClientSession(stdio, write)
    )
    await session.initialize()

    # List available tools
    tools = await session.list_tools()
    print("Tools:", [t.name for t in tools.tools])

    # Call a tool
    result = await session.call_tool("get_alerts", {"state": "CA"})
    print("Result:", result.content[0].text)

    await exit_stack.aclose()

asyncio.run(main())
```

## Host Configuration

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": ["--directory", "/path/to/weather", "run", "weather.py"]
    }
  }
}
```

Location: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS), `%AppData%\Claude\claude_desktop_config.json` (Windows)

## Debugging with MCP Inspector

Interactive debugging tool for MCP servers. [VERIFIED, official docs]

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/server run server.py
```

Features: connect to any MCP server, test tool calls, inspect resources, view protocol messages.

## Important Development Notes

**Logging for stdio servers**: NEVER use `console.log()` (JS) or `print()` (Python) for logging - these write to stdout and corrupt JSON-RPC messages. Use `console.error()` (JS) or `logging.getLogger().handlers` writing to stderr (Python). [VERIFIED, official docs]

## Limitations and Known Issues

- Tier 3 SDKs have no conformance minimum - protocol compliance may vary
- Kotlin SDK still at TBD tier with no formal maintenance commitment
- No official SDK for C or C++ - embedded or systems-level integrations require custom implementation
- MCP Inspector is development-only; no official production monitoring tool exists

## Sources

- MCP-SC-MCPIO-LLMSFULL (positions 0-39, 87-104, 434-437)
- MCP-SC-GH-TSSDK, MCP-SC-GH-PYSDK

## Document History

**[2026-06-12 10:10]**
- Initial topic file with SDK tiering, Python/TypeScript server and client examples, debugging
