# INFO: Gemini API Generate Content

**Doc ID**: GEMAPI-IN07
**Goal**: Document the primary generateContent endpoint with full request/response schemas
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The `generateContent` endpoint (`POST /v1beta/models/{model}:generateContent`) is the primary interface for all content generation in the Gemini API. It accepts a JSON request body containing `contents` (conversation turns as Content objects with typed `parts`), `systemInstruction` (system prompt), `generationConfig` (temperature, topP, topK, maxOutputTokens, responseMimeType, responseSchema, stopSequences), `safetySettings` (per-request harm thresholds), `tools` (function declarations and built-in tools), and `toolConfig` (function calling mode). The response returns a `candidates` array with generated content, `finishReason`, `safetyRatings`, `citationMetadata`, plus `usageMetadata` with token counts and `modelVersion`. The same request body is used for streaming via `streamGenerateContent`. Multi-turn conversations pass full history in `contents`. System instructions are a separate top-level field using Content object format, not embedded in messages. The model is specified in the URL path, not the request body.

## Key Facts

- [VERIFIED] Endpoint: `POST /v1beta/models/{model}:generateContent` (GEMAPI-SC-GOOG-GENCNT)
- [VERIFIED] Streaming: `POST /v1beta/models/{model}:streamGenerateContent` (same request body) (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Request uses `contents` array of Content objects with `parts` (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Roles: `user` and `model` (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] System instruction is separate `system_instruction` field (GEMAPI-SC-GOOG-TXTGEN)
- [VERIFIED] Response: `candidates` array with content, finishReason, safetyRatings (GEMAPI-SC-GOOG-APIOVW)
- [VERIFIED] Streaming chunks share same `responseId` (GEMAPI-SC-GOOG-APIOVW)

## Quick Reference

**Endpoint**: `POST /v1beta/models/{model}:generateContent`
**Streaming**: `POST /v1beta/models/{model}:streamGenerateContent`
**Auth**: `x-goog-api-key: YOUR_API_KEY`
**Content-Type**: `application/json`

## REST API

### Request

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

**Full Request Body Schema:**

```json
{
  "system_instruction": {
    "parts": [{ "text": "System prompt text" }]
  },
  "contents": [
    {
      "role": "user",
      "parts": [
        { "text": "User message" },
        { "inlineData": { "mimeType": "image/jpeg", "data": "base64..." } },
        { "fileData": { "mimeType": "application/pdf", "fileUri": "files/abc123" } }
      ]
    },
    {
      "role": "model",
      "parts": [
        { "text": "Model response" },
        { "functionCall": { "name": "func_name", "args": {} } }
      ]
    },
    {
      "role": "user",
      "parts": [
        { "functionResponse": { "name": "func_name", "response": {} } }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 1.0,
    "topP": 0.95,
    "topK": 40,
    "maxOutputTokens": 8192,
    "candidateCount": 1,
    "stopSequences": ["END"],
    "responseMimeType": "text/plain",
    "responseSchema": {},
    "presencePenalty": 0.0,
    "frequencyPenalty": 0.0,
    "responseLogprobs": false,
    "logprobs": 0,
    "thinkingConfig": {
      "thinkingBudget": 1024
    }
  },
  "safetySettings": [
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
  ],
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": "function_name",
          "description": "What the function does",
          "parameters": {
            "type": "object",
            "properties": {
              "param1": { "type": "string", "description": "Param description" }
            },
            "required": ["param1"]
          }
        }
      ]
    }
  ],
  "toolConfig": {
    "functionCallingConfig": {
      "mode": "AUTO",
      "allowedFunctionNames": ["function_name"]
    }
  },
  "cachedContent": "cachedContents/abc123"
}
```

**Top-Level Parameters:**
- **system_instruction** (Content, optional): System prompt. Parts array with text
- **contents** (array of Content, required): Conversation turns
- **generationConfig** (object, optional): Generation parameters
- **safetySettings** (array, optional): Per-request safety thresholds
- **tools** (array, optional): Function declarations and built-in tools
- **toolConfig** (object, optional): Tool calling configuration
- **cachedContent** (string, optional): Reference to cached content resource name

**Content Object:**
- **role** (string): `user` or `model`
- **parts** (array of Part): Content data

**Part Types:**
- **text** (string): Text content
- **inlineData** (Blob): `{mimeType, data}` - base64-encoded media
- **fileData** (FileData): `{mimeType, fileUri}` - File API reference
- **functionCall** (FunctionCall): `{name, args}` - Model's function call request
- **functionResponse** (FunctionResponse): `{name, response}` - User's function result
- **executableCode** (ExecutableCode): Code execution input
- **codeExecutionResult** (CodeExecutionResult): Code execution output

**GenerationConfig Parameters:**
- **temperature** (float, 0.0-2.0): Controls randomness. 0=deterministic, 2=creative
- **topP** (float, 0.0-1.0): Nucleus sampling probability threshold
- **topK** (integer): Number of highest probability tokens to consider
- **maxOutputTokens** (integer): Maximum number of output tokens
- **candidateCount** (integer): Number of response candidates (default 1)
- **stopSequences** (array of string): Up to 5 sequences that stop generation
- **responseMimeType** (string): `text/plain` (default) or `application/json`
- **responseSchema** (object): JSON Schema for structured output (requires `application/json`)
- **presencePenalty** (float): Penalizes repeated tokens
- **frequencyPenalty** (float): Penalizes frequent tokens
- **responseLogprobs** (boolean): Return log probabilities
- **logprobs** (integer): Number of top log probabilities
- **thinkingConfig** (object): Thinking/reasoning configuration
  - **thinkingBudget** (integer): Token budget for reasoning (Gemini 2.5)
  - **thinkingLevel** (string): off/low/default/high (Gemini 3)

### Response

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          { "text": "Generated response text..." }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0,
      "safetyRatings": [
        {
          "category": "HARM_CATEGORY_HARASSMENT",
          "probability": "NEGLIGIBLE",
          "blocked": false
        }
      ],
      "citationMetadata": {
        "citationSources": [
          {
            "startIndex": 0,
            "endIndex": 50,
            "uri": "https://example.com",
            "license": ""
          }
        ]
      },
      "groundingMetadata": {
        "webSearchQueries": ["search query"],
        "groundingChunks": [],
        "groundingSupports": []
      }
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 100,
    "candidatesTokenCount": 250,
    "totalTokenCount": 350,
    "thoughtsTokenCount": 50,
    "cachedContentTokenCount": 0
  },
  "modelVersion": "gemini-2.5-flash",
  "responseId": "unique-response-id"
}
```

**Response Fields:**
- **candidates** (array): Response candidates
  - **content** (Content): Generated content with `role: "model"`
  - **finishReason** (string): STOP, MAX_TOKENS, SAFETY, RECITATION, OTHER
  - **index** (integer): Candidate index
  - **safetyRatings** (array): Per-category safety assessments
  - **citationMetadata** (object): Source citations
  - **groundingMetadata** (object): Google Search grounding data (if enabled)
- **usageMetadata** (object): Token consumption
  - **promptTokenCount** (integer): Input tokens
  - **candidatesTokenCount** (integer): Output tokens
  - **totalTokenCount** (integer): All tokens
  - **thoughtsTokenCount** (integer): Thinking tokens (if thinking enabled)
  - **cachedContentTokenCount** (integer): Tokens from cache
- **modelVersion** (string): Exact model version used
- **responseId** (string): Unique response ID (shared across streaming chunks)

## Python Examples

### Example 1: Basic Generation

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain quantum computing in simple terms"
)
print(response.text)
print(f"Tokens: {response.usage_metadata.total_token_count}")
```

