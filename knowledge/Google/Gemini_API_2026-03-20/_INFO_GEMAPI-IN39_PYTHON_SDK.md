# INFO: Gemini API Python SDK

**Doc ID**: GEMAPI-IN39
**Goal**: Document the google-genai Python SDK, client initialization, configuration, and patterns
**Version scope**: API v1beta, google-genai SDK, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The official Gemini Python SDK (`google-genai`) provides a high-level client for all Gemini API features. The client is initialized via `genai.Client(api_key=...)` and exposes namespaced methods: `models.generate_content()`, `models.generate_content_stream()`, `models.count_tokens()`, `models.embed_content()`, `models.generate_images()`, `models.generate_videos()`, `files.upload()`, `files.list()`, `files.get()`, `files.delete()`, `caches.create()`, `caches.list()`, `caches.update()`, `caches.delete()`, and async variants via `aio`. The SDK uses Pydantic-style types from `google.genai.types` for configuration. Automatic function calling is a Python SDK-exclusive feature where the SDK handles the function call/response loop. The SDK supports both Google AI (API key) and Vertex AI (service account) backends via the same interface. Install via `pip install google-genai`.

## Key Facts

- [VERIFIED] Package: `google-genai` (pip install google-genai) (GEMAPI-SC-GOOG-PYTSDK)
- [VERIFIED] Client: `genai.Client(api_key=...)` (GEMAPI-SC-GOOG-PYTSDK)
- [VERIFIED] Namespaced: models, files, caches, batches (GEMAPI-SC-GOOG-PYTSDK)
- [VERIFIED] Types: `google.genai.types` for configuration (GEMAPI-SC-GOOG-PYTSDK)
- [VERIFIED] Automatic function calling: Python SDK exclusive (GEMAPI-SC-GOOG-FUNCAL)
- [VERIFIED] Async support via `client.aio` namespace (GEMAPI-SC-GOOG-PYTSDK)
- [VERIFIED] Dual backend: Google AI (API key) and Vertex AI (service account) (GEMAPI-SC-GOOG-PYTSDK)

## Quick Reference

**Install**: `pip install google-genai`
**Import**: `from google import genai`
**Types**: `from google.genai import types`
**Client**: `client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])`

## Installation

```bash
pip install google-genai
```

## Client Initialization

### Google AI (API Key)

```python
from google import genai
import os

# From environment variable (recommended)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Explicit key (development only)
client = genai.Client(api_key="YOUR_API_KEY")
```

### Vertex AI (Service Account)

```python
from google import genai

client = genai.Client(
    vertexai=True,
    project="your-project-id",
    location="us-central1"
)
```

### Custom HTTP Options

```python
from google import genai

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options={"api_version": "v1alpha"}  # For preview features
)
```

## SDK Method Reference

### Content Generation

```python
# Synchronous
response = client.models.generate_content(model, contents, config=...)

# Streaming
for chunk in client.models.generate_content_stream(model, contents, config=...):
    print(chunk.text)

# Async
response = await client.aio.models.generate_content(model, contents, config=...)

# Async streaming
async for chunk in client.aio.models.generate_content_stream(model, contents, config=...):
    print(chunk.text)
```

### Token Counting

```python
result = client.models.count_tokens(model, contents)
print(result.total_tokens)
```

### Embeddings

```python
result = client.models.embed_content(model, contents, config=...)
print(result.embeddings[0].values)
```

### File Management

```python
uploaded = client.files.upload(file="path/to/file")
files = client.files.list()
file_info = client.files.get(name="files/abc123")
client.files.delete(name="files/abc123")
```

### Caching

```python
cache = client.caches.create(model, config=...)
caches = client.caches.list()
client.caches.update(name, config=...)
client.caches.delete(name)
```

### Live API

```python
async with client.aio.live.connect(model, config=...) as session:
    await session.send(input="Hello", end_of_turn=True)
    async for msg in session.receive():
        print(msg.text)
```

## Configuration Types

```python
from google.genai import types

# GenerateContentConfig
config = types.GenerateContentConfig(
    system_instruction="...",
    temperature=0.7,
    top_p=0.9,
    max_output_tokens=4096,
    response_mime_type="application/json",
    response_json_schema={...},
    safety_settings=[types.SafetySetting(...)],
    tools=[types.Tool(...)],
    tool_config=types.ToolConfig(...),
    thinking_config=types.ThinkingConfig(thinking_budget=1024),
    response_modalities=["TEXT"],
    speech_config=types.SpeechConfig(...),
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
)
```

## Python Examples

### Example 1: Complete Workflow

```python
from google import genai
from google.genai import types
from pydantic import BaseModel
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 1. Check available models
for model in client.models.list():
    if "flash" in model.name:
        print(f"{model.name}: {model.input_token_limit} in / {model.output_token_limit} out")

# 2. Generate with structured output
class Analysis(BaseModel):
    topic: str
    summary: str
    key_points: list[str]
    sentiment: str

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="Analyze the following text.",
        response_mime_type="application/json",
        response_json_schema=Analysis.model_json_schema(),
        temperature=0.3,
    ),
    contents="Python 3.13 introduces free-threaded mode and a JIT compiler."
)

result = Analysis.model_validate_json(response.text)
print(f"Topic: {result.topic}")
print(f"Sentiment: {result.sentiment}")
for point in result.key_points:
    print(f"  - {point}")
```

