# INFO: Gemini API Token Counting

**Doc ID**: GEMAPI-IN25
**Goal**: Document the countTokens endpoint, tokenization, and billing token categories
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini API provides a `countTokens` endpoint (`POST /v1beta/models/{model}:countTokens`) that returns the exact token count for a given request before execution, enabling cost estimation and context window management. The endpoint accepts the same request body as `generateContent` (contents, systemInstruction, tools) and returns `totalTokens` plus optional `cachedContentTokenCount`. Token counts are model-specific. Response `usageMetadata` in `generateContent` provides actual consumption: `promptTokenCount`, `candidatesTokenCount`, `totalTokenCount`, `thoughtsTokenCount`, and `cachedContentTokenCount`. Multimodal inputs (images, audio, video) are converted to visual/audio tokens with model-specific rates. The Python SDK provides `count_tokens()` for direct access. Unlike OpenAI's tiktoken library for offline counting, Gemini requires an API call for accurate counts.

## Key Facts

- [VERIFIED] Endpoint: `POST /v1beta/models/{model}:countTokens` (GEMAPI-SC-GOOG-TOKENS)
- [VERIFIED] Same request body as generateContent (GEMAPI-SC-GOOG-TOKENS)
- [VERIFIED] Returns totalTokens and cachedContentTokenCount (GEMAPI-SC-GOOG-TOKENS)
- [VERIFIED] Token counts are model-specific (GEMAPI-SC-GOOG-TOKENS)
- [VERIFIED] usageMetadata in response: prompt, candidates, total, thoughts, cached (GEMAPI-SC-GOOG-GENCNT)

## Quick Reference

**Endpoint**: `POST /v1beta/models/{model}:countTokens`
**SDK**: `client.models.count_tokens(model, contents)`

## REST API

### Request

```json
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:countTokens

{
  "contents": [
    {"role": "user", "parts": [{"text": "Hello, how are you?"}]}
  ],
  "systemInstruction": {
    "parts": [{"text": "You are a helpful assistant."}]
  }
}
```

### Response

```json
{
  "totalTokens": 12
}
```

### Usage Metadata in generateContent Response

```json
{
  "usageMetadata": {
    "promptTokenCount": 100,
    "candidatesTokenCount": 250,
    "totalTokenCount": 400,
    "thoughtsTokenCount": 50,
    "cachedContentTokenCount": 0
  }
}
```

**Token Categories:**
- **promptTokenCount**: Input tokens (user content + system instruction)
- **candidatesTokenCount**: Output tokens (model response)
- **thoughtsTokenCount**: Thinking/reasoning tokens (billed, not visible in output)
- **cachedContentTokenCount**: Tokens served from cache (reduced rate)
- **totalTokenCount**: Sum of all token categories

## Python Examples

### Example 1: Count Tokens Before Sending

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = "Explain the theory of general relativity in detail."

token_count = client.models.count_tokens(
    model="gemini-2.5-flash",
    contents=prompt
)
print(f"Token count: {token_count.total_tokens}")

# Check against model limits before sending
model_info = client.models.get(model="gemini-2.5-flash")
print(f"Input limit: {model_info.input_token_limit}")

if token_count.total_tokens < model_info.input_token_limit:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    print(f"\nResponse tokens: {response.usage_metadata.total_token_count}")
```

### Example 2: Count Multimodal Tokens

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open("photo.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

token_count = client.models.count_tokens(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[
            types.Part(inline_data=types.Blob(
                mime_type="image/jpeg", data=image_data
            )),
            types.Part(text="Describe this image"),
        ])
    ]
)
print(f"Total tokens (text + image): {token_count.total_tokens}")
```

## cURL Examples

### Example: Count Tokens

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:countTokens" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Hello world"}]}]
  }'
```

## Comparison with Other APIs

### vs OpenAI

- **Token counting**: Gemini: API call required | OpenAI: tiktoken library (offline) + API usage
- **Pre-request**: Gemini: countTokens endpoint | OpenAI: tiktoken estimate
- **Response metadata**: Both include usage in response
- **Thinking tokens**: Gemini: `thoughtsTokenCount` | OpenAI: `completion_tokens_details.reasoning_tokens`

### vs Anthropic

- **Token counting**: Gemini: API endpoint | Anthropic: token_count in response only (no pre-count API)
- **Pre-request estimation**: Gemini: exact count via API | Anthropic: approximate via tokenizer
- **Cache tokens**: Both report cached token counts separately

## Error Responses

- **400**: Invalid content format
- **404**: Invalid model name

## Rate Limiting / Throttling

countTokens counts toward RPM but typically has higher limits. See GEMAPI-IN04.

## Limitations and Known Issues

- Token counts are model-specific - same content may have different counts across models
- Multimodal token counts can be surprisingly high (images, video, audio)

## Gotchas and Quirks

- Must make an API call to count tokens (no offline library like OpenAI's tiktoken)
- countTokens is cheap but still counts toward rate limits
- Image/video/audio token costs are significant - always check before sending large media
- `thoughtsTokenCount` appears in response but cannot be pre-counted (model decides at runtime)
- `totalTokenCount` includes ALL categories: prompt + candidates + thoughts

## Sources

- GEMAPI-SC-GOOG-TOKENS: https://ai.google.dev/gemini-api/docs/tokens [VERIFIED]
- GEMAPI-SC-GOOG-GENCNT: https://ai.google.dev/api/generate-content [VERIFIED]

## Document History

**[2026-03-20 04:45]**
- Initial document created
