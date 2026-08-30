# INFO: Gemini API Safety Settings

**Doc ID**: GEMAPI-IN11
**Goal**: Document safety categories, HarmBlockThreshold, per-request configuration, and blocked responses
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini API provides configurable per-request safety settings that filter content across four harm categories: sexually explicit, hate speech, harassment, and dangerous content. Each category can be set to a block threshold (BLOCK_NONE, BLOCK_LOW_AND_ABOVE, BLOCK_MEDIUM_AND_ABOVE, BLOCK_HIGH_AND_ABOVE) via the `safetySettings` array in the request body. The API returns `safetyRatings` in each candidate response with probability assessments per category. When content is blocked, the `finishReason` is set to `SAFETY` and the response `parts` array may be empty. `BlockedReason.OTHER` indicates terms of service violations rather than safety filter triggers. This per-request configurability is unique to Gemini - OpenAI uses a separate Moderations API and Anthropic relies on built-in content policy without user-configurable thresholds.

## Key Facts

- [VERIFIED] Four harm categories: SEXUALLY_EXPLICIT, HATE_SPEECH, HARASSMENT, DANGEROUS_CONTENT (GEMAPI-SC-GOOG-SAFETY)
- [VERIFIED] Configurable per-request via `safetySettings` array (GEMAPI-SC-GOOG-SAFETY)
- [VERIFIED] Block thresholds: BLOCK_NONE, BLOCK_LOW_AND_ABOVE, BLOCK_MEDIUM_AND_ABOVE, BLOCK_HIGH_AND_ABOVE (GEMAPI-SC-GOOG-SAFETY)
- [VERIFIED] Response includes `safetyRatings` with probability per category (GEMAPI-SC-GOOG-GENCNT)
- [VERIFIED] Blocked content: finishReason=SAFETY, empty parts (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] BlockedReason.OTHER = ToS violation, not safety filter (GEMAPI-SC-GOOG-TROUBL)

## Quick Reference

**Request field**: `safetySettings` (array of `{category, threshold}`)
**Response field**: `candidates[].safetyRatings` (array of `{category, probability, blocked}`)

## Harm Categories

- **HARM_CATEGORY_SEXUALLY_EXPLICIT**: Sexual content
- **HARM_CATEGORY_HATE_SPEECH**: Hate speech targeting identity groups
- **HARM_CATEGORY_HARASSMENT**: Harassment, bullying, threats
- **HARM_CATEGORY_DANGEROUS_CONTENT**: Dangerous activities, self-harm, weapons

## Block Thresholds

- **BLOCK_NONE**: No blocking (all content passes)
- **BLOCK_LOW_AND_ABOVE**: Block if probability >= LOW
- **BLOCK_MEDIUM_AND_ABOVE**: Block if probability >= MEDIUM (default for most categories)
- **BLOCK_HIGH_AND_ABOVE**: Block only if probability is HIGH

## Probability Levels

Response `safetyRatings` include a `probability` field:
- **NEGLIGIBLE**: Very low probability of harm
- **LOW**: Low probability
- **MEDIUM**: Medium probability
- **HIGH**: High probability

## REST API

### Request with Safety Settings

```json
{
  "contents": [{"parts": [{"text": "Your prompt here"}]}],
  "safetySettings": [
    {
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_LOW_AND_ABOVE"
    },
    {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "threshold": "BLOCK_HIGH_AND_ABOVE"
    }
  ]
}
```

### Response with Safety Ratings

```json
{
  "candidates": [
    {
      "content": {"parts": [{"text": "Response..."}], "role": "model"},
      "finishReason": "STOP",
      "safetyRatings": [
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE", "blocked": false},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "probability": "NEGLIGIBLE", "blocked": false},
        {"category": "HARM_CATEGORY_HARASSMENT", "probability": "LOW", "blocked": false},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "probability": "NEGLIGIBLE", "blocked": false}
      ]
    }
  ]
}
```

### Blocked Response

