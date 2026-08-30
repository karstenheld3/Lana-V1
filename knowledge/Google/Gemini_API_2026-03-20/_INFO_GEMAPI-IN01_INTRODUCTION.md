# INFO: Gemini API Introduction

**Doc ID**: GEMAPI-IN01
**Goal**: Document the Gemini API overview, base URL, protocol, request/response format, and API versioning
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Google Gemini API is a RESTful JSON API hosted at `https://generativelanguage.googleapis.com` that provides access to Google's Gemini family of generative AI models. The API uses URL-based versioning (`/v1beta` for preview features, `/v1` for stable) with the model name embedded in the URL path rather than the request body. The primary endpoint `generateContent` accepts a `contents` array of `Content` objects, each containing a `parts` array with typed data (text, inline media, file references). Roles are `user` and `model` (not `assistant`). System instructions are a separate top-level field `system_instruction`, not part of the messages array. The API supports four interaction modes: standard REST (`generateContent`), SSE streaming (`streamGenerateContent`), WebSocket bidirectional (`BidiGenerateContent`), and batch processing (`batchGenerateContent`). Additional endpoints serve embeddings, token counting, file management, context caching, and media generation (images via Imagen, video via Veo). Authentication uses the `x-goog-api-key` header. All endpoints return JSON with a `candidates` array containing generated content.

## Key Facts

