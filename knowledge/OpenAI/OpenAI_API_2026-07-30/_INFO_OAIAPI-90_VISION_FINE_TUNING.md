# Vision Fine-Tuning

**Doc ID**: OAIAPI-IN90
**Goal**: Document vision fine-tuning for specialized visual understanding
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Fine-tuning models with image inputs for specialized visual understanding tasks. Training data includes image-text pairs. Supports supervised fine-tuning with vision-capable base models. Separate from text-only fine-tuning due to different data format requirements and model selection. [VERIFIED] (OAIAPI-SC-OAI-GVFT (https://developers.openai.com/api/docs/guides/vision-fine-tuning))

## Key Facts

- **Purpose**: Train models on image-text pairs for specialized visual tasks [VERIFIED]
- **Data format**: JSONL with image URLs or base64 in messages [VERIFIED]
- **Base models**: Vision-capable models only (GPT-5.4-mini with vision) [VERIFIED]
- **API**: Same fine-tuning API (`POST /v1/fine_tuning/jobs`) [VERIFIED]
- **Distinction**: Different training data format from text-only fine-tuning

## Use Cases

- **Document classification**: Classify document types from images
- **Visual inspection**: Detect defects in product images
- **Medical imaging**: Specialized analysis (with appropriate compliance)
- **Brand recognition**: Identify logos, products, packaging
- **OCR enhancement**: Improve text extraction for specific document formats

## Training Data Format

### JSONL Structure

```json
{
  "messages": [
    {"role": "system", "content": "You classify document types."},
    {"role": "user", "content": [
      {"type": "image_url", "image_url": {"url": "https://example.com/doc.png"}},
      {"type": "text", "text": "Classify this document."}
    ]},
    {"role": "assistant", "content": "This is an invoice from Company XYZ dated 2024-01-15."}
  ]
}
```

### Image Requirements

- **Formats**: PNG, JPEG, GIF, WebP
- **Max size**: 20 MB per image
- **URL access**: Images must be publicly accessible during training (or use base64)
- **Min training examples**: 10+ recommended (50+ for best results)

## SDK Examples (Python)

### Create Vision Fine-Tuning Job

```python
from openai import OpenAI

client = OpenAI()

# Upload training file (JSONL with image-text pairs)
training_file = client.files.create(
    file=open("vision_training.jsonl", "rb"),
    purpose="fine-tune",
)

# Create fine-tuning job with vision model
job = client.fine_tuning.jobs.create(
    training_file=training_file.id,
    model="gpt-5.4-mini",  # Must be vision-capable
    hyperparameters={"n_epochs": 3},
)
print(f"Vision fine-tune job: {job.id}")
```

### Prepare Training Data

```python
import json

# Create training examples with images
examples = [
    {
        "messages": [
            {"role": "system", "content": "You identify product defects from images."},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": "https://storage.example.com/img1.jpg"}},
                {"type": "text", "text": "Inspect this product image."}
            ]},
            {"role": "assistant", "content": "DEFECT: Scratch on upper-left corner, 2mm length."}
        ]
    },
    # ... more examples
]

with open("vision_training.jsonl", "w") as f:
    for example in examples:
        f.write(json.dumps(example) + "\n")
```

## Differences from Text Fine-Tuning

- **Data format**: Messages include `image_url` content blocks
- **Model selection**: Must use vision-capable base model
- **Cost**: Higher per-token cost due to image processing
- **Training time**: Longer due to image encoding

## Gotchas and Quirks

- **Image accessibility**: Training images must remain accessible for duration of training [VERIFIED]
- **Base64 alternative**: Use base64 encoding if images cannot be hosted publicly [VERIFIED]
- **Token counting**: Images consume tokens based on resolution and detail level [VERIFIED]
- **GPT-5.5 not supported**: Vision fine-tuning not available for GPT-5.5 (text FT also unavailable) [VERIFIED]

## TypeScript Examples

### Basic Response

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Explain this concept briefly.",
});

console.log(response.output_text);
```

### With Instructions

```typescript
const response = await client.responses.create({
  model: "gpt-4o-mini",
  instructions: "You are a helpful assistant.",
  input: "What is 2+2?",
});

console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-GVFT - Vision fine-tuning guide (https://developers.openai.com/api/docs/guides/vision-fine-tuning)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Training data format, SDK examples, differences from text FT, gotchas

**[2026-05-22 13:05]**
- Initial documentation (gap found during /improve review)
