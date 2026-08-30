# INFO: Gemini API System Instructions

**Doc ID**: GEMAPI-IN35
**Goal**: Document system_instruction field, best practices, and interaction with other features
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini API system instructions are provided as a separate top-level `system_instruction` field in the request body, using a Content object format with a `parts` array. Unlike OpenAI (system role in messages array) and Anthropic (top-level `system` string/array), Gemini's system instructions are structurally separate from the conversation history and use the same Content object format as user/model messages. System instructions can include text and file references (e.g., uploaded documents as reference material). They persist across the conversation without being repeated in each turn. System instructions are processed before the conversation content and can be cached via context caching for cost savings on repeated use. In the Live API, system instructions are set in the WebSocket setup message and persist for the session duration.

## Key Facts

- [VERIFIED] Field: `system_instruction` (top-level, separate from contents) (GEMAPI-SC-GOOG-TXTGEN)
- [VERIFIED] Format: Content object with `parts` array (GEMAPI-SC-GOOG-GENCNT)
- [VERIFIED] Can include text and file references (GEMAPI-SC-GOOG-TXTGEN)
- [VERIFIED] Cacheable via context caching (GEMAPI-SC-GOOG-CACHNG)
- [VERIFIED] Persists in Live API for full session (GEMAPI-SC-GOOG-LIVAPI)

## Quick Reference

**REST field**: `system_instruction`
**SDK config**: `system_instruction` in GenerateContentConfig
**Format**: `{"parts": [{"text": "..."}]}`

## REST API

### Basic System Instruction

```json
{
  "system_instruction": {
    "parts": [
      {"text": "You are a helpful coding assistant. Always include code comments. Use Python 3.12 syntax."}
    ]
  },
  "contents": [
    {"role": "user", "parts": [{"text": "Write a fibonacci function"}]}
  ]
}
```

### System Instruction with File Reference

```json
{
  "system_instruction": {
    "parts": [
      {"text": "You are a customer support agent. Use the following product manual as reference:"},
      {"fileData": {"mimeType": "application/pdf", "fileUri": "https://generativelanguage.googleapis.com/v1beta/files/abc123"}}
    ]
  },
  "contents": [
    {"role": "user", "parts": [{"text": "How do I reset the device?"}]}
  ]
}
```

## Python Examples

### Example 1: Basic System Instruction

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a pirate. Respond in pirate speak. Keep responses under 3 sentences."
    ),
    contents="What is the weather like today?"
)
print(response.text)
```

### Example 2: Multi-Part System Instruction

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=types.Content(
            parts=[
                types.Part(text="You are a senior Python developer."),
                types.Part(text="Rules: 1) Always add type hints. 2) Include docstrings. 3) Handle errors with try/except."),
            ]
        )
    ),
    contents="Write a function to read a CSV file and return the average of a column"
)
print(response.text)
```

### Example 3: Cached System Instruction

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Upload reference document
uploaded = client.files.upload(file="product_manual.pdf")
while uploaded.state == "PROCESSING":
    time.sleep(2)
    uploaded = client.files.get(name=uploaded.name)

# Cache system instruction + document
cache = client.caches.create(
    model="gemini-2.5-flash",
    config=types.CreateCachedContentConfig(
        system_instruction="You are a support agent. Answer questions using only the provided manual.",
        contents=[
            types.Content(role="user", parts=[
                types.Part(file_data=types.FileData(
                    mime_type="application/pdf", file_uri=uploaded.uri
                ))
            ])
        ],
        ttl="3600s",
    )
)

# Use cached system instruction for multiple queries
for q in ["How to setup?", "How to troubleshoot?", "Warranty info?"]:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        cached_content=cache.name,
        contents=q
    )
    print(f"Q: {q}\nA: {response.text[:150]}...\n")
```

## Comparison with Other APIs

### vs OpenAI

- **Format**: Gemini: `system_instruction` (Content object) | OpenAI: `system` role in messages array
- **Separation**: Gemini: separate field | OpenAI: part of messages history
- **File reference**: Gemini: can include fileData | OpenAI: text only in system message
- **Caching**: Gemini: explicit cache | OpenAI: automatic caching

### vs Anthropic

- **Format**: Gemini: Content object with parts | Anthropic: `system` (string or content blocks)
- **Separation**: Both: separate from messages
- **File reference**: Gemini: fileData in parts | Anthropic: base64/URL content blocks
- **Caching**: Gemini: explicit | Anthropic: `cache_control` blocks

## Error Responses

- **400**: Invalid system_instruction format

## Rate Limiting / Throttling

System instruction tokens count toward TPM. Cache to reduce cost. See GEMAPI-IN04.

## Limitations and Known Issues

- System instructions are advisory - model may not follow all instructions perfectly
- Very long system instructions consume context window tokens

## Gotchas and Quirks

- Uses Content object format (with `parts`), not a plain string in REST
- SDK accepts plain string shorthand: `system_instruction="text"` (auto-wrapped)
- `system_instruction` is NOT in the `contents` array - separate top-level field
- When using `cachedContent`, do NOT also set `system_instruction` (it's in the cache)
- File references in system instructions count as tokens
- No `role` field needed in system_instruction Content object

## Sources

- GEMAPI-SC-GOOG-TXTGEN: https://ai.google.dev/gemini-api/docs/text-generation [VERIFIED]
- GEMAPI-SC-GOOG-GENCNT: https://ai.google.dev/api/generate-content [VERIFIED]
- GEMAPI-SC-GOOG-CACHNG: https://ai.google.dev/gemini-api/docs/caching [VERIFIED]

## Document History

**[2026-03-20 05:35]**
- Initial document created
