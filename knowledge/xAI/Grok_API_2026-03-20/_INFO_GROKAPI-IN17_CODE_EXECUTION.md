# INFO: Code Execution Tool

**Doc ID**: GROKAPI-IN17
**Goal**: Python sandbox, capabilities, use cases, limitations, security
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Code Execution tool (`code_execution` / `code_interpreter`) provides a server-side Python sandbox where Grok can write and execute Python code during inference. The model autonomously decides when to run code for tasks like data analysis, calculations, chart generation, and file processing. Executes on xAI servers in a sandboxed environment. Billed at $5 per 1,000 invocations plus token costs. Usage category: `SERVER_SIDE_TOOL_CODE_EXECUTION`. Note: In gRPC API (xAI SDK), the `code_interpreter` name is not supported - use `code_execution`. Similar to Gemini's built-in code_execution tool. [VERIFIED] (GROKAPI-SC-XAI-CODEEXEC | https://docs.x.ai/developers/tools/code-execution)

## Key Facts

- [VERIFIED] Tool names: `code_execution`, `code_interpreter` (Responses API only for code_interpreter) (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Server-side Python sandbox (GROKAPI-SC-XAI-CODEEXEC)
- [VERIFIED] Invocation cost: $5 per 1,000 calls (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] gRPC API does not support `code_interpreter` name (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Usage category: `SERVER_SIDE_TOOL_CODE_EXECUTION` (GROKAPI-SC-XAI-TOOLDETAILS)

## Quick Reference

- **Tool type**: Server-side
- **Tool name**: `code_execution` (preferred) or `code_interpreter` (Responses API only)
- **Cost**: $5 / 1K invocations + token costs
- **Language**: Python
- **Environment**: Sandboxed, isolated

## Examples

### Enable Code Execution (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Calculate the first 20 Fibonacci numbers and plot them."}],
    tools=[{"type": "code_execution"}],
)
print(response.output_text)
```

### Combined with Web Search (xAI SDK)

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, code_execution

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.20-beta-latest-non-reasoning",
    tools=[web_search(), code_execution()],
)

chat.append(user("Find the current S&P 500 price and calculate the annualized return from $10,000 invested 5 years ago."))
response = chat.sample()
print(response.content)
```

## Use Cases

- **Data analysis**: Statistical calculations, data transformations
- **Visualization**: Chart and graph generation
- **Mathematical proofs**: Step-by-step calculations with verification
- **File processing**: Parse and analyze structured data
- **Code verification**: Test code snippets in sandbox

## Differences from Other APIs

### vs OpenAI
- **Similar concept**: OpenAI has code_interpreter in Assistants API
- **Server-side**: Both execute on provider servers
- **Naming**: xAI uses `code_execution` (primary) and `code_interpreter` (alias)

### vs Anthropic
- **UNIQUE**: Anthropic has no built-in code execution tool (relies on client-side tools or computer_use)

### vs Gemini
- **Similar**: Gemini has built-in `code_execution` tool with Python sandbox
- **Same concept**: Both are server-side Python sandboxes

## Limitations and Known Issues

- [VERIFIED] `code_interpreter` name not supported in gRPC API (GROKAPI-SC-XAI-MODELS)
- Sandboxed environment with limited package availability
- No persistent state between invocations

## Sources

- GROKAPI-SC-XAI-CODEEXEC | https://docs.x.ai/developers/tools/code-execution | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:40]**
- Initial document created with code execution reference and examples
