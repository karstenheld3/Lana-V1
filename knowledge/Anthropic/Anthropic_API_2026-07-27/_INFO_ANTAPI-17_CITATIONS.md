# Citations

**Doc ID**: ANTAPI-IN17
**Goal**: Document citation types, configuration, document types, and response structure
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` for Messages API request/response schema

## Summary

Citations enable Claude to reference specific passages from source documents in its responses. When enabled via `citations: {"enabled": true}` on document blocks, Claude returns text blocks with inline citation objects pointing to exact locations in the source material. Three document types are supported: plain text (auto-chunked into sentences), PDF (text extracted and chunked), and custom content (user-defined chunks for fine-grained control). Citations work with documents provided inline (base64, URL, text) or via the Files API (file_id reference).

## Key Facts

- **Enable**: `citations: {"enabled": true}` on document blocks
- **Document Types**: plain_text, pdf, custom content
- **Auto-Chunking**: Plain text and PDF are chunked into sentences
- **Custom Chunks**: User-defined text blocks (no additional chunking)
- **Citation Types**: char_location, page_location, content_block_location, search_result_location, web_search_result_location
- **File Reference**: Documents can use `file_id` from Files API
- **Status**: GA

## Document Types

### Plain Text Documents

Auto-chunked into sentences. Provide inline or by file_id:

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "plain_text",
                        "text": "The Earth orbits the Sun at an average distance of about 93 million miles. "
                               "It takes approximately 365.25 days to complete one orbit.",
                    },
                    "title": "Earth Facts",
                    "citations": {"enabled": True},
                },
                {"type": "text", "text": "How far is Earth from the Sun?"},
            ],
        }
    ],
)
```

### PDF Documents

Text extracted and chunked into sentences. Provide as base64 or file_id:

```python
import anthropic
import base64

client = anthropic.Anthropic()

with open("report.pdf", "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                    "title": "Annual Report",
                    "citations": {"enabled": True},
                },
                {"type": "text", "text": "What were the key findings?"},
            ],
        }
    ],
)
```

### Custom Content Documents

User-defined chunks for fine-grained citation control:

```python
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "content",
                        "content": [
                            {"type": "text", "text": "Revenue grew 15% year-over-year."},
                            {"type": "text", "text": "Customer retention rate was 94%."},
                            {"type": "text", "text": "New product launches exceeded targets."},
                        ],
                    },
                    "title": "Q4 Summary",
                    "context": "Internal quarterly business review",  # not cited from
                    "citations": {"enabled": True},
                },
                {"type": "text", "text": "Summarize the business performance."},
            ],
        }
    ],
)
```

## Response Structure

Text blocks in the response include `citations` arrays with location objects:

```json
{
  "type": "text",
  "text": "The Earth is about 93 million miles from the Sun.",
  "citations": [
    {
      "type": "char_location",
      "cited_text": "The Earth orbits the Sun at an average distance of about 93 million miles.",
      "document_index": 0,
      "document_title": "Earth Facts",
      "start_char_index": 0,
      "end_char_index": 74
    }
  ]
}
```

### Citation Location Types

- **char_location** - Character offsets in plain text documents
- **page_location** - Page numbers in PDF documents
- **content_block_location** - Block indices in custom content documents
- **search_result_location** - References to search results
- **web_search_result_location** - References to web search results

## Gotchas and Quirks

- `.csv`, `.xlsx`, `.docx`, `.md`, `.txt` files are not supported as document blocks; convert to plain text first
- PDFs that are scanned images without extractable text cannot be cited (image citations not yet supported)
- The `context` field on documents provides background info but is not citable
- Custom content documents receive no additional chunking; each text block is one citable unit
- Citations add token overhead; monitor usage with token counting

## Related Endpoints

- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` - Messages API (document blocks)
- `_INFO_ANTAPI-19_PDF_SUPPORT.md [ANTAPI-IN19]` - PDF input details
- `_INFO_ANTAPI-30_FILES_API.md [ANTAPI-IN30]` - File upload for document references

## Sources

- ANTAPI-SC-ANTH-CITE - https://platform.claude.com/docs/en/build-with-claude/citations - Full citations guide

## SDK Verification

All 3 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `resources/messages/messages.py`: `create()` accepts document content blocks in messages
- `types/` document source types: `plain_text`, `base64`, `content` source types confirmed
- Citation config `{"enabled": True}` on document blocks is SDK-compatible

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:55]**
- Added: SDK verification section (anthropic 0.120.0, all 3 examples valid)

**[2026-03-20 03:20]**
- Initial documentation created from citations guide
