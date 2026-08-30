# INFO: Gemini API Models

**Doc ID**: GEMAPI-IN05
**Goal**: Document model listing API, model families, capabilities, context windows, and version naming
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini API provides access to multiple model families through the Models API (`GET /v1beta/models`). The current generation is Gemini 3 with three main variants: Gemini 3.1 Pro (highest intelligence), Gemini 3 Flash (cost-efficient frontier), and Gemini 3.1 Flash-Lite (high-volume workhorse). Image generation uses Nano Banana 2 (speed-optimized) and Nano Banana Pro (quality-optimized). Video generation uses Veo 3.1 (4K + audio) and Veo 2.0 (1080p production). Audio models include native audio preview and TTS variants. Specialized models include Computer Use (UI automation), Deep Research (multi-step research agent), Gemini Embedding (text/multimodal embeddings), and Gemini Robotics. Model version names follow patterns: stable (`gemini-2.5-flash`), preview (`gemini-3-flash-preview`), latest (`gemini-flash-latest`), and experimental. Previous generation models (2.5, 2.0) remain available but some are deprecated. Context windows range from 32K to 2M tokens depending on model.

## Key Facts

- [VERIFIED] GET /v1beta/models lists all available models (GEMAPI-SC-GOOG-MODREF)
- [VERIFIED] GET /v1beta/models/{name} returns model info including supported parameters (GEMAPI-SC-GOOG-MODREF)
- [VERIFIED] Gemini 3.1 Pro: highest intelligence, complex reasoning (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Gemini 3 Flash: frontier performance at lower cost (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Gemini 3.1 Flash-Lite: high-volume cost-optimized (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Version patterns: stable, preview, latest, experimental (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Preview models: billing enabled, restricted rate limits, 2-week deprecation notice (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Experimental models: not for production, subject to change (GEMAPI-SC-GOOG-MODELS)

## Use Cases

- **Model selection**: Choose optimal model for cost/quality tradeoff
- **Model discovery**: List available models and capabilities programmatically
- **Version management**: Pin to stable versions or track latest

## Quick Reference

**List Models**: `GET /v1beta/models`
**Get Model**: `GET /v1beta/models/{name}`

## Model Families (March 2026)

### Gemini 3 Series (Current Generation)

- **Gemini 3.1 Pro** (`gemini-3.1-pro-preview`)
  - Most intelligent model, complex problem-solving, agentic and vibe coding
  - Status: New Preview

- **Gemini 3 Flash** (`gemini-3-flash-preview`)
  - Frontier-class performance at fraction of cost
  - Status: Preview

- **Gemini 3.1 Flash-Lite** (`gemini-3.1-flash-lite-preview`)
  - High-volume workhorse with Gemini 3 quality
  - Status: New Preview

### Gemini 2.5 Series

- **Gemini 2.5 Flash** (`gemini-2.5-flash`)
  - Stable production model
  - Status: Stable

- **Gemini 2.5 Flash-Lite** (`gemini-2.5-flash-lite`)
  - Cost-efficient stable model
  - Status: Stable

- **Gemini 2.5 Pro** (`gemini-2.5-pro`)
  - High-quality reasoning model
  - Status: Stable

### Image Generation Models

- **Nano Banana 2** (`gemini-3.1-flash-image-preview`)
  - High-efficiency image generation and editing, optimized for speed
  - Status: Preview

- **Nano Banana Pro** (`gemini-3-pro-image-preview`)
  - State-of-the-art image generation for highly contextual creation
  - Status: Preview

- **Nano Banana** (`gemini-2.5-flash-image`)
  - Previous gen native image generation
  - Status: Stable

- **Imagen 4** - Dedicated standalone image generation model

### Video Generation Models

- **Veo 3.1** (`veo-3.1-generate-preview`)
  - Cinematic 4K video with native synchronized audio
  - Status: Preview

- **Veo 2.0** (`veo-2.0-generate-001`)
  - 1080p production-ready video generation
  - Status: Stable

### Audio Models

- **Gemini 2.5 Flash Live Preview** - Native audio for Live API
- **Gemini 2.5 Flash TTS Preview** - Text-to-speech
- **Gemini 2.5 Pro TTS Preview** - High-quality TTS
- **Lyria Experimental** - Music/audio generation

### Tool and Agent Models

- **Computer Use Preview** (`gemini-2.5-computer-use-preview`)
  - Screen understanding and UI automation (click, type, navigate)

- **Gemini Deep Research Preview** (`deep-research-pro-preview`)
  - Autonomous multi-step research agent with cited reports

### Specialized Task Models

- **Gemini Embedding 2 Preview** - Multimodal embeddings (text, image, video, audio)
- **Gemini Embedding** (`gemini-embedding-001`) - Text embeddings
- **Gemini Robotics Preview** - VLM for physical world reasoning

### Previous Models (Deprecated/Shutdown)

- **Gemini 2.0 Flash** - Deprecated
- **Gemini 2.0 Flash-Lite** - Deprecated
- **Gemini 3 Pro Preview** - Shut down March 9, 2026

## Version Name Patterns

- **Stable** (`gemini-2.5-flash`): Specific stable version, does not change, for production
- **Preview** (`gemini-2.5-flash-preview-09-2025`): May be used for production, billing enabled, restricted rate limits, deprecated with 2-week notice
- **Latest** (`gemini-flash-latest`): Points to latest release (stable, preview, or experimental), hot-swapped with 2-week email notice
- **Experimental**: Feedback-gathering models, not for production, may disappear without notice

## REST API

### List Models

```
GET https://generativelanguage.googleapis.com/v1beta/models
```

**Response:**

```json
{
  "models": [
    {
      "name": "models/gemini-2.5-flash",
      "version": "2.5",
      "displayName": "Gemini 2.5 Flash",
      "description": "Fast and versatile...",
      "inputTokenLimit": 1048576,
      "outputTokenLimit": 65536,
      "supportedGenerationMethods": [
        "generateContent",
        "countTokens",
        "createCachedContent"
      ],
      "temperature": 1.0,
      "maxTemperature": 2.0,
      "topP": 0.95,
      "topK": 40
    }
  ]
}
```

### Get Model

```
GET https://generativelanguage.googleapis.com/v1beta/models/{model}
```

**Response Fields:**
- **name** (string): Model resource name (e.g., `models/gemini-2.5-flash`)
- **version** (string): Model version
- **displayName** (string): Human-readable name
- **description** (string): Model description
- **inputTokenLimit** (integer): Maximum input context window
- **outputTokenLimit** (integer): Maximum output tokens
- **supportedGenerationMethods** (array): Available API methods
- **temperature** (float): Default temperature
- **maxTemperature** (float): Maximum temperature
- **topP** (float): Default nucleus sampling
- **topK** (integer): Default top-k sampling

## Python Examples

### Example 1: List All Models

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

for model in client.models.list():
    print(f"{model.name}: {model.display_name}")
    print(f"  Input: {model.input_token_limit} tokens")
    print(f"  Output: {model.output_token_limit} tokens")
    print(f"  Methods: {model.supported_generation_methods}")
    print()
```

### Example 2: Get Specific Model Info

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

model = client.models.get(model="gemini-2.5-flash")
print(f"Name: {model.display_name}")
print(f"Input limit: {model.input_token_limit}")
print(f"Output limit: {model.output_token_limit}")
print(f"Temperature range: 0 - {model.max_temperature}")
```

## cURL Examples

### Example 1: List Models

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models" \
  -H "x-goog-api-key: $GEMINI_API_KEY"
```

### Example 2: Get Model Info

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash" \
  -H "x-goog-api-key: $GEMINI_API_KEY"
```

## Comparison with Other APIs

### vs OpenAI

- **Model in request**: Gemini: URL path `/models/{model}:method` | OpenAI: `model` field in body
- **Model listing**: Gemini: GET /v1beta/models | OpenAI: GET /v1/models
- **Model info richness**: Gemini: includes limits, defaults, methods | OpenAI: minimal (id, created, owner)
- **Version patterns**: Gemini: stable/preview/latest/experimental | OpenAI: date-stamped (gpt-4o-2024-11-20)
- **Context windows**: Gemini: up to 2M tokens | OpenAI: up to 200K tokens
- **Specialized models**: Gemini: Computer Use, Deep Research, Robotics | OpenAI: DALL-E, Whisper, TTS

### vs Anthropic

- **Model listing**: Gemini: GET /v1beta/models | Anthropic: GET /v1/models (limited)
- **Model info**: Gemini: detailed with limits/defaults | Anthropic: basic metadata
- **Context windows**: Gemini: up to 2M tokens | Anthropic: 200K tokens
- **Version patterns**: Gemini: stable/preview/latest | Anthropic: date-stamped
- **Image/Video generation**: Gemini: Nano Banana, Imagen, Veo | Anthropic: none

## Rate Limiting / Throttling

Model-specific rate limits. Preview/experimental models have more restricted limits. Check AI Studio for current values per model. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Experimental models may disappear without notice (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] `latest` alias can change with 2-week notice - not suitable for reproducible production (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Some languages unsupported - may produce unexpected responses (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] `gemini-3-pro-preview` has been SHUT DOWN and replaced by `gemini-3.1-pro-preview` (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] `gemini-2.0-flash` and `gemini-2.0-flash-lite` are DEPRECATED (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Beta features (v1beta) may not be available on stable API version (v1) (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] Gemini Robotics Preview (`gemini-robotics-er-1.5-preview`) is a specialized embodied reasoning model for robotic agents (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Gemini Embedding 2 Preview maps text, images, video, audio, AND PDFs into unified embedding space (GEMAPI-SC-GOOG-MODELS)

## Gotchas and Quirks

- Model name includes `models/` prefix in response (e.g., `models/gemini-2.5-flash`) but not in URL path
- "Nano Banana" is Google's brand name for Gemini's native image generation - not a separate model family
- The `latest` alias tracks the most recent release of ANY stability level, including experimental
- Deprecated models have a shutdown date but continue working until then
- `gemini-3-pro-preview` was shut down quickly and replaced by 3.1-pro - preview models can be short-lived
- 2.5 models have higher latency/token usage than 2.0 due to thinking enabled by default

## Sources

- GEMAPI-SC-GOOG-MODREF: https://ai.google.dev/api/models [VERIFIED]
- GEMAPI-SC-GOOG-MODELS: https://ai.google.dev/gemini-api/docs/models [VERIFIED]
- GEMAPI-SC-GOOG-GEMMOD: https://ai.google.dev/gemini-api/docs/models/gemini [VERIFIED]
- GEMAPI-SC-GOOG-G31PRO: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview [VERIFIED]
- GEMAPI-SC-GOOG-G3FLSH: https://ai.google.dev/gemini-api/docs/models/gemini-3-flash-preview [VERIFIED]

## Document History

**[2026-03-20 06:20]**
- Added: gemini-3-pro shutdown status, robotics model details, embedding 2 multimodal scope
- Added: deprecation warnings for 2.0 models, v1beta feature availability note
- Added: 2.5 thinking latency gotcha

**[2026-03-20 03:05]**
- Initial document created with all model families and version naming
