# Models API

**Doc ID**: OAIAPI-IN27
**Goal**: Document the Models API - list, retrieve, and delete models
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Models API provides endpoints to list available models, retrieve model details, and delete fine-tuned models. GET /v1/models returns all models accessible to the organization. GET /v1/models/{model} returns details for a specific model. DELETE /v1/models/{model} deletes fine-tuned models only. Model IDs follow patterns: base models use descriptive names (gpt-5.5, o3), dated snapshots use date suffixes, fine-tuned models use `ft:` prefix. No pagination - returns all at once. [VERIFIED] (OAIAPI-SC-OAI-MODAPI)

## Key Facts

- **List**: GET /v1/models - all accessible models [VERIFIED]
- **Retrieve**: GET /v1/models/{model} - model details [VERIFIED]
- **Delete**: DELETE /v1/models/{model} - fine-tuned models only [VERIFIED]
- **No pagination**: List returns all models at once [VERIFIED]
- **Fine-tune prefix**: `ft:` prefix for fine-tuned models [VERIFIED]

## Model Object

```json
{
  "id": "gpt-5.5",
  "object": "model",
  "created": 1686935002,
  "owned_by": "openai"
}
```

## Model ID Patterns

- **Base models**: `gpt-5.5`, `o3`, `gpt-4.1-mini`, `gpt-4.1-nano`
- **Dated snapshots**: `gpt-4o-2024-08-06`, `o3-2025-04-16`
- **Fine-tuned**: `ft:gpt-4.1:my-org:custom-name:abc123`
- **Realtime**: `gpt-realtime-1.5`
- **Image**: `gpt-image-1`, `gpt-image-2`
- **Embedding**: `text-embedding-3-small`, `text-embedding-3-large`
- **TTS**: `tts-1`, `tts-1-hd`, `gpt-audio-1.5`
- **Transcription**: `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `whisper-1`
- **Moderation**: `omni-moderation-latest`

## SDK Examples (Python)

### List and Filter Models

```python
from openai import OpenAI

client = OpenAI()

models = client.models.list()
fine_tuned = [m for m in models if m.id.startswith("ft:")]
gpt_models = [m for m in models if "gpt" in m.id]

for m in sorted(gpt_models, key=lambda x: x.id):
    print(f"  {m.id} (owned by: {m.owned_by})")
```

### Delete Fine-Tuned Model

```python
from openai import OpenAI

client = OpenAI()

try:
    result = client.models.delete("ft:gpt-4.1:my-org:custom-name:abc123")
    print(f"Deleted: {result.id}, Status: {result.deleted}")
except Exception as e:
    print(f"Error: {e}")
```

## Error Responses

- **401 Unauthorized** - Invalid API key
- **404 Not Found** - Model not found or not accessible
- **403 Forbidden** - Cannot delete base models

## Differences from Other APIs

- **vs Anthropic**: No models list endpoint; model IDs are documented
- **vs Gemini**: `models.list()` with more metadata (token limits, capabilities)
- **vs Grok**: Uses OpenAI-compatible models endpoint

## TypeScript Examples

### List and Retrieve Models

```typescript
import OpenAI from "openai";

const client = new OpenAI();

// List models
for await (const model of await client.models.list()) {
  console.log(model.id);
}

// Retrieve specific model
const model = await client.models.retrieve("gpt-4o-mini");
console.log(`${model.id} owned by ${model.owned_by}`);
```

## Sources

- OAIAPI-SC-OAI-MODAPI - Models API Reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 15:25]**
- Enriched: Full model object, ID patterns, SDK examples from 2026-03-20
- Updated: Model refs to gpt-5.5, added gpt-image-2, gpt-audio-1.5

**[2026-05-22 11:40]**
- Stub created
