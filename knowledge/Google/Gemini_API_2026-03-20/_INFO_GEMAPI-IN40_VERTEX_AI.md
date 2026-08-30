# INFO: Gemini API Vertex AI Integration

**Doc ID**: GEMAPI-IN40
**Goal**: Document Vertex AI as an alternative backend, differences from Google AI Studio, and enterprise features
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini models are accessible through two backends: **Google AI** (developer-focused, API key auth, `generativelanguage.googleapis.com`) and **Vertex AI** (enterprise-focused, IAM/service account auth, `{region}-aiplatform.googleapis.com`). Both backends offer the same models and capabilities, but Vertex AI adds enterprise features: VPC Service Controls, Customer-Managed Encryption Keys (CMEK), data residency guarantees, audit logging, fine-tuning, model evaluation, and integration with Google Cloud services. The Python SDK (`google-genai`) supports both backends with a single client - set `vertexai=True` to switch. Vertex AI uses OAuth 2.0 / service account credentials instead of API keys. Pricing differs between backends. For production enterprise deployments, Vertex AI is recommended; for prototyping and individual development, Google AI Studio is simpler.

## Key Facts

- [VERIFIED] Two backends: Google AI (API key) and Vertex AI (IAM) (GEMAPI-SC-GOOG-VTXAI)
- [VERIFIED] Same models available on both (GEMAPI-SC-GOOG-VTXAI)
- [VERIFIED] Vertex AI: enterprise features (VPC, CMEK, data residency, audit) (GEMAPI-SC-GOOG-VTXAI)
- [VERIFIED] SDK: `genai.Client(vertexai=True, project=..., location=...)` (GEMAPI-SC-GOOG-PYTSDK)
- [VERIFIED] Vertex AI endpoint: `{region}-aiplatform.googleapis.com` (GEMAPI-SC-GOOG-VTXAI)

## Quick Reference

**Google AI**: `generativelanguage.googleapis.com` + API key
**Vertex AI**: `{region}-aiplatform.googleapis.com` + service account/OAuth

## Backend Comparison

- **Authentication**
  - Google AI: API key (`x-goog-api-key` header)
  - Vertex AI: OAuth 2.0 / service account (`Authorization: Bearer` header)

- **Endpoint**
  - Google AI: `generativelanguage.googleapis.com`
  - Vertex AI: `{region}-aiplatform.googleapis.com`

- **Setup complexity**
  - Google AI: Create key in AI Studio (minutes)
  - Vertex AI: GCP project + IAM + billing (hours)

- **Enterprise features**
  - Google AI: None
  - Vertex AI: VPC-SC, CMEK, data residency, audit logs, SLA

- **Rate limits**
  - Google AI: Per-project, tier-based
  - Vertex AI: Per-project, higher limits available

- **Fine-tuning**
  - Google AI: Limited
  - Vertex AI: Full fine-tuning support

- **Pricing**
  - Google AI: Pay-as-you-go, free tier available
  - Vertex AI: Pay-as-you-go, committed use discounts

## Python Examples

### Example 1: Vertex AI Client

```python
from google import genai
import os

# Vertex AI client (uses Application Default Credentials)
client = genai.Client(
    vertexai=True,
    project=os.environ["GCP_PROJECT_ID"],
    location="us-central1"
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain cloud computing"
)
print(response.text)
```

### Example 2: Switch Between Backends

```python
from google import genai
import os

# Development: Google AI
dev_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Production: Vertex AI
prod_client = genai.Client(
    vertexai=True,
    project=os.environ["GCP_PROJECT_ID"],
    location="us-central1"
)

# Same code works with both clients
def analyze_text(client, text):
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Analyze: {text}"
    ).text

# Use dev_client for development, prod_client for production
print(analyze_text(dev_client, "Test input"))
```

## Comparison with Other APIs

### vs OpenAI

- **Deployment options**: Gemini: Google AI + Vertex AI | OpenAI: OpenAI API + Azure OpenAI
- **Enterprise**: Both offer enterprise variants (Vertex AI / Azure OpenAI)
- **SDK switching**: Gemini: same SDK, flag toggle | OpenAI: different SDKs (openai vs azure)

### vs Anthropic

- **Deployment options**: Gemini: Google AI + Vertex AI | Anthropic: Anthropic API + AWS Bedrock + GCP Vertex
- **Enterprise**: Gemini: Vertex AI | Anthropic: Bedrock/Vertex
- **Note**: Anthropic models also available ON Vertex AI alongside Gemini

## Error Responses

- **403**: Permission denied (IAM misconfiguration)
- **404**: Project not found, model not available in region

## Rate Limiting / Throttling

Vertex AI has separate, typically higher rate limits. Quotas manageable via GCP Console. See GEMAPI-IN04.

## Limitations and Known Issues

- Vertex AI requires GCP project setup (more complex than API key)
- Some preview features may appear on Google AI before Vertex AI (or vice versa)
- Region availability varies for some models

## Gotchas and Quirks

- Same `google-genai` SDK for both backends - just set `vertexai=True`
- Vertex AI uses Application Default Credentials (ADC) - run `gcloud auth application-default login`
- Model names are the same across both backends
- Some features (e.g., free tier) only available on Google AI, not Vertex AI
- Data residency guarantees only on Vertex AI
- Anthropic Claude models are also available on Vertex AI (separate from Gemini)

## Sources

- GEMAPI-SC-GOOG-VTXAI: https://cloud.google.com/vertex-ai/generative-ai/docs/overview [VERIFIED]
- GEMAPI-SC-GOOG-PYTSDK: https://ai.google.dev/gemini-api/docs/quickstart [VERIFIED]

## Document History

**[2026-03-20 06:00]**
- Initial document created
