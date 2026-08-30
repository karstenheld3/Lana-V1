# INFO: Gemini API Long Context

**Doc ID**: GEMAPI-IN36
**Goal**: Document large context window capabilities, prompting strategies, and token management
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini models offer industry-leading context windows: Gemini 2.5 Pro supports up to 1M tokens input, Gemini 2.5 Flash supports 1M tokens, and Gemini 3 models continue this trend. These large context windows enable processing entire codebases, long documents, multi-hour audio, and extended video content in a single request. Key strategies for long context include: placing reference material before the question ("needle in a haystack"), using context caching for repeated queries against the same material, combining the File API for media with inline text, and leveraging `countTokens` to manage context budgets. Long context does not significantly degrade quality for most retrieval tasks. Cost management is critical - context caching reduces per-query cost for repeated use of the same large context.

## Key Facts

- [VERIFIED] Gemini 2.5 Pro/Flash: 1M token input context (GEMAPI-SC-GOOG-LNGCTX)
- [VERIFIED] Strategy: reference material before question (GEMAPI-SC-GOOG-FILPRM)
- [VERIFIED] Context caching reduces cost for repeated queries (GEMAPI-SC-GOOG-CACHNG)
- [VERIFIED] countTokens for budget management (GEMAPI-SC-GOOG-TOKENS)
- [VERIFIED] Quality maintained for retrieval in large contexts (GEMAPI-SC-GOOG-LNGCTX)

## Quick Reference

**Max context**: 1M tokens (model-dependent)
**Cost strategy**: Context caching for repeated queries
**Token check**: `countTokens` endpoint before sending

## Long Context Use Cases

- **Full codebase analysis**: Analyze entire repository in one request
- **Document Q&A**: Query across hundreds of pages
- **Meeting transcripts**: Process multi-hour audio transcriptions
- **Video analysis**: Analyze up to ~1 hour of video content
- **Legal review**: Cross-reference multiple long contracts
- **Research synthesis**: Combine multiple research papers

## Prompting Strategies

- **Reference-first**: Place documents/data BEFORE the question
- **Explicit instructions**: Tell model where to look ("In section 3...")
- **Chunked queries**: For very large contexts, ask focused questions
- **Structured output**: Use JSON schemas to extract specific data points
- **Multi-pass**: First pass for overview, second for specific details

## Python Examples

### Example 1: Multi-Document Analysis

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Upload multiple documents
files = []
for doc_path in ["report_q1.pdf", "report_q2.pdf", "report_q3.pdf", "report_q4.pdf"]:
    uploaded = client.files.upload(file=doc_path)
    while uploaded.state == "PROCESSING":
        time.sleep(2)
        uploaded = client.files.get(name=uploaded.name)
    files.append(uploaded)

# Query across all documents
parts = []
for f in files:
    parts.append(types.Part(file_data=types.FileData(
        mime_type=f.mime_type, file_uri=f.uri
    )))
parts.append(types.Part(text="Compare revenue trends across all four quarters. Identify the quarter with highest growth."))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[types.Content(role="user", parts=parts)]
)
print(response.text)
print(f"Total tokens: {response.usage_metadata.total_token_count}")
```

### Example 2: Context Budget Management

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Check token count before sending
large_text = open("full_codebase.txt").read()

count = client.models.count_tokens(
    model="gemini-2.5-flash",
    contents=large_text
)

model_info = client.models.get(model="gemini-2.5-flash")
print(f"Content tokens: {count.total_tokens}")
print(f"Model limit: {model_info.input_token_limit}")
print(f"Remaining for output: {model_info.input_token_limit - count.total_tokens}")

if count.total_tokens < model_info.input_token_limit * 0.9:  # 90% safety margin
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{large_text}\n\nFind all security vulnerabilities in this code."
    )
    print(response.text)
else:
    print("Content too large - consider chunking or using a model with larger context")
```

## Comparison with Other APIs

### vs OpenAI

- **Max context**: Gemini: 1M tokens | OpenAI: 128K (GPT-4o), 200K (o1/o3)
- **ADVANTAGE**: Gemini offers 5-8x larger context windows
- **Caching**: Gemini: explicit cache API | OpenAI: automatic caching

### vs Anthropic

- **Max context**: Gemini: 1M tokens | Anthropic: 200K tokens
- **ADVANTAGE**: Gemini offers 5x larger context window
- **Caching**: Gemini: explicit cache | Anthropic: cache_control blocks

## Error Responses

- **400**: Content exceeds model's input token limit
- **429**: Rate limit (large requests consume more TPM)

## Rate Limiting / Throttling

Large context requests consume significant TPM quota. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Very large contexts increase latency (GEMAPI-SC-GOOG-LNGCTX)
- Thinking tokens compound cost on top of large input tokens
- Quality may degrade for very specific retrieval in 1M+ contexts (rare)

## Gotchas and Quirks

- 1M tokens is ~750K words or ~3000 pages of text - genuinely large
- Always check with countTokens before sending large requests to avoid wasted API calls
- Context caching is essential for cost management with repeated large-context queries
- Place the question AFTER the reference material for best results
- Thinking tokens add on top of large input - disable thinking for simple extraction tasks
- Large context = high TPM usage = may hit rate limits faster

## Sources

- GEMAPI-SC-GOOG-LNGCTX: https://ai.google.dev/gemini-api/docs/long-context [VERIFIED]
- GEMAPI-SC-GOOG-FILPRM: https://ai.google.dev/gemini-api/docs/file-prompting-strategies [VERIFIED]

## Document History

**[2026-03-20 05:40]**
- Initial document created
