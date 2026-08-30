# Legacy APIs and Model Deprecations

**Doc ID**: ANTAPI-IN39
**Goal**: Document deprecated models, legacy API patterns, and migration guidance
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` for API versioning
- `_INFO_ANTAPI-13_MODELS.md [ANTAPI-IN13]` for current model list

## Summary

Anthropic follows a structured model deprecation policy. Models are marked as deprecated with advance notice, then eventually removed from service. The legacy Text Completions API (`POST /v1/complete`) is fully deprecated in favor of the Messages API. Model deprecation dates and migration paths are published on the deprecations page. Users should migrate to current models and the Messages API for continued support.

## Key Facts

- **Deprecation Notice**: Published in advance on deprecations page
- **Legacy API**: Text Completions (`POST /v1/complete`) - fully deprecated
- **Current API**: Messages (`POST /v1/messages`)
- **Deprecated Models**: Claude 3.x fully retired; Opus 4.1 deprecated; Sonnet 4/Opus 4 retired
- **Migration**: Update model ID in API calls; Messages API is the only supported interface
- **Deprecation Notice**: At least 60 days before retirement for publicly released models
- **Status**: Ongoing deprecation cycle

## Model Status (as of 2026-07-26)

### Active Models
- **claude-opus-5** - State-of-the-art (Jul 24, 2026)
- **claude-fable-5** - Mythos-class with safety classifiers (Jun 9, 2026)
- **claude-mythos-5** - Glasswing partners only (Jun 9, 2026)
- **claude-sonnet-5** - Most agentic Sonnet (Jun 30, 2026)
- **claude-opus-4-8** - Previous frontier (May 28, 2026)
- **claude-opus-4-7** - Active (fast mode removed Jul 24)
- **claude-opus-4-6** - Active (fast mode removed Jun 29)
- **claude-sonnet-4-6** - Best speed/intelligence ratio
- **claude-haiku-4-5-20251001** - Fast and cost-effective

### Deprecated
- **claude-opus-4-1-20250805** - Deprecated Jun 5, 2026; retiring Aug 5, 2026. Migrate to claude-opus-4-8
- **claude-mythos-preview** - Deprecated; migrate to claude-mythos-5

### Retired
- **claude-sonnet-4-20250514** - Retired Jun 15, 2026; migrate to claude-sonnet-4-6
- **claude-opus-4-20250514** - Retired Jun 15, 2026; migrate to claude-opus-4-8
- **claude-3-haiku-20240307** - Retired April 20, 2026; migrate to claude-haiku-4-5-20251001
- **claude-3-5-haiku-20241022** - Retired February 19, 2026
- **claude-3-7-sonnet-20250219** - Retired February 19, 2026; migrate to claude-sonnet-4-6
- **claude-3-5-sonnet-20241022** - Retired October 28, 2025
- **claude-3-5-sonnet-20240620** - Retired October 28, 2025
- **claude-3-opus-20240229** - Retired January 5, 2026; migrate to claude-opus-5
- **claude-3-sonnet-20240229** - Retired July 21, 2025

## Workbench Sunset

The legacy Workbench (platform.claude.com/workbench) is being sunset with access ending August 17, 2026. Saved prompts, variables, and evals are not supported in the updated Workbench.

The experimental prompt tools APIs are being retired alongside:
- `POST /v1/experimental/generate_prompt`
- `POST /v1/experimental/improve_prompt`
- `POST /v1/experimental/templatize_prompt`

After August 17, 2026, requests to these endpoints will return errors.

## Legacy Text Completions API

The Text Completions API (`POST /v1/complete`) is fully deprecated. All users should migrate to the Messages API:

### Migration Example

```python
import anthropic

client = anthropic.Anthropic()

# LEGACY (deprecated) - Text Completions
# response = client.completions.create(
#     model="claude-2",
#     max_tokens_to_sample=1024,
#     prompt="\n\nHuman: Hello\n\nAssistant:",
# )

# CURRENT - Messages API
response = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.content[0].text)
```

### Key Differences from Text Completions

- **Structured messages** instead of raw prompt string
- **Content blocks** in response instead of flat text
- **Role-based** conversation (user, assistant) instead of Human/Assistant format
- **Stop reasons** instead of stop_reason field
- **Token usage** reported in response body
- **Streaming** via SSE events instead of raw text chunks
- **Tool use** natively supported (no prompt engineering needed)

## Deprecation Lifecycle

1. **Active** - Fully supported and recommended for use
2. **Legacy** - No longer receives updates, may be deprecated in the future
3. **Deprecated** - Still functional but not recommended; replacement and retirement date assigned
4. **Retired** - No longer available; requests return error

Anthropic provides at least 60 days notice before retirement for publicly released models. Deprecation dates on this page apply to Anthropic-operated platforms (Claude API, Claude Platform on AWS, Microsoft Foundry). Partner platforms (Amazon Bedrock, Vertex AI) set their own schedules.

## Auditing Model Usage

To identify usage of deprecated models:
1. Go to the Usage page in Claude Console
2. Click "Export" button
3. Review the CSV to find usage by API key and model

## API Version Compatibility

- Current GA version: `2023-06-01`
- Beta features accessed via `anthropic-beta` header
- Older API versions may lose support; always use current version
- New features may require newer model versions

## Gotchas and Quirks

- Deprecated models still function until their end-of-life date
- Model IDs change between versions; do not hardcode without checking deprecation page
- The Messages API is the only active API; Text Completions is fully deprecated
- Pre-4.6 convenience aliases (`claude-opus-4`, `claude-sonnet-4`) now return errors
- Fast mode removed from Opus 4.7 (Jul 24) and Opus 4.6 (Jun 29); requests with `speed: "fast"` on 4.7 return error, on 4.6 silently downgrade to standard
- Experimental prompt tools APIs retiring Aug 17, 2026
- Researchers can request ongoing access to retired models via External Researcher Access Program
- Check `client.models.list()` for currently available models

## Related Endpoints

- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` - API version management
- `_INFO_ANTAPI-13_MODELS.md [ANTAPI-IN13]` - Current model capabilities
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` - Current Messages API (replacement for Text Completions)

## Sources

- ANTAPI-SC-ANTH-DEPR - https://platform.claude.com/docs/en/about-claude/model-deprecations - Deprecation schedule
- ANTAPI-SC-ANTH-LEGACY - https://platform.claude.com/docs/en/api/complete - Legacy Text Completions reference

## SDK Verification

1 Python example verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `_client.py`: `Anthropic.completions` property exists (legacy Text Completions)
- `resources/messages/messages.py`: `Messages.create()` confirmed as current API

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: 5 new active models (Opus 5, Opus 4.8, Fable 5, Mythos 5, Sonnet 5)
- Changed: Opus 4.1 deprecated (Jun 5, retiring Aug 5)
- Changed: Sonnet 4 and Opus 4 retired (Jun 15)
- Added: Workbench sunset section (Aug 17)
- Added: Prompt tools APIs retirement
- Added: Fast mode removal notes for Opus 4.7/4.6

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model status list completely refreshed (retirements, new deprecations)
- Added: Sonnet 4 + Opus 4 deprecated (April 14, 2026, retiring June 15)
- Added: Haiku 3 retired (April 20, 2026)
- Added: Deprecation lifecycle with 4 stages (Active, Legacy, Deprecated, Retired)
- Added: 60-day notice policy, platform-specific schedules note
- Added: Auditing model usage section

**[2026-03-20 07:05]**
- Added: SDK verification section (anthropic 0.120.0, 1 example valid)

**[2026-03-20 04:33]**
- Initial documentation created from deprecation schedule and legacy API reference