- [VERIFIED] Base URL: `https://generativelanguage.googleapis.com` (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Protocol: HTTPS REST with JSON request/response bodies (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] API versions: `/v1beta` (preview), `/v1` (stable) in URL path (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] Authentication: `x-goog-api-key` header (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Model specified in URL path: `/v1beta/models/{model}:endpoint` (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Content structure: `contents` array with `Content` objects containing `parts` (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Roles: `user` and `model` (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] System instructions: separate `system_instruction` field (GEMAPI-SC-GOOG-TXTGEN)

## Use Cases

- **Text generation**: Single-turn or multi-turn text conversations
- **Multimodal understanding**: Process text + images, audio, video, documents
- **Code generation**: Generate, explain, and debug code
- **Data extraction**: Extract structured data from unstructured input
- **Real-time interaction**: Voice/video agents via Live API
- **Batch processing**: Async bulk workload processing

## Quick Reference

**Base URL**: `https://generativelanguage.googleapis.com`
**Auth**: `x-goog-api-key: YOUR_API_KEY`
**Content-Type**: `application/json`
**API Version**: `/v1beta` (preview) or `/v1` (stable)

**Primary Endpoints:**
- `POST /v1beta/models/{model}:generateContent` - Standard generation
- `POST /v1beta/models/{model}:streamGenerateContent` - SSE streaming
- `WS /v1beta/models/{model}:bidiGenerateContent` - Live API (WebSocket)
- `POST /v1beta/models/{model}:batchGenerateContent` - Batch processing
- `POST /v1beta/models/{model}:embedContent` - Embeddings
- `POST /v1beta/models/{model}:countTokens` - Token counting

## API Architecture

### URL Structure

All Gemini API endpoints follow the pattern:

```
https://generativelanguage.googleapis.com/{version}/models/{model}:{method}
```

- **version**: `v1beta` for preview features, `v1` for stable
- **model**: Model identifier (e.g., `gemini-2.5-flash`, `gemini-3-flash-preview`)
- **method**: API method (e.g., `generateContent`, `streamGenerateContent`)

### Interaction Modes

- **Standard (REST)**: `generateContent` - sends request, receives complete response
- **Streaming (SSE)**: `streamGenerateContent` - same request, response chunks via SSE
- **Live (WebSocket)**: `BidiGenerateContent` - stateful bidirectional real-time streaming
- **Batch (REST)**: `batchGenerateContent` - async bulk processing

## REST API

### Request Structure

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

**Headers:**
- `x-goog-api-key`: Required. Your API key
- `Content-Type`: application/json

**Request Body:**

```json
{
  "system_instruction": {
    "parts": [
      { "text": "You are a helpful assistant." }
    ]
  },
  "contents": [
    {
      "role": "user",
      "parts": [
        { "text": "Hello, how are you?" }
      ]
    },
    {
      "role": "model",
      "parts": [
        { "text": "I am doing well, thank you!" }
      ]
    },
    {
      "role": "user",
      "parts": [
        { "text": "Tell me a joke." }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 1.0,
    "topP": 0.95,
    "topK": 40,
    "maxOutputTokens": 8192,
    "responseMimeType": "text/plain"
  },
  "safetySettings": [
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
  ]
}
```

**Top-Level Parameters:**
- **system_instruction** (object, optional): System prompt as a Content object with `parts`
- **contents** (array, required): Conversation turns as Content objects
- **generationConfig** (object, optional): Generation parameters
- **safetySettings** (array, optional): Per-request safety thresholds
- **tools** (array, optional): Tool/function declarations
- **toolConfig** (object, optional): Tool calling configuration
- **cachedContent** (string, optional): Reference to cached content

**Content Object:**
- **role** (string): `user` or `model`
- **parts** (array): List of Part objects

**Part Object Types:**
- `{"text": "..."}` - Text content
- `{"inlineData": {"mimeType": "image/jpeg", "data": "base64..."}}` - Inline media
- `{"fileData": {"mimeType": "application/pdf", "fileUri": "..."}}` - File API reference
- `{"functionCall": {"name": "...", "args": {...}}}` - Function call (from model)
- `{"functionResponse": {"name": "...", "response": {...}}}` - Function result (from user)

**GenerationConfig Parameters:**
- **temperature** (float, 0.0-2.0): Randomness control
- **topP** (float, 0.0-1.0): Nucleus sampling
- **topK** (integer): Top-k sampling
- **maxOutputTokens** (integer): Maximum response tokens
- **responseMimeType** (string): `text/plain` or `application/json`
- **responseSchema** (object): JSON Schema for structured output
- **stopSequences** (array of strings): Up to 5 stop sequences
- **candidateCount** (integer): Number of candidates to generate

### Response Structure

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          { "text": "Here is a joke for you..." }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0,
      "safetyRatings": [
        {
          "category": "HARM_CATEGORY_HARASSMENT",
          "probability": "NEGLIGIBLE"
        }
      ]
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 25,
    "candidatesTokenCount": 42,
    "totalTokenCount": 67
  },
  "modelVersion": "gemini-2.5-flash",
  "responseId": "abc123..."
}
```

**Response Fields:**
- **candidates** (array): Generated response candidates
  - **content** (Content): Generated content with role `model`
  - **finishReason** (string): `STOP`, `MAX_TOKENS`, `SAFETY`, `RECITATION`, `OTHER`
  - **index** (integer): Candidate index
  - **safetyRatings** (array): Per-category safety assessments
  - **citationMetadata** (object): Citation information if applicable
- **usageMetadata** (object): Token usage statistics
  - **promptTokenCount** (integer): Input tokens
  - **candidatesTokenCount** (integer): Output tokens
  - **totalTokenCount** (integer): Total tokens
- **modelVersion** (string): Model version used
- **responseId** (string): Unique response identifier (ties streaming chunks together)

### Streaming Response

Streaming via `streamGenerateContent` returns the same structure but as SSE chunks. Each chunk contains a partial `candidates` array. All chunks share the same `responseId`.

```
data: {"candidates":[{"content":{"parts":[{"text":"Here"}],"role":"model"},"index":0}],"responseId":"abc123"}

data: {"candidates":[{"content":{"parts":[{"text":" is a joke"}],"role":"model"},"index":0}],"responseId":"abc123"}

data: {"candidates":[{"content":{"parts":[{"text":"..."}],"role":"model"},"finishReason":"STOP","index":0}],"usageMetadata":{"promptTokenCount":25,"candidatesTokenCount":42,"totalTokenCount":67},"responseId":"abc123"}
```

## Python Examples

### Example 1: Basic Text Generation

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words"
)
print(response.text)
```

### Example 2: System Instruction with Configuration

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful coding assistant. Always include comments.",
        temperature=0.7,
        max_output_tokens=2048,
    ),
    contents="Write a Python function to calculate Fibonacci numbers"
)
print(response.text)
```

### Example 3: Multi-Turn Conversation

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[types.Part(text="What is the capital of France?")]),
        types.Content(role="model", parts=[types.Part(text="The capital of France is Paris.")]),
        types.Content(role="user", parts=[types.Part(text="What is its population?")]),
    ]
)
print(response.text)
```

### Example 4: Multimodal Input (Text + Image)

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open("photo.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(
            role="user",
            parts=[
                types.Part(inline_data=types.Blob(
                    mime_type="image/jpeg",
                    data=image_data
                )),
                types.Part(text="What is in this picture?"),
            ]
        )
    ]
)
print(response.text)
```

## cURL Examples

### Example 1: Basic Text Generation

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          { "text": "Explain how AI works in a few words" }
        ]
      }
    ]
  }'
```

