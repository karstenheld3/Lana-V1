# Changelog and Deprecations

**Doc ID**: OAIAPI-IN62
**Goal**: Document API changelog since 2026-03 and current deprecation schedule
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Major API changes March-2026-07: **GPT-5.6** released as new flagship (2026-07-09) with Sol/Terra/Luna tiers, Programmatic Tool Calling, Multi-Agent beta, persisted reasoning, Pro mode, explicit caching controls. GPT-Realtime-2.1 and mini (July). June deprecation wave: Evals platform, Agent Builder, Reusable Prompts, older GPT Image models. Inline moderation and web search image results (June). Amazon Bedrock integration (June). Container per-minute billing (2026-06-02). Workload Identity Federation (May). GPT-5.5 deprecated (2026-06-11, removal 2026-12-11). Previous: GPT-5.5 released (2026-04-24), GPT Image 2 (2026-04-21), Realtime 2/Translate/Whisper (May), DALL-E 2/3 removed (2026-05-12), massive model deprecation wave (2026-04-22). [VERIFIED] (OAIAPI-SC-OAI-GCHLOG, OAIAPI-SC-OAI-GDEPR)

## Changelog (March-2026-07)

### 2026-07

- **GPT-5.6** released (2026-07-09) as new flagship family [VERIFIED]
  - Three tiers: Sol (frontier), Terra (balanced), Luna (efficient)
  - 1M token context, self-serve, all new features
  - Programmatic Tool Calling: model writes JS to orchestrate tools in V8 sandbox
  - Multi-Agent beta: parallel subagent coordination in Responses API
  - Persisted reasoning: `reasoning.context` carries chain-of-thought across turns
  - Pro mode: `reasoning.mode: "pro"` for harder tasks
  - 6 effort levels: none, low, medium, high, xhigh, max
  - Explicit caching with breakpoints and TTL
  - Original image detail parameter for gpt-image-2
- **GPT-Realtime-2.1** released: improved alphanumeric handling, interruption, reasoning [VERIFIED]
- **GPT-Realtime-2.1 mini** released: distilled, cost-efficient variant [VERIFIED]
- **Python SDK v2.45.0** with GPT-5.6 support [VERIFIED]

### 2026-06

- **Inline moderation** (2026-06-24): `moderation` object in Responses/Chat Completions for input+output scoring without separate call [VERIFIED]
- **Web search image results** (2026-06-17): web_search tool returns images alongside text [VERIFIED]
- **Amazon Bedrock integration** (2026-06-16): OpenAI models via AWS Bedrock Responses API endpoint [VERIFIED]
- **GPT-5/o3 snapshots deprecated** (2026-06-11): removal 2026-12-11, route to gpt-5.5 [VERIFIED]
- **GPT-5.5 deprecated** (2026-06-11): removal 2026-12-11, replaced by GPT-5.6 [VERIFIED]
- **Safety Usage Dashboard** (2026-06-05): `safety_identifier` for tracking blocked requests [VERIFIED]
- **Agent Builder deprecated** (2026-06-03): migrate to Agents SDK or Workspace Agents [VERIFIED]
- **Evals platform deprecated** (2026-06-03): migrate to Promptfoo [VERIFIED]
- **Reusable prompts deprecated** (2026-06-03): migrate to application code [VERIFIED]
- **Container per-minute billing** (2026-06-02): 5-min minimum, replaces 20-min flat rate [VERIFIED]
- **gpt-image-1-mini, gpt-image-1.5, chatgpt-image-latest deprecated** (2026-06-02): removal 2026-12-01 [VERIFIED]
- **Python SDK v2.39.0-v2.44.0**: workload identity, Bedrock support, inline moderation, admin spend alerts [VERIFIED]

### 2026-05

