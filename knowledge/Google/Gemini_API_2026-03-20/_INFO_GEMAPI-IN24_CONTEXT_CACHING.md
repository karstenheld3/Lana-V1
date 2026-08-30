# INFO: Gemini API Context Caching

**Doc ID**: GEMAPI-IN24
**Goal**: Document context caching for reducing cost on repeated prompts with shared context
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Context caching allows storing frequently reused input content (system instructions, large documents, media files) on Google's servers and referencing it across multiple `generateContent` requests at reduced cost. Cached content is created via `POST /v1beta/cachedContents` with a specified model and TTL (default 1 hour). The cached content resource name is then passed in the `cachedContent` field of subsequent requests, replacing the need to re-send the same tokens. Cached tokens are billed at a reduced rate compared to standard input tokens. The cache has a minimum token count requirement (varies by model, typically 4096+ tokens). Cached content can include system instructions, conversation prefixes, and uploaded files. Cache entries can be updated (TTL extension) or deleted. This is similar to Anthropic's prompt caching but uses an explicit API rather than automatic caching.

## Key Facts

- [VERIFIED] Create: `POST /v1beta/cachedContents` (GEMAPI-SC-GOOG-CACHNG)
- [VERIFIED] Default TTL: 1 hour, configurable (GEMAPI-SC-GOOG-CACHNG)
- [VERIFIED] Minimum token count required (model-specific, typically 4096+) (GEMAPI-SC-GOOG-CACHNG)
- [VERIFIED] Cached tokens billed at reduced rate (GEMAPI-SC-GOOG-CACHNG)
- [VERIFIED] Referenced via `cachedContent` field in generateContent (GEMAPI-SC-GOOG-CACHNG)
- [VERIFIED] Can cache system instructions, content, and files (GEMAPI-SC-GOOG-CACHNG)

## Quick Reference

**Create**: `POST /v1beta/cachedContents`
**List**: `GET /v1beta/cachedContents`
**Get**: `GET /v1beta/cachedContents/{name}`
**Update**: `PATCH /v1beta/cachedContents/{name}`
**Delete**: `DELETE /v1beta/cachedContents/{name}`
**Use**: `{"cachedContent": "cachedContents/abc123"}` in generateContent

## REST API

### Create Cached Content

```json
POST https://generativelanguage.googleapis.com/v1beta/cachedContents

{
  "model": "models/gemini-2.5-flash",
  "displayName": "Legal Document Analysis Cache",
  "systemInstruction": {
    "parts": [{"text": "You are a legal document analyst. Extract key clauses and risks."}]
  },
  "contents": [
    {
      "role": "user",
      "parts": [
        {"fileData": {"mimeType": "application/pdf", "fileUri": "https://generativelanguage.googleapis.com/v1beta/files/abc123"}}
      ]
    }
  ],
  "ttl": "3600s"
}
```

**Response:**
```json
{
  "name": "cachedContents/xyz789",
  "model": "models/gemini-2.5-flash",
  "displayName": "Legal Document Analysis Cache",
  "usageMetadata": {
    "totalTokenCount": 50000
  },
  "createTime": "2026-03-20T04:00:00Z",
  "updateTime": "2026-03-20T04:00:00Z",
  "expireTime": "2026-03-20T05:00:00Z"
}
```

### Use Cached Content

```json
POST /v1beta/models/gemini-2.5-flash:generateContent

{
  "cachedContent": "cachedContents/xyz789",
  "contents": [
    {"role": "user", "parts": [{"text": "What are the termination clauses?"}]}
  ]
}
```

### Update TTL

```json
PATCH /v1beta/cachedContents/xyz789

{
  "ttl": "7200s"
}
```

## Python Examples

### Example 1: Cache Large Document

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Upload document
uploaded = client.files.upload(file="large_report.pdf")
while uploaded.state == "PROCESSING":
    time.sleep(2)
    uploaded = client.files.get(name=uploaded.name)

# Create cache
cache = client.caches.create(
    model="gemini-2.5-flash",
    config=types.CreateCachedContentConfig(
        display_name="Q4 Report Cache",
        system_instruction="You are a financial analyst. Provide detailed analysis.",
        contents=[
            types.Content(role="user", parts=[
                types.Part(file_data=types.FileData(
                    mime_type="application/pdf",
                    file_uri=uploaded.uri
                ))
            ])
        ],
        ttl="3600s",
    )
)
print(f"Cache created: {cache.name}")
print(f"Cached tokens: {cache.usage_metadata.total_token_count}")

# Query against cached content (multiple times at reduced cost)
for question in [
    "What was the total revenue?",
    "Summarize the risk factors.",
    "What are the growth projections?"
]:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        cached_content=cache.name,
        contents=question
    )
    print(f"\nQ: {question}")
    print(f"A: {response.text[:200]}...")
    print(f"Cached tokens: {response.usage_metadata.cached_content_token_count}")
```

### Example 2: Cache Management

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# List caches
for cache in client.caches.list():
    print(f"{cache.name}: {cache.display_name} (expires: {cache.expire_time})")

# Update TTL
client.caches.update(
    name="cachedContents/xyz789",
    config={"ttl": "7200s"}
)

# Delete cache
client.caches.delete(name="cachedContents/xyz789")
```

## Comparison with Other APIs

### vs OpenAI

- **Caching**: Gemini: explicit cache creation API | OpenAI: automatic prompt caching (no user API)
- **Control**: Gemini: full lifecycle management (create/update/delete) | OpenAI: automatic, no control
- **TTL**: Gemini: configurable | OpenAI: automatic eviction
- **Billing**: Gemini: reduced rate for cached tokens | OpenAI: 50% discount on cached tokens

### vs Anthropic

- **Caching**: Gemini: explicit API | Anthropic: `cache_control` blocks in request
- **Approach**: Gemini: separate cache resource | Anthropic: inline cache markers
- **TTL**: Gemini: configurable (default 1h) | Anthropic: 5 minutes (auto-extended on use)
- **Minimum**: Both have minimum token requirements
- **Billing**: Both offer reduced rates for cached tokens

## Error Responses

- **400**: Content below minimum token count, invalid model for caching
- **404**: Cache not found (expired or deleted)
- Using expired cache returns error

## Rate Limiting / Throttling

Cache creation may have separate rate limits. Cached requests use standard RPM/TPM. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Minimum token count required per model (GEMAPI-SC-GOOG-CACHNG)
- [VERIFIED] Not all models support caching (check `supportedGenerationMethods`) (GEMAPI-SC-GOOG-CACHNG)
- Cannot modify cached content - must delete and recreate

## Gotchas and Quirks

- Cache must use the SAME model as the generateContent request - cannot share across models
- Content below minimum token threshold is rejected (wasted API call)
- Cache TTL counts from creation, not last use - unlike Anthropic's auto-extension
- `cachedContent` field replaces `systemInstruction` and cached `contents` - don't duplicate
- Cached files must still be active (not expired from File API) when cache is created
- Check `cachedContentTokenCount` in response to verify cache hit

## Sources

- GEMAPI-SC-GOOG-CACHNG: https://ai.google.dev/gemini-api/docs/caching [VERIFIED]
- GEMAPI-SC-GOOG-CACHRF: https://ai.google.dev/api/caching [VERIFIED]

## Document History

**[2026-03-20 04:40]**
- Initial document created with full caching API documentation
