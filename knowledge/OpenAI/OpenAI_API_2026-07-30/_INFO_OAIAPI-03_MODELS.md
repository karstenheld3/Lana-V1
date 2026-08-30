# Models

**Doc ID**: OAIAPI-IN03
**Goal**: Document OpenAI model families, capabilities, pricing, context windows, and deprecations
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_01-SUMMARY.md [OAIAPI-IN01]` for topic index
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI provides multiple model families: GPT-5.6 flagship family (Sol, Terra, Luna - three tiers from frontier to efficient), GPT-5.5 (deprecated 2026-12), GPT-5.4 series, image generation (gpt-image-2), video generation (Sora - deprecated Sept 2026), audio models (Whisper, gpt-4o-mini-transcribe, gpt-audio-1.5 for TTS), realtime voice models (gpt-realtime-2.1, gpt-realtime-2.1-mini, gpt-realtime-2, gpt-realtime-translate, gpt-realtime-whisper), embeddings (text-embedding-3-small/large), and moderation (omni-moderation-latest). GPT-5.6 is the current flagship (2026-07-09): Sol/Terra/Luna tiers, 1M context, Programmatic Tool Calling, Multi-agent beta, Pro mode, persisted reasoning, 6 effort levels (none-max), explicit caching with TTL. GPT-5.5 and GPT-5.5-pro deprecated 2026-06-11 (removal 2026-12-11). GPT-Realtime-2.1 adds improved alphanumeric recognition and interruption handling. 2026-06 deprecation wave: Evals platform, Agent Builder, Reusable Prompts, gpt-image-1-mini/1.5. [VERIFIED] (OAIAPI-SC-OAI-GMODLS, OAIAPI-SC-OAI-GPRICE, OAIAPI-SC-OAI-GCHLOG, OAIAPI-SC-OAI-GDEPR)

## Key Facts

- **Latest flagship**: GPT-5.6 Sol/Terra/Luna (1M context, 2026-07). `gpt-5.6` alias routes to Sol. [VERIFIED] (OAIAPI-SC-OAI-GLATEST)
- **Model families**: GPT-5.6 (flagship), GPT-5.5/5.4 (deprecated/legacy), gpt-image (images), Sora (video, deprecated), Realtime 2.1 (voice), Whisper/TTS (audio), embeddings, moderation [VERIFIED] (OAIAPI-SC-OAI-GMODLS)
- **New since 2026-05-22**: GPT-5.6 Sol/Terra/Luna, GPT-Realtime-2.1, GPT-Realtime-2.1-mini [VERIFIED] (OAIAPI-SC-OAI-GCHLOG)
- **Deprecated 2026-06**: GPT-5.5, GPT-5.5-pro, o3 snapshots (removal 2026-12-11); Evals, Agent Builder, Reusable Prompts; gpt-image-1-mini/1.5 (removal 2026-12-01) [VERIFIED] (OAIAPI-SC-OAI-GDEPR)
- **Removed**: DALL-E 2/3 (2026-05-12), Realtime API Beta (2026-05-12) [VERIFIED] (OAIAPI-SC-OAI-GDEPR)
- **Context windows**: 4K-1M tokens depending on model [VERIFIED] (OAIAPI-SC-OAI-GMODLS)

## Model Families

### GPT-5.6 Series (Current Flagship - 2026-07-09)

#### GPT-5.6 Sol (Frontier)
- **Context window**: 1,000,000 tokens
- **Max output**: 128,000 tokens
- **Pricing**: $5.00/MTok input, $30.00/MTok output (estimated based on tier positioning)
- **Reasoning**: 6 effort levels: none, low, medium (DEFAULT), high, xhigh, max. Pro mode available.
- **Features**: Programmatic Tool Calling, Multi-agent beta, persisted reasoning, explicit caching (TTL), original image detail
- **Tools (Responses API)**: web_search, file_search, image_generation, code_interpreter, hosted_shell, apply_patch, skills, computer_use, mcp, tool_search, programmatic_tool_calling
- **Endpoints**: Chat Completions, Responses, Batch
- **Use case**: Frontier capability, complex professional work, deep reasoning
- **Model ID**: `gpt-5.6-sol` (alias: `gpt-5.6`)

#### GPT-5.6 Terra (Balanced)
- **Context window**: 1,000,000 tokens
- **Pricing**: Lower than Sol, balanced intelligence/cost
- **Reasoning**: Same 6 effort levels, Pro mode available
- **Features**: Same as Sol
- **Use case**: Strong performance at lower price for everyday workloads
- **Model ID**: `gpt-5.6-terra`

#### GPT-5.6 Luna (Efficient)
- **Context window**: 1,000,000 tokens
- **Pricing**: Lowest tier (~$1/MTok input, $6/MTok output based on MarkTechPost)
- **Reasoning**: Same 6 effort levels, Pro mode available
- **Features**: Same as Sol
- **Use case**: Fast, cost-efficient high-volume tasks
- **Model ID**: `gpt-5.6-luna`

### GPT-5.x Series (Previous Generation - DEPRECATED)

#### GPT-5.5 (DEPRECATED - removal 2026-12-11)
- **Context window**: 1,050,000 tokens
- **Max output**: 128,000 tokens
- **Pricing**: $5.00/MTok input, $30.00/MTok output, $0.50 cached input
- **Long context surcharge**: >272K input tokens = 2x input, 1.5x output for full session
- **Regional processing**: 10% uplift for data residency endpoints
- **Reasoning**: Supports effort levels: none, low, medium (DEFAULT), high, xhigh
- **Knowledge cutoff**: 2025-12-01
- **Tools (Responses API)**: web_search, file_search, image_generation, code_interpreter, hosted_shell, apply_patch, skills, computer_use, mcp, tool_search
- **Endpoints**: Chat Completions, Responses, Realtime, Batch, Assistants
- **Caching**: Extended prompt caching ONLY (in-memory caching NOT supported)
- **Snapshot**: `gpt-5.5-2026-04-23`
- **Use case**: Previous flagship, migrate to GPT-5.6
- **Model ID**: `gpt-5.5`
- **Deprecation**: Announced 2026-06-11. Removal 2026-12-11. Routes to gpt-5.5 until removal.

#### GPT-5.5 pro (DEPRECATED - removal 2026-12-11)
- **Purpose**: Extended compute for harder problems
- **Availability**: Responses API only
- **Use case**: Deep research, complex analysis. Migrate to GPT-5.6 Sol with Pro mode.
- **Model ID**: `gpt-5.5-pro`
- **Deprecation**: Announced 2026-06-11. Removal 2026-12-11.

#### GPT-5.4
- **Context window**: 1,000,000 tokens
- **Max output**: 128,000 tokens
- **Pricing**: $2.50/MTok input, $15.00/MTok output
- **Reasoning**: Supports effort levels: none, low, medium, high, xhigh
- **Knowledge cutoff**: 2025-08-31
- **Tools**: web_search, file_search, code_interpreter, computer_use, mcp, tool_search, compaction
- **Snapshot**: `gpt-5.4-2025-08-15`
- **Use case**: Strong flagship at lower cost than GPT-5.5
- **Model ID**: `gpt-5.4`

#### GPT-5.4 mini
- **Context window**: 400,000 tokens
- **Max output**: 128,000 tokens
- **Pricing**: $0.75/MTok input, $4.50/MTok output
- **Reasoning**: Supports reasoning effort
- **Tools**: web_search, file_search, computer_use, tool_search, compaction
- **Knowledge cutoff**: 2025-08-31
- **Use case**: Strongest mini model for coding, computer use, subagents
- **Model ID**: `gpt-5.4-mini`

#### GPT-5.4 nano
- **Context window**: 400,000 tokens
- **Max output**: 128,000 tokens
- **Pricing**: $0.20/MTok input, $1.25/MTok output
- **Reasoning**: Supports reasoning effort
- **Tools**: Compaction (no tool_search, no computer_use)
- **Knowledge cutoff**: 2025-08-31
- **Use case**: Cheapest GPT-5.4-class for simple high-volume tasks
- **Model ID**: `gpt-5.4-nano`

#### GPT-5.4 pro
- **Purpose**: Extended compute for GPT-5.4-class problems
- **Pricing**: $30.00/MTok input, $180.00/MTok output
- **Availability**: Responses API only
- **Model ID**: `gpt-5.4-pro`

#### chat-latest (NEW - 2026-05)
- **Purpose**: Points to latest Instant model used in ChatGPT
- **Note**: Regularly updated snapshot, NOT for production (use GPT-5.5 instead)
- **Model ID**: `chat-latest`

### o-Series (Reasoning Models)

#### o4-mini
- **Purpose**: Fast reasoning for everyday tasks
- **Use case**: General reasoning, coding, math
- **Status**: Being deprecated (2026-04-22 wave), replaced by gpt-5.4-mini
- **Model ID**: `o4-mini`

#### o3-pro
- **Purpose**: Advanced reasoning for complex problems
- **Status**: Being deprecated (2026-04-22 wave), replaced by gpt-5.5-pro
- **Model ID**: `o3-pro`

### Image Generation Models

#### GPT Image 2 (NEW - 2026-04-21)
- **Purpose**: State-of-the-art image generation and editing
- **Resolution**: Up to 2K
- **Pricing**: Token-based ($8/$30 per MTok estimated), Batch API with 50% discount
- **Features**: Flexible sizes, high-fidelity image inputs, multilingual text rendering, agentic reasoning
- **Snapshot**: `gpt-image-2-2026-04-21`
- **Rate limits**: Tier 1: 100K TPM / 5 IPM, Tier 5: 8M TPM / 250 IPM
- **Use case**: Primary image generation model (replaces gpt-image-1.5 and DALL-E)
- **Model ID**: `gpt-image-2`

#### gpt-image-1
- **Purpose**: Standard image generation
- **Status**: Being deprecated (2026-04-22 wave), replaced by gpt-image-2
- **Model ID**: `gpt-image-1`

#### gpt-image-1.5
- **Purpose**: Full-featured image generation
- **Pricing**: Image $8/$32, Text $5/$10 per MTok
- **Status**: Active (not deprecated)
- **Model ID**: `gpt-image-1.5`

#### gpt-image-1-mini
- **Purpose**: Lower-cost image generation
- **Pricing**: Image $2.50/$8, Text $2/$0 per MTok
- **Model ID**: `gpt-image-1-mini`

#### DALL-E 3, DALL-E 2
- **Status**: **REMOVED** from API (2026-05-12)
- **Replacement**: gpt-image-2, gpt-image-1, gpt-image-1-mini

### Video Generation Models

#### sora-2-pro
- **Purpose**: Higher quality, longer generation time, 1080p output
- **Pricing**: $0.70/second for 1080p
- **Status**: **DEPRECATED** (2026-03-24, shutdown Sept 24, 2026)
- **Model ID**: `sora-2-pro`

#### sora-2
- **Purpose**: Standard video generation, up to 20s, Batch API support
- **Status**: **DEPRECATED** (2026-03-24, shutdown Sept 24, 2026)
- **Model ID**: `sora-2`

#### Sora
- **Purpose**: Original video model
- **Model ID**: `sora`

### Realtime Voice Models

#### gpt-realtime-2 (NEW - 2026-05)
- **Purpose**: Most intelligent voice model with GPT-5-class reasoning
- **Capabilities**: Listen, reason, handle interruptions, use tools, sustain longer conversations
- **Use case**: Voice agents requiring reasoning
- **Model ID**: `gpt-realtime-2`

#### gpt-realtime-translate (NEW - 2026-05)
- **Purpose**: Live speech translation
- **Languages**: 70+ input languages, 13 output languages
- **Keeps pace**: Translates in real-time as speaker talks
- **Model ID**: `gpt-realtime-translate`

#### gpt-realtime-1.5
- **Purpose**: Best voice model for audio in, audio out
- **Pricing**: Audio $32/$64, Text $4/$16 per MTok
- **Model ID**: `gpt-realtime-1.5`

#### gpt-realtime-mini
- **Purpose**: Cost-efficient realtime voice model
- **Pricing**: Audio $10/$20, Text $0.60/$2.40 per MTok
- **Model ID**: `gpt-realtime-mini`

#### gpt-realtime-whisper (NEW - 2026-05)
- **Purpose**: Streaming speech-to-text
- **Capabilities**: Live transcription as speaker talks
- **Use case**: Real-time transcription pipelines
- **Model ID**: `gpt-realtime-whisper`

### Audio Models

#### Whisper
- **Purpose**: Audio transcription and translation
- **Languages**: Multilingual support
- **Model ID**: `whisper-1`

#### gpt-4o-transcribe
- **Purpose**: Speech-to-text model powered by GPT-4o
- **Pricing**: $2.50/$10.00 per MTok (~$0.006/minute)
- **Model ID**: `gpt-4o-transcribe`

#### gpt-4o-mini-transcribe
- **Purpose**: Cost-efficient transcription model
- **Pricing**: $1.25/$5.00 per MTok (~$0.003/minute)
- **Model ID**: `gpt-4o-mini-transcribe`

#### gpt-audio-1.5 (NEW)
- **Purpose**: Text-to-speech (replaces deprecated gpt-4o-mini-tts models)
- **Model ID**: `gpt-audio-1.5`

#### TTS (Text-to-Speech)
- **Models**: `tts-1`, `tts-1-hd`
- **Voices**: Multiple voice options (alloy, echo, fable, onyx, nova, shimmer)
- **Custom voices**: Available for eligible accounts with consent management

### Embeddings Models

#### text-embedding-3-large
- **Dimensions**: Up to 3072
- **Use case**: High-quality semantic search, clustering
- **Model ID**: `text-embedding-3-large`

#### text-embedding-3-small
- **Dimensions**: Up to 1536
- **Use case**: Cost-effective embeddings
- **Model ID**: `text-embedding-3-small`

### Moderation Models

#### omni-moderation-latest
- **Purpose**: Multi-modal content moderation
- **Input**: Text and images
- **Model ID**: `omni-moderation-latest`

### Codex Models (Code Generation)

#### gpt-5.3-codex
- **Purpose**: Codex coding agent
- **Pricing**: $1.75/MTok input, $14.00/MTok output
- **Status**: Current (gpt-5.2-codex deprecated)
- **Model ID**: `gpt-5.3-codex`

#### gpt-5.4 / gpt-5.5 (for code)
- **Purpose**: GPT-5.4/5.5 support hosted_shell and apply_patch tools for code tasks
- **Note**: Older Codex-specific models (gpt-5-codex, gpt-5.1-codex, gpt-5.2-codex) are deprecated

## Model Aliases vs Snapshots

### Auto-Updating Aliases

Model aliases automatically point to latest version:
- `gpt-5.5` -> latest GPT-5.5 snapshot
- `gpt-5.4` -> latest GPT-5.4 snapshot
- `gpt-5.4-mini` -> latest mini snapshot
- `gpt-image-2` -> latest GPT Image 2 snapshot
- `chat-latest` -> latest ChatGPT Instant model (regularly updated)

**Behavior**: Model prompting and output may change as snapshots update

### Pinned Snapshots

Specific dated versions for consistent behavior:
- `gpt-5.5-2026-04-23`
- `gpt-image-2-2026-04-21`
- `gpt-5.4-2025-08-15`

**Recommendation**: Use pinned snapshots for production + implement evals

## Pricing Summary

### Text Models (Short Context)
- **GPT-5.5**: $5.00 / $0.50 cached / $30.00 per MTok
- **GPT-5.5-pro**: $30.00 / - / $180.00 per MTok
- **GPT-5.4**: $2.50 / $0.25 cached / $15.00 per MTok
- **GPT-5.4-pro**: $30.00 / - / $180.00 per MTok
- **GPT-5.4 mini**: $0.75 / $0.075 cached / $4.50 per MTok
- **GPT-5.4 nano**: $0.20 / $0.02 cached / $1.25 per MTok

### Text Models (Long Context)
- **GPT-5.5**: $10.00 / $1.00 cached / $45.00 per MTok
- **GPT-5.5-pro**: $60.00 / - / $270.00 per MTok
- **GPT-5.4**: $5.00 / $0.50 cached / $22.50 per MTok
- **GPT-5.4-pro**: $60.00 / - / $270.00 per MTok

### Image Generation
- **GPT Image 2**: Image $8/$30, Text $5/- per MTok
- **gpt-image-1.5**: Image $8/$32, Text $5/$10 per MTok
- **gpt-image-1-mini**: Image $2.50/$8, Text $2/- per MTok

### Realtime Voice
- **gpt-realtime-2**: Audio $32/$64, Text $4/$24, Image $5/- per MTok
- **gpt-realtime-1.5**: Audio $32/$64, Text $4/$16 per MTok
- **gpt-realtime-mini**: Audio $10/$20, Text $0.60/$2.40 per MTok
- **gpt-realtime-translate**: $0.034/minute

### Transcription
- **gpt-4o-transcribe**: $2.50/$10 per MTok (~$0.006/min)
- **gpt-4o-mini-transcribe**: $1.25/$5 per MTok (~$0.003/min)

### Specialized
- **chat-latest**: $5/$30 per MTok
- **gpt-5.3-codex**: $1.75/$14 per MTok

### Tool Pricing
- **Web search**: $10.00 / 1k calls + content tokens at model rates
- **File search**: $2.50 / 1k calls + $0.10/GB/day storage (1 GB free)
- **Containers** (hosted shell, code interpreter): $0.03-$1.92 per 20-min session (1-64 GB)

## GPT-5.5 Rate Limits (by Tier)

Long context rate limits:
- **Tier 1**: 500 RPM, 500K TPM, 1.5M Batch queue
- **Tier 2**: 5,000 RPM, 1M TPM, 3M Batch queue
- **Tier 3**: 5,000 RPM, 2M TPM, 100M Batch queue
- **Tier 4**: 10,000 RPM, 4M TPM, 200M Batch queue
- **Tier 5**: 15,000 RPM, 40M TPM, 15B Batch queue
- **Free tier**: Not supported

## Deprecation Wave (April-2026-05)

Major model cleanup announced 2026-04-22:

### Removed (2026-05-12)
- `dall-e-2`, `dall-e-3` -> use gpt-image-2/1/1-mini
- Realtime API Beta interface -> use GA Realtime API

### Being Deprecated (with replacements)
- `gpt-5.2-chat-latest`, `gpt-5.3-chat-latest` -> `gpt-5.5`
- `gpt-5-chat-latest`, `gpt-5.1-chat-latest` -> `gpt-5.5`
- `gpt-5-codex`, `gpt-5.1-codex`, `gpt-5.1-codex-max`, `gpt-5.1-codex-mini`, `gpt-5.2-codex` -> `gpt-5.5`
- `computer-use-preview-2025-03-11` -> `gpt-5.4-mini` (built-in computer use)
- `o3-deep-research-*`, `o4-mini-deep-research-*` -> `gpt-5.5-pro`
- `gpt-image-1` -> `gpt-image-2`
- `gpt-4-0613`, `gpt-4-turbo*`, `gpt-4.1-nano*` -> `gpt-5.5` or `gpt-5.4-nano`
- `gpt-3.5-turbo-0125`, `gpt-3.5-turbo-completions` -> `gpt-5.4-mini`
- `o1*`, `o3-mini*`, `o4-mini*` -> `gpt-5.5` or `gpt-5.4-mini`
- `sora-2`, `sora-2-pro` -> shutdown Sept 24, 2026

### Self-Serve Fine-Tuning Update (2026-05-07)
- **Fine-tuning platform winding down**: No longer accessible to new users [VERIFIED]
- Existing users can create training jobs for the coming months
- Inference on fine-tuned models continues until base model deprecation
- Only o4-mini-2025-04-16 listed for new training ($100/hour)

## SDK Examples (Python)

### List All Models

```python
from openai import OpenAI

