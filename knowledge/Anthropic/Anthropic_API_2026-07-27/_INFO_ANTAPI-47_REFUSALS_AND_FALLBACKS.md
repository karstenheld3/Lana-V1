# Refusals and Fallbacks

**Doc ID**: ANTAPI-IN47
**Goal**: Document refusal stop reason, stop_details categories, fallbacks parameter, and server-side fallback handling
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-11_STOP_REASONS.md [ANTAPI-IN11]` for stop_reason values
- `_INFO_ANTAPI-13_MODELS.md [ANTAPI-IN13]` for model capabilities

## Summary

Claude Fable 5, Mythos 5, and Opus 5 run safety classifiers on requests and during response generation. When a classifier declines a request, the Messages API returns `stop_reason: "refusal"` with a `stop_details` object containing a `category` and `explanation`. Requests refused before any output is generated are not billed. The opt-in `fallbacks` parameter (beta) re-runs refused requests on another model automatically. Server-side fallback mode `"default"` applies Anthropic's recommended fallback by refusal category.

## Key Facts

- **Stop Reason**: `"refusal"` in response `stop_reason` field
- **Details Field**: `stop_details.category` and `stop_details.explanation`
- **Categories**: `"cyber"`, `"bio"`, `"reasoning_extraction"`, or `null`
- **Billing**: Not billed for requests refused before any output
- **Fallback Parameter**: `fallbacks` in request body (beta)
- **Beta Header**: `server-side-fallback-2026-07-01`
- **Fallback Modes**: `"default"` (Anthropic-recommended), explicit model list
- **Supported On**: Claude API, Claude Platform on AWS; **not** Message Batches API
- **Status**: Beta (fallbacks), GA (stop_reason/stop_details)

## Refusal Categories

- **`"cyber"`** - Request blocked under cybersecurity restrictions
- **`"bio"`** - Request blocked under biology/chemistry restrictions
- **`"reasoning_extraction"`** - Request blocked under ToS restrictions on reverse-engineering or duplicating model outputs (Fable 5 only)
- **`null`** - General refusal without specific category

## Handling Refusals

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-fable-5",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Analyze this security vulnerability..."}],
)

if response.stop_reason == "refusal":
    details = response.stop_details
    if details:
        print(f"Category: {details.category}")
        print(f"Explanation: {details.explanation}")
    # Not billed if no output was generated
```

## Server-Side Fallback (Beta)

The `fallbacks` parameter automatically re-runs refused requests on a fallback model. This avoids writing client-side retry logic.

### Default Fallback Mode

```python
import anthropic

client = anthropic.Anthropic()

# "default" mode: Anthropic picks the best fallback per refusal category
response = client.beta.messages.create(
    model="claude-fable-5",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Help me understand this code..."}],
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
)

# If Fable 5 refused and Opus 4.8 succeeded, response.model shows the fallback model
print(f"Responded by: {response.model}")
```

### How Fallback Works

1. Request sent to primary model (e.g., Fable 5)
2. If classifier triggers `stop_reason: "refusal"`, the API re-runs on fallback model
3. Fallback request reuses the cached prompt (billed as cache read at 0.1x, not cache write)
4. Response contains the fallback model's output, billed at fallback model's rates
5. A `fallback` content block appears in the response when fallback activates

### Streaming with Fallback

When streaming, if a refusal occurs mid-stream:
- The stream may contain partial content from the primary model
- A `fallback` content block appears indicating the model switch
- The fallback model's response follows in subsequent content blocks

## Gotchas and Quirks

- `stop_details` is GA and appears on all models, but categories are primarily relevant for Fable 5/Mythos 5/Opus 5
- Not billed for pre-output refusals (since Jun 2, 2026); partial-output refusals still billed for generated tokens
- `fallbacks` parameter is not supported on Message Batches API
- Sending both `fallbacks` and `betas=["server-side-fallback-2026-07-01"]` is required during beta
- The `"default"` fallback mode selects the fallback model per refusal category (not configurable)
- Fallback input tokens billed as cache read (0.1x), significantly cheaper than re-sending
- `"reasoning_extraction"` category only appears on Fable 5
- Opus 4.7 rejects `role: "system"` in messages with a 400 error (not a refusal)

## Related Endpoints

- `_INFO_ANTAPI-11_STOP_REASONS.md [ANTAPI-IN11]` - All stop reason values
- `_INFO_ANTAPI-14_PRICING.md [ANTAPI-IN14]` - Refusal billing and fallback pricing
- `_INFO_ANTAPI-09_STREAMING.md [ANTAPI-IN09]` - Streaming refusals and fallback blocks

## Sources

- ANTAPI-SC-ANTH-REFUSAL - https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback - Refusals, stop_details, fallback parameter
- ANTAPI-SC-ANTH-STOPREASON - https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons - Stop reason handling

## SDK Verification

Examples written for `anthropic` SDK 0.120.0. Pending re-verification in Prompt 3.

## Document History

**[2026-07-26]**
- Initial documentation created (new topic)
- Covers: refusal stop_reason, stop_details categories, server-side fallback (beta), billing
