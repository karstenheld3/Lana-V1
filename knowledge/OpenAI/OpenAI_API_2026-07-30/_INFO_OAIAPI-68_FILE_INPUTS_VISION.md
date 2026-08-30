# File Inputs for Text Generation

**Doc ID**: OAIAPI-IN68
**Goal**: Document file input support in Chat Completions and Responses API - PDF, images, documents as context
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

File inputs allow passing documents directly to models for analysis, summarization, extraction, and question-answering. Supported in both Chat Completions and Responses API. Two methods: reference an uploaded file by `file_id` (from the Files API) or pass file content inline as base64. Supported types: PDF, images (PNG/JPEG/GIF/WebP), text, code. PDFs processed page-by-page with text extraction and optional figure analysis. Images support detail levels (auto, low, high). Multiple files per request supported. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-GFILE)

## Key Facts

- **Methods**: file_id reference or base64 inline [VERIFIED] (OAIAPI-SC-OAI-GFILE)
- **Supported types**: PDF, images (PNG/JPEG/GIF/WebP), text, code [VERIFIED] (OAIAPI-SC-OAI-GFILE)
- **PDF processing**: Page-by-page text extraction + figure analysis [VERIFIED] (OAIAPI-SC-OAI-GFILE)
- **Image detail**: auto, low, high - affects tokens and quality [VERIFIED] (OAIAPI-SC-OAI-CHATC)
- **Multiple files**: Multiple files per request supported [VERIFIED] (OAIAPI-SC-OAI-GFILE)
- **APIs**: Chat Completions and Responses API [VERIFIED] (OAIAPI-SC-OAI-GFILE)

## Use Cases

- **Document analysis**: Summarize PDFs, extract key points
- **Data extraction**: Pull structured data from documents
- **Image analysis**: Describe, analyze, or OCR images
- **Code review**: Analyze code files for bugs or improvements
- **Comparison**: Compare multiple documents side-by-side
- **Q&A**: Answer questions about document content

## Quick Reference

### Chat Completions - File by ID

```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "Summarize this document."},
    {
      "type": "file",
      "file": {"file_id": "file-abc123"}
    }
  ]
}
```

### Responses API - File Input

```json
{
  "model": "gpt-5.5",
  "input": [
    {
      "type": "message",
      "role": "user",
      "content": [
        {"type": "input_text", "text": "Summarize this PDF."},
        {"type": "input_file", "file_id": "file-abc123"}
      ]
    }
  ]
}
```

## SDK Examples (Python)

### Upload and Analyze PDF

```python
from openai import OpenAI

client = OpenAI()

with open("quarterly_report.pdf", "rb") as f:
    file = client.files.create(file=f, purpose="assistants")

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract key financial metrics from this report."},
                {"type": "file", "file": {"file_id": file.id}}
            ]
        }
    ],
    max_completion_tokens=2000
)

print(response.choices[0].message.content)
```

### Multi-File Comparison

```python
from openai import OpenAI

client = OpenAI()

with open("contract_v1.pdf", "rb") as f:
    file1 = client.files.create(file=f, purpose="assistants")

with open("contract_v2.pdf", "rb") as f:
    file2 = client.files.create(file=f, purpose="assistants")

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Compare these two contracts. List all changes between v1 and v2."},
                {"type": "file", "file": {"file_id": file1.id}},
                {"type": "file", "file": {"file_id": file2.id}}
            ]
        }
    ],
    max_completion_tokens=3000
)

print(response.choices[0].message.content)
```

### Image Analysis with Detail Control

```python
from openai import OpenAI
import base64

client = OpenAI()

with open("diagram.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this architecture diagram in detail."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_b64}",
                        "detail": "high"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

## Error Responses

- **400 Bad Request** - Unsupported file type or corrupt file
- **404 Not Found** - file_id not found
- **413 Payload Too Large** - File exceeds size limits

## Differences from Other APIs

- **vs Anthropic**: Anthropic supports PDF and image inputs via base64 in messages. Similar capability
- **vs Gemini**: Gemini supports file upload via File API and inline data. Supports video input (OpenAI does not)
- **vs Grok**: Limited file input support

## Limitations and Known Issues

- **Token cost**: Large PDFs and high-detail images consume significant context tokens [VERIFIED] (OAIAPI-SC-OAI-GFILE)
- **No video**: Video files not supported for text generation [ASSUMED]
- **PDF quality**: Scanned PDFs with poor OCR may produce lower quality extraction [ASSUMED]

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

- OAIAPI-SC-OAI-GFILE - File Inputs Guide
- OAIAPI-SC-OAI-GFILIN - File Inputs Reference
- OAIAPI-SC-OAI-CHATC - Chat Completions API Reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:55]**
- Enriched from 2026-03-20 IN68 (19 -> 190 lines)
- Updated model references to gpt-5.5

**[2026-05-22 11:50]**
- Stub created