client = OpenAI()

models = client.models.list()
for model in models.data:
    print(f"{model.id}: owned by {model.owned_by}")
```

### Retrieve Model Details

```python
from openai import OpenAI

client = OpenAI()

model = client.models.retrieve("gpt-5.5")
print(f"Model: {model.id}")
print(f"Owner: {model.owned_by}")
```

### Using GPT-5.5 with Responses API

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Analyze the trade-offs between microservices and monolithic architecture for a startup with 5 engineers.",
    reasoning={"effort": "high"},
)
print(response.output_text)
```

### Using GPT-5.5 with Chat Completions

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {"role": "system", "content": "You are a senior software architect."},
        {"role": "user", "content": "Design a rate limiting system for a high-traffic API."}
    ],
    reasoning_effort="medium",
)
print(response.choices[0].message.content)
```

### Production Setup with Model Pinning

```python
from openai import OpenAI

client = OpenAI()

# Pin specific snapshot for production consistency
MODEL_ID = "gpt-5.5-2026-04-23"

try:
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role": "user", "content": "Summarize the key changes in Python 3.13."}]
    )
    print(response.choices[0].message.content)
    # Access request ID for debugging
    print(f"Request ID: {response._request_id}")
except Exception as e:
    print(f"Error using model {MODEL_ID}: {e}")