- **Secure MCP Tunnel** released for enterprise (account-led GA, not self-serve). Connects ChatGPT, Codex, Responses API, AgentKit to private MCP servers via tunnel-client [VERIFIED]
- **DALL-E 2/3 removed** (2026-05-12). Use gpt-image-2, gpt-image-1, or gpt-image-1-mini [VERIFIED]
- **Realtime API Beta removed** (2026-05-12). Migrate to GA Realtime API [VERIFIED]
- **`return_token_budget`** added for Responses API web search tool. Opt in to longer GPT-5.5+ reasoning search runs [VERIFIED]
- **Realtime 2** released: voice model with configurable reasoning for speech-to-speech agents [VERIFIED]
- **Realtime Translate** released: streaming speech translation (70+ input, 13 output languages) [VERIFIED]
- **Realtime Whisper** released: streaming speech-to-text [VERIFIED]
- **chat-latest** snapshot released (points to latest ChatGPT Instant model) [VERIFIED]
- **Admin APIs in SDKs**: Python, Node, Go, Ruby, Java support [VERIFIED]
- **Agents SDK TypeScript**: sandbox agents, open-source harness [VERIFIED]
- **OpenAI Developers plugin for Codex** released [VERIFIED]
- **gpt-5.2-chat-latest, gpt-5.3-chat-latest deprecated** (2026-05-08) -> use gpt-5.5 [VERIFIED]
- **Self-serve fine-tuning changes** announced (2026-05-07) [VERIFIED]

### 2026-04

- **GPT-5.5** released (2026-04-24) to Chat Completions and Responses API [VERIFIED]
  - 1M+ token context, $5/$30 per MTok
  - Reasoning effort defaults to medium
  - Extended prompt caching only (no in-memory)
  - Supports: tool search, computer use, hosted shell, apply patch, Skills, MCP, web search
- **GPT-5.5 pro** released for Responses API (harder problems, more compute) [VERIFIED]
- **GPT Image 2** released (2026-04-21): 2K resolution, token-based pricing, Batch support with 50% discount [VERIFIED]
- **Agents SDK updated**: sandbox agents, inspectable harness, memory control [VERIFIED]
- **Legacy GPT model snapshots deprecated** (2026-04-22): massive wave retiring dozens of models [VERIFIED]

### 2026-03 (post-baseline)

- **GPT-5.4 mini and GPT-5.4 nano** released [VERIFIED]
  - Mini: tool search, computer use, compaction
  - Nano: compaction only (no tool search/computer use)
- **gpt-5.3-chat-latest** snapshot updated [VERIFIED]
- **Sora API expanded**: character references, 20s generations, 1080p, video extensions, Batch API [VERIFIED]
- **POST /v1/videos/edits** added (replacing /v1/videos/{id}/remix, deprecated in 6 months) [VERIFIED]
- **GPT-5.4 and GPT-5.4 pro** released [VERIFIED]
  - Tool search, Computer use, 1M context, Compaction
- **gpt-5.3-chat-latest** released [VERIFIED]

## Current Deprecation Schedule

### Already Removed

- **DALL-E 2** (`dall-e-2`) - Removed 2026-05-12 -> gpt-image-2/1/1-mini
- **DALL-E 3** (`dall-e-3`) - Removed 2026-05-12 -> gpt-image-2/1/1-mini
- **Realtime API Beta** - Removed 2026-05-12 -> GA Realtime API

### Upcoming Deprecations

#### 2026-05-08: Chat-latest snapshots
- `gpt-5.2-chat-latest` -> `gpt-5.5`
- `gpt-5.3-chat-latest` -> `gpt-5.5`

#### 2026-04-22: Legacy GPT model wave

**Flagship/Reasoning replacements** (-> gpt-5.5):
- `gpt-5-chat-latest`, `gpt-5.1-chat-latest`
- `gpt-5-codex`, `gpt-5.1-codex`, `gpt-5.1-codex-max`, `gpt-5.1-codex-mini`, `gpt-5.2-codex`
- `gpt-4-0613`, `gpt-4-1106-preview`
- `gpt-4-turbo`, `gpt-4-turbo-2024-04-09`
- `gpt-4o-2024-05-13`
- `o1-2024-12-17` / `o1`
- `o3-mini-2025-01-31` / `o3-mini`

**Mini/Nano replacements** (-> gpt-5.4-mini or gpt-5.4-nano):
- `computer-use-preview-2025-03-11` -> `gpt-5.4-mini`
- `gpt-4o-mini-search-preview-2025-03-11` -> `gpt-5.4-mini`
- `gpt-3.5-turbo-0125` -> `gpt-3.5-turbo`
- `gpt-3.5-turbo-completions` -> `gpt-5.4-mini`
- `gpt-4.1-nano-2025-04-14` -> `gpt-5.4-nano`
- `o4-mini-2025-04-16` / `o4-mini` -> `gpt-5.4-mini`
- `ft-o4-mini-2025-04-16` -> `gpt-5.4-mini`
- `gpt-4o-mini-tts-2025-03-20`, `gpt-4o-mini-tts-2025-12-15` -> (TTS models)

