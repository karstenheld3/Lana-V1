# MCP and Connectors

**Doc ID**: OAIAPI-IN66
**Goal**: Document Remote MCP server integration, Secure MCP Tunnels, connector setup
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The MCP (Model Context Protocol) tool allows models to connect to remote MCP servers for accessing external tools and data sources. GPT-5.5 and GPT-5.4 support MCP natively via the Responses API. Remote MCP servers are configured as tool definitions specifying the server URL and authentication. New in 2026-05: **Secure MCP Tunnel** enables enterprise customers to connect to private or on-premises MCP servers without exposing them to the public internet, using a customer-hosted tunnel-client. Initial GA is account-led (not self-serve). Supported products: ChatGPT web, Codex, Responses API, AgentKit. [VERIFIED] (OAIAPI-SC-OAI-GMCP, OAIAPI-SC-OAI-GSCMCP, OAIAPI-SC-OAI-GCHLOG)

## REST API

### Responses API with MCP

**Endpoint**: `POST /v1/responses`

```json
{
  "model": "gpt-5.5",
  "input": "Look up the latest sales data from our internal CRM.",
  "tools": [
    {
      "type": "mcp",
      "server_label": "internal_crm",
      "server_url": "https://mcp.company.com/crm",
      "require_approval": "never",
      "allowed_tools": ["search_contacts", "get_deals"]
    }
  ]
}
```

**MCP Tool Parameters**:

- **type** (string, required) - Always `"mcp"`
- **server_label** (string, required) - Human-readable label for the MCP server
- **server_url** (string, required) - URL of the MCP server (HTTPS)
- **require_approval** (string, optional) - `"never"`, `"always"`, or `"on_first_use"`. Default: `"on_first_use"`
- **allowed_tools** (array, optional) - List of tool names to expose from the server
- **headers** (object, optional) - Custom headers for authentication

## Secure MCP Tunnel (NEW - 2026-05)

For enterprise customers with private or on-premises MCP servers not accessible from the public internet.

### How it Works

1. Customer deploys a `tunnel-client` on their internal network
2. Tunnel-client establishes outbound connection to OpenAI's tunnel service
3. OpenAI products (ChatGPT, Codex, Responses API, AgentKit) connect through the tunnel
4. Private MCP servers remain unexposed to the public internet

### Setup

```bash
# Install tunnel-client
tunnel-client install

# Configure with organization credentials
tunnel-client config --org-id org_abc123 --api-key sk-admin-...

# Start tunnel pointing to internal MCP server
tunnel-client start --target http://internal-mcp:8080
```

**Availability**: Account-led GA (not self-serve). Contact OpenAI sales.

## SDK Examples (Python)

### Basic MCP Connection

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Search for all customers who signed up last month.",
    tools=[{
        "type": "mcp",
        "server_label": "customer_db",
        "server_url": "https://mcp.company.com/db",
        "require_approval": "never",
        "allowed_tools": ["search_customers", "get_customer_details"],
    }],
)
print(response.output_text)
```

### MCP with Authentication

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Get the latest deployment status from our CI/CD pipeline.",
    tools=[{
        "type": "mcp",
        "server_label": "cicd",
        "server_url": "https://mcp.company.com/cicd",
        "headers": {
            "Authorization": "Bearer internal-token-xyz",
        },
        "require_approval": "always",
    }],
)
print(response.output_text)
```

## Error Responses

- **400 Bad Request** - Invalid MCP server URL or configuration
- **502 Bad Gateway** - MCP server unreachable or returned error
- **504 Gateway Timeout** - MCP server timed out

## Gotchas and Quirks

- **Secure MCP Tunnel**: Enterprise-only, account-led GA (not self-serve) [VERIFIED]
- **Tunnel-client**: Customer-hosted, requires outbound internet access [VERIFIED]
- **require_approval**: Default is `on_first_use`, not `never` [VERIFIED]
- **allowed_tools**: Filter exposed tools to minimize attack surface [VERIFIED]

## TypeScript Examples

### Basic Response

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Explain this concept briefly.",
});

console.log(response.output_text);
```

### With Instructions

```typescript
const response = await client.responses.create({
  model: "gpt-4o-mini",
  instructions: "You are a helpful assistant.",
  input: "What is 2+2?",
});

console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-GMCP - MCP and Connectors guide
- OAIAPI-SC-OAI-GSCMCP - Secure MCP Tunnels guide
- OAIAPI-SC-OAI-GCHLOG - Changelog (2026-05)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 10:50]**
- Updated from 2026-03-20 version
- Added: Secure MCP Tunnel documentation (2026-05)
- Added: tunnel-client setup instructions
- Changed: Model references to GPT-5.5