### Example 2: Automatic Function Calling

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_stock_price(symbol: str) -> dict:
    """Gets the current stock price for a ticker symbol.

    Args:
        symbol: Stock ticker symbol (e.g., GOOG, AAPL).

    Returns:
        Dictionary with price and currency.
    """
    prices = {"GOOG": 185.50, "AAPL": 198.30, "MSFT": 445.20}
    return {"price": prices.get(symbol, 0), "currency": "USD"}

# SDK handles the full function call loop automatically
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What are the current prices of Google and Apple stock?",
    config=types.GenerateContentConfig(
        tools=[get_stock_price],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
    )
)
print(response.text)  # Natural language answer using function results
```

### Example 3: Error Handling Pattern

```python
# SOURCE: Google API docs (may use google.api_core.exceptions)
from google import genai
from google.genai import types
from google.api_core import exceptions
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            if response.candidates and response.candidates[0].finish_reason == "SAFETY":
                print("Content blocked by safety filter")
                return None
            return response.text
        except exceptions.ResourceExhausted:
            wait = 2 ** attempt
            print(f"Rate limited, waiting {wait}s...")
            time.sleep(wait)
        except exceptions.InvalidArgument as e:
            print(f"Invalid request: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            if attempt == max_retries - 1:
                raise
    return None

result = generate_with_retry("Explain machine learning")
if result:
    print(result)
```

**SDK-verified correction** (google-genai v1.68.0, `google/genai/errors.py`):

`google.api_core` is NOT a dependency of `google-genai`. The SDK uses its own error
hierarchy: `APIError` > `ClientError` (4xx), `ServerError` (5xx).

```python
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            if response.candidates and response.candidates[0].finish_reason == "SAFETY":
                print("Content blocked by safety filter")
                return None
            return response.text
        except ClientError as e:
            if e.code == 429:
                wait = 2 ** attempt
                print(f"Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif e.code == 400:
                print(f"Invalid request: {e.message}")
                return None
            else:
                raise
        except ServerError as e:
            wait = 2 ** attempt
            print(f"Server error ({e.code}), waiting {wait}s...")
            time.sleep(wait)
    return None

result = generate_with_retry("Explain machine learning")
if result:
    print(result)
```

## Comparison with Other APIs

### vs OpenAI Python SDK

- **Package**: Gemini: `google-genai` | OpenAI: `openai`
- **Client**: Gemini: `genai.Client(api_key=...)` | OpenAI: `OpenAI(api_key=...)`
- **Methods**: Gemini: `client.models.generate_content()` | OpenAI: `client.chat.completions.create()`
- **Streaming**: Gemini: `generate_content_stream()` | OpenAI: `stream=True` parameter
- **Types**: Gemini: `google.genai.types` | OpenAI: Pydantic models
- **Auto function calling**: Gemini: yes (SDK exclusive) | OpenAI: no
- **Async**: Gemini: `client.aio` namespace | OpenAI: `AsyncOpenAI` class
- **Dual backend**: Gemini: Google AI + Vertex AI | OpenAI: single backend

### vs Anthropic Python SDK

- **Package**: Gemini: `google-genai` | Anthropic: `anthropic`
- **Client**: Gemini: `genai.Client()` | Anthropic: `Anthropic()`
- **Auto function calling**: Gemini: yes | Anthropic: no
- **Live/WebSocket**: Gemini: `client.aio.live.connect()` | Anthropic: no equivalent
- **File management**: Gemini: `client.files` | Anthropic: no equivalent

## Error Responses

SDK raises errors from `google.genai.errors` (NOT `google.api_core.exceptions`):
- `ClientError` (4xx): Bad request (400), permission denied (403), not found (404), rate limit (429)
- `ServerError` (5xx): Internal server error (500), service unavailable (503)
- `APIError`: Base class for all API errors

Use `error.code` for HTTP status, `error.message` for detail, `error.status` for gRPC status.

## Limitations and Known Issues

- Automatic function calling only works with Python SDK (not REST, not other SDKs)
- Some preview features require `http_options={"api_version": "v1alpha"}`

## Gotchas and Quirks

- `google-genai` is the NEW SDK; `google-generativeai` is the OLD SDK (deprecated)
- SDK auto-wraps strings: `contents="text"` becomes `[Content(role="user", parts=[Part(text="text")])]`
- `config` parameter in SDK maps to multiple REST fields (generationConfig, safetySettings, tools, etc.)
- `client.aio` namespace mirrors sync API exactly - same method names
- For Vertex AI: set `vertexai=True` - same SDK, different auth
- Error types come from `google.genai.errors` (APIError, ClientError, ServerError) - NOT `google.api_core`

## Sources

- GEMAPI-SC-GOOG-PYTSDK: https://ai.google.dev/gemini-api/docs/quickstart [VERIFIED]
- GEMAPI-SC-GOOG-FUNCAL: https://ai.google.dev/gemini-api/docs/function-calling [VERIFIED]

## Document History

**[2026-03-20 07:30]**
- Fixed: Error handling used google.api_core.exceptions (not installed with google-genai)
- Fixed: Error Responses section and Gotchas corrected to reference google.genai.errors
- Added: SDK-verified error handling example using ClientError/ServerError
- Source: google-genai v1.68.0, google/genai/errors.py

**[2026-03-20 05:55]**
- Initial document created with full SDK documentation
