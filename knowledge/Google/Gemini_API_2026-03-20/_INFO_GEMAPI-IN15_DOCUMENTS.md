# INFO: Gemini API Document Processing

**Doc ID**: GEMAPI-IN15
**Goal**: Document PDF processing, document understanding, page limits, and long context strategies
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini models process PDF documents as multimodal input, understanding both textual content and visual layout including images, charts, tables, and formatting. PDFs are provided via inline base64 data or File API references. The API supports up to 1000 pages per document. Gemini processes PDFs as a combination of extracted text and rendered page images, enabling understanding of both content and visual structure. Long documents benefit from context caching to reduce cost on repeated queries. Document understanding tasks include summarization, Q&A, data extraction, comparison, and translation.

## Key Facts

- [VERIFIED] PDF input via inlineData (base64) or fileData (File API) (GEMAPI-SC-GOOG-DOCPRC)
- [VERIFIED] Up to 1000 pages per document (GEMAPI-SC-GOOG-DOCPRC)
- [VERIFIED] Multimodal understanding: text + layout + images (GEMAPI-SC-GOOG-DOCPRC)
- [VERIFIED] Long documents benefit from context caching (GEMAPI-SC-GOOG-LNGCTX)

## Quick Reference

**Inline**: `{"inlineData": {"mimeType": "application/pdf", "data": "base64..."}}`
**File API**: `{"fileData": {"mimeType": "application/pdf", "fileUri": "..."}}`
**Max pages**: ~1000 per document

## Python Examples

### Example 1: PDF Analysis

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

uploaded = client.files.upload(file="report.pdf")
while uploaded.state == "PROCESSING":
    time.sleep(2)
    uploaded = client.files.get(name=uploaded.name)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[
            types.Part(file_data=types.FileData(
                mime_type="application/pdf", file_uri=uploaded.uri
            )),
            types.Part(text="Summarize the key findings in this report. Extract all tables as structured data."),
        ])
    ]
)
print(response.text)
```

### Example 2: Small PDF via Inline Base64

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open("invoice.pdf", "rb") as f:
    pdf_data = base64.b64encode(f.read()).decode("utf-8")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[
            types.Part(inline_data=types.Blob(
                mime_type="application/pdf", data=pdf_data
            )),
            types.Part(text="Extract the invoice number, date, total amount, and line items."),
        ])
    ]
)
print(response.text)
```

## Comparison with Other APIs

### vs OpenAI

- **PDF input**: Both support PDF input natively
- **Page limit**: Gemini: ~1000 pages | OpenAI: similar limits
- **Multimodal**: Both understand text + layout + images in PDFs

### vs Anthropic

- **PDF input**: Gemini: inlineData/fileData | Anthropic: base64 or URL in document blocks
- **Page limit**: Gemini: ~1000 | Anthropic: 100 pages per document
- **Advantage**: Gemini supports significantly more pages per document

## Error Responses

- **400**: Corrupt PDF, exceeds page limit, file too large for inline

## Rate Limiting / Throttling

Standard rate limits. Large PDFs consume many tokens. See GEMAPI-IN04.

## Limitations and Known Issues

- Very complex PDFs with many images may consume large token counts
- Scanned documents (image-only PDFs) processed via OCR with varying accuracy

## Gotchas and Quirks

- Large PDFs should use File API, not inline base64
- Page count limit is approximate and depends on page complexity
- Use context caching for repeated queries against the same document to save cost
- Token count for PDFs can be surprisingly high - check with countTokens first

## Sources

- GEMAPI-SC-GOOG-DOCPRC: https://ai.google.dev/gemini-api/docs/document-processing [VERIFIED]
- GEMAPI-SC-GOOG-LNGCTX: https://ai.google.dev/gemini-api/docs/long-context [VERIFIED]

## Document History

**[2026-03-20 04:00]**
- Initial document created