### Example 2: With System Instruction

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "system_instruction": {
      "parts": [{ "text": "You are a cat. Your name is Neko." }]
    },
    "contents": [
      {
        "parts": [{ "text": "Hello there" }]
      }
    ]
  }'
```

### Example 3: Multi-Turn Chat

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "contents": [
      { "role": "user", "parts": [{ "text": "Hello." }] },
      { "role": "model", "parts": [{ "text": "Hello! How can I help?" }] },
      { "role": "user", "parts": [{ "text": "Write a poem about the ocean." }] }
    ]
  }'
```

## Comparison with Other APIs

### vs OpenAI

- **Base URL**: Gemini: `generativelanguage.googleapis.com` | OpenAI: `api.openai.com`
- **Model specification**: Gemini: in URL path `/models/{model}:method` | OpenAI: `model` field in request body
- **Auth header**: Gemini: `x-goog-api-key` | OpenAI: `Authorization: Bearer`
- **Message structure**: Gemini: `contents[].parts[]` | OpenAI: `messages[].content`
- **Role names**: Gemini: `user`/`model` | OpenAI: `system`/`user`/`assistant`/`tool`
- **System prompt**: Gemini: separate `system_instruction` field | OpenAI: `system` role in messages
- **Streaming**: Gemini: separate endpoint (`streamGenerateContent`) | OpenAI: `stream: true` parameter
- **API versioning**: Gemini: URL path (`/v1beta`, `/v1`) | OpenAI: `openai-version` header
- **Temperature range**: Gemini: 0.0-2.0 | OpenAI: 0.0-2.0 (same)

### vs Anthropic

- **Base URL**: Gemini: `generativelanguage.googleapis.com` | Anthropic: `api.anthropic.com`
- **Auth header**: Gemini: `x-goog-api-key` | Anthropic: `x-api-key`
- **Message structure**: Gemini: `contents[].parts[]` | Anthropic: `messages[].content`
- **Role names**: Gemini: `user`/`model` | Anthropic: `user`/`assistant`
- **System prompt**: Gemini: `system_instruction` (Content object) | Anthropic: `system` (string or array)
- **Versioning**: Gemini: URL path | Anthropic: `anthropic-version` header
- **Temperature range**: Gemini: 0.0-2.0 | Anthropic: 0.0-1.0
- **Context window**: Gemini: up to 2M tokens | Anthropic: 200K tokens
- **Multiple interaction modes**: Gemini has 4 modes (REST/SSE/WebSocket/batch) | Anthropic has 2 (REST/SSE)

## Error Responses

- **400 Bad Request**: Invalid request body, unsupported parameters, model parameter errors
- **401 Unauthorized**: Missing or invalid API key
- **403 Forbidden**: API key lacks permissions or is restricted
- **404 Not Found**: Invalid model name or endpoint
- **429 Too Many Requests**: Rate limit exceeded (RPM, TPM, or RPD)
- **500 Internal Server Error**: Server-side error, retry with backoff
- **503 Service Unavailable**: Temporary overload, retry with backoff

## Rate Limiting / Throttling

Standard Gemini API rate limits apply. Rate limits depend on model and usage tier (Free, Tier 1-3). Limits measured in RPM, TPM, and RPD. See GEMAPI-IN04 for details.

## Limitations and Known Issues

- [VERIFIED] API version `/v1beta` required for many features; `/v1` has limited feature set (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] Preview/experimental models have more restricted rate limits (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Thinking enabled by default on 2.5+ models, increasing latency and token usage (GEMAPI-SC-GOOG-TROUBL)

## Gotchas and Quirks

- Model is specified in the URL path, not the request body - forgetting to change the model in the URL is a common migration mistake from OpenAI
- The `role` field uses `model` (not `assistant`) - will cause errors if using OpenAI conventions
- System instructions use a `Content` object with `parts`, not a plain string
- When `role` is omitted from a single-turn request, it defaults to `user`
- The `contents` field uses `parts` (array of typed objects), not a simple `content` string

## Sources

- GEMAPI-SC-GOOG-APIOVW: https://ai.google.dev/gemini-api/docs/api-overview [VERIFIED]
- GEMAPI-SC-GOOG-DOCS: https://ai.google.dev/gemini-api/docs [VERIFIED]
- GEMAPI-SC-GOOG-TXTGEN: https://ai.google.dev/gemini-api/docs/text-generation [VERIFIED]
- GEMAPI-SC-GOOG-TROUBL: https://ai.google.dev/gemini-api/docs/troubleshooting [VERIFIED]

## Document History

**[2026-03-20 02:45]**
- Initial document created with full request/response schemas and comparison
