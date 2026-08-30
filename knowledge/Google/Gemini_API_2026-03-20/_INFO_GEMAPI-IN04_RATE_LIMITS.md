# INFO: Gemini API Rate Limits, Billing, and Pricing

**Doc ID**: GEMAPI-IN04
**Goal**: Document rate limit dimensions, usage tiers, billing setup, and pricing structure
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini API enforces rate limits across three primary dimensions: Requests Per Minute (RPM), Tokens Per Minute (TPM, input), and Requests Per Day (RPD). Some models add Images Per Minute (IPM) for image generation or Tokens Per Day (TPD). Limits are applied per Google Cloud project, not per API key, and RPD resets at midnight Pacific time. Usage tiers (Free, Tier 1, Tier 2, Tier 3) determine rate limits, with upgrades based on cumulative Google Cloud spending. The Free tier provides limited access without billing; paid tiers require a linked billing account in Google AI Studio. Preview and experimental models have more restricted limits. The Batch API has separate limits: 100 concurrent requests, 2GB input file size, 20GB storage. Actual rate limits are dynamic and viewable in Google AI Studio. Pricing is per-token with different rates for input, output, and cached tokens, varying by model.

## Key Facts

- [VERIFIED] Three rate limit dimensions: RPM, TPM (input), RPD (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Additional dimensions for some models: IPM, TPD (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Limits applied per project, not per API key (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] RPD resets at midnight Pacific time (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Four usage tiers: Free, Tier 1, Tier 2, Tier 3 (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Tier upgrades based on cumulative Google Cloud spending (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Batch API: 100 concurrent, 2GB input, 20GB storage (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Free-to-Tier-1 upgrade is instant; subsequent upgrades within 10 minutes (GEMAPI-SC-GOOG-RTLMTS)

## Use Cases

- **Cost planning**: Estimate API costs before production deployment
- **Capacity planning**: Choose appropriate tier for expected traffic
- **Rate limit handling**: Implement retry logic with backoff

## Quick Reference

**Rate Limit Dimensions:**
- RPM (Requests Per Minute)
- TPM (Tokens Per Minute, input)
- RPD (Requests Per Day)
- IPM (Images Per Minute, Nano Banana only)
- TPD (Tokens Per Day, some models)

**View Your Limits**: https://aistudio.google.com/rate-limit

## Usage Tiers

### Free Tier

- No billing account required
- Access to select models with restricted limits
- Prompts/responses may be used to improve Google products
- Suitable for prototyping and experimentation

### Tier 1

- Requires linked billing account in Google AI Studio
- Increased RPM, TPM, RPD limits
- Prompts/responses NOT used to improve products
- Upgrade from Free is typically instant

### Tier 2 and Tier 3

- Based on cumulative Google Cloud spending (all services, not just Gemini)
- Progressively higher rate limits
- Upgrade within 10 minutes of qualifying
- Rare cases: upgrade may be denied based on review

### Tier Upgrade Process

1. Set up billing in Google AI Studio: https://ai.google.dev/gemini-api/docs/billing
2. Free to Tier 1: instant after billing linked
3. Tier 1 to 2+: automatic when spending threshold met
4. Check current tier: https://aistudio.google.com/projects

## Rate Limit Behavior

- Exceeding ANY dimension triggers 429 error (even if other dimensions have headroom)
- Preview/experimental models have more restricted limits than stable models
- Limits are dynamic and may change - always check AI Studio for current values
- Specified rate limits are not guaranteed; actual capacity may vary

## Batch API Rate Limits

Batch API has its own separate limits:
- **Concurrent batch requests**: 100
- **Input file size limit**: 2GB
- **File storage limit**: 20GB
- **Enqueued tokens per model**: Model-specific maximum across all active batch jobs

## Python Examples

### Example 1: Rate Limit Retry Logic

```python
# SOURCE: Google API docs (may use google.api_core.exceptions)
import time
from google import genai
from google.api_core import exceptions
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate_with_backoff(prompt, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except exceptions.ResourceExhausted:
            wait = min(2 ** attempt, 60)  # Cap at 60 seconds
            print(f"Rate limited (attempt {attempt + 1}). Waiting {wait}s...")
            time.sleep(wait)
    raise Exception(f"Failed after {max_retries} retries")

result = generate_with_backoff("Explain machine learning")
print(result)
```

**SDK-verified correction** (google-genai v1.68.0, `google/genai/errors.py`):

`google.api_core` is NOT a dependency of `google-genai`. Use `google.genai.errors.ClientError`
and check `error.code == 429` for rate limiting.

```python
import time
from google import genai
from google.genai.errors import ClientError, ServerError
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate_with_backoff(prompt, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except ClientError as e:
            if e.code == 429:
                wait = min(2 ** attempt, 60)
                print(f"Rate limited (attempt {attempt + 1}). Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
        except ServerError:
            wait = min(2 ** attempt, 60)
            time.sleep(wait)
    raise Exception(f"Failed after {max_retries} retries")

result = generate_with_backoff("Explain machine learning")
print(result)
```

### Example 2: Batch Processing with Rate Awareness

```python
import time
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompts = [f"Summarize topic {i}" for i in range(100)]
results = []

for i, prompt in enumerate(prompts):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        results.append(response.text)

        # Simple rate limiting: ~10 requests per second
        if (i + 1) % 10 == 0:
            time.sleep(1)

    except Exception as e:
        print(f"Error on prompt {i}: {e}")
        time.sleep(5)

print(f"Completed {len(results)}/{len(prompts)} prompts")
```

## cURL Examples

### Example: Check Model Rate Limits

```bash
# List models to see supported parameters
curl "https://generativelanguage.googleapis.com/v1beta/models" \
  -H "x-goog-api-key: $GEMINI_API_KEY"
```

## Comparison with Other APIs

### vs OpenAI

- **Limit dimensions**: Gemini: RPM, TPM, RPD, IPM, TPD | OpenAI: RPM, TPM, RPD, TPD, images/min
- **Limit scope**: Gemini: per-project | OpenAI: per-organization + per-project
- **Tier system**: Gemini: Free/1/2/3 based on Google Cloud spend | OpenAI: Tier 1-5 based on OpenAI spend
- **Rate limit headers**: Gemini: none in response | OpenAI: `x-ratelimit-*` headers
- **Limit visibility**: Gemini: AI Studio dashboard | OpenAI: response headers + dashboard
- **RPD reset**: Gemini: midnight Pacific | OpenAI: midnight UTC

### vs Anthropic

- **Limit dimensions**: Gemini: RPM, TPM, RPD, IPM | Anthropic: RPM, TPM, TPD
- **Tier system**: Gemini: Google Cloud spend | Anthropic: Anthropic spend + manual upgrade
- **Rate limit headers**: Gemini: none | Anthropic: `anthropic-ratelimit-*` headers
- **Batch discount**: Gemini: Batch API (separate) | Anthropic: 50% off via Message Batches

## Error Responses

- **429 RESOURCE_EXHAUSTED**: Rate limit exceeded
  - Check which dimension was exceeded (RPM, TPM, or RPD)
  - Implement exponential backoff
  - Consider upgrading tier or using Batch API for bulk work

## Limitations and Known Issues

- [VERIFIED] No rate limit headers in API responses - must monitor via AI Studio (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Specified rate limits are not guaranteed; actual capacity may vary (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] IPM (Images Per Minute) applies only to image generation models like Nano Banana (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] TPD (Tokens Per Day) limit applies to some models in addition to RPM/TPM/RPD (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Preview and experimental models have more restricted rate limits (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Tier 2/3 qualification based on TOTAL cumulative Google Cloud spending, not just Gemini API (GEMAPI-SC-GOOG-RTLMTS)
- [VERIFIED] Tier upgrade requests may be denied in rare cases based on review (GEMAPI-SC-GOOG-RTLMTS)
- [COMMUNITY] Free tier quotas have been reduced significantly for some models (GEMAPI-SC-FORUM-RTLMT)

## Gotchas and Quirks

- Rate limits are per-project, not per-key - creating multiple keys does not increase limits
- RPD resets at midnight **Pacific time**, not UTC - important for international applications
- Exceeding any single dimension triggers rate limiting, even if others have headroom
- Tier upgrades based on ALL Google Cloud spending, not just Gemini API spend
- No rate limit headers in responses (unlike OpenAI/Anthropic) - harder to implement proactive throttling
- Free to Tier 1 upgrade is typically instant; subsequent tier upgrades take up to 10 minutes
- View active rate limits in AI Studio: https://aistudio.google.com/rate-limit
- Batch API has separate limits: 100 concurrent batch requests, 2GB input file, 20GB storage

## Sources

- GEMAPI-SC-GOOG-RTLMTS: https://ai.google.dev/gemini-api/docs/rate-limits [VERIFIED]
- GEMAPI-SC-GOOG-BILLNG: https://ai.google.dev/gemini-api/docs/billing [VERIFIED]
- GEMAPI-SC-GOOG-PRICNG: https://ai.google.dev/gemini-api/docs/pricing [VERIFIED]
- GEMAPI-SC-FORUM-RTLMT: https://discuss.ai.google.dev/t/gemini-api-free-tier-daily-quota-25-rpd-blocking-paid-usage-tier-1-1000-rpd/79899 [COMMUNITY]

## Document History

**[2026-03-20 07:20]**
- Fixed: Rate limit retry example used google.api_core.exceptions (not installed with google-genai)
- Added: SDK-verified correction using google.genai.errors.ClientError with code==429
- Source: google-genai v1.68.0, google/genai/errors.py

**[2026-03-20 06:50]**
- Added: IPM, TPD dimensions, tier upgrade timing, not-guaranteed caveat
- Added: total GCP spend qualification, upgrade denial possibility, Batch API limits

**[2026-03-20 03:00]**
- Initial document created with rate limits, tiers, billing, and pricing