```json
{
  "candidates": [
    {
      "content": {"parts": [], "role": "model"},
      "finishReason": "SAFETY",
      "safetyRatings": [
        {"category": "HARM_CATEGORY_HARASSMENT", "probability": "HIGH", "blocked": true}
      ]
    }
  ]
}
```

## Python Examples

### Example 1: Custom Safety Settings

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_LOW_AND_ABOVE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_NONE"
            ),
        ]
    ),
    contents="Explain how fireworks are manufactured"
)
print(response.text)
```

### Example 2: Check Safety Ratings

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write about conflict resolution strategies"
)

if response.candidates:
    candidate = response.candidates[0]

    if candidate.finish_reason == "SAFETY":
        print("Response blocked by safety filter:")
        for rating in candidate.safety_ratings:
            if rating.blocked:
                print(f"  {rating.category}: {rating.probability}")
    else:
        print(response.text)
        print("\nSafety ratings:")
        for rating in candidate.safety_ratings:
            print(f"  {rating.category}: {rating.probability}")
```

### Example 3: Permissive Settings for Research

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Set all categories to BLOCK_NONE for maximum permissiveness
permissive_settings = [
    types.SafetySetting(category=cat, threshold="BLOCK_NONE")
    for cat in [
        "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "HARM_CATEGORY_HATE_SPEECH",
        "HARM_CATEGORY_HARASSMENT",
        "HARM_CATEGORY_DANGEROUS_CONTENT",
    ]
]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(safety_settings=permissive_settings),
    contents="Analyze the historical context of propaganda techniques"
)
print(response.text)
```

## cURL Examples

### Example: Custom Safety Thresholds

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Explain cybersecurity attack vectors"}]}],
    "safetySettings": [
      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
      {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ]
  }'
```

## Comparison with Other APIs

### vs OpenAI

- **Safety approach**: Gemini: configurable per-request thresholds | OpenAI: separate Moderations API + built-in filtering
- **User control**: Gemini: BLOCK_NONE possible per category | OpenAI: no per-request safety tuning
- **Response metadata**: Gemini: safetyRatings in every response | OpenAI: no safety scores in chat response
- **Configuration granularity**: Gemini: 4 categories x 4 thresholds | OpenAI: binary moderation categories

### vs Anthropic

- **Safety approach**: Gemini: configurable thresholds | Anthropic: built-in content policy, no user override
- **User control**: Gemini: can set BLOCK_NONE | Anthropic: no per-request safety configuration
- **Block behavior**: Gemini: finishReason=SAFETY | Anthropic: stop_reason with content policy message
- **UNIQUE to Gemini**: Per-request configurable safety thresholds

## Error Responses

- Safety blocks return HTTP 200 with `finishReason: "SAFETY"`, not HTTP 4xx
- `BlockedReason.OTHER` (ToS violation) is distinct from safety blocks

## Rate Limiting / Throttling

Standard Gemini API rate limits apply. Safety-blocked requests still count against limits. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] BLOCK_NONE does not guarantee content passes - ToS violations still blocked as OTHER (GEMAPI-SC-GOOG-TROUBL)
- [VERIFIED] Default thresholds may vary by model and region (GEMAPI-SC-GOOG-SAFETY)

## Gotchas and Quirks

- Safety blocks return HTTP 200, not 4xx - must check `finishReason` in response
- `BLOCK_NONE` disables safety filtering but ToS violations still blocked as `OTHER`
- Safety ratings are always returned even when content is not blocked
- Setting `safetySettings` for only some categories leaves others at model defaults
- Cannot configure safety settings via OpenAI compatibility endpoint

## Sources

- GEMAPI-SC-GOOG-SAFETY: https://ai.google.dev/gemini-api/docs/safety-settings [VERIFIED]
- GEMAPI-SC-GOOG-SAFGUI: https://ai.google.dev/gemini-api/docs/safety-guidance [VERIFIED]
- GEMAPI-SC-GOOG-TROUBL: https://ai.google.dev/gemini-api/docs/troubleshooting [VERIFIED]

## Document History

**[2026-03-20 03:35]**
- Initial document created with safety categories, thresholds, and examples
