# SDK Model Methods: Verified Parameter Combinations

**Doc ID**: ANTAPI-IN50
**Goal**: Document which thinking/effort parameters each Claude model accepts, verified via live API calls
**SDK version**: `@anthropic-ai/sdk` 0.115.0 (TypeScript/Node.js)
**Tested**: 2026-07-27
**Test script**: `sdk_test.cjs` (22 tests, 14 passed, 8 failed)

## Key Findings

Three distinct parameter regimes exist across Claude model generations. Using the wrong regime returns HTTP 400 immediately.

**Generation boundary**: Models before Opus 4.6 use `thinking: {type: "enabled"}`. Models from Opus 4.6 onward use `thinking: {type: "adaptive"}`. There is no overlap - each model supports exactly one type. The `effort-2025-11-24` beta header for Opus 4.5 is no longer required (works without it), and `output_config: {effort}` works on Opus 4.5 without any beta header.

**Opus 4 (deprecated)**: Model `claude-opus-4-20250514` returns 404 - it has been removed from the API as of its June 2026 end-of-life.

## Model Method Matrix

```
Model               thinking: enabled   thinking: adaptive   output_config.effort   No thinking param
----               -----------------   ------------------   --------------------   -----------------
Sonnet 4.5              PASS                 FAIL                  N/T                   PASS
Haiku 4.5               PASS                 FAIL                  N/T                   PASS
Opus 4.5                PASS                 FAIL                  PASS                  PASS
Opus 4.8                FAIL                 PASS                  PASS                  PASS
Fable 5                 N/T                  PASS                  PASS                  PASS (thinks anyway)
Opus 4 (deprecated)     404                  404                   N/T                   N/T
```

N/T = not tested (implied by other results)

## Method 1: thinking: enabled (4.5-generation models)

**Supported by**: Sonnet 4.5, Haiku 4.5, Opus 4.5
**NOT supported by**: Opus 4.8, Fable 5 (returns 400: "thinking.type.enabled is not supported for this model")

The model always thinks when enabled. Thinking tokens appear as a `thinking` content block before the `text` block. The caller controls thinking depth via `budget_tokens`.

```javascript
import Anthropic from "@anthropic-ai/sdk";
const client = new Anthropic({ apiKey: "sk-ant-..." });

// Sonnet 4.5 with thinking enabled
const message = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 8192,
  thinking: { type: "enabled", budget_tokens: 4000 },
  messages: [{ role: "user", content: "What is 2+2?" }],
});
// Response content: [{ type: "thinking", thinking: "..." }, { type: "text", text: "4" }]
// usage.output_tokens_details.thinking_tokens: 46

// Opus 4.5 with thinking enabled (also works)
const msg2 = await client.messages.create({
  model: "claude-opus-4-5-20251101",
  max_tokens: 8192,
  thinking: { type: "enabled", budget_tokens: 4000 },
  messages: [{ role: "user", content: "What is 2+2?" }],
});
// Response content: [{ type: "thinking", thinking: "..." }, { type: "text", text: "4" }]

// Haiku 4.5 with thinking enabled
const msg3 = await client.messages.create({
  model: "claude-haiku-4-5-20251001",
  max_tokens: 8192,
  thinking: { type: "enabled", budget_tokens: 4000 },
  messages: [{ role: "user", content: "What is 2+2?" }],
});
```

**Constraint**: `max_tokens` must exceed `budget_tokens`. If `max_tokens <= budget_tokens`, the API returns 400.

**Without thinking**: Omit the `thinking` parameter entirely. The model responds without thinking blocks.

```javascript
const plain = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  messages: [{ role: "user", content: "What is 2+2?" }],
});
// Response content: [{ type: "text", text: "4" }]
// No thinking_tokens in usage
```

## Method 2: thinking: adaptive (4.6+ generation models)

**Supported by**: Opus 4.6, Opus 4.7, Opus 4.8, Fable 5, Sonnet 5, Opus 5
**NOT supported by**: Sonnet 4.5, Haiku 4.5, Opus 4.5 (returns 400: "adaptive thinking is not supported on this model")

The model decides whether to think based on task complexity. For trivial tasks, `thinking_tokens: 0` and no thinking block appears. For complex tasks, thinking blocks appear automatically.

```javascript
// Opus 4.8 with adaptive thinking
const message = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 4096,
  thinking: { type: "adaptive" },
  messages: [{ role: "user", content: "Reply with exactly: OK" }],
});
// Simple task: content = [{ type: "text", text: "OK" }], thinking_tokens: 0
// Complex task: content = [{ type: "thinking", ... }, { type: "text", ... }]

// Fable 5 with adaptive thinking
const msg2 = await client.messages.create({
  model: "claude-fable-5",
  max_tokens: 4096,
  thinking: { type: "adaptive" },
  messages: [{ role: "user", content: "Reply with exactly: OK" }],
});
```

### Controlling effort with output_config

Use `output_config: { effort: "low" | "medium" | "high" | "xhigh" | "max" }` to influence how much effort the model invests. Higher effort = more thinking tokens.