```

### Image Generation with GPT Image 2

```python
from openai import OpenAI

client = OpenAI()

result = client.images.generate(
    model="gpt-image-2",
    prompt="A photorealistic landscape of mountains at sunset with a lake reflection",
    size="1536x1024",
    quality="high",
)
print(result.data[0].url)
```

## Error Responses

- **404 Not Found** - Model does not exist or has been deprecated/removed
- **400 Bad Request** - Invalid model ID format
- **403 Forbidden** - Account lacks access to specified model (tier restriction)

## Differences from Other APIs

- **vs Anthropic**: OpenAI has broader model family (image, video, audio, realtime voice); Anthropic focuses on Claude text models with Extended Thinking
- **vs Gemini**: OpenAI has more specialized models; Gemini has native multimodal (audio/video in/out)
- **vs Grok**: OpenAI has wider model selection; Grok focuses on text models with X/Twitter integration

## Gotchas and Quirks

- **GPT-5.5 caching**: ONLY extended prompt caching works, NOT in-memory caching (unlike GPT-5.4) [VERIFIED] (OAIAPI-SC-OAI-MGP55)
- **GPT-5.5 reasoning default**: Defaults to `medium` (unlike older models that default to higher). Adjust for your use case [VERIFIED] (OAIAPI-SC-OAI-MGP55)
- **GPT-5.5 long context pricing**: >272K input = 2x input + 1.5x output for ENTIRE session, not just overflow [VERIFIED] (OAIAPI-SC-OAI-MGP55)
- **Alias behavior changes**: Using `gpt-5.5` alias means output may change without warning when new snapshot released [VERIFIED] (OAIAPI-SC-OAI-GMODLS)
- **Context != output**: Max output tokens (128K) is much smaller than context window (1M+) [VERIFIED]
- **DALL-E removed**: Any code using `dall-e-2` or `dall-e-3` will get 404 errors since 2026-05-12 [VERIFIED] (OAIAPI-SC-OAI-GDEPR)
- **chat-latest NOT for production**: Snapshot changes frequently, use GPT-5.5 alias or pinned snapshot instead [VERIFIED] (OAIAPI-SC-OAI-GCHLOG)
- **Fine-tuning winding down**: Platform no longer accessible to new users. Existing users can still create jobs temporarily [VERIFIED] (OAIAPI-SC-OAI-GPRICE)
- **GPT-5.4 long context pricing**: Separate long context tier: $5/$22.50 per MTok (2x input, 1.5x output) [VERIFIED] (OAIAPI-SC-OAI-GPRICE)

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

- OAIAPI-SC-OAI-MODAPI - Models API reference
- OAIAPI-SC-OAI-GMODLS - Models overview guide
- OAIAPI-SC-OAI-GPRICE - Pricing information
- OAIAPI-SC-OAI-GLATEST - Using GPT-5.5 guide
- OAIAPI-SC-OAI-GDEPR - Deprecations guide
- OAIAPI-SC-OAI-GCHLOG - Changelog
- OAIAPI-SC-OAI-MGP55 - GPT-5.5 model page
- OAIAPI-SC-OAI-MGP55P - GPT-5.5 Pro model page
- OAIAPI-SC-OAI-MGIMG2 - GPT Image 2 model page
- OAIAPI-SC-OAI-MGRT2 - Realtime 2 model info

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: GPT-5.6 Sol/Terra/Luna as new flagship family (2026-07-09)
- Added: GPT-Realtime-2.1 and GPT-Realtime-2.1 mini
- Changed: GPT-5.5 and GPT-5.5-pro marked DEPRECATED (removal 2026-12-11)
- Changed: o3 snapshots deprecated (removal 2026-12-11)
- Added: 2026-06 deprecation wave (Evals, Agent Builder, Reusable Prompts, Image models)
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 13:35]**
- Fixed: GPT-5.4 output pricing $12 -> $15 per MTok (verified from live pricing page)
- Added: GPT-5.4-pro model ($30/$180 per MTok)
- Added: gpt-realtime-1.5 and gpt-realtime-mini models with pricing
- Added: gpt-image-1.5 model with pricing
- Added: gpt-4o-transcribe model with pricing
- Added: Long context pricing tier (separate column from short context)
- Added: Tool pricing (web search, file search, containers)
- Added: Fine-tuning winding down note
- Added: gpt-5.3-codex pricing ($1.75/$14)
- Added: GPT-5.5-pro pricing ($30/$180)

**[2026-05-22 09:45]**
- Major update from 2026-03-20 version
- Added: GPT-5.5 as new flagship ($5/$30, 1M+ context, 2025-12 cutoff)
- Added: GPT-5.5-pro (replaces o3/o4-mini deep research)
- Added: GPT Image 2 (token pricing, 2K resolution, Batch support)
- Added: Realtime 2, Translate, Whisper models
- Added: chat-latest snapshot, gpt-audio-1.5, gpt-5.3-codex
- Added: Full deprecation wave documentation (April-2026-05)
- Added: GPT-5.5 rate limits by tier
- Added: Image generation and Responses API Python examples
- Changed: DALL-E 2/3 marked as REMOVED (2026-05-12)
- Changed: Sora models marked as DEPRECATED (Sept 2026 shutdown)
- Changed: o3-deep-research/o4-mini-deep-research replaced by gpt-5.5-pro
- Changed: Pricing section updated with GPT-5.5 tiers
- Changed: SDK examples updated to use gpt-5.5
