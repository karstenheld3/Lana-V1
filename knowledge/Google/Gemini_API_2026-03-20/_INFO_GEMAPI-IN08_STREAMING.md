# INFO: Gemini API Streaming

**Doc ID**: GEMAPI-IN08
**Goal**: Document SSE streaming via streamGenerateContent, chunk handling, and partial responses
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini API supports Server-Sent Events (SSE) streaming through the `streamGenerateContent` endpoint. This is a separate endpoint from `generateContent` that accepts the identical request body but returns the response as a stream of `GenerateContentResponse` chunks. Each chunk contains a partial `candidates` array with incremental text in `content.parts[].text`. All chunks in a single response share the same `responseId`, enabling client-side reassembly. The final chunk includes `finishReason` and `usageMetadata` with complete token counts. In REST, streaming requires the `?alt=sse` query parameter. The Python SDK provides `generate_content_stream()` which returns an iterator of chunks. Unlike OpenAI (which uses `stream: true` parameter on the same endpoint) and Anthropic (which also uses `stream: true`), Gemini uses a dedicated streaming endpoint.

## Key Facts

- [VERIFIED] Streaming endpoint: `POST /v1beta/models/{model}:streamGenerateContent` (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Same request body as generateContent (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Returns stream of GenerateContentResponse instances (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] All chunks share same `responseId` (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] REST requires `?alt=sse` query parameter (GEMAPI-SC-GOOG-TXTGEN)
- [VERIFIED] Final chunk includes finishReason and usageMetadata (GEMAPI-SC-GOOG-APIOVW)

## Quick Reference

**Endpoint**: `POST /v1beta/models/{model}:streamGenerateContent?alt=sse`
**Auth**: `x-goog-api-key: YOUR_API_KEY`
**Content-Type**: `application/json`
**Response Format**: `text/event-stream` (SSE)

## REST API

### Request

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse
```

Same request body as `generateContent`. See GEMAPI-IN07 for full schema.

### Response (SSE Stream)

Each SSE event contains a JSON `GenerateContentResponse`:

```
data: {"candidates":[{"content":{"parts":[{"text":"The"}],"role":"model"},"index":0}],"modelVersion":"gemini-2.5-flash","responseId":"abc123"}

data: {"candidates":[{"content":{"parts":[{"text":" capital of"}],"role":"model"},"index":0}],"modelVersion":"gemini-2.5-flash","responseId":"abc123"}

data: {"candidates":[{"content":{"parts":[{"text":" France is Paris."}],"role":"model"},"finishReason":"STOP","index":0}],"usageMetadata":{"promptTokenCount":10,"candidatesTokenCount":8,"totalTokenCount":18},"modelVersion":"gemini-2.5-flash","responseId":"abc123"}
```

**Chunk Fields:**
- **candidates[0].content.parts[0].text** (string): Incremental text fragment
- **candidates[0].finishReason** (string): Present only on final chunk
- **usageMetadata** (object): Present only on final chunk (complete token counts)
- **responseId** (string): Same across all chunks in one response

## Python Examples

### Example 1: Basic Streaming

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="Write a detailed explanation of photosynthesis"
):
    print(chunk.text, end="", flush=True)
print()
```

### Example 2: Streaming with Full Response Assembly

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

full_text = ""
usage = None

for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a creative writer.",
        temperature=0.9,
        max_output_tokens=2048,
    ),
    contents="Write a short story about a robot discovering emotions"
):
    if chunk.text:
        full_text += chunk.text
        print(chunk.text, end="", flush=True)
    if chunk.usage_metadata:
        usage = chunk.usage_metadata

print(f"\n\nTotal tokens: {usage.total_token_count}")
print(f"Input: {usage.prompt_token_count}, Output: {usage.candidates_token_count}")
```

### Example 3: Streaming with Error Handling

```python
# SOURCE: Google API docs (may use google.api_core.exceptions)
from google import genai
from google.api_core import exceptions
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

try:
    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents="Explain the theory of relativity"
    ):
        if chunk.candidates and chunk.candidates[0].finish_reason == "SAFETY":
            print("\n[Content blocked by safety filter]")
            break
        print(chunk.text, end="", flush=True)
    print()
except exceptions.ResourceExhausted:
    print("\nRate limited during streaming")
except Exception as e:
    print(f"\nStreaming error: {e}")
```

**SDK-verified correction** (google-genai v1.68.0, `google/genai/errors.py`):

```python
from google import genai
from google.genai.errors import ClientError, ServerError
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

try:
    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents="Explain the theory of relativity"
    ):
        if chunk.candidates and chunk.candidates[0].finish_reason == "SAFETY":
            print("\n[Content blocked by safety filter]")
            break
        print(chunk.text, end="", flush=True)
    print()
except ClientError as e:
    if e.code == 429:
        print("\nRate limited during streaming")
    else:
        print(f"\nClient error {e.code}: {e.message}")
except ServerError as e:
    print(f"\nServer error {e.code}: {e.message}")
```

## cURL Examples

### Example: SSE Streaming

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?alt=sse" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Write a poem about the stars"}]}]
  }'
```

## Comparison with Other APIs

### vs OpenAI

- **Activation**: Gemini: separate endpoint | OpenAI: `stream: true` parameter
- **SSE format**: Gemini: `data: {json}` | OpenAI: `data: {json}` (similar)
- **End signal**: Gemini: final chunk with finishReason | OpenAI: `data: [DONE]`
- **Chunk identity**: Gemini: `responseId` | OpenAI: `id` field
- **Token usage**: Gemini: in final chunk `usageMetadata` | OpenAI: in final chunk `usage` (with `stream_options`)

### vs Anthropic

- **Activation**: Gemini: separate endpoint | Anthropic: `stream: true` parameter
- **Event types**: Gemini: single `data` event type | Anthropic: typed events (message_start, content_block_delta, etc.)
- **Chunk structure**: Gemini: full GenerateContentResponse | Anthropic: delta events with type discrimination
- **Token usage**: Gemini: final chunk only | Anthropic: message_start + message_delta events

## Error Responses

Same as generateContent. Errors during streaming may terminate the stream mid-response. See GEMAPI-IN03.

## Rate Limiting / Throttling

Same rate limits as generateContent. Each streaming request counts as one request for RPM. Token counts include all streamed tokens. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] REST streaming requires `?alt=sse` query parameter (GEMAPI-SC-GOOG-TXTGEN)
- Network disconnections during streaming lose partial responses (no resume)

## Gotchas and Quirks

- Separate endpoint (`streamGenerateContent`) not a parameter - easy migration mistake
- Must append `?alt=sse` in REST calls; SDK handles this automatically
- No `data: [DONE]` terminator like OpenAI - detect end via `finishReason` in last chunk
- `usageMetadata` only in final chunk - cannot track token consumption mid-stream
- Intermediate chunks may have empty `text` (e.g., thinking model producing thought tokens)

## Sources

- GEMAPI-SC-GOOG-GENCNT: https://ai.google.dev/api/generate-content [VERIFIED]
- GEMAPI-SC-GOOG-APIOVW: https://ai.google.dev/gemini-api/docs/api-overview [VERIFIED]
- GEMAPI-SC-GOOG-TXTGEN: https://ai.google.dev/gemini-api/docs/text-generation [VERIFIED]

## Document History

**[2026-03-20 07:25]**
- Fixed: Streaming error handling used google.api_core.exceptions (not installed with google-genai)
- Added: SDK-verified correction using google.genai.errors
- Source: google-genai v1.68.0, google/genai/errors.py

**[2026-03-20 03:20]**
- Initial document created with SSE streaming documentation
