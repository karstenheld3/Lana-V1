# INFO: Chat with Files

**Doc ID**: GROKAPI-IN29
**Goal**: File attachments in chat, attachment_search tool, supported formats
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Chat with Files enables attaching documents directly to chat messages for analysis. Uses the `attachment_search` server-side tool ($10 per 1,000 invocations). Files are attached to the message and the model can search through them during inference. Different from Collections (which are persistent, reusable document stores) - file attachments are per-message and ephemeral. Useful for one-off document analysis without setting up a collection. [VERIFIED] (GROKAPI-SC-XAI-CHATWFILES | https://docs.x.ai/developers/model-capabilities/text/chat-with-files)

## Key Facts

- [VERIFIED] Tool: `attachment_search` for searching attached files (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Cost: $10 per 1,000 invocations (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Per-message file attachment (ephemeral, not persistent like Collections) (GROKAPI-SC-XAI-CHATWFILES)

## Quick Reference

- **Tool**: `attachment_search`
- **Cost**: $10 / 1K invocations + token costs
- **Use case**: One-off document analysis

## Examples

### Chat with File Attachment (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# Upload file first
file = client.files.create(file=open("report.pdf", "rb"), purpose="assistants")

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{
        "role": "user",
        "content": "Summarize the key findings in this report.",
        "attachments": [{"file_id": file.id, "tools": [{"type": "attachment_search"}]}],
    }],
    tools=[{"type": "attachment_search"}],
)
print(response.output_text)
```

## Differences from Other APIs

### vs OpenAI
- **Similar**: OpenAI Assistants supports file attachments with file_search
- **Different scope**: xAI attachment_search is per-message; OpenAI uses vector stores

### vs Collections Search
- **Ephemeral**: Attachments are per-message; Collections are persistent
- **No setup**: No need to create a collection first
- **Higher cost**: $10/1K vs $2.50/1K for collections_search

## Sources

- GROKAPI-SC-XAI-CHATWFILES | https://docs.x.ai/developers/model-capabilities/text/chat-with-files | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:50]**
- Initial document created with chat with files reference
