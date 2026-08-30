# Search and Embeddings

**Doc ID**: ANTAPI-IN22
**Goal**: Document search result content blocks, embeddings alternatives, and RAG patterns
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` for Messages API content block types

## Summary

Anthropic does not provide a dedicated embeddings API. For search and retrieval-augmented generation (RAG), Claude accepts `search_result` content blocks that represent pre-retrieved search results. These blocks can be cited when citations are enabled. For embeddings, use third-party providers (e.g., Voyage AI, which Anthropic has partnered with). The web search server tool provides built-in search capabilities without external retrieval.

## Key Facts

- **Search Result Block**: `{"type": "search_result", ...}` in message content
- **Embeddings**: Not provided by Anthropic; use Voyage AI or other providers
- **RAG Pattern**: Retrieve externally, pass as content blocks to Claude
- **Citations**: Search results are citable with `search_result_location` type
- **Web Search Tool**: Built-in server tool for real-time web search
- **Status**: GA (search results), N/A (embeddings)

## Search Result Content Blocks

Pass pre-retrieved search results as structured content blocks:

```python
import anthropic

client = anthropic.Anthropic()

# Pass RAG results as search_result blocks
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "search_result",
                    "source": "internal_docs",
                    "title": "API Rate Limits",
                    "content": "Rate limits are enforced per organization...",
                    "url": "https://docs.example.com/rate-limits",
                },
                {
                    "type": "search_result",
                    "source": "internal_docs",
                    "title": "Authentication Guide",
                    "content": "API keys are scoped to workspaces...",
                    "url": "https://docs.example.com/auth",
                },
                {"type": "text", "text": "How do rate limits work for our API?"},
            ],
        }
    ],
)
```

## RAG Pattern with External Embeddings

```python
import anthropic
# Use a third-party embedding provider (e.g., Voyage AI)
# import voyageai

client = anthropic.Anthropic()

def rag_query(query, retriever, top_k=5):
    """Retrieve relevant docs and query Claude with context."""
    # Step 1: Retrieve relevant documents using external embeddings
    results = retriever.search(query, top_k=top_k)

    # Step 2: Format as content blocks
    content = []
    for result in results:
        content.append({
            "type": "document",
            "source": {
                "type": "plain_text",
                "text": result["text"],
            },
            "title": result["title"],
            "citations": {"enabled": True},
        })
    content.append({"type": "text", "text": query})

    # Step 3: Query Claude with retrieved context
    message = client.messages.create(
        model="claude-opus-5",
        max_tokens=2048,
        messages=[{"role": "user", "content": content}],
    )
    return message
```

## Gotchas and Quirks

- Anthropic does not offer an embeddings API; Voyage AI is the recommended partner
- Search result blocks are a convenience format; you can also use plain text or document blocks for RAG
- Web search tool (server-side) provides real-time search without external retrieval setup
- Citations work with search results, documents, and web search results
- Large numbers of search results consume context window tokens

## Related Endpoints

- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` - Messages API (search_result blocks)
- `_INFO_ANTAPI-17_CITATIONS.md [ANTAPI-IN17]` - Citations with search results
- `_INFO_ANTAPI-24_WEB_TOOLS.md [ANTAPI-IN24]` - Built-in web search tool

## Sources

- ANTAPI-SC-ANTH-MSGCRT - https://platform.claude.com/docs/en/api/messages/create - Search result block schema
- ANTAPI-SC-ANTH-RAG - https://platform.claude.com/docs/en/build-with-claude/retrieval-augmented-generation - RAG patterns

## SDK Verification

All 2 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `resources/messages/messages.py`: `create()` accepts `search_result` and `document` content blocks in messages
- Document source type `plain_text` with `citations` config confirmed

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:55]**
- Added: SDK verification section (anthropic 0.120.0, all 2 examples valid)

**[2026-03-20 03:35]**
- Initial documentation created from Messages API reference and RAG guide