### Example 2: Full Configuration

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a concise technical writer.",
        temperature=0.3,
        top_p=0.9,
        max_output_tokens=4096,
        stop_sequences=["---"],
    ),
    contents="Write documentation for a REST API endpoint"
)
print(response.text)
```

### Example 3: Multi-Turn with Roles

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

history = [
    types.Content(role="user", parts=[types.Part(text="What is Python?")]),
    types.Content(role="model", parts=[types.Part(text="Python is a programming language.")]),
    types.Content(role="user", parts=[types.Part(text="What are its main features?")]),
]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=history
)
print(response.text)
```

### Example 4: Streaming

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="Write a long story about space exploration"
):
    print(chunk.text, end="")
print()
```

### Example 5: JSON Structured Output

```python
from google import genai
from google.genai import types
from pydantic import BaseModel
import os

class CityInfo(BaseModel):
    name: str
    country: str
    population: int
    landmarks: list[str]

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=CityInfo.model_json_schema(),
    ),
    contents="Tell me about Paris"
)

city = CityInfo.model_validate_json(response.text)
print(f"{city.name}, {city.country} - Pop: {city.population}")
```

## cURL Examples

### Example 1: Simple Text Generation

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "What is machine learning?"}]}]
  }'
```

### Example 2: With System Instruction and Config

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "system_instruction": {
      "parts": [{"text": "Respond in exactly 3 bullet points."}]
    },
    "contents": [{"parts": [{"text": "Benefits of exercise"}]}],
    "generationConfig": {
      "temperature": 0.5,
      "maxOutputTokens": 256
    }
  }'