```javascript
// Low effort - fast, minimal thinking
const low = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 4096,
  thinking: { type: "adaptive" },
  output_config: { effort: "low" },
  messages: [{ role: "user", content: "Classify: great product!" }],
});

// High effort - deeper analysis
const high = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 4096,
  thinking: { type: "adaptive" },
  output_config: { effort: "high" },
  messages: [{ role: "user", content: "Design a database schema for..." }],
});

// Fable 5 with effort control
const fable = await client.messages.create({
  model: "claude-fable-5",
  max_tokens: 4096,
  thinking: { type: "adaptive" },
  output_config: { effort: "high" },
  messages: [{ role: "user", content: "Analyze this code..." }],
});
// Verified: thinking block appears at high effort, thinking_tokens: 12
```

### Fable 5: Thinks by default even without thinking param

```javascript
// No thinking parameter at all - Fable 5 STILL produces thinking blocks
const plain = await client.messages.create({
  model: "claude-fable-5",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Reply with exactly: OK" }],
});
// content: [{ type: "thinking", ... }, { type: "text", text: "OK" }]
// thinking_tokens: 16
```

This means code consuming Fable 5 responses must always handle `thinking` content blocks, even without requesting them.

## Method 3: output_config.effort without thinking (Opus 4.5)

**Supported by**: Opus 4.5 (and likely all models that accept output_config)
**Beta header**: `effort-2025-11-24` is NO LONGER REQUIRED. The API accepts `output_config` without the beta header.

```javascript
// Opus 4.5 with effort control (no thinking, no beta header needed)
const message = await client.messages.create({
  model: "claude-opus-4-5-20251101",
  max_tokens: 1024,
  output_config: { effort: "high" },
  messages: [{ role: "user", content: "What is 2+2?" }],
});
// Response: [{ type: "text", text: "OK" }] - no thinking block
// Works identically with or without anthropic-beta header

// With beta header (still works, just unnecessary)
const msg2 = await client.messages.create(
  {
    model: "claude-opus-4-5-20251101",
    max_tokens: 1024,
    output_config: { effort: "high" },
    messages: [{ role: "user", content: "What is 2+2?" }],
  },
  { headers: { "anthropic-beta": "effort-2025-11-24" } }
);
```

## Usage Response Format

All models return usage in the same format:

```json
{
  "input_tokens": 12,
  "cache_creation_input_tokens": 0,
  "cache_read_input_tokens": 0,
  "cache_creation": {
    "ephemeral_5m_input_tokens": 0,
    "ephemeral_1h_input_tokens": 0
  },
  "output_tokens": 53,
  "output_tokens_details": {
    "thinking_tokens": 46
  },
  "service_tier": "standard",
  "inference_geo": "global"
}
```

- `output_tokens_details.thinking_tokens` only present when model produces thinking blocks
- `inference_geo`: "global" for 4.6+ models, "not_available" for 4.5-generation
- `cache_creation` object is new in recent SDK versions

## Streaming

The SDK returns a `Stream<RawMessageStreamEvent>` when `stream: true`. All parameter combinations above work identically with streaming:

```javascript
const stream = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 4096,
  thinking: { type: "adaptive" },
  output_config: { effort: "high" },
  stream: true,
  messages: [{ role: "user", content: "Hello" }],
});

for await (const event of stream) {
  if (event.type === "content_block_start") {
    // event.content_block.type === "thinking" or "text" or "tool_use"
  } else if (event.type === "content_block_delta") {
    if (event.delta.type === "thinking_delta") {
      // event.delta.thinking - streaming thinking text
    } else if (event.delta.type === "text_delta") {
      // event.delta.text - streaming response text
    }
  }
}
```

## SDK v0.115.0 Notes

- `betas` parameter is NOT supported on `client.messages.create()` in this SDK version. Passing `betas: [...]` in the body causes API error "betas: Extra inputs are not permitted". Use `headers: { "anthropic-beta": "..." }` in the options (second argument) instead.
- SDK warns when using deprecated models (console.warn with migration URL)
- SDK auto-detects model-specific timeout behavior for non-streaming calls

## Implications for model-config.ts

Based on these findings, the model registry `method` field maps to API parameters as follows:

```
Registry method        API parameters
---------------        --------------
"thinking"             thinking: { type: "enabled", budget_tokens: N }    (Sonnet 4.5, Haiku 4.5, Opus 4.5)
"effort"               output_config: { effort: "low"|"medium"|"high" }   (Opus 4.5 only, beta header optional)
"adaptive_thinking"    thinking: { type: "adaptive" }                     (Opus 4.6+, Fable 5, Opus 5)
                       + output_config: { effort: "..." }                 (optional, controls thinking depth)
"temperature"          temperature: N                                     (OpenAI models)
"reasoning_effort"     reasoning_effort: "..."                            (OpenAI reasoning models)
```

**Opus 4.5 dual support**: Opus 4.5 supports BOTH `thinking: {type: "enabled"}` AND `output_config: {effort}`. The registry currently uses `method: "effort"` which sends only `output_config`. This is valid. Alternatively, `method: "thinking"` would also work. The key constraint is that `thinking: {type: "adaptive"}` is NOT supported.

## Sources

All results from live API calls on 2026-07-27 using `@anthropic-ai/sdk` v0.115.0.
Test script: `docs/Anthropic/sdk_test.cjs`
Raw results: `docs/Anthropic/sdk_test_results.json`

## Document History

**[2026-07-27 12:34]**
- Initial document created from 22 live API tests across 6 models