**Pro/Research replacements** (-> gpt-5.5-pro):
- `o3-deep-research-2025-06-26` / `o3-deep-research`
- `o4-mini-deep-research-2025-06-26` / `o4-mini-deep-research`
- `o1-pro-2025-03-19` / `o1-pro`

**Image model** (-> gpt-image-2):
- `gpt-image-1`

**Audio model** (-> gpt-audio-1.5):
- `gpt-audio-mini-2025-10-06`

**Realtime model**:
- `gpt-realtime-mini-2025-10-06` -> `gpt-realtime-mini`

**Fine-tuned model replacements**:
- `ft-gpt-3.5-turbo` -> `gpt-5.4-mini`
- `ft-gpt-4` -> `gpt-5.5`
- `ft-gpt-4.1-nano-2025-04-14` -> `gpt-5.4-nano`
- `ft-babbage-002`, `ft-davinci-002` -> `gpt-5.4-mini`

#### 2026-03-24: Sora 2 models
- `sora-2`, `sora-2-pro`, and snapshots -> shutdown 2026-09-24

#### 2026-08-26: Assistants API
- Full Assistants API sunset. Migrate to Responses API + Conversations API

## Migration Guides

### DALL-E -> GPT Image 2

```python
# OLD (will fail with 404)
result = client.images.generate(model="dall-e-3", prompt="A cat", size="1024x1024")

# NEW
result = client.images.generate(model="gpt-image-2", prompt="A cat", size="1024x1024", quality="high")
```

### Realtime Beta -> GA Realtime

Key differences:
- New event format (see migration guide in Realtime docs)
- Client secrets for WebRTC
- Calls API for call management
- Translation and Whisper sessions available

### o3-deep-research -> gpt-5.5-pro

```python
# OLD
response = client.responses.create(model="o3-deep-research", input="Research topic...", background=True)

# NEW
response = client.responses.create(model="gpt-5.5-pro", input="Research topic...", reasoning={"effort": "xhigh"})
```

## SDK Examples (Python)

### Check Model Availability

```python
from openai import OpenAI

client = OpenAI()

# Check if a model is still available
try:
    model = client.models.retrieve("dall-e-3")
    print(f"Model available: {model.id}")
except Exception as e:
    print(f"Model removed: {e}")  # Will show 404 for dall-e-3
```

### Migration Helper

```python
from openai import OpenAI

client = OpenAI()

# Model replacement mapping
REPLACEMENTS = {
    "dall-e-2": "gpt-image-2",
    "dall-e-3": "gpt-image-2",
    "gpt-5-chat-latest": "gpt-5.5",
    "gpt-5.1-chat-latest": "gpt-5.5",
    "gpt-5.2-chat-latest": "gpt-5.5",
    "gpt-5.3-chat-latest": "gpt-5.5",
    "o3-deep-research": "gpt-5.5-pro",
    "o4-mini-deep-research": "gpt-5.5-pro",
    "computer-use-preview": "gpt-5.4-mini",
    "gpt-image-1": "gpt-image-2",
}

def get_current_model(model_id: str) -> str:
    """Return current replacement model if deprecated, else original."""
    return REPLACEMENTS.get(model_id, model_id)
```

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

- OAIAPI-SC-OAI-GCHLOG - Changelog
- OAIAPI-SC-OAI-GDEPR - Deprecations page

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: 2026-07 changelog (GPT-5.6, Realtime 2.1, SDK v2.45.0)
- Added: 2026-06 changelog (deprecation wave, inline moderation, Bedrock, image search)
- Changed: Summary updated for March-2026-07 scope
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 10:20]**
- Major update from 2026-03-20 version
- Added: Full March-2026-05 changelog
- Added: 2026-04-22 massive deprecation wave (dozens of models)
- Added: 2026-05-12 removals (DALL-E 2/3, Realtime Beta)
- Added: Migration code examples for common scenarios
- Added: Model replacement mapping helper
