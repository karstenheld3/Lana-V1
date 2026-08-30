# Moderation API

**Doc ID**: OAIAPI-IN26
**Goal**: Document content moderation API with omni-moderation models and category detection
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI Moderation API (POST /v1/moderations) classifies text and images for policy-violating content. Model omni-moderation-latest supports multi-modal input. Returns category flags and confidence scores for 11 categories: hate, hate/threatening, harassment, harassment/threatening, self-harm, self-harm/intent, self-harm/instructions, sexual, sexual/minors, violence, violence/graphic. Free for API customers. Multi-language support. Model auto-updates. **NEW (2026-06)**: Inline moderation - pass a `moderation` object in Responses API or Chat Completions requests to receive moderation results for both input and output in the same response, eliminating the need for separate moderation calls. [VERIFIED] (OAIAPI-SC-OAI-MODCRT, OAIAPI-SC-OAI-GMOD, OAIAPI-SC-OAI-GCHLOG)

## Key Facts

- **Endpoint**: POST /v1/moderations [VERIFIED]
- **Inline moderation**: Pass `moderation` object in Responses/Chat Completions for in-request scoring (NEW 2026-06) [VERIFIED]
- **Model**: omni-moderation-latest (multi-modal) [VERIFIED]
- **Input**: Text and/or images [VERIFIED]
- **Categories**: 11 policy categories [VERIFIED]
- **Free**: No cost for API customers [VERIFIED]

## Content Categories

- **hate** / **hate/threatening**: Content promoting hatred, threats based on protected characteristics
- **harassment** / **harassment/threatening**: Bullying, intimidation, threats against individuals
- **self-harm** / **self-harm/intent** / **self-harm/instructions**: Self-harm content, intent, or methods
- **sexual** / **sexual/minors**: Sexual content, child exploitation
- **violence** / **violence/graphic**: Violence promotion, graphic content

## Request Format

### Text Only

```json
{"model": "omni-moderation-latest", "input": "Text to moderate"}
```

### Text + Images (Multi-Modal)

```json
{
  "model": "omni-moderation-latest",
  "input": [
    {"type": "text", "text": "Text to moderate"},
    {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
  ]
}
```

## Response Format

```json
{
  "id": "modr_abc123",
  "model": "omni-moderation-latest",
  "results": [{
    "flagged": false,
    "categories": {"hate": false, "violence": false, ...},
    "category_scores": {"hate": 0.001, "violence": 0.001, ...}
  }]
}
```

- **flagged**: True if content violates policy
- **categories**: Boolean flags per category
- **category_scores**: Confidence scores (0-1) per category

## SDK Examples (Python)

### Basic Text Moderation

```python
from openai import OpenAI

client = OpenAI()

response = client.moderations.create(
    model="omni-moderation-latest",
    input="This is a sample text to moderate"
)

result = response.results[0]
if result.flagged:
    print("Content flagged")
    for category, flagged in result.categories.items():
        if flagged:
            print(f"  {category}: {result.category_scores[category]:.4f}")
else:
    print("Content passed")
```

### Multi-Modal Moderation

```python
from openai import OpenAI

client = OpenAI()

response = client.moderations.create(
    model="omni-moderation-latest",
    input=[
        {"type": "text", "text": "Check this content"},
        {"type": "image_url", "image_url": {"url": "https://example.com/user-upload.jpg"}}
    ]
)
print(f"Flagged: {response.results[0].flagged}")
```

### Batch Moderation

```python
from openai import OpenAI

client = OpenAI()

texts = ["First user comment", "Second user comment", "Third user comment"]
response = client.moderations.create(model="omni-moderation-latest", input=texts)

for i, result in enumerate(response.results):
    print(f"Text {i+1}: {'FLAGGED' if result.flagged else 'OK'}")
```

### Score-Based Filtering

```python
from openai import OpenAI

client = OpenAI()

def moderate_with_threshold(text: str, threshold: float = 0.5):
    response = client.moderations.create(model="omni-moderation-latest", input=text)
    result = response.results[0]
    
    violations = [{"category": cat, "score": score}
                  for cat, score in result.category_scores.items() if score >= threshold]
    return {"flagged": result.flagged, "violations": violations}
```

### Production Moderation Service

```python
from openai import OpenAI
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ModerationService:
    def __init__(self):
        self.client = OpenAI()
    
    def moderate_text(self, text: str) -> Dict:
        try:
            response = self.client.moderations.create(model="omni-moderation-latest", input=text)
            return self._format_result(response.results[0])
        except Exception as e:
            logger.error(f"Moderation error: {e}")
            return {"allowed": False, "error": str(e)}  # Fail closed
    
    def moderate_batch(self, texts: List[str]) -> List[Dict]:
        try:
            response = self.client.moderations.create(model="omni-moderation-latest", input=texts)
            return [self._format_result(r) for r in response.results]
        except Exception as e:
            logger.error(f"Batch error: {e}")
            return [{"allowed": False, "error": str(e)} for _ in texts]
    
    def _format_result(self, result) -> Dict:
        return {
            "allowed": not result.flagged,
            "categories": {k: v for k, v in result.categories.items() if v},
            "top_scores": sorted(result.category_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        }

# Usage
service = ModerationService()
result = service.moderate_text("User input")
if not result["allowed"]:
    print(f"Blocked: {result['categories']}")
```

## Error Responses

- **400 Bad Request** - Invalid input format
- **429 Too Many Requests** - Rate limit exceeded (rare, generous limits)

## Differences from Other APIs

- **vs Perspective API**: OpenAI multi-modal, Perspective text-only
- **vs Azure Content Safety**: Similar capabilities, different categories
- **vs AWS Rekognition**: AWS image-focused, OpenAI multi-modal

## Limitations and Known Issues

- **Language coverage**: Best for English, supports others [ASSUMED]
- **Context-dependent**: May miss context-specific violations [ASSUMED]
- **False positives**: Some legitimate content flagged [ASSUMED]

## Gotchas and Quirks

- **Auto-updates**: Model improves without API changes [VERIFIED]
- **Threshold tuning**: May need custom thresholds per use case [ASSUMED]
- **Combined scores**: Text + image scored together in multi-modal [VERIFIED]

## TypeScript Examples

### Content Moderation

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const result = await client.moderations.create({
  model: "omni-moderation-latest",
  input: "Check this content for safety.",
});

console.log(`Flagged: ${result.results[0].flagged}`);
```

## Sources

- OAIAPI-SC-OAI-MODCRT - POST Create moderation
- OAIAPI-SC-OAI-GMOD - Moderation guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: Inline moderation feature (2026-06) - `moderation` object in Responses/Chat Completions
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 15:20]**
- Enriched: Full categories, request/response formats, SDK examples from 2026-03-20
- Changed: Doc ID from IN24 to IN26 per renumbering

**[2026-05-22 11:40]**
- Stub created