```

### Example 3: Streaming

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?alt=sse" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Write a poem about the ocean"}]}]
  }'
```

## Comparison with Other APIs

### vs OpenAI

- **Endpoint**: Gemini: `/models/{model}:generateContent` | OpenAI: `/v1/chat/completions`
- **Model location**: Gemini: URL path | OpenAI: request body `model` field
- **Message format**: Gemini: `contents[].parts[]` | OpenAI: `messages[].content`
- **System prompt**: Gemini: `system_instruction` (Content object) | OpenAI: `system` role message
- **Streaming**: Gemini: separate endpoint + `?alt=sse` | OpenAI: `stream: true` param
- **Response wrapper**: Gemini: `candidates[].content.parts[].text` | OpenAI: `choices[].message.content`
- **Token metadata**: Gemini: `usageMetadata` includes `thoughtsTokenCount` | OpenAI: `usage`
- **Thinking tokens**: Gemini: reported in `thoughtsTokenCount` | OpenAI: in `completion_tokens_details`

### vs Anthropic

- **Endpoint**: Gemini: `:generateContent` | Anthropic: `/v1/messages`
- **Content parts**: Gemini: typed `parts` array | Anthropic: `content` blocks with `type`
- **System prompt**: Gemini: Content object in `system_instruction` | Anthropic: `system` string/array
- **Finish reason**: Gemini: `finishReason` | Anthropic: `stop_reason`
- **Safety**: Gemini: `safetyRatings` per candidate | Anthropic: no per-response safety ratings
- **Model role name**: Gemini: `model` | Anthropic: `assistant`

## Error Responses

- **400**: Invalid parameters, missing required fields, malformed JSON
- **404**: Invalid model name
- **429**: Rate limit exceeded
- **500/503**: Server errors

See GEMAPI-IN03 for detailed error handling.

## Rate Limiting / Throttling

Standard Gemini API rate limits (RPM, TPM, RPD) apply. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Only JSON Schema subset supported for responseSchema (GEMAPI-SC-GOOG-STRUCT)
- [VERIFIED] Very large/deeply nested schemas may be rejected (GEMAPI-SC-GOOG-STRUCT)
- [VERIFIED] Thinking enabled by default on 2.5+ models increases latency (GEMAPI-SC-GOOG-TROUBL)

## Gotchas and Quirks

- Model goes in URL path, not request body - major difference from OpenAI/Anthropic
- Role `model` not `assistant` - common migration mistake
- `system_instruction` is a Content object with `parts`, not a plain string
- Streaming requires `?alt=sse` query parameter in REST (SDK handles automatically)
- `candidateCount` > 1 is rarely used and may not be supported by all models
- `finishReason` in 200 response can indicate blocked content (SAFETY, RECITATION)
- `responseId` ties streaming chunks together - useful for reassembly

## Sources

- GEMAPI-SC-GOOG-GENCNT: https://ai.google.dev/api/generate-content [VERIFIED]
- GEMAPI-SC-GOOG-TXTGEN: https://ai.google.dev/gemini-api/docs/text-generation [VERIFIED]
- GEMAPI-SC-GOOG-APIOVW: https://ai.google.dev/gemini-api/docs/api-overview [VERIFIED]
- GEMAPI-SC-GOOG-STRUCT: https://ai.google.dev/gemini-api/docs/structured-output [VERIFIED]

## Document History

**[2026-03-20 03:15]**
- Initial document created with full request/response schemas
