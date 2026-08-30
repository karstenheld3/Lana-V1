# INFO: Collections Search Tool

**Doc ID**: GROKAPI-IN18
**Goal**: RAG with uploaded documents, collection management, citations, hybrid search
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Collections Search (`collections_search` / `file_search`) is a server-side RAG tool that enables Grok to query uploaded document collections during inference. Documents are uploaded via the Collections API, organized into collections, and automatically indexed. The model autonomously performs semantic search across collection documents, returning results with structured citations using `collections://collection_id/files/file_id` URI format. Supports combining with web_search, x_search, and code_execution for hybrid analysis (internal data + external intelligence). Billed at $2.50 per 1,000 invocations plus token costs. The tool demonstrates efficient prompt caching - cached_tokens can be very high (e.g., 177K) across multiple queries within a session. In gRPC API (xAI SDK), `file_search` name is not supported - use `collections_search`. [VERIFIED] (GROKAPI-SC-XAI-COLLSEARCH | https://docs.x.ai/developers/tools/collections-search)

## Key Facts

- [VERIFIED] Tool names: `collections_search`, `file_search` (Responses API only for file_search) (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Server-side RAG tool (GROKAPI-SC-XAI-COLLSEARCH)
- [VERIFIED] Invocation cost: $2.50 per 1,000 calls (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Citation format: `collections://collection_id/files/file_id` (GROKAPI-SC-XAI-COLLSEARCH)
- [VERIFIED] Model autonomously performs multiple search queries (GROKAPI-SC-XAI-COLLSEARCH)
- [VERIFIED] High prompt caching efficiency across queries (GROKAPI-SC-XAI-COLLSEARCH)
- [VERIFIED] gRPC API does not support `file_search` name (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Can combine with web_search, x_search, code_execution (GROKAPI-SC-XAI-COLLSEARCH)

## Quick Reference

- **Tool type**: Server-side (RAG)
- **Tool name**: `collections_search` (preferred) or `file_search` (Responses API only)
- **Cost**: $2.50 / 1K invocations + token costs
- **Citation format**: `collections://collection_id/files/file_id`
- **Parameters**: `collection_ids` (array of collection IDs to search)

## Examples

### Basic Collections Search (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What are the key findings in the Q3 report?"}],
    tools=[{
        "type": "collections_search",
        "collection_ids": ["collection_3be0eec8-ee8e-4a18-a9d4-fb70a3150d64"],
    }],
)
print(response.output_text)
```

### Hybrid Search (Internal + External)

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{
        "role": "user",
        "content": "Based on our internal production data, how does our performance compare to industry benchmarks?",
    }],
    tools=[
        {"type": "collections_search", "collection_ids": ["col_internal_data"]},
        {"type": "web_search"},
        {"type": "x_search"},
        {"type": "code_execution"},
    ],
)
```

### xAI SDK with Streaming

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import collections_search, web_search, code_execution

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.20-beta-latest-non-reasoning",
    tools=[
        collections_search(collection_ids=["col_abc123"]),
        web_search(),
        code_execution(),
    ],
    include=["verbose_streaming"],
)

chat.append(user("Analyze Tesla's production figures from our documents vs market expectations."))

for response, chunk in chat.stream():
    for tool_call in chunk.tool_calls:
        print(f"\nTool: {tool_call.function.name}({tool_call.function.arguments})")
    if chunk.content:
        print(chunk.content, end="", flush=True)

print(f"\nCitations: {response.citations}")
print(f"Tool usage: {response.server_side_tool_usage}")
```

## Citation Format

Citations use a special URI format:
```
collections://collection_id/files/file_id
```

Components:
- `collections://` - Protocol identifier
- `collection_id` - Unique collection identifier
- `files/` - Path segment for file reference
- `file_id` - Specific document file identifier

## Use Cases

- **Financial analysis**: Query internal reports, compare with market data
- **Legal review**: Search contract collections, cross-reference regulations
- **Research synthesis**: Combine internal papers with current publications
- **Customer intelligence**: Internal CRM data + external sentiment
- **Compliance**: Internal policies vs current regulatory requirements

## Differences from Other APIs

### vs OpenAI
- **Similar concept**: OpenAI Assistants has `file_search` with vector stores
- **Server-side**: Both execute on provider servers
- **Hybrid search**: xAI natively combines with web_search/x_search in one request
- **Citation format**: xAI uses `collections://` URI; OpenAI uses file annotations

### vs Anthropic
- **UNIQUE**: Anthropic has no built-in RAG tool (relies on context window or third-party)

### vs Gemini
- **Similar**: Gemini has semantic retrieval with corpora
- **Different API**: Different collection management and search patterns

## Limitations and Known Issues

- [VERIFIED] `file_search` name not supported in gRPC API (GROKAPI-SC-XAI-MODELS)
- Documents must be uploaded and indexed via Collections API before searching

## Sources

- GROKAPI-SC-XAI-COLLSEARCH | https://docs.x.ai/developers/tools/collections-search | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:50]**
- Initial document created with Collections Search reference, citation format, and hybrid search
